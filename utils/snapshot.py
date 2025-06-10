import json
import time
import re
from pathlib import Path

def safe_filename(name):
    """
    Convert a string to a safe filename by replacing invalid characters.
    """
    return re.sub(r"[^\w\-\.]", "_", name)

def save_snapshot(service: str, data: dict):
    safe_service = safe_filename(service or "unknown")
    timestamp = time.strfttime("%Y%m%d_%H%M%S")
    path = Path("snapshots") / safe_service
    path.mkdir(parents=True, exist_ok=True)
    file = path / f"slo_snapshot_{timestamp}.json"
    file.write_text(json.dumps(data, indent=2))

    