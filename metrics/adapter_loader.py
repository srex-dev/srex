import json
from pathlib import Path
from metrics.adapters.prometheus_adapter import PrometheusAdapter
from metrics.adapters.datadog_adapter import DatadogAdapter
from core.logger import logger

def load_adapter(config_path: str = "config.json"):
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path) as f:
        config = json.load(f)

    adapter_type = config.get("adapter")
    if adapter_type == "prometheus":
        prom_conf = config.get("prometheus", {})
        return PrometheusAdapter(base_url=prom_conf.get("base_url"))
    elif adapter_type == "datadog":
        dd_conf = config.get("datadog", {})
        return DatadogAdapter(
            api_key=dd_conf.get("api_key"),
            app_key=dd_conf.get("app_key"),
            base_url=dd_conf.get("base_url", "https://api.datadoghq.com")
        )
    else:
        raise ValueError(f"Unsupported adapter type: {adapter_type}")