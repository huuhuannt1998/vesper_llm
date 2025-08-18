#!/usr/bin/env python3
"""
Test text-only requests to confirm server is working
"""
import requests
import time

def test_text_only():
    """Test basic text-only completion"""
    data = {
        "model": "google/gemma-3-27b",
        "messages": [{"role": "user", "content": "What is the capital of France? One word only."}],
        "max_tokens": 10
    }
    
    print("🔄 Testing text-only request...")
    start = time.time()
    
    try:
        resp = requests.post(
            "http://100.98.151.66:1234/v1/chat/completions",
            json=data,
            timeout=30
        )
        
        elapsed = time.time() - start
        print(f"✅ Text response in {elapsed:.1f}s:")
        print(resp.json()["choices"][0]["message"]["content"])
        return True
        
    except Exception as e:
        print(f"❌ Text request failed: {e}")
        return False

if __name__ == "__main__":
    test_text_only()
