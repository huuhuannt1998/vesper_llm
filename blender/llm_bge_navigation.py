# VESPER LLM Navigation - BGE Implementation
# This script must be in the same directory as the .blend file

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
            if obj.name == "BirdEyeCamera":
                bird_camera = obj
                break
        
        if not bird_camera:
            print("⚠️ BGE: BirdEyeCamera not found - using any available camera")
            # Fallback to any camera for screenshot
            for obj in scene.objects:
                if "camera" in obj.name.lower():
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
            # print(f"❌ BGE: Screenshot file not visible: bge_{next_num:03d}.png")
            print(f"")
        return screenshot_path
        
    except Exception as e:
        print(f"❌ BGE: Screenshot failed: {e}")
        return None
        
        file_size = os.path.getsize(screenshot_path)
        print(f"📸 BGE: Fresh screenshot captured: {screenshot_path} ({file_size} bytes)")
        
        return screenshot_path
        
        # Optionally create enhanced version with annotations
        try:
            enhanced_path = create_enhanced_screenshot(screenshot_path)
            if enhanced_path and os.path.exists(enhanced_path):
                print(f"📝 BGE: Enhanced screenshot: {enhanced_path}")
                return enhanced_path  # Return enhanced version for VLM
            else:
                print(f"📝 BGE: Using original screenshot (enhancement failed)")
                return screenshot_path  # Use original if enhancement fails
        except Exception as e:
            print(f"⚠️ BGE: Could not enhance screenshot: {e}")
            print(f"� BGE: Using original screenshot")
            return screenshot_path  # Fall back to original screenshot
        
        return screenshot_path
        
    except Exception as e:
        print(f"❌ BGE: Screenshot failed: {e}")
        return None
        
        # Restore original camera
        scene.active_camera = original_camera
        
        print(f"📸 BGE: Fresh screenshot captured: {screenshot_path}")
        
        # Optionally create enhanced version with annotations
        try:
            enhanced_path = create_enhanced_screenshot(screenshot_path)
            if enhanced_path and os.path.exists(enhanced_path):
                print(f"📝 BGE: Enhanced screenshot: {enhanced_path}")
                return enhanced_path  # Return enhanced version for VLM
            else:
                print(f"📝 BGE: Using original screenshot (enhancement failed)")
                return screenshot_path  # Use original if enhancement fails
        except Exception as e:
            print(f"⚠️ BGE: Could not enhance screenshot: {e}")
            print(f"📝 BGE: Using original screenshot")
            return screenshot_path  # Fall back to original screenshot
        
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
    
    NOTE: This function is now used only as a fallback when the main VLM
    doesn't provide clear safety analysis. The primary navigation now uses
    comprehensive single-call analysis to reduce VLM calls from 5 to 1-2 per step.
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
    """Find an alternative safe direction when original direction is blocked"""
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
    """Get navigation command from LLM with vision support"""
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
        
        system_prompt = """You are a navigation AI controlling an actor in a 3D house environment with advanced spatial reasoning for room identification.

CRITICAL RULES:
1. NEVER suggest moving into walls, obstacles, or blocked areas
2. If you see a wall or obstacle in the direction you want to move, choose a different direction
3. Always prioritize safe, open paths
4. If all directions appear blocked, suggest staying in place

SPATIAL REASONING FOR ROOM IDENTIFICATION:
- Analyze the house layout to identify different room types
- BATHROOM: Small, enclosed rectangular rooms (often 1x2 or 2x2 room size)
- KITCHEN: Larger rooms with appliances/counters (distinctive furniture patterns)
- LIVING ROOM: Open central areas with seating arrangements
- BEDROOM: Private rooms with bed furniture, enclosed by walls

MOVEMENT COMMANDS:
- "UP" = move forward (+Y direction)
- "DOWN" = move backward (-Y direction) 
- "LEFT" = move left (-X direction)
- "RIGHT" = move right (+X direction)
- "STAY" = stop (task complete or in target room)

COMPREHENSIVE ANALYSIS REQUIRED:
You must analyze ALL four directions (UP, DOWN, LEFT, RIGHT) for obstacles/walls and provide:
1. The PRIMARY recommended action based on task objective
2. 2-3 SAFE ALTERNATIVE actions if the primary is blocked
3. Detailed safety analysis for each direction
4. Room identification reasoning when relevant

NAVIGATION RULES:
- NEVER move through walls (dark gray/black areas)
- ONLY move through open doorways and corridors
- Navigate around obstacles and furniture
- Look for clear paths between rooms
- The actor appears as a colored dot in the image
- For bathroom tasks: prioritize movement toward small, enclosed rooms
- Use spatial reasoning to identify room types by size and layout

RESPONSE FORMAT (JSON only):
{
  "next_direction": "UP|DOWN|LEFT|RIGHT|STAY",
  "alternatives": ["action1", "action2", "action3"],
  "safety_analysis": {
    "UP": "CLEAR|BLOCKED - reason and room identification if relevant",
    "DOWN": "CLEAR|BLOCKED - reason and room identification if relevant", 
    "LEFT": "CLEAR|BLOCKED - reason and room identification if relevant",
    "RIGHT": "CLEAR|BLOCKED - reason and room identification if relevant"
  },
  "reasoning": "detailed explanation including room identification and task progression logic"
}"""

        user_prompt = f"""Current Task: {current_task}
Actor Position: [{actor_position[0]:.2f}, {actor_position[1]:.2f}]

Look at the bird's eye view image and decide the next movement to complete this task.

ROOM IDENTIFICATION GUIDE:
In this house layout, you can identify rooms by their characteristics:
- BATHROOM: Usually a small, enclosed room with fixtures (often in corners or along walls)
- KITCHEN: Larger room with appliances and counters (often has distinctive kitchen furniture)
- LIVING ROOM: Open central area with seating furniture
- BEDROOM: Private room with bed furniture, usually separated by walls

NAVIGATION STRATEGY FOR BATHROOM TASKS:
- Look for small, enclosed rooms that could be bathrooms
- Bathrooms are typically accessed through doorways from hallways or main areas
- If you see multiple small rooms, move toward the one that appears most bathroom-like
- Small rectangular rooms along walls are often bathrooms

You can see:
- House layout with walls (dark areas) and open spaces (light areas)
- Doorways and corridors for navigation
- The actor's current position as a colored dot
- Room layouts and furniture that help identify room types

CRITICAL: Analyze the image carefully and AVOID WALLS. Only move through open doorways and clear paths. If you see walls blocking the direct path, navigate around them through available doorways.

IMPORTANT: If the actor appears to be AT or VERY CLOSE to the target room/area for the task, respond with "STAY" to complete the task. Don't keep moving if you're already in the right location.

For bathroom tasks specifically:
- Look for small, enclosed rectangular spaces
- Move toward areas that appear to be private rooms
- If uncertain about room identity, move toward unexplored small rooms
- Use doorways and corridors to explore different areas of the house

Examples:
- If task is "Go to kitchen" and actor is in/near the kitchen area, use "STAY"
- If task is "Go to bathroom" and actor is in/near a small enclosed room, use "STAY"
- If task is "Prepare in bathroom" and actor is inside what appears to be a bathroom, use "STAY"
- If there's a wall in the direct path, find an alternative route through doorways"""

        # Use vision if screenshot available, otherwise wait
        print(f"🔍 BGE: Checking screenshot: {screenshot_path}")
        print(f"🔍 BGE: Screenshot exists: {os.path.exists(screenshot_path) if screenshot_path else 'No path'}")
        
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                response = chat_completion_with_vision(
                    f"{system_prompt}\n\n{user_prompt}", 
                    image_path=screenshot_path
                )
                print("🔍 BGE: Using vision-based navigation")
                
                # Check if response indicates timeout or connection error
                if "TIMEOUT_ERROR" in response or "CONNECTION_ERROR" in response:
                    print(f"⏳ BGE: VLM timeout/connection issue - staying in place")
                    return {"next_direction": "STAY", "reasoning": "VLM timeout - waiting for reconnection"}
                    
            except Exception as e:
                print(f"❌ BGE: VLM call failed: {e}")
                print("⏳ BGE: Waiting for VLM - no fallback navigation")
                return {"next_direction": "STAY", "reasoning": f"VLM connection error: {e} - waiting for reconnection"}
        else:
            print("❌ BGE: No screenshot available")
            return {"next_direction": "STAY", "reasoning": "No screenshot available for vision analysis"}
        
        # Parse JSON response
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                
                # Extract comprehensive navigation data
                proposed_direction = result.get("next_direction", "STAY")
                alternatives = result.get("alternatives", [])
                safety_analysis = result.get("safety_analysis", {})
                reasoning = result.get("reasoning", "No reasoning provided")
                
                print(f"🧠 BGE: VLM Analysis - Primary: {proposed_direction}")
                print(f"🧠 BGE: Alternatives: {alternatives}")
                for direction, analysis in safety_analysis.items():
                    print(f"🔍 BGE: {direction}: {analysis}")
                
                # Use VLM's comprehensive analysis to select safe direction
                if proposed_direction != "STAY":
                    # Check if VLM marked the primary direction as safe
                    primary_analysis = safety_analysis.get(proposed_direction, "")
                    if "CLEAR" in primary_analysis.upper():
                        print(f"✅ BGE: Primary direction {proposed_direction} verified as safe by VLM")
                        return result
                    elif "BLOCKED" in primary_analysis.upper():
                        # VLM detected obstacle in primary direction, use alternatives
                        print(f"⚠️ BGE: VLM detected obstacle in {proposed_direction}, checking alternatives")
                        
                        # Try alternatives in order, using VLM's safety analysis
                        for alt_direction in alternatives:
                            if alt_direction in safety_analysis:
                                alt_analysis = safety_analysis[alt_direction]
                                if "CLEAR" in alt_analysis.upper():
                                    print(f"🔄 BGE: Using safe alternative: {alt_direction}")
                                    result["next_direction"] = alt_direction
                                    result["reasoning"] = f"Alternative route: {alt_analysis}"
                                    return result
                        
                        # If no alternatives are clear, stay in place
                        print(f"🛑 BGE: All directions blocked according to VLM, staying put")
                        result["next_direction"] = "STAY"
                        result["reasoning"] = "All paths blocked - safety override"
                        return result
                    else:
                        # VLM didn't provide clear safety analysis, do minimal validation
                        print(f"⚠️ BGE: Unclear VLM safety analysis, performing single validation check")
                        is_safe = validate_movement_with_vlm(screenshot_path, proposed_direction, actor_position)
                        if not is_safe:
                            result["next_direction"] = "STAY"
                            result["reasoning"] = "Safety validation failed"
                        return result
                else:
                    # VLM chose STAY
                    print(f"🏁 BGE: VLM chose to stay - task likely complete")
                    return result
            else:
                print("❌ BGE: JSON structure not found in VLM response")
                return {"next_direction": "STAY", "reasoning": "JSON parse failed - waiting for valid VLM response"}
        except json.JSONDecodeError as e:
            print(f"❌ BGE: JSON decode error: {e}")
            return {"next_direction": "STAY", "reasoning": "JSON decode failed - waiting for valid VLM response"}
        except Exception as e:
            print(f"❌ BGE: Response processing error: {e}")
            return {"next_direction": "STAY", "reasoning": f"Processing error: {e} - waiting for valid VLM response"}
            
    except Exception as e:
        print(f"❌ BGE: LLM error: {e}")
        return {"next_direction": "UP", "reasoning": f"LLM error: {e}"}

