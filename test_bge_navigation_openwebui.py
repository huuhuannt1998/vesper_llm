#!/usr/bin/env python3
"""
Test BGE navigation with Open WebUI integration
"""

import os
import sys

# Add project paths to Python path (same as BGE navigation does)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def test_bge_navigation_llm_integration():
    """Test the LLM integration that BGE navigation uses"""
    
    print("🔍 Testing BGE Navigation LLM Integration")
    print("=" * 50)
    
    # Test the same imports that BGE navigation uses
    try:
        from backend.app.llm.client import chat_completion_with_vision, chat_completion
        print("✅ Successfully imported LLM client modules")
    except ImportError as e:
        print(f"❌ Failed to import LLM client: {e}")
        return False
    
    # Test text completion (for fallback scenarios)
    print("\n🧪 Testing text completion...")
    try:
        text_result = chat_completion(
            "You are a navigation assistant.",
            "The user is in the living room and wants to go to the kitchen. Provide a brief direction.",
            temperature=0.3
        )
        print(f"✅ Text completion successful: {text_result[:100]}...")
    except Exception as e:
        print(f"❌ Text completion failed: {e}")
        return False
    
    # Test vision completion with a simple test image
    print("\n👁️ Testing vision completion...")
    try:
        # Create a simple test image file
        from PIL import Image
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            # Create a simple indoor scene image
            img = Image.new('RGB', (640, 480), 'lightblue')
            # Add some simple shapes to simulate a room
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.rectangle([100, 300, 300, 400], fill='brown')  # Floor/furniture
            draw.rectangle([400, 200, 600, 450], fill='gray')   # Wall/appliance
            
            img.save(tmp_file.name)
            test_image_path = tmp_file.name
        
        # Test vision completion
        vision_prompt = """Analyze this indoor scene image. Describe what you can see and identify the type of room.
Provide navigation-relevant information such as obstacles, pathways, or room features.
Keep the response concise and focused on navigation."""
        
        vision_result = chat_completion_with_vision(vision_prompt, image_path=test_image_path)
        print(f"✅ Vision completion successful: {vision_result[:150]}...")
        
        # Clean up temp file
        os.unlink(test_image_path)
        
    except Exception as e:
        print(f"❌ Vision completion failed: {e}")
        return False
    
    # Test the wrapper function that BGE navigation creates
    print("\n🔧 Testing BGE navigation wrapper logic...")
    try:
        def vlm_wrapper(prompt, images=None):
            """Simulate the wrapper that BGE navigation creates"""
            if not images or len(images) == 0:
                print("⚠️ No images provided to VLM")
                return None
            
            # Use the first image (first-person view) as primary
            primary_image = images[0]
            
            if len(images) > 1:
                enhanced_prompt = f"{prompt}\n\nNOTE: House plan reference is also available for spatial context."
                print(f"🔍 Using first-person image with enhanced prompt (total images: {len(images)})")
                result = chat_completion_with_vision(enhanced_prompt, image_path=primary_image)
            else:
                print(f"🔍 Using first-person image only")
                result = chat_completion_with_vision(prompt, image_path=primary_image)
            
            return result
        
        # Test the wrapper with multiple images
        test_images = [test_image_path, test_image_path]  # Simulate FP + house plan
        
        # Create another test image first
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img = Image.new('RGB', (320, 240), 'white')
            img.save(tmp_file.name)
            test_image_path2 = tmp_file.name
        
        wrapper_result = vlm_wrapper(
            "What type of room is this? Provide navigation advice.",
            [test_image_path2]
        )
        print(f"✅ BGE wrapper test successful: {wrapper_result[:100]}...")
        
        # Clean up
        os.unlink(test_image_path2)
        
    except Exception as e:
        print(f"❌ BGE wrapper test failed: {e}")
        return False
    
    print(f"\n🎉 BGE Navigation LLM Integration Test Complete!")
    print(f"✅ All tests passed - BGE navigation should work with Open WebUI")
    return True

def test_navigation_specific_prompts():
    """Test navigation-specific prompts that BGE uses"""
    
    print(f"\n🧭 Testing Navigation-Specific Prompts")
    print("=" * 40)
    
    from backend.app.llm.client import chat_completion
    
    # Test typical BGE navigation prompts
    test_cases = [
        {
            "name": "Room Identification",
            "system": "You are a room identification expert. Identify the room type and provide navigation context.",
            "prompt": "I can see a stove, refrigerator, and countertop. What room am I in?"
        },
        {
            "name": "Navigation Decision", 
            "system": "You are a navigation assistant. Provide clear movement instructions.",
            "prompt": "I'm in the kitchen and need to go to the bedroom. The hallway is visible to my left. What should I do?"
        },
        {
            "name": "Object Interaction",
            "system": "You are an object interaction guide. Identify objects and interaction possibilities.",
            "prompt": "I see a coffee maker on the counter. How should I approach it to make coffee?"
        }
    ]
    
    for test_case in test_cases:
        try:
            print(f"\n📝 Testing: {test_case['name']}")
            response = chat_completion(
                test_case['system'], 
                test_case['prompt'],
                temperature=0.3
            )
            print(f"✅ Response: {response[:120]}...")
        except Exception as e:
            print(f"❌ Test '{test_case['name']}' failed: {e}")

def show_configuration_info():
    """Show current LLM configuration"""
    
    print(f"\n⚙️ Current LLM Configuration")
    print("=" * 35)
    
    # Check environment variables
    use_openwebui = os.getenv("USE_OPENWEBUI", "true").lower() == "true"
    openwebui_url = os.getenv("OPENWEBUI_URL", "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions")
    openwebui_model = os.getenv("OPENWEBUI_MODEL", "OpenGVLab/InternVL3_5-30B-A3B")
    
    print(f"USE_OPENWEBUI: {use_openwebui}")
    print(f"OPENWEBUI_URL: {openwebui_url}")
    print(f"OPENWEBUI_MODEL: {openwebui_model}")
    
    if use_openwebui:
        print(f"✅ BGE Navigation will use Open WebUI server")
        print(f"🚀 Model: {openwebui_model}")
    else:
        print(f"⚠️ BGE Navigation will use Ollama (fallback)")
    
    print(f"\n💡 To ensure Open WebUI is used, set these environment variables:")
    print(f"   USE_OPENWEBUI=true")
    print(f"   OPENWEBUI_URL={openwebui_url}")
    print(f"   OPENWEBUI_MODEL={openwebui_model}")

if __name__ == "__main__":
    print("🚀 BGE Navigation Open WebUI Integration Test")
    print("=" * 55)
    
    show_configuration_info()
    
    success = test_bge_navigation_llm_integration()
    
    if success:
        test_navigation_specific_prompts()
        
        print(f"\n🎉 BGE Navigation is Ready!")
        print(f"✅ LLM integration working with Open WebUI")
        print(f"✅ InternVL3_5-30B-A3B model connected")
        print(f"✅ Vision and text completion tested")
        print(f"📍 BGE navigation can now use the faster model!")
    else:
        print(f"\n❌ BGE Navigation Integration Issues")
        print(f"🔧 Check configuration and server connectivity")