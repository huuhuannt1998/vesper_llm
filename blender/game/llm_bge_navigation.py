# VESPER LLM Navigation - BGE Implementation with Path Fixing
# This script runs INSIDE the Game Engine and controls the actor directly

import bge
import sys
import os
import time
import json
import base64
import tempfile
import math

# Fix Python path for BGE - multiple fallback strategies
def setup_python_path():
    """Setup Python path to find our modules"""
    try:
        # Strategy 1: Get the blend file directory
        blend_file_path = bge.logic.expandPath("//")
        if blend_file_path and os.path.exists(blend_file_path):
            # Go up one level to vesper_llm root
            vesper_root = os.path.dirname(blend_file_path)
            if vesper_root not in sys.path:
                sys.path.insert(0, vesper_root)
                print(f"✅ BGE: Added path from blend file: {vesper_root}")
                return vesper_root
    except:
        pass
    
    # Strategy 2: Use hardcoded path as fallback
    fallback_path = r"c:\Users\hbui11\Desktop\vesper_llm"
    if os.path.exists(fallback_path) and fallback_path not in sys.path:
        sys.path.insert(0, fallback_path)
        print(f"✅ BGE: Added fallback path: {fallback_path}")
        return fallback_path
    
    # Strategy 3: Try to find vesper_llm directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while current_dir and current_dir != os.path.dirname(current_dir):
        if os.path.basename(current_dir) == 'vesper_llm':
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
                print(f"✅ BGE: Found vesper_llm at: {current_dir}")
                return current_dir
        current_dir = os.path.dirname(current_dir)
    
    print("⚠️ BGE: Could not setup Python path")
    return None

# Setup path before importing
vesper_root = setup_python_path()

# Try to import LLM client
LLM_AVAILABLE = False
try:
    from backend.app.llm.client import chat_completion
    LLM_AVAILABLE = True
    print("✅ BGE: LLM client connected successfully")
except ImportError as e:
    print(f"⚠️ BGE: LLM client not available - {e}")
    print(f"⚠️ BGE: Python path: {sys.path}")

def capture_bge_screenshot():
    """Capture screenshot using BGE render system"""
    try:
        # Get BGE render system
        import bgl
        
        # Get viewport dimensions
        viewport = bgl.Buffer(bgl.GL_INT, 4)
        bgl.glGetIntegerv(bgl.GL_VIEWPORT, viewport)
        width, height = viewport[2], viewport[3]
        
        # Capture RGB data
        buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 3)
        bgl.glReadPixels(0, 0, width, height, bgl.GL_RGB, bgl.GL_UNSIGNED_BYTE, buffer)
        
        # Convert to base64
        image_data = bytes(buffer)
        screenshot_base64 = base64.b64encode(image_data).decode('utf-8')
        
        print(f"📸 BGE: Screenshot captured ({width}x{height})")
        return screenshot_base64
        
    except Exception as e:
        print(f"❌ BGE: Screenshot failed: {e}")
        return None

def get_llm_navigation_command(current_task, actor_position, screenshot_base64=None):
    """Get navigation command from LLM"""
    if not LLM_AVAILABLE:
        return {"next_direction": "UP", "reasoning": "LLM unavailable - using fallback"}
    
    try:
        system_prompt = """You are controlling an actor in a house. Look at the screenshot and help navigate.

MOVEMENT COMMANDS:
- "UP" = move forward (+Y direction)
- "DOWN" = move backward (-Y direction) 
- "LEFT" = move left (-X direction)
- "RIGHT" = move right (+X direction)
- "STAY" = stop (task complete)

RESPONSE FORMAT (JSON only):
{
  "next_direction": "UP|DOWN|LEFT|RIGHT|STAY",
  "reasoning": "why this direction helps complete the task",
  "task_complete": true/false
}"""

        user_prompt = f"""Current Task: {current_task}
Actor Position: {actor_position}

Look at the screenshot and decide the next movement to complete this task."""

        # Get LLM response with vision
        response = chat_completion(system_prompt, user_prompt, max_tokens=300, image_base64=screenshot_base64)
        
        # Parse JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                print(f"🧠 BGE: LLM Decision → {result.get('next_direction', 'STAY')}")
                return result
            else:
                return {"next_direction": "UP", "reasoning": "JSON parse failed"}
        except json.JSONDecodeError:
            return {"next_direction": "UP", "reasoning": "JSON decode failed"}
            
    except Exception as e:
        print(f"❌ BGE: LLM error: {e}")
        return {"next_direction": "UP", "reasoning": f"LLM error: {e}"}