def move_actor_bge(actor, direction, step_size=0.3):
    """Move actor in BGE coordinate system"""
    if direction == "STAY":
        print("🛑 BGE: Actor staying - task complete or waiting for VLM!")
        return True
    
    if direction == "UP":
        actor.worldPosition.y += step_size
    elif direction == "DOWN":
        actor.worldPosition.y -= step_size
    elif direction == "LEFT":
        actor.worldPosition.x -= step_size
    elif direction == "RIGHT":
        actor.worldPosition.x += step_size
    
    print(f"🎮 BGE: Actor moved {direction} to [{actor.worldPosition.x:.2f}, {actor.worldPosition.y:.2f}]")
    return False

def find_or_create_actor(scene):
    """Find existing actor named 'Actor' or rename/create one for consistent naming"""
    actor = None
    
    # First, try to find an object specifically named "Actor"
    for obj in scene.objects:
        if obj.name == "Actor":
            actor = obj
            print(f"✅ BGE: Found Actor: {obj.name}")
            break
    
    # If no "Actor" found, look for suitable objects to rename as "Actor"
    if not actor:
        # Try character-like objects first (prioritize character shapes)
        character_objects = []
        other_suitable = []
        
        for obj in scene.objects:
            if (not obj.name.lower().startswith(('camera', 'light', 'lamp', 'floor', 'wall', 'ceiling')) 
                and hasattr(obj, 'worldPosition')):
                
                # Check if it's a character-like object
                if any(keyword in obj.name.lower() for keyword in ['character', 'player', 'human', 'person', 'suzanne', 'monkey']):
                    character_objects.append(obj)
                else:
                    other_suitable.append(obj)
        
        # Prioritize character objects to preserve character-like appearance
        if character_objects:
            actor = character_objects[0]
            old_name = actor.name
            actor.name = "Actor"
            print(f"✅ BGE: Renamed character '{old_name}' to 'Actor' for consistent naming")
        elif other_suitable:
            # Use other suitable objects if no character found
            for obj in other_suitable:
                if obj.name.lower().startswith(('player', 'cube', 'sphere')):
                    actor = obj
                    old_name = obj.name
                    obj.name = "Actor"
                    print(f"✅ BGE: Renamed '{old_name}' to 'Actor' for consistent naming")
                    break
            
            # If no preferred objects, use first suitable
            if not actor and other_suitable:
                actor = other_suitable[0]
                old_name = actor.name
                actor.name = "Actor"
                print(f"✅ BGE: Renamed '{old_name}' to 'Actor' for navigation")
    
    # Last resort: notify need for manual setup
    if not actor:
        print("⚠️ BGE: No suitable object found to use as 'Actor' - add a movable object to the scene")
        print("💡 BGE: Consider adding a character, player, or any movable mesh object")
        return None
    
    return actor

