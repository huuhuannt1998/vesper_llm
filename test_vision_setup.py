#!/usr/bin/env python3
"""
Test script to verify Ollama vision setup for VESPER navigation
"""
import os
import sys
import base64
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_text_completion():
    """Test basic text completion"""
    print("🧪 Testing basic text completion...")
    try:
        from backend.app.llm.client import chat_completion
        response = chat_completion(
            "You are a helpful assistant.",
            "Say only the word: pong",
            temperature=0.0
        )
        print(f"✅ Text completion works: {response}")
        return True
    except Exception as e:
        print(f"❌ Text completion failed: {e}")
        return False

def test_vision_capability():
    """Test vision completion with a sample image"""
    print("\n🔍 Testing vision completion...")
    try:
        from backend.app.llm.client import chat_completion_with_vision
        
        # Create a simple test image if none exists
        test_image_path = "test_image.png"
        if not os.path.exists(test_image_path):
            print("📸 Creating test image...")
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (200, 100), color='blue')
                draw = ImageDraw.Draw(img)
                draw.text((10, 10), "VESPER TEST", fill='white')
                img.save(test_image_path)
            except ImportError:
                print("⚠️ PIL not available, skipping image creation test")
                return False
        
        # Test vision completion
        response = chat_completion_with_vision(
            "What do you see in this image? Describe it briefly.",
            image_path=test_image_path
        )
        print(f"✅ Vision completion works: {response}")
        
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return True
    except Exception as e:
        print(f"❌ Vision completion failed: {e}")
        return False

def check_model_availability():
    """Check what models are available"""
    print("\n📋 Checking available models...")
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        print(result.stdout)
        
        if 'llava' in result.stdout:
            print("✅ LLaVA vision model found!")
            return True
        else:
            print("⚠️ No vision models found. Install with: ollama pull llava:7b")
            return False
    except Exception as e:
        print(f"❌ Could not check models: {e}")
        return False

def main():
    print("🚀 VESPER Ollama Vision Setup Test\n")
    
    # Check models first
    models_ok = check_model_availability()
    
    # Test text completion
    text_ok = test_text_completion()
    
    # Test vision (only if models are available)
    vision_ok = False
    if models_ok:
        vision_ok = test_vision_capability()
    
    print("\n" + "="*50)
    print("📊 SETUP SUMMARY:")
    print(f"📋 Models Available: {'✅' if models_ok else '❌'}")
    print(f"💬 Text Completion: {'✅' if text_ok else '❌'}")
    print(f"👁️ Vision Completion: {'✅' if vision_ok else '❌'}")
    
    if models_ok and text_ok and vision_ok:
        print("\n🎉 YOUR OLLAMA SETUP IS READY FOR VESPER NAVIGATION!")
        print("💡 The system can now analyze bird's eye screenshots for navigation.")
    elif models_ok and text_ok:
        print("\n⚠️ PARTIAL SETUP: Text works, but vision needs debugging.")
    else:
        print("\n❌ SETUP INCOMPLETE: Please install vision models and retry.")
        print("💡 Run: ollama pull llava:7b")

if __name__ == "__main__":
    main()
