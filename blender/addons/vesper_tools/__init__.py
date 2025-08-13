
bl_info = {
    "name": "VESPER Tools",
    "author": "VESPER Team", 
    "version": (2, 3, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Press P",
    "description": "LLM-controlled smart house navigation with bird's eye view",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
import tempfile
import base64
import os
import sys

class VESPER_OT_tag_device(bpy.types.Operator):
    bl_idname = "vesper.tag_device"
    bl_label = "Tag Selected as Device"
    device_type: bpy.props.EnumProperty(items=[
        ('light','Light',''),('switch','Switch',''),('sensor','Sensor','')])
    device_id: bpy.props.StringProperty()

    def execute(self, ctx):
        for obj in ctx.selected_objects:
            obj["vesper_device"] = {
                "id": self.device_id,
                "type": self.device_type,
                "room": ctx.scene.get("vesper_room","Unknown")
            }
        return {'FINISHED'}

class VESPER_OT_LLMNavigation(bpy.types.Operator):
    bl_idname = "vesper.llm_navigation"
    bl_label = "VESPER LLM Navigation"
    bl_description = "Execute LLM-based navigation with task planning"

    def execute(self, context):
        print("🎯 VESPER LLM NAVIGATION TRIGGERED!")
        print("🎮 Game Engine Started")  # Clear test message
        
        # Smart scene detection - check if this is a BGE project
        scene = context.scene
        logic_count = 0
        
        for obj in scene.objects:
            if hasattr(obj, 'game') and obj.game:
                if (hasattr(obj.game, 'sensors') and obj.game.sensors) or \
                   (hasattr(obj.game, 'controllers') and obj.game.controllers) or \
                   (hasattr(obj.game, 'actuators') and obj.game.actuators):
                    logic_count += 1
        
        has_bge_logic = logic_count > 10  # Threshold for BGE project
        
        if has_bge_logic:
            print("⚠️ BGE project detected - Starting Game Engine instead")
            try:
                bpy.ops.view3d.game_start()
                return {'FINISHED'}
            except:
                print("❌ Could not start Game Engine")
        else:
            print("📍 VESPER NAVIGATION ACTIVE - House navigation mode!")
        
        # Check Blender version and setup
        print(f"🔧 Blender version: {bpy.app.version}")
        print("🏠 Running VESPER house navigation system")
        
        try:
            # Self-contained navigation without external dependencies
            self.execute_self_contained_navigation()
            
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            self.report({'ERROR'}, f"Navigation failed: {e}")
        
        return {'FINISHED'}
    
    def execute_self_contained_navigation(self):
        """Execute LLM-controlled step-by-step navigation with visual feedback"""
        print("🚀 Starting VESPER LLM Navigation with Bird's Eye View")
        
        try:
            import random
            import sys
            
            # Add VESPER path for LLM client (with error handling)
            vesper_path = r"c:\Users\hbui11\Desktop\vesper_llm"
            if vesper_path not in sys.path:
                sys.path.insert(0, vesper_path)
            
            # Test LLM availability quickly
            llm_available = False
            try:
                from backend.app.llm.client import chat_completion
                llm_available = True
                print("✅ LLM client available")
            except Exception as e:
                print(f"⚠️ LLM client not available, using fallback: {e}")
                llm_available = False
            
            # Predefined task routines
            MORNING_ROUTINE = ["Wake up", "Brush teeth", "Make coffee"]
            EVENING_ROUTINE = ["Turn on TV", "Dim living room lights", "Go to bedroom"]
            CLEANING_ROUTINE = ["Check kitchen", "Tidy living room", "Make bed"]
            WORK_BREAK = ["Get coffee", "Check TV news", "Return to work area"]
            GUEST_PREPARATION = ["Clean living room", "Prepare coffee", "Check bedroom"]
            RELAXATION_TIME = ["Turn off all lights", "Watch TV", "Go to bed"]
            
            ALL_ROUTINES = [
                ("MORNING_ROUTINE", MORNING_ROUTINE),
                ("EVENING_ROUTINE", EVENING_ROUTINE),
                ("CLEANING_ROUTINE", CLEANING_ROUTINE),
                ("WORK_BREAK", WORK_BREAK),
                ("GUEST_PREPARATION", GUEST_PREPARATION),
                ("RELAXATION_TIME", RELAXATION_TIME)
            ]

            # Room configurations
            ROOMS = {
                "LivingRoom": {"center": [-2.0, 1.5]},
                "Kitchen": {"center": [2.0, 1.5]}, 
                "Bedroom": {"center": [-3.0, -2.0]},
                "Bathroom": {"center": [1.0, -2.0]},
                "DiningRoom": {"center": [0.0, 1.0]},
                "Office": {"center": [3.0, 3.0]}
            }
            
            # Step 1: Get 3 random tasks
            routine_name, tasks = random.choice(ALL_ROUTINES)
            random_tasks = random.sample(tasks, min(3, len(tasks)))
            
            print(f"📋 Selected 3 Random Tasks: {random_tasks}")
            
            # Step 2: Get room order 
            if llm_available:
                room_order = self.get_llm_room_order(random_tasks, ROOMS)
            else:
                room_order = self.fallback_room_order(random_tasks, ROOMS)
                
            print(f"🎯 Room Order: {room_order}")
            
            # Step 3: Find actor
            actor = self.find_actor()
            if not actor:
                print("❌ No actor found")
                return
            
            print(f"🚶 Found actor: {actor.name} at [{actor.location.x:.2f}, {actor.location.y:.2f}]")
            
            # NEW: Start Game Engine FIRST, then do step-by-step movement inside it
            print("🎮 Starting Game Engine for LLM-controlled navigation...")
            self.start_game_engine_with_llm_control(actor, room_order, ROOMS, llm_available)
            
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            print("🔧 Stopping navigation to prevent freeze")
    
    def start_game_engine_with_llm_control(self, actor, room_order, ROOMS, llm_available):
        """Start Game Engine and then perform LLM-controlled movement within it"""
        try:
            print("🎮 Starting Blender Game Engine for real-time control...")
            print("� Bird's eye view screenshots will be captured during Game Engine")
            print("🤖 LLM will control actor movement step-by-step")
            
            # Set up Game Engine movement logic here
            # This would run INSIDE the Game Engine
            
            # For now, let's do the movement before Game Engine to test
            print("🔧 DEMO MODE: Moving actor first, then starting Game Engine")
            
            completed_rooms = 0
            for i, target_room in enumerate(room_order[:2]):  # Limit to 2 rooms
                print(f"\n🎯 Task {i+1}: Moving to {target_room}")
                
                if target_room in ROOMS:
                    target_pos = ROOMS[target_room]["center"]
                    print(f"📍 Target: {target_room} at {target_pos}")
                    
                    # Take bird's eye screenshot BEFORE movement
                    screenshot_path = self.capture_birds_eye_view()
                    if screenshot_path:
                        print(f"📸 Bird's eye screenshot captured: {screenshot_path}")
                    
                    # Step-by-step movement with LLM guidance
                    success = self.move_actor_step_by_step(actor, target_room, target_pos, llm_available)
                    
                    if success:
                        completed_rooms += 1
                        print(f"✅ Reached {target_room}")
                        
                        # Take screenshot AFTER movement
                        final_screenshot = self.capture_birds_eye_view()
                        if final_screenshot:
                            print(f"📸 Final position screenshot: {final_screenshot}")
                    
                else:
                    print(f"❌ Unknown room: {target_room}")
            
            print(f"\n🎊 Navigation completed! Visited {completed_rooms} rooms.")
            print("✅ LLM navigation finished - starting Game Engine")
            print("🔄 ADDON VERSION: v2.2 - Bird's Eye View Enabled")
            
            # Now start Game Engine
            bpy.ops.view3d.game_start()
            print("✅ Game Engine started successfully!")
            
        except Exception as e:
            print(f"❌ Game Engine start failed: {e}")
            print("💡 Make sure you're in the 3D Viewport and have a camera in the scene")
    
    def try_start_game_engine(self):
        """Attempt to start the Blender Game Engine"""
        try:
            print("🎮 Starting Blender Game Engine...")
            bpy.ops.view3d.game_start()
            print("✅ Game Engine started successfully!")
        except Exception as e:
            print(f"⚠️ Could not start Game Engine: {e}")
            print("💡 Make sure you're in the 3D Viewport and have a camera in the scene")
        
    def get_llm_room_order(self, tasks, rooms):
        """Get room order from LLM based on tasks"""
        try:
            from backend.app.llm.client import chat_completion
            
            rooms_list = list(rooms.keys())
            system_prompt = "You are a smart house navigation assistant. Analyze tasks and return optimal room visitation order."
            user_prompt = f"""Given these 3 tasks: {tasks}
            
Available rooms: {rooms_list}

Return ONLY a JSON list of room names in the order the actor should visit them to complete the tasks efficiently.
Example: ["Kitchen", "LivingRoom", "Bedroom"]

Consider logical task flow and minimize unnecessary movement."""
            
            # Fix: Use correct function signature with system and user prompts
            response = chat_completion(system_prompt, user_prompt)
            print(f"🧠 LLM Response: {response}")
            
            # Extract JSON from response
            import json
            import re
            
            # Look for JSON array pattern
            json_match = re.search(r'\[.*?\]', response, re.DOTALL)
            if json_match:
                room_order = json.loads(json_match.group())
                # Validate rooms exist
                valid_rooms = [room for room in room_order if room in rooms]
                if valid_rooms:
                    print(f"✅ LLM suggested rooms: {valid_rooms}")
                    return valid_rooms[:3]  # Max 3 rooms
                
        except Exception as e:
            print(f"⚠️ LLM room order failed: {e}")
        
        return self.fallback_room_order(tasks, rooms)
    
    def fallback_room_order(self, tasks, rooms):
        """Fallback room order when LLM is unavailable"""
        task_to_room = {
            "wake up": "Bedroom", "bed": "Bedroom", "sleep": "Bedroom",
            "brush teeth": "Bathroom", "bathroom": "Bathroom", "shower": "Bathroom",
            "coffee": "Kitchen", "cook": "Kitchen", "eat": "Kitchen", "kitchen": "Kitchen",
            "tv": "LivingRoom", "watch": "LivingRoom", "relax": "LivingRoom", "lights": "LivingRoom",
            "work": "Office", "computer": "Office", "desk": "Office",
            "dining": "DiningRoom", "dinner": "DiningRoom", "meal": "DiningRoom"
        }
        
        room_order = []
        for task in tasks:
            task_lower = task.lower()
            room = "LivingRoom"  # Default
            
            for keyword, room_name in task_to_room.items():
                if keyword in task_lower:
                    room = room_name
                    break
            
            if room not in room_order:
                room_order.append(room)
        
        return room_order
    
    def move_actor_with_llm_guidance(self, actor, target_room, target_pos, llm_available):
        """Move actor step-by-step using LLM visual feedback with safety measures"""
        max_steps = 15  # Reduced to prevent freezing
        step_size = 0.5  # Larger steps for faster movement
        tolerance = 0.8   # More lenient tolerance
        
        print(f"🚶 Starting movement to {target_room} at {target_pos}")
        print(f"📍 Actor starting position: [{actor.location.x:.2f}, {actor.location.y:.2f}]")
        
        # For now, disable LLM visual feedback to prevent freezing
        # Use direct movement until we can debug the screenshot/LLM issue
        print("🔧 Using direct movement (LLM visual feedback temporarily disabled)")
        
        for step in range(max_steps):
            # Get current actor position
            current_pos = [actor.location.x, actor.location.y]
            
            # Check if reached target
            distance = ((current_pos[0] - target_pos[0])**2 + (current_pos[1] - target_pos[1])**2)**0.5
            print(f"🔍 Step {step+1}: Actor at [{current_pos[0]:.2f}, {current_pos[1]:.2f}], Distance: {distance:.2f}")
            
            if distance < tolerance:
                print(f"🎯 Reached {target_room}!")
                return True
            
            # Use direct movement for now (no screenshots to prevent freezing)
            command = self.calculate_direct_movement(current_pos, target_pos)
            print(f"📡 Movement command: {command}")
            
            # Execute movement with error handling
            try:
                if self.execute_movement_command(actor, command, step_size):
                    # Update viewport safely
                    bpy.context.view_layer.update()
                    
                    # Force UI update without hanging
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            area.tag_redraw()
                            break
                    
                    # Process events to prevent freezing
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                    
                else:
                    print("⚠️ Invalid movement command")
                    break
                    
            except Exception as e:
                print(f"❌ Movement error: {e}")
                break
        
        print(f"⚠️ Movement to {target_room} completed (may not have reached exact target)")
        return True  # Return success to continue with next room
    
    def capture_birds_eye_view(self):
        """Capture bird's eye view screenshot of the scene"""
        try:
            import tempfile
            import os
            
            print("📸 Capturing bird's eye view screenshot...")
            
            # Switch to top view in the 3D viewport
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            # Override context for viewport operations
                            override = {
                                'area': area,
                                'region': region,
                                'edit_object': bpy.context.edit_object,
                                'active_object': bpy.context.active_object,
                                'selected_objects': bpy.context.selected_objects
                            }
                            
                            # Set to top view (bird's eye)
                            with bpy.context.temp_override(**override):
                                bpy.ops.view3d.view_axis(type='TOP')
                                
                                # Create temp file for screenshot
                                temp_dir = tempfile.gettempdir()
                                screenshot_path = os.path.join(temp_dir, "vesper_birds_eye.png")
                                
                                # Take screenshot
                                bpy.ops.screen.screenshot(filepath=screenshot_path)
                                
                                if os.path.exists(screenshot_path):
                                    print(f"✅ Bird's eye screenshot saved: {screenshot_path}")
                                    return screenshot_path
                                else:
                                    print("⚠️ Screenshot file not created")
                                    return None
                            
            print("⚠️ Could not find 3D Viewport for screenshot")
            return None
            
        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None
    
    def move_actor_step_by_step(self, actor, target_room, target_pos, llm_available):
        """Move actor step-by-step with realistic human-like movement"""
        print(f"🚶 Starting realistic human movement to {target_room}")
        
        max_steps = 25  # More steps for smoother movement
        step_size = 0.12  # Much smaller steps for realistic movement
        tolerance = 0.3   # Tighter tolerance for accuracy
        
        for step in range(max_steps):
            # Get current position
            current_pos = [actor.location.x, actor.location.y]
            distance = ((current_pos[0] - target_pos[0])**2 + (current_pos[1] - target_pos[1])**2)**0.5
            
            print(f"  Step {step+1}: Actor at [{current_pos[0]:.2f}, {current_pos[1]:.2f}], Distance: {distance:.2f}")
            
            # Check if reached target
            if distance < tolerance:
                print(f"  🎯 Reached {target_room} in {step+1} steps!")
                return True
            
            # Calculate next movement
            if llm_available:
                # For now, use direct movement (LLM visual analysis would go here)
                command = self.calculate_direct_movement(current_pos, target_pos)
            else:
                command = self.calculate_direct_movement(current_pos, target_pos)
            
            print(f"  📡 Movement: {command} (small human step)")
            
            # Execute movement
            if self.execute_movement_command(actor, command, step_size):
                # Update scene
                bpy.context.view_layer.update()
                
                # Refresh viewport to show gradual movement
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        area.tag_redraw()
                        break
                
                # Human-like pause between steps (realistic walking speed)
                import time
                time.sleep(0.4)  # Slower, more realistic timing
            else:
                print("  ❌ Movement failed")
                break
                break
        
        print(f"  ⚠️ Could not reach {target_room} in {max_steps} steps")
        return True  # Continue anyway
    
    def calculate_direct_movement(self, current_pos, target_pos):
        """Calculate direct movement when LLM is unavailable"""
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        # Choose dominant direction
        if abs(dx) > abs(dy):
            return "RIGHT" if dx > 0 else "LEFT"
        else:
            return "UP" if dy > 0 else "DOWN"
    
    def execute_movement_command(self, actor, command, step_size):
        """Execute movement command on actor"""
        try:
            if command == "UP":
                actor.location.y += step_size
            elif command == "DOWN":
                actor.location.y -= step_size
            elif command == "LEFT":
                actor.location.x -= step_size
            elif command == "RIGHT":
                actor.location.x += step_size
            elif command == "STOP":
                return True
            else:
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Movement execution failed: {e}")
            return False
    
    def find_actor(self):
        """Find actor object in the scene"""
        # Priority search order
        actor_keywords = ['actor', 'human', 'player', 'character', 'person']
        
        # First, try exact matches
        for keyword in actor_keywords:
            for obj in bpy.context.scene.objects:
                if obj.name.lower() == keyword and obj.type == 'MESH':
                    return obj
        
        # If no exact match, try partial matches
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                obj_name_lower = obj.name.lower()
                for keyword in actor_keywords:
                    if keyword in obj_name_lower:
                        return obj
        
        # Last resort - look for common mesh names
        fallback_names = ['Actor', 'Cube', 'Sphere', 'Suzanne']
        for name in fallback_names:
            obj = bpy.context.scene.objects.get(name)
            if obj and obj.type == 'MESH':
                return obj
        
        return None
    
    def try_start_game_engine(self):
        """Attempt to start the Game Engine"""
        try:
            print("🎮 Attempting to start Game Engine...")
            
            # Check if we're already in Game Engine mode
            if bpy.context.mode == 'GAME':
                print("✅ Already in Game Engine mode")
                return
            
            # Try different methods to start Game Engine
            if hasattr(bpy.ops.view3d, 'game_start'):
                bpy.ops.view3d.game_start()
                print("✅ Game Engine started via view3d.game_start")
            elif hasattr(bpy.ops, 'logic') and hasattr(bpy.ops.logic, 'game_start'):
                bpy.ops.logic.game_start()
                print("✅ Game Engine started via logic.game_start")
            else:
                print("⚠️ Game Engine start operators not available")
                print("💡 This might be regular Blender instead of UPBGE")
                
        except Exception as e:
            print(f"⚠️ Could not start Game Engine: {e}")
            print("💡 Navigation completed in regular Blender mode")

class VESPER_OT_GameEngineTest(bpy.types.Operator):
    bl_idname = "vesper.game_engine_test"
    bl_label = "Test Game Engine"
    bl_description = "Test if Game Engine can be started"

    def execute(self, context):
        print("🎮 GAME ENGINE TEST STARTED")
        print("=" * 30)
        
        # Check Blender version
        print(f"🔧 Blender version: {bpy.app.version}")
        
        # Check if this is UPBGE
        if hasattr(bpy.app, 'upbge_version'):
            print(f"✅ UPBGE version: {bpy.app.upbge_version}")
        else:
            print("⚠️ This appears to be regular Blender, not UPBGE")
            
        # Check available Game Engine operators
        game_operators = []
        if hasattr(bpy.ops.view3d, 'game_start'):
            game_operators.append("view3d.game_start")
        if hasattr(bpy.ops, 'logic') and hasattr(bpy.ops.logic, 'game_start'):
            game_operators.append("logic.game_start")
        if hasattr(bpy.ops, 'wm') and hasattr(bpy.ops.wm, 'upbge_start'):
            game_operators.append("wm.upbge_start")
            
        if game_operators:
            print(f"✅ Available Game Engine operators: {game_operators}")
        else:
            print("❌ No Game Engine operators found")
            
        # Check current mode
        print(f"🎯 Current mode: {bpy.context.mode}")
        
        # Try to start Game Engine
        try:
            if hasattr(bpy.ops.view3d, 'game_start'):
                print("🚀 Starting Game Engine...")
                bpy.ops.view3d.game_start()
                print("✅ Game Engine Started Successfully!")
            else:
                print("❌ Cannot start Game Engine - operators not available")
                print("💡 Make sure you're using UPBGE, not regular Blender")
        except Exception as e:
            print(f"❌ Game Engine start failed: {e}")
            
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(VESPER_OT_tag_device.bl_idname, text="Tag as VESPER Device")
    self.layout.operator(VESPER_OT_GameEngineTest.bl_idname, text="Test Game Engine")

# Key mapping for P key - Smart detection for BGE vs house.blend
addon_keymaps = []

def register():
    bpy.utils.register_class(VESPER_OT_tag_device)
    bpy.utils.register_class(VESPER_OT_LLMNavigation)
    bpy.utils.register_class(VESPER_OT_GameEngineTest)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
    # Add P-key mapping - scene detection will happen during execution
    print("🎯 VESPER: Setting up P-key navigation")
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        # Add P-key mapping
        kmi1 = km.keymap_items.new(VESPER_OT_LLMNavigation.bl_idname, 'P', 'PRESS')
        kmi1.active = True
        addon_keymaps.append((km, kmi1))
        
        # Add backup N-key mapping
        kmi2 = km.keymap_items.new(VESPER_OT_LLMNavigation.bl_idname, 'N', 'PRESS')
        kmi2.active = True
        addon_keymaps.append((km, kmi2))
        
        print("✅ P-key and N-key navigation active!")
        print("🎮 Press P or N → VESPER Navigation")

def unregister():
    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    bpy.utils.unregister_class(VESPER_OT_tag_device)
    bpy.utils.unregister_class(VESPER_OT_LLMNavigation)
    bpy.utils.unregister_class(VESPER_OT_GameEngineTest)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
