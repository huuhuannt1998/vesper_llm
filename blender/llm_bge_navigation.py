"""
VESPER BGE Navigation System - Fixed Version
Enhanced for local Ollama LLaVA integration
(Camera calibration disabled to preserve manual settings)
"""

import bge
import mathutils
import os
import sys
import json
import time
import re

# =============================
# BGE screenshot state
# =============================

# =============================
# Python path & .env bootstrap
# =============================
def setup_python_path():
    """Setup path to access LLM client"""
    try:
        vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"

        if vesper_root not in sys.path:
            sys.path.insert(0, vesper_root)
            print(f"✅ BGE: Added vesper_llm path: {vesper_root}")

        # Load environment variables
        env_path = os.path.join(vesper_root, "backend", "app", "llm", ".env")
        if os.path.exists(env_path):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                print(f"✅ BGE: Loaded .env from {env_path} (dotenv)")
            except ImportError:
                print("⚠️ BGE: dotenv not available, parsing .env manually")
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                print(f"✅ BGE: Manually loaded .env from {env_path}")
        else:
            print(f"⚠️ BGE: No .env file found at {env_path}")

        return True
    except Exception as e:
        print(f"❌ BGE: Path setup failed: {e}")
    return False

path_ok = setup_python_path()

# =============================
# LLM client import
# =============================
LLM_AVAILABLE = False
if path_ok:
    try:
        print(f"🔍 BGE: Current sys.path includes: {sys.path[:3]}...")
        from backend.app.llm.client import chat_completion, chat_completion_with_vision
        LLM_AVAILABLE = True
        print("✅ BGE: LLM client connected successfully")
    except ImportError as e:
        print(f"⚠️ BGE: LLM client not available - {e}")
        print(f"🔍 BGE: Python sys.path: {sys.path}")
        backend_path = os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm", "backend")
        print(f"🔍 BGE: Backend directory exists: {os.path.exists(backend_path)}")
        if os.path.exists(backend_path):
            print(f"🔍 BGE: Backend contents: {os.listdir(backend_path)}")
else:
    print("❌ BGE: Path setup failed, cannot import LLM client")

# =============================
# Screenshot helpers (non-blocking)
# =============================
def _init_shot_state():
    """Ensure global shot state exists."""
    if not hasattr(bge.logic, "_vesper_shot"):
        bge.logic._vesper_shot = {
            "pending": False,
            "path": None,
            "start_time": 0.0,
            "tries": 0,
        }

def _captures_dir():
    vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
    captures_dir = os.path.join(vesper_root, "blender", "captures")
    os.makedirs(captures_dir, exist_ok=True)
    return captures_dir

def _next_screenshot_path(captures_dir):
    existing_files = [f for f in os.listdir(captures_dir) if f.startswith("bge_") and f.endswith(".png")]
    if existing_files:
        nums = []
        for f in existing_files:
            try:
                nums.append(int(f.split("_")[1].split(".")[0]))
            except Exception:
                pass
        n = (max(nums) + 1) if nums else 1
    else:
        n = 1
    p = os.path.join(captures_dir, f"bge_{n:03d}.png")
    while os.path.exists(p):
        n += 1
        p = os.path.join(captures_dir, f"bge_{n:03d}.png")
    return p

