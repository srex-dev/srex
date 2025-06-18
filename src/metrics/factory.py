from typing import Dict, Any, Optional, List
from core.logger import setup_logger
from src.metrics.base import MetricsAdapter
from src.metrics.prometheus import PrometheusAdapter
from src.metrics.datadog import DatadogAdapter
from src.metrics.newrelic import NewRelicAdapter
from core.config import CONFIG

logger = setup_logger(__name__)

class MetricsAdapterFactory:
    """Factory for creating metrics adapters."""
    
    _adapters: Dict[str, type] = {
        "prometheus": PrometheusAdapter,
        "datadog": DatadogAdapter,
        "newrelic": NewRelicAdapter
    }
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: type) -> None:
        """Register a new metrics adapter."""
        if not issubclass(adapter_class, MetricsAdapter):
            raise ValueError(f"Adapter class must inherit from MetricsAdapter")
        cls._adapters[name] = adapter_class
    
    @classmethod
    def create_adapter(cls, adapter_type: str, config: Dict[str, Any]) -> MetricsAdapter:
        """Create a metrics adapter instance."""
        if adapter_type not in cls._adapters:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
        
        try:
            return cls._adapters[adapter_type](config)
        except Exception as e:
            logger.error(f"Failed to create {adapter_type} adapter: {str(e)}")
            raise
    
    @classmethod
    def get_available_adapters(cls) -> List[str]:
        """Get list of available adapter names."""
        return list(cls._adapters.keys()) 