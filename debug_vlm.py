#!/usr/bin/env python3
"""
VLM Debug Tool - See what the VLM actually sees
"""

import os
import glob
import sys

# Add the current directory to path so we can import our client
sys.path.insert(0, os.path.dirname(__file__))

def test_vlm_on_screenshot():
    """Test VLM analysis on the latest screenshot"""
    
    # Find latest screenshot
    captures_dir = os.path.join("blender", "captures")
    
    if not os.path.exists(captures_dir):
        print(f"❌ Captures directory not found: {captures_dir}")
        return
    
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        print(f"❌ No screenshots found in {captures_dir}")
        return
    
    # Get latest screenshot  
    latest = max(screenshots, key=os.path.getmtime)
    print(f"📸 Latest screenshot: {latest}")
    print(f"📁 File exists: {os.path.exists(latest)}")
    print(f"📊 File size: {os.path.getsize(latest)} bytes")
    
    # Test the client import
    try:
        from backend.app.llm.client import chat_completion_with_vision
        print("✅ Successfully imported VLM client")
    except Exception as e:
        print(f"❌ Failed to import VLM client: {e}")
        return
    
    # Test VLM analysis
    try:
        print("\n🧠 Testing VLM analysis...")
        
        response = chat_completion_with_vision(
            "You are analyzing an image.",
            "What do you see in this image? Describe it in detail.",
            latest,
            max_tokens=300
        )
        
        print("\n✅ VLM Response:")
        print("="*50)
        print(response)
        print("="*50)
        
    except Exception as e:
        print(f"❌ VLM analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vlm_on_screenshot()
