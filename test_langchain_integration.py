#!/usr/bin/env python3
"""
Test script for LangChain integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from llm.providers import LLMProviderFactory
from llm.interface import call_llm, get_available_providers
from core.services.logging.logger import logger

def test_langchain_provider():
    """Test the LangChain provider"""
    print("🧪 Testing LangChain Provider Integration")
    print("=" * 50)
    
    # Test 1: Check available providers
    print("\n1. Checking available providers...")
    providers = get_available_providers()
    print(f"Available providers: {providers}")
    
    if "langchain" not in providers:
        print("❌ LangChain provider not available!")
        return False
    
    print("✅ LangChain provider is available")
    
    # Test 2: Create LangChain provider
    print("\n2. Creating LangChain provider...")
    try:
        langchain_provider = LLMProviderFactory.create_provider(
            "langchain",
            model="llama2",
            temperature=0.7
        )
        print("✅ LangChain provider created successfully")
    except Exception as e:
        print(f"❌ Failed to create LangChain provider: {e}")
        return False
    
    # Test 3: Test simple generation
    print("\n3. Testing simple generation...")
    try:
        test_prompt = "Generate a simple JSON response with a 'message' field containing 'Hello from LangChain!'"
        response = langchain_provider.generate(test_prompt, explain=False)
        print(f"✅ LangChain response: {response[:100]}...")
    except Exception as e:
        print(f"❌ LangChain generation failed: {e}")
        return False
    
    # Test 4: Test through interface
    print("\n4. Testing through LLM interface...")
    try:
        response = call_llm(
            "Return a JSON object with a 'status' field set to 'success'",
            explain=False,
            model="llama2",
            temperature=0.7,
            provider="langchain"
        )
        print(f"✅ Interface response: {response[:100]}...")
    except Exception as e:
        print(f"❌ Interface test failed: {e}")
        return False
    
    # Test 5: Compare with Ollama provider
    print("\n5. Comparing with Ollama provider...")
    try:
        ollama_response = call_llm(
            "Return a JSON object with a 'status' field set to 'success'",
            explain=False,
            model="llama2",
            temperature=0.7,
            provider="ollama"
        )
        print(f"✅ Ollama response: {ollama_response[:100]}...")
        print("✅ Both providers working correctly")
    except Exception as e:
        print(f"❌ Ollama comparison failed: {e}")
        return False
    
    print("\n🎉 All LangChain integration tests passed!")
    return True

def test_provider_selection():
    """Test provider selection functionality"""
    print("\n🧪 Testing Provider Selection")
    print("=" * 50)
    
    providers = ["ollama", "langchain"]
    
    for provider in providers:
        print(f"\nTesting {provider} provider...")
        try:
            response = call_llm(
                "Generate a simple test response",
                explain=False,
                model="llama2",
                temperature=0.7,
                provider=provider
            )
            print(f"✅ {provider} provider working: {response[:50]}...")
        except Exception as e:
            print(f"❌ {provider} provider failed: {e}")
            return False
    
    print("\n🎉 All provider selection tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting LangChain Integration Tests")
    print("=" * 60)
    
    success = True
    
    # Run tests
    if not test_langchain_provider():
        success = False
    
    if not test_provider_selection():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! LangChain integration is working correctly.")
        print("\nYou can now use the LangChain provider in the frontend by:")
        print("1. Going to the Analysis page")
        print("2. Selecting 'LangChain Provider' radio button")
        print("3. Running your analysis")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1) 