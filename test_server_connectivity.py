#!/usr/bin/env python3
"""
Test the LLM server connectivity directly with a simple HTTP request
"""
import requests
import json

def test_llm_server():
    url = "http://100.98.151.66:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 5
    }
    
    try:
        print(f"🧪 Testing LLM server at {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LLM server is responding!")
            print(f"📝 Response: {data}")
        else:
            print(f"❌ LLM server returned error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - LLM server may be down")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_llm_server()
