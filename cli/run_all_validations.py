# cli/run_all_validations.py

import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    "validate_context.py",
    "validate_inputs.py",
    "validate_outputs.py",
    "test_all_contexts.py"
]

def run_script(script_name):
    path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(path):
        print(f"❌ Script not found: {script_name}")
        return

    print(f"\n🚀 Running: {script_name}")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(f"⚠️ Errors from {script_name}:\n{result.stderr}")

def main():
    print("🔁 Starting Full Validation Pipeline...\n")
    for script in SCRIPTS:
        run_script(script)
    print("\n✅ All scripts executed.\n")

if __name__ == "__main__":
    main()