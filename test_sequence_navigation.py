#!/usr/bin/env python3
"""
Test sequence-based VLM navigation 
"""
import sys
import os
import json

# Add the backend path to import the LLM client
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))
os.chdir(os.path.dirname(__file__))

try:
    from backend.app.llm.client import chat_completion_with_vision
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'app'))
    from llm.client import chat_completion_with_vision

def test_sequence_navigation():
    """Test VLM sequence planning with BGE screenshot"""
    
    screenshot_path = "blender/captures/bge_001.png"
    if not os.path.exists(screenshot_path):
        print(f"❌ Screenshot not found: {screenshot_path}")
        return
    
    tasks = [
        "Go to bedroom",
        "Cook in kitchen", 
        "Rest in living room"
    ]
    
    for task in tasks:
        print(f"\\n{'='*60}")
        print(f"🎯 Task: {task}")
        print(f"{'='*60}")
        
        sequence = get_navigation_sequence(screenshot_path, task)
        if sequence:
            print(f"🧠 VLM Sequence: {sequence['movement_sequence']}")
            print(f"💭 Reasoning: {sequence['reasoning']}")
            print(f"📊 Total Steps: {len(sequence['movement_sequence'])}")
        else:
            print(f"❌ Failed to get sequence for task: {task}")

def get_navigation_sequence(screenshot_path, task):
    """Get movement sequence from VLM"""
    
    system_prompt = "You are a navigation AI. Analyze the bird's eye view image and plan a complete movement sequence."

    user_prompt = f'''Task: {task}

Look at this bird's eye view image. The colored dot/diamond is the actor you control.

Plan a COMPLETE sequence of moves to reach the target location efficiently:
- Analyze the current room and target destination
- Dark areas = walls (avoid)
- Light areas = open space (safe to move)
- Plan 4-8 moves to reach the destination
- Consider doorways, corridors, and room layouts

Room identification:
- Kitchen: Look for counters, appliances, sinks, cooking areas
- Bedroom: Look for beds, dressers, private sleeping areas  
- Living room: Look for sofas, TV areas, open central spaces

Respond ONLY in this JSON format:
{{
  "movement_sequence": ["LEFT", "LEFT", "UP", "RIGHT", "UP"],
  "reasoning": "Current location analysis and path explanation"
}}'''

    try:
        # Read and encode image
        import base64
        with open(screenshot_path, 'rb') as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Get VLM sequence
        response = chat_completion_with_vision(user_prompt, image_base64=image_data)
        
        # Clean and parse JSON response
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        result = json.loads(clean_response)
        
        # Validate sequence
        if "movement_sequence" in result and isinstance(result["movement_sequence"], list):
            valid_moves = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
            sequence = [move for move in result["movement_sequence"] if move in valid_moves]
            
            if sequence:
                return {
                    "movement_sequence": sequence,
                    "reasoning": result.get("reasoning", "No reasoning provided")
                }
        
        print(f"⚠️ Invalid sequence format in response")
        return None
        
    except Exception as e:
        print(f"❌ Sequence planning failed: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Testing sequence-based VLM navigation...")
    test_sequence_navigation()
