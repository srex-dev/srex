import subprocess
import os

TEMPLATES = [
    "observability",
    "reliability",
    "availability",
    "automation",
    "alerting"
]

EXAMPLES_DIR = "examples/context-variants"
OUTPUT_DIR = "outputs"
MODEL = "ollama"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_test(template):
    input_file = os.path.join(EXAMPLES_DIR, f"{template}.json")
    output_file = os.path.join(OUTPUT_DIR, f"{template}.json")

    cmd = [
        "python", "main.py", "generate",
        "-i", input_file,
        "-o", output_file,
        "-t", template,
        "--model", MODEL,
        "--explain",
        "--no-suggestions"
    ]

    print(f"\n🚀 Testing template: {template}")
    print("🔧 Running:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Test failed.")
            print(result.stderr)
        else:
            print("✅ Test passed.")
    except Exception as e:
        print(f"❌ Exception occurred: {e}")


if __name__ == "__main__":
    for template in TEMPLATES:
        run_test(template)