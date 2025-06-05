import typer
import json
from pathlib import Path
from core.prompt_engine import generate_definitions
from core.output_schema import validate_srex_output
from core.logger import logger

app = typer.Typer()

@app.command()
def generate(
    input: str = typer.Option(..., "-i", "--input", help="Input JSON file"),
    output: str = typer.Option(..., "-o", "--output", help="Output JSON file"),
    template: str = typer.Option("base", "-t", "--template", help="Prompt template to use (e.g., reliability, automation)"),
    explain: bool = typer.Option(False, "--explain", help="Include LLM explanation in output"),
    no_suggestions: bool = typer.Option(False, "--no-suggestions", help="Suppress LLM suggestions in output"),
    model: str = typer.Option("ollama", "--model", help="LLM backend to use (ollama, openai, etc.)")
):
    """
    Generate SLOs, SLIs, and alerting rules using the selected prompt template.
    """
    logger.info(
        f"🚀 Starting generation: template='{template}', input='{input}', output='{output}', "
        f"explain={explain}, model='{model}', suggestions={'off' if no_suggestions else 'on'}"
    )
    try:
        generate_definitions(
            input_path=input,
            output_path=output,
            template=template,
            explain=explain,
            model=model,
            show_suggestions=not no_suggestions
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