import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path("config.json")

if CONFIG_PATH.exists():
    CONFIG = json.loads(CONFIG_PATH.read_text())
else:
    CONFIG = {
        "metrics_provider": os.getenv("METRICS_PROVIDER", "static"),
        "prometheus": {
            "base_url": os.getenv("PROMETHEUS_URL", "http://localhost:9090")
        },
        "datadog": {
            "api_key": os.getenv("DATADOG_API_KEY", ""),
            "app_key": os.getenv("DATADOG_APP_KEY", ""),
            "base_url": os.getenv("DATADOG_BASE_URL", "https://api.datadoghq.com")
        },
        "static_path": os.getenv("STATIC_SLI_PATH", "examples/static_sli.json")
    }