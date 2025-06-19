#!/usr/bin/env python3
"""
Test script for the 5-step LLM process.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.services.prompt.prompt_engine import generate_prompt_response_5step
from core.services.logging.logger import logger

def test_5step_llm():
    """Test the 5-step LLM process with sample data."""
    
    # Sample input data
    input_data = {
        "service_name": "test-api",
        "description": "A test API service for demonstration",
        "timeframe": "5min",
        "metrics": [
            {
                "name": "http_requests_total",
                "type": "counter",
                "source": "prometheus",
                "value": 1000,
                "unit": "requests"
            },
            {
                "name": "http_request_duration_seconds",
                "type": "histogram", 
                "source": "prometheus",
                "value": 0.15,
                "unit": "seconds"
            }
        ]
    }
    
    try:
        logger.info("🧪 Starting 5-step LLM test...")
        
        # Run the 5-step process with faster settings
        result = generate_prompt_response_5step(
            input_data,
            model="llama3.2:1b",  # Faster model
            temperature=0.3       # Lower temperature for speed
        )
        
        # Validate the result
        logger.info("✅ 5-step LLM process completed successfully!")
        logger.info(f"📊 Generated {len(result.get('final_data', {}).get('sli', []))} SLIs")
        logger.info(f"🎯 Generated {len(result.get('final_data', {}).get('slo', []))} SLOs")
        logger.info(f"🚨 Generated {len(result.get('final_data', {}).get('alerts', []))} alerts")
        
        # Print the result
        import json
        print("\n" + "="*50)
        print("5-STEP LLM RESULT (FAST MODE)")
        print("="*50)
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 5-step LLM test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_5step_llm()
    sys.exit(0 if success else 1) 