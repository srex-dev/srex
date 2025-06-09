import json
import time
from pathlib import Path
from core.logger import logger


class StaticAdapter:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.static_data = self._load_static_data()

    def _load_static_data(self) -> dict:
        try:
            path = Path(self.file_path)
            if not path.exists():
                raise FileNotFoundError(f"Static SLI file not found: {self.file_path}")

            with open(path, "r") as f:
                data = json.load(f)
                logger.info(f"📄 Loaded static SLI data from {self.file_path}")
                if isinstance(data, list):
                    return {
                        entry["name"].lower(): entry
                        for entry in data
                        if "name" in entry and "value" in entry
                    }
                elif isinstance(data, dict):
                    return {
                        k.lower(): v for k, v in data.items()
                        if "value" in v
                    }
                else:
                    raise ValueError("Unexpected format in static SLI data.")
        except Exception as e:
            logger.error(f"❌ Failed to load static SLI file: {e}")
            return {}

    def query_sli(self, component: str, sli_type: str) -> dict:
        key = f"{sli_type}_{component}".lower()
        result = self.static_data.get(key)

        if not result:
            logger.warning(f"⚠️ No static SLI data for key: {key}")
            return None

        return {
            "name": key,
            "value": result["value"],
            "unit": result.get("unit", self._default_unit(sli_type)),
            "source": "static",
            "timestamp": int(time.time())
        }

    def load_all(self) -> list:
        return [
            {
                "name": key,
                "value": val["value"],
                "unit": val.get("unit", self._default_unit_from_name(key)),
                "source": "static",
                "timestamp": int(time.time())
            }
            for key, val in self.static_data.items()
        ]

    def _default_unit(self, sli_type: str) -> str:
        return {
            "availability": "percentage",
            "latency": "seconds",
            "error_rate": "percentage"
        }.get(sli_type, "value")

    def _default_unit_from_name(self, key: str) -> str:
        if "availability" in key:
            return "percentage"
        elif "latency" in key:
            return "seconds"
        elif "error_rate" in key:
            return "percentage"
        return "value"