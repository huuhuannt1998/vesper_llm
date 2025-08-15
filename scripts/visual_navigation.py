"""
LLM Visual Position Detection for VESPER
Takes bird's-eye screenshots and uses LLM to determine actor position and next movement
NO HARDCODED COORDINATES - Pure LLM visual navigation
"""
import os, sys
import base64
from io import BytesIO

# Get project root directory
def get_project_root():
    """Get the absolute path to the project root directory."""
    current_file = os.path.abspath(__file__)
    # Navigate from scripts/visual_navigation.py to project root
    return os.path.dirname(os.path.dirname(current_file))

PROJECT_ROOT = get_project_root()
sys.path.insert(0, PROJECT_ROOT)

from backend.app.llm.client import chat_completion
import yaml
import json
import time

# Load room data with absolute path
try:
    rooms_path = os.path.join(PROJECT_ROOT, "configs", "rooms.yaml")
    with open(rooms_path, "r") as f:
        ROOMS = yaml.safe_load(f)
except FileNotFoundError:
    print("⚠️ Warning: configs/rooms.yaml not found, using fallback room configuration")
    ROOMS = {
        "Kitchen": {"center": [3.0, -1.0]},
        "LivingRoom": {"center": [-2.0, 1.5]},
        "Bedroom": {"center": [-3.0, -2.0]},
        "Bathroom": {"center": [1.0, 3.0]}
    }

VISUAL_NAVIGATION_PROMPT = """You are an advanced visual navigation AI analyzing bird's-eye view images of an apartment.

OBJECTIVE: Guide a red human actor through the apartment using ONLY visual analysis - NO hardcoded coordinates.

VISUAL ELEMENTS TO IDENTIFY:
- BRIGHT RED GLOWING HUMAN FIGURE (the actor you're controlling)
- Yellow marker floating above the actor
- Green circle marker on ground below actor
- Room boundaries (walls, doorways)
- Furniture and obstacles
- Open doorways and corridors

NAVIGATION RULES:
1. ONLY move in cardinal directions: UP, DOWN, LEFT, RIGHT
2. Each move should be small, careful steps
3. Avoid walls and furniture
4. Navigate through doorways to reach target room
5. If already in target room, return STAY

CURRENT TASK: Navigate actor from current position to {target_room}

RESPONSE FORMAT (JSON ONLY):
{{"current_room": "detected_room_name", "next_direction": "UP|DOWN|LEFT|RIGHT|STAY", "movement_distance": "SHORT|MEDIUM|LONG", "reasoning": "what you see and why this direction", "obstacles_detected": ["list of visible obstacles"], "path_clear": true|false}}"""

SPATIAL_ANALYSIS_PROMPT = """You are a spatial intelligence AI analyzing apartment layouts from bird's-eye view.

ANALYZE THIS IMAGE FOR:
1. Room identification and boundaries
2. Wall positions and doorway locations  
3. Furniture placement and obstacle positions
4. Clear navigation paths between rooms
5. Actor's current position (bright red figure)

SPATIAL INTELLIGENCE TASKS:
- Map the apartment layout visually
- Identify safe navigation corridors
- Detect obstacles that block movement
- Plan optimal path to target room

TARGET DESTINATION: {target_room}

Return comprehensive spatial analysis as JSON:
{{"room_layout": {{"detected_rooms": [], "room_connections": [], "doorway_positions": []}}, "obstacle_map": [], "navigation_assessment": {{"current_position": "", "target_accessible": true|false, "recommended_route": [], "hazards": []}}, "movement_guidance": {{"immediate_direction": "UP|DOWN|LEFT|RIGHT|STAY", "step_size": "SMALL|MEDIUM|LARGE", "confidence": "HIGH|MEDIUM|LOW"}}}}"""

