from src.metrics.prometheus import PrometheusAdapter
from core.services.logging.logger import logger

def load_metrics_adapter(config):
    """Load and return the appropriate metrics adapter based on config."""
    provider = getattr(config, 'provider', None) or (config.get('provider') if isinstance(config, dict) else None)
    url = getattr(config, 'url', None) or (config.get('url') if isinstance(config, dict) else None)
    timeout = getattr(config, 'timeout', 30) if hasattr(config, 'timeout') else config.get('timeout', 30) if isinstance(config, dict) else 30

    logger.info(f"Loading metrics adapter with provider={provider}, url={url}, timeout={timeout}")

    if provider and provider.lower() == 'prometheus' and url:
        try:
            adapter = PrometheusAdapter(url=url, timeout=timeout)
            logger.info("Successfully created Prometheus adapter")
            return adapter
        except Exception as e:
            logger.error(f"Failed to create Prometheus adapter: {e}")
            return None
    else:
        logger.warning(f"Invalid metrics config: provider={provider}, url={url}")
        return None 