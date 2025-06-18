import pytest
from datetime import datetime
from core.schema import validate_input, validate_output, get_input_errors, get_output_errors

def test_validate_input():
    """Test input validation."""
    # Valid input
    valid_input = {
        "service": "api",
        "service_name": "API Service",
        "sli_inputs": [
            {
                "component": "api",
                "sli_type": "availability",
                "value": 99.9,
                "unit": "percent",
                "query": "sum(rate(http_requests_total{status=~\"2..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
                "source": "prometheus",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "temperature": 0.7
    }
    assert validate_input(valid_input) is True
    assert len(get_input_errors()) == 0

    # Invalid input - missing required field
    invalid_input = {
        "service": "api",
        "sli_inputs": [
            {
                "component": "api",
                "sli_type": "availability",
                # Missing required fields: value, unit, query, source
            }
        ]
    }
    assert validate_input(invalid_input) is False
    assert len(get_input_errors()) > 0

def test_validate_output():
    """Test output validation."""
    # Valid output
    valid_output = {
        "sli": [
            {
                "name": "API Availability",
                "description": "API service availability",
                "type": "availability",
                "target": 99.9,
                "unit": "percent",
                "window": "30d",
                "query": "sum(rate(http_requests_total{status=~\"2..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
                "source": "prometheus"
            }
        ],
        "slo": [
            {
                "name": "API SLO",
                "description": "API service SLO",
                "target": 99.9,
                "window": "30d",
                "slis": ["API Availability"]
            }
        ],
        "alerts": [
            {
                "name": "High Error Rate",
                "description": "Alert on high error rate",
                "condition": "error_rate > 1%",
                "severity": "critical",
                "slo": "API SLO"
            }
        ],
        "explanation": "Generated SLIs, SLOs, and alerts based on service metrics",
        "llm_suggestions": [
            {
                "type": "optimization",
                "description": "Consider increasing availability target",
                "priority": "medium",
                "action": "Review current availability and adjust target if needed"
            }
        ],
        "ai_model": "gpt-4",
        "temperature": 0.7,
        "ai_confidence": 85.0
    }
    assert validate_output(valid_output) is True
    assert len(get_output_errors()) == 0

    # Invalid output - missing required field
    invalid_output = {
        "sli": [],
        "slo": [],
        "alerts": [],
        "explanation": "Test",
        "llm_suggestions": [],
        "ai_model": "gpt-4",
        "temperature": 0.7
        # Missing ai_confidence
    }
    assert validate_output(invalid_output) is False
    assert len(get_output_errors()) > 0 