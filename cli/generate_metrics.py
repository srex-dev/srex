# cli/generate_metrics.py

import json
from pathlib import Path
import typer
from backend.core.config import CONFIG
from metrics.loader import load_metrics_adapter
from backend.core.services.prompt.prompt_engine import generate_prompt_response
from core.services.logging.logger import logger

app = typer.Typer()

@app.command()
def generate(
    input_path: str = typer.Argument(..., help="Path to input JSON file"),
    output_path: str = typer.Argument(..., help="Path to write output JSON"),
    template: str = typer.Option("availability", "--template", "-t", help="Template to use"),
    explain: bool = typer.Option(True, "--explain/--no-explain", help="Include explanations")
):
    """Generate metrics with live SLI injection and LLM prompt generation"""
    try:
        logger.info(f"📥 Loading input file: {input_path}")
        input_data = Path(input_path).read_text()
        input_json = json.loads(input_data)

        adapter = load_metrics_adapter(CONFIG)

        sli_results = []
        for obj in input_json.get("objectives", []):
            sli = adapter.query_sli(
                component=obj["component"],
                sli_type=obj.get("sli_type", "availability"),
                timeframe="3m"
            )
            if sli:
                sli_results.append(sli)

        if not sli_results:
            logger.warning("⚠️ No live SLI data found. Using static fallback.")
            fallback_adapter = load_metrics_adapter({
                "metrics_provider": "static",
                "static_path": CONFIG.get("static_path")
            })
            sli_results = fallback_adapter.load_all()

        input_json["live_sli_data"] = sli_results
        logger.info(f"📊 Injected {len(sli_results)} SLI result(s).")

        json_data = generate_prompt_response(input_json, template=template, explain=explain)

        Path(output_path).write_text(json.dumps(json_data, indent=2))
        logger.info(f"✅ Output JSON written to {output_path}")

        print("\n📄 JSON Output:\n" + "-" * 50)
        print(json.dumps(json_data, indent=2))

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    app()