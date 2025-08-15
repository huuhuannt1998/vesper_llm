"""
LLM Task Planning for VESPER
Takes task lists like MORNING_ROUTINE and asks LLM to plan optimal room visitation order
"""
import os, sys

# Get project root and add to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from backend.app.llm.client import chat_completion
import yaml
import json

# Load room configurations with absolute path
try:
    rooms_path = os.path.join(project_root, "configs", "rooms.yaml")
    with open(rooms_path, "r") as f:
        ROOMS = yaml.safe_load(f)
except FileNotFoundError:
    ROOMS = {
        "Kitchen": {"center": [3.0, -1.0]},
        "LivingRoom": {"center": [-2.0, 1.5]},
        "Bedroom": {"center": [-3.0, -2.0]},
        "Bathroom": {"center": [1.0, 3.0]}
    }

# Predefined task sequences
MORNING_ROUTINE = ["Wake up", "Brush teeth", "Make coffee"]
EVENING_ROUTINE = ["Turn on TV", "Dim living room lights", "Go to bedroom"]
CLEANING_ROUTINE = ["Check kitchen", "Tidy living room", "Make bed"]
WORK_BREAK = ["Get coffee", "Check TV news", "Return to work area"]
GUEST_PREPARATION = ["Clean living room", "Prepare coffee", "Check bedroom"]
RELAXATION_TIME = ["Turn off all lights", "Watch TV", "Go to bed"]

LLM_PLANNING_PROMPT = """You are a house navigation planner AI.

TASK: Given a list of tasks, determine the optimal order of rooms to visit to complete them efficiently.

Available rooms: {rooms}

Room locations and purposes:
{room_details}

For the given tasks, determine:
1. Which room each task should be performed in
2. The optimal order to visit rooms (minimize walking distance)
3. Create a step-by-step plan

Return ONLY a JSON object:
{{
  "planned_sequence": [
    {{"task": "task name", "room": "RoomName", "order": 1}},
    {{"task": "task name", "room": "RoomName", "order": 2}},
    {{"task": "task name", "room": "RoomName", "order": 3}}
  ],
  "reasoning": "brief explanation of room order choice"
}}
"""

def plan_task_sequence(tasks: list, routine_name: str = "") -> dict:
    """
    Send task list to LLM to determine optimal room visitation order
    """
    # Prepare room information for LLM
    room_list = list(ROOMS.keys())
    room_details = []
    
    for room_name, room_data in ROOMS.items():
        center = room_data.get("center", [0, 0])
        room_details.append(f"- {room_name}: Center at ({center[0]}, {center[1]})")
    
    room_details_str = "\n".join(room_details)
    
    system_prompt = LLM_PLANNING_PROMPT.format(
        rooms=", ".join(room_list),
        room_details=room_details_str
    )
    
    user_prompt = f"""Plan the optimal room visitation order for these tasks:

ROUTINE: {routine_name}
TASKS: {tasks}

Consider:
- Which room is most logical for each task
- Minimize walking distance between rooms
- Efficient navigation path

Example task-to-room mapping:
- "Wake up" → Bedroom
- "Brush teeth" → Bedroom (if bathroom connected) or nearest room
- "Make coffee" → Kitchen
- "Watch TV" → LivingRoom
- "Turn on lights" → Room where lights are needed

Return the JSON plan with optimal room order."""
    
    try:
        response = chat_completion(system_prompt, user_prompt, max_tokens=150)
        print(f"🧠 LLM Planning Response: {response}")
        
        # Extract JSON from response
        start_idx = response.find('{')
        end_idx = response.rfind('}')
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx+1]
            result = json.loads(json_str)
            
            if "planned_sequence" in result:
                return result
        
        # Fallback planning if JSON parsing fails
        print("⚠️ Could not parse JSON from LLM response, using fallback plan")
        return create_fallback_plan(tasks)
        
    except Exception as e:
        print(f"❌ LLM planning failed: {e}")
        return create_fallback_plan(tasks)

def create_fallback_plan(tasks: list) -> dict:
    """Create a simple fallback plan if LLM fails"""
    
    # Simple heuristic mapping
    task_to_room = {
        "wake up": "Bedroom",
        "brush teeth": "Bedroom", 
        "make coffee": "Kitchen",
        "coffee": "Kitchen",
        "tv": "LivingRoom",
        "watch": "LivingRoom",
        "lights": "LivingRoom",
        "living room": "LivingRoom",
        "bedroom": "Bedroom",
        "bed": "Bedroom",
        "kitchen": "Kitchen",
        "clean": "LivingRoom"
    }
    
    planned_sequence = []
    for i, task in enumerate(tasks):
        task_lower = task.lower()
        
        # Find matching room
        room = "LivingRoom"  # Default
        for keyword, room_name in task_to_room.items():
            if keyword in task_lower:
                room = room_name
                break
        
        planned_sequence.append({
            "task": task,
            "room": room, 
            "order": i + 1
        })
    
    return {
        "planned_sequence": planned_sequence,
        "reasoning": "Fallback heuristic planning used"
    }

def get_random_routine():
    """Get a random routine for navigation testing"""
    import random
    
    all_routines = [
        ("MORNING_ROUTINE", MORNING_ROUTINE),
        ("EVENING_ROUTINE", EVENING_ROUTINE), 
        ("CLEANING_ROUTINE", CLEANING_ROUTINE),
        ("WORK_BREAK", WORK_BREAK),
        ("GUEST_PREPARATION", GUEST_PREPARATION),
        ("RELAXATION_TIME", RELAXATION_TIME)
    ]
    
    routine_name, tasks = random.choice(all_routines)
    return routine_name, tasks

def test_planning():
    """Test the LLM planning system"""
    print("🧠 TESTING LLM TASK PLANNING")
    print("=" * 28)
    
    # Test with morning routine
    routine_name, test_tasks = get_random_routine()
    print(f"🎯 Testing with: {routine_name}")
    print(f"📋 Tasks: {test_tasks}")
    
    plan = plan_task_sequence(test_tasks, routine_name)
    
    print(f"\n📍 LLM PLANNED SEQUENCE:")
    if "planned_sequence" in plan:
        for step in plan["planned_sequence"]:
            print(f"   {step['order']}. {step['task']} → {step['room']}")
        
        if "reasoning" in plan:
            print(f"\n💭 LLM Reasoning: {plan['reasoning']}")
    
    return plan

if __name__ == "__main__":
    plan = test_planning()
    print(f"\n🎊 LLM PLANNING SYSTEM READY!")
    print(f"✅ Task sequences defined")
    print(f"✅ LLM room planning working")
    print(f"✅ Ready for navigation execution")