def find_navigation_camera(scene):
    """Find existing camera named 'BirdEyeCamera' or rename one for consistent naming"""
    camera = None
    
    # First, try to find a camera specifically named "BirdEyeCamera"
    for obj in scene.objects:
        if obj.name == "BirdEyeCamera":
            camera = obj
            print(f"✅ BGE: Found BirdEyeCamera: {obj.name}")
            break
    
    # If no "BirdEyeCamera" found, look for cameras to rename as "BirdEyeCamera"
    if not camera:
        # Try to find any camera and rename it to "BirdEyeCamera"
        camera_priorities = ["TopCamera", "OverheadCamera", "NavCamera", "Camera"]
        
        # First, try preferred camera names
        for preferred_name in camera_priorities:
            for obj in scene.objects:
                if obj.name.lower() == preferred_name.lower():
                    old_name = obj.name
                    obj.name = "BirdEyeCamera"
                    camera = obj
                    print(f"✅ BGE: Renamed camera '{old_name}' to 'BirdEyeCamera' for consistent naming")
                    break
            if camera:
                break
        
        # If no preferred cameras found, use any camera
        if not camera:
            for obj in scene.objects:
                if "camera" in obj.name.lower():
                    old_name = obj.name
                    obj.name = "BirdEyeCamera"
                    camera = obj
                    print(f"✅ BGE: Renamed camera '{old_name}' to 'BirdEyeCamera' for navigation")
                    break
    
    if not camera:
        print("⚠️ BGE: No camera found to rename as 'BirdEyeCamera' - add a camera to the scene")
        print("💡 BGE: Position the camera above the house for best bird's eye view screenshots")
    
    return camera

