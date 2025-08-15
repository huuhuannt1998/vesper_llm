#!/usr/bin/env python3
"""
Basic LLM Connection Test - No Dependencies
This script tests the LLM connection using only built-in libraries.
"""

import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env file
API_URL = os.getenv("LLM_API_URL", "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions")
API_KEY = os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
MODEL = os.getenv("LLM_MODEL", "gpt-oss:120b")
TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "30"))

def test_basic_http_connection():
    """Test basic HTTP connectivity to the LLM server"""
    print("Basic HTTP Connection Test")
    print("="*50)
    
    try:
        # Parse URL to get base URL for testing
        parsed_url = urllib.parse.urlparse(API_URL)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        print(f"Testing connection to: {base_url}")
        
        # Simple GET request to test connectivity
        req = urllib.request.Request(base_url)
        req.add_header('User-Agent', 'LLM-Test/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            print(f"✓ Server responded with HTTP {status_code}")
            return True
            
    except urllib.error.URLError as e:
        print(f"✗ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_llm_completion():
    """Test LLM chat completion using urllib"""
    print("\nLLM Chat Completion Test")
    print("="*50)
    print(f"API URL: {API_URL}")
    print(f"Model: {MODEL}")
    print(f"API Key: {API_KEY[:10]}...")
    print()
    
    try:
        # Prepare the request payload
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Be concise."},
                {"role": "user", "content": "Say 'Hello, LLM test is working!' exactly."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        # Convert to JSON
        data = json.dumps(payload).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(API_URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {API_KEY}')
        req.add_header('User-Agent', 'LLM-Test/1.0')
        
        print("Sending chat completion request...")
        
        # Send request
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"✓ HTTP {status_code} response received")
            
            # Parse JSON response
            try:
                result = json.loads(response_data)
                
                # Extract the message content
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    content = message.get('content', '')
                    
                    if content:
                        print(f"✓ LLM Response: {content}")
                        return True
                    else:
                        print("✗ Empty response content")
                        print(f"Raw response: {response_data[:200]}...")
                        return False
                else:
                    print("✗ No choices in response")
                    print(f"Raw response: {response_data[:200]}...")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"✗ Failed to parse JSON response: {e}")
                print(f"Raw response: {response_data[:200]}...")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"Error details: {error_body[:200]}...")
        except:
            pass
        return False
        
    except urllib.error.URLError as e:
        print(f"✗ URL error: {e}")
        return False
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_simple_math():
    """Test LLM with a simple math question"""
    print("\nSimple Math Test")
    print("="*50)
    
    try:
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful math assistant."},
                {"role": "user", "content": "What is 25 + 17? Just give the number."}
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(API_URL, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {API_KEY}')
        
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"Math question: What is 25 + 17?")
                print(f"✓ LLM answer: {content}")
                return True
            else:
                print("✗ No response received")
                return False
                
    except Exception as e:
        print(f"✗ Math test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("LLM Connection Test Suite (No Dependencies)")
    print("="*60)
    
    tests = [
        ("Basic HTTP Connection", test_basic_http_connection),
        ("LLM Chat Completion", test_llm_completion),
        ("Simple Math Test", test_simple_math)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n>>> Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
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
    elif passed == 0:
        print("❌ All tests failed. Check connection and configuration.")
        print("\nTroubleshooting:")
        print("1. Verify the server is running and accessible")
        print("2. Check network connectivity")  
        print("3. Verify API_URL and API_KEY in .env file")
        print("4. Check firewall settings")
    else:
        print("⚠️  Some tests passed, some failed. Partial connectivity.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    print(f"\nExiting with code: {exit_code}")
    exit(exit_code)
