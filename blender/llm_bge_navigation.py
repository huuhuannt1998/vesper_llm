import bge
import mathutils
import os
import sys
import json
import time

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
            print(f"✅ BGE: Path setup complete")

        # Load environment variables
        env_path = os.path.join(vesper_root, "backend", "app", "llm", ".env")
        if os.path.exists(env_path):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                print(f"✅ BGE: Environment loaded")
            except ImportError:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()

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
        from backend.app.llm.client import chat_completion, chat_completion_with_vision
        LLM_AVAILABLE = True
        print("🔗 LLM: Connected")
    except ImportError as e:
        print(f"❌ BGE: LLM not available - {e}")
else:
    print("❌ BGE: Setup failed")

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
                break
        if not camera:
            print("❌ BGE: No camera available")
            return None

    # Ensure we capture from the right camera
    try:
        scene.active_camera = camera
    except Exception as e:
        print(f"⚠️ BGE: Camera error: {e}")

    capdir = _captures_dir()
    shot_path = _next_screenshot_path(capdir)

    # Ask the rasterizer to dump the next rendered frame to file
    bge.render.makeScreenshot(shot_path)

    st = bge.logic._vesper_shot
    st["pending"] = True
    st["path"] = shot_path
    st["start_time"] = time.time()
    st["tries"] += 1

    return shot_path