def analyze_scene_layout(scene):
    """Analyze the imported scene to understand layout"""
    layout_info = {
        "total_objects": len(scene.objects),
        "cameras": [],
        "lights": [],
        "static_objects": [],
        "movable_objects": [],
        "bounds": {"min_x": float('inf'), "max_x": float('-inf'), 
                  "min_y": float('inf'), "max_y": float('-inf')}
    }
    
    for obj in scene.objects:
        name_lower = obj.name.lower()
        
        # Categorize objects
        if "camera" in name_lower:
            layout_info["cameras"].append(obj.name)
        elif any(light_type in name_lower for light_type in ["light", "lamp", "sun"]):
            layout_info["lights"].append(obj.name)
        elif any(static_type in name_lower for static_type in ["floor", "wall", "ceiling", "door", "window"]):
            layout_info["static_objects"].append(obj.name)
        else:
            layout_info["movable_objects"].append(obj.name)
        
        # Calculate scene bounds
        if hasattr(obj, 'worldPosition'):
            x, y = obj.worldPosition.x, obj.worldPosition.y
            layout_info["bounds"]["min_x"] = min(layout_info["bounds"]["min_x"], x)
            layout_info["bounds"]["max_x"] = max(layout_info["bounds"]["max_x"], x)
            layout_info["bounds"]["min_y"] = min(layout_info["bounds"]["min_y"], y)
            layout_info["bounds"]["max_y"] = max(layout_info["bounds"]["max_y"], y)
    
    return layout_info

