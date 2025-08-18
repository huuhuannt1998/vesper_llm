#!/usr/bin/env python3
"""
Quick VLM Screenshot Test
Test VLM analysis on a single screenshot
"""

import os
import glob
from backend.app.llm.client import chat_completion_with_vision

def quick_vlm_test():
    """Quick test of VLM on latest screenshot"""
    
    captures_dir = os.path.join("blender", "captures")
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        print("❌ No screenshots found")
        return
    
    # Get latest screenshot
    latest = max(screenshots, key=os.path.getmtime)
    print(f"📸 Testing latest screenshot: {os.path.basename(latest)}")
    
    # Simple analysis
    system_prompt = "You are analyzing a bird's eye view of a house layout."
    
    user_prompt = """Look at this house layout image and answer:

1. What rooms can you identify?
2. Can you see any character/actor in the image?
3. Where would the kitchen be located?
4. Where would the bathroom be located?  
5. What's the overall layout structure?

Be specific about directions (left, right, up, down) and spatial relationships."""

    try:
        print("\n🧠 VLM Analysis:")
        print("="*50)
        
        response = chat_completion_with_vision(
            system_prompt, 
            user_prompt, 
            latest, 
            max_tokens=500,
            temperature=0.1
        )
        
        print(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_vlm_test()
