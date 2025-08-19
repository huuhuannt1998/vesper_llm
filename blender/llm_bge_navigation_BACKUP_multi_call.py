# VESPER LLM Navigation - BGE Implementation (BACKUP - Multi-Call Validation Version)
# This is the previous version with individual collision validation calls
# Use this if you need to revert from the optimized single-call approach

import bge
import sys
import os
import time
import json
import math

# Add parent directory to Python path for imports
def setup_python_path():
    """Setup Python path to find our modules"""
    try:
        # Get the directory containing this script (same as .blend file)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to vesper_llm root
        vesper_root = os.path.dirname(script_dir)
        
        if vesper_root not in sys.path:
            sys.path.insert(0, vesper_root)
            print(f"✅ BGE: Added vesper_llm path: {vesper_root}")
        
        # Load environment variables from the correct .env path
        env_path = os.path.join(vesper_root, "backend", "app", "llm", ".env")
        if os.path.exists(env_path):
            # Try to use dotenv if available, otherwise parse manually
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                print(f"✅ BGE: Loaded .env from {env_path} (dotenv)")
            except ImportError:
                # Fallback: manually parse .env file
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

# Setup path
path_ok = setup_python_path()

# Try to import LLM client
LLM_AVAILABLE = False
if path_ok:
    try:
        from backend.app.llm.client import chat_completion, chat_completion_with_vision
        LLM_AVAILABLE = True
        print("✅ BGE: LLM client connected successfully")
    except ImportError as e:
        print(f"⚠️ BGE: LLM client not available - {e}")
        print(f"Current sys.path: {sys.path[:3]}...")  # Show first 3 paths

def get_simple_navigation_command(current_task, step_count):
    """Simple fallback navigation patterns"""
    task_lower = current_task.lower()
    
    if "bedroom" in task_lower:
        directions = ["UP", "UP", "RIGHT", "RIGHT", "UP"]
    elif "kitchen" in task_lower:
        directions = ["LEFT", "LEFT", "UP", "UP", "LEFT"]
    elif "living" in task_lower:
        directions = ["RIGHT", "RIGHT", "DOWN", "DOWN", "RIGHT"]
    else:
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    
    return directions[step_count % len(directions)]

def capture_bird_eye_screenshot():
    """Capture bird's eye view screenshot for LLM analysis"""
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find or create bird's eye camera
        bird_camera = None
        for obj in scene.objects:
            if obj.name == "BirdEyeCamera" or obj.name == "Camera" or "camera" in obj.name.lower():
                bird_camera = obj
                break
        
        if not bird_camera:
            print("⚠️ BGE: No suitable camera found for screenshots")
            return None
        
        # Set bird's eye camera as active
        original_camera = scene.active_camera
        scene.active_camera = bird_camera
        
        # Generate sequential filename
        captures_dir = os.path.join(os.path.dirname(__file__), "captures")
        if not os.path.exists(captures_dir):
            os.makedirs(captures_dir)
        
        # Find next sequential number
        existing_files = [f for f in os.listdir(captures_dir) if f.startswith('bge_') and f.endswith('.png')]
        if existing_files:
            # Extract numbers from filenames like bge_001.png, bge_002.png
            numbers = []
            for f in existing_files:
                try:
                    num_str = f.replace('bge_', '').replace('.png', '')
                    if num_str.isdigit():
                        numbers.append(int(num_str))
                except:
                    pass
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        
        screenshot_path = os.path.join(captures_dir, f"bge_{next_num:03d}.png")
        
        # Capture screenshot
        bge.render.makeScreenshot(screenshot_path)
        
        # Give BGE time to create the file - retry until file exists
        import time
        for attempt in range(20):  # Try for up to 2 seconds
            if os.path.exists(screenshot_path):
                break
            time.sleep(0.1)
        
        # Restore original camera
        scene.active_camera = original_camera
        
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"📸 BGE: Screenshot captured: bge_{next_num:03d}.png ({file_size} bytes)")
        else:
            print(f"")
        return screenshot_path
        
    except Exception as e:
        print(f"❌ BGE: Screenshot failed: {e}")
        return None

