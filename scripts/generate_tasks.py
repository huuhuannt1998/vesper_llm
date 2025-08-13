"""
Random task generator for VESPER navigation testing
Generates 3 random tasks that require visiting different rooms
"""
import random
import yaml

# Load room and device configurations
with open("configs/rooms.yaml", "r") as f:
    ROOMS = yaml.safe_load(f)

with open("configs/devices.yaml", "r") as f:
    DEVICES = yaml.safe_load(f)

# Predefined task sequences that the LLM will plan room order for
MORNING_ROUTINE = ["Wake up", "Brush teeth", "Make coffee"]
EVENING_ROUTINE = ["Turn on TV", "Dim living room lights", "Go to bedroom"]
CLEANING_ROUTINE = ["Check kitchen", "Tidy living room", "Make bed"]
WORK_BREAK = ["Get coffee", "Check TV news", "Return to work area"]
GUEST_PREPARATION = ["Clean living room", "Prepare coffee", "Check bedroom"]
RELAXATION_TIME = ["Turn off all lights", "Watch TV", "Go to bed"]

def generate_random_tasks(count=3):
    """Generate a random task sequence and let LLM decide room order"""
    
    # Available task sequences
    all_routines = [
        ("MORNING_ROUTINE", MORNING_ROUTINE),
        ("EVENING_ROUTINE", EVENING_ROUTINE), 
        ("CLEANING_ROUTINE", CLEANING_ROUTINE),
        ("WORK_BREAK", WORK_BREAK),
        ("GUEST_PREPARATION", GUEST_PREPARATION),
        ("RELAXATION_TIME", RELAXATION_TIME)
    ]
    
    # Pick a random routine
    routine_name, selected_routine = random.choice(all_routines)
    
    print(f"🎯 Selected routine: {routine_name}")
    print(f"📋 Tasks: {selected_routine}")
    
    return {
        "routine_name": routine_name,
        "tasks": selected_routine,
        "needs_llm_planning": True
    }

def print_task_plan(tasks):
    """Print the generated tasks in a nice format"""
    print("🎯 GENERATED NAVIGATION TASKS:")
    print("=" * 30)
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task}")
    
    print(f"\n📍 EXPECTED ROOM SEQUENCE:")
    expected_rooms = []
    for task in tasks:
        task_lower = task.lower()
        if "kitchen" in task_lower or "coffee" in task_lower or "refrigerator" in task_lower:
            expected_rooms.append("Kitchen")
        elif "living" in task_lower or "tv" in task_lower or "sofa" in task_lower:
            expected_rooms.append("LivingRoom") 
        elif "bedroom" in task_lower or "bed" in task_lower or "closet" in task_lower:
            expected_rooms.append("Bedroom")
        else:
            expected_rooms.append("Other")
    
    for i, room in enumerate(expected_rooms, 1):
        print(f"   {i}. {room}")
    
    return expected_rooms

if __name__ == "__main__":
    tasks = generate_random_tasks(3)
    expected_rooms = print_task_plan(tasks)
    
    print(f"\n🎮 READY FOR NAVIGATION!")
    print(f"✅ Tasks generated")
    print(f"✅ Room sequence planned") 
    print(f"✅ Ready for LLM planning and Blender execution")
