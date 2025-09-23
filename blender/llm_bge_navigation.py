import bge
import mathutils
import os
import sys
import json
import time
import re
import math
import queue
import threading

try:
    from enhanced_vlm_extensions import (
        get_enhanced_vlm_manager, 
        get_casas_subtask_manager,
        EnhancedVLMManager,
        CASASSubtaskManager
    )
    ENHANCED_VLM_AVAILABLE = True
except ImportError:
    ENHANCED_VLM_AVAILABLE = False

# MCP Integration (optional) 
try:
    from bge_mcp_integration import (
        initialize_mcp_for_bge,
        get_enhanced_context_for_navigation,
        capture_scene_images,
        get_navigation_context,
        execute_navigation_action,
        create_llm_prompt_for_task,
        execute_llm_tool_suggestion,
        check_mcp_services_status
    )
    MCP_INTEGRATION_AVAILABLE = True
except ImportError:
    MCP_INTEGRATION_AVAILABLE = False

# =============================
# VESPER Evaluation Metrics & Logging System
# =============================
class VESPERMetricsLogger:
    """Comprehensive logging and metrics tracking for VESPER navigation evaluation"""
    
    def __init__(self):
        self.session_start_time = time.time()
        self.current_task_start_time = None
        self.log_dir = os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\blender", "evaluation_logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Session log file with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"vesper_navigation_log_{timestamp}.json")
        
        # Initialize metrics tracking
        self.session_data = {
            "session_id": timestamp,
            "start_time": self.session_start_time,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_steps": 0,
            "total_screenshots": 0,
            "total_llm_calls": 0,
            "total_device_interactions": 0,  # Track virtual device interactions
            "total_subtasks_completed": 0,   # Track CASAS subtask completion
            "task_details": []
        }
        
        # Current task tracking
        self.current_task_data = None
        
        print(f"📊 VESPER: Metrics logging initialized - {self.log_file}")

    def start_task(self, task_name, task_index):
        """Log the start of a new task"""
        # Map CASAS task names to IDs for dataset compatibility
        casas_task_mapping = {
            "Make a phone call": "t1",
            "Wash hands": "t2", 
            "Cook oatmeal": "t3",
            "Eat meal": "t4",
            "Clean dishes": "t5"
        }
        
        casas_task_id = casas_task_mapping.get(task_name, f"t{task_index + 1}")
        
        self.current_task_start_time = time.time()
        self.current_task_data = {
            "task_name": task_name,
            "task_index": task_index,
            "casas_task_id": casas_task_id,
            "casas_compatible": True,
            "start_time": self.current_task_start_time,
            "start_position": None,
            "end_position": None,
            "completion_time": None,
            "steps_taken": 0,
            "screenshots_captured": 0,
            "llm_calls": 0,
            "success": False,
            "failure_reason": None,
            "movement_path": [],
            "room_detections": [],
            "vlm_responses": []
        }
        
        # Add task to session immediately so it appears in JSON
        self.session_data["task_details"].append(self.current_task_data)
        
        print(f"📋 METRICS: Starting task {task_index + 1}: '{task_name}'")
        self._log_to_file()
    
    def log_step(self, step_number, action, old_pos, new_pos, room_detected=None):
        """Log each movement step"""
        if self.current_task_data:
            self.current_task_data["steps_taken"] += 1
            self.current_task_data["movement_path"].append({
                "step": step_number,
                "action": action,
                "from_position": [round(old_pos[0], 2), round(old_pos[1], 2)],
                "to_position": [round(new_pos[0], 2), round(new_pos[1], 2)],
                "room_detected": room_detected,
                "timestamp": time.time()
            })
            
            if room_detected:
                self.current_task_data["room_detections"].append({
                    "step": step_number,
                    "room": room_detected,
                    "position": [round(new_pos[0], 2), round(new_pos[1], 2)]
                })
        
        self.session_data["total_steps"] += 1
        
        # Save session data after each step
        self._log_to_file()
        
        print(f"📊 METRICS: Step {step_number} - {action} from [{old_pos[0]:.1f}, {old_pos[1]:.1f}] to [{new_pos[0]:.1f}, {new_pos[1]:.1f}]")
        if room_detected:
            print(f"🏠 METRICS: Room detected - {room_detected}")
    
    def log_screenshot(self, screenshot_path, analysis_count):
        """Log screenshot capture and analysis"""
        if self.current_task_data:
            self.current_task_data["screenshots_captured"] += 1
        
        self.session_data["total_screenshots"] += 1
        
        # Save session data after each screenshot
        self._log_to_file()
        
        print(f"📸 METRICS: Screenshot {self.session_data['total_screenshots']} captured - Analysis #{analysis_count}")
    
    def log_llm_call(self, response_data, room_detected, furniture_visible, task_complete, response_time=None, timeout=False):
        """Log LLM/VLM response details"""
        if self.current_task_data:
            self.current_task_data["llm_calls"] += 1
            self.current_task_data["vlm_responses"].append({
                "call_number": self.current_task_data["llm_calls"],
                "room_detected": room_detected,
                "furniture_visible": furniture_visible,
                "task_complete": task_complete,
                "response_length": len(str(response_data)),
                "response_time": response_time,
                "timeout": timeout,
                "timestamp": time.time()
            })
        
        self.session_data["total_llm_calls"] += 1
        
        # Save session data after each LLM call
        self._log_to_file()
        
        timeout_msg = " (TIMEOUT)" if timeout else ""
        time_msg = f" ({response_time:.1f}s)" if response_time else ""
        print(f"🧠 METRICS: LLM Call {self.session_data['total_llm_calls']}{timeout_msg}{time_msg} - Room: {room_detected}, Task Complete: {task_complete}")
    
    def complete_task(self, success=True, failure_reason=None, final_position=None):
        """Mark current task as completed"""
        if self.current_task_data:
            completion_time = time.time() - self.current_task_start_time
            self.current_task_data["completion_time"] = completion_time
            self.current_task_data["success"] = success
            self.current_task_data["failure_reason"] = failure_reason
            self.current_task_data["end_position"] = [round(final_position[0], 2), round(final_position[1], 2)] if final_position else None
            
            # Update session totals
            if success:
                self.session_data["tasks_completed"] += 1
                print(f"✅ METRICS: Task COMPLETED in {completion_time:.1f}s with {self.current_task_data['steps_taken']} steps")
            else:
                self.session_data["tasks_failed"] += 1
                print(f"❌ METRICS: Task FAILED after {completion_time:.1f}s - {failure_reason}")
            
            # Task is already in session_data["task_details"], just reset current_task_data
            self.current_task_data = None
            
            self._log_to_file()
            self._print_task_summary()
    
    def _print_task_summary(self):
        """Print summary of current session metrics"""
        total_tasks = self.session_data["tasks_completed"] + self.session_data["tasks_failed"]
        success_rate = (self.session_data["tasks_completed"] / total_tasks * 100) if total_tasks > 0 else 0
        session_time = time.time() - self.session_start_time
        
        print("\n" + "="*60)
        print("📊 VESPER NAVIGATION METRICS SUMMARY")
        print("="*60)
        print(f"⏱️  Session Duration: {session_time:.1f}s")
        print(f"🎯 Tasks Completed: {self.session_data['tasks_completed']}/{total_tasks} ({success_rate:.1f}%)")
        print(f"👣 Total Steps: {self.session_data['total_steps']}")
        print(f"📸 Screenshots Taken: {self.session_data['total_screenshots']}")
        print(f"🧠 LLM Calls Made: {self.session_data['total_llm_calls']}")
        
        if self.session_data["task_details"]:
            avg_steps = sum(task["steps_taken"] for task in self.session_data["task_details"]) / len(self.session_data["task_details"])
            avg_time = sum(task["completion_time"] for task in self.session_data["task_details"] if task["completion_time"]) / len([t for t in self.session_data["task_details"] if t["completion_time"]])
            print(f"📈 Average Steps per Task: {avg_steps:.1f}")
            print(f"📈 Average Time per Task: {avg_time:.1f}s")
        
        print("="*60)
        print(f"💾 Full log saved to: {self.log_file}")
        print("="*60 + "\n")
    
    def _log_to_file(self):
        """Save current metrics to JSON file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ METRICS: Failed to save log file - {e}")

# Initialize global metrics logger
metrics_logger = None

def get_metrics_logger():
    """Get or create the global metrics logger"""
    global metrics_logger
    if metrics_logger is None:
        metrics_logger = VESPERMetricsLogger()
    return metrics_logger

def debug_scene_objects():
    """Debug function to list all objects in the scene"""
    try:
        scene = bge.logic.getCurrentScene()
        print("\n🔍 DEBUG: Scene Objects Analysis")
        print("=" * 40)
        
        # BGE objects is an EXP_ListValue, not a dict
        all_objects = [obj.name for obj in scene.objects]
        print(f"📊 Total objects in scene: {len(all_objects)}")
        
        # Look for potential actors
        actor_candidates = []
        camera_candidates = []
        
        for obj_name in all_objects:
            if any(keyword in obj_name.lower() for keyword in ['actor', 'player', 'character', 'main']):
                actor_candidates.append(obj_name)
            if any(keyword in obj_name.lower() for keyword in ['camera', 'cam', 'fp']):
                camera_candidates.append(obj_name)
        
        print(f"🎭 Potential actors: {actor_candidates}")
        print(f"📷 Potential cameras: {camera_candidates}")
        
        # Show first 20 objects with their positions
        print(f"📝 First 20 objects:")
        for i, obj_name in enumerate(all_objects[:20]):
            try:
                obj = scene.objects[obj_name]
                pos = obj.worldPosition
                print(f"  {i+1:2d}. {obj_name} - Pos: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
            except:
                print(f"  {i+1:2d}. {obj_name} - Position: ERROR")
        
        if len(all_objects) > 20:
            print(f"  ... and {len(all_objects) - 20} more objects")
        
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()

def reset_screenshot_counter():
    """Reset the screenshot counter to start from 001 again"""
    bge.logic.screenshot_counter = 1
    print("🔄 Screenshot counter reset to 001")

# Global variables
llm_complete_func = None
scene_running = False

def setup_python_path():
    """Setup Python path for external modules"""
    try:
        # Add current directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Add parent directory for vesper modules
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        print(f"✅ Python path configured: {current_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Python path setup failed: {e}")
        return False

def initialize_llm_client():
    """Initialize LLM client with Ollama connection"""
    global llm_complete_func
    
    try:
        # Setup Python path first
        setup_python_path()
        
        # Import VLM client from backend
        from backend.app.llm.client import chat_completion_with_vision
        
        # Create wrapper to handle multiple images
        def vlm_wrapper(prompt, images=None):
            """Wrapper to handle BGE navigation's image list format"""
            try:
                if not images or len(images) == 0:
                    print("⚠️ No images provided to VLM")
                    return None
                
                # Use the first image (first-person view) as primary
                primary_image = images[0]
                
                if len(images) > 1:
                    # If we have multiple images (FP + house plan), 
                    # for now use the first-person view and mention house plan in prompt
                    enhanced_prompt = f"{prompt}\n\nNOTE: House plan reference is also available for spatial context."
                    print(f"🔍 Using first-person image with enhanced prompt (total images: {len(images)})")
                    result = chat_completion_with_vision(enhanced_prompt, image_path=primary_image)
                else:
                    print(f"🔍 Using first-person image only")
                    result = chat_completion_with_vision(prompt, image_path=primary_image)
                
                return result
                
            except Exception as e:
                print(f"❌ VLM wrapper error: {e}")
                return None
        
        llm_complete_func = vlm_wrapper
        print("✅ LLM client initialized successfully with VLM wrapper")
        return True
        
    except Exception as e:
        print(f"❌ LLM client initialization failed: {e}")
        # Try fallback import
        try:
            from backend.app.llm.client import chat_completion
            
            # Create text-only wrapper
            def text_wrapper(prompt, images=None):
                if images and len(images) > 0:
                    print(f"⚠️ Using text-only completion (images provided: {len(images)})")
                return chat_completion("You are a helpful assistant.", prompt)
            
            llm_complete_func = text_wrapper
            print("✅ LLM client initialized with text-only fallback")
            return True
            
        except Exception as fallback_e:
            print(f"❌ Fallback LLM initialization failed: {fallback_e}")
            return False

