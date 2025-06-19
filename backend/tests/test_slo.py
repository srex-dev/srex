import pytest
from pathlib import Path
import yaml
from datetime import datetime, timedelta
from backend.core.slo import get_slo_history, analyze_slo_trend

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

def test_get_slo_history(test_slo_file):
    """Test getting SLO history."""
    # Test with default parameters
    result = get_slo_history(test_slo_file)
    assert "history" in result
    assert "metadata" in result
    assert len(result["history"]) > 0
    
    # Verify history data structure
    history_item = result["history"][0]
    assert "timestamp" in history_item
    assert "value" in history_item
    assert "metric" in history_item
    assert isinstance(history_item["value"], float)
    assert 0 <= history_item["value"] <= 1
    
    # Test with custom time range
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    time_range = {
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    result = get_slo_history(test_slo_file, time_range=time_range)
    assert len(result["history"]) > 0
    
    # Test with custom interval
    result = get_slo_history(test_slo_file, interval="1d")
    assert len(result["history"]) > 0
    
    # Test without metadata
    result = get_slo_history(test_slo_file, include_metadata=False)
    assert "history" in result
    assert result.get("metadata") is None

def test_get_slo_history_file_not_found():
    """Test getting SLO history with non-existent file."""
    with pytest.raises(FileNotFoundError):
        get_slo_history("non_existent_file.yaml")

def test_get_slo_history_invalid_interval(test_slo_file):
    """Test getting SLO history with invalid interval."""
    with pytest.raises(ValueError):
        get_slo_history(test_slo_file, interval="1x")

def test_analyze_slo_trend(test_slo_file):
    """Test analyzing SLO trends."""
    # Test linear trend
    result = analyze_slo_trend(test_slo_file, trend_type="linear")
    assert "trend" in result
    assert "forecast" in result
    assert "metadata" in result
    
    trend = result["trend"]
    assert "type" in trend
    assert "direction" in trend
    assert trend["type"] == "linear"
    assert trend["direction"] in ["improving", "degrading", "stable"]
    
    # Test exponential trend
    result = analyze_slo_trend(test_slo_file, trend_type="exponential")
    assert result["trend"]["type"] == "exponential"
    
    # Test moving average trend
    result = analyze_slo_trend(test_slo_file, trend_type="moving_average", window="7d")
    assert result["trend"]["type"] == "moving_average"
    assert "window" in result["trend"]
    
    # Verify forecast data
    forecast = result["forecast"]
    assert len(forecast) == 7  # 7 days forecast
    assert all("timestamp" in item for item in forecast)
    assert all("value" in item for item in forecast)
    assert all(0 <= item["value"] <= 1 for item in forecast)

def test_analyze_slo_trend_file_not_found():
    """Test analyzing SLO trend with non-existent file."""
    with pytest.raises(FileNotFoundError):
        analyze_slo_trend("non_existent_file.yaml")

def test_analyze_slo_trend_invalid_type(test_slo_file):
    """Test analyzing SLO trend with invalid trend type."""
    with pytest.raises(ValueError):
        analyze_slo_trend(test_slo_file, trend_type="invalid_type")

def test_analyze_slo_trend_custom_time_range(test_slo_file):
    """Test analyzing SLO trend with custom time range."""
    end = datetime.utcnow()
    start = end - timedelta(days=14)
    time_range = {
        "start": start.isoformat(),
        "end": end.isoformat()
    }
    
    result = analyze_slo_trend(test_slo_file, time_range=time_range)
    assert "trend" in result
    assert "forecast" in result
    assert "metadata" in result
    assert result["metadata"]["time_range"]["start"] == start.isoformat()
    assert result["metadata"]["time_range"]["end"] == end.isoformat() 