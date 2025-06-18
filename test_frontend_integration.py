#!/usr/bin/env python3
"""
Test script to verify both original and 5-step LLM methods work correctly.
"""

import requests
import json
import time
from typing import Dict, Any

def test_original_method():
    """Test the original LLM method."""
    print("🧪 Testing Original Method...")
    
    payload = {
        "task": "default",
        "input": {
            "service_name": "api",
            "timeframe": "5min"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/llm",
            json=payload,
            timeout=1800  # 30 minutes
        )
        response.raise_for_status()
        result = response.json()
        
        print("✅ Original method successful!")
        print(f"📊 Output keys: {list(result.get('output', {}).keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Original method failed: {e}")
        return False

def test_5step_method():
    """Test the 5-step LLM method."""
    print("🧪 Testing 5-Step Method...")
    
    payload = {
        "input": {
            "service_name": "api",
            "description": "A test API service for 5-step validation",
            "timeframe": "5min"
        },
        "model": "llama2",
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/llm/5step",
            json=payload,
            timeout=1800  # 30 minutes for 5-step process
        )
        response.raise_for_status()
        result = response.json()
        
        print("✅ 5-step method successful!")
        print(f"📊 Output keys: {list(result.get('output', {}).keys())}")
        
        # Check for 5-step specific metadata
        output = result.get('output', {})
        if 'metadata' in output and output['metadata'].get('generation_method') == '5step_llm_process':
            print("✅ 5-step metadata confirmed!")
        else:
            print("⚠️ 5-step metadata not found")
            
        return True
        
    except Exception as e:
        print(f"❌ 5-step method failed: {e}")
        return False

def test_frontend_api():
    """Test the frontend API route that handles both methods."""
    print("🧪 Testing Frontend API Route...")
    
    # Test original method through frontend API
    original_payload = {
        "task": "default",
        "input": {
            "service_name": "api",
            "timeframe": "5min"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/llm",
            json=original_payload,
            timeout=1800  # 30 minutes
        )
        response.raise_for_status()
        result = response.json()
        
        print("✅ Frontend API (original) successful!")
        
    except Exception as e:
        print(f"❌ Frontend API (original) failed: {e}")
        return False
    
    # Test 5-step method through frontend API
    step5_payload = {
        "method": "5step",
        "input": {
            "service_name": "api",
            "description": "A test API service for frontend API validation",
            "timeframe": "5min"
        },
        "model": "llama2",
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "http://localhost:3000/api/llm",
            json=step5_payload,
            timeout=1800  # 30 minutes for 5-step process
        )
        response.raise_for_status()
        result = response.json()
        
        print("✅ Frontend API (5-step) successful!")
        return True
        
    except Exception as e:
        print(f"❌ Frontend API (5-step) failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting LLM Method Integration Tests")
    print("=" * 50)
    
    # Check if services are running
    try:
        # Check backend
        backend_response = requests.get("http://localhost:8001/", timeout=5)
        print("✅ Backend is running")
    except:
        print("❌ Backend is not running on localhost:8001")
        return False
    
    try:
        # Check frontend
        frontend_response = requests.get("http://localhost:3000/", timeout=5)
        print("✅ Frontend is running")
    except:
        print("❌ Frontend is not running on localhost:3000")
        return False
    
    print("\n" + "=" * 50)
    
    # Run tests
    tests = [
        ("Original Method", test_original_method),
        ("5-Step Method", test_5step_method),
        ("Frontend API", test_frontend_api)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        start_time = time.time()
        success = test_func()
        end_time = time.time()
        duration = end_time - start_time
        
        results.append((test_name, success, duration))
        print(f"⏱️  {test_name} took {duration:.2f} seconds")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary")
    print("=" * 50)
    
    all_passed = True
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Both methods are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 