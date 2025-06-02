import typer
import yaml
from pathlib import Path
from core.prompt_engine import generate_slo_definitions
from core.schema import validate_slo_yaml
from core.logger import logger

app = typer.Typer()

@app.command()
def generate(
    input: str = typer.Option(..., "-i", "--input", help="Input YAML file"),
    output: str = typer.Option(..., "-o", "--output", help="Output YAML file"),
    template: str = typer.Option("base", "-t", "--template", help="Prompt template name"),
    explain: bool = typer.Option(
    False,
    "--explain",
    help="Include LLM explanation in output",
    is_flag=True,)
):
    """Generate SLOs from the given input file using a selected prompt template."""
    logger.info(f"Starting SLO generation with template='{template}', input='{input}', output='{output}', explain={explain}")
    try:
        generate_slo_definitions(input, output, template, explain, "ollama")
        logger.info("✅ SLO generation completed successfully.")
    except Exception as e:
        logger.error(f"❌ Error during SLO generation: {e}")
        raise typer.Exit(code=1)

@app.command()
def validate(
    input: str = typer.Option(..., "-i", "--input", help="YAML file to validate")
):
    """Validate the provided YAML input file against the SLO schema."""
    logger.info(f"Validating input YAML: {input}")
    try:
        with open(input, "r") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"❌ Error reading input file: {e}")
        typer.echo(f"Error reading input file: {e}")
        raise typer.Exit(code=1)

    is_valid, errors = validate_slo_yaml(data)
    if is_valid:
        typer.echo("✅ SLO YAML is valid.")
        logger.info("✅ SLO YAML is valid.")
    else:
        typer.echo("❌ SLO YAML is invalid:")
        logger.warning("❌ SLO YAML failed validation.")
        for field, error in errors.items():
            typer.echo(f"  - {field}: {error}")
            logger.warning(f"  - {field}: {error}")
        raise typer.Exit(code=1)