import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .base import MetricsAdapter, SLIResult
from core.services.logging.logger import logger

PROMETHEUS_TIMEFRAME_MAP = {
    "3m": "3m",
    "5min": "5m",
    "30min": "30m",
    "1hr": "1h",
    "1d": "1d",
    "7d": "7d",
    "30d": "30d",
}

def to_prometheus_timeframe(timeframe: str) -> str:
    return PROMETHEUS_TIMEFRAME_MAP.get(timeframe, "5m")

class PrometheusAdapter(MetricsAdapter):
    """Prometheus metrics adapter implementation."""
    
    def __init__(self, url: str, timeout: int = 30, verify_ssl: bool = True):
        self.url = url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._validate_connection()

    def _validate_connection(self) -> bool:
        """Validate connection to Prometheus."""
        try:
            response = requests.get(
                f"{self.url}/api/v1/status/config",
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Prometheus at {self.url}: {e}")
            return False

    def query_sli(self, component: str, sli_type: str, timeframe: str = "3m") -> Optional[SLIResult]:
        """Query an SLI from Prometheus."""
        try:
            prom_timeframe = to_prometheus_timeframe(timeframe)
            # Map SLI types to Prometheus queries
            query_map = {
                "availability": f'sum(rate(http_requests_total{{component="{component}",status=~"2.."}}[{prom_timeframe}])) / sum(rate(http_requests_total{{component="{component}"}}[{prom_timeframe}])) * 100',
                "latency": f'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{{component="{component}"}}[{prom_timeframe}])) by (le))',
                "error_rate": f'sum(rate(http_requests_total{{component="{component}",status=~"5.."}}[{prom_timeframe}])) / sum(rate(http_requests_total{{component="{component}"}}[{prom_timeframe}])) * 100'
            }

            if sli_type not in query_map:
                logger.error(f"Unsupported SLI type: {sli_type}")
                return None

            # Execute query
            response = requests.get(
                f"{self.url}/api/v1/query",
                params={"query": query_map[sli_type]},
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            result = response.json()

            if not result.get("data", {}).get("result"):
                logger.warning(f"No data found for {sli_type} on {component}")
                return None

            value = float(result["data"]["result"][0]["value"][1])
            
            # Map units based on SLI type
            unit_map = {
                "availability": "percent",
                "latency": "seconds",
                "error_rate": "percent"
            }

            return SLIResult(
                value=value,
                unit=unit_map[sli_type],
                query=query_map[sli_type],
                source="prometheus",
                timestamp=datetime.now().isoformat(),
                metadata={
                    "component": component,
                    "sli_type": sli_type,
                    "prometheus_url": self.url
                }
            )

        except Exception as e:
            logger.error(f"Failed to query Prometheus for {sli_type} on {component}: {e}")
            return None

    def get_available_components(self) -> List[str]:
        """Get list of available components from Prometheus."""
        try:
            response = requests.get(
                f"{self.url}/api/v1/label/component/values",
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()["data"]
        except Exception as e:
            logger.error(f"Failed to get components from Prometheus: {e}")
            return []

    def get_available_sli_types(self) -> List[str]:
        """Get list of available SLI types."""
        return ["availability", "latency", "error_rate"]

    def validate_connection(self) -> bool:
        """Validate the connection to Prometheus."""
        return self._validate_connection() 