def get_fallback_direction(task, step):
    """Simple fallback navigation when LLM is unavailable"""
    task_lower = task.lower()
    if "bedroom" in task_lower:
        return ["UP", "RIGHT", "UP", "LEFT"][step % 4]
    elif "kitchen" in task_lower:
        return ["LEFT", "UP", "LEFT", "DOWN"][step % 4]
    elif "living" in task_lower:
        return ["RIGHT", "DOWN", "RIGHT", "UP"][step % 4]
    else:
        return ["UP", "DOWN", "LEFT", "RIGHT"][step % 4]

def move_actor_bge(actor, direction, step_size=0.3):
    """Move actor in BGE coordinate system"""
    if direction == "UP":
        actor.worldPosition.y += step_size
    elif direction == "DOWN":
        actor.worldPosition.y -= step_size
    elif direction == "LEFT":
        actor.worldPosition.x -= step_size
    elif direction == "RIGHT":
        actor.worldPosition.x += step_size
    elif direction == "STAY":
        print("🛑 BGE: Actor staying - task complete!")
        return True
    
    print(f"🎮 BGE: Actor moved {direction} to [{actor.worldPosition.x:.2f}, {actor.worldPosition.y:.2f}]")
    return False

def main():
    """Main BGE navigation function"""
    controller = bge.logic.getCurrentController()
    owner = controller.owner
    scene = bge.logic.getCurrentScene()
    
    # Find actor
    actor = scene.objects.get("Actor") or owner
    if not actor:
        print("❌ BGE: No Actor found!")
        return
    
    # Initialize navigation state
    if not hasattr(bge.logic, "vesper_nav_state"):
        tasks = ["Go to bedroom", "Go to kitchen", "Go to living room"]  # Default tasks
        bge.logic.vesper_nav_state = {
            "tasks": tasks,
            "current_task_index": 0,
            "step_count": 0,
            "max_steps": 15,
            "last_update": time.time(),
            "update_interval": 2.0,  # LLM decision every 2 seconds
            "navigation_active": True
        }
        print("🧠 BGE: VESPER Navigation initialized!")
        print(f"📋 BGE: Tasks: {tasks}")
        print(f"📍 BGE: LLM Available: {LLM_AVAILABLE}")
    
    state = bge.logic.vesper_nav_state
    
    # Check if navigation is complete
    if not state["navigation_active"] or state["current_task_index"] >= len(state["tasks"]):
        return
    
    # Time-based updates (not every frame)
    current_time = time.time()
    if current_time - state["last_update"] < state["update_interval"]:
        return
    
    state["last_update"] = current_time
    state["step_count"] += 1
    
    # Get current task
    current_task = state["tasks"][state["current_task_index"]]
    
    print(f"\n📍 BGE Step {state['step_count']} - Task: {current_task}")
    
    # 1. Capture screenshot (if LLM available)
    screenshot_base64 = None
    if LLM_AVAILABLE:
        screenshot_base64 = capture_bge_screenshot()
    
    # 2. Get navigation decision
    actor_pos = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
    
    if LLM_AVAILABLE:
        llm_result = get_llm_navigation_command(current_task, actor_pos, screenshot_base64)
        direction = llm_result.get("next_direction", "STAY")
        reasoning = llm_result.get("reasoning", "No reasoning")
        task_complete = llm_result.get("task_complete", False)
    else:
        # Use simple fallback navigation
        direction = get_fallback_direction(current_task, state["step_count"])
        reasoning = "Using fallback navigation (no LLM)"
        task_complete = False
    
    print(f"💭 BGE: Reasoning: {reasoning}")
    
    # 3. Move actor
    task_finished = move_actor_bge(actor, direction)
    
    # 4. Check if task is complete
    if task_finished or task_complete or direction == "STAY" or state["step_count"] >= state["max_steps"]:
        print(f"✅ BGE: Task '{current_task}' completed!")
        state["current_task_index"] += 1
        state["step_count"] = 0
        
        if state["current_task_index"] >= len(state["tasks"]):
            print("🎉 BGE: ALL TASKS COMPLETED!")
            state["navigation_active"] = False

# Main entry point for BGE
if __name__ == "__main__":
    main()
else:
    # Called from BGE Logic Brick
    main()
