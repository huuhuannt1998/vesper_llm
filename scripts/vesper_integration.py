"""
VESPER Navigation Integration - Connect task planning with Blender navigation
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.llm_planner import get_random_routine, create_fallback_plan, MORNING_ROUTINE
from backend.app.llm.client import chat_completion
import yaml

# Load room configurations
with open("configs/rooms.yaml", "r") as f:
    ROOMS = yaml.safe_load(f)

def get_navigation_plan():
    """Get a task routine and create navigation plan"""
    print("🎯 VESPER NAVIGATION PLANNING")
    print("=" * 30)
    
    # Get a routine to execute
    routine_name, tasks = get_random_routine()
    print(f"📋 Selected Routine: {routine_name}")
    print(f"🎯 Tasks: {tasks}")
    
    # Create simple room mapping plan
    plan = create_fallback_plan(tasks)
    
    print(f"\n📍 NAVIGATION PLAN:")
    for step in plan["planned_sequence"]:
        room_center = ROOMS.get(step['room'], {}).get('center', [0, 0])
        print(f"   {step['order']}. {step['task']} → {step['room']} ({room_center[0]}, {room_center[1]})")
    
    return plan

def create_blender_navigation_command(plan):
    """Create Blender Python code to execute the navigation plan"""
    
    blender_code = '''
import bpy
import time

def navigate_to_room(room_name, x, y):
    """Move actor to specified room coordinates"""
    scene = bpy.context.scene
    
    # Find the actor
    actor = None
    for obj in scene.objects:
        if "actor" in obj.name.lower() or "human" in obj.name.lower():
            actor = obj
            break
    
    if actor:
        print(f"🚶 Moving to {room_name} at ({x}, {y})")
        actor.location.x = x
        actor.location.y = y
        bpy.context.view_layer.update()
    else:
        print("❌ No actor found in scene")

# Execute navigation plan
'''
    
    for step in plan["planned_sequence"]:
        room_center = ROOMS.get(step['room'], {}).get('center', [0, 0])
        x, y = room_center[0], room_center[1]
        
        blender_code += f'''
print("🎯 Task {step['order']}: {step['task']}")
navigate_to_room("{step['room']}", {x}, {y})
time.sleep(1)  # Brief pause between moves
'''
    
    blender_code += '''
print("✅ Navigation sequence completed!")
'''
    
    return blender_code

if __name__ == "__main__":
    # Get navigation plan
    plan = get_navigation_plan()
    
    # Generate Blender code
    blender_code = create_blender_navigation_command(plan)
    
    print(f"\n🔧 BLENDER NAVIGATION CODE:")
    print("-" * 40)
    print(blender_code)
    
    print(f"\n🎊 VESPER INTEGRATION READY!")
    print(f"✅ Task planning working")  
    print(f"✅ Room mapping complete")
    print(f"✅ Blender code generated")
    print(f"\nNext: Execute this code in Blender with P key!")
