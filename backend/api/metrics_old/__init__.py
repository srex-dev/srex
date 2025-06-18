from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Create router
router = APIRouter()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "srex_http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "srex_http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)
ACTIVE_USERS = Gauge(
    "srex_active_users",
    "Number of active users"
)
API_KEY_USAGE = Counter(
    "srex_api_key_usage_total",
    "Total API key usage",
    ["api_key_id"]
)

@router.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)