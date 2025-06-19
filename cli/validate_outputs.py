import os
import json
from backend.core.output_schema import (
    validate_observability_output,
    validate_alerting_output,
    validate_automation_output,
    validate_availability_output,
    validate_reliability_output,
    validate_slo_output
)

# Map schema type to validator function
VALIDATORS = {
    "observability": validate_observability_output,
    "alerting": validate_alerting_output,
    "automation": validate_automation_output,
    "availability": validate_availability_output,
    "reliability": validate_reliability_output,
    "slo": validate_slo_output
}

# Adjust this to match where your LLM outputs are stored
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "outputs"))

def infer_schema_type(filename):
    for key in VALIDATORS:
        if key in filename:
            return key
    return None

def validate_all_outputs():
    print("🚀 Validating All Generated Outputs\n")

    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        print(f"🔍 Validating {filename}...")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")
            continue

        schema_type = infer_schema_type(filename)
        if not schema_type:
            print("⚠️  Skipping — unable to infer schema type.")
            continue

        validator = VALIDATORS[schema_type]
        is_valid, errors = validator(data)

        if is_valid:
            print("✅ Output is valid.")
        else:
            print(f"❌ Output is invalid:\n{json.dumps(errors, indent=2)}")

if __name__ == "__main__":
    validate_all_outputs()