# core/config.py

import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "metrics_provider": os.getenv("METRICS_PROVIDER", "static"),
    "prometheus_url": os.getenv("PROMETHEUS_URL", "http://localhost:9090"),
    "datadog_api_key": os.getenv("DATADOG_API_KEY", ""),
    "datadog_app_key": os.getenv("DATADOG_APP_KEY", ""),
    "datadog_base_url": os.getenv("DATADOG_BASE_URL", "https://api.datadoghq.com"),
    "static_path": os.getenv("STATIC_SLI_PATH", "/sli_static.json")
}