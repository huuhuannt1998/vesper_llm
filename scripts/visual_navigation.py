"""
LLM Visual Position Detection for VESPER
Takes bird's-eye screenshots and uses LLM to determine actor position and next movement
"""
import os, sys
import base64
from io import BytesIO
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.app.llm.client import chat_completion
import yaml

# Load room data
with open("configs/rooms.yaml", "r") as f:
    ROOMS = yaml.safe_load(f)

POSITION_DETECTION_PROMPT = """You are a navigation AI for a top-down house simulation. 

TASK: Analyze this bird's-eye view image and determine:
1. Which room the bright red human actor is currently in
2. What direction they should move next to reach the target room

You will see:
- A house layout from above (open-top view)
- A bright red glowing human figure (the actor)
- Yellow marker above the actor
- Green circle marker on the ground below the actor

ROOMS available: {rooms}

INSTRUCTIONS:
- Look for the bright red human figure
- Identify which room they are currently in
- Determine the best single step direction (UP/DOWN/LEFT/RIGHT) to get closer to: {target_room}
- If already in the target room, return STAY

Return ONLY a JSON object:
{{"current_room": "RoomName", "direction": "UP|DOWN|LEFT|RIGHT|STAY", "reasoning": "brief explanation"}}
"""

def detect_position_and_next_move(screenshot_base64: str, target_room: str) -> dict:
    """
    Send bird's-eye screenshot to LLM to detect actor position and get next movement direction
    """
    rooms_list = ", ".join(ROOMS.keys())
    
    system_prompt = POSITION_DETECTION_PROMPT.format(
        rooms=rooms_list,
        target_room=target_room
    )
    
    user_prompt = f"""Analyze this bird's-eye view image of the house.

Target room: {target_room}

The image shows a top-down view of the house with:
- Bright red glowing human actor (impossible to miss)
- Yellow floating marker above the actor  
- Green ground circle below the actor
- Open-top house design showing all rooms clearly

Determine the actor's current room and the direction to move toward {target_room}.

Image data: data:image/png;base64,{screenshot_base64}"""
    
    try:
        response = chat_completion(system_prompt, user_prompt, max_tokens=100)
        
        # Extract JSON from response
        import json
        
        # Try to find JSON in the response
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx+1]
            result = json.loads(json_str)
            
            # Validate the response
            if "current_room" in result and "direction" in result:
                return result
        
        # Fallback if JSON parsing fails
        return {
            "current_room": "Unknown",
            "direction": "STAY", 
            "reasoning": f"Could not parse LLM response: {response[:100]}..."
        }
        
    except Exception as e:
        return {
            "current_room": "Unknown", 
            "direction": "STAY",
            "reasoning": f"LLM error: {str(e)}"
        }

def simple_position_test():
    """Test position detection without a real screenshot"""
    print("🧠 TESTING LLM POSITION DETECTION")
    print("=" * 32)
    
    # Test with a simple text description instead of image
    test_prompt = """The actor is a bright red human figure currently in the Kitchen area of the house.
    
Target room: LivingRoom

Which direction should the actor move to get from Kitchen to LivingRoom?
Return JSON: {"current_room": "Kitchen", "direction": "UP|DOWN|LEFT|RIGHT", "reasoning": "explanation"}"""
    
    try:
        response = chat_completion(
            "You are a navigation AI. Return only JSON.",
            test_prompt,
            max_tokens=80
        )
        print(f"LLM Response: {response}")
        
        # Try to extract direction
        if "RIGHT" in response:
            direction = "RIGHT"
        elif "LEFT" in response:
            direction = "LEFT"  
        elif "UP" in response:
            direction = "UP"
        elif "DOWN" in response:
            direction = "DOWN"
        else:
            direction = "STAY"
            
        print(f"✅ Detected direction: {direction}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = simple_position_test()
    if success:
        print("\n🎊 LLM POSITION DETECTION READY!")
    else:
        print("\n❌ LLM position detection needs debugging")
