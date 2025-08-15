#!/usr/bin/env python3
"""
Standalone LLM Connection Test
This script tests the LLM connection independently without requiring the backend structure.
"""

import os
import httpx
from dotenv import load_dotenv
from openai import OpenAI, DefaultHttpxClient

# Load environment variables
load_dotenv()

# Configuration (same as in client.py)
BASE_URL = os.getenv("LLM_API_URL", "http://100.98.151.66:1234/v1")
if "/chat/completions" in BASE_URL:
    BASE_URL = BASE_URL.split("/chat/completions")[0]

# Override with working IP address if the environment variable points to the broken hostname
if "cci-siscluster1.charlotte.edu" in BASE_URL:
    print("⚠ Detected hostname with DNS issues, switching to IP address...")
    BASE_URL = "http://100.98.151.66:1234/v1"
    
API_KEY = os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "30"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "256"))

def test_llm_connection():
    """Test the LLM connection using the same configuration as client.py"""
    
    print("LLM Connection Test")
    print("="*50)
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Timeout: {TIMEOUT}s")
    print(f"Max Tokens: {MAX_TOKENS}")
    print()
    
    try:
        # Create OpenAI client with custom httpx configuration
        print("Creating OpenAI client...")
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            http_client=DefaultHttpxClient(
                transport=httpx.HTTPTransport(local_address="0.0.0.0"),
                timeout=TIMEOUT
            ),
        )
        print("✓ Client created successfully")
        
        # Test 1: Simple chat completion
        print("\nTest 1: Basic chat completion")
        print("-" * 30)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Be concise."},
                {"role": "user", "content": "Say 'Hello, LLM is working!' exactly."},
            ],
            max_tokens=50,
        )
        
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content
            print(f"✓ Response: {content}")
        else:
            print("✗ Empty response received")
            return False
            
        # Test 2: Math question
        print("\nTest 2: Simple math question")
        print("-" * 30)
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful math assistant."},
                {"role": "user", "content": "What is 15 + 27?"},
            ],
            max_tokens=30,
        )
        
        if response.choices and response.choices[0].message.content:
            content = response.choices[0].message.content
            print(f"✓ Math response: {content}")
        else:
            print("✗ Empty math response")
            return False
            
        # Test 3: Try to get available models
        print("\nTest 3: List available models")
        print("-" * 30)
        
        try:
            models_response = client.models.list()
            models = [model.id for model in models_response.data]
            if models:
                print(f"✓ Found {len(models)} models:")
                for model in models[:5]:  # Show first 5 models
                    print(f"  - {model}")
                if len(models) > 5:
                    print(f"  ... and {len(models) - 5} more")
            else:
                print("⚠ No models returned (server may not support /v1/models)")
        except Exception as e:
            print(f"⚠ Could not get models: {e}")
            
        print("\n" + "="*50)
        print("🎉 All tests completed successfully!")
        print("LLM connection is working properly.")
        return True
        
    except Exception as e:
        print(f"\n✗ Connection test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if the LLM server is running")
        print("2. Verify the BASE_URL is correct")
        print("3. Check network connectivity")
        print("4. Verify API key if required")
        return False

def test_connection_details():
    """Test basic network connectivity to the server"""
    print("\nNetwork Connectivity Test")
    print("="*50)
    
    try:
        # Parse the base URL to get host and port
        from urllib.parse import urlparse
        parsed = urlparse(BASE_URL)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        print(f"Testing connection to {host}:{port}...")
        
        # Simple HTTP client test
        with httpx.Client(timeout=10.0) as client:
            # Try to hit the base URL
            response = client.get(f"{BASE_URL.rstrip('/')}/")
            print(f"✓ Server responded with status: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"✗ Network test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting LLM Connection Tests...\n")
    
    # Test network connectivity first
    network_ok = test_connection_details()
    
    if network_ok:
        # Run main LLM test
        success = test_llm_connection()
        exit_code = 0 if success else 1
    else:
        print("Skipping LLM test due to network connectivity issues.")
        exit_code = 1
    
    print(f"\nTest completed with exit code: {exit_code}")
    exit(exit_code)
