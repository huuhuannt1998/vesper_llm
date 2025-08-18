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
            print(f"❌ BGE: Screenshot file not visible: bge_{next_num:03d}.png")
            
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
        
        system_prompt = """You are controlling an actor in a house. Help navigate to complete the task.

MOVEMENT COMMANDS:
- "UP" = move forward (+Y direction)
- "DOWN" = move backward (-Y direction) 
- "LEFT" = move left (-X direction)
- "RIGHT" = move right (+X direction)
- "STAY" = stop (task complete)

RESPONSE FORMAT (JSON only):
{
  "next_direction": "UP|DOWN|LEFT|RIGHT|STAY",
  "reasoning": "why this direction helps complete the task"
}"""

        user_prompt = f"""Current Task: {current_task}
Actor Position: [{actor_position[0]:.2f}, {actor_position[1]:.2f}]

Look at the bird's eye view image and decide the next movement to complete this task. You can see the layout of the house, walls, doors, and rooms. The actor's current position should be visible in the image.

IMPORTANT: If the actor appears to be AT or VERY CLOSE to the target room/area for the task, respond with "STAY" to complete the task. Don't keep moving if you're already in the right location.

Examples:
- If task is "Go to kitchen" and actor is in/near the kitchen area, use "STAY"
- If task is "Go to bathroom" and actor is in/near the bathroom area, use "STAY"
- If task is "Cook in kitchen" and actor is in the kitchen, use "STAY"""

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
    
    # Find actor
    actor = scene.objects.get("Actor") or owner
    if not actor:
        print("❌ BGE: No Actor found!")
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
