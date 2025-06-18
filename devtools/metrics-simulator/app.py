from flask import Flask, Response
import time
import random
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import os

app = Flask(__name__)

# Simulated component name - change this to match your service
COMPONENT = "service"  # This will be the component name in Prometheus queries

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "status", "component"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["component"])
RESPONSE_CODES = Counter("http_response_code", "HTTP response codes", ["component", "code"])
UP_METRIC = Gauge("up", "Service health status", ["component"])

# Simulate different types of requests
def simulate_request(component, request_type="normal"):
    method = random.choice(["GET", "POST"])
    
    # Adjust success rate based on request type
    if request_type == "normal":
        status = random.choices(["200", "500"], weights=[0.95, 0.05])[0]  # 95% success rate
        latency = random.uniform(0.05, 0.2)  # 50-200ms for normal requests
    elif request_type == "slow":
        status = random.choices(["200", "500"], weights=[0.90, 0.10])[0]  # 90% success rate
        latency = random.uniform(0.2, 0.5)  # 200-500ms for slow requests
    else:  # error case
        status = random.choices(["200", "500"], weights=[0.80, 0.20])[0]  # 80% success rate
        latency = random.uniform(0.5, 1.0)  # 500-1000ms for error cases

    # Record metrics
    REQUEST_COUNT.labels(method=method, status=status, component=component).inc()
    RESPONSE_CODES.labels(component=component, code=status).inc()
    UP_METRIC.labels(component=component).set(1 if status == "200" else 0)

    # Simulate request processing time
    with REQUEST_LATENCY.labels(component=component).time():
        time.sleep(latency)

    return ("OK" if status == "200" else "Error"), int(status)

@app.route("/health")
def health():
    UP_METRIC.labels(component=COMPONENT).set(1)
    return "OK", 200

@app.route("/", methods=["GET", "POST"])
def root():
    # Simulate a mix of request types
    request_type = random.choices(["normal", "slow", "error"], weights=[0.7, 0.2, 0.1])[0]
    return simulate_request(COMPONENT, request_type)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 8000))
    app.run(host="0.0.0.0", port=port, threaded=True)