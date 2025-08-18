"""
VESPER Tools - Simple LLM Navigation Add-on for Blender/UPBGE
Focus: Simple Game Engine navigation with LLM visual guidance
"""

bl_info = {
    "name": "VESPER Tools",
    "author": "VESPER Team", 
    "version": (1, 0, 0),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > VESPER",
    "description": "LLM-powered navigation in Game Engine",
    "category": "Game Engine"
}

import bpy
import bpy.props
import json
import time
import os
import tempfile
import math
import base64
import random

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def get_random_tasks():
    """Generate 3 random tasks for the actor"""
    tasks = [
        "Go to bathroom",
        "Go to kitchen", 
        "Go to bedroom",
        "Go to living room",
        "Prepare in bathroom",
        "Cook in kitchen",
        "Rest in bedroom",
        "Relax in living room"
    ]
    return random.sample(tasks, 3)

def capture_bird_eye_screenshot():
    """Capture bird's eye view screenshot centered on actor"""
    try:
        scene = bpy.context.scene
        
        # Find actor
        actor = None
        for obj in scene.objects:
            if obj.name == "Actor" or (obj.type == 'MESH' and 'actor' in obj.name.lower()):
                actor = obj
                break
        
        if not actor:
            print("❌ No actor found")
            return None
            
        # Save original camera settings
        original_camera = scene.camera
        original_res_x = scene.render.resolution_x
        original_res_y = scene.render.resolution_y
        original_filepath = scene.render.filepath
        
        # Create or reuse bird's eye camera
        bird_cam = None
        for obj in scene.objects:
            if obj.name == "BirdEyeCamera" and obj.type == 'CAMERA':
                bird_cam = obj
                break
                
        if not bird_cam:
            bpy.ops.object.camera_add()
            bird_cam = bpy.context.object
            bird_cam.name = "BirdEyeCamera"
            bird_cam.data.type = 'ORTHO'
            bird_cam.data.ortho_scale = 12
        
        # Position camera above actor
        actor_pos = actor.location
        bird_cam.location = (actor_pos.x, actor_pos.y, actor_pos.z + 10)
        bird_cam.rotation_euler = (math.radians(90), 0, 0)  # Look down
        
        # Set camera and render settings
        scene.camera = bird_cam
        scene.render.resolution_x = 512
        scene.render.resolution_y = 512
        
        # Render screenshot
        screenshot_path = os.path.join(tempfile.gettempdir(), "vesper_screenshot.png")
        scene.render.filepath = screenshot_path
        bpy.ops.render.render(write_still=True)
        
        # Restore original settings
        scene.camera = original_camera
        scene.render.resolution_x = original_res_x
        scene.render.resolution_y = original_res_y
        scene.render.filepath = original_filepath
        
        print(f"📸 Screenshot saved: {screenshot_path}")
        return screenshot_path
        
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return None