def request_bird_eye_screenshot():
    """
    Kick off a screenshot of the next rendered frame from BirdEyeCamera.
    Non-blocking: returns immediately; result is polled via poll_screenshot_ready().
    """
    import bge.render

    _init_shot_state()
    scene = bge.logic.getCurrentScene()

    # Find BirdEyeCamera
    camera = scene.objects.get("BirdEyeCamera")
    if not camera:
        # Fallback: try to find any camera-like object
        print("⚠️ BGE: No BirdEyeCamera found. Searching for camera-like object...")
        for obj in scene.objects:
            if 'camera' in obj.name.lower() or 'cam' in obj.name.lower():
                camera = obj
                print(f"🔍 BGE: Using fallback camera-like object: {obj.name}")
                break
        if not camera:
            print("❌ BGE: No camera available to capture from.")
            return None

    # Ensure we capture from the right camera
    try:
        scene.active_camera = camera
        print(f"✅ BGE: Active camera set to {camera.name} for screenshot")
    except Exception as e:
        print(f"⚠️ BGE: Could not set active camera: {e}")

    capdir = _captures_dir()
    shot_path = _next_screenshot_path(capdir)
    print(f"📸 BGE: Requesting screenshot -> {shot_path}")

    # Ask the rasterizer to dump the next rendered frame to file
    bge.render.makeScreenshot(shot_path)

    st = bge.logic._vesper_shot
    st["pending"] = True
    st["path"] = shot_path
    st["start_time"] = time.time()
    st["tries"] += 1

    return shot_path

def poll_screenshot_ready(min_bytes: int = 1000, timeout_s: float = 5.0):
    """
    Check whether the requested screenshot is now on disk and looks valid.
    Returns:
      - None        -> not ready yet
      - "TIMEOUT"   -> timed out; caller may re-request
      - <path str>  -> valid file ready
    """
    _init_shot_state()
    st = bge.logic._vesper_shot
    if not st["pending"]:
        return None

    p = st["path"]
    if p and os.path.exists(p):
        try:
            size = os.path.getsize(p)
            if size >= min_bytes:
                st["pending"] = False
                print(f"✅ BGE: Screenshot ready: {os.path.basename(p)} ({size} bytes)")
                return p
        except Exception as e:
            print(f"⚠️ BGE: Stat failed on {p}: {e}")

    # timeout -> caller may re-request
    if time.time() - st["start_time"] > timeout_s:
        st["pending"] = False
        print("⏲️ BGE: Screenshot timeout; will re-request next tick")
        return "TIMEOUT"

    return None

