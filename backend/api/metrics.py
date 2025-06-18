from fastapi import APIRouter, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, timedelta
import random

# Create router
router = APIRouter()

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)
ACTIVE_USERS = Gauge(
    "active_users",
    "Number of active users"
)
API_KEY_USAGE = Counter(
    "api_key_usage_total",
    "Total API key usage",
    ["api_key_id"]
)

@router.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/health")
async def health():
    """Get system health metrics."""
    return {
        "healthPercentage": random.randint(85, 99),
        "activeIncidents": random.randint(0, 3),
        "uptimePercentage": random.randint(95, 99)
    }

@router.get("/activity")
async def activity():
    """Get recent activity metrics."""
    activities = [
        {
            "id": "1",
            "description": "Database backup completed",
            "status": "success",
            "time": (datetime.now() - timedelta(minutes=5)).isoformat()
        },
        {
            "id": "2", 
            "description": "High CPU usage detected",
            "status": "warning",
            "time": (datetime.now() - timedelta(minutes=15)).isoformat()
        },
        {
            "id": "3",
            "description": "Service restart initiated",
            "status": "success", 
            "time": (datetime.now() - timedelta(minutes=30)).isoformat()
        },
        {
            "id": "4",
            "description": "Memory usage threshold exceeded",
            "status": "error",
            "time": (datetime.now() - timedelta(hours=1)).isoformat()
        }
    ]
    return activities 