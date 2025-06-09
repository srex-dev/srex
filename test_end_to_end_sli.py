# test_end_to_end_sli.py

import json
import logging
from core.prompt_engine import generate_definitions
from metrics.adapters.prometheus_adapter import PrometheusAdapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_full_pipeline():
    logging.info("🚀 Starting end-to-end SLI pipeline...")

    # Step 1: Live SLI fetch from Prometheus
    adapter = PrometheusAdapter("http://localhost:9090")
    component = "api"
    sli_types = ["availability", "latency", "error_rate"]

    sli_inputs = []
    for sli_type in sli_types:
        logging.info(f"🔍 Fetching SLI type '{sli_type}' for component '{component}'...")
        result = adapter.query_sli(component, sli_type)
        if result:
            logging.info(f"✅ Received SLI result: {result}")
            sli_inputs.append({
                "component": component,
                "sli_type": sli_type,
                "value": result["value"],
                "unit": result["unit"],
                "query": result["query"],
                "source": result["source"]
            })
        else:
            logging.warning(f"⚠️ No result for {sli_type}")

    if not sli_inputs:
        logging.error("❌ No SLI data retrieved. Aborting pipeline.")
        return

    # Step 2: Structure input schema
    input_json = {
        "service_name": "metrics-app",
        "description": "Test service collecting live metrics from Prometheus",
        "sli_inputs": sli_inputs
    }

    input_path = "examples/sli_live.json"
    output_path = "output/sli_live_output.json"

    # Step 3: Save input for debugging
    logging.info(f"💾 Saving input JSON to {input_path}")
    with open(input_path, "w") as f:
        json.dump(input_json, f, indent=2)

    # Step 4: Run prompt + validation pipeline
    logging.info("🧠 Invoking LLM prompt engine...")
    generate_definitions(
        input_path=input_path,
        output_path=output_path,
        template="sli",
        explain=True,
        model="ollama"
    )
    logging.info(f"✅ Output JSON written to {output_path}")

if __name__ == "__main__":
    run_full_pipeline()