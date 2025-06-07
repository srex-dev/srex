import os
import json
from cerberus import Validator
from core.input_schema import (
    observability_context_schema,
    availability_context_schema,
    alerting_context_schema,
    reliability_context_schema,
    automation_context_schema,
    slo_context_schema
)

# 🔁 Schema map for auto-detection
SCHEMA_MAP = {
    "observability": observability_context_schema,
    "availability": availability_context_schema,
    "alerting": alerting_context_schema,
    "reliability": reliability_context_schema,
    "automation": automation_context_schema,
    "slo": slo_context_schema
}

CONTEXT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "context-variants"))

def validate_context(json_data):
    for schema_name, schema in SCHEMA_MAP.items():
        validator = Validator(schema)
        if validator.validate(json_data):
            return schema_name, True, None
    return None, False, "No matching schema."

def validate_all_context_files():
    print("📂 Scanning all context files...\n")

    for filename in os.listdir(CONTEXT_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(CONTEXT_DIR, filename)
        print(f"🔍 Validating {filename}...")

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")
            continue

        schema_name, is_valid, error = validate_context(data)
        if is_valid:
            print(f"✅ Valid input. Matches `{schema_name}` schema.\n")
        else:
            print(f"❌ Invalid context: {filename}")
            print(error)
            print()

if __name__ == "__main__":
    validate_all_context_files()