def diagnose_camera_view():
    """Diagnose camera positioning and potential rendering issues"""
    try:
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        fp_camera = scene.objects.get("Actor_FPCamera")
        
        if not actor or not fp_camera:
            print("❌ Missing actor or camera for diagnosis")
            return
        
        # Check camera position relative to actor
        cam_pos = fp_camera.worldPosition
        actor_pos = actor.worldPosition
        distance = ((cam_pos[0] - actor_pos[0])**2 + 
                   (cam_pos[1] - actor_pos[1])**2 + 
                   (cam_pos[2] - actor_pos[2])**2)**0.5
        
        print(f"🔍 Camera Diagnosis:")
        print(f"  📍 Actor position: [{actor_pos[0]:.2f}, {actor_pos[1]:.2f}, {actor_pos[2]:.2f}]")
        print(f"  📷 Camera position: [{cam_pos[0]:.2f}, {cam_pos[1]:.2f}, {cam_pos[2]:.2f}]")
        print(f"  📏 Distance from actor: {distance:.2f}")
        print(f"  🎯 Near clipping: {getattr(fp_camera, 'near', 'unknown')}")
        print(f"  🎯 Far clipping: {getattr(fp_camera, 'far', 'unknown')}")
        
        # Check for objects very close to camera that might cause pink overlay
        nearby_objects = []
        for obj in scene.objects:
            if obj != fp_camera and hasattr(obj, 'worldPosition'):
                obj_distance = ((cam_pos[0] - obj.worldPosition[0])**2 + 
                              (cam_pos[1] - obj.worldPosition[1])**2 + 
                              (cam_pos[2] - obj.worldPosition[2])**2)**0.5
                if obj_distance < 0.5:  # Very close objects
                    nearby_objects.append((obj.name, obj_distance))
        
        if nearby_objects:
            print(f"  ⚠️ Nearby objects that might cause rendering issues:")
            for obj_name, dist in nearby_objects[:5]:  # Show top 5
                print(f"    - {obj_name}: {dist:.3f} units away")
        
    except Exception as e:
        print(f"❌ Camera diagnosis failed: {e}")

