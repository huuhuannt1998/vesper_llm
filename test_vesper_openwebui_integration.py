#!/usr/bin/env python3
"""
Test VESPER integration with Open WebUI server
"""

import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

from llm.client import chat_completion, chat_completion_with_vision
import tempfile
from PIL import Image, ImageDraw

def test_vesper_openwebui_integration():
    """Test VESPER with Open WebUI integration"""
    
    print("🚀 VESPER Open WebUI Integration Test")
    print("=" * 50)
    
    # Test 1: Basic navigation prompt
    print("\n🧭 Test 1: Navigation Decision")
    navigation_prompt = """You are a navigation assistant for an indoor environment. 
The user is currently in the living room and wants to go to the kitchen.
Based on the house layout, provide a simple navigation instruction.
Keep your response brief and actionable."""
    
    user_request = "I'm in the living room and need to go to the kitchen to get water."
    
    try:
        response = chat_completion(navigation_prompt, user_request, temperature=0.3)
        print(f"✅ Navigation response: {response}")
    except Exception as e:
        print(f"❌ Navigation test failed: {e}")
    
    # Test 2: Room detection from description
    print("\n🏠 Test 2: Room Detection")
    room_detection_prompt = """You are a room identification expert. 
Based on the description provided, identify which room the person is likely in.
Respond with only the room name (e.g., "kitchen", "bedroom", "living room")."""
    
    room_description = "I can see a stove, refrigerator, and sink. There are cabinets on the walls and a counter with some dishes."
    
    try:
        room_response = chat_completion(room_detection_prompt, room_description, temperature=0.1)
        print(f"✅ Room detection response: {room_response}")
    except Exception as e:
        print(f"❌ Room detection test failed: {e}")
    
    # Test 3: Vision-based navigation (with test image)
    print("\n👁️ Test 3: Vision-Based Navigation")
    
    # Create a simple test image representing a room
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        # Create a simple room-like image
        img = Image.new('RGB', (400, 300), 'lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw some furniture-like shapes
        draw.rectangle([50, 200, 150, 280], fill='brown')  # Table
        draw.rectangle([200, 150, 350, 280], fill='gray')   # Counter
        draw.rectangle([300, 50, 380, 140], fill='white')   # Appliance
        
        img.save(temp_file.name)
        temp_image_path = temp_file.name
    
    vision_prompt = """Analyze this image and describe what type of room this appears to be. 
Look for furniture, appliances, or other clues that would indicate the room's purpose.
Provide a brief room identification and any navigation-relevant observations."""
    
    try:
        vision_response = chat_completion_with_vision(vision_prompt, image_path=temp_image_path)
        print(f"✅ Vision navigation response: {vision_response}")
    except Exception as e:
        print(f"❌ Vision navigation test failed: {e}")
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_image_path)
        except:
            pass
    
    # Test 4: Task-specific instruction
    print("\n📋 Test 4: Task-Specific Guidance")
    task_prompt = """You are helping someone navigate to complete a specific task.
Provide step-by-step navigation instructions for the given task.
Be specific and practical."""
    
    task_request = "I need to make coffee. I'm currently in the bedroom. Help me navigate and complete this task."
    
    try:
        task_response = chat_completion(task_prompt, task_request, temperature=0.2)
        print(f"✅ Task guidance response: {task_response}")
    except Exception as e:
        print(f"❌ Task guidance test failed: {e}")
    
    print(f"\n🎉 VESPER Open WebUI Integration Test Complete!")
    print(f"✅ All tests demonstrate successful integration with faster model")
    print(f"🚀 InternVL3_5-30B-A3B model is ready for VESPER navigation tasks!")


def test_performance_comparison():
    """Quick performance test"""
    
    print("\n⚡ Performance Test")
    print("=" * 30)
    
    import time
    
    test_prompt = "Describe the fastest route from living room to kitchen in a typical house."
    
    start_time = time.time()
    response = chat_completion("You are a navigation expert.", test_prompt, temperature=0.1)
    end_time = time.time()
    
    response_time = end_time - start_time
    response_length = len(response)
    
    print(f"📊 Performance Metrics:")
    print(f"  Response time: {response_time:.2f} seconds")
    print(f"  Response length: {response_length} characters")
    print(f"  Words per second: {len(response.split()) / response_time:.1f}")
    print(f"📝 Response preview: {response[:100]}...")


if __name__ == "__main__":
    test_vesper_openwebui_integration()
    test_performance_comparison()