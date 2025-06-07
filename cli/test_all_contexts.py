import json
from pathlib import Path
from core.prompt_engine import generate_prompt_response

CONTEXT_DIR = Path(__file__).resolve().parent.parent / "core" / "input" / "metrics"

def test_all():
    print("🚀 Running LLM Prompt Tests for All Input Contexts\n")

    json_files = list(CONTEXT_DIR.glob("*.json"))

    if not json_files:
        print(f"⚠️  No input context files found in {CONTEXT_DIR}")
        return

    for file_path in json_files:
        template = file_path.stem  # e.g., "observability" from "observability.json"
        print(f"\n🔍 Testing {template} from {file_path.name}...")

        try:
            input_data = json.loads(file_path.read_text())
        except Exception as e:
            print(f"❌ Failed to load {file_path.name}: {e}")
            continue

        try:
            result = generate_prompt_response(
                input_json=input_data,
                template=template,
                explain=True,
                model="ollama"
            )

            if isinstance(result, dict):
                print("✅ Valid JSON response received.")
                print(f"📦 Top-level keys: {list(result.keys())}")
            else:
                print("❌ Output is not a JSON object.")

        except Exception as e:
            print(f"❌ LLM processing error for {template}: {e}")

if __name__ == "__main__":
    test_all()