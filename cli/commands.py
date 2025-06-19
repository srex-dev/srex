import typer
import json
from pathlib import Path
from backend.core.services.prompt.prompt_engine import generate_definitions
from backend.core.output_schema import validate_srex_output
from core.services.logging.logger import logger
from backend.core.config import CONFIG

app = typer.Typer(no_args_is_help=True, add_completion=False)

@app.command()
def generate(
    input: str = typer.Option(None, "-i", "--input", help="Input JSON file (optional if using live metrics)"),
    output: str = typer.Option(..., "-o", "--output", help="Output JSON file"),
    template: str = typer.Option("base", "-t", "--template", help="Prompt template to use (e.g., reliability, automation)"),
    explain: bool = typer.Option(False, "--explain", help="Include LLM explanation in output"),
    no_suggestions: bool = typer.Option(False, "--no-suggestions", help="Suppress LLM suggestions in output"),
    model: str = typer.Option("llama2", "--model", help="LLM model to use (e.g., llama2, mistral)"),
    adapter: str = typer.Option(None, "--adapter", help="Metrics adapter to use (e.g., prometheus, datadog, static)"),
    live_metrics: bool = typer.Option(False, "--live-metrics", help="Fetch and inject live SLIs using the selected adapter"),
    service_name: str = typer.Option("web", "--service-name", help="Service/component name for live metrics"),
    temperature: float = typer.Option(0.7, "--temperature", help="LLM temperature setting (default: 0.7)"),
    mode: str = typer.Option("default", "--mode", help="Generation mode: default, minimal, or saas")  # ✅ NEW
):
    """
    Generate SLOs, SLIs, and alerting rules using the selected prompt template.
    """
    print(f"📍 CLI 'generate' called with template={template} input={input}")
    logger.info("✅ Logger is working from CLI")

    if adapter:
        CONFIG["metrics_provider"] = adapter
        logger.info(f"🔌 Adapter override: {adapter}")

    metrics_adapter = None
    if live_metrics:
        from metrics.loader import load_metrics_adapter
        metrics_adapter = load_metrics_adapter(CONFIG)
        print(f"📡 [CLI] Live metrics enabled using adapter: {CONFIG['metrics_provider']}")
        logger.info(f"📡 Live metrics mode enabled using adapter: {CONFIG['metrics_provider']}")
        logger.info(f"🎯 Service target: {service_name}")

    if not input and live_metrics:
        input_json = {
            "service_name": service_name,
            "description": "Auto-generated input from --live-metrics mode"
        }
        fallback_input_path = "examples/autogen_input.json"
        Path(fallback_input_path).write_text(json.dumps(input_json, indent=2))
        input = fallback_input_path
        print(f"📄 [CLI] Auto-generated input saved to {fallback_input_path}")
        logger.info(f"📄 Auto-generated input written to {fallback_input_path}")
    elif not input:
        logger.error("❌ Must provide either --input or --live-metrics")
        print("❌ [CLI] Must provide either --input or --live-metrics")
        raise typer.Exit(code=1)

    # Automatically control RAG mode
    rag_enabled = mode == "saas"

    print(f"🚀 [CLI] Generating output to: {output}")
    logger.info(
        f"🚀 Starting generation: template='{template}', input='{input}', output='{output}', "
        f"explain={explain}, model='{model}', suggestions={'off' if no_suggestions else 'on'}, "
        f"temperature={temperature}, mode={mode}, rag={rag_enabled}"
    )

    try:
        generate_definitions(
            input_path=input,
            output_path=output,
            template=template,
            explain=explain,
            model=model,
            show_suggestions=not no_suggestions,
            adapter=metrics_adapter,
            temperature=temperature,
            rag=rag_enabled,
            mode=mode  # ✅ passed to downstream functions
        )
        logger.info("✅ Generation completed successfully.")
    except Exception as e:
        logger.error(f"❌ Error during generation: {e}")
        raise typer.Exit(code=1)

@app.command()
def validate(
    input: str = typer.Option(..., "-i", "--input", help="Path to output JSON to validate"),
    mode: str = typer.Option("combined", "-m", "--mode", help="Validation mode: 'slo', 'sli', 'alert', or 'combined'")
):
    """
    Validate output JSON against the SREx schema for SLOs, SLIs, Alerts, or full structure.
    """
    logger.info(f"🔍 Validating JSON file: '{input}' (mode: {mode})")
    try:
        with open(input, "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to read input: {e}")
        typer.echo(f"❌ Failed to read input: {e}")
        raise typer.Exit(code=1)

    is_valid, errors = validate_srex_output(data)

    if is_valid:
        typer.echo(f"✅ {mode.upper()} JSON is valid.")
        logger.info(f"✅ {mode.upper()} JSON is valid.")
    else:
        typer.echo(f"❌ {mode.upper()} JSON is invalid:")
        logger.warning(f"❌ {mode.upper()} JSON is invalid.")
        for field, msg in errors.items():
            typer.echo(f"  - {field}: {msg}")
            logger.warning(f"  - {field}: {msg}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()