# =============================
# LLM logic
# =============================
def get_navigation_sequence_with_vlm(screenshot_path, current_task):
    """Get movement sequence from VLM - MUST have a real screenshot"""
    if not LLM_AVAILABLE:
        raise Exception("❌ LLM not available - cannot proceed without vision capabilities")

    if not screenshot_path or not os.path.exists(screenshot_path):
        raise Exception(f"❌ No valid screenshot available at: {screenshot_path}")

    # Get current actor position for context
    import bge
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    current_pos = f"[{actor.worldPosition.x:.1f}, {actor.worldPosition.y:.1f}]" if actor else "[unknown]"

    print(f"🔍 BGE: Using vision analysis with screenshot: {os.path.basename(screenshot_path)}")
    print(f"📍 BGE: Actor current position: {current_pos}")

    system_prompt = "You are a spatial navigation expert analyzing a bird's eye view of a house. The pink dot is an actor that needs to navigate between rooms."

    user_prompt = f'''TASK: {current_task}
CURRENT ACTOR POSITION: {current_pos}

CRITICAL ROOM IDENTIFICATION GUIDE:
Looking at this bird's eye house layout:

🏠 HOUSE LAYOUT ANALYSIS:
- KITCHEN: Look for appliances, counters, typically has darker rectangular objects (stove, fridge, sink)
- BEDROOM: Look for beds (rectangular furniture), dressers, typically more enclosed/private spaces
- LIVING ROOM: Open central area, may have seating furniture, typically larger open space
- BATHROOMS: Small rooms with fixtures, usually compact
- HALLWAYS: Narrow corridors connecting rooms

📍 CURRENT POSITION:
Find the pink/colored dot - this is the actor. Analyze what room features surround it.

🎯 TARGET: {"BEDROOM (find beds, dressers, private sleeping area)" if "bedroom" in current_task.lower() else "KITCHEN (find appliances, counters, cooking area)" if "kitchen" in current_task.lower() else "LIVING ROOM (find open central area, seating)"}

🧭 MOVEMENT PLANNING:
- UP = +Y direction (towards top of image)
- DOWN = -Y direction (towards bottom of image)  
- LEFT = -X direction (towards left of image)
- RIGHT = +X direction (towards right of image)
- Each move = 0.3 units
- Plan 6-12 moves to reach target room
- Navigate through doorways (openings in walls)
- Avoid dark wall areas

ANALYZE THE CURRENT ROOM FEATURES CAREFULLY:
- What furniture/objects do you see around the pink dot?
- What room type does this indicate?
- Where do you see the target room features?
- What path connects them?
- End with "STAY" only when you've reached the target room

CRITICAL: Look at the house layout carefully. Plan a realistic path that:
1. Moves through doorways between rooms
2. Navigates around walls (dark areas)
3. Actually reaches a different area of the house
4. Takes enough steps to traverse multiple rooms

Respond ONLY in this JSON format (keep reasoning brief, single line):
{{
  "current_location": "Currently in [specific room description]",
  "target_room": "Need to reach [target room]", 
  "movement_sequence": ["RIGHT", "RIGHT", "UP", "UP", "UP", "LEFT", "LEFT", "UP", "STAY"],
  "reasoning": "Brief single-line path description"
}}'''

    response = chat_completion_with_vision(
        f"{system_prompt}\n\n{user_prompt}",
        image_path=screenshot_path
    )
    print("✅ BGE: Vision-based navigation analysis completed")
    print(f"🔍 BGE: VLM Response → {response[:300]}...")  # Show first 300 chars

    # Parse JSON payload
    start = response.find('{')
    end = response.rfind('}') + 1
    if start >= 0 and end > start:
        json_str = response[start:end]
        result = json.loads(json_str)

        if "movement_sequence" in result and isinstance(result["movement_sequence"], list):
            sequence = [m for m in result["movement_sequence"] if m in ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]]
            if sequence:
                print(f"🧠 BGE: VLM Sequence → {sequence}")
                print(f"� BGE: Current Location → {result.get('current_location', 'Unknown')}")
                print(f"🎯 BGE: Target Room → {result.get('target_room', 'Unknown')}")
                print(f"�💭 BGE: Path Plan → {result.get('reasoning', 'No reasoning provided')}")
                return {"movement_sequence": sequence, "reasoning": result.get('reasoning', '')}

    raise Exception(f"❌ Vision analysis failed - invalid response format: {response[:200]}...")

def get_navigation_decision_with_vlm(screenshot_path, current_task):
    """Simple step-wise VLM navigation with clear prompts"""
    if not LLM_AVAILABLE:
        # Simple fallback pattern when LLM is unavailable
        print("🔄 BGE: Using fallback pattern navigation (LLM not available)")
        task_lower = current_task.lower()
        step_count = getattr(bge.logic, 'fallback_step_count', 0)
        bge.logic.fallback_step_count = step_count + 1

        if "bedroom" in task_lower:
            directions = ["UP", "UP", "RIGHT", "RIGHT", "UP", "LEFT", "STAY"]
        elif "kitchen" in task_lower:
            directions = ["LEFT", "LEFT", "UP", "UP", "LEFT", "DOWN", "STAY"]
        elif "living" in task_lower or "rest" in task_lower:
            directions = ["RIGHT", "RIGHT", "DOWN", "DOWN", "RIGHT", "UP", "STAY"]
        else:
            directions = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]

        direction = directions[step_count % len(directions)]
        return {"next_direction": direction, "reasoning": f"Fallback pattern step {step_count}: {direction}"}

    # Normal (vision) path:
    system_prompt = "You are a navigation AI. Analyze the bird's eye view image and respond only in JSON format."
    user_prompt = f'''Task: {current_task}

Look at this bird's eye view image. The colored dot/diamond is the actor you control.

Choose the best direction to move toward the target:
- Dark areas = walls (avoid)
- Light areas = open space (safe)
- Analyze what room you're currently in
- Determine where the target room is located

Room identification:
- Kitchen: Look for counters, appliances, sinks
- Bedroom: Look for beds, dressers, private spaces
- Living room: Look for sofas, TV areas, open spaces

Choose UP, DOWN, LEFT, RIGHT, or STAY

Respond ONLY in this JSON format:
{{
  "next_direction": "UP",
  "reasoning": "Current room analysis and movement explanation"
}}'''

    if not screenshot_path or not os.path.exists(screenshot_path):
        print("❌ BGE: No screenshot available")
        return {"next_direction": "STAY", "reasoning": "No screenshot available"}

    try:
        response = chat_completion_with_vision(
            f"{system_prompt}\n\n{user_prompt}",
            image_path=screenshot_path
        )
        print("🔍 BGE: Using vision-based navigation")

        # Parse JSON
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            result = json.loads(json_str)

            direction = result.get("next_direction", "STAY")
            reasoning = result.get("reasoning", "No reasoning provided")

            print(f"🧠 BGE: LLM Decision → {direction}")
            print(f"💭 BGE: {reasoning}")

            return {"next_direction": direction, "reasoning": reasoning}
        else:
            print("❌ BGE: Could not parse VLM response")
            return {"next_direction": "STAY", "reasoning": "Parse error"}

    except Exception as e:
        print(f"❌ BGE: VLM call failed: {e}")
        return {"next_direction": "STAY", "reasoning": f"VLM error: {e}"}

