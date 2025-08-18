#!/usr/bin/env python3
"""
Lightweight VLM Test - Check image size and test with simpler requests
"""

import os
import glob
from PIL import Image

def check_image_details():
    """Check the size and details of the latest screenshot"""
    
    captures_dir = os.path.join("blender", "captures")
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        print("❌ No screenshots found")
        return None
    
    latest = max(screenshots, key=os.path.getmtime)
    
    # Check file details
    file_size = os.path.getsize(latest)
    print(f"📸 Screenshot: {os.path.basename(latest)}")
    print(f"📁 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    # Check image dimensions
    try:
        with Image.open(latest) as img:
            width, height = img.size
            print(f"📏 Dimensions: {width} x {height} pixels")
            print(f"🎨 Mode: {img.mode}")
            
            # Calculate if image is too large
            total_pixels = width * height
            print(f"🔢 Total pixels: {total_pixels:,}")
            
            if file_size > 5 * 1024 * 1024:  # 5MB
                print("⚠️  Image is quite large - this might cause timeouts")
                return "large"
            elif total_pixels > 2000 * 2000:  # 4M pixels
                print("⚠️  High resolution - might need compression")
                return "high_res"
            else:
                print("✅ Image size looks reasonable")
                return "ok"
                
    except Exception as e:
        print(f"❌ Could not analyze image: {e}")
        return None

def create_compressed_version():
    """Create a smaller version of the screenshot for faster VLM processing"""
    
    captures_dir = os.path.join("blender", "captures")
    screenshots = glob.glob(os.path.join(captures_dir, "bge_screenshot_*.png"))
    
    if not screenshots:
        return None
    
    latest = max(screenshots, key=os.path.getmtime)
    
    try:
        with Image.open(latest) as img:
            # Calculate new size (max 800x800)
            width, height = img.size
            max_size = 800
            
            if width > max_size or height > max_size:
                ratio = min(max_size / width, max_size / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                # Resize image
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save compressed version
                compressed_path = latest.replace(".png", "_compressed.png")
                resized.save(compressed_path, "PNG", optimize=True)
                
                compressed_size = os.path.getsize(compressed_path)
                print(f"🗜️  Created compressed version: {os.path.basename(compressed_path)}")
                print(f"📏 New dimensions: {new_width} x {new_height}")
                print(f"📁 New size: {compressed_size:,} bytes ({compressed_size/1024/1024:.2f} MB)")
                
                return compressed_path
            else:
                print("✅ Image is already small enough")
                return latest
                
    except Exception as e:
        print(f"❌ Could not compress image: {e}")
        return None

def test_text_only_vlm():
    """Test if the VLM server works with text-only requests"""
    
    import requests
    import json
    
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
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Say 'Hello! VLM server is working!' in exactly those words."
            }
        ],
        "max_tokens": 50,
        "temperature": 0.0
    }
    
    try:
        print("🔄 Testing text-only request...")
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"✅ Text-only response: {content}")
            return True
        else:
            print(f"❌ Text-only failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Text-only error: {e}")
        return False

def main():
    """Main function to diagnose VLM issues"""
    
    print("🔧 VLM Diagnostic Tool")
    print("="*40)
    
    # Step 1: Check server with text-only
    print("\n1️⃣ Testing VLM server connection...")
    if not test_text_only_vlm():
        print("❌ VLM server is not responding to text requests")
        return
    
    # Step 2: Check image details
    print("\n2️⃣ Analyzing screenshot details...")
    image_status = check_image_details()
    
    if image_status is None:
        print("❌ Could not analyze image")
        return
    
    # Step 3: Create compressed version if needed
    if image_status in ["large", "high_res"]:
        print("\n3️⃣ Creating compressed version...")
        compressed_path = create_compressed_version()
        
        if compressed_path:
            print("✅ Compressed version ready for testing")
            print(f"💡 Try using: {os.path.basename(compressed_path)}")
        else:
            print("❌ Could not create compressed version")
    
    # Step 4: Recommendations
    print("\n📋 Recommendations:")
    print("="*40)
    
    if image_status == "large":
        print("🔸 Your screenshots are too large for the VLM server")
        print("🔸 Use compressed versions or reduce screenshot resolution")
    elif image_status == "high_res":
        print("🔸 High resolution might be causing timeouts")
        print("🔸 Consider using 800x800 or smaller images")
    else:
        print("🔸 Image size is reasonable")
        print("🔸 The timeout might be due to:")
        print("   - VLM server processing load")
        print("   - Network latency")
        print("   - Model complexity with vision tasks")
    
    print("\n💡 Suggested solutions:")
    print("🔸 Increase timeout from 60s to 120s")
    print("🔸 Use compressed/smaller images")
    print("🔸 Test with simpler prompts first")
    print("🔸 Check if server has enough memory/CPU")

if __name__ == "__main__":
    main()
