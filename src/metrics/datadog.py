from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.models import QuerySort, QueryOrder
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from .base import MetricsAdapter, SLIResult
from core.services.logging.logger import logger

class DatadogAdapter(MetricsAdapter):
    """Datadog metrics adapter implementation."""
    
    def __init__(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        self.configuration = Configuration(
            api_key=api_key,
            app_key=app_key,
            host=f"https://api.{site}"
        )
        self._validate_connection()

    def _validate_connection(self) -> bool:
        """Validate connection to Datadog."""
        try:
            with ApiClient(self.configuration) as api_client:
                api_instance = MonitorsApi(api_client)
                api_instance.list_monitors()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Datadog: {e}")
            return False

    def query_sli(self, component: str, sli_type: str) -> Optional[SLIResult]:
        """Query an SLI from Datadog."""
        try:
            # Map SLI types to Datadog queries
            query_map = {
                "availability": f"sum:http.requests{{component:{component},status_code:2xx}} / sum:http.requests{{component:{component}}} * 100",
                "latency": f"p95:http.request.duration{{component:{component}}}",
                "error_rate": f"sum:http.requests{{component:{component},status_code:5xx}} / sum:http.requests{{component:{component}}} * 100"
            }

            if sli_type not in query_map:
                logger.error(f"Unsupported SLI type: {sli_type}")
                return None

            # Execute query
            with ApiClient(self.configuration) as api_client:
                api_instance = MetricsApi(api_client)
                end_time = datetime.now()
                start_time = end_time - timedelta(minutes=5)
                
                response = api_instance.query_metrics(
                    _from=int(start_time.timestamp()),
                    to=int(end_time.timestamp()),
                    query=query_map[sli_type]
                )

                if not response.series:
                    logger.warning(f"No data found for {sli_type} on {component}")
                    return None

                value = float(response.series[0].pointlist[-1][1])
                
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
                    source="datadog",
                    timestamp=datetime.now().isoformat(),
                    metadata={
                        "component": component,
                        "sli_type": sli_type,
                        "datadog_site": self.configuration.host
                    }
                )

        except Exception as e:
            logger.error(f"Failed to query Datadog for {sli_type} on {component}: {e}")
            return None

    def get_available_components(self) -> List[str]:
        """Get list of available components from Datadog."""
        try:
            with ApiClient(self.configuration) as api_client:
                api_instance = MetricsApi(api_client)
                response = api_instance.list_metrics(
                    tag_filter="component:*"
                )
                return list(set(metric.split(":")[1] for metric in response.metrics))
        except Exception as e:
            logger.error(f"Failed to get components from Datadog: {e}")
            return []

    def get_available_sli_types(self) -> List[str]:
        """Get list of available SLI types."""
        return ["availability", "latency", "error_rate"]

    def validate_connection(self) -> bool:
        """Validate the connection to Datadog."""
        return self._validate_connection() 