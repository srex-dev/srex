from typing import Dict, List, Optional, Any
import importlib
import pkgutil
import inspect
from pathlib import Path
import yaml
from core.services.logging.logger import logger

class MetricAdapter:
    """Base class for metric adapters."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def query_metrics(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query metrics from the adapter."""
        raise NotImplementedError
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get adapter capabilities."""
        return {
            "name": self.__class__.__name__,
            "description": self.__class__.__doc__ or "",
            "supported_metrics": [],
            "config_schema": {}
        }

class PrometheusAdapter(MetricAdapter):
    """Adapter for Prometheus metrics."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.url = config.get("url", "http://localhost:9090")
        # TODO: Initialize Prometheus client
    
    def query_metrics(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        # TODO: Implement Prometheus query
        return []
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            **super().get_capabilities(),
            "supported_metrics": ["prometheus"],
            "config_schema": {
                "url": {"type": "string", "description": "Prometheus server URL"},
                "auth": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    }
                }
            }
        }

class CloudWatchAdapter(MetricAdapter):
    """Adapter for AWS CloudWatch metrics."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.region = config.get("region", "us-west-2")
        # TODO: Initialize AWS client
    
    def query_metrics(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        # TODO: Implement CloudWatch query
        return []
    
    def get_capabilities(self) -> Dict[str, Any]:
        return {
            **super().get_capabilities(),
            "supported_metrics": ["cloudwatch"],
            "config_schema": {
                "region": {"type": "string", "description": "AWS region"},
                "credentials": {
                    "type": "object",
                    "properties": {
                        "access_key": {"type": "string"},
                        "secret_key": {"type": "string"}
                    }
                }
            }
        }

def discover_adapters() -> List[Dict[str, Any]]:
    """
    Discover available metric adapters.
    
    Returns:
        List of adapter information dictionaries
    """
    try:
        adapters = []
        
        # Get all adapter classes
        adapter_classes = [
            cls for name, cls in globals().items()
            if inspect.isclass(cls)
            and issubclass(cls, MetricAdapter)
            and cls != MetricAdapter
        ]
        
        # Get capabilities for each adapter
        for adapter_class in adapter_classes:
            adapter = adapter_class()
            capabilities = adapter.get_capabilities()
            adapters.append(capabilities)
        
        return adapters
    
    except Exception as e:
        logger.error(f"Error discovering adapters: {str(e)}")
        raise

def configure_adapter(adapter_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configure a metric adapter.
    
    Args:
        adapter_name: Name of the adapter to configure
        config: Configuration dictionary
    
    Returns:
        Dictionary containing configuration status
    """
    try:
        # Find adapter class
        adapter_class = next(
            (cls for name, cls in globals().items()
             if inspect.isclass(cls)
             and issubclass(cls, MetricAdapter)
             and cls.__name__ == adapter_name),
            None
        )
        
        if not adapter_class:
            raise ValueError(f"Adapter not found: {adapter_name}")
        
        # Create adapter instance with config
        adapter = adapter_class(config)
        
        # Save configuration
        config_dir = Path("config/adapters")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / f"{adapter_name.lower()}.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        
        return {
            "status": "success",
            "adapter": adapter_name,
            "config_keys": list(config.keys())
        }
    
    except Exception as e:
        logger.error(f"Error configuring adapter: {str(e)}")
        raise

def get_adapter(adapter_name: str) -> Optional[MetricAdapter]:
    """
    Get a configured adapter instance.
    
    Args:
        adapter_name: Name of the adapter to get
    
    Returns:
        Configured adapter instance or None if not found
    """
    try:
        # Find adapter class
        adapter_class = next(
            (cls for name, cls in globals().items()
             if inspect.isclass(cls)
             and issubclass(cls, MetricAdapter)
             and cls.__name__ == adapter_name),
            None
        )
        
        if not adapter_class:
            return None
        
        # Load configuration
        config_file = Path("config/adapters") / f"{adapter_name.lower()}.yaml"
        if not config_file.exists():
            return None
        
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        
        # Create and return adapter instance
        return adapter_class(config)
    
    except Exception as e:
        logger.error(f"Error getting adapter: {str(e)}")
        return None 