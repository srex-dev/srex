import pytest
from pathlib import Path
import yaml
from core.adapters import (
    discover_adapters,
    configure_adapter,
    get_adapter,
    PrometheusAdapter,
    CloudWatchAdapter
)

@pytest.fixture
def test_config_dir(tmp_path):
    """Create a test config directory."""
    config_dir = tmp_path / "config" / "adapters"
    config_dir.mkdir(parents=True)
    return config_dir

def test_discover_adapters():
    """Test discovering available adapters."""
    adapters = discover_adapters()
    assert len(adapters) > 0
    
    # Verify adapter information
    for adapter in adapters:
        assert "name" in adapter
        assert "description" in adapter
        assert "supported_metrics" in adapter
        assert "config_schema" in adapter
        
        # Verify specific adapters
        if adapter["name"] == "PrometheusAdapter":
            assert "prometheus" in adapter["supported_metrics"]
            assert "url" in adapter["config_schema"]
        elif adapter["name"] == "CloudWatchAdapter":
            assert "cloudwatch" in adapter["supported_metrics"]
            assert "region" in adapter["config_schema"]

def test_configure_adapter(test_config_dir, monkeypatch):
    """Test configuring an adapter."""
    # Mock the config directory
    monkeypatch.setattr("core.adapters.Path", lambda x: test_config_dir / x)
    
    # Test Prometheus adapter configuration
    prom_config = {
        "url": "http://localhost:9090",
        "auth": {
            "username": "admin",
            "password": "secret"
        }
    }
    result = configure_adapter("PrometheusAdapter", prom_config)
    assert result["status"] == "success"
    assert result["adapter"] == "PrometheusAdapter"
    assert set(result["config_keys"]) == {"url", "auth"}
    
    # Verify config file was created
    config_file = test_config_dir / "prometheusadapter.yaml"
    assert config_file.exists()
    with open(config_file) as f:
        saved_config = yaml.safe_load(f)
    assert saved_config == prom_config
    
    # Test CloudWatch adapter configuration
    cw_config = {
        "region": "us-west-2",
        "credentials": {
            "access_key": "test-key",
            "secret_key": "test-secret"
        }
    }
    result = configure_adapter("CloudWatchAdapter", cw_config)
    assert result["status"] == "success"
    assert result["adapter"] == "CloudWatchAdapter"
    assert set(result["config_keys"]) == {"region", "credentials"}

def test_configure_adapter_invalid_name():
    """Test configuring a non-existent adapter."""
    with pytest.raises(ValueError):
        configure_adapter("InvalidAdapter", {})

def test_get_adapter(test_config_dir, monkeypatch):
    """Test getting a configured adapter."""
    # Mock the config directory
    monkeypatch.setattr("core.adapters.Path", lambda x: test_config_dir / x)
    
    # Configure an adapter first
    config = {
        "url": "http://localhost:9090",
        "auth": {
            "username": "admin",
            "password": "secret"
        }
    }
    configure_adapter("PrometheusAdapter", config)
    
    # Get the adapter
    adapter = get_adapter("PrometheusAdapter")
    assert adapter is not None
    assert isinstance(adapter, PrometheusAdapter)
    assert adapter.config == config
    
    # Test getting non-existent adapter
    assert get_adapter("NonExistentAdapter") is None

def test_adapter_query_metrics():
    """Test adapter metric querying."""
    # Test Prometheus adapter
    prom_adapter = PrometheusAdapter({
        "url": "http://localhost:9090"
    })
    metrics = prom_adapter.query_metrics({
        "query": "up",
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-02T00:00:00Z"
    })
    assert isinstance(metrics, list)
    
    # Test CloudWatch adapter
    cw_adapter = CloudWatchAdapter({
        "region": "us-west-2"
    })
    metrics = cw_adapter.query_metrics({
        "namespace": "AWS/EC2",
        "metric_name": "CPUUtilization",
        "start": "2024-01-01T00:00:00Z",
        "end": "2024-01-02T00:00:00Z"
    })
    assert isinstance(metrics, list)

def test_adapter_capabilities():
    """Test adapter capabilities."""
    # Test Prometheus adapter
    prom_adapter = PrometheusAdapter()
    capabilities = prom_adapter.get_capabilities()
    assert capabilities["name"] == "PrometheusAdapter"
    assert "prometheus" in capabilities["supported_metrics"]
    assert "url" in capabilities["config_schema"]
    
    # Test CloudWatch adapter
    cw_adapter = CloudWatchAdapter()
    capabilities = cw_adapter.get_capabilities()
    assert capabilities["name"] == "CloudWatchAdapter"
    assert "cloudwatch" in capabilities["supported_metrics"]
    assert "region" in capabilities["config_schema"] 