def capture_first_person_view():
    """Capture current first-person view using async approach (adapted from working backup protocol)"""
    try:
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        # Try multiple camera names to find the user's camera
        fp_camera = (scene.objects.get("Actor_FPCamera") or 
                    scene.objects.get("Camera") or 
                    scene.objects.get("FPCamera") or
                    scene.objects.get("MainCamera"))
        
        if not actor:
            print("❌ Actor not found for FP capture")
            return None
            
        if not fp_camera:
            print("❌ No camera found for FP capture (tried: Actor_FPCamera, Camera, FPCamera, MainCamera)")
            return None
        
        print(f"📸 Using camera: {fp_camera.name}")
        
        # Store original camera
        original_camera = scene.active_camera
        
        try:
            # Switch to first-person camera
            scene.active_camera = fp_camera
            
            # Use the pre-configured camera as-is - don't modify position
            print(f"✅ Using pre-configured camera '{fp_camera.name}' as-is")
            
            # Create capture directory
            captures_dir = os.path.join(os.path.dirname(__file__), "captures")
            os.makedirs(captures_dir, exist_ok=True)
            
            # Ensure the directory is writable
            if not os.access(captures_dir, os.W_OK):
                print(f"⚠️ Capture directory not writable: {captures_dir}")
                # Try using a temp directory instead
                import tempfile
                captures_dir = tempfile.gettempdir()
                print(f"🔄 Using temp directory: {captures_dir}")
            
            # Generate sequential filename (like working backup)
            existing_files = [f for f in os.listdir(captures_dir) if f.startswith("first_person_") and f.endswith(".png")]
            if existing_files:
                # Extract numbers and find max
                numbers = []
                for f in existing_files:
                    try:
                        num_str = f.replace("first_person_", "").replace(".png", "")
                        numbers.append(int(num_str))
                    except ValueError:
                        continue
                n = max(numbers) + 1 if numbers else 1
            else:
                n = 1
            
            fp_path = os.path.join(captures_dir, f"first_person_{n:03d}.png")
            
            print(f"📁 Capture directory: {captures_dir}")
            print(f"📁 Full capture path: {fp_path}")
            print(f"📁 Directory exists: {os.path.exists(captures_dir)}")
            print(f"📸 Capturing FP view from {fp_camera.name}...")
            
            # Use working screenshot method from backup
            # Screenshot capture ready
            
            # Ensure we capture from the right camera (critical step from backup)
            scene.active_camera = fp_camera
            
            # ASYNC APPROACH: Request screenshot and wait for completion (like backup)
            print("📸 Requesting screenshot...")
            result = bge.render.makeScreenshot(fp_path)
            print(f"🔍 makeScreenshot returned: {result}")
            
            # Wait for screenshot to complete (like backup polling)
            print("⏳ Waiting for screenshot to complete...")
            timeout_seconds = 5.0
            min_file_size = 1000
            start_time = time.time()
            
            while (time.time() - start_time) < timeout_seconds:
                if os.path.exists(fp_path):
                    file_size = os.path.getsize(fp_path)
                    if file_size >= min_file_size:
                        print(f"✅ FP capture successful: {os.path.basename(fp_path)} ({file_size:,} bytes)")
                        print(f"📁 Saved to: {fp_path}")
                        return fp_path
                    else:
                        print(f"⏳ Screenshot still rendering... ({file_size}/{min_file_size} bytes)")
                
                time.sleep(0.2)  # Check every 200ms
            
            # Timeout - check final state
            if os.path.exists(fp_path):
                file_size = os.path.getsize(fp_path)
                if file_size > 0:
                    print(f"⚠️ Screenshot completed but small: {file_size} bytes")
                    return fp_path
                else:
                    print(f"❌ Screenshot file empty: {file_size} bytes")
                    return None
            else:
                print("❌ FP capture failed - no file created after timeout")
                print(f"📁 Expected path: {fp_path}")
                print(f"📁 Directory contents: {os.listdir(os.path.dirname(fp_path)) if os.path.exists(os.path.dirname(fp_path)) else 'Directory does not exist'}")
                return None
                
        finally:
            # Always restore original camera
            if original_camera:
                scene.active_camera = original_camera
                
    except Exception as e:
        print(f"❌ FP capture error: {e}")
        return None

def load_house_plan():
    """Load house plan reference image"""
    house_plan_path = os.path.join(os.path.dirname(__file__), "house_layout_reference2.png")
    
    if os.path.exists(house_plan_path):
        print(f"🏠 House plan loaded: {os.path.basename(house_plan_path)}")
        return house_plan_path
    
    print("⚠️ house_layout_reference2.png not found - navigation will use FP view only")
    return None

def analyze_navigation_step(fp_image_path, house_plan_path, task, current_position):
    """Analyze navigation using first-person view (adapted from working backup protocol)"""
    try:
        global llm_complete_func
        
        if not fp_image_path or not os.path.exists(fp_image_path):
            print("❌ No first-person image available for analysis")
            return None
        
        if not llm_complete_func:
            print("❌ LLM client not available for analysis")
            return None
        
        # Build comprehensive prompt for first-person navigation (adapted from backup)
        system_prompt = """You are an expert AI navigation assistant analyzing a FIRST-PERSON view from inside a house. 
You help navigate through the house to complete daily tasks.

CRITICAL ANALYSIS REQUIREMENTS:
1. Analyze the FIRST-PERSON view to understand what you can see ahead
2. Identify rooms, furniture, objects, and pathways visible in the view
3. Determine safe movement directions (avoid walls, furniture, obstacles)
4. Consider the current task and navigate toward the appropriate room
5. Provide step-by-step navigation decisions

FIRST-PERSON VIEW CONTEXT:
- You are seeing through the actor's eyes inside the house
- Look for doors, hallways, furniture to identify current location
- Check for clear paths forward, left, or right
- Avoid moving into walls or furniture
- Navigate toward rooms appropriate for the current task

MOVEMENT OPTIONS: FORWARD, LEFT, RIGHT, BACKWARD
RESPONSE FORMAT: JSON only with navigation decision"""

        # User prompt for first-person navigation
        user_prompt = f"""CURRENT TASK: {task}

Analyze this FIRST-PERSON view and provide navigation guidance:

1. CURRENT LOCATION: What room/area are you in based on visible furniture/features?
2. VISIBLE PATHS: What directions can you move safely (no walls/furniture blocking)?
3. TASK NAVIGATION: Which direction leads toward the room needed for "{task}"?
4. MOVEMENT DECISION: Choose the best safe movement direction

RESPOND WITH JSON ONLY:
{{
    "current_room": "room_name_or_area",
    "visible_objects": ["furniture", "items", "doors"],
    "safe_directions": ["directions_with_clear_paths"],
    "task_relevant_direction": "direction_toward_task_room",
    "movement_decision": "FORWARD|LEFT|RIGHT|BACKWARD",
    "reasoning": "brief_explanation_of_decision"
}}

Base your analysis entirely on what you see in this first-person view."""
        
        # Enhanced prompt if house plan is available
        if house_plan_path and os.path.exists(house_plan_path):
            user_prompt += f"\n\nNOTE: House layout reference is available for spatial context, but prioritize what you see in the first-person view."
        
        # Call VLM analysis (adapted from backup's working method)
        print(f"🔍 Analyzing first-person view for task: '{task}'")
        
        # Use the proven VLM wrapper from initialization
        try:
            if house_plan_path and os.path.exists(house_plan_path):
                # Multi-image analysis (FP + house plan)
                images = [fp_image_path, house_plan_path]
                response = llm_complete_func(user_prompt, images)
            else:
                # Single first-person image analysis
                response = llm_complete_func(user_prompt, [fp_image_path])
            
            if not response:
                print("❌ VLM analysis returned no response")
                return None
            
            print(f"✅ VLM analysis completed")
            # debug removed
            
            # Parse JSON response (adapted from backup)
            return parse_navigation_response(response)
            
        except Exception as e:
            print(f"❌ VLM analysis failed: {e}")
            return None
        
    except Exception as e:
        print(f"❌ Navigation analysis error: {e}")
        return None

def parse_navigation_response(response):
    """Parse VLM navigation response (adapted from backup's JSON parsing)"""
    try:
        import json
        import re
        
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON directly
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                print("⚠️ No JSON found in VLM response")
                return None
        
        # Parse JSON
        try:
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['movement_decision', 'reasoning']
            for field in required_fields:
                if field not in result:
                    print(f"⚠️ Missing required field '{field}' in VLM response")
                    return None
            
            # Validate movement decision
            valid_movements = ['FORWARD', 'LEFT', 'RIGHT', 'BACKWARD']
            if result['movement_decision'] not in valid_movements:
                print(f"⚠️ Invalid movement decision: {result['movement_decision']}")
                return None
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {response[:300]}...")
            return None
        
    except Exception as e:
        print(f"❌ Response parsing error: {e}")
        return None

def parse_llm_response(response_text):
    """Legacy parse function - kept for compatibility"""
    return parse_navigation_response(response_text)

