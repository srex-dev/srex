# cli/commands.py
import typer
from core.prompt_engine import generate_slo_definitions, validate_slo_definitions

app = typer.Typer()

@app.command()
def generate(
    input: str = typer.Option(..., "-i", "--input", help="Input YAML file"),
    output: str = typer.Option(..., "-o", "--output", help="Output YAML file"),
):
    """Generate SLOs from the given input file."""
    generate_slo_definitions(input, output)

@app.command()
def validate(
    input: str = typer.Option(..., "-i", "--input", help="YAML file to validate"),
):
    """Validate the provided YAML input file."""
    validate_slo_definitions(input)