def setup_navigation_for_new_layout():
    """Setup navigation system for newly imported glTF layout"""
    scene = bge.logic.getCurrentScene()
    
    print("\n🏠 BGE: Setting up navigation for new layout...")
    
    # Analyze the scene
    layout_info = analyze_scene_layout(scene)
    
    print(f"📊 BGE: Scene Analysis:")
    print(f"   Objects: {layout_info['total_objects']}")
    print(f"   Cameras: {len(layout_info['cameras'])} - {layout_info['cameras']}")
    print(f"   Lights: {len(layout_info['lights'])}")
    print(f"   Static: {len(layout_info['static_objects'])}")
    print(f"   Movable: {len(layout_info['movable_objects'])}")
    
    # Calculate scene bounds
    bounds = layout_info["bounds"]
    if bounds["min_x"] != float('inf'):
        width = bounds["max_x"] - bounds["min_x"]
        height = bounds["max_y"] - bounds["min_y"]
        center_x = (bounds["min_x"] + bounds["max_x"]) / 2
        center_y = (bounds["min_y"] + bounds["max_y"]) / 2
        
        print(f"🗺️ BGE: Layout bounds:")
        print(f"   X: {bounds['min_x']:.1f} to {bounds['max_x']:.1f} (width: {width:.1f})")
        print(f"   Y: {bounds['min_y']:.1f} to {bounds['max_y']:.1f} (height: {height:.1f})")
        print(f"   Center: ({center_x:.1f}, {center_y:.1f})")
    
    # Find/setup actor
    actor = find_or_create_actor(scene)
    if actor:
        # Store original position before any modifications
        original_pos = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
        print(f"📍 BGE: Actor original position: ({original_pos[0]:.1f}, {original_pos[1]:.1f}, {original_pos[2]:.1f})")
        
        # Check if auto-positioning is disabled
        auto_position_disabled = False
        try:
            # Try to access scene properties to check positioning setting
            if hasattr(bge.logic, 'globalDict') and 'vesper_disable_auto_position' in bge.logic.globalDict:
                auto_position_disabled = bge.logic.globalDict['vesper_disable_auto_position']
        except:
            pass
        
        if auto_position_disabled:
            print(f"📍 BGE: Auto-positioning disabled - keeping actor at current position")
        else:
            # Only reposition actor if it's at origin (0,0,0) or outside reasonable bounds
            if bounds["min_x"] != float('inf'):
                # Check if actor is at origin or outside scene bounds
                at_origin = (abs(actor.worldPosition.x) < 0.1 and abs(actor.worldPosition.y) < 0.1)
                outside_bounds = (actor.worldPosition.x < bounds["min_x"] - 2 or 
                                actor.worldPosition.x > bounds["max_x"] + 2 or
                                actor.worldPosition.y < bounds["min_y"] - 2 or 
                                actor.worldPosition.y > bounds["max_y"] + 2)
                
                if at_origin or outside_bounds:
                    center_x = (bounds["min_x"] + bounds["max_x"]) / 2
                    center_y = (bounds["min_y"] + bounds["max_y"]) / 2
                    actor.worldPosition.x = center_x
                    actor.worldPosition.y = center_y
                    print(f"📍 BGE: Repositioned actor from origin/outside bounds to center: ({center_x:.1f}, {center_y:.1f})")
                else:
                    print(f"📍 BGE: Keeping actor at current position: ({original_pos[0]:.1f}, {original_pos[1]:.1f})")
            else:
                print(f"📍 BGE: Keeping actor at current position (no scene bounds calculated)")
    
    # Find/setup camera
    camera = find_navigation_camera(scene)
    
    # Store layout info for navigation system
    bge.logic.vesper_layout_info = layout_info
    
    print("✅ BGE: Navigation setup complete for new layout!\n")
    
    return actor, camera, layout_info

