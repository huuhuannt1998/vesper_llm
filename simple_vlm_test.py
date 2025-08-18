#!/usr/bin/env python3
"""
Simple VLM timeout test - focuses just on the timeout issue
"""
import requests
import base64
import time
from pathlib import Path

def simple_vlm_test():
    """Minimal VLM test to isolate timeout issue"""
    # Find latest screenshot
    captures_dir = Path("blender/captures")
    if not captures_dir.exists():
        print("❌ No captures folder")
        return
    
    png_files = list(captures_dir.glob("*.png"))
    if not png_files:
        print("❌ No screenshots found")
        return
    
    latest = max(png_files, key=lambda f: f.stat().st_mtime)
    print(f"📸 Using: {latest.name}")
    
    # Encode image
    with open(latest, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    
    # Simple request
    data = {
        "model": "google/gemma-3-27b", 
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What do you see? One sentence only."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}
            ]
        }],
        "max_tokens": 50
    }
    
    print("🔄 Sending request...")
    start = time.time()
    
    try:
        resp = requests.post(
            "http://100.98.151.66:1234/v1/chat/completions",
            json=data,
            timeout=300  # 5 minutes
        )
        
        elapsed = time.time() - start
        print(f"✅ Response in {elapsed:.1f}s:")
        print(resp.json()["choices"][0]["message"]["content"])
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout after {time.time() - start:.1f}s")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_vlm_test()
