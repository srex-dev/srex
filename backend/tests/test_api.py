import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import sys
import yaml

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from backend.api.main import app

client = TestClient(app)

@pytest.fixture
def test_files():
    """Create test files for policy and SLO validation."""
    # Create test infrastructure file
    infra_dir = Path(project_root) / "examples"
    infra_dir.mkdir(parents=True, exist_ok=True)
    
    infra_file = infra_dir / "test_infra.yaml"
    with open(infra_file, "w") as f:
        yaml.dump({
            "resource": {
                "aws_s3_bucket": {
                    "test-bucket": {
                        "versioning": {
                            "enabled": True
                        },
                        "server_side_encryption_configuration": {
                            "rule": {
                                "apply_server_side_encryption_by_default": {
                                    "sse_algorithm": "AES256"
                                }
                            }
                        }
                    }
                }
            }
        }, f)
    
    # Create test SLO file
    slo_file = infra_dir / "test_slo.yaml"
    with open(slo_file, "w") as f:
        yaml.dump({
            "slo": {
                "name": "test-slo",
                "description": "Test SLO",
                "target": 0.99,
                "window": "30d",
                "metric": {
                    "name": "test_metric",
                    "type": "ratio",
                    "numerator": "success_count",
                    "denominator": "total_count"
                }
            }
        }, f)
    
    # Create test baseline SLO file
    baseline_file = infra_dir / "test_baseline.yaml"
    with open(baseline_file, "w") as f:
        yaml.dump({
            "slo": {
                "name": "test-baseline",
                "description": "Test Baseline",
                "target": 0.95,
                "window": "30d",
                "metric": {
                    "name": "test_metric",
                    "type": "ratio",
                    "numerator": "success_count",
                    "denominator": "total_count"
                }
            }
        }, f)
    
    yield {
        "infra": str(infra_file),
        "slo": str(slo_file),
        "baseline": str(baseline_file)
    }
    
    # Cleanup
    infra_file.unlink()
    slo_file.unlink()
    baseline_file.unlink()

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_policy():
    """Test policy generation endpoint."""
    response = client.post(
        "/api/v1/policies/generate",
        json={
            "input": "Ensure all S3 buckets have versioning enabled",
            "policy_type": "rego",
            "model": "llama2",
            "temperature": 0.3
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "policy_path" in data
    assert data["metadata"]["type"] == "rego"

def test_validate_policy(test_files):
    """Test policy validation endpoint."""
    # First generate a policy
    gen_response = client.post(
        "/api/v1/policies/generate",
        json={
            "input": "Ensure all S3 buckets have versioning enabled",
            "policy_type": "rego"
        }
    )
    assert gen_response.status_code == 200
    policy_path = gen_response.json()["policy_path"]
    
    # Then validate it
    response = client.post(
        "/api/v1/policies/validate",
        json={
            "policy_path": policy_path,
            "infra_path": test_files["infra"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "violations" in data

def test_validate_policy_file_not_found():
    """Test policy validation with non-existent file."""
    response = client.post(
        "/api/v1/policies/validate",
        json={
            "policy_path": "nonexistent.rego",
            "infra_path": "nonexistent.yaml"
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_generate_slo():
    """Test SLO generation endpoint."""
    response = client.post(
        "/api/v1/slos/generate",
        json={
            "input": "99.9% of requests should complete within 200ms",
            "model": "llama2",
            "temperature": 0.3,
            "explain": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "slo_path" in data
    assert data["metadata"]["explain"] is True

def test_validate_slo(test_files):
    """Test SLO validation endpoint."""
    response = client.post(
        "/api/v1/slos/validate",
        json={
            "slo_path": test_files["slo"],
            "live_metrics": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "violations" in data

def test_validate_slo_live_metrics():
    """Test SLO validation with live metrics."""
    response = client.post(
        "/api/v1/slos/validate",
        json={
            "slo_path": "test_slo.yaml",
            "live_metrics": True,
            "adapter": "prometheus"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "violations" in data

def test_validate_slo_live_metrics_no_adapter():
    """Test SLO validation with live metrics but no adapter."""
    response = client.post(
        "/api/v1/slos/validate",
        json={
            "slo_path": "test_slo.yaml",
            "live_metrics": True
        }
    )
    assert response.status_code == 400
    assert "adapter must be specified" in response.json()["detail"].lower()

def test_get_slo_history(test_files):
    """Test SLO history endpoint."""
    response = client.post(
        "/api/v1/slos/history",
        json={
            "slo_path": test_files["slo"],
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z"
            },
            "interval": "1h",
            "include_metadata": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "history" in data
    assert "metadata" in data
    assert data["metadata"]["interval"] == "1h"

def test_get_slo_history_file_not_found():
    """Test SLO history with non-existent file."""
    response = client.post(
        "/api/v1/slos/history",
        json={
            "slo_path": "nonexistent.yaml",
            "interval": "1h"
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_analyze_slo_trend(test_files):
    """Test SLO trend analysis endpoint."""
    response = client.post(
        "/api/v1/slos/trend",
        json={
            "slo_path": test_files["slo"],
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z"
            },
            "trend_type": "linear",
            "window": "7d"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "trend" in data
    assert "forecast" in data
    assert data["metadata"]["trend_type"] == "linear"
    assert data["metadata"]["window"] == "7d"

def test_analyze_slo_trend_file_not_found():
    """Test SLO trend analysis with non-existent file."""
    response = client.post(
        "/api/v1/slos/trend",
        json={
            "slo_path": "nonexistent.yaml",
            "trend_type": "linear",
            "window": "7d"
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_analyze_slo_drift(test_files):
    """Test SLO drift analysis endpoint."""
    response = client.post(
        "/api/v1/slos/drift",
        json={
            "slo_path": test_files["slo"],
            "baseline_path": test_files["baseline"],
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z"
            },
            "threshold": 0.1
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "drift_percentage" in data
    assert "trend" in data
    assert "recommendations" in data
    assert data["metadata"]["threshold"] == 0.1

def test_analyze_slo_drift_file_not_found():
    """Test SLO drift analysis with non-existent file."""
    response = client.post(
        "/api/v1/slos/drift",
        json={
            "slo_path": "nonexistent.yaml",
            "threshold": 0.1
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_generate_scorecard(test_files):
    """Test scorecard generation endpoint."""
    response = client.post(
        "/api/v1/scorecard",
        json={
            "slo_paths": [test_files["slo"]],
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z"
            },
            "include_drift": True,
            "include_recommendations": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "score" in data
    assert "slo_status" in data
    assert "drift_status" in data
    assert "recommendations" in data
    assert data["metadata"]["include_drift"] is True

def test_generate_scorecard_file_not_found():
    """Test scorecard generation with non-existent file."""
    response = client.post(
        "/api/v1/scorecard",
        json={
            "slo_paths": ["nonexistent.yaml"],
            "include_drift": True
        }
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_query_metrics():
    """Test metrics query endpoint."""
    response = client.post(
        "/api/v1/metrics/query",
        json={
            "query": "rate(http_requests_total[5m])",
            "adapter": "prometheus",
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-02T00:00:00Z"
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "metrics" in data
    assert data["metadata"]["adapter"] == "prometheus"

def test_configure_adapter():
    """Test adapter configuration endpoint."""
    response = client.post(
        "/api/v1/adapters/configure",
        json={
            "adapter": "prometheus",
            "config": {
                "url": "http://localhost:9090",
                "timeout": 30,
                "verify_ssl": False
            }
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "configured"
    assert "config_keys" in data["metadata"]
    assert len(data["metadata"]["config_keys"]) == 3

def test_discover_adapters():
    """Test adapter discovery endpoint."""
    response = client.get("/api/v1/adapters/discover")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "adapters" in data
    assert len(data["adapters"]) > 0
    
    # Check first adapter
    adapter = data["adapters"][0]
    assert "name" in adapter
    assert "description" in adapter
    assert "capabilities" in adapter
    assert "config_schema" in adapter
    
    # Check metadata
    assert "total_adapters" in data["metadata"]
    assert "timestamp" in data["metadata"] 