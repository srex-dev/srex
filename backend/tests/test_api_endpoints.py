import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import yaml
from api.main import app

client = TestClient(app)

@pytest.fixture
def test_slo_file(tmp_path):
    """Create a test SLO file."""
    slo_content = {
        "slo": {
            "name": "test-slo",
            "description": "Test SLO",
            "metric": {
                "name": "test_metric",
                "type": "ratio",
                "numerator": "success_count",
                "denominator": "total_count"
            },
            "target": 0.99,
            "window": "30d"
        }
    }
    
    slo_file = tmp_path / "test_slo.yaml"
    with open(slo_file, "w") as f:
        yaml.dump(slo_content, f)
    
    return str(slo_file)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_slo_history(test_slo_file):
    """Test SLO history endpoint."""
    # Test with default parameters
    response = client.post(
        "/api/v1/slos/history",
        json={"slo_path": test_slo_file}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "history" in data
    assert "metadata" in data
    assert len(data["history"]) > 0
    
    # Test with custom parameters
    response = client.post(
        "/api/v1/slos/history",
        json={
            "slo_path": test_slo_file,
            "interval": "1d",
            "include_metadata": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "history" in data
    assert data.get("metadata") is None

def test_get_slo_history_file_not_found():
    """Test SLO history endpoint with non-existent file."""
    response = client.post(
        "/api/v1/slos/history",
        json={"slo_path": "non_existent_file.yaml"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_analyze_slo_trend(test_slo_file):
    """Test SLO trend analysis endpoint."""
    # Test with default parameters
    response = client.post(
        "/api/v1/slos/trend",
        json={"slo_path": test_slo_file}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "trend" in data
    assert "forecast" in data
    assert "metadata" in data
    
    # Test with custom parameters
    response = client.post(
        "/api/v1/slos/trend",
        json={
            "slo_path": test_slo_file,
            "trend_type": "moving_average",
            "window": "7d"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["trend"]["type"] == "moving_average"

def test_analyze_slo_trend_file_not_found():
    """Test SLO trend analysis endpoint with non-existent file."""
    response = client.post(
        "/api/v1/slos/trend",
        json={"slo_path": "non_existent_file.yaml"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_discover_adapters():
    """Test adapter discovery endpoint."""
    response = client.get("/api/v1/adapters/discover")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "adapters" in data
    assert len(data["adapters"]) > 0
    
    # Verify adapter information
    for adapter in data["adapters"]:
        assert "name" in adapter
        assert "description" in adapter
        assert "supported_metrics" in adapter
        assert "config_schema" in adapter

def test_configure_adapter():
    """Test adapter configuration endpoint."""
    # Test Prometheus adapter configuration
    response = client.post(
        "/api/v1/adapters/configure",
        json={
            "adapter_name": "PrometheusAdapter",
            "config": {
                "url": "http://localhost:9090",
                "auth": {
                    "username": "admin",
                    "password": "secret"
                }
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["adapter"] == "PrometheusAdapter"
    assert set(data["config_keys"]) == {"url", "auth"}
    
    # Test invalid adapter name
    response = client.post(
        "/api/v1/adapters/configure",
        json={
            "adapter_name": "InvalidAdapter",
            "config": {}
        }
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower() 