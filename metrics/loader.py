# metrics/loader.py

from metrics.adapters.prometheus_adapter import PrometheusAdapter
from metrics.adapters.datadog_adapter import DatadogAdapter
from core.logger import logger


def load_metrics_adapter(config):
    provider = config.get("metrics_provider", "static").lower()

    if provider == "prometheus":
        return PrometheusAdapter(config["prometheus_url"])

    elif provider == "datadog":
        return DatadogAdapter(
            api_key=config["datadog_api_key"],
            app_key=config["datadog_app_key"],
            base_url=config.get("datadog_base_url", "https://api.datadoghq.com")
        )

    elif provider == "static":
        from metrics.adapters.static_adapter import StaticAdapter
        return StaticAdapter(config["static_path"])

    else:
        logger.error(f"❌ Unknown metrics provider: {provider}")
        raise ValueError(f"Unsupported provider: {provider}")