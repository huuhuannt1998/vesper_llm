#!/usr/bin/env python3
"""
Minimal test to isolate the hanging issue
"""
import requests
import json

def minimal_test():
    try:
        print("🧪 Testing minimal HTTP request...")
        url = "http://100.98.151.66:1234/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-a6af2053d49649d2925ff91fef71cb65"
        }
        
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 5
        }
        
        print(f"🔗 Making request to: {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            print(f"✅ Success! Response: '{content}'")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    minimal_test()