def poll_screenshot_ready(min_bytes: int = 1000, timeout_s: float = 5.0):
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
                filename = os.path.basename(p)
                print(f"📸 Screenshot ready: {filename}")
                return p
        except Exception as e:
            print(f"⚠️ BGE: Screenshot error: {e}")

    # timeout -> caller may re-request
    if time.time() - st["start_time"] > timeout_s:
        st["pending"] = False
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

    # Get current actor position and movement history for context
    import bge
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    current_pos = f"[{actor.worldPosition.x:.1f}, {actor.worldPosition.y:.1f}]" if actor else "[unknown]"
    
    # Track position history to detect looping and drift
    if not hasattr(bge.logic, 'position_history'):
        bge.logic.position_history = []
    if not hasattr(bge.logic, 'analysis_count'):
        bge.logic.analysis_count = 0
    
    bge.logic.analysis_count += 1
    
    if actor:
        pos = (round(actor.worldPosition.x, 1), round(actor.worldPosition.y, 1))
        bge.logic.position_history.append(pos)
        # Keep only last 8 positions for loop detection
        if len(bge.logic.position_history) > 8:
            bge.logic.position_history.pop(0)
            
        # Detect looping behavior
        if len(bge.logic.position_history) >= 6:
            recent_positions = bge.logic.position_history[-6:]
            unique_positions = len(set(recent_positions))
            if unique_positions <= 3:
                print(f"🔄 BGE: LOOP DETECTED - Only {unique_positions} unique positions in last 6 moves")
                print(f"📍 BGE: Recent path: {recent_positions}")
            
        # Check if actor is drifting toward extreme coordinates
        if abs(actor.worldPosition.x) > 10 or abs(actor.worldPosition.y) > 10:
            print(f"⚠️ BGE: POSITION ALERT - Actor at extreme coordinates: {current_pos}")

    # Show which image we're analyzing
    image_filename = os.path.basename(screenshot_path)
    print(f"🔍 BGE: Analyzing image: {image_filename} - Actor at {current_pos}")

    # Add context about analysis frequency for VLM
    analysis_context = f"ANALYSIS #{bge.logic.analysis_count}"
    if bge.logic.analysis_count > 10:
        analysis_context += " - MANY ATTEMPTS! Focus on task completion."

    system_prompt = "You are a navigation AI with computer vision. Analyze this bird's eye view image and detect walls, obstacles, and safe pathways visually. CRITICAL: Keep the actor within the visible house structure and focus on completing tasks efficiently. The house has LIVING ROOM (bottom), KITCHEN (middle), and BEDROOM (top) areas."

    # Add enhanced position context with spatial awareness
    position_context = ""
    if hasattr(bge.logic, 'position_history') and len(bge.logic.position_history) > 1:
        recent_positions = bge.logic.position_history[-3:]  # last 3 positions
        position_context = f"\nRECENT POSITIONS: {recent_positions}"
        
        # Add spatial awareness based on coordinates
        x, y = actor.worldPosition.x, actor.worldPosition.y
        spatial_hints = ""
        
        if x < -4.0:
            spatial_hints += " (Near LEFT edge of house - kitchen/bedroom area)"
        elif x > 0:
            spatial_hints += " (Near RIGHT edge of house - living room area)"
        else:
            spatial_hints += " (Center area of house)"
            
        if y > 4.0:
            spatial_hints += " (UPPER level - bedroom area)"
        elif y > 1.0:
            spatial_hints += " (Middle level - kitchen area)"  
        else:
            spatial_hints += " (Lower level - living room area)"
            
        position_context += spatial_hints
        
        # Check for drift detection
        if abs(x) > 5.0 or abs(y) > 5.0:
            position_context += " ⚠️ APPROACHING HOUSE BOUNDARIES!"

    # Enhanced room identification based on task
    if "bedroom" in current_task.lower():
        target_features = "BED (rectangular furniture), DRESSER/WARDROBE (tall furniture), PILLOWS, or bedroom-specific items"
        completion_criteria = "You must see a BED or bedroom furniture near the pink dot"
    elif "kitchen" in current_task.lower():
        target_features = "STOVE/OVEN (cooking appliances), REFRIGERATOR (large box), SINK, COUNTERTOPS, or kitchen cabinets"
        completion_criteria = "You must see kitchen appliances (stove, oven, fridge) or countertops near the pink dot"
    else:
        target_features = "SOFA/COUCH (seating furniture), COFFEE TABLE, TV, or living room furniture"
        completion_criteria = "You must see living room furniture near the pink dot"

    user_prompt = f'''TASK: {current_task}
CURRENT POSITION: {current_pos}{position_context}
{analysis_context}

🔍 ROOM IDENTIFICATION PRIORITY:
Your PRIMARY job is to accurately identify which room the pink dot is currently in by analyzing the furniture around it.

ROOM FEATURES TO LOOK FOR:
BEDROOM: {target_features if "bedroom" in current_task.lower() else "BED, dresser, wardrobe, pillows"}
KITCHEN: {target_features if "kitchen" in current_task.lower() else "Stove/oven, refrigerator, sink, countertops, cabinets"}  
LIVING ROOM: {target_features if "living room" in current_task.lower() else "Sofa/couch, coffee table, TV, seating area"}

TASK COMPLETION RULE:
ONLY use "STAY" if: {completion_criteria}
If the pink dot is NOT in the target room, continue navigating - do NOT use "STAY"

VISUAL ANALYSIS STEPS:
1. LOCATE PINK DOT - Find the actor's current position
2. ANALYZE FURNITURE AROUND PINK DOT - What furniture is immediately visible near the pink dot?
3. IDENTIFY CURRENT ROOM - Based on furniture, which room contains the pink dot?
4. CHECK IF TASK IS COMPLETE - Is the pink dot in the target room with correct furniture?
5. PLAN MOVEMENT - If not in target room, navigate toward target area

SAFETY BOUNDARIES:
- SAFE AREAS: Rooms with floors, furniture, walls, textures (stay here!)
- UNSAFE AREAS: Dark/black spaces, empty voids outside rooms (NEVER go here!)
- If pink dot approaches dark edges → move back toward center/furniture

MOVEMENT RULES:
- MAXIMUM 1-2 moves per sequence (be efficient!)
- Only move through areas with visible floors and furniture
- Stop immediately when you reach the correct room with target furniture
- If you've been analyzing many times, prioritize finding and completing the task quickly
- If image is unclear, use STAY and request new analysis rather than guessing directions
- NEVER suggest moves that could lead outside the visible house structure

CRITICAL SAFETY:
- If you cannot clearly identify furniture or room boundaries, use "STAY" 
- If the image is blurry/unclear, respond with current_room: "UNKNOWN" and movement_sequence: ["STAY"]
- Focus on visible furniture landmarks to determine safe movement directions

JSON Response Format:
{{
  "current_room": "Based on furniture around pink dot: [BEDROOM/KITCHEN/LIVING_ROOM/UNKNOWN]",
  "furniture_visible": "List the specific furniture items you can see near the pink dot",
  "task_complete": true/false,
  "movement_sequence": ["UP", "RIGHT"] or ["STAY"],
  "reasoning": "ROOM ANALYSIS: [describe furniture seen]. TASK STATUS: [complete/continue]. PATH: [next moves]"
}}

CRITICAL: movement_sequence must contain ONLY these exact words: "UP", "DOWN", "LEFT", "RIGHT", "STAY"'''

    response = chat_completion_with_vision(
        f"{system_prompt}\n\n{user_prompt}",
        image_path=screenshot_path
    )
    print("✅ BGE: Vision-based navigation analysis completed")
    print(f"🔍 BGE: VLM Response → {response[:300]}...")  # Show first 300 chars
    print(f"📏 BGE: Full response length: {len(response)} characters")

    # Parse JSON payload - handle markdown code blocks and formatting
    import re
    
    # First try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        print(f"📦 BGE: Extracted from markdown: {len(json_str)} chars")
    else:
        # Fallback: look for JSON object boundaries
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            print(f"📦 BGE: Extracted from boundaries: {len(json_str)} chars")
        else:
            json_str = None
            print("❌ BGE: No JSON boundaries found")
    
    if json_str:
        try:
            # Clean up any control characters or extra whitespace
            json_str = re.sub(r'[\x00-\x1f\x7f]', '', json_str)  # Remove control chars
            print(f"🧹 BGE: Cleaned JSON preview: {json_str[:150]}...")
            
            result = json.loads(json_str)
            print(f"✅ BGE: JSON parsed successfully")
            
            # Check if task is complete based on room analysis
            task_complete = result.get("task_complete", False)
            current_room = result.get("current_room", "UNKNOWN")
            furniture_visible = result.get("furniture_visible", "None specified")
            
            print(f"🏠 BGE: Current room identified: {current_room}")
            print(f"🪑 BGE: Furniture visible: {furniture_visible}")
            print(f"✅ BGE: Task complete: {task_complete}")

            if "movement_sequence" in result and isinstance(result["movement_sequence"], list):
                # Extract movement directions from potentially descriptive text
                raw_sequence = result["movement_sequence"]
                sequence = []
                
                for move in raw_sequence:
                    # Handle both plain directions and descriptive formats
                    if isinstance(move, str):
                        move_upper = move.upper()
                        # Extract all direction keywords from the text
                        directions_found = []
                        if "UP" in move_upper:
                            directions_found.append("UP")
                        if "DOWN" in move_upper:
                            directions_found.append("DOWN")
                        if "LEFT" in move_upper:
                            directions_found.append("LEFT")
                        if "RIGHT" in move_upper:
                            directions_found.append("RIGHT")
                        if "STAY" in move_upper:
                            directions_found.append("STAY")
                        
                        # If multiple directions found in one string, add them all
                        if directions_found:
                            sequence.extend(directions_found)
                        # If it's already a valid direction, keep it
                        elif move_upper in ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]:
                            sequence.append(move_upper)
                
                print(f"🔄 BGE: Raw sequence: {raw_sequence}")
                print(f"🎯 BGE: Extracted sequence: {sequence}")
                
                if sequence:
                    print(f"🧠 BGE: Sequence → {sequence}")
                    print(f"💭 BGE: {result.get('reasoning', 'No reasoning')}")
                    return {
                        "movement_sequence": sequence, 
                        "reasoning": result.get('reasoning', ''),
                        "task_complete": task_complete,
                        "current_room": current_room,
                        "furniture_visible": furniture_visible
                    }
                else:
                    print(f"❌ BGE: No valid movements extracted from: {raw_sequence}")
                    # If no valid movements but task is complete, return STAY
                    if task_complete:
                        return {
                            "movement_sequence": ["STAY"], 
                            "reasoning": result.get('reasoning', ''),
                            "task_complete": task_complete,
                            "current_room": current_room,
                            "furniture_visible": furniture_visible
                        }
            else:
                print(f"❌ BGE: Missing or invalid movement_sequence in result: {list(result.keys())}")
                
        except json.JSONDecodeError as e:
            print(f"⚠️ BGE: JSON parsing error: {e}")
            print(f"📝 BGE: Problematic JSON: {json_str}")
    else:
        print("❌ BGE: No JSON string extracted from response")

    # Show full response for debugging
    print(f"🔍 BGE: FULL VLM RESPONSE DEBUG:")
    print(f"'{response}'")
    
    raise Exception(f"❌ Vision analysis failed - see debug output above")