# =============================
# Movement
# =============================
def move_actor(actor, direction, step_size=0.3):
    """Move actor in BGE coordinate system - corrected for bird's eye camera orientation"""
    if direction == "STAY":
        print("🛑 BGE: Actor staying - task complete or waiting for VLM!")
        return True

    current_pos = actor.worldPosition.copy()
    print(f"🔍 BGE: Before move - Actor at [{current_pos.x:.2f}, {current_pos.y:.2f}]")

    # CORRECTED coordinate mapping based on actual XYZ system:
    # UP = +Y, DOWN = -Y, LEFT = -X, RIGHT = +X
    if direction == "UP":
        actor.worldPosition.y += step_size
        print(f"🧭 BGE: UP direction = +Y movement")
    elif direction == "DOWN":
        actor.worldPosition.y -= step_size
        print(f"🧭 BGE: DOWN direction = -Y movement")
    elif direction == "LEFT":
        actor.worldPosition.x -= step_size
        print(f"🧭 BGE: LEFT direction = -X movement")
    elif direction == "RIGHT":
        actor.worldPosition.x += step_size
        print(f"🧭 BGE: RIGHT direction = +X movement")

    new_pos = actor.worldPosition
    print(f"🎮 BGE: Actor moved {direction} to [{new_pos.x:.2f}, {new_pos.y:.2f}]")
    print(f"📏 BGE: Movement delta: X={new_pos.x-current_pos.x:.2f}, Y={new_pos.y-current_pos.y:.2f}")
    return True