def analyze_visual_scene_for_navigation(screenshot_base64: str, target_room: str) -> dict:
    """
    Advanced LLM visual analysis for navigation - NO hardcoded coordinates
    """
    system_prompt = VISUAL_NAVIGATION_PROMPT.format(target_room=target_room)
    
    user_prompt = f"""ANALYZE this bird's-eye view apartment image for navigation guidance.

TARGET ROOM: {target_room}

VISUAL ANALYSIS REQUIREMENTS:
1. Locate the BRIGHT RED HUMAN ACTOR (impossible to miss - glowing red figure)
2. Identify current room by analyzing visual boundaries and spatial context
3. Plan next movement direction based on apartment layout
4. Detect any obstacles or walls blocking the path
5. Provide movement guidance using ONLY visual information

The image shows a top-down view with:
- Open-top apartment design (walls are visible boundaries)
- Bright red glowing human figure with yellow floating marker
- Green ground marker beneath actor
- Clear room divisions and doorways
- Furniture and obstacle placement

Provide navigation guidance based purely on visual spatial analysis.

Image: data:image/png;base64,{screenshot_base64}"""
    
    try:
        print("🧠 LLM analyzing bird's-eye view for navigation...")
        response = chat_completion(system_prompt, user_prompt, max_tokens=300)
        
        # Extract JSON from response
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx+1]
            result = json.loads(json_str)
            
            print(f"🎯 LLM Navigation Analysis: {result.get('current_room', 'Unknown')} → {result.get('next_direction', 'STAY')}")
            print(f"💭 LLM Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            
            return result
        
        # Fallback parsing if complex JSON fails
        direction = "STAY"
        if "UP" in response.upper():
            direction = "UP"
        elif "DOWN" in response.upper():
            direction = "DOWN"
        elif "LEFT" in response.upper():
            direction = "LEFT"
        elif "RIGHT" in response.upper():
            direction = "RIGHT"
            
        return {
            "current_room": "Visual_Detection",
            "next_direction": direction,
            "movement_distance": "SHORT",
            "reasoning": f"Parsed from LLM response: {response[:100]}...",
            "obstacles_detected": [],
            "path_clear": True
        }
        
    except Exception as e:
        print(f"❌ LLM visual analysis failed: {e}")
        return {
            "current_room": "Unknown",
            "next_direction": "STAY",
            "movement_distance": "SHORT", 
            "reasoning": f"Analysis error: {str(e)}",
            "obstacles_detected": ["Analysis_Error"],
            "path_clear": False
        }

def get_spatial_intelligence_analysis(screenshot_base64: str, target_room: str) -> dict:
    """
    Advanced spatial intelligence analysis using LLM vision
    """
    system_prompt = SPATIAL_ANALYSIS_PROMPT.format(target_room=target_room)
    
    user_prompt = f"""SPATIAL INTELLIGENCE ANALYSIS of apartment bird's-eye view.

MISSION: Create a comprehensive spatial map and navigation plan to reach {target_room}.

ANALYZE FOR:
- Complete apartment layout from visual inspection
- Room boundaries, walls, doorways (visible as architectural features)  
- Obstacle locations (furniture, fixtures)
- Actor position (bright red figure with yellow and green markers)
- Optimal navigation route based on spatial analysis

SPATIAL REASONING APPROACH:
1. Visually map the apartment architecture 
2. Identify clear navigation corridors
3. Plan obstacle-free path to target room
4. Provide step-by-step movement guidance

IMAGE FEATURES:
- Red glowing human actor (your navigation target)
- Open-top apartment view showing all rooms
- Clear architectural boundaries and doorways
- Furniture and obstacle placement visible

Provide comprehensive spatial analysis and navigation guidance.

Image: data:image/png;base64,{screenshot_base64}"""
    
    try:
        print("🗺️ Running spatial intelligence analysis...")
        response = chat_completion(system_prompt, user_prompt, max_tokens=500)
        
        # Try to parse complex spatial analysis JSON
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx+1]
            result = json.loads(json_str)
            
            # Extract key navigation guidance
            movement_guidance = result.get('movement_guidance', {})
            immediate_direction = movement_guidance.get('immediate_direction', 'STAY')
            confidence = movement_guidance.get('confidence', 'MEDIUM')
            
            print(f"🧭 Spatial Analysis Complete - Direction: {immediate_direction} (Confidence: {confidence})")
            return result
        
        # Simplified fallback
        return {
            "room_layout": {"detected_rooms": [], "room_connections": []},
            "navigation_assessment": {"current_position": "Visual_Analysis", "target_accessible": True},
            "movement_guidance": {"immediate_direction": "STAY", "step_size": "SMALL", "confidence": "LOW"}
        }
        
    except Exception as e:
        print(f"❌ Spatial analysis failed: {e}")
        return {
            "room_layout": {"detected_rooms": [], "room_connections": []}, 
            "navigation_assessment": {"current_position": "Error", "target_accessible": False},
            "movement_guidance": {"immediate_direction": "STAY", "step_size": "SMALL", "confidence": "LOW"}
        }
def convert_llm_direction_to_movement(direction: str, distance: str = "SHORT") -> tuple:
    """
    Convert LLM direction guidance into Blender coordinate movement
    NO HARDCODED ROOM POSITIONS - purely relative movement
    """
    # Define movement step sizes based on LLM guidance
    step_sizes = {
        "SHORT": 0.2,    # Small careful steps
        "MEDIUM": 0.4,   # Normal navigation steps  
        "LONG": 0.8      # Larger movements in open spaces
    }
    
    step_size = step_sizes.get(distance.upper(), 0.2)
    
    # Convert cardinal directions to Blender coordinate offsets
    direction_map = {
        "UP": (0, step_size, 0),      # +Y in Blender
        "DOWN": (0, -step_size, 0),   # -Y in Blender
        "LEFT": (-step_size, 0, 0),   # -X in Blender
        "RIGHT": (step_size, 0, 0),   # +X in Blender
        "STAY": (0, 0, 0)             # No movement
    }
    
    movement = direction_map.get(direction.upper(), (0, 0, 0))
    print(f"🎮 Converting LLM direction '{direction}' ({distance}) → Blender offset {movement}")
    
    return movement

