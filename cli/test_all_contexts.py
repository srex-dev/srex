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
from core.prompt_engine import generate_prompt_response

# Map schema names to their validation schemas
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
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "prompt_templates"))

def validate_with_schema(data):
    for name, schema in SCHEMA_MAP.items():
        validator = Validator(schema)
        if validator.validate(data):
            return name, True, None
    return None, False, "No matching schema."

def test_all_contexts():
    for filename in os.listdir(CONTEXT_DIR):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(CONTEXT_DIR, filename)
        print(f"\n🔍 Validating {filename}...")

        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load JSON: {e}")
            continue

        schema_name, is_valid, error = validate_with_schema(data)
        if not is_valid:
            print(f"❌ Schema validation failed: {error}")
            continue

        print(f"✅ Input schema matched: {schema_name}")

        try:
            template_file = os.path.abspath(os.path.join(TEMPLATE_DIR, f"{schema_name}.txt"))
            print(f"📄 Looking for template: {template_file}")
            if not os.path.exists(template_file):
                print(f"⚠️ Skipping LLM generation — template not found: {template_file}")
                continue

            result = generate_prompt_response(
                data,
                template=template_file,        # full path to template
                schema_type=schema_name        # key for selecting output schema
            )
            print(f"🧠 Prompt engine responded successfully.")

        except Exception as e:
            print(f"❌ Prompt engine failed: {e}")

if __name__ == "__main__":
    test_all_contexts()