# =============================
# Main tick
# =============================
def main():
    """Main BGE navigation function with sequence-based movement (non-blocking screenshots, manual camera settings preserved)"""
    controller = bge.logic.getCurrentController()
    scene = bge.logic.getCurrentScene()

    # Find actor
    actor = scene.objects.get("Actor")
    if not actor:
        print("❌ BGE: No 'Actor' object found!")
        return

    # Init state once
    if not hasattr(bge.logic, "vesper_nav_init"):
        bge.logic.vesper_nav_init = True
        bge.logic.vesper_current_task_index = 0
        bge.logic.vesper_tasks = ["Go to bedroom", "Cook in kitchen", "Rest in bedroom"]
        bge.logic.vesper_movement_queue = []  # sequence of moves
        bge.logic.vesper_sequence_step = 0
        bge.logic.last_screenshot_path = None

        print("🧠 BGE: VESPER Navigation initialized!")
        print(f"📋 BGE: Tasks: {bge.logic.vesper_tasks}")
        print(f"📍 BGE: LLM Available: {LLM_AVAILABLE}")
        print("🔧 BGE: Camera calibration DISABLED - your manual settings preserved!")

        # Kick off initial screenshot (non-blocking)
        print("📸 BGE: Requesting initial screenshot...")
        request_bird_eye_screenshot()
        return  # yield this tick so a frame can render

    # If a screenshot is pending, poll it
    shot_status = poll_screenshot_ready()
    if shot_status is None:
        # Not ready yet; let the engine render another frame
        pass
    elif shot_status == "TIMEOUT":
        # Re-request next frame
        request_bird_eye_screenshot()
        return
    else:
        # Ready path
        bge.logic.last_screenshot_path = shot_status

    # Stop if all tasks done
    if bge.logic.vesper_current_task_index >= len(bge.logic.vesper_tasks):
        print("🎉 BGE: ALL TASKS COMPLETED!")
        return

    current_task = bge.logic.vesper_tasks[bge.logic.vesper_current_task_index]

    # If we need a new movement plan
    if not bge.logic.vesper_movement_queue:
        # Ensure we have a screenshot (request one if we don't)
        if not bge.logic._vesper_shot["pending"] and not bge.logic.last_screenshot_path:
            print(f"\n📍 BGE: Planning sequence for task: {current_task}")
            print("📸 BGE: Requesting fresh screenshot for analysis...")
            request_bird_eye_screenshot()
            return  # allow frame to render

        # If a recent screenshot is ready, analyze it
        if bge.logic.last_screenshot_path:
            try:
                sequence_result = get_navigation_sequence_with_vlm(bge.logic.last_screenshot_path, current_task)
                if "movement_sequence" in sequence_result:
                    bge.logic.vesper_movement_queue = sequence_result["movement_sequence"].copy()
                    bge.logic.vesper_sequence_step = getattr(bge.logic, 'vesper_sequence_step', 0)
                    print(f"🎯 BGE: Loaded sequence: {bge.logic.vesper_movement_queue}")
                    print(f"💭 BGE: {sequence_result.get('reasoning', 'No reasoning provided')}")
                else:
                    raise Exception("❌ VLM did not return movement_sequence - critical error")
            finally:
                # Consume this screenshot; next cycle will take a new one
                bge.logic.last_screenshot_path = None

    # Execute next step if we have a plan
    if bge.logic.vesper_movement_queue:
        next_move = bge.logic.vesper_movement_queue.pop(0)
        bge.logic.vesper_sequence_step += 1

        print(f"🎮 BGE: Step {bge.logic.vesper_sequence_step}: {next_move}")
        print(f"📍 BGE: Remaining in sequence: {bge.logic.vesper_movement_queue}")

        old_position = [actor.worldPosition.x, actor.worldPosition.y]
        move_actor(actor, next_move)
        new_position = [actor.worldPosition.x, actor.worldPosition.y]

        # Detect if stuck
        moved_distance = ((new_position[0] - old_position[0])**2 + (new_position[1] - old_position[1])**2)**0.5
        if moved_distance < 0.1 and next_move != "STAY":
            print("⚠️ BGE: Actor appears stuck, will re-analyze with new screenshot")
            bge.logic.vesper_movement_queue = []  # trigger replanning
            # Request new screenshot immediately
            if not bge.logic._vesper_shot["pending"]:
                request_bird_eye_screenshot()
            return

        # If the short sequence is finished, request a new screenshot for the next cycle
        if not bge.logic.vesper_movement_queue:
            print("📸 BGE: Short sequence completed - requesting NEW screenshot for re-analysis")
            if next_move == "STAY":
                print(f"✅ BGE: Task '{current_task}' completed (STAY command)!")
                bge.logic.vesper_current_task_index += 1
                bge.logic.vesper_sequence_step = 0
            else:
                print(f"🔄 BGE: Continuing task '{current_task}' with new analysis cycle")

            # Request the next screenshot right away
            if not bge.logic._vesper_shot["pending"]:
                request_bird_eye_screenshot()
            return

if __name__ == "__main__":
    main()