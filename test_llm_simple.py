#!/usr/bin/env python3
"""
Simple test script for LLM connection.
This script tests the basic functionality of the LLM client.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.llm.client import chat_completion, get_models, BASE_URL, MODEL, API_KEY
    print("✓ Successfully imported LLM client")
except ImportError as e:
    print(f"✗ Failed to import LLM client: {e}")
    sys.exit(1)

def test_basic_connection():
    """Test basic LLM connection with a simple query."""
    print("\n" + "="*50)
    print("Testing Basic LLM Connection")
    print("="*50)
    
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    try:
        # Simple test query
        system_prompt = "You are a helpful assistant. Respond concisely."
        user_query = "Say 'Hello, LLM connection is working!' in exactly that phrase."
        
        print(f"\nSending test query: '{user_query}'")
        print("Waiting for response...")
        
        response = chat_completion(
            system=system_prompt,
            user=user_query,
            max_tokens=50
        )
        
        print(f"✓ Response received: {response}")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_get_models():
    """Test retrieving available models."""
    print("\n" + "="*50)
    print("Testing Model Discovery")
    print("="*50)
    
    try:
        models = get_models()
        if models:
            print(f"✓ Found {len(models)} available models:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
        else:
            print("⚠ No models found (this might be normal for some LLM servers)")
        return True
        
    except Exception as e:
        print(f"✗ Model discovery failed: {e}")
        return False

def test_conversation():
    """Test a simple conversation flow."""
    print("\n" + "="*50)
    print("Testing Conversation Flow")
    print("="*50)
    
    try:
        # First message
        system_prompt = "You are a helpful assistant."
        response1 = chat_completion(
            system=system_prompt,
            user="What is 2 + 2?",
            max_tokens=30
        )
        print(f"Q: What is 2 + 2?")
        print(f"A: {response1}")
        
        # Second message  
        response2 = chat_completion(
            system=system_prompt,
            user="What programming language is Python similar to?",
            max_tokens=50
        )
        print(f"\nQ: What programming language is Python similar to?")
        print(f"A: {response2}")
        
        print("✓ Conversation test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Conversation test failed: {e}")
        return False

def main():
    """Run all LLM connection tests."""
    print("LLM Connection Test Suite")
    print("=" * 60)
    
    # Enable debug mode for detailed output
    os.environ["LLM_DEBUG"] = "1"
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Model Discovery", test_get_models),
        ("Conversation Flow", test_conversation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            break
        except Exception as e:
            print(f"Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"{symbol} {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! LLM connection is working properly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the connection configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
