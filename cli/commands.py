# cli/commands.py
import typer
from core.prompt_engine import generate_slo_definitions
from pathlib import Path

app = typer.Typer(help="SREx CLI - Generate SLO definitions from infrastructure specs.")

@app.command("gen")
def generate(
    input_file: Path = typer.Option(..., "-i", "--input", help="Path to input YAML"),
    output_file: Path = typer.Option(..., "-o", "--output", help="Path to output YAML")
):
    """
    Generate SLO definitions based on the input service specification.
    """
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        generate_slo_definitions(input_file, output_file)
        typer.echo(f"✅ SLO definitions written to: {output_file}")
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(code=1)