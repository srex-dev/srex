# core/prompt_engine.py
import yaml

def generate_slo_definitions(input_path: str, output_path: str):
    with open(input_path, "r") as f:
        data = yaml.safe_load(f)

    # Simulated generation logic (can be replaced with actual LLM prompt logic)
    slo_output = {
        "service": data.get("service", "unknown"),
        "slos": [
            {
                "name": "availability",
                "objective": "99.9%",
                "description": "Service should be available 99.9% of the time"
            },
            {
                "name": "latency",
                "objective": "p95 < 300ms",
                "description": "95% of requests should respond within 300ms"
            }
        ]
    }

    with open(output_path, "w") as f:
        yaml.dump(slo_output, f, sort_keys=False)

    print(f"[✓] SLOs generated and written to {output_path}")


def validate_slo_definitions(input_path: str):
    try:
        with open(input_path, "r") as f:
            data = yaml.safe_load(f)

        if "service" not in data or "slos" not in data:
            print("[!] Validation failed: Missing 'service' or 'slos' keys.")
            return

        print(f"[✓] Validation successful for {input_path}")
    except Exception as e:
        print(f"[!] Validation error: {e}")