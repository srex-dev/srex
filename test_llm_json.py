#!/usr/bin/env python3

import asyncio
import json
import sys
import os

# Change to backend directory for proper imports
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

from core.services.prompt.prompt_engine import generate_drift_suggestions_response

async def test_drift_suggestions():
    """Test the drift suggestions generation with updated prompt template."""
    
    # Sample drift data
    drift_data = {
        'confidence_drift': {
            'status': 'analyzed',
            'recent_avg_confidence': 80.79,
            'older_avg_confidence': 85.0,
            'drift_percentage': -4.95,
            'drift_direction': 'declining',
            'trend': 'positive'
        },
        'output_consistency': {
            'total_analyses': 60,
            'consistent_structure': 36,
            'missing_fields': {
                'sli': 4,
                'slo': 24,
                'alerts': 20,
                'llm_suggestions': 1
            },
            'structure_variations': 24,
            'consistency_percentage': 60.0
        },
        'coverage_drift': {
            'status': 'analyzed',
            'recent_averages': {
                'slis': 2.5,
                'slos': 2.7,
                'alerts': 3.9,
                'suggestions': 2.5
            },
            'older_averages': {
                'slis': 2.2,
                'slos': 0.62,
                'alerts': 0.95,
                'suggestions': 1.95
            },
            'coverage_trends': {
                'slis': {'change': 0.3, 'percentage_change': 13.64},
                'slos': {'change': 2.08, 'percentage_change': 335.48},
                'alerts': {'change': 2.95, 'percentage_change': 310.53},
                'suggestions': {'change': 0.55, 'percentage_change': 28.21}
            }
        },
        'quality_drift': {
            'total_analyses': 60,
            'validation_present': 0,
            'complete_outputs': 36,
            'quality_scores': [0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 25, 100, 25, 25, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 50, 50, 50, 50, 50, 50, 50, 50, 75, 75, 75, 50, 50, 50, 50, 50, 75, 50, 50, 50],
            'avg_quality_score': 79.58,
            'validation_percentage': 0.0,
            'completeness_percentage': 60.0
        }
    }
    
    input_json = {
        'drift_data': drift_data,
        'service_name': 'test-service',
        'analysis_period_days': 7,
        'current_timestamp': '2025-06-19T05:38:52.206271'
    }
    
    try:
        print("🧪 Testing drift suggestions generation...")
        result = await generate_drift_suggestions_response(input_json, 'llama2', 0.7, 'ollama')
        
        print("✅ Success! Generated drift suggestions:")
        print(json.dumps(result, indent=2))
        
        # Validate the response structure
        required_fields = ['ai_confidence', 'priority_actions', 'improvement_areas', 'suggestions', 'root_causes', 'success_metrics', 'explanation']
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"⚠️ Warning: Missing required fields: {missing_fields}")
        else:
            print("✅ All required fields present")
            
        # Check if ai_confidence is a decimal
        confidence = result.get('ai_confidence')
        if confidence is not None:
            if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
                print(f"✅ ai_confidence is valid decimal: {confidence}")
            else:
                print(f"⚠️ Warning: ai_confidence should be decimal 0-1, got: {confidence}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing drift suggestions: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_drift_suggestions())
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1) 