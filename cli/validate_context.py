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

def validate_context(json_data):
    for schema_name, schema in SCHEMA_MAP.items():
        validator = Validator(schema)
        if validator.validate(json_data):
            return schema_name, True, None
    return None, False, "No matching schema."

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python validate_context.py <context_file.json>")
        exit(1)

    context_path = sys.argv[1]

    try:
        with open(context_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"â Failed to load JSON file: {e}")
        exit(1)

    schema_name, is_valid, errors = validate_context(data)
    if is_valid:
        print(f"â Valid context. Matches `{schema_name}` schema.")
    else:
        print("â Invalid context:")
        print(json.dumps(errors, indent=2))
