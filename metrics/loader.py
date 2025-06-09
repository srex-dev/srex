from metrics.adapters.prometheus_adapter import PrometheusAdapter
from metrics.adapters.datadog_adapter import DatadogAdapter
from metrics.adapters.static_adapter import StaticAdapter

def load_metrics_adapter(config):
    provider = config.get("metrics_provider", "static")

    if provider == "prometheus":
        base_url = config["prometheus"]["base_url"]
        return PrometheusAdapter(base_url)

    elif provider == "datadog":
        return DatadogAdapter(
            api_key=config["datadog"]["api_key"],
            app_key=config["datadog"]["app_key"],
            base_url=config["datadog"].get("base_url", "https://api.datadoghq.com")
        )

    elif provider == "static":
        return StaticAdapter(config["static_path"])

    raise ValueError(f"Unknown metrics provider: {provider}")