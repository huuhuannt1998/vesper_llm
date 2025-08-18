#!/usr/bin/env python3
"""
Fixed VLM Test with extended timeouts and better error handling
"""
import os
import sys
import base64
import requests
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def find_latest_screenshot():
    """Find the latest screenshot in captures folder"""
    captures_dir = Path("blender/captures")
    if not captures_dir.exists():
        return None
    
    png_files = list(captures_dir.glob("*.png"))
    if not png_files:
        return None
    
    # Sort by modification time
    latest = max(png_files, key=lambda f: f.stat().st_mtime)
    return str(latest)

def test_vlm_with_extended_timeout():
    """Test VLM with 3-minute timeout"""
    screenshot_path = find_latest_screenshot()
    if not screenshot_path:
        print("❌ No screenshot found!")
        return False
    
    print(f"📸 Using screenshot: {screenshot_path}")
    
    # Read and encode image
    try:
        with open(screenshot_path, "rb") as f:
            image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        print(f"✅ Image encoded: {len(encoded_image)} chars, {len(image_data)} bytes")
    except Exception as e:
        print(f"❌ Failed to encode image: {e}")
        return False
    
    # Simple analysis prompt
    prompt = "What rooms can you see in this house layout? Just list the rooms briefly."
    
    data = {
        "model": "google/gemma-3-27b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 200
    }
    
    print("🔄 Sending VLM request with 180s timeout...")
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://100.98.151.66:1234/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=180  # 3 minutes
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️ Request completed in {elapsed:.1f} seconds")
        
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        print("✅ VLM Response:")
        print(content)
        return True
        
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"❌ Request timed out after {elapsed:.1f} seconds")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Request failed after {elapsed:.1f} seconds: {e}")
        return False

def test_server_connectivity():
    """Test basic server connectivity"""
    print("🔍 Testing server connectivity...")
    
    try:
        response = requests.get("http://100.98.151.66:1234/v1/models", timeout=10)
        response.raise_for_status()
        models = response.json()
        print("✅ Server is reachable")
        print(f"📋 Available models: {[m.get('id', 'unknown') for m in models.get('data', [])]}")
        return True
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return False

def main():
    print("=== Fixed VLM Test with Extended Timeouts ===\n")
    
    # Test 1: Server connectivity
    if not test_server_connectivity():
        return
    
    print()
    
    # Test 2: VLM with extended timeout
    test_vlm_with_extended_timeout()

if __name__ == "__main__":
    main()
