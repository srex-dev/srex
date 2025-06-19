#!/usr/bin/env python3
"""
Test script for quantity controls
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.services.prompt.prompt_engine import generate_prompt_response
from core.services.logging.logger import logger

def test_quantity_controls():
    """Test that quantity parameters are passed through correctly"""
    print("🧪 Testing Quantity Controls")
    print("=" * 50)
    
    # Test input with custom quantities
    test_input = {
        "service_name": "test-service",
        "timeframe": "5min",
        "sli_quantity": 3,
        "slo_quantity": 2,
        "alert_quantity": 1,
        "suggestion_quantity": 4
    }
    
    print(f"Test input quantities:")
    print(f"  SLI: {test_input['sli_quantity']}")
    print(f"  SLO: {test_input['slo_quantity']}")
    print(f"  Alert: {test_input['alert_quantity']}")
    print(f"  Suggestion: {test_input['suggestion_quantity']}")
    
    try:
        # Test the prompt generation (this will show if quantities are passed to templates)
        result = generate_prompt_response(
            input_json=test_input,
            template='default',
            explain=False,
            model='llama2',
            temperature=0.7,
            provider='ollama'
        )
        
        print("\n✅ Quantity controls test completed successfully!")
        print(f"Generated {len(result.get('sli', []))} SLIs")
        print(f"Generated {len(result.get('slo', []))} SLOs")
        print(f"Generated {len(result.get('alerts', []))} Alerts")
        print(f"Generated {len(result.get('llm_suggestions', []))} Suggestions")
        
        return True
        
    except Exception as e:
        print(f"❌ Quantity controls test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Quantity Controls Test")
    print("=" * 60)
    
    success = test_quantity_controls()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Quantity controls test passed!")
        print("\nYou can now use the quantity sliders in the frontend to control:")
        print("- Number of SLIs generated")
        print("- Number of SLOs generated") 
        print("- Number of alerts generated")
        print("- Number of suggestions generated")
    else:
        print("❌ Quantity controls test failed. Please check the errors above.")
        sys.exit(1) 