#!/usr/bin/env python3
"""
LLM Connection Test with Multiple URLs
Tests both the hostname and IP address configurations.
"""

import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Multiple URL configurations to test
URLS_TO_TEST = [
    {
        "name": "Environment URL (hostname)",
        "url": os.getenv("LLM_API_URL", "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions"),
        "model": os.getenv("LLM_MODEL", "gpt-oss:120b"),
        "key": os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
    },
    {
        "name": "IP Address URL",
        "url": "http://100.98.151.66:1234/v1/chat/completions",
        "model": "openai/gpt-oss-120b",
        "key": os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
    },
    {
        "name": "Local LM Studio",
        "url": "http://localhost:1234/v1/chat/completions",
        "model": "local-model",
        "key": "not-needed"
    }
]

TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "30"))

def test_connection_and_llm(config):
    """Test both basic connectivity and LLM functionality for a given configuration"""
    print(f"\nTesting: {config['name']}")
    print("="*60)
    print(f"URL: {config['url']}")
    print(f"Model: {config['model']}")
    print(f"Key: {config['key'][:10]}...")
    
    # Parse URL for base connectivity test
    parsed_url = urllib.parse.urlparse(config['url'])
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Test 1: Basic connectivity
    print(f"\n1. Testing basic connectivity to {base_url}")
    try:
        req = urllib.request.Request(base_url)
        req.add_header('User-Agent', 'LLM-Test/1.0')
        
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            print(f"   ✓ Server responded with HTTP {status_code}")
            connectivity = True
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        connectivity = False
    
    if not connectivity:
        print("   Skipping LLM test due to connectivity issues.")
        return False
    
    # Test 2: LLM Chat Completion
    print("\n2. Testing LLM chat completion")
    try:
        payload = {
            "model": config['model'],
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Just say 'Working' if you can respond."}
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(config['url'], data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {config["key"]}')
        req.add_header('User-Agent', 'LLM-Test/1.0')
        
        print("   Sending chat completion request...")
        
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status_code = response.getcode()
            response_data = response.read().decode('utf-8')
            
            print(f"   ✓ HTTP {status_code} response received")
            
            # Parse response
            try:
                result = json.loads(response_data)
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    if content:
                        print(f"   ✓ LLM Response: {content}")
                        return True
                    else:
                        print("   ✗ Empty response content")
                else:
                    print("   ✗ No choices in response")
                    print(f"   Raw response: {response_data[:100]}...")
                    
            except json.JSONDecodeError as e:
                print(f"   ✗ JSON decode error: {e}")
                print(f"   Raw response: {response_data[:100]}...")
                
    except urllib.error.HTTPError as e:
        print(f"   ✗ HTTP error {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"   Error details: {error_body[:100]}...")
        except:
            pass
    except Exception as e:
        print(f"   ✗ LLM test error: {e}")
    
    return False

def main():
    """Test multiple LLM configurations"""
    print("Multi-URL LLM Connection Test")
    print("="*80)
    print("Testing different LLM server configurations to find a working one...")
    
    working_configs = []
    
    for i, config in enumerate(URLS_TO_TEST, 1):
        print(f"\n[Test {i}/{len(URLS_TO_TEST)}]", end="")
        
        try:
            if test_connection_and_llm(config):
                working_configs.append(config)
                print(f"   🎉 SUCCESS: {config['name']} is working!")
            else:
                print(f"   ❌ FAILED: {config['name']} is not working")
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            break
        except Exception as e:
            print(f"   💥 ERROR: Unexpected error testing {config['name']}: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    if working_configs:
        print(f"✅ Found {len(working_configs)} working configuration(s):")
        for config in working_configs:
            print(f"   - {config['name']}: {config['url']}")
        
        print(f"\n💡 Recommendation: Use the first working configuration in your .env file:")
        best_config = working_configs[0]
        print(f"   LLM_API_URL={best_config['url']}")
        print(f"   LLM_MODEL={best_config['model']}")
        print(f"   LLM_API_KEY={best_config['key']}")
        
        return True
    else:
        print("❌ No working LLM configurations found.")
        print("\nTroubleshooting suggestions:")
        print("1. Check if any LLM server is running on your network")
        print("2. Verify network connectivity and firewall settings")
        print("3. Try running a local LM Studio instance")
        print("4. Contact your network administrator about server access")
        
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nExiting with {'success' if success else 'failure'}")
    exit(0 if success else 1)
