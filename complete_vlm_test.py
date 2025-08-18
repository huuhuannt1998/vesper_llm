#!/usr/bin/env python3
"""
Complete VLM Analysis Tool
Self-contained tool to test VLM capabilities on house screenshots
"""

import os
import glob
import base64
import requests
import json

def get_latest_screenshot():
    """Get the latest screenshot from captures folder"""
    captures_dir = os.path.join("blender", "captures")
    
    if not os.path.exists(captures_dir):
        print(f"❌ Captures directory not found: {captures_dir}")
        return None
    
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        print(f"❌ No screenshots found in {captures_dir}")
        return None
    
    latest = max(screenshots, key=os.path.getmtime)
    print(f"📸 Latest screenshot: {os.path.basename(latest)}")
    return latest

def encode_image_to_base64(image_path):
    """Convert image to base64 for VLM analysis"""
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        return image_data
    except Exception as e:
        print(f"❌ Error encoding image: {e}")
        return None

def analyze_with_vlm(image_path, analysis_prompt):
    """Analyze image with VLM using direct API call"""
    
    # Encode image
    image_b64 = encode_image_to_base64(image_path)
    if not image_b64:
        return None
    
    # Prepare API request
    url = "http://100.98.151.66:1234/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer not-needed"
    }
    
    payload = {
        "model": "google/gemma-3-27b",
        "messages": [
            {
                "role": "system",
                "content": "You are analyzing a bird's eye view image of a house layout."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": analysis_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    try:
        print("🔄 Sending request to VLM...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def run_vlm_capability_test():
    """Run comprehensive VLM capability test"""
    
    print("🏠 VLM House Layout Capability Test")
    print("="*50)
    
    # Get latest screenshot
    screenshot = get_latest_screenshot()
    if not screenshot:
        return
    
    # Different analysis prompts to test VLM capabilities
    tests = [
        {
            "name": "Basic Layout Analysis",
            "prompt": """Look at this bird's eye view of a house and describe:
1. What rooms can you identify?
2. What is the overall layout structure?
3. Are there any visible characters or objects?"""
        },
        {
            "name": "Room Identification",
            "prompt": """Analyze this house layout and identify:
1. Where is the kitchen located? (describe position using directions like left, right, up, down)
2. Where is the bathroom located?
3. Where are other rooms like bedroom, living room?
4. Can you see any character/actor in the image? If so, where?"""
        },
        {
            "name": "Navigation Analysis", 
            "prompt": """Look at this house layout from a navigation perspective:
1. If there's a character visible, where are they positioned?
2. What would be the best path to reach the kitchen from the character's position?
3. What would be the best path to reach the bathroom?
4. Are there walls, obstacles, or clear pathways visible?"""
        },
        {
            "name": "Detailed Spatial Assessment",
            "prompt": """Provide a detailed spatial analysis:
1. Describe the house layout in terms of coordinates (left/right, up/down)
2. What distinctive features help identify each room?
3. How clear and analyzable is this image for navigation purposes?
4. What improvements would help with better navigation analysis?"""
        }
    ]
    
    # Run each test
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"🔍 TEST {i}: {test['name']}")
        print(f"{'='*60}")
        
        result = analyze_with_vlm(screenshot, test["prompt"])
        
        if result:
            print("\n✅ VLM Response:")
            print("-" * 40)
            print(result)
            print("-" * 40)
        else:
            print("\n❌ Test failed")
        
        print(f"\n🏁 Test {i} completed\n")

if __name__ == "__main__":
    run_vlm_capability_test()
