# metrics/adapters/prometheus_adapter.py

import requests
import time
import json
from core.logger import logger


class PrometheusAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        logger.info(f"🔌 PrometheusAdapter initialized with base URL: {self.base_url}")

    def query_sli(self, component: str, sli_type: str) -> dict:
        """
        Query Prometheus for a given SLI type (e.g. availability, latency, error_rate)
        """
        query = self._build_query(component, sli_type)
        if not query:
            logger.warning(f"⚠️ Unsupported SLI type: {sli_type}")
            return None

        logger.info(f"📡 Executing Prometheus query for {sli_type} on component '{component}':\n{query}")
        url = f"{self.base_url}/api/v1/query"
        try:
            response = requests.get(url, params={"query": query})
            logger.debug(f"🔁 HTTP GET {response.url}")
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success":
                logger.error(f"❌ Prometheus returned non-success status: {data.get('status')}")
                return None

            result = data.get("data", {}).get("result", [])
            if not result:
                logger.warning(f"⚠️ No Prometheus result for {sli_type} on '{component}'")
                return None

            value = float(result[0]["value"][1])
            metric_info = {
                "name": f"{sli_type}_{component}",
                "value": value,
                "unit": self._get_unit(sli_type),
                "source": "prometheus",
                "timestamp": int(time.time()),
                "query": query,
                "raw_result": result[0]
            }

            logger.info(f"✅ SLI result for {component} ({sli_type}): {value} {metric_info['unit']}")
            return metric_info

        except requests.RequestException as e:
            logger.error(f"❌ Prometheus API request failed: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"❌ Failed to parse Prometheus result: {e}")
            logger.debug(f"🧪 Raw Prometheus response:\n{json.dumps(data, indent=2)}")
            return None

    def _build_query(self, component: str, sli_type: str) -> str:
        if sli_type == "availability":
            return (
                f'sum(rate(http_requests_total{{component="{component}",status=~"2.."}}[5m])) / '
                f'sum(rate(http_requests_total{{component="{component}"}}[5m]))'
            )
        elif sli_type == "latency":
            return (
                f'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket'
                f'{{component="{component}"}}[5m])) by (le))'
            )
        elif sli_type == "error_rate":
            return (
                f'sum(rate(http_requests_total{{component="{component}",status=~"5.."}}[5m])) / '
                f'sum(rate(http_requests_total{{component="{component}"}}[5m]))'
            )
        return None

    def _get_unit(self, sli_type: str) -> str:
        return {
            "availability": "percentage",
            "latency": "seconds",
            "error_rate": "percentage"
        }.get(sli_type, "value")