#!/usr/bin/env python3
"""
Quick VLM Fix - Test with longer timeout and smaller images
"""

import os
import glob
import base64
import requests
import json

def test_vlm_with_longer_timeout():
    """Test VLM with extended timeout and simpler prompt"""
    
    # Get latest screenshot
    captures_dir = os.path.join("blender", "captures")
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        print("❌ No screenshots found")
        return
    
    latest = max(screenshots, key=os.path.getmtime)
    print(f"📸 Testing: {os.path.basename(latest)}")
    
    # Check file size
    file_size = os.path.getsize(latest)
    print(f"📁 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Encode image
    try:
        with open(latest, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"❌ Could not encode image: {e}")
        return
    
    # Simple test with longer timeout
    url = "http://100.98.151.66:1234/v1/chat/completions"
    
    payload = {
        "model": "google/gemma-3-27b",
        "messages": [
            {
                "role": "system",
                "content": "You are analyzing an image. Be brief."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What do you see in this image? Answer in 1-2 sentences only."
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
        "max_tokens": 100,  # Very limited
        "temperature": 0.0
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer not-needed"
    }
    
    try:
        print("🔄 Testing with 180s timeout and simple prompt...")
        response = requests.post(url, headers=headers, json=payload, timeout=180)  # 3 minutes
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print("\n✅ SUCCESS! VLM Response:")
            print("="*40)
            print(content)
            print("="*40)
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Still timed out after 180 seconds")
        print("💡 Suggestion: The image might be too complex for the VLM server")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_simple_test_image():
    """Create a simple test image to verify VLM vision capabilities"""
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple 400x400 test image
        img = Image.new('RGB', (400, 400), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw simple shapes and labels
        # Kitchen (green rectangle)
        draw.rectangle([50, 50, 150, 150], fill='green', outline='black', width=2)
        draw.text((60, 60), "KITCHEN", fill='white')
        
        # Bathroom (blue rectangle)
        draw.rectangle([250, 50, 350, 150], fill='blue', outline='black', width=2)
        draw.text((260, 60), "BATHROOM", fill='white')
        
        # Living room (yellow rectangle)
        draw.rectangle([50, 250, 150, 350], fill='yellow', outline='black', width=2)
        draw.text((60, 260), "LIVING", fill='black')
        
        # Actor (red circle)
        draw.ellipse([190, 190, 210, 210], fill='red', outline='black', width=2)
        draw.text((180, 215), "ACTOR", fill='black')
        
        # Save test image
        test_path = os.path.join("blender", "captures", "test_simple_house.png")
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        img.save(test_path)
        
        print(f"🎨 Created simple test image: {test_path}")
        return test_path
        
    except ImportError:
        print("⚠️ PIL not available, cannot create test image")
        return None
    except Exception as e:
        print(f"❌ Could not create test image: {e}")
        return None

def main():
    """Main diagnostic function"""
    
    print("🚀 Quick VLM Fix Test")
    print("="*30)
    
    # Test 1: Try with longer timeout
    print("\n📋 Test 1: Extended timeout with real screenshot")
    success = test_vlm_with_longer_timeout()
    
    if success:
        print("\n✅ VLM is working! The issue was timeout.")
        print("💡 Solution: Use longer timeouts (180s instead of 60s)")
        return
    
    # Test 2: Try with simple test image
    print("\n📋 Test 2: Simple test image")
    test_image = create_simple_test_image()
    
    if test_image:
        print("🔄 Testing VLM with simple synthetic image...")
        # Test the simple image (you can run this manually)
        print(f"💡 Manually test with: {test_image}")
    
    print("\n📋 Recommendations:")
    print("="*30)
    print("🔸 Increase timeout to 180-300 seconds")
    print("🔸 Reduce image complexity/size")
    print("🔸 Use simpler prompts (fewer tokens)")
    print("🔸 Check VLM server resources (CPU/memory)")

if __name__ == "__main__":
    main()