def main():
    """Main BGE navigation function"""
    controller = bge.logic.getCurrentController()
    owner = controller.owner
    scene = bge.logic.getCurrentScene()
    
    # Check if this is a new scene/layout that needs setup
    if not hasattr(bge.logic, "vesper_layout_setup_done"):
        print("🔄 BGE: Detecting new layout - setting up navigation...")
        actor, camera, layout_info = setup_navigation_for_new_layout()
        bge.logic.vesper_layout_setup_done = True
        
        # Use the found/created actor instead of default owner
        if actor:
            owner = actor
    else:
        # Find actor for existing setup - always use "Actor" name
        actor = None
        for obj in scene.objects:
            if obj.name == "Actor":
                actor = obj
                break
        
        if not actor:
            print("❌ BGE: No 'Actor' object found! Run setup again or manually rename your actor to 'Actor'")
            return
    
    # Initialize navigation state
    if not hasattr(bge.logic, "vesper_nav_state"):
        # Read tasks from the addon (stored in scene properties)
        scene = bge.logic.getCurrentScene()
        
        # Try to get tasks from the VESPER addon - different approaches
        tasks = []
        
        # Method 1: Check scene properties directly
        try:
            import bpy
            if hasattr(bpy.context.scene, 'vesper_tasks') and bpy.context.scene.vesper_tasks:
                tasks = [task.strip() for task in bpy.context.scene.vesper_tasks.split("|") if task.strip()]
                print(f"✅ BGE: Loaded tasks from bpy.context: {tasks}")
        except:
            pass
        
        # Method 2: Check scene custom properties 
        if not tasks:
            try:
                if 'vesper_tasks' in scene:
                    tasks = [task.strip() for task in scene['vesper_tasks'].split("|") if task.strip()]
                    print(f"✅ BGE: Loaded tasks from scene properties: {tasks}")
            except:
                pass
        
        # Method 3: Check global storage
        if not tasks and hasattr(bge.logic, 'globalDict') and 'vesper_tasks' in bge.logic.globalDict:
            try:
                tasks = [task.strip() for task in bge.logic.globalDict['vesper_tasks'].split("|") if task.strip()]
                print(f"✅ BGE: Loaded tasks from globalDict: {tasks}")
            except:
                pass
        
        # Method 4: Read from tasks file
        if not tasks:
            try:
                # Get the directory containing this script (same as .blend file)
                script_dir = os.path.dirname(os.path.abspath(__file__))
                tasks_file = os.path.join(script_dir, "vesper_tasks.txt")
                if os.path.exists(tasks_file):
                    with open(tasks_file, 'r') as f:
                        file_content = f.read().strip()
                        if file_content:
                            tasks = [task.strip() for task in file_content.split("|") if task.strip()]
                            print(f"✅ BGE: Loaded tasks from file: {tasks}")
            except Exception as e:
                print(f"⚠️ BGE: Could not read tasks file: {e}")
        
        # Fallback to default tasks if none found
        if not tasks:
            tasks = ["Go to bedroom", "Go to kitchen", "Go to living room"]
            print(f"⚠️ BGE: No addon tasks found, using default: {tasks}")
        
        bge.logic.vesper_nav_state = {
            "tasks": tasks,
            "current_task_index": 0,
            "step_count": 0,
            "max_steps": 12,
            "last_update": time.time(),
            "update_interval": 2.0,  # Decision every 2 seconds
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
    
    # Get navigation decision
    actor_pos = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
    
    print(f"🎯 BGE: Actor at [{actor_pos[0]:.2f}, {actor_pos[1]:.2f}]")
    
    if LLM_AVAILABLE:
        # Use LLM for navigation
        llm_result = get_llm_navigation_command(current_task, actor_pos)
        direction = llm_result.get("next_direction", "STAY")
        reasoning = llm_result.get("reasoning", "No reasoning")
        print(f"🧠 BGE: LLM Decision → {direction}")
        print(f"💭 BGE: {reasoning}")
    else:
        # Use simple pattern navigation
        direction = get_simple_navigation_command(current_task, state["step_count"])
        print(f"🔄 BGE: Pattern Decision → {direction} (no LLM)")
    
    # Move actor
    task_finished = move_actor_bge(actor, direction)
    
    # Capture fresh screenshot after movement for next decision
    # This ensures the LLM sees the updated actor position
    if not task_finished and direction != "STAY":
        # Wait a moment for the movement to complete
        time.sleep(0.1)
        
        # Capture screenshot showing new position
        fresh_screenshot = capture_bird_eye_screenshot()
        if fresh_screenshot:
            # Store the fresh screenshot path for next iteration
            state["last_screenshot"] = fresh_screenshot
            print(f"📱 BGE: Fresh screenshot saved for next decision")
    
    # Check if task is complete
    if task_finished or direction == "STAY" or state["step_count"] >= state["max_steps"]:
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
