# metrics/adapter_loader.py

from metrics.adapters.prometheus_adapter import PrometheusAdapter
from metrics.adapters.datadog_adapter import DatadogAdapter
from core.logger import logger


def get_adapter(config: dict):
    """
    Load the appropriate SLI adapter based on config.

    Expected keys:
    - type: "prometheus" or "datadog"
    - endpoint or base_url
    - api_key and app_key (for Datadog only)
    """
    adapter_type = config.get("type", "").lower()

    if adapter_type == "prometheus":
        base_url = config.get("endpoint") or config.get("base_url")
        if not base_url:
            raise ValueError("Prometheus config missing 'endpoint' or 'base_url'")
        logger.info("🔧 Using PrometheusAdapter")
        return PrometheusAdapter(base_url=base_url)

    elif adapter_type == "datadog":
        api_key = config.get("api_key")
        app_key = config.get("app_key")
        base_url = config.get("endpoint") or config.get("base_url", "https://api.datadoghq.com/api/v1")

        if not all([api_key, app_key]):
            raise ValueError("Datadog config requires 'api_key' and 'app_key'")
        logger.info("🔧 Using DatadogAdapter")
        return DatadogAdapter(api_key=api_key, app_key=app_key, base_url=base_url)

    else:
        raise ValueError(f"Unsupported adapter type: {adapter_type}")
