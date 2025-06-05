# cli/test_selected_contexts.py

import os
import json
from pathlib import Path
from cerberus import Validator
from core.input_schema import automation_context_schema, availability_context_schema
from core.prompt_engine import generate_prompt_response
from core.output_schema import validate_srex_output

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTEXT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "examples", "context-variants"))
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "prompt_templates"))

SELECTED_CONTEXTS = {
    "automation": {
        "schema": automation_context_schema,
        "filename": "automation.json",
        "template": "automation"
    },
    "availability": {
        "schema": availability_context_schema,
        "filename": "availability.json",
        "template": "availability"
    }
}

def validate_with_schema(data, schema):
    validator = Validator(schema)
    return validator.validate(data), validator.errors

def test_selected_contexts():
    for name, config in SELECTED_CONTEXTS.items():
        print(f"\n🔍 Validating {config['filename']}...")
        context_path = os.path.join(CONTEXT_DIR, config["filename"])

        if not os.path.exists(context_path):
            print(f"❌ File not found: {context_path}")
            continue

        with open(context_path) as f:
            data = json.load(f)

        is_valid, errors = validate_with_schema(data, config["schema"])
        if not is_valid:
            print(f"❌ Schema validation failed for {name}: {errors}")
            continue
        print(f"✅ Input schema matched: {name}")

        template_file = os.path.join(TEMPLATE_DIR, f"{config['template']}.txt")
        if not os.path.exists(template_file):
            print(f"⚠️ Skipping — template not found: {template_file}")
            continue

        try:
            result = generate_prompt_response(
                input_json=data,
                template=config["template"],
                schema_type=name
         )
            
            is_valid_out, errors_out = validate_srex_output(result, schema_type=name)
            if is_valid_out:
                print(f"🧠 Output validated successfully for {name}.")
            else:
                print(f"❌ Output validation failed for {name}: {errors_out}")
        except Exception as e:
            print(f"❌ Error processing {name}: {e}")

if __name__ == "__main__":
    test_selected_contexts()