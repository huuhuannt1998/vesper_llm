#!/usr/bin/env python3
"""
Test VLM navigation with actual BGE screenshots
"""
import sys
import os
import json
import shutil

# Add the backend path to import the LLM client
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))
os.chdir(os.path.dirname(__file__))

try:
    from backend.app.llm.client import chat_completion_with_vision
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))
    from llm.client import chat_completion_with_vision

def test_navigation_sequence():
    """Test VLM navigation with sequence of BGE screenshots"""
    
    captures_dir = "blender/captures"
    if not os.path.exists(captures_dir):
        print(f"❌ Captures directory not found: {captures_dir}")
        return
    
    # Get all BGE screenshots
    screenshots = [f for f in os.listdir(captures_dir) if f.startswith("bge_") and f.endswith(".png")]
    screenshots.sort()
    
    if not screenshots:
        print(f"❌ No BGE screenshots found in {captures_dir}")
        return
    
    print(f"🔍 Found {len(screenshots)} screenshots to test")
    
    # Test first few screenshots to see VLM decision progression
    test_positions = [
        [-2.04, -0.58],  # Starting position
        [-2.34, -0.58],  # After first LEFT move
        [-2.64, -0.58],  # After second LEFT move
        [-2.94, -0.58],  # After third LEFT move
        [-3.24, -0.58],  # After fourth LEFT move
    ]
    
    for i, (screenshot, position) in enumerate(zip(screenshots[:5], test_positions)):
        print(f"\n📍 Step {i+1}: Testing {screenshot}")
        print(f"🎯 Simulated Actor Position: [{position[0]:.2f}, {position[1]:.2f}]")
        
        screenshot_path = os.path.join(captures_dir, screenshot)
        decision = test_vlm_navigation(screenshot_path, "Cook in kitchen", position)
        
        if decision:
            print(f"🧠 VLM Decision: {decision['next_direction']}")
            print(f"💭 Reasoning: {decision['reasoning']}")
        else:
            print(f"❌ Failed to get VLM decision")
        
        print("=" * 50)

def test_vlm_navigation(screenshot_path, task, actor_position):
    """Test VLM navigation decision for a single screenshot"""
    
    if not os.path.exists(screenshot_path):
        print(f"❌ Screenshot not found: {screenshot_path}")
        return None
    
    # Create navigation prompt
    system_prompt = "You are a navigation AI. Analyze the bird's eye view image and respond only in JSON format."

    user_prompt = f'''Task: {task}
Actor Position: [{actor_position[0]:.2f}, {actor_position[1]:.2f}]

Look at this bird's eye view image. The pink/colored dot is the actor you control.

Choose the best direction to move toward the kitchen:
- Dark areas = walls (avoid)
- Light areas = open space (safe to move)
- Look for kitchen features like counters, appliances, sinks

Respond ONLY in this JSON format:
{{
  "next_direction": "UP/DOWN/LEFT/RIGHT/STAY",
  "reasoning": "brief explanation"
}}'''

    try:
        # Read and encode image
        import base64
        with open(screenshot_path, 'rb') as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Get VLM decision
        response = chat_completion_with_vision(user_prompt, image_base64=image_data)
        
        # Clean and parse JSON response
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        decision = json.loads(clean_response)
        return decision
        
    except Exception as e:
        print(f"❌ VLM navigation test failed: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Testing VLM navigation with BGE screenshots...")
    test_navigation_sequence()