# =============================
# Movement
# =============================
def move_actor(actor, direction, step_size=0.3):
    """Move actor in BGE coordinate system with safety boundaries"""
    if direction == "STAY":
        print("🛑 BGE: Actor staying - task complete!")
        return True

    current_pos = actor.worldPosition.copy()
    print(f"🔍 BGE: Before move - Actor at [{current_pos.x:.2f}, {current_pos.y:.2f}]")
    
    # Calculate proposed new position
    proposed_pos = current_pos.copy()
    if direction == "UP":
        proposed_pos.y += step_size
    elif direction == "DOWN":
        proposed_pos.y -= step_size
    elif direction == "LEFT":
        proposed_pos.x -= step_size
    elif direction == "RIGHT":
        proposed_pos.x += step_size
    
    # CRITICAL: House boundary enforcement to prevent actor from leaving
    # Based on log analysis, safe house boundaries appear to be approximately:
    HOUSE_BOUNDS = {
        'x_min': -6.0,   # Left boundary
        'x_max': 2.0,    # Right boundary  
        'y_min': -1.0,   # Bottom boundary
        'y_max': 6.0     # Top boundary
    }
    
    # Check if proposed move would leave house boundaries
    if (proposed_pos.x < HOUSE_BOUNDS['x_min'] or proposed_pos.x > HOUSE_BOUNDS['x_max'] or
        proposed_pos.y < HOUSE_BOUNDS['y_min'] or proposed_pos.y > HOUSE_BOUNDS['y_max']):
        
        print(f"🚨 BGE: BOUNDARY VIOLATION PREVENTED!")
        print(f"   Proposed position: [{proposed_pos.x:.2f}, {proposed_pos.y:.2f}]")
        print(f"   House bounds: X({HOUSE_BOUNDS['x_min']} to {HOUSE_BOUNDS['x_max']}), Y({HOUSE_BOUNDS['y_min']} to {HOUSE_BOUNDS['y_max']})")
        print(f"   🛑 Movement {direction} BLOCKED - staying in current position")
        return False  # Movement blocked
    
    # Apply the safe movement
    actor.worldPosition = proposed_pos
    new_pos = actor.worldPosition
    print(f"🎮 Moved {direction} → [{new_pos.x:.2f}, {new_pos.y:.2f}]")
    
    # Additional safety check after movement
    if (abs(new_pos.x) > 10 or abs(new_pos.y) > 10):
        print(f"🚨 BGE: EMERGENCY: Actor at extreme coordinates!")
        print(f"   Resetting to safe position...")
        # Reset to safe center position
        actor.worldPosition.x = -2.0
        actor.worldPosition.y = -0.5
        print(f"   🔧 Reset to safe position: [{actor.worldPosition.x:.2f}, {actor.worldPosition.y:.2f}]")
        
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
            print(f"\n📍 Planning: {current_task}")
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
                    
                    # Store VLM analysis results for validation
                    bge.logic.vlm_analysis = {
                        "task_complete": sequence_result.get("task_complete", False),
                        "current_room": sequence_result.get("current_room", "UNKNOWN"),
                        "furniture_visible": sequence_result.get("furniture_visible", "None"),
                        "reasoning": sequence_result.get("reasoning", "")
                    }
                    
                    print(f"🎯 BGE: Loaded sequence: {bge.logic.vesper_movement_queue}")
                    print(f"🏠 BGE: Room Analysis - Current: {bge.logic.vlm_analysis['current_room']}")
                    print(f"🪑 BGE: Furniture: {bge.logic.vlm_analysis['furniture_visible']}")
                    print(f"💭 BGE: {sequence_result.get('reasoning', 'No reasoning provided')}")
                    
                    # Check if VLM says task is complete
                    if bge.logic.vlm_analysis["task_complete"]:
                        print(f"🎯 BGE: VLM confirms task complete - actor in correct room!")
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
        print(f"📍 Queue: {bge.logic.vesper_movement_queue}")

        old_position = [actor.worldPosition.x, actor.worldPosition.y]
        move_success = move_actor(actor, next_move)
        new_position = [actor.worldPosition.x, actor.worldPosition.y]

        # Position drift detection - check if actor is moving to extreme coordinates
        if abs(new_position[0]) > 15 or abs(new_position[1]) > 15:
            print(f"🚨 BGE: EXTREME POSITION DETECTED! Actor at [{new_position[0]:.1f}, {new_position[1]:.1f}]")
            print("🔄 BGE: Position appears outside house - requesting immediate visual re-analysis")
            bge.logic.vesper_movement_queue = []  # clear current plan
            if not bge.logic._vesper_shot["pending"]:
                request_bird_eye_screenshot()
            return

        # Detect if stuck (position didn't change)
        moved_distance = ((new_position[0] - old_position[0])**2 + (new_position[1] - old_position[1])**2)**0.5
        if moved_distance < 0.1 and next_move != "STAY":
            print("⚠️ BGE: Actor appears stuck or movement blocked by safety boundaries")
            bge.logic.vesper_movement_queue = []  # trigger replanning
            # Request new screenshot immediately
            if not bge.logic._vesper_shot["pending"]:
                request_bird_eye_screenshot()
            return

        # If the short sequence is finished, request a new screenshot for the next cycle
        if not bge.logic.vesper_movement_queue:
            print("📸 BGE: Short sequence completed - requesting NEW screenshot for re-analysis")
            
            # Enhanced task completion validation
            if next_move == "STAY":
                # Validate task completion based on VLM room analysis
                vlm_analysis = getattr(bge.logic, 'vlm_analysis', {})
                task_complete_confirmed = vlm_analysis.get("task_complete", False)
                current_room = vlm_analysis.get("current_room", "UNKNOWN")
                furniture_visible = vlm_analysis.get("furniture_visible", "None")
                
                if task_complete_confirmed:
                    print(f"✅ BGE: Task '{current_task}' VALIDATED - Actor confirmed in correct room!")
                    print(f"🏠 BGE: Final location: {current_room}")
                    print(f"🪑 BGE: Furniture confirmation: {furniture_visible}")
                    bge.logic.vesper_current_task_index += 1
                    bge.logic.vesper_sequence_step = 0
                    
                    # Clear VLM analysis for next task
                    bge.logic.vlm_analysis = {}
                else:
                    print(f"⚠️ BGE: STAY command but task NOT validated!")
                    print(f"🏠 BGE: Current room: {current_room} (target needed for '{current_task}')")
                    print(f"🔄 BGE: Continuing navigation - need to reach correct room")
                    # Don't advance task index - continue navigation
            else:
                print(f"🔄 BGE: Continuing task '{current_task}' with new analysis cycle")

            # Request the next screenshot right away
            if not bge.logic._vesper_shot["pending"]:
                request_bird_eye_screenshot()
            return

if __name__ == "__main__":
    main()