def create_enhanced_screenshot(screenshot_path):
    """Create enhanced screenshot with room labels and actor position"""
    try:
        # Import PIL for image enhancement
        from PIL import Image, ImageDraw, ImageFont
        
        # Get current navigation state for context
        state = getattr(bge.logic, "vesper_nav_state", {})
        current_task = state.get("tasks", ["Unknown"])[state.get("current_task_index", 0)] if state.get("tasks") else "Unknown"
        step_number = state.get("step_count", 0)
        
        # Open image
        img = Image.open(screenshot_path)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Try to load font
        try:
            font_large = ImageFont.truetype("arial.ttf", 16)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Add room labels (approximate positions - adjust based on your house layout)
        room_labels = [
            ("KITCHEN", (width * 0.2, height * 0.3), (0, 255, 0)),     # Green
            ("BATHROOM", (width * 0.1, height * 0.2), (0, 255, 255)),   # Cyan
            ("BEDROOM", (width * 0.4, height * 0.6), (255, 255, 0)),    # Yellow
            ("LIVING ROOM", (width * 0.6, height * 0.5), (255, 0, 255)) # Magenta
        ]
        
        for room_name, (x, y), color in room_labels:
            # Draw room label with background
            text_bbox = draw.textbbox((x, y), room_name, font=font_small)
            draw.rectangle(text_bbox, fill=(0, 0, 0, 180), outline=color)
            draw.text((x, y), room_name, fill=color, font=font_small)
        
        # Add current task information
        task_text = f"STEP {step_number}: {current_task}"
        draw.rectangle((5, 5, 300, 25), fill=(0, 0, 0, 180), outline=(255, 255, 0))
        draw.text((10, 10), task_text, fill=(255, 255, 0), font=font_small)
        
        # Add coordinate grid
        grid_color = (128, 128, 128, 100)
        for i in range(0, width, width//8):
            draw.line([(i, 0), (i, height)], fill=grid_color, width=1)
        for i in range(0, height, height//8):
            draw.line([(0, i), (width, i)], fill=grid_color, width=1)
        
        # Save enhanced version
        enhanced_path = screenshot_path.replace(".png", "_enhanced.png")
        img.save(enhanced_path)
        return enhanced_path
        
    except Exception as e:
        print(f"⚠️ BGE: Could not enhance screenshot: {e}")
        return None

def validate_movement_with_vlm(screenshot_path, direction, actor_position):
    """Validate if a movement direction is safe using VLM collision detection
    
    ORIGINAL MULTI-CALL VERSION: This function makes individual VLM calls
    to validate each direction separately. This was the working collision
    detection system before optimization.
    """
    if not screenshot_path or not os.path.exists(screenshot_path):
        return True  # Can't validate, allow movement
    
    try:
        # Ask VLM specifically about collision detection for this direction
        collision_prompt = f"""Look at this bird's eye view image. I can see a colored dot (the actor) at position [{actor_position[0]:.2f}, {actor_position[1]:.2f}].

QUESTION: If the actor moves {direction} from their current position, will they hit a wall or obstacle?

Analyze what is directly {direction.lower()} of the colored dot in the image.

Answer ONLY with:
- "SAFE" if the path is clear (no walls/obstacles)
- "BLOCKED" if there are walls/obstacles in that direction

Look carefully at the immediate area {direction.lower()} of the colored dot."""

        collision_response = chat_completion_with_vision(collision_prompt, image_path=screenshot_path)
        
        is_safe = "SAFE" in collision_response.upper()
        print(f"🛡️ BGE: Collision check for {direction}: {'SAFE' if is_safe else 'BLOCKED'}")
        
        return is_safe
        
    except Exception as e:
        print(f"⚠️ BGE: Collision validation failed: {e}")
        return True  # If validation fails, allow movement

def find_alternative_direction(screenshot_path, original_direction, actor_position, current_task):
    """Find an alternative safe direction when original direction is blocked
    
    ORIGINAL MULTI-CALL VERSION: This function makes up to 3 additional VLM calls
    to validate alternative directions one by one.
    """
    if not screenshot_path or not os.path.exists(screenshot_path):
        return "STAY"
    
    # Try alternative directions in order of preference
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    directions.remove(original_direction)  # Remove the blocked direction
    
    for direction in directions:
        if validate_movement_with_vlm(screenshot_path, direction, actor_position):
            print(f"🔄 BGE: Found alternative direction: {direction} (original {original_direction} was blocked)")
            return direction
    
    print(f"🛑 BGE: All directions blocked, staying in place")
    return "STAY"

def get_llm_navigation_command(current_task, actor_position):
    """Get navigation command from LLM with vision support
    
    ORIGINAL MULTI-CALL VERSION: This is the working collision detection system
    that makes 1 primary navigation call + up to 4 validation calls per step.
    Total: 5 VLM calls per navigation step.
    """
    if not LLM_AVAILABLE:
        return {"next_direction": "UP", "reasoning": "LLM unavailable"}
    
    try:
        # Check if we have a fresh screenshot from previous movement
        screenshot_path = None
        if hasattr(bge.logic, "vesper_nav_state") and "last_screenshot" in bge.logic.vesper_nav_state:
            screenshot_path = bge.logic.vesper_nav_state["last_screenshot"]
            if screenshot_path and os.path.exists(screenshot_path):
                print(f"🔄 BGE: Using fresh screenshot: {os.path.basename(screenshot_path)}")
            else:
                screenshot_path = None
        
        # If no fresh screenshot available, capture one now
        if not screenshot_path:
            screenshot_path = capture_bird_eye_screenshot()
            
        # If BGE screenshot failed, use the most recent existing screenshot
        if not screenshot_path or not os.path.exists(screenshot_path):
            captures_dir = os.path.join(os.path.dirname(__file__), "captures")
            if os.path.exists(captures_dir):
                png_files = [f for f in os.listdir(captures_dir) if f.startswith('bge_') and f.endswith('.png')]
                if png_files:
                    # Sort by filename (bge_001.png, bge_002.png, etc.)
                    png_files.sort()
                    latest_file = png_files[-1]  # Get the highest numbered file
                    screenshot_path = os.path.join(captures_dir, latest_file)
                    print(f"🔄 BGE: Using latest existing screenshot: {latest_file}")
                else:
                    print("❌ BGE: No screenshots available in captures folder")
                    screenshot_path = None
            else:
                print("❌ BGE: Captures folder doesn't exist")
                screenshot_path = None
        
        # ORIGINAL SIMPLE SYSTEM PROMPT - SINGLE DIRECTION DECISION
        system_prompt = """You are controlling an actor in a house. Help navigate to complete the task.

MOVEMENT COMMANDS:
- "UP" = move forward (+Y direction)
- "DOWN" = move backward (-Y direction) 
- "LEFT" = move left (-X direction)
- "RIGHT" = move right (+X direction)
- "STAY" = stop (task complete)

NAVIGATION RULES:
- NEVER move through walls (dark gray/black areas)
- ONLY move through open doorways and corridors
- Navigate around obstacles and furniture
- Look for clear paths between rooms
- The actor appears as a colored dot in the image

RESPONSE FORMAT (JSON only):
{
  "next_direction": "UP|DOWN|LEFT|RIGHT|STAY",
  "reasoning": "why this direction helps complete the task and avoids obstacles"
}"""

        user_prompt = f"""Current Task: {current_task}
Actor Position: [{actor_position[0]:.2f}, {actor_position[1]:.2f}]

Look at the bird's eye view image and decide the next movement to complete this task. You can see:
- House layout with walls (dark areas) and open spaces (light areas)
- Doorways and corridors for navigation
- The actor's current position as a colored dot
- Room layouts and furniture

CRITICAL: Analyze the image carefully and AVOID WALLS. Only move through open doorways and clear paths. If you see walls blocking the direct path, navigate around them through available doorways.

IMPORTANT: If the actor appears to be AT or VERY CLOSE to the target room/area for the task, respond with "STAY" to complete the task. Don't keep moving if you're already in the right location.

Examples:
- If task is "Go to kitchen" and actor is in/near the kitchen area, use "STAY"
- If task is "Go to bathroom" and actor is in/near the bathroom area, use "STAY"
- If task is "Cook in kitchen" and actor is in the kitchen, use "STAY"
- If there's a wall in the direct path, find an alternative route through doorways"""

        # Use vision if screenshot available, otherwise text-only
        print(f"🔍 BGE: Checking screenshot: {screenshot_path}")
        print(f"🔍 BGE: Screenshot exists: {os.path.exists(screenshot_path) if screenshot_path else 'No path'}")
        
        if screenshot_path and os.path.exists(screenshot_path):
            response = chat_completion_with_vision(
                f"{system_prompt}\n\n{user_prompt}", 
                image_path=screenshot_path
            )
            print("🔍 BGE: Using vision-based navigation")
        else:
            print("❌ BGE: No screenshot available - cannot proceed without vision")
            return {"next_direction": "STAY", "reasoning": "No screenshot available for vision analysis"}
        
        # Parse JSON
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                
                # ORIGINAL MULTI-CALL COLLISION VALIDATION SYSTEM
                # Validate the VLM's movement decision with individual collision detection calls
                proposed_direction = result.get("next_direction", "STAY")
                if proposed_direction != "STAY":
                    # This makes an additional VLM call to validate the proposed direction
                    is_safe = validate_movement_with_vlm(screenshot_path, proposed_direction, actor_position)
                    
                    if not is_safe:
                        # VLM proposed an unsafe move, find alternative
                        # This can make up to 3 more VLM calls to check alternative directions
                        alternative_direction = find_alternative_direction(
                            screenshot_path, proposed_direction, actor_position, current_task
                        )
                        print(f"⚠️ BGE: VLM suggested unsafe move {proposed_direction}, using {alternative_direction} instead")
                        result["next_direction"] = alternative_direction
                        result["reasoning"] = f"Collision avoided: {result['reasoning']} (redirected from {proposed_direction})"
                    else:
                        print(f"✅ BGE: VLM decision {proposed_direction} validated as safe")
                
                return result
            else:
                return {"next_direction": "UP", "reasoning": "JSON parse failed"}
        except json.JSONDecodeError:
            return {"next_direction": "UP", "reasoning": "JSON decode failed"}
            
    except Exception as e:
        print(f"❌ BGE: LLM error: {e}")
        return {"next_direction": "UP", "reasoning": f"LLM error: {e}"}

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
    
    # Initialize navigation state if not present
    if not hasattr(bge.logic, "vesper_nav_state"):
        bge.logic.vesper_nav_state = {
            "active": False,
            "step_count": 0,
            "tasks": ["Go to the kitchen", "Go to the bedroom", "Go to the bathroom"],
            "current_task_index": 0,
            "last_screenshot": None
        }
    
    state = bge.logic.vesper_nav_state
    
    # Check for P key press to start/stop navigation
    keyboard = bge.logic.keyboard
    p_key = bge.events.PKEY
    
    if keyboard.events[p_key] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        state["active"] = not state["active"]
        if state["active"]:
            state["step_count"] = 0
            print(f"🎮 BGE: Navigation STARTED - Task: {state['tasks'][state['current_task_index']]}")
        else:
            print("🛑 BGE: Navigation STOPPED")
    
    # Execute navigation if active
    if state["active"]:
        try:
            current_task = state["tasks"][state["current_task_index"]]
            actor_position = [owner.worldPosition.x, owner.worldPosition.y]
            
            # Capture fresh screenshot for this navigation step
            screenshot_path = capture_bird_eye_screenshot()
            
            if screenshot_path:
                state["last_screenshot"] = screenshot_path
                print(f"📸 BGE: Fresh screenshot for step {state['step_count']}: {os.path.basename(screenshot_path)}")
            
            # Get navigation command from LLM or fallback
            if LLM_AVAILABLE:
                nav_result = get_llm_navigation_command(current_task, actor_position)
                next_direction = nav_result["next_direction"]
                reasoning = nav_result["reasoning"]
                print(f"🧠 BGE: LLM decision: {next_direction} - {reasoning}")
            else:
                next_direction = get_simple_navigation_command(current_task, state["step_count"])
                reasoning = "LLM fallback navigation"
                print(f"🎮 BGE: Fallback direction: {next_direction}")
            
            # Move actor and check for task completion
            task_completed = move_actor_bge(owner, next_direction)
            
            if task_completed or next_direction == "STAY":
                # Task completed - move to next task or stop
                state["current_task_index"] = (state["current_task_index"] + 1) % len(state["tasks"])
                print(f"✅ BGE: Task completed! Next task: {state['tasks'][state['current_task_index']]}")
                state["step_count"] = 0
            else:
                state["step_count"] += 1
                
            # Limit steps per task to prevent infinite loops
            if state["step_count"] > 20:
                print("⚠️ BGE: Step limit reached, moving to next task")
                state["current_task_index"] = (state["current_task_index"] + 1) % len(state["tasks"])
                state["step_count"] = 0
            
            # Add delay between navigation steps
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ BGE: Navigation error: {e}")
            import traceback
            traceback.print_exc()

# Run the main navigation logic
if __name__ == "__main__":
    main()