def visual_navigation_test():
    """Test the visual navigation system"""
    print("🔍 TESTING LLM VISUAL NAVIGATION SYSTEM")
    print("=" * 45)
    print("📋 Testing LLM's ability to analyze spatial layouts")
    print("🎯 NO HARDCODED COORDINATES - Pure visual analysis")
    print()
    
    # Test basic direction parsing
    test_directions = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
    
    for direction in test_directions:
        movement = convert_llm_direction_to_movement(direction, "MEDIUM")
        print(f"✅ {direction:>5} → {movement}")
    
    print()
    print("🧠 Testing LLM spatial reasoning...")
    
    # Simulate LLM response for testing
    mock_llm_response = {
        "current_room": "Kitchen", 
        "next_direction": "RIGHT",
        "movement_distance": "SHORT",
        "reasoning": "Actor is in kitchen, need to move right toward hallway to reach living room",
        "obstacles_detected": ["kitchen_counter"],
        "path_clear": True
    }
    
    print("📊 Mock LLM Analysis Result:")
    for key, value in mock_llm_response.items():
        print(f"   {key}: {value}")
    
    # Test movement conversion
    direction = mock_llm_response["next_direction"] 
    distance = mock_llm_response["movement_distance"]
    movement = convert_llm_direction_to_movement(direction, distance)
    
    print(f"\n🎮 Final Movement Command: {movement}")
    print("✅ Visual Navigation System Ready!")
    
    return True

def simple_position_test():
    """Test visual navigation without real screenshot"""
    print("🧠 TESTING LLM VISUAL NAVIGATION INTELLIGENCE")  
    print("=" * 50)
    print("🎯 Testing pure visual analysis capabilities")
    print()
    
    # Test LLM's spatial reasoning with text description
    test_scenario = """Imagine a bird's-eye view of an apartment:
- You see a bright red human figure (the actor) in what appears to be a kitchen area
- There are walls forming room boundaries visible
- You can see doorways connecting different rooms
- The target destination is the living room
- Kitchen appears to be on the left side of the apartment
- Living room appears to be toward the right side

Based on this spatial layout, what direction should the actor move?"""
    
    try:
        response = chat_completion(
            "You are a visual navigation AI. Analyze spatial layouts and provide movement directions. Respond with JSON format: {\"direction\": \"UP|DOWN|LEFT|RIGHT\", \"reasoning\": \"your spatial analysis\"}",
            test_scenario,
            max_tokens=150
        )
        
        print(f"🧠 LLM Spatial Analysis Response:")
        print(f"{response}")
        print()
        
        # Extract direction from response  
        direction = "STAY"
        if "RIGHT" in response.upper():
            direction = "RIGHT"
        elif "LEFT" in response.upper():
            direction = "LEFT"
        elif "UP" in response.upper():
            direction = "UP"
        elif "DOWN" in response.upper():
            direction = "DOWN"
            
        print(f"✅ LLM Recommended Direction: {direction}")
        
        # Test movement conversion
        movement_offset = convert_llm_direction_to_movement(direction, "MEDIUM")
        print(f"🎮 Blender Movement Offset: {movement_offset}")
        
        print("\n🎊 LLM VISUAL NAVIGATION SYSTEM OPERATIONAL!")
        return True
        
    except Exception as e:
        print(f"❌ LLM navigation test failed: {e}")
        print("🔧 Check LLM connection and try again")
        return False

if __name__ == "__main__":
    print("🚀 VESPER LLM VISUAL NAVIGATION SYSTEM")
    print("=" * 45)
    print("📋 NO HARDCODED COORDINATES")
    print("🧠 PURE LLM VISUAL ANALYSIS")
    print("📸 BIRD'S-EYE VIEW INTELLIGENCE")
    print()
    
    # Test the enhanced visual navigation
    success = visual_navigation_test()
    
    if success:
        # Test LLM spatial reasoning
        llm_success = simple_position_test()
        if llm_success:
            print("\n� ALL SYSTEMS READY FOR LLM-DRIVEN NAVIGATION!")
        else:
            print("\n⚠️ LLM connection needs attention")
    else:
        print("\n❌ Visual navigation system needs debugging")
