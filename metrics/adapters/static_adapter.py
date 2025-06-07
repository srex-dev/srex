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
                    # Convert list of dicts into a keyed lookup
                    return {
                        entry["name"].lower(): entry
                        for entry in data
                        if "name" in entry and "value" in entry
                    }
                elif isinstance(data, dict):
                    return data
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
            "unit": result.get("unit", "percentage"),
            "source": "static",
            "timestamp": int(time.time())
        }

    def load_all(self) -> list:
        """
        Return all static SLI entries as a list.
        """
        return [
            {
                "name": k,
                "value": v["value"],
                "unit": v.get("unit", "percentage"),
                "source": "static",
                "timestamp": int(time.time())
            }
            for k, v in self.static_data.items()
        ]