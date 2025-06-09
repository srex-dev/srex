# metrics/adapters/datadog_adapter.py

import time
import requests
from core.logger import logger


class DatadogAdapter:
    def __init__(self, api_key: str, app_key: str, base_url: str = "https://api.datadoghq.com"):
        self.api_key = api_key
        self.app_key = app_key
        self.base_url = base_url.rstrip("/")
        logger.info("🔌 DatadogAdapter initialized")

    def query_sli(self, component: str, sli_type: str) -> dict:
        metric, agg = self._build_query(component, sli_type)
        if not metric:
            logger.warning(f"⚠️ Unsupported SLI type: {sli_type}")
            return None

        end_time = int(time.time())
        start_time = end_time - 300  # last 5 minutes

        url = f"{self.base_url}/api/v1/query"
        params = {
            "from": start_time,
            "to": end_time,
            "query": f"{agg}:{metric}{{component:{component}}}.rollup(avg,60)"
        }
        headers = {
            "DD-API-KEY": self.api_key,
            "DD-APPLICATION-KEY": self.app_key
        }

        logger.info(f"📡 Querying Datadog: {params['query']}")
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            series = data.get("series", [])
            if not series or "pointlist" not in series[0] or not series[0]["pointlist"]:
                logger.warning(f"⚠️ No Datadog result for {sli_type} on '{component}'")
                return None

            last_point = series[0]["pointlist"][-1][1]
            value = float(last_point)
            return {
                "name": f"{sli_type}_{component}",
                "value": value,
                "unit": self._get_unit(sli_type),
                "source": "datadog",
                "timestamp": int(time.time()),
                "query": params["query"]
            }

        except Exception as e:
            logger.error(f"❌ Datadog query failed: {e}")
            return None

    def _build_query(self, component: str, sli_type: str):
        if sli_type == "availability":
            return "http.requests.total", "sum"
        elif sli_type == "latency":
            return "http.request.duration", "avg"
        elif sli_type == "error_rate":
            return "http.requests.error", "sum"
        return None, None

    def _get_unit(self, sli_type: str) -> str:
        return {
            "availability": "percentage",
            "latency": "seconds",
            "error_rate": "percentage"
        }.get(sli_type, "value")