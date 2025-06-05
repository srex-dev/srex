import os
import json
from cerberus import Validator
from core.input_schema import (
    observability_context_schema,
    availability_context_schema,
    alerting_context_schema,
    reliability_context_schema,
    frontend_web_app_context_schema,
    sli_context_schema,
    automation_context_schema
)

SCHEMA_MAP = {
    "observability": observability_context_schema,
    "availability": availability_context_schema,
    "alerting": alerting_context_schema,
    "reliability": reliability_context_schema,
    "sli": sli_context_schema,
    "frontend-web-app": frontend_web_app_context_schema,
    "automation": automation_context_schema
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTEXT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "examples", "context-variants"))

def validate_with_schema(data):
    for name, schema in SCHEMA_MAP.items():
        validator = Validator(schema)
        if validator.validate(data):
            return name, True, None
    return None, False, "No matching schema."

def validate_all_contexts():
    for filename in os.listdir(CONTEXT_DIR):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(CONTEXT_DIR, filename)
        print(f"\nð Validating {filename}...")

        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"â Failed to load JSON: {e}")
            continue

        schema_name, is_valid, error = validate_with_schema(data)
        if is_valid:
            print(f"â Valid context. Matches `{schema_name}` schema.")
        else:
            print("â Invalid context:")
            print(json.dumps(error, indent=2))

if __name__ == "__main__":
    validate_all_contexts()