def send_to_llm(screenshot_path, current_task, step_count):
    """Send screenshot to LLM and get movement command"""
    try:
        # Import LLM client
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        from backend.app.llm.client import chat_completion
        
        # Encode screenshot
        screenshot_base64 = None
        if screenshot_path and os.path.exists(screenshot_path):
            with open(screenshot_path, "rb") as img_file:
                img_data = img_file.read()
                screenshot_base64 = base64.b64encode(img_data).decode('utf-8')
                print(f"📸 Screenshot encoded ({len(screenshot_base64)} chars)")
        else:
            print("⚠️ No screenshot available")

        # Create prompt
        system_prompt = """You are controlling an actor in a house simulation. 
        Analyze the provided bird's-eye view image and help navigate the actor.

        TASK: Complete the assigned task by moving the actor to the correct target room.

        MOVEMENT COMMANDS (use only these):
        - "UP"    = move forward (+Y direction)
        - "DOWN"  = move backward (-Y direction) 
        - "LEFT"  = move left (-X direction)
        - "RIGHT" = move right (+X direction)
        - "STAY"  = remain still (only when the task is complete)

        ROOM DETECTION:
        - Valid room names: ["bedroom", "bathroom", "kitchen", "living_room", "office", "hallway", "unknown"]
        - Use "unknown" if the current room cannot be confidently identified.

        RESPONSE FORMAT (return JSON only, with no extra text):
        {
        "current_room": "<room name>",
        "next_direction": "UP|DOWN|LEFT|RIGHT|STAY",
        "reasoning": "<short reasoning why this direction is chosen>",
        "task_complete": true/false
        }

        STRICT RULES:
        1. Respond with **JSON only** — no explanations outside the JSON.
        2. Always include a reasoning field in one sentence.
        3. Use "STAY" only when task_complete = true.
        """


        user_prompt = f"""Current Task: {current_task}
Step: {step_count}

Look at the bird's eye view image and decide the next movement to complete this task."""

        # Get LLM response with vision
        response = chat_completion(system_prompt, user_prompt, max_tokens=300, image_base64=screenshot_base64)
        print(f"🧠 LLM Response: {response}")
        
        # Parse JSON response
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                return result
            else:
                print("⚠️ No JSON found in response")
                return {"next_direction": "UP", "task_complete": False, "reasoning": "fallback"}
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            return {"next_direction": "UP", "task_complete": False, "reasoning": "fallback"}
            
    except Exception as e:
        print(f"❌ LLM communication failed: {e}")
        return {"next_direction": "UP", "task_complete": False, "reasoning": "error fallback"}

def move_actor(direction):
    """Move actor based on direction command"""
    try:
        # Find actor
        actor = None
        for obj in bpy.context.scene.objects:
            if obj.name == "Actor" or (obj.type == 'MESH' and 'actor' in obj.name.lower()):
                actor = obj
                break
        
        if not actor:
            print("❌ No actor to move")
            return False
        
        # Movement distance
        step_size = 0.3  # Human-like movement speed
        
        # Calculate movement offset
        offset = [0, 0, 0]
        if direction == "UP":
            offset = [0, step_size, 0]
        elif direction == "DOWN":
            offset = [0, -step_size, 0]
        elif direction == "LEFT":
            offset = [-step_size, 0, 0]
        elif direction == "RIGHT":
            offset = [step_size, 0, 0]
        elif direction == "STAY":
            print("🛑 Actor staying in place")
            return True
        
        # Apply movement
        old_pos = actor.location.copy()
        actor.location.x += offset[0]
        actor.location.y += offset[1]
        actor.location.z += offset[2]
        
        # Update scene
        bpy.context.view_layer.update()
        
        new_pos = actor.location
        print(f"🚶 Actor moved {direction}: [{old_pos.x:.2f}, {old_pos.y:.2f}] → [{new_pos.x:.2f}, {new_pos.y:.2f}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Movement failed: {e}")
        return False

# =============================================================================
# BLENDER UI PANELS
# =============================================================================

class VESPER_PT_MainPanel(bpy.types.Panel):
    """Main VESPER control panel"""
    bl_label = "VESPER Navigation"
    bl_idname = "VESPER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VESPER'

    def draw(self, context):
        layout = self.layout
        
        # Task generation
        row = layout.row()
        row.operator("vesper.generate_tasks", text="🎯 Generate Random Tasks", icon='PLAY')
        
        # Show current tasks if available
        if hasattr(context.scene, 'vesper_tasks') and context.scene.vesper_tasks:
            box = layout.box()
            box.label(text="Current Tasks:")
            for i, task in enumerate(context.scene.vesper_tasks.split("|")):
                box.label(text=f"{i+1}. {task}")
            
            # Instructions for auto-start
            box = layout.box()
            box.label(text="🎮 Press P to start Game Engine", icon='INFO')
            box.label(text="Navigation will start automatically!")
        
        # Manual start navigation (backup option)
        row = layout.row()
        row.operator("vesper.start_navigation", text="🚀 Start Navigation (Manual)", icon='PLAY')