def execute_movement(action):
    """Execute movement action with collision detection and proper human-like turning"""
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find actor with multiple possible names
        actor = None
        actor_names = ["Actor", "Player", "Character", "Actor_Object", "MainCharacter"]
        
        for name in actor_names:
            if name in scene.objects:
                actor = scene.objects[name]
                print(f"✅ Found actor: {name}")
                break
        
        if not actor:
            print("❌ No actor found in scene")
            print(f"🔍 Available objects: {[obj.name for obj in scene.objects]}")
            return False
        
        # Store position before movement for logging
        old_position = [actor.worldPosition.x, actor.worldPosition.y]
        
        # Movement parameters - smaller for better VLM feedback
        MOVE_SPEED = 0.8      # Reduced for frequent VLM updates
        TURN_SPEED = 0.2      # Smaller rotation for precise control
        MOVE_FRAMES = 15      # Fewer frames for quicker movements
        
        print(f"🎮 Executing: {action.upper()}")
        print(f"📍 Actor position before: {actor.worldPosition}")
        print(f"🧭 Actor orientation before: {actor.worldOrientation.to_euler()}")
        
        # Store initial state for verification
        initial_pos = actor.worldPosition.copy()
        initial_orient = actor.worldOrientation.copy()
        
        # Check for obstacles before moving
        def check_collision_ahead(distance=2.0):
            """Check if there's an obstacle ahead using raycasting"""
            try:
                # Get forward direction
                forward_vec = actor.worldOrientation.col[1]  # Y axis is forward in Blender
                start_pos = actor.worldPosition
                end_pos = start_pos + (forward_vec * distance)
                
                # Perform raycast
                hit_obj, hit_point, hit_normal = actor.rayCast(end_pos, start_pos, distance)
                
                if hit_obj:
                    obstacle_name = hit_obj.name if hasattr(hit_obj, 'name') else str(hit_obj)
                    print(f"🚧 Obstacle detected: {obstacle_name} at distance {(hit_point - start_pos).magnitude:.2f}")
                    return True, hit_obj
                return False, None
            except Exception as e:
                print(f"⚠️ Collision check failed: {e}")
                return False, None
        
        # Execute movement based on action
        movement_success = False
        
        if action.upper() in ["UP", "FORWARD"]:
            print("🔼 Moving forward")
            
            # Check for obstacles ahead
            has_obstacle, obstacle = check_collision_ahead(MOVE_SPEED)
            
            if has_obstacle:
                print("🚧 Cannot move forward - obstacle detected!")
                print("🔄 Trying to turn to avoid obstacle...")
                # Try turning right to avoid obstacle
                for _ in range(MOVE_FRAMES // 2):
                    actor.applyRotation([0, 0, -TURN_SPEED/MOVE_FRAMES], True)
                movement_success = True
            else:
                # Safe to move forward
                for _ in range(MOVE_FRAMES):
                    actor.applyMovement([0, MOVE_SPEED/MOVE_FRAMES, 0], True)
                movement_success = True
                
        elif action.upper() in ["DOWN", "BACKWARD"]:
            print("🔽 Moving backward")
            # Backward movement - less collision checking needed
            for _ in range(MOVE_FRAMES):
                actor.applyMovement([0, -MOVE_SPEED/MOVE_FRAMES, 0], True)
            movement_success = True
                
        elif action.upper() == "LEFT":
            print("◀️ Turning left (human-like rotation)")
            # Pure rotation - no forward movement during turn
            for _ in range(MOVE_FRAMES):
                actor.applyRotation([0, 0, TURN_SPEED/MOVE_FRAMES], True)
            movement_success = True
                
        elif action.upper() == "RIGHT":
            print("▶️ Turning right (human-like rotation)")
            # Pure rotation - no forward movement during turn
            for _ in range(MOVE_FRAMES):
                actor.applyRotation([0, 0, -TURN_SPEED/MOVE_FRAMES], True)
            movement_success = True
                
        else:
            print(f"❌ Unknown action: {action}")
            return False
        
        # Wait for physics to update
        time.sleep(0.3)
        
        # Verify movement/rotation occurred
        final_pos = actor.worldPosition
        final_orient = actor.worldOrientation
        
        distance_moved = (final_pos - initial_pos).magnitude
        
        # Fix Euler orientation calculation
        try:
            initial_euler = initial_orient.to_euler()
            final_euler = final_orient.to_euler()
            orientation_changed = abs(final_euler.z - initial_euler.z)  # Focus on Z rotation for turning
        except:
            orientation_changed = 0.0
        
        print(f"📍 Actor position after: {final_pos}")
        print(f"🧭 Actor orientation after: {final_orient.to_euler()}")
        print(f"📏 Distance moved: {distance_moved:.3f} units")
        print(f"🔄 Orientation change: {orientation_changed:.3f} radians")
        
        # Log movement step for metrics
        new_position = [final_pos.x, final_pos.y]
        if hasattr(bge.logic, 'metrics_logger') and hasattr(bge.logic, 'navigation_step'):
            # Try to get current room (this would need to be enhanced with room detection)
            current_room = "UNKNOWN"  # Could be enhanced with room detection logic
            bge.logic.metrics_logger.log_step(
                bge.logic.navigation_step + 1, 
                action.upper(), 
                old_position, 
                new_position, 
                current_room
            )
        
        if movement_success:
            if action.upper() in ["LEFT", "RIGHT"]:
                print(f"✅ Rotation executed successfully: {action}")
            else:
                print(f"✅ Movement executed successfully: {action}")
            return True
        else:
            print(f"⚠️ Movement execution may have failed")
            return False
            
    except Exception as e:
        print(f"❌ Movement execution error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"❌ Movement execution failed: {e}")
        return False



def run_navigation_task(task_name, max_steps=10):
    """Run a navigation task with simplified first-person capture"""
    try:
        print(f"🎯 Starting navigation task: '{task_name}'")
        
        # Initialize system
        if not initialize_llm_client():
            print("❌ Failed to initialize LLM client")
            return False
        
        # Verify existing camera is available
        scene = bge.logic.getCurrentScene()
        fp_camera = scene.objects.get("Actor_FPCamera")
        if not fp_camera:
            # Try alternative camera names
            fp_camera = scene.objects.get("Camera") or scene.objects.get("FPCamera")
            if not fp_camera:
                print("❌ Camera not found - please ensure a camera exists in the scene")
                return False
            else:
                print(f"✅ Using existing camera: {fp_camera.name}")
        else:
            print("✅ Using existing Actor_FPCamera")
        
        # Load house plan
        house_plan_path = load_house_plan()
        
        # Navigation loop
        for step in range(max_steps):
            print(f"\n🔄 Navigation Step {step + 1}/{max_steps}")
            
            
            # Capture first-person view
            fp_image_path = capture_first_person_view()
            if not fp_image_path:
                print("❌ Failed to capture first-person view")
                continue
            
            # Get current position
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            current_position = f"({actor.worldPosition[0]:.1f}, {actor.worldPosition[1]:.1f})" if actor else "unknown"
            
            # Analyze navigation step
            result = analyze_navigation_step(fp_image_path, house_plan_path, task_name, current_position)
            if not result:
                print("❌ Failed to analyze navigation step")
                continue
            
            # Execute movement based on new response format
            action = result.get('movement_decision', '')
            if not action:
                # Fallback to old format
                action = result.get('next_action', '')
            
            if action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'UP', 'DOWN']:
                print(f"🎯 Navigation decision: {action}")
                print(f"💭 Reasoning: {result.get('reasoning', 'No reasoning provided')}")
                
                execute_movement(action)
                time.sleep(1)  # Allow movement to complete
            else:
                print(f"⚠️ Invalid action: {action}")
                print(f"📝 Full result: {result}")
                continue
            
            # Check if task is complete (basic heuristic)
            confidence = result.get('confidence', 'low')
            current_room = result.get('current_room', '')
            target_room = result.get('task_location_needed', '')
            
            if confidence == 'high' and current_room.lower() == target_room.lower():
                print(f"🎉 Task completed! Reached {current_room}")
                return True
        
        print("⏰ Maximum steps reached")
        return False
        
    except Exception as e:
        print(f"❌ Navigation task failed: {e}")
        return False

def check_bge_readiness():
    """Check if BGE is ready - simplified check"""
    try:
        scene = bge.logic.getCurrentScene()
        if not scene:
            return False
        
        # Check if we have basic scene objects
        objects = scene.objects
        if len(objects) == 0:
            return False
        
        # Basic check passed - BGE scene is loaded
        return True
        
    except Exception as e:
        print(f"🔍 BGE readiness check failed: {e}")
        return False

def wait_for_bge_initialization(max_wait_seconds=5):
    """Wait for BGE to be fully initialized - simplified approach"""
    print("⏳ Waiting for BGE to fully initialize...")
    
    # Simple fixed delay approach since BGE is actually running
    initial_delay = 3.0  # Give BGE 3 seconds to fully start up
    print(f"⏳ Initial BGE startup delay: {initial_delay} seconds...")
    time.sleep(initial_delay)
    
    # Now check if scene is available
    start_time = time.time()
    check_interval = 0.5
    
    while (time.time() - start_time) < max_wait_seconds:
        if check_bge_readiness():
            elapsed = time.time() - start_time + initial_delay
            print(f"✅ BGE ready after {elapsed:.1f} seconds")
            return True
        
        print(f"⏳ Waiting for BGE scene... ({time.time() - start_time:.1f}s)")
        time.sleep(check_interval)
    
    # Even if check fails, try to proceed anyway since BGE is running
    print(f"⚠️ BGE readiness check unclear, but proceeding since BGE is running...")
    return True

def main():
    """Main BGE navigation function - continuous task execution"""
    global scene_running
    
    # Initialize once
    if not scene_running:
        scene_running = True
        print("🚀 BGE Continuous Navigation System Starting...")
        
        # Initialize BGE state for continuous operation
        if not hasattr(bge.logic, "vesper_continuous_nav"):
            bge.logic.vesper_continuous_nav = True
            
            # CASAS-aligned ADL Task list for comparable evaluation
            bge.logic.vesper_tasks = [
                "Make a phone call",     # t1: Move to phone in dining room
                "Wash hands",            # t2: Move to kitchen sink
                "Cook oatmeal",          # t3: Cook in kitchen per directions
                "Eat meal",              # t4: Take food to dining room
                "Clean dishes"           # t5: Take dishes to sink and clean
            ]
            
            bge.logic.current_task_index = 0
            bge.logic.navigation_step = 0
            bge.logic.max_steps_per_task = 20
            bge.logic.llm_initialized = False
            bge.logic.startup_complete = False
            
            print(f"📋 Task List: {bge.logic.vesper_tasks}")
            print("🔧 Continuous navigation initialized")
        
        # BGE startup delay
        print("⏳ Waiting 3 seconds for BGE to stabilize...")
        time.sleep(3.0)
        
        # Initialize LLM
        if not bge.logic.llm_initialized:
            print("🔧 Initializing LLM client...")
            if initialize_llm_client():
                bge.logic.llm_initialized = True
                print("✅ LLM client ready")
            else:
                print("❌ LLM initialization failed")
                return False
        
        # Initialize metrics logging
        if not hasattr(bge.logic, 'metrics_logger'):
            bge.logic.metrics_logger = get_metrics_logger()
            print("📊 Metrics logging system initialized")
        
        bge.logic.startup_complete = True
        print("🎮 Starting continuous task execution...")
    
    # Run continuous navigation if startup is complete
    if hasattr(bge.logic, "startup_complete") and bge.logic.startup_complete:
        run_continuous_navigation()
    
    return True

def run_continuous_navigation():
    """Continuous navigation system that runs until all tasks are completed"""
    try:
        # Debug scene objects on first run
        if not hasattr(bge.logic, 'debug_run'):
            debug_scene_objects()
            bge.logic.debug_run = True
        
        # Check if all tasks are completed
        if bge.logic.current_task_index >= len(bge.logic.vesper_tasks):
            print("🎉 ALL TASKS COMPLETED! Navigation system finished.")
            
            # Print final metrics summary
            if hasattr(bge.logic, 'metrics_logger'):
                bge.logic.metrics_logger._print_task_summary()
            
            return
        
        # Get current task
        current_task = bge.logic.vesper_tasks[bge.logic.current_task_index]
        
        # Check if this is a new task and log it
        if not hasattr(bge.logic, 'current_task_logged') or bge.logic.current_task_logged != bge.logic.current_task_index:
            if hasattr(bge.logic, 'metrics_logger'):
                bge.logic.metrics_logger.start_task(current_task, bge.logic.current_task_index)
            bge.logic.current_task_logged = bge.logic.current_task_index
        
        # Check if current task has exceeded max steps
        if bge.logic.navigation_step >= bge.logic.max_steps_per_task:
            print(f"⏰ Task '{current_task}' exceeded max steps ({bge.logic.max_steps_per_task})")
            print("➡️ Moving to next task...")
            
            # Log task completion/failure
            if hasattr(bge.logic, 'metrics_logger'):
                scene = bge.logic.getCurrentScene()
                actor = scene.objects.get("Actor")
                final_pos = [actor.worldPosition.x, actor.worldPosition.y] if actor else None
                bge.logic.metrics_logger.complete_task(
                    success=False, 
                    failure_reason=f"Exceeded max steps ({bge.logic.max_steps_per_task})",
                    final_position=final_pos
                )
            
            bge.logic.current_task_index += 1
            bge.logic.navigation_step = 0
            time.sleep(2.0)  # Brief pause between tasks
            return
        
        # Execute navigation step for current task
        print(f"\n🎯 Task {bge.logic.current_task_index + 1}/{len(bge.logic.vesper_tasks)}: '{current_task}'")
        print(f"🔄 Step {bge.logic.navigation_step + 1}/{bge.logic.max_steps_per_task}")
        
        # Capture dual images (FP view + house layout)
        fp_image_path, house_layout_path = capture_dual_images()
        
        # Log screenshot capture
        if hasattr(bge.logic, 'metrics_logger') and fp_image_path and fp_image_path != "dummy_screenshot.png":
            bge.logic.metrics_logger.log_screenshot(fp_image_path, bge.logic.navigation_step + 1)
        
        # Always try VLM analysis first, even with dummy screenshot
        if fp_image_path == "dummy_screenshot.png":
            print("❌ Dummy screenshot detected - stopping navigation (no fallback)")
            # No position-based navigation - stop if screenshots fail
            navigation_result = None
        elif fp_image_path:
            print("� Using image-based VLM navigation")
            # Get actor position for context
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            current_position = f"({actor.worldPosition[0]:.1f}, {actor.worldPosition[1]:.1f})" if actor else "unknown"
            
            # Analyze with VLM using both images
            navigation_result = analyze_dual_image_navigation(
                fp_image_path, 
                house_layout_path, 
                current_task, 
                current_position,
                bge.logic.navigation_step
            )
        else:
            print("❌ Complete image capture failure - stopping navigation (no fallback)")
            navigation_result = None
        
        # Execute navigation decision
        if navigation_result and 'movement_decision' in navigation_result:
            action = navigation_result.get('movement_decision', '')
            reasoning = navigation_result.get('reasoning', 'No reasoning provided')
            task_complete = navigation_result.get('task_complete', False)
            
            print(f"🤖 VLM Decision: {action}")
            print(f"💭 VLM Reasoning: {reasoning}")
            
            # Log VLM response for metrics
            if hasattr(bge.logic, 'metrics_logger'):
                current_room = navigation_result.get('current_room', 'UNKNOWN')
                furniture = navigation_result.get('furniture_visible', 'None specified')
                response_time = navigation_result.get('response_time', None)
                timeout = navigation_result.get('timeout_occurred', False)
                
                bge.logic.metrics_logger.log_llm_call(
                    navigation_result,
                    current_room,
                    furniture,
                    task_complete,
                    response_time,
                    timeout
                )
            
            # Check if VLM thinks task is complete
            if task_complete:
                print(f"✅ VLM reports task '{current_task}' is COMPLETE!")
                
                # Log successful task completion
                if hasattr(bge.logic, 'metrics_logger'):
                    scene = bge.logic.getCurrentScene()
                    actor = scene.objects.get("Actor")
                    final_pos = [actor.worldPosition.x, actor.worldPosition.y] if actor else None
                    bge.logic.metrics_logger.complete_task(
                        success=True,
                        final_position=final_pos
                    )
                
                bge.logic.current_task_index += 1
                bge.logic.navigation_step = 0
                time.sleep(2.0)  # Shorter pause for faster progression
                return
            
            # Execute movement
            if action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'UP', 'DOWN']:
                success = execute_movement(action)
                if success:
                    print(f"✅ Movement executed: {action}")
                    
                    # Track movements to prevent turning loops
                    if not hasattr(bge.logic, 'recent_movements'):
                        bge.logic.recent_movements = []
                    bge.logic.recent_movements.append(action.upper())
                    
                    # Keep only last 6 movements for loop detection
                    if len(bge.logic.recent_movements) > 6:
                        bge.logic.recent_movements.pop(0)
                        
                    print(f"📝 Movement history: {bge.logic.recent_movements}")
                else:
                    print(f"❌ Movement failed: {action}")
            else:
                print(f"⚠️ Invalid VLM action: {action}")
                
        else:
            print("❌ No valid navigation result - stopping navigation (no fallback)")
            print("🛑 Navigation halted due to VLM failure")
            return
        
        if not house_layout_path:
            print("⚠️ House layout not available, using FP view only")
        
        # Get actor position for context
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        current_position = f"({actor.worldPosition[0]:.1f}, {actor.worldPosition[1]:.1f})" if actor else "unknown"
        
        # Analyze with VLM using both images
        navigation_result = analyze_dual_image_navigation(
            fp_image_path, 
            house_layout_path, 
            current_task, 
            current_position,
            bge.logic.navigation_step
        )
        
        if not navigation_result:
            print("❌ Image-based VLM failed - stopping navigation (no fallback)")
            print("🛑 Navigation halted due to VLM analysis failure")
            return
        
        # Execute VLM decision
        action = navigation_result.get('movement_decision', '')
        reasoning = navigation_result.get('reasoning', 'No reasoning provided')
        task_complete = navigation_result.get('task_complete', False)
        
        print(f"🤖 VLM Decision: {action}")
        print(f"💭 VLM Reasoning: {reasoning}")
        
        # Check if VLM thinks task is complete
        if task_complete:
            print(f"✅ VLM reports task '{current_task}' is COMPLETE!")
            bge.logic.current_task_index += 1
            bge.logic.navigation_step = 0
            time.sleep(3.0)  # Pause to appreciate completion
            return
        
        # Execute movement
        if action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'UP', 'DOWN']:
            success = execute_movement(action)
            if success:
                print(f"✅ Movement executed: {action}")
            else:
                print(f"❌ Movement failed: {action}")
        else:
            print(f"⚠️ Invalid VLM action: {action}")
        
        # Increment step and continue
        bge.logic.navigation_step += 1
        
        # BGE-STYLE TIMING: Return control to BGE render loop
        # No recursive calls - let BGE timer system handle next iteration
        print("🔄 Movement completed, yielding to BGE render cycle")
        return  # CRITICAL: Let BGE render the next frame before continuing
        
    except Exception as e:
        print(f"❌ Continuous navigation error: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(2.0)

def capture_dual_images():
    """Capture both first-person view and load house layout reference"""
    try:
        # Capture first-person screenshot
        fp_image_path = take_enhanced_screenshot()
        
        # Load house layout reference
        house_layout_path = load_house_plan()
        
        return fp_image_path, house_layout_path
        
    except Exception as e:
        print(f"❌ Dual image capture failed: {e}")
        return None, None

def take_enhanced_screenshot():
    """Simplified screenshot capture - no fallbacks"""
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find camera
        fp_camera = (scene.objects.get("Actor_FPCamera") or 
                    scene.objects.get("Camera") or 
                    scene.objects.get("FPCamera") or
                    scene.objects.get("MainCamera"))
        
        if not fp_camera:
            print("❌ No camera found")
            return None
        
        # Set active camera
        original_camera = scene.active_camera
        scene.active_camera = fp_camera
        
        try:
            # Create capture directory with absolute path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            captures_dir = os.path.join(script_dir, "captures")
            os.makedirs(captures_dir, exist_ok=True)
            
            # Initialize global screenshot counter if not exists
            if not hasattr(bge.logic, 'screenshot_counter'):
                bge.logic.screenshot_counter = 1
            
            # Use simple sequential naming: fp_view_001, fp_view_002, etc.
            filename = f"fp_view_{bge.logic.screenshot_counter:03d}.png"
            screenshot_path = os.path.join(captures_dir, filename)
            
            # Increment counter for next screenshot
            bge.logic.screenshot_counter += 1
            
            # Remove existing file if present
            if os.path.exists(screenshot_path):
                try:
                    os.remove(screenshot_path)
                except:
                    pass
            
            print(f"📸 Capturing: {filename} (#{bge.logic.screenshot_counter-1})")
            
            # BGE screenshot with frame-yield approach like backup
            result = bge.render.makeScreenshot(screenshot_path)
            
            # Add small delay to allow BGE to complete the frame render
            time.sleep(0.5)  # Brief delay for frame completion
            
            # BGE screenshots are async - return path and trust it will be created
            print(f"✅ Screenshot requested: {filename} (BGE async)")
            return screenshot_path
            
        finally:
            # Restore original camera
            if original_camera:
                scene.active_camera = original_camera
                
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        return None

# Position-based navigation removed - only image-based VLM navigation allowed

def analyze_dual_image_navigation(fp_image_path, house_layout_path, task, current_position, step_number):
    """Analyze navigation using BOTH first-person view AND house layout reference with obstacle avoidance"""
    try:
        global llm_complete_func
        
        if not fp_image_path:
            print("❌ No first-person image path provided")
            return None
        
        # Wait briefly for BGE's async screenshot to complete (like backup)
        max_wait = 2  # Maximum 2 seconds like backup
        wait_interval = 0.3  # Check every 0.3 seconds
        screenshot_ready = False
        
        for attempt in range(int(max_wait / wait_interval)):
            if os.path.exists(fp_image_path):
                try:
                    file_size = os.path.getsize(fp_image_path)
                    if file_size > 2500:  # Use backup's min_bytes (2500)
                        print(f"✅ Screenshot ready: {os.path.basename(fp_image_path)} ({file_size:,} bytes)")
                        screenshot_ready = True
                        break
                except:
                    pass
            time.sleep(wait_interval)
        
        # If current screenshot not ready, use most recent available screenshot
        if not screenshot_ready:
            print(f"⏳ Current screenshot not ready, checking for recent screenshots...")
            captures_dir = os.path.dirname(fp_image_path)
            if os.path.exists(captures_dir):
                # Find most recent fp_view screenshot
                existing_files = [f for f in os.listdir(captures_dir) if f.startswith("fp_view_") and f.endswith(".png")]
                if existing_files:
                    # Sort by filename to get most recent
                    existing_files.sort(reverse=True)
                    recent_screenshot = os.path.join(captures_dir, existing_files[0])
                    
                    # Check if we're about to use the same screenshot as last time
                    if hasattr(bge.logic, 'last_used_screenshot') and recent_screenshot == bge.logic.last_used_screenshot:
                        print(f"⚠️ Would reuse same screenshot: {os.path.basename(recent_screenshot)}")
                        print(f"🔄 Waiting longer for new screenshot...")
                        time.sleep(2.0)  # Wait longer for new screenshot
                        
                        # Check again for newer screenshots
                        existing_files = [f for f in os.listdir(captures_dir) if f.startswith("fp_view_") and f.endswith(".png")]
                        if existing_files:
                            existing_files.sort(reverse=True)
                            newer_screenshot = os.path.join(captures_dir, existing_files[0])
                            if newer_screenshot != bge.logic.last_used_screenshot:
                                recent_screenshot = newer_screenshot
                                print(f"📸 Found newer screenshot: {os.path.basename(recent_screenshot)}")
                    
                    if os.path.exists(recent_screenshot):
                        file_size = os.path.getsize(recent_screenshot)
                        if file_size > 1000:
                            print(f"📸 Using recent screenshot: {os.path.basename(recent_screenshot)} ({file_size:,} bytes)")
                            fp_image_path = recent_screenshot
                            bge.logic.last_used_screenshot = recent_screenshot  # Track usage
                            screenshot_ready = True
        
        if not screenshot_ready:
            print(f"❌ No valid screenshots available")
            return None
        
        if not llm_complete_func:
            print("❌ LLM client not available")
            return None
        
        # Track recent movements to avoid turning loops
        if not hasattr(bge.logic, 'recent_movements'):
            bge.logic.recent_movements = []
        
        # Check for excessive turning - encourage forward movement
        recent_turns = [m for m in bge.logic.recent_movements[-4:] if m in ['LEFT', 'RIGHT']]
        turn_warning = ""
        if len(recent_turns) >= 3:
            turn_warning = f"\n\n🚨 CRITICAL ANTI-LOOP WARNING: You have been turning {len(recent_turns)} times recently: {recent_turns}. You MUST try FORWARD movement if you see any clear space, doorway, or open area ahead. Stop turning and start moving forward to make progress!"
        elif len(recent_turns) >= 2:
            turn_warning = f"\n\n⚠️ MOVEMENT WARNING: Recent turns: {recent_turns}. Look for opportunities to move FORWARD instead of continuing to turn."
        
        # Enhanced prompt for spatial awareness and obstacle avoidance
        prompt = f"""You are an AI navigation assistant controlling a character in a 3D house environment. You have access to TWO CRITICAL IMAGES:

🏠 IMAGE 1 - HOUSE LAYOUT: Top-down floor plan showing the complete house structure
👁️ IMAGE 2 - FIRST-PERSON VIEW: What the character currently sees from their perspective

CURRENT MISSION: {task}
CURRENT POSITION: {current_position}
STEP: {step_number + 1}

CRITICAL NAVIGATION RULES:
🚧 OBSTACLE AVOIDANCE: 
- Do NOT walk through walls, furniture, or objects
- Look for DOORWAYS and open pathways
- If you see a wall directly ahead, you MUST turn
- Furniture blocks movement - navigate around it

🗺️ HOUSE LAYOUT KNOWLEDGE (Based on floor plan):
- **LIVING ROOM**: Large room on the left with sofas, dining table, and TV area
- **KITCHEN**: Upper center room with appliances, connected to living room
- **BEDROOM**: Lower right room with bed, connected to bathroom area  
- **BATHROOM**: Small room on the right with toilet and bathtub
- **HALLWAYS**: Connect all rooms - use these for navigation between areas

🧭 ROOM CONNECTIONS & NAVIGATION PATHS:
- From LIVING ROOM → KITCHEN: Go through the central doorway/opening  
- From LIVING ROOM → BEDROOM: Navigate through the hallway system
- From LIVING ROOM → BATHROOM: Go to bedroom area first, then bathroom
- From KITCHEN → Other rooms: Return to living room first, then navigate
- Use doorways and openings visible in the floor plan to move between rooms

📍 NAVIGATION TIPS:
- The actor typically starts in or near the LIVING ROOM area
- Look for furniture patterns to identify rooms (sofa=living room, bed=bedroom, etc.)
- Use the floor plan as your map - it shows exact room positions and connections
- Doorways appear as openings/gaps in walls on the floor plan
- If lost, navigate back to the large LIVING ROOM and reorient using the floor plan

🎯 TASK-SPECIFIC ROOM TARGETS (CASAS ADL Tasks):
- **"Make a phone call"**: Navigate to DINING ROOM to access phone and phone book
- **"Wash hands"**: Navigate to KITCHEN (sink area) or BATHROOM for hand washing
- **"Cook oatmeal"**: Navigate to KITCHEN (stove, pots, ingredients area)
- **"Eat meal"**: Navigate to DINING ROOM for eating location
- **"Clean dishes"**: Navigate to KITCHEN (sink area) for dishwashing

📋 CASAS TASK COMPLETION CRITERIA:
- **"Make a phone call"**: COMPLETE when you reach DINING ROOM and can see phone/table area
- **"Wash hands"**: COMPLETE when you reach KITCHEN sink area OR BATHROOM with visible sink
- **"Cook oatmeal"**: COMPLETE when you reach KITCHEN and can see stove/cooking area
- **"Eat meal"**: COMPLETE when you reach DINING ROOM and can see dining table/eating area  
- **"Clean dishes"**: COMPLETE when you reach KITCHEN sink area where dishes can be washed

🚨 TASK COMPLETION RULE: Set "task_complete": true ONLY when you have successfully navigated to the correct room for the current CASAS task and can see the relevant furniture/appliances.

MOVEMENT COMMANDS:
- FORWARD: Move straight ahead (only if path is clear!)
- BACKWARD: Move backward (use when stuck or need to retreat)
- LEFT: Turn body left (human-like rotation, no forward movement)
- RIGHT: Turn body right (human-like rotation, no forward movement)

DECISION PROCESS:
1. **IDENTIFY CURRENT ROOM**: Look at first-person view and match with floor plan layout
2. **LOCATE TARGET ROOM**: Find target room on floor plan (Living Room, Kitchen, Bedroom, Bathroom)
3. **PLAN ROUTE**: Trace path from current room to target using doorways shown on floor plan
4. **CHECK IMMEDIATE VIEW**: Look for obstacles, walls, furniture in first-person view
5. **EXECUTE SAFE MOVEMENT**: Choose action that progresses toward target while avoiding collisions

🚀 NAVIGATION STRATEGY (CRITICAL):
- **Use Floor Plan as GPS**: The house layout shows exactly where each room is located
- **Follow Doorway Connections**: Look for openings between rooms shown on floor plan
- **Wall Detection**: If you see a WALL directly ahead → Turn LEFT or RIGHT to find clear path
- **Forward Progress**: If you see an OPEN DOORWAY or clear space → Move FORWARD immediately
- **Room Identification**: Match what you see in first-person view with the floor plan layout
- AVOID endless turning - after 1-2 turns, you should try FORWARD
- Look for doorways, hallways, and open pathways to move through
- Don't just spin in place - FORWARD movement is essential for progress

RESPOND WITH JSON ONLY:
{{
    "current_room": "LIVING_ROOM|KITCHEN|BEDROOM|BATHROOM|DINING_ROOM|HALLWAY|UNKNOWN",
    "target_room": "LIVING_ROOM|KITCHEN|BEDROOM|BATHROOM|DINING_ROOM",
    "casas_task": "Make a phone call|Wash hands|Cook oatmeal|Eat meal|Clean dishes",
    "visible_obstacles": ["walls", "furniture", "objects_blocking_path"],
    "clear_directions": ["directions_with_open_paths_or_doorways"],
    "relevant_furniture": ["phone", "sink", "stove", "table", "counter", "etc"],
    "floor_plan_analysis": "what_you_see_on_the_floor_plan_for_navigation",
    "route_plan": "step_by_step_path_from_current_to_target_room",
    "movement_decision": "FORWARD|BACKWARD|LEFT|RIGHT",
    "reasoning": "why_this_movement_progresses_toward_target_room_safely",
    "doorway_visible": "yes|no - can_you_see_a_doorway_or_opening_ahead",
    "task_complete": false,
    "casas_completion_reason": "explanation_if_task_complete_is_true",
    "confidence": "high|medium|low"
}}

REMEMBER: After turning to avoid obstacles, you should move FORWARD when you see clear space or doorways. Don't keep turning forever!{turn_warning}"""
        
        # Prepare images for VLM
        images = [fp_image_path]
        if house_layout_path and os.path.exists(house_layout_path):
            images.append(house_layout_path)
            print(f"🔍 VLM analyzing: FP view + house layout for '{task}' (obstacle-aware)")
        else:
            print(f"🔍 VLM analyzing: FP view only for '{task}' (obstacle-aware)")
        
        # Call VLM with dual images
        response = llm_complete_func(prompt, images)
        
        if not response:
            print("❌ VLM returned no response")
            return None
        
        print("✅ VLM spatial analysis completed")
        
        # Parse VLM response
        return parse_navigation_response(response)
        
    except Exception as e:
        print(f"❌ Dual image navigation analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def take_simple_screenshot(step_number):
    """Take screenshot with simple synchronous approach"""
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find camera
        fp_camera = (scene.objects.get("Actor_FPCamera"))
        
        if not fp_camera:
            print("❌ No camera found")
            return None
        
        print(f"� Using camera: {fp_camera.name}")
        
        # Set active camera
        original_camera = scene.active_camera
        scene.active_camera = fp_camera
        
        try:
            # Create capture directory
            captures_dir = os.path.join(os.path.dirname(__file__), "captures")
            os.makedirs(captures_dir, exist_ok=True)
            
            # Use step number for filename
            screenshot_path = os.path.join(captures_dir, f"first_person_{step_number:03d}.png")
            
            print(f"📁 Screenshot path: {screenshot_path}")
            
            # Request screenshot
            print("📸 Taking screenshot...")
            result = bge.render.makeScreenshot(screenshot_path)
            print(f"🔍 makeScreenshot returned: {result}")
            
            # Wait for file with longer timeout
            timeout = 10.0
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                if os.path.exists(screenshot_path):
                    file_size = os.path.getsize(screenshot_path)
                    if file_size >= 1000:
                        print(f"✅ Screenshot ready: {os.path.basename(screenshot_path)} ({file_size:,} bytes)")
                        return screenshot_path
                    else:
                        print(f"⏳ File growing: {file_size} bytes...")
                
                time.sleep(0.5)  # Check every 500ms
            
            print("❌ Screenshot timeout")
            return None
            
        finally:
            # Restore original camera
            if original_camera:
                scene.active_camera = original_camera
                
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        return None

def run_frame_based_navigation():
    """Frame-based navigation - called every frame, doesn't block"""
    
    # Check if we've reached max steps
    if bge.logic.vesper_step >= bge.logic.vesper_max_steps:
        print("⏰ Maximum steps reached")
        return
    
    # State: Need screenshot
    if not bge.logic.vesper_screenshot_pending and not bge.logic.vesper_screenshot_path:
        print(f"\n🔄 Navigation Step {bge.logic.vesper_step + 1}/{bge.logic.vesper_max_steps}")
        print("📸 Requesting screenshot...")
        
        # Request screenshot (non-blocking)
        if request_screenshot_async():
            bge.logic.vesper_screenshot_pending = True
        
        return  # Allow frame to render
    
    # State: Screenshot pending - check if ready
    if bge.logic.vesper_screenshot_pending:
        screenshot_path = check_screenshot_ready()
        
        if screenshot_path == "TIMEOUT":
            print("❌ Screenshot timeout, retrying...")
            bge.logic.vesper_screenshot_pending = False
            return  # Retry next frame
        elif screenshot_path:
            print(f"✅ Screenshot ready: {os.path.basename(screenshot_path)}")
            bge.logic.vesper_screenshot_path = screenshot_path
            bge.logic.vesper_screenshot_pending = False
            return  # Allow frame to render before analysis
        else:
            return  # Still waiting, check next frame
    
    # State: Screenshot ready - analyze and move
    if bge.logic.vesper_screenshot_path:
        print("🔍 Analyzing navigation...")
        
        # Load house plan
        house_plan_path = load_house_plan()
        
        # Get current position
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        current_position = f"({actor.worldPosition[0]:.1f}, {actor.worldPosition[1]:.1f})" if actor else "unknown"
        
        # Analyze navigation step
        result = analyze_navigation_step(
            bge.logic.vesper_screenshot_path, 
            house_plan_path, 
            bge.logic.vesper_task, 
            current_position
        )
        
        if result:
            # Execute movement
            action = result.get('movement_decision', '')
            if action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT']:
                print(f"🎯 Movement: {action}")
                print(f"💭 Reasoning: {result.get('reasoning', 'No reasoning')}")
                execute_movement(action)
            else:
                print(f"⚠️ Invalid action: {action}")
        else:
            print("❌ Navigation analysis failed")
        
        # Reset for next step
        bge.logic.vesper_screenshot_path = None
        bge.logic.vesper_step += 1
        
        return  # Allow frame to render

def request_screenshot_async():
    """Request screenshot asynchronously (non-blocking)"""
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find camera
        fp_camera = (scene.objects.get("Actor_FPCamera"))
        
        if not fp_camera:
            print("❌ No camera found")
            return False
        
        # Set active camera
        scene.active_camera = fp_camera
        
        # Create capture directory
        captures_dir = os.path.join(os.path.dirname(__file__), "captures")
        os.makedirs(captures_dir, exist_ok=True)
        
        # Generate filename
        existing_files = [f for f in os.listdir(captures_dir) if f.startswith("first_person_") and f.endswith(".png")]
        if existing_files:
            numbers = []
            for f in existing_files:
                try:
                    num_str = f.replace("first_person_", "").replace(".png", "")
                    numbers.append(int(num_str))
                except ValueError:
                    continue
            n = max(numbers) + 1 if numbers else 1
        else:
            n = 1
        
        screenshot_path = os.path.join(captures_dir, f"first_person_{n:03d}.png")
        
        # Store screenshot info in BGE state
        if not hasattr(bge.logic, "_screenshot_state"):
            bge.logic._screenshot_state = {}
        
        bge.logic._screenshot_state = {
            "path": screenshot_path,
            "start_time": time.time(),
            "pending": True
        }
        
        # Request screenshot (async)
        result = bge.render.makeScreenshot(screenshot_path)
        print(f"📸 Screenshot requested: {os.path.basename(screenshot_path)} (result: {result})")
        
        return True
        
    except Exception as e:
        print(f"❌ Screenshot request failed: {e}")
        return False

def check_screenshot_ready():
    """Check if screenshot is ready (non-blocking polling)"""
    if not hasattr(bge.logic, "_screenshot_state"):
        return None
    
    state = bge.logic._screenshot_state
    if not state.get("pending", False):
        return None
    
    screenshot_path = state["path"]
    start_time = state["start_time"]
    
    # Check timeout (5 seconds)
    if time.time() - start_time > 5.0:
        state["pending"] = False
        return "TIMEOUT"
    
    # Check if file exists and has reasonable size
    if os.path.exists(screenshot_path):
        try:
            file_size = os.path.getsize(screenshot_path)
            if file_size >= 1000:  # Minimum file size
                state["pending"] = False
                return screenshot_path
        except Exception:
            pass
    
    return None  # Still waiting

# BGE Logic Entry Point
if __name__ == "__main__":
    main()

# Alternative entry point for BGE module mode
def bge_navigation_update():
    """Alternative entry point for continuous BGE updates"""
    return main()

# Try to set up continuous execution if we're not called every frame
try:
    # Check if we're already running frame-based
    if not hasattr(bge.logic, "vesper_continuous_setup"):
        bge.logic.vesper_continuous_setup = True
        
        # Try to set up a simple timer to call our function
        import bge.logic
        
        def continuous_navigation():
            try:
                main()
            except Exception as e:
                print(f"❌ Navigation update error: {e}")
        
        # Store the function reference for potential BGE logic brick usage
        bge.logic.vesper_main_function = continuous_navigation
        
        print("🔧 Continuous navigation setup complete")
        
except Exception as e:
    print(f"⚠️ Continuous setup failed: {e}")
    # Fallback: just run main once
    main()
