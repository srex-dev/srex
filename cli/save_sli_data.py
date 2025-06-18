# cli/save_sli_data.py

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import argparse

# ✅ Ensure core/ is in the module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import CONFIG
from metrics.loader import load_metrics_adapter
from core.services.logging.logger import logger
from core.services.prompt.prompt_engine import generate_prompt_response


def save_live_sli(service_name="metrics-app", output_path="examples/sli_live.json"):
    timestamp = int(time.time())
    readable_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{readable_time}] 🚀 Starting SLI fetch and save...")

    adapter = load_metrics_adapter(CONFIG)
    sli_types = ["availability", "latency", "error_rate"]
    sli_inputs = []

    for sli_type in sli_types:
        logger.info(f"🔍 Fetching {sli_type} for {service_name}...")
        try:
            result = adapter.query_sli(component="api", sli_type=sli_type, timeframe="3m")
            if result:
                logger.info(f"✅ {sli_type}: {result}")
                sli_inputs.append({
                    "component": "api",
                    "sli_type": sli_type,
                    "value": result["value"],
                    "unit": result["unit"],
                    "query": result["query"],
                    "source": result["source"],
                    "timestamp": timestamp
                })
            else:
                logger.warning(f"⚠️ No result for {sli_type}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch {sli_type}: {e}")

    output = {
        "service_name": service_name,
        "description": "Test service collecting live metrics from Prometheus",
        "sli_inputs": sli_inputs,
        "generated_at": readable_time
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(output, indent=2))
    logger.info(f"💾 Saved SLI data to {output_path}")


def run_periodically(interval: int):
    while True:
        save_live_sli()
        logger.info(f"⏱️ Sleeping for {interval} seconds...\n")
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and save SLI data from metrics adapter.")
    parser.add_argument("--interval", type=int, help="Run periodically every N seconds")
    args = parser.parse_args()

    if args.interval:
        run_periodically(args.interval)
    else:
        save_live_sli()