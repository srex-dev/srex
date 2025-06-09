import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # root of project

from metrics.adapters.prometheus_adapter import PrometheusAdapter

# Configure to match your running Prometheus
adapter = PrometheusAdapter(base_url="http://localhost:9090")

for sli_type in ["availability", "latency", "error_rate"]:
    result = adapter.query_sli(component="api", sli_type=sli_type)
    print(f"\n🔎 SLI type: {sli_type}")
    if result:
        for k, v in result.items():
            print(f"{k}: {v}")
    else:
        print("⚠️ No result")