# =============================================================================
# BLENDER OPERATORS
# =============================================================================

class VESPER_OT_GenerateTasks(bpy.types.Operator):
    """Generate random tasks for the actor"""
    bl_idname = "vesper.generate_tasks"
    bl_label = "Generate Tasks"
    
    def execute(self, context):
        tasks = get_random_tasks()
        context.scene.vesper_tasks = "|".join(tasks)
        
        # Also store in BGE globalDict for Game Engine access
        try:
            import bge
            if hasattr(bge, 'logic') and hasattr(bge.logic, 'globalDict'):
                bge.logic.globalDict['vesper_tasks'] = "|".join(tasks)
                print("✅ Tasks also stored in BGE globalDict")
        except:
            # bge not available in regular Blender context, only in Game Engine
            pass
        
        # Also save to a text file that BGE can read
        try:
            import os
            tasks_file = os.path.join(os.path.dirname(__file__), "..", "..", "vesper_tasks.txt")
            with open(tasks_file, 'w') as f:
                f.write("|".join(tasks))
            print(f"✅ Tasks saved to file: {tasks_file}")
        except Exception as e:
            print(f"⚠️ Could not save tasks file: {e}")
        
        self.report({'INFO'}, f"Generated tasks: {', '.join(tasks)}")
        print("🎯 Generated Tasks:")
        for i, task in enumerate(tasks):
            print(f"  {i+1}. {task}")
        
        return {'FINISHED'}

class VESPER_OT_StartNavigation(bpy.types.Operator):
    """Start LLM navigation in Game Engine"""
    bl_idname = "vesper.start_navigation"  
    bl_label = "Start Navigation"
    
    def execute(self, context):
        # Check if tasks are generated
        if not hasattr(context.scene, 'vesper_tasks') or not context.scene.vesper_tasks:
            self.report({'ERROR'}, "Please generate tasks first!")
            return {'CANCELLED'}
        
        tasks = context.scene.vesper_tasks.split("|")
        
        print("🚀 VESPER NAVIGATION STARTING")
        print("=" * 50)
        print("📋 Task List:")
        for i, task in enumerate(tasks):
            print(f"  {i+1}. {task}")
        print("=" * 50)
        
        # Start the navigation loop
        self.navigation_loop(tasks)
        
        return {'FINISHED'}
    
    def navigation_loop(self, tasks):
        """Main navigation loop that will run in Game Engine"""
        
        for task_index, current_task in enumerate(tasks):
            print(f"\n🎯 Starting Task {task_index + 1}: {current_task}")
            
            step_count = 0
            max_steps = 20  # Prevent infinite loops
            task_complete = False
            
            while step_count < max_steps and not task_complete:
                step_count += 1
                print(f"\n📍 Step {step_count} - Task: {current_task}")
                
                # 1. Capture bird's eye screenshot
                print("📸 Capturing bird's eye view...")
                screenshot_path = capture_bird_eye_screenshot()
                
                # 2. Send to LLM for analysis
                print("🧠 Sending to LLM for analysis...")
                llm_result = send_to_llm(screenshot_path, current_task, step_count)
                
                direction = llm_result.get("next_direction", "STAY")
                reasoning = llm_result.get("reasoning", "No reasoning")
                task_complete = llm_result.get("task_complete", False)
                
                print(f"🧠 LLM Decision: {direction}")
                print(f"💭 Reasoning: {reasoning}")
                
                # 3. Move actor based on LLM command
                if direction != "STAY":
                    success = move_actor(direction)
                    if not success:
                        print("❌ Movement failed, stopping task")
                        break
                
                # 4. Check if task is complete
                if task_complete or direction == "STAY":
                    print(f"✅ Task completed: {current_task}")
                    break
                
                # Small delay for human-like movement
                time.sleep(0.5)
            
            if step_count >= max_steps:
                print(f"⚠️ Task {current_task} reached max steps")
        
        print("\n🎉 ALL TASKS COMPLETED!")

