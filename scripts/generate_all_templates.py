import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))  # 👈 Add project root to sys.path

import typer
import yaml
import json
import logging
from core.prompt_engine import generate_slo_definitions
from concurrent.futures import ThreadPoolExecutor, as_completed
app = typer.Typer()

# Setup logging
log_file = Path("outputs/generation.log")
log_file.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# All available prompt templates
TEMPLATES = ["base", "availability", "latency", "error_budget", "database", "queue"]

def generate_single_template(input_path, output_dir, tmpl, format):
    output_file = output_dir / f"slo_{tmpl}.{format}"
    try:
        logging.info(f"🚀 Generating SLO using template: {tmpl}")
        generate_slo_definitions(
            input_path=str(input_path),
            output_path=str(output_file),
            template=tmpl,
            explain=True,
            provider="ollama"
        )
        with open(output_file, "r") as f:
            return tmpl, yaml.safe_load(f)
    except Exception as e:
        logging.error(f"❌ Failed for template '{tmpl}': {e}")
        return tmpl, None

@app.command()
def generate(
    input_path: Path,
    output_dir: Path,
    template: str = typer.Option("all", "--template", "-t", help="Specify a template or 'all'"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format: yaml or json"),
    parallel: bool = typer.Option(False, "--parallel", help="Enable parallel generation")
):
    """
    Generate SLOs for all or one template using the provided input YAML.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_templates = TEMPLATES if template == "all" else [template]
    combined_output = {}

    if parallel:
        logging.info("⚡ Running in parallel mode...")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(generate_single_template, input_path, output_dir, tmpl, format): tmpl
                for tmpl in selected_templates
            }
            for future in as_completed(futures):
                tmpl, result = future.result()
                if result:
                    combined_output[tmpl] = result
    else:
        for tmpl in selected_templates:
            tmpl, result = generate_single_template(input_path, output_dir, tmpl, format)
            if result:
                combined_output[tmpl] = result

    if format == "json":
        combined_file = output_dir / "slo_combined.json"
        with open(combined_file, "w") as f:
            json.dump(combined_output, f, indent=2)
        logging.info(f"✅ Combined JSON output saved to {combined_file}")
    else:
        combined_file = output_dir / "slo_combined.yaml"
        with open(combined_file, "w") as f:
            yaml.dump(combined_output, f)
        logging.info(f"✅ Combined YAML output saved to {combined_file}")

if __name__ == "__main__":
    app()