#!/usr/bin/env python3
"""
Test script to verify the complete flow for fetching components from Prometheus
through the backend API to the frontend.
"""

import requests
import json
import time

def test_backend_components():
    """Test the backend components endpoint."""
    print("🔍 Testing backend components endpoint...")
    try:
        response = requests.get("http://localhost:8001/api/v1/adapters/components")
        if response.status_code == 200:
            components = response.json()
            print(f"✅ Backend returned {len(components)} components: {components}")
            return components
        else:
            print(f"❌ Backend returned status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return None

def test_frontend_proxy():
    """Test the frontend proxy endpoint."""
    print("\n🔍 Testing frontend proxy endpoint...")
    try:
        response = requests.get("http://localhost:3000/api/llm/components")
        if response.status_code == 200:
            components = response.json()
            print(f"✅ Frontend proxy returned {len(components)} components: {components}")
            return components
        else:
            print(f"❌ Frontend proxy returned status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Frontend proxy test failed: {e}")
        return None

def test_prometheus_connection():
    """Test direct Prometheus connection."""
    print("\n🔍 Testing direct Prometheus connection...")
    try:
        response = requests.get("http://localhost:9090/api/v1/label/component/values")
        if response.status_code == 200:
            data = response.json()
            components = data.get("data", [])
            print(f"✅ Prometheus returned {len(components)} components: {components}")
            return components
        else:
            print(f"❌ Prometheus returned status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Prometheus test failed: {e}")
        return None

def main():
    """Run all tests."""
    print("🚀 Testing Component Flow from Prometheus → Backend → Frontend")
    print("=" * 60)
    
    # Test Prometheus directly
    prometheus_components = test_prometheus_connection()
    
    # Test backend
    backend_components = test_backend_components()
    
    # Test frontend proxy
    frontend_components = test_frontend_proxy()
    
    # Compare results
    print("\n📊 Results Summary:")
    print("-" * 30)
    
    if prometheus_components:
        print(f"Prometheus: {len(prometheus_components)} components")
    else:
        print("Prometheus: ❌ Failed")
    
    if backend_components:
        print(f"Backend:    {len(backend_components)} components")
    else:
        print("Backend:    ❌ Failed")
    
    if frontend_components:
        print(f"Frontend:   {len(frontend_components)} components")
    else:
        print("Frontend:   ❌ Failed")
    
    # Check consistency
    if all([prometheus_components, backend_components, frontend_components]):
        if (set(prometheus_components) == set(backend_components) == set(frontend_components)):
            print("\n✅ All endpoints return consistent data!")
        else:
            print("\n⚠️  Data inconsistency detected between endpoints")
    else:
        print("\n❌ Some endpoints failed - check service status")
    
    print("\n🌐 Frontend Analysis Page:")
    print("Visit: http://localhost:3000/analysis")
    print("The 'Service Name' dropdown should show the components above.")

if __name__ == "__main__":
    main() 