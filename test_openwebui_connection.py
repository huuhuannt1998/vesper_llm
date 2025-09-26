#!/usr/bin/env python3
"""
Test script to verify connection to Open WebUI server
"""

import requests
import json
import sys
import time

def test_openwebui_connection():
    """Test the connection to the Open WebUI server"""
    
    print("🔍 Testing Open WebUI Server Connection")
    print("=" * 50)
    
    # Server configuration from your example
    url = 'http://cci-siscluster1.charlotte.edu:8080/api/chat/completions'
    headers = {
        'Authorization': 'Bearer sk-a6af2053d49649d2925ff91fef71cb65',
        'Content-Type': 'application/json'
    }
    
    # Test with a simple text prompt first
    test_data = {
        "model": "OpenGVLab/InternVL3_5-30B-A3B",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that strictly follows the user's instructions."
            },
            {
                "role": "user",
                "content": "Say only the word 'PONG' to test the connection."
            }
        ]
    }
    
    try:
        print(f"📡 Testing connection to: {url}")
        print(f"🔑 Using model: {test_data['model']}")
        
        start_time = time.time()
        response = requests.post(url, headers=headers, json=test_data, timeout=30)
        end_time = time.time()
        
        print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
        print(f"🔍 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Connection successful!")
            print(f"📄 Response structure: {list(result.keys())}")
            
            # Try to extract the content
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"💬 Model response: '{content}'")
                print("✅ Text completion test passed!")
                return True, result
            else:
                print(f"⚠️ Unexpected response format: {result}")
                return False, result
                
        else:
            print(f"❌ Connection failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print("❌ Connection timed out (30s)")
        return False, None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None


def test_openwebui_vision():
    """Test vision capabilities with a simple base64 image"""
    
    print("\n🖼️ Testing Open WebUI Vision Capabilities")
    print("=" * 50)
    
    # Create a simple test image in base64 (1x1 red pixel PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    url = 'http://cci-siscluster1.charlotte.edu:8080/api/chat/completions'
    headers = {
        'Authorization': 'Bearer sk-a6af2053d49649d2925ff91fef71cb65',
        'Content-Type': 'application/json'
    }
    
    test_data = {
        "model": "OpenGVLab/InternVL3_5-30B-A3B",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that analyzes images."
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": "What do you see in this image? Describe it briefly."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{test_image_b64}"
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        print(f"📡 Testing vision capabilities...")
        
        start_time = time.time()
        response = requests.post(url, headers=headers, json=test_data, timeout=60)
        end_time = time.time()
        
        print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
        print(f"🔍 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Vision test successful!")
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"👁️ Vision response: '{content}'")
                print("✅ Vision completion test passed!")
                return True, result
            else:
                print(f"⚠️ Unexpected vision response format: {result}")
                return False, result
                
        else:
            print(f"❌ Vision test failed with status {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Vision test error: {e}")
        return False, None


def test_server_info():
    """Get server information if available"""
    
    print("\n🛠️ Testing Server Information")
    print("=" * 50)
    
    base_url = 'http://cci-siscluster1.charlotte.edu:8080'
    headers = {
        'Authorization': 'Bearer sk-a6af2053d49649d2925ff91fef71cb65',
        'Content-Type': 'application/json'
    }
    
    # Try to get models list
    try:
        models_url = f"{base_url}/api/models"
        print(f"📡 Checking available models at: {models_url}")
        
        response = requests.get(models_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Models endpoint accessible!")
            print(f"📋 Available models: {len(models.get('data', []))} found")
            
            for model in models.get('data', [])[:5]:  # Show first 5 models
                print(f"  - {model.get('id', 'Unknown')}")
            
            if len(models.get('data', [])) > 5:
                print(f"  ... and {len(models.get('data', [])) - 5} more")
                
        else:
            print(f"⚠️ Models endpoint returned status {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Could not get models list: {e}")


if __name__ == "__main__":
    print("🧪 VESPER Open WebUI Server Tests")
    print("=" * 60)
    
    # Test basic connection
    text_success, text_result = test_openwebui_connection()
    
    # Test vision capabilities 
    vision_success, vision_result = test_openwebui_vision()
    
    # Get server info
    test_server_info()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Text completion: {'✅ PASS' if text_success else '❌ FAIL'}")
    print(f"Vision completion: {'✅ PASS' if vision_success else '❌ FAIL'}")
    
    if text_success:
        print("\n🎉 Server is ready for integration!")
        print("✅ The Open WebUI server is working correctly")
        print("✅ Model responds to text prompts")
        if vision_success:
            print("✅ Vision capabilities are working")
        else:
            print("⚠️ Vision capabilities may need adjustment")
    else:
        print("\n❌ Server connection issues detected")
        print("🔧 Please check server status and credentials")
        
    sys.exit(0 if text_success else 1)