from flask import Flask, Response
import time
import random
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import typer

app = Flask(__name__)

# Define Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "status", "component"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ["component"])

@app.route("/health")
def health():
    return "OK", 200

@app.route("/api")
def api():
    component = "api"
    status = random.choices(["200", "500"], weights=[0.9, 0.1])[0]

    # Log request count
    REQUEST_COUNT.labels(method="GET", status=status, component=component).inc()

    # Simulate latency with duration tied to success/failure
    with REQUEST_LATENCY.labels(component=component).time():
        time.sleep(random.uniform(0.05, 0.4) if status == "200" else random.uniform(0.5, 1.5))

    return ("OK" if status == "200" else "Error"), int(status)

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)