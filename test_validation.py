#!/usr/bin/env python3
"""
Test script to verify the validation function works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.output_schema import validate_srex_output
from backend.core.services.prompt.prompt_engine import convert_types_for_schema

# Test data that should pass validation
test_data = {
    "sli": [
        {
            "name": "api_latency_p95",
            "description": "95th percentile response time for API requests",
            "type": "latency",
            "unit": "milliseconds",
            "source": "prometheus",
            "metric": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) * 1000",
            "value": "245.6"
        }
    ],
    "slo": [
        {
            "name": "Default SLO for api_latency_p95",
            "description": "95% of requests for api_latency_p95 complete in under 200ms over a 7-day window.",
            "sli": "api_latency_p95",
            "target": "0.95",
            "time_window": "7d"
        }
    ],
    "alerts": [
        {
            "name": "Default Alert for api_latency_p95",
            "description": "Alert if api_latency_p95 latency exceeds 200ms for 5m.",
            "threshold": "200",
            "duration": "5m"
        }
    ],
    "explanation": "No explanation provided.",
    "llm_suggestions": [
        {
            "metric": "unknown",
            "recommendation": "No specific numeric recommendation was generated."
        }
    ]
}

def test_validation():
    print("Testing validation with clean data...")
    print(f"Input data keys: {list(test_data.keys())}")
    print(f"SLO data: {test_data['slo']}")
    
    converted = convert_types_for_schema(test_data)
    print(f"Converted data: {converted}")
    
    is_valid, errors = validate_srex_output(converted, schema_type="slo")
    
    print(f"Validation result: {is_valid}")
    if not is_valid:
        print(f"Validation errors: {errors}")
    else:
        print("✅ Validation passed!")

if __name__ == "__main__":
    test_validation() 