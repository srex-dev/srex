# core/prompt_engine.py
from pathlib import Path
import yaml

def generate_slo_definitions(input_file: Path, output_file: Path):
    with open(input_file, 'r') as f:
        service_spec = yaml.safe_load(f)

    slo_definitions = {
        "service": service_spec.get("name", "unknown-service"),
        "slos": [
            {"metric": "availability", "target": "99.9%"},
            {"metric": "latency", "target": "< 300ms"}
        ]
    }

    with open(output_file, 'w') as f:
        yaml.dump(slo_definitions, f)