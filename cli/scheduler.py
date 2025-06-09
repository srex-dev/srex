import sys
import os
import time
import logging
from datetime import datetime

# ✅ Fix: Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import CONFIG
from core.prompt_engine import generate_definitions
from metrics.loader import load_metrics_adapter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

INTERVAL = 300  # seconds

def periodic_task():
    timestamp = datetime.now().strftime("[%Y%m%d_%H%M%S]")
    logging.info(f"{timestamp} 🔄 Running periodic SLI check...")

    input_path = "examples/sli_live.json"
    output_path = "core/output/sli_live_output.json"
    template = "sli"

    try:
        generate_definitions(
            input_path=input_path,
            output_path=output_path,
            template=template,
            explain=True,
            model="ollama",
            show_suggestions=True
        )
    except Exception as e:
        logging.error(f"{timestamp} ❌ Error: {e}")

if __name__ == "__main__":
    logging.info("🚀 Starting periodic scheduler. Interval = %s seconds", INTERVAL)
    while True:
        periodic_task()
        time.sleep(INTERVAL)