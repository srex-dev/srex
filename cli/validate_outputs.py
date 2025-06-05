import os
import json
from core.output_schema import validate_srex_output

# Adjust this to match where your LLM outputs are stored
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "outputs"))

def validate_all_outputs():
    print("🚀 Validating All Generated Outputs\n")

    for filename in os.listdir(OUTPUT_DIR):
        if not filename.endswith(".json"):
            continue

        filepath = os.path.join(OUTPUT_DIR, filename)
        print(f"🔍 Validating {filename}...")

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")
            continue

        is_valid, errors = validate_srex_output(data)
        if is_valid:
            print("✅ Output is valid.")
        else:
            print(f"❌ Output is invalid: {errors}")

if __name__ == "__main__":
    validate_all_outputs()