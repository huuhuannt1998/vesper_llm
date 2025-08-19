#!/usr/bin/env python3
"""
Simple VLM test to see what it understands about navigation
"""
import requests
import base64
import json
from pathlib import Path

def simple_vlm_navigation_test():
    """Simple test of VLM navigation understanding"""
    # Find latest screenshot
    captures_dir = Path("blender/captures")
    png_files = [f for f in captures_dir.glob("bge_*.png")]
    if not png_files:
        print("❌ No screenshots found")
        return
    
    png_files.sort()
    latest = png_files[-1]
    print(f"📸 Testing with: {latest.name}")
    
    # Encode image
    with open(latest, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    
    # Simple navigation test
    prompt = """Look at this bird's eye view of a house. I can see a pink/colored dot which is an actor.

Question: If the actor moves RIGHT from current position, will it hit a wall?
Answer only: YES (will hit wall) or NO (safe to move)

Look carefully at what's directly to the right of the colored dot."""
    
    data = {
        "model": "google/gemma-3-27b",
        "messages": [{
            "role": "user", 
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}}
            ]
        }],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            "http://100.98.151.66:1234/v1/chat/completions",
            json=data,
            timeout=120
        )
        
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        print(f"VLM Answer: {answer}")
        
        # Follow-up question
        prompt2 = """Same image. What do you see directly to the RIGHT of the pink/colored dot? 
Describe the area/space/object that is immediately to the right."""
        
        data["messages"][0]["content"][0]["text"] = prompt2
        
        response2 = requests.post(
            "http://100.98.151.66:1234/v1/chat/completions",
            json=data,
            timeout=120
        )
        
        result2 = response2.json()
        answer2 = result2["choices"][0]["message"]["content"]
        print(f"VLM Description: {answer2}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_vlm_navigation_test()
