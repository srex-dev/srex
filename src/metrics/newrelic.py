from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from core.logger import setup_logger
from src.metrics.base import MetricsAdapter, SLIResult

logger = setup_logger(__name__)

@dataclass
class NewRelicConfig:
    """New Relic configuration."""
    api_key: str
    account_id: str
    region: str = "US"

class NewRelicAdapter(MetricsAdapter):
    """New Relic metrics adapter."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize New Relic adapter."""
        self.config = NewRelicConfig(**config)
        self._client = None
        self._validate_connection()
    
    def _validate_connection(self) -> bool:
        """Validate connection to New Relic."""
        try:
            import newrelic.agent
            newrelic.agent.initialize(self.config.api_key)
            self._client = newrelic.agent
            return True
        except Exception as e:
            logger.error(f"Failed to connect to New Relic: {str(e)}")
            return False
    
    def query_sli(self, component: str, sli_type: str) -> Optional[SLIResult]:
        """Query SLI from New Relic."""
        try:
            # Map SLI types to New Relic queries
            query_map = {
                "availability": f"SELECT percentage(count(*), WHERE http.status_code < 500) FROM Transaction WHERE appName = '{component}'",
                "latency": f"SELECT average(duration) FROM Transaction WHERE appName = '{component}'",
                "error_rate": f"SELECT percentage(count(*), WHERE error IS NOT NULL) FROM Transaction WHERE appName = '{component}'",
                "throughput": f"SELECT rate(count(*)) FROM Transaction WHERE appName = '{component}'"
            }
            
            if sli_type not in query_map:
                logger.warning(f"Unsupported SLI type: {sli_type}")
                return None
            
            # Execute query
            result = self._client.query(query_map[sli_type])
            
            # Map result to SLIResult
            value = float(result[0]['result'])
            unit = self._get_unit(sli_type)
            
            return SLIResult(
                value=value,
                unit=unit,
                source="newrelic",
                timestamp=result[0]['timestamp']
            )
        except Exception as e:
            logger.error(f"Error querying New Relic: {str(e)}")
            return None
    
    def get_available_components(self) -> List[str]:
        """Get list of available components."""
        try:
            # Query New Relic for available applications
            result = self._client.query("SELECT uniques(appName) FROM Transaction")
            return [app['name'] for app in result[0]['result']]
        except Exception as e:
            logger.error(f"Error getting components from New Relic: {str(e)}")
            return []
    
    def get_available_sli_types(self) -> List[str]:
        """Get list of available SLI types."""
        return ["availability", "latency", "error_rate", "throughput"]
    
    def _get_unit(self, sli_type: str) -> str:
        """Get unit for SLI type."""
        unit_map = {
            "availability": "percent",
            "latency": "milliseconds",
            "error_rate": "percent",
            "throughput": "requests_per_second"
        }
        return unit_map.get(sli_type, "unknown")
    
    def validate_connection(self) -> bool:
        """Validate connection to New Relic."""
        return self._validate_connection() 