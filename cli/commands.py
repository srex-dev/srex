import typer
import json
from pathlib import Path
from core.prompt_engine import generate_definitions
from core.schema import validate_slo_json, validate_sli_json, validate_alert_json
from core.logger import logger

app = typer.Typer()

@app.command()
def generate(
    input: str = typer.Option(..., "-i", "--input", help="Input JSON file"),
    output: str = typer.Option(..., "-o", "--output", help="Output JSON file"),
    template: str = typer.Option("base", "-t", "--template", help="Prompt template name"),
    explain: bool = typer.Option(
        False,
        "--explain",
        help="Include LLM explanation in output",
        is_flag=True,
    ),
    model: str = typer.Option("ollama", "--model", help="LLM provider model to use (e.g. ollama, openai)")
):
    """
    Generate SLOs, SLIs, or alerts from the given input file using the selected prompt template.
    """
    logger.info(f"🚀 Starting generation: template='{template}', input='{input}', output='{output}', explain={explain}, model='{model}'")
    try:
        generate_definitions(input, output, template, explain, model=model)
        logger.info("✅ Generation completed successfully.")
    except Exception as e:
        logger.error(f"❌ Error during generation: {e}")
        raise typer.Exit(code=1)


@app.command()
def validate(
    input: str = typer.Option(..., "-i", "--input", help="JSON file to validate"),
    mode: str = typer.Option("slo", "-m", "--mode", help="Validation mode: 'slo', 'sli', or 'alert'")
):
    """
    Validate the provided JSON file against the SLO, SLI, or alert schema.
    """
    logger.info(f"🔍 Validating JSON: '{input}' as {mode.upper()}")
    try:
        with open(input, "r") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Error reading input file: {e}")
        typer.echo(f"Error reading input file: {e}")
        raise typer.Exit(code=1)

    if mode.lower() == "slo":
        is_valid, errors = validate_slo_json(data)
    elif mode.lower() == "sli":
        is_valid, errors = validate_sli_json(data)
    elif mode.lower() == "alert":
        is_valid, errors = validate_alert_json(data)
    else:
        typer.echo("❌ Invalid validation mode. Use 'slo', 'sli', or 'alert'.")
        raise typer.Exit(code=1)

    if is_valid:
        typer.echo(f"✅ {mode.upper()} JSON is valid.")
        logger.info(f"✅ {mode.upper()} JSON is valid.")
    else:
        typer.echo(f"❌ {mode.upper()} JSON is invalid:")
        logger.warning(f"❌ {mode.upper()} JSON failed validation.")
        for field, error in errors.items():
            typer.echo(f"  - {field}: {error}")
            logger.warning(f"  - {field}: {error}")
        raise typer.Exit(code=1)