# =============================================================================
# AUTO-START HANDLER FOR GAME ENGINE  
# =============================================================================

@bpy.app.handlers.persistent  
def game_engine_pre_handler(scene):
    """Handler called before Game Engine starts"""
    try:
        # Check if we have tasks ready
        if hasattr(scene, 'vesper_tasks') and scene.vesper_tasks:
            print("🎮 GAME ENGINE STARTING - VESPER NAVIGATION READY!")
            # Set a flag to start navigation after Game Engine is running
            scene.vesper_auto_start = True
        else:
            print("🎮 Game Engine starting - Generate tasks first for auto-navigation")
            scene.vesper_auto_start = False
    except:
        pass

@bpy.app.handlers.persistent
def game_engine_post_handler(scene):
    """Handler called after Game Engine starts"""
    try:
        # Auto-start navigation if flag is set
        if hasattr(scene, 'vesper_auto_start') and scene.vesper_auto_start:
            print("🚀 AUTO-STARTING VESPER NAVIGATION!")
            
            # Start navigation with a timer delay
            def start_navigation():
                try:
                    tasks = scene.vesper_tasks.split("|")
                    navigation_operator = VESPER_OT_StartNavigation()
                    navigation_operator.navigation_loop(tasks)
                except Exception as e:
                    print(f"❌ Auto-navigation failed: {e}")
                return None  # Stop timer
            
            bpy.app.timers.register(start_navigation, first_interval=2.0)
            scene.vesper_auto_start = False  # Reset flag
    except:
        pass

# =============================================================================
# BLENDER REGISTRATION
# =============================================================================

# Scene properties for storing tasks
def init_scene_props():
    """Initialize scene properties"""
    bpy.types.Scene.vesper_tasks = bpy.props.StringProperty(
        name="VESPER Tasks",
        description="Generated tasks for the actor",
        default=""
    )
    bpy.types.Scene.vesper_auto_start = bpy.props.BoolProperty(
        name="VESPER Auto Start",
        description="Flag to auto-start navigation in Game Engine",
        default=False
    )

def clear_scene_props():
    """Clear scene properties"""
    if hasattr(bpy.types.Scene, 'vesper_tasks'):
        del bpy.types.Scene.vesper_tasks
    if hasattr(bpy.types.Scene, 'vesper_auto_start'):
        del bpy.types.Scene.vesper_auto_start

# Registration
classes = [
    VESPER_PT_MainPanel,
    VESPER_OT_GenerateTasks,
    VESPER_OT_StartNavigation,
]

def register():
    """Register the add-on"""
    print("🔧 Registering VESPER Tools Add-on...")
    
    for cls in classes:
        bpy.utils.register_class(cls)
    
    init_scene_props()
    
    # Register Game Engine handlers for auto-start
    if game_engine_pre_handler not in bpy.app.handlers.game_pre:
        bpy.app.handlers.game_pre.append(game_engine_pre_handler)
    if game_engine_post_handler not in bpy.app.handlers.game_post:
        bpy.app.handlers.game_post.append(game_engine_post_handler)
    
    print("✅ VESPER Tools registered successfully!")

def unregister():
    """Unregister the add-on"""
    print("🔧 Unregistering VESPER Tools Add-on...")
    
    # Remove handlers
    if game_engine_pre_handler in bpy.app.handlers.game_pre:
        bpy.app.handlers.game_pre.remove(game_engine_pre_handler)
    if game_engine_post_handler in bpy.app.handlers.game_post:
        bpy.app.handlers.game_post.remove(game_engine_post_handler)
    
    clear_scene_props()
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("✅ VESPER Tools unregistered!")

if __name__ == "__main__":
    register()
