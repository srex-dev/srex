import subprocess
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_script(description, command):
    print(f"\n🚀 {description}")
    print(f"🔧 Running: {command}")
    result = subprocess.run(command, shell=True, cwd=PROJECT_ROOT, capture_output=True, text=True)
    print(f"📤 Output:\n{result.stdout}")
    if result.stderr:
        print(f"⚠️ Errors:\n{result.stderr}")

if __name__ == "__main__":
    run_script("Test All Contexts with Prompt Engine", "PYTHONPATH=. python cli/test_all_contexts.py")
    run_script("Validate All Contexts for Schema Match", "PYTHONPATH=. python cli/validate_all_contexts.py")
    run_script("Validate One Context File (observability.json)", 
               "PYTHONPATH=. python cli/validate_context.py examples/context-variants/observability.json")
