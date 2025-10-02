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

# Position Mapping Integration (NEW)
try:
    import sys
    import os
    
    # Add map directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_dir = os.path.join(os.path.dirname(current_dir), 'map')
    if map_dir not in sys.path:
        sys.path.insert(0, map_dir)
    
    from bge_integration import (
        get_navigation_mapper,
        update_actor_position_map,
        get_current_position_map,
        generate_session_summary_map
    )
    from enhanced_vlm_analysis import (
        analyze_navigation_with_position_map,
        enhanced_analyze_dual_image_navigation
    )
    POSITION_MAPPING_AVAILABLE = True
    print("✅ Position mapping system integrated")
except ImportError as e:
    POSITION_MAPPING_AVAILABLE = False
    print(f"⚠️ ï¸ Position mapping not available: {e}")

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
        
        print(f"VESPER: Metrics logging initialized - {self.log_file}")

    def start_task(self, task_name, task_index):
        """Log the start of a new task"""
        # Map CASAS task names to IDs for dataset compatibility
        # casas_task_mapping = {
        #     "Make a phone call": "t1",
        #     "Wash hands": "t2", 
        #     "Cook oatmeal": "t3",
        #     "Eat meal": "t4",
        #     "Clean dishes": "t5"
        # }
        casas_task_mapping = {
            "Go to the kitchen": "t1",
            "Go to the bedroom": "t2", 
            "Go to the livingroom": "t3"
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
        
        print(f"METRICS: Starting task {task_index + 1}: '{task_name}'")
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
        
        print(f"METRICS: Step {step_number} - {action} from [{old_pos[0]:.1f}, {old_pos[1]:.1f}] to [{new_pos[0]:.1f}, {new_pos[1]:.1f}]")
        if room_detected:
            print(f"METRICS: Room detected - {room_detected}")
    
    def log_screenshot(self, screenshot_path, analysis_count):
        """Log screenshot capture and analysis"""
        if self.current_task_data:
            self.current_task_data["screenshots_captured"] += 1
        
        self.session_data["total_screenshots"] += 1
        
        # Save session data after each screenshot
        self._log_to_file()
        
        print(f"METRICS: Screenshot {self.session_data['total_screenshots']} captured - Analysis #{analysis_count}")
    
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
        print(f"ðŸ§  METRICS: LLM Call {self.session_data['total_llm_calls']}{timeout_msg}{time_msg} - Room: {room_detected}, Task Complete: {task_complete}")
    
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
                print(f"âŒ METRICS: Task FAILED after {completion_time:.1f}s - {failure_reason}")
            
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
        print("VESPER NAVIGATION METRICS SUMMARY")
        print("="*60)
        print(f"📅  Session Duration: {session_time:.1f}s")
        print(f"🎯 Tasks Completed: {self.session_data['tasks_completed']}/{total_tasks} ({success_rate:.1f}%)")
        print(f"📊 Total Steps: {self.session_data['total_steps']}")
        print(f"📸 Screenshots Taken: {self.session_data['total_screenshots']}")
        print(f"📅 LLM Calls Made: {self.session_data['total_llm_calls']}")

        if self.session_data["task_details"]:
            avg_steps = sum(task["steps_taken"] for task in self.session_data["task_details"]) / len(self.session_data["task_details"])
            avg_time = sum(task["completion_time"] for task in self.session_data["task_details"] if task["completion_time"]) / len([t for t in self.session_data["task_details"] if t["completion_time"]])
            print(f"🧠 Average Steps per Task: {avg_steps:.1f}")
            print(f"🧠 Average Time per Task: {avg_time:.1f}s")
        
        print("="*60)
        print(f"📁 Full log saved to: {self.log_file}")
        print("="*60 + "\n")
    
    def _log_to_file(self):
        """Save current metrics to JSON file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ ï¸ METRICS: Failed to save log file - {e}")

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
        print(f"🧠 Total objects in scene: {len(all_objects)}")
        
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
        print(f"🔍 First 20 objects:")
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
        print(f"🔍 Debug error: {e}")
        import traceback
        traceback.print_exc()

def reset_screenshot_counter():
    """Reset the screenshot counter to start from 001 again"""
    bge.logic.screenshot_counter = 1
    print("📸 Screenshot counter reset to 001")

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
        print(f"🔍 Python path setup failed: {e}")
        return False

def initialize_llm_client():
    """Initialize LLM client with Open WebUI or Ollama connection"""
    global llm_complete_func
    
    try:
        # Setup Python path first
        setup_python_path()
        
        # Check and display current LLM configuration
        use_openwebui = os.getenv("USE_OPENWEBUI", "true").lower() == "true"
        openwebui_model = os.getenv("OPENWEBUI_MODEL", "OpenGVLab/InternVL3_5-30B-A3B")
        openwebui_url = os.getenv("OPENWEBUI_URL", "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions")
        
        print(f"🔧 BGE Navigation LLM Configuration:")
        if use_openwebui:
            print(f"  🚀 Using Open WebUI Server: {openwebui_url}")
            print(f"  🤖 Model: {openwebui_model}")
        else:
            print(f"  📝 Using Ollama (fallback mode)")
        
        # Import VLM client from backend
        from backend.app.llm.client import chat_completion_with_vision
        
        # Create wrapper to handle multiple images
        def vlm_wrapper(prompt, images=None):
            """Wrapper to handle BGE navigation's image list format with true dual-image support"""
            try:
                if not images or len(images) == 0:
                    print("⚠️ No images provided to VLM")
                    return None
                
                if len(images) > 1:
                    # Send both FP view and navigation map to VLM
                    print(f"🔍 Using dual-image VLM navigation (total images: {len(images)})")
                    print(f"📷 Image 1: {os.path.basename(images[0])} (FP view)")
                    print(f"📷 Image 2: {os.path.basename(images[1])} (navigation map)")
                    
                    # Enhanced prompt for dual-image analysis with highlighted rooms
                    enhanced_prompt = f"""You are analyzing TWO images for enhanced room-based navigation:

📷 IMAGE 1: First-person view from the actor's camera showing immediate surroundings, furniture, and obstacles
📷 IMAGE 2: Enhanced house layout with HIGHLIGHTED ROOM AREAS showing exact room locations and boundaries

🏠 HIGHLIGHTED ROOM NAVIGATION:
The house layout (Image 2) contains highlighted/marked areas that show:
- Exact boundaries of each room (Kitchen, Living Room, Bedroom, Bathroom)
- Clear visual separation between different rooms  
- Doorways and connections between rooms
- Your current position marker relative to room boundaries

🎯 DUAL-IMAGE ANALYSIS STRATEGY:
1. **Use Image 2 (Layout)**: Identify all highlighted room areas and locate your position relative to them
2. **Use Image 1 (First-Person)**: See immediate obstacles, furniture, and available pathways
3. **Coordinate Views**: Plan room-to-room movement using layout, execute safely using first-person view
4. **Room Recognition**: Match furniture in first-person view with appropriate highlighted room areas

{prompt}

**CRITICAL**: Use the highlighted room areas in the layout map as your primary navigation reference. They show exactly where each room is located and how to move between them efficiently."""
                    
                    result = chat_completion_with_vision(enhanced_prompt, image_paths=images)
                else:
                    # Single image (FP view only)
                    print(f"🔍 Using first-person image only")
                    result = chat_completion_with_vision(prompt, image_path=images[0])
                
                return result
                
            except Exception as e:
                print(f"🔍 VLM wrapper error: {e}")
                return None
        
        llm_complete_func = vlm_wrapper
        print("✅ LLM client initialized successfully with VLM wrapper")
        if use_openwebui:
            print(f"🎭 BGE Navigation connected to Open WebUI model: {openwebui_model}")
        return True
        
    except Exception as e:
        print(f"🔍 LLM client initialization failed: {e}")
        # Try fallback import
        try:
            from backend.app.llm.client import chat_completion
            
            # Create text-only wrapper
            def text_wrapper(prompt, images=None):
                if images and len(images) > 0:
                    print(f"⚠️Using text-only completion (images provided: {len(images)})")
                return chat_completion("You are a helpful assistant.", prompt)
            
            llm_complete_func = text_wrapper
            print("✅ LLM client initialized with text-only fallback")
            return True
            
        except Exception as fallback_e:
            print(f"🔍 Fallback LLM initialization failed: {fallback_e}")
            return False

def diagnose_camera_view():
    """Diagnose camera positioning and potential rendering issues"""
    try:
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        fp_camera = scene.objects.get("Actor_FPCamera")
        
        if not actor or not fp_camera:
            print("🔍 Missing actor or camera for diagnosis")
            return
        
        # Check camera position relative to actor
        cam_pos = fp_camera.worldPosition
        actor_pos = actor.worldPosition
        distance = ((cam_pos[0] - actor_pos[0])**2 + 
                   (cam_pos[1] - actor_pos[1])**2 + 
                   (cam_pos[2] - actor_pos[2])**2)**0.5

        print(f"🔍 Camera Diagnosis:")
        print(f"  🔍 Actor position: [{actor_pos[0]:.2f}, {actor_pos[1]:.2f}, {actor_pos[2]:.2f}]")
        print(f"  🔍 Camera position: [{cam_pos[0]:.2f}, {cam_pos[1]:.2f}, {cam_pos[2]:.2f}]")
        print(f"  🔍 Distance from actor: {distance:.2f}")
        print(f"  🔍 Near clipping: {getattr(fp_camera, 'near', 'unknown')}")
        print(f"  🔍 Far clipping: {getattr(fp_camera, 'far', 'unknown')}")

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
            print(f"  ⚠️ ï¸ Nearby objects that might cause rendering issues:")
            for obj_name, dist in nearby_objects[:5]:  # Show top 5
                print(f"    - {obj_name}: {dist:.3f} units away")
        
    except Exception as e:
        print(f"🔍 Camera diagnosis failed: {e}")

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
            print("âŒ Actor not found for FP capture")
            return None
            
        if not fp_camera:
            print("âŒ No camera found for FP capture (tried: Actor_FPCamera, Camera, FPCamera, MainCamera)")
            return None
        
        print(f"ðŸ“¸ Using camera: {fp_camera.name}")
        
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
                print(f"⚠️ ï¸ Capture directory not writable: {captures_dir}")
                # Try using a temp directory instead
                import tempfile
                captures_dir = tempfile.gettempdir()
                print(f"🔍 Using temp directory: {captures_dir}")
            
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

            print(f"🔍 Capture directory: {captures_dir}")
            print(f"🔍 Full capture path: {fp_path}")
            print(f"🔍 Directory exists: {os.path.exists(captures_dir)}")
            print(f"🔍 Capturing FP view from {fp_camera.name}...")

            # Use working screenshot method from backup
            # Screenshot capture ready
            
            # Ensure we capture from the right camera (critical step from backup)
            scene.active_camera = fp_camera
            
            # ASYNC APPROACH: Request screenshot and wait for completion (like backup)
            print("🔍 Requesting screenshot...")
            result = bge.render.makeScreenshot(fp_path)
            print(f"🔍 makeScreenshot returned: {result}")

            # Wait for screenshot to complete (like backup polling)
            print("🔍 Waiting for screenshot to complete...")
            timeout_seconds = 5.0
            min_file_size = 1000
            start_time = time.time()
            
            while (time.time() - start_time) < timeout_seconds:
                if os.path.exists(fp_path):
                    file_size = os.path.getsize(fp_path)
                    if file_size >= min_file_size:
                        print(f"✅ FP capture successful: {os.path.basename(fp_path)} ({file_size:,} bytes)")
                        print(f"🔍 Saved to: {fp_path}")
                        return fp_path
                    else:
                        print(f"🔍 Screenshot still rendering... ({file_size}/{min_file_size} bytes)")

                time.sleep(0.2)  # Check every 200ms
            
            # Timeout - check final state
            if os.path.exists(fp_path):
                file_size = os.path.getsize(fp_path)
                if file_size > 0:
                    print(f"⚠️ ï¸ Screenshot completed but small: {file_size} bytes")
                    return fp_path
                else:
                    print(f"âŒ Screenshot file empty: {file_size} bytes")
                    return None
            else:
                print("🔍 FP capture failed - no file created after timeout")
                print(f"🔍 Expected path: {fp_path}")
                print(f"🔍 Directory contents: {os.listdir(os.path.dirname(fp_path)) if os.path.exists(os.path.dirname(fp_path)) else 'Directory does not exist'}")
                return None
                
        finally:
            # Always restore original camera
            if original_camera:
                scene.active_camera = original_camera
                
    except Exception as e:
        print(f"âŒ FP capture error: {e}")
        return None

def load_house_plan():
    """Load house plan reference image"""
    house_plan_path = os.path.join(os.path.dirname(__file__), "house_layout_reference2.png")
    
    if os.path.exists(house_plan_path):
        print(f"🔍 House plan loaded: {os.path.basename(house_plan_path)}")
        return house_plan_path
    
    print("⚠️ house_layout_reference2.png not found - navigation will use FP view only")
    return None

def analyze_navigation_step(fp_image_path, house_plan_path, task, current_position):
    """Analyze navigation using first-person view (adapted from working backup protocol)"""
    try:
        global llm_complete_func
        
        if not fp_image_path or not os.path.exists(fp_image_path):
            print("âŒ No first-person image available for analysis")
            return None
        
        if not llm_complete_func:
            print("âŒ LLM client not available for analysis")
            return None
        
        # Build comprehensive prompt for first-person navigation (enhanced for highlighted room layout)
        system_prompt = """You are an expert AI navigation assistant with enhanced safety systems and HIGHLIGHTED ROOM LAYOUT analyzing navigation images.
You help navigate through the house to complete daily tasks safely and efficiently using visual room identification.

🏠 ENHANCED HOUSE LAYOUT AVAILABLE:
- Updated house_layout_reference2.png with HIGHLIGHTED ROOM AREAS
- Each room is visually marked/highlighted to show clear boundaries  
- Room positions are clearly defined with visual indicators
- Use this enhanced layout to identify exact room locations and boundaries

🔒 SAFETY SYSTEMS ACTIVE:
- Collision Detection: System will block unsafe movements into walls/obstacles
- Boundary Checking: System prevents leaving the house area  
- Room Detection: System tracks your location automatically
- Enhanced Layout: Visual room highlighting guides navigation decisions

CRITICAL ANALYSIS REQUIREMENTS:
1. Analyze the FIRST-PERSON view to understand immediate surroundings
2. Use the HIGHLIGHTED LAYOUT MAP to identify all room positions and boundaries
3. Determine safe pathways between rooms using visual room markers
4. Navigate efficiently toward the target room using highlighted areas as reference
5. If OUTSIDE the house, use the layout to find the nearest entrance

ENHANCED NAVIGATION CONTEXT:
- First-person view shows immediate obstacles, furniture, and pathways
- Highlighted layout map shows exact room locations with visual boundaries
- Coordinate both views: layout for strategy, first-person for immediate navigation
- Room boundaries are clearly marked - use them to plan accurate routes
- Trust the safety systems while focusing on room-to-room navigation

MOVEMENT OPTIONS: NORTH, SOUTH, EAST, WEST (preferred directional) or FORWARD, LEFT, RIGHT, BACKWARD (legacy)
RESPONSE FORMAT: JSON only with navigation decision"""

        # Get current room for context
        detected_room = detect_current_room(world_coords[0], world_coords[1])
        
        # Enhanced user prompt leveraging highlighted room layout
        location_status = "🏠 INSIDE HOUSE" if detected_room != "OUTSIDE" else "⚠️ OUTSIDE HOUSE"
        
        user_prompt = f"""🎯 CURRENT TASK: {task}
📍 SYSTEM DETECTED: {detected_room} {location_status}
📊 COORDINATES: ({world_coords[0]:.1f}, {world_coords[1]:.1f})

🔒 SAFETY STATUS: Collision detection and boundary checking are ACTIVE
🏠 ENHANCED LAYOUT: Highlighted room areas available for precise navigation

{"🚨 PRIORITY: You are OUTSIDE the house! Use the highlighted layout to find the nearest entrance!" if detected_room == "OUTSIDE" else ""}

Analyze BOTH images using the enhanced highlighted room layout:

🎯 **INCREMENTAL NAVIGATION - ONE STEP AT A TIME**:
This is a SINGLE MOVE decision. After you move, the map will UPDATE with your new position, then you'll make the NEXT decision.

1. **CURRENT POSITION** (from layout map): 
   - Where is the red arrow/triangle on the map?
   - Which highlighted room area are you in RIGHT NOW?
   - Which direction is the arrow pointing?

2. **TARGET ROOM** (from layout map):
   - Where is the "{task}" area/room on the highlighted layout?
   - Which highlighted area contains what you need?

3. **NEXT SINGLE STEP** (choose ONE direction):
   - What is the NEXT SINGLE MOVE to get closer to the target?
   - Will this move keep you in a valid pathway (not through walls)?
   - After this ONE move, will you be closer to the target highlighted area?

4. **FIRST-PERSON VALIDATION**:
   - Does the first-person view show a clear path in your chosen direction?
   - Are there immediate obstacles blocking this ONE move?

🔑 **KEY PRINCIPLE**: You are making ONE move, then the system will update the map with your new position. Don't plan the entire route - just the NEXT STEP toward the target room.

**MOVEMENT DISTANCE**: Each move covers approximately 0.8 units, so you may need MULTIPLE moves to:
- Cross a room
- Go through a doorway  
- Reach a distant room

📍 **NAVIGATION STRATEGY**:
1. Identify target room's highlighted area on layout map
2. Choose ONE direction that moves you closer to that highlighted area
3. Verify the path is clear in first-person view
4. Make that ONE move
5. Wait for updated map to show new position
6. Repeat until you reach the target highlighted area

1. LAYOUT ANALYSIS: Identify ALL room locations using the highlighted areas in the house layout
2. CURRENT POSITION: Where are you on the highlighted layout map? Does it match "{detected_room}"?
3. TARGET IDENTIFICATION: Locate the target room for "{task}" using the highlighted areas
4. PATHWAY PLANNING: Plan the route from current highlighted area to target highlighted area
5. IMMEDIATE NAVIGATION: Which direction moves you toward the target room boundary?

🎯 ROOM IDENTIFICATION GUIDE (use highlighted areas):
- Kitchen: Highlighted area with cooking appliances (stove, sink, counters)
- Living Room: Highlighted area with seating furniture (sofa, TV area)
- Bedroom: Highlighted area with sleeping furniture (bed, dresser)
- Bathroom: Highlighted area with bathroom fixtures (toilet, sink, shower)
- Hallways: Connecting areas between highlighted rooms

📍 NAVIGATION STRATEGY:
1. Identify your current highlighted area on the layout map
2. Locate the target room's highlighted area  
3. Plan the most direct path between highlighted areas
4. Use first-person view to navigate safely toward that path
5. Move toward room boundaries shown in highlighted areas

RESPOND WITH JSON ONLY:
{{
    "arrow_position_on_map": "describe where the red arrow is on the layout map",
    "current_highlighted_area": "which highlighted room area contains the arrow",
    "arrow_pointing_direction": "which direction (NORTH/SOUTH/EAST/WEST) is arrow facing",
    "target_highlighted_area": "which highlighted area contains the target for '{task}'",
    "distance_to_target": "far|medium|close - how far to target highlighted area",
    "next_single_move": "NORTH|SOUTH|EAST|WEST - ONE direction to move closer",
    "reasoning": "why this ONE move gets closer to the target highlighted area",
    "first_person_clear": "is the path clear in first-person view for this move",
    "task_complete": false
}}

Remember: This is ONE move only. After this move, the map updates and you decide the NEXT move."""
        
        # Enhanced prompt if house plan is available
        if house_plan_path and os.path.exists(house_plan_path):
            dual_image_prompt = """

DUAL-IMAGE ANALYSIS WITH HIGHLIGHTED ROOMS:
IMAGE 1 (First-Person): Shows immediate view - furniture, obstacles, pathways you can see right now
IMAGE 2 (Highlighted Layout): Shows house overview with HIGHLIGHTED ROOM AREAS for precise navigation

ENHANCED NAVIGATION WORKFLOW:
1. Layout Strategy: Use highlighted areas to identify where each room is located
2. Current Position: Find your position marker on the layout relative to highlighted room boundaries  
3. Target Identification: Locate the target room's highlighted area on the layout map
4. Route Planning: Plan path from your current highlighted area to target highlighted area
5. Immediate Execution: Use first-person view to navigate safely in the planned direction

Room Boundary Recognition: The highlighted areas show exact room boundaries - use these to:
- Identify which highlighted area you're currently in
- See doorways and connections between highlighted rooms
- Plan the shortest route between highlighted areas
- Navigate toward specific room boundaries

Coordinate both images: Layout map for strategic room-to-room planning, first-person view for safe immediate movement execution."""
            
            user_prompt += dual_image_prompt
        
        # Call VLM analysis (adapted from backup's working method)
        print(f"Analyzing first-person view for task: '{task}'")
        
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
                print("VLM analysis returned no response")
                return None
            
            print(f"✅ VLM analysis completed")
            # debug removed
            
            # Parse JSON response (adapted from backup)
            return parse_navigation_response(response)
            
        except Exception as e:
            print(f"âŒ VLM analysis failed: {e}")
            return None
        
    except Exception as e:
        print(f"Navigation analysis error: {e}")
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
                print("⚠️ ï¸ No JSON found in VLM response")
                return None
        
        # Parse JSON
        try:
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['movement_decision', 'reasoning']
            for field in required_fields:
                if field not in result:
                    print(f"⚠️ ï¸ Missing required field '{field}' in VLM response")
                    return None
            
            # Validate movement decision
            valid_movements = ['FORWARD', 'LEFT', 'RIGHT', 'BACKWARD', 'NORTH', 'SOUTH', 'EAST', 'WEST']
            if result['movement_decision'] not in valid_movements:
                print(f"⚠️ ï¸ Invalid movement decision: {result['movement_decision']}")
                return None
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"âŒ JSON parsing failed: {e}")
            print(f"Raw response: {response[:300]}...")
            return None
        
    except Exception as e:
        print(f"Response parsing error: {e}")
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
            print("âŒ No actor found in scene")
            print(f"ðŸ” Available objects: {[obj.name for obj in scene.objects]}")
            return False
        
        # Store position before movement for logging
        old_position = [actor.worldPosition.x, actor.worldPosition.y]
        
        # Movement parameters - smaller for better VLM feedback
        MOVE_SPEED = 0.8      # Reduced for frequent VLM updates
        TURN_SPEED = 0.2      # Smaller rotation for precise control
        MOVE_FRAMES = 15      # Fewer frames for quicker movements

        print(f"Executing: {action.upper()}")
        print(f"Actor position before: {actor.worldPosition}")
        print(f"Actor orientation before: {actor.worldOrientation.to_euler()}")

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
                    print(f"ðŸš§ Obstacle detected: {obstacle_name} at distance {(hit_point - start_pos).magnitude:.2f}")
                    return True, hit_obj
                return False, None
            except Exception as e:
                print(f"⚠️ Collision check failed: {e}")
                return False, None
        
        # Execute movement based on action
        movement_success = False
        
        if action.upper() in ["UP", "FORWARD"]:
            print("Moving forward")
            
            # Check for obstacles ahead
            has_obstacle, obstacle = check_collision_ahead(MOVE_SPEED)
            
            if has_obstacle:
                print("ðŸš§ Cannot move forward - obstacle detected!")
                print("ðŸ”„ Trying to turn to avoid obstacle...")
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
            print("Moving backward")
            # Backward movement - less collision checking needed
            for _ in range(MOVE_FRAMES):
                actor.applyMovement([0, -MOVE_SPEED/MOVE_FRAMES, 0], True)
            movement_success = True
                
        elif action.upper() == "LEFT":
            print("Turning left (human-like rotation)")
            # Pure rotation - no forward movement during turn
            for _ in range(MOVE_FRAMES):
                actor.applyRotation([0, 0, TURN_SPEED/MOVE_FRAMES], True)
            movement_success = True
                
        elif action.upper() == "RIGHT":
            print("Turning right (human-like rotation)")
            # Pure rotation - no forward movement during turn
            for _ in range(MOVE_FRAMES):
                actor.applyRotation([0, 0, -TURN_SPEED/MOVE_FRAMES], True)
            movement_success = True
                
        elif action.upper() in ["NORTH", "SOUTH", "EAST", "WEST"]:
            print(f"Executing directional movement: {action.upper()}")
            # Use the directional movement function
            success = execute_directional_movement(action.upper())
            if success:
                movement_success = True
            else:
                print(f"âŒ Directional movement failed: {action}")
                return False
                
        else:
            print(f"Unknown action: {action}")
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
        
        print(f"ðŸ“ Actor position after: {final_pos}")
        print(f"ðŸ§­ Actor orientation after: {final_orient.to_euler()}")
        print(f"ðŸ“ Distance moved: {distance_moved:.3f} units")
        print(f"ðŸ”„ Orientation change: {orientation_changed:.3f} radians")
        
        # Log movement step for metrics
        new_position = [final_pos.x, final_pos.y]
        if hasattr(bge.logic, 'metrics_logger') and hasattr(bge.logic, 'navigation_step'):
            # Get current room using position-based detection
            current_room = detect_current_room(new_position[0], new_position[1])
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
            print(f"⚠️ ï¸ Movement execution may have failed")
            return False
            
    except Exception as e:
        print(f"âŒ Movement execution error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"âŒ Movement execution failed: {e}")
        return False


def detect_current_room(x, y):
    """Detect current room based on world coordinates matching highlighted room areas
    
    Args:
        x, y: World coordinates
        
    Returns:
        str: Room name (kitchen, living_room, bedroom, bathroom, hallway, or outside)
    """
    # Room detection coordinated with highlighted areas in house_layout_reference2.png
    # These boundaries should match the highlighted room areas in your updated layout
    
    # NOTE: Adjust these coordinates to match your specific highlighted room areas
    if -6.0 <= x <= -2.0 and 2.0 <= y <= 6.0:
        return "KITCHEN"
    elif -5.0 <= x <= -2.0 and -3.0 <= y <= 2.0:
        return "LIVING_ROOM"  
    elif -2.0 <= x <= 2.0 and -3.0 <= y <= 2.0:
        return "BEDROOM"
    elif -2.0 <= x <= 2.0 and 2.0 <= y <= 6.0:
        return "BATHROOM"
    elif -3.0 <= x <= 1.0 and -4.0 <= y <= 7.0:
        return "HALLWAY"
    else:
        return "OUTSIDE"
        
    # TODO: Fine-tune these coordinates based on the actual highlighted areas
    # in your updated house_layout_reference2.png for maximum accuracy


def execute_directional_movement(direction):
    """Execute directional movement with enhanced collision detection
    
    Args:
        direction: NORTH, SOUTH, EAST, WEST
    
    Returns:
        bool: True if successful
    """
    import math
    
    try:
        print(f"\n🔍 COLLISION SYSTEM: Starting directional movement {direction}")
        print(f"🔍 COLLISION SYSTEM: Enhanced safety checks enabled")
        
        # Get actor first before using it
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if not actor:
            print("❌ No actor found")
            return False
        
        # Movement configuration
        MOVE_SPEED = 0.8      # Movement speed for collision detection
        MOVE_FRAMES = 15      # Number of frames for smooth movement
        TURN_SPEED = 1.5      # Turn speed for rotation
        
        # Debug: Check actor physics properties
        if hasattr(actor, 'mass'):
            print(f"🔍 Actor physics: mass={getattr(actor, 'mass', 'N/A')}")
        if hasattr(actor, 'physics_type'):
            print(f"🔍 Actor physics type: {getattr(actor, 'physics_type', 'UNKNOWN')}")
        
        # Debug: Check for collision-capable objects in scene
        collision_objects = [obj for obj in scene.objects if hasattr(obj, 'worldPosition') and 'wall' in obj.name.lower()]
        print(f"🔍 Found {len(collision_objects)} potential wall objects")
        
        if not actor:
            print("❌ No actor found")
            return False
        
        # Get current orientation
        current_orientation = actor.worldOrientation.to_euler().z
        
        # Define target angles for each direction (in radians)
        # BGE uses Z-axis rotation: 0 = East, π/2 = North, π = West, -π/2 or 3π/2 = South
        direction_angles = {
            'NORTH': math.pi / 2,      # 90° - facing up on map
            'SOUTH': -math.pi / 2,     # -90° or 270° - facing down on map
            'EAST': 0,                 # 0° - facing right on map
            'WEST': math.pi            # 180° - facing left on map
        }
        
        direction_upper = direction.upper()
        if direction_upper not in direction_angles:
            print(f"❌ Invalid direction: {direction}")
            return False
        
        target_angle = direction_angles[direction_upper]
        
        # Calculate angular difference
        angle_diff = target_angle - current_orientation
        
        # Normalize angle to [-π, π]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        print(f"🧭 Turning to face {direction_upper}")
        print(f"   Current: {current_orientation * 180 / math.pi:.1f}°")
        print(f"   Target: {target_angle * 180 / math.pi:.1f}°")
        print(f"   Rotation needed: {angle_diff * 180 / math.pi:.1f}°")
        
        # Turn to face the direction
        TURN_FRAMES = 20
        for _ in range(TURN_FRAMES):
            actor.applyRotation([0, 0, angle_diff / TURN_FRAMES], True)
        
        time.sleep(0.2)
        
        # Check for obstacles before moving
        def check_collision_ahead(distance=2.0):
            """Check if there's an obstacle ahead using raycasting"""
            try:
                # Get forward direction after rotation
                forward_vec = actor.worldOrientation.col[1]  # Y axis is forward in Blender
                start_pos = actor.worldPosition
                end_pos = start_pos + (forward_vec * distance)
                
                print(f"🔍 Raycast: from ({start_pos.x:.2f}, {start_pos.y:.2f}) to ({end_pos.x:.2f}, {end_pos.y:.2f})")
                
                # Try both raycast parameter orders (BGE can be inconsistent)
                hit_obj, hit_point, hit_normal = actor.rayCast(end_pos, start_pos, distance)
                
                if hit_obj and hit_obj != actor:  # Don't hit self
                    obstacle_name = hit_obj.name if hasattr(hit_obj, 'name') else str(hit_obj)
                    distance_to_hit = (hit_point - start_pos).magnitude if hit_point else distance
                    print(f"ðŸš§ Obstacle detected: {obstacle_name} at distance {distance_to_hit:.2f}")
                    return True, obstacle_name
                else:
                    print(f"✅ Path clear for {distance:.2f} units")
                    return False, None
            except Exception as e:
                print(f"⚠️ Collision check failed: {e}")
                # Fallback: assume path is blocked if raycast fails
                return True, "raycast_failed"
        
        # Check bounds before movement (prevent going too far outside house)
        current_pos = actor.worldPosition
        future_pos_x = current_pos.x
        future_pos_y = current_pos.y
        
        # Estimate future position after movement
        forward_vec = actor.worldOrientation.col[1]
        future_pos_x += forward_vec.x * MOVE_SPEED
        future_pos_y += forward_vec.y * MOVE_SPEED
        
        # Define conservative house boundaries based on starting position (-1.79, -2.07)
        HOUSE_BOUNDS = {
            'min_x': -8.0, 'max_x': 3.0,   # More restrictive X boundaries
            'min_y': -5.0, 'max_y': 8.0    # More restrictive Y boundaries  
        }
        
        if (future_pos_x < HOUSE_BOUNDS['min_x'] or future_pos_x > HOUSE_BOUNDS['max_x'] or
            future_pos_y < HOUSE_BOUNDS['min_y'] or future_pos_y > HOUSE_BOUNDS['max_y']):
            print(f"ðŸš§ Cannot move {direction_upper} - would go outside house boundaries!")
            print(f"⚠️ Current: ({current_pos.x:.1f}, {current_pos.y:.1f}), Future: ({future_pos_x:.1f}, {future_pos_y:.1f})")
            return False
        
        # Check for obstacles ahead using multiple methods
        has_obstacle, obstacle = check_collision_ahead(MOVE_SPEED)
        
        # Secondary collision check: look for nearby objects
        def check_nearby_obstacles():
            """Alternative obstacle detection using object proximity"""
            try:
                scene = bge.logic.getCurrentScene()
                current_pos = actor.worldPosition
                future_pos = current_pos + (forward_vec * MOVE_SPEED)
                
                # Check all objects in scene for proximity to future position
                for obj in scene.objects:
                    if obj != actor and hasattr(obj, 'worldPosition'):
                        obj_pos = obj.worldPosition
                        distance = (obj_pos - future_pos).magnitude
                        if distance < 1.5:  # Within 1.5 units - likely an obstacle
                            print(f"ðŸš§ Proximity obstacle: {obj.name} at distance {distance:.2f}")
                            return True, obj.name
                return False, None
            except Exception as e:
                print(f"⚠️ Proximity check failed: {e}")
                return False, None
        
        # Use both collision detection methods
        has_proximity_obstacle, prox_obstacle = check_nearby_obstacles()
        
        if has_obstacle or has_proximity_obstacle:
            obstacle_type = obstacle or prox_obstacle or "unknown"
            print(f"ðŸš§ Cannot move {direction_upper} - obstacle detected: {obstacle_type}")
            print("⚠️ Movement blocked by collision detection")
            return False
        
        # ADDITIONAL SAFETY: Check if movement would go through known wall areas
        # This is a physics-independent backup check
        def check_wall_coordinates():
            """Check if target position intersects known wall areas"""
            future_x = future_pos_x
            future_y = future_pos_y
            
            # Define known wall/obstacle areas based on house layout
            # These should be adjusted based on your specific house design
            wall_areas = [
                # Example wall areas - adjust these coordinates based on your house layout
                {'min_x': -6, 'max_x': -4, 'min_y': 3, 'max_y': 5},  # Potential kitchen wall
                {'min_x': -3, 'max_x': -1, 'min_y': 0, 'max_y': 2},   # Potential interior wall
                # Add more wall areas as needed
            ]
            
            for wall in wall_areas:
                if (wall['min_x'] <= future_x <= wall['max_x'] and 
                    wall['min_y'] <= future_y <= wall['max_y']):
                    print(f"🚧 Coordinate-based wall detection: would intersect wall area")
                    print(f"   Target: ({future_x:.1f}, {future_y:.1f})")
                    print(f"   Wall: X[{wall['min_x']}, {wall['max_x']}], Y[{wall['min_y']}, {wall['max_y']}]")
                    return True
            return False
        
        # Apply coordinate-based wall checking as final safety measure
        if check_wall_coordinates():
            print(f"ðŸš§ Cannot move {direction_upper} - coordinate-based wall detection")
            print("⚠️ Movement blocked by geometric constraint")
            return False
        
        # Now move forward with collision-aware movement
        print(f"➡️ Moving FORWARD (towards {direction_upper}) with collision detection")
        
        # Store initial position for collision detection
        initial_position = actor.worldPosition.copy()
        
        # Adaptive movement - slower if we were close to obstacles
        movement_multiplier = 1.0
        if has_proximity_obstacle:
            movement_multiplier = 0.5  # Move slower if proximity obstacles detected
            print("⚠️ Using reduced movement speed due to proximity obstacles")
        
        adjusted_move_speed = MOVE_SPEED * movement_multiplier
        
        # Move with collision detection enabled (local=False for world coordinates)
        movement_per_frame = adjusted_move_speed / MOVE_FRAMES
        successful_frames = 0
        
        for frame in range(MOVE_FRAMES):
            pos_before = actor.worldPosition.copy()
            
            # Apply movement with collision detection
            actor.applyMovement([0, movement_per_frame, 0], False)  # False = world coordinates
            
            pos_after = actor.worldPosition.copy()
            movement_distance = (pos_after - pos_before).magnitude
            
            # Check if we actually moved (collision would prevent movement)
            if movement_distance < movement_per_frame * 0.1:  # Less than 10% expected movement
                print(f"🚧 Collision detected at frame {frame} - movement blocked")
                print(f"   Expected: {movement_per_frame:.3f}, Actual: {movement_distance:.3f}")
                break
            else:
                successful_frames += 1
        
        time.sleep(0.3)
        
        # Check if movement was successful
        total_movement = (actor.worldPosition - initial_position).magnitude
        expected_movement = adjusted_move_speed
        
        if total_movement < expected_movement * 0.3:  # Less than 30% of expected movement
            print(f"⚠️ Movement mostly blocked by collision")
            print(f"   Expected: {expected_movement:.2f}, Actual: {total_movement:.2f}")
        else:
            print(f"✅ Movement completed: {total_movement:.2f} units ({successful_frames}/{MOVE_FRAMES} frames)")
        
        # Verify final position
        final_pos = actor.worldPosition
        final_orientation = actor.worldOrientation.to_euler().z
        
        # Validate the movement was successful and within bounds
        if (final_pos.x < HOUSE_BOUNDS['min_x'] or final_pos.x > HOUSE_BOUNDS['max_x'] or
            final_pos.y < HOUSE_BOUNDS['min_y'] or final_pos.y > HOUSE_BOUNDS['max_y']):
            print(f"⚠️ Movement resulted in out-of-bounds position!")
            print(f"   Position: ({final_pos.x:.2f}, {final_pos.y:.2f})")
            print(f"   Bounds: X[{HOUSE_BOUNDS['min_x']}, {HOUSE_BOUNDS['max_x']}], Y[{HOUSE_BOUNDS['min_y']}, {HOUSE_BOUNDS['max_y']}]")
            # Don't return False here, just log the warning
        
        print(f"✅ Moved to {direction_upper}")
        print(f"   Final position: ({final_pos.x:.2f}, {final_pos.y:.2f})")
        print(f"   Final orientation: {final_orientation * 180 / math.pi:.1f}°")
        
        return True
        
    except Exception as e:
        print(f"❌ Directional movement failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_navigation_task(task_name, max_steps=10):
    """Run a navigation task with simplified first-person capture"""
    try:
        print(f"ðŸŽ¯ Starting navigation task: '{task_name}'")
        
        # Initialize system
        if not initialize_llm_client():
            print("âŒ Failed to initialize LLM client")
            return False
        
        # Verify existing camera is available
        scene = bge.logic.getCurrentScene()
        fp_camera = scene.objects.get("Actor_FPCamera")
        if not fp_camera:
            # Try alternative camera names
            fp_camera = scene.objects.get("Camera") or scene.objects.get("FPCamera")
            if not fp_camera:
                print("âŒ Camera not found - please ensure a camera exists in the scene")
                return False
            else:
                print(f"✅ Using existing camera: {fp_camera.name}")
        else:
            print("✅ Using existing Actor_FPCamera")
        
        # Load house plan
        house_plan_path = load_house_plan()
        
        # Navigation loop
        for step in range(max_steps):
            print(f"\nðŸ”„ Navigation Step {step + 1}/{max_steps}")
            
            
            # Capture first-person view
            fp_image_path = capture_first_person_view()
            if not fp_image_path:
                print("âŒ Failed to capture first-person view")
                continue
            
            # Get current position
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            current_position = f"({actor.worldPosition[0]:.1f}, {actor.worldPosition[1]:.1f})" if actor else "unknown"
            
            # Analyze navigation step
            result = analyze_navigation_step(fp_image_path, house_plan_path, task_name, current_position)
            if not result:
                print("âŒ Failed to analyze navigation step")
                continue
            
            # Execute movement based on new response format
            action = result.get('movement_decision', '')
            if not action:
                # Fallback to old format
                action = result.get('next_action', '')
            
            if action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'NORTH', 'SOUTH', 'EAST', 'WEST']:
                print(f"ðŸŽ¯ Navigation decision: {action}")
                print(f"ðŸ’­ Reasoning: {result.get('reasoning', 'No reasoning provided')}")
                
                execute_movement(action)
                time.sleep(1)  # Allow movement to complete
            else:
                print(f"⚠️ ï¸ Invalid action: {action}")
                print(f"ðŸ“ Full result: {result}")
                continue
            
            # Check if task is complete (basic heuristic)
            confidence = result.get('confidence', 'low')
            current_room = result.get('current_room', '')
            target_room = result.get('task_location_needed', '')
            
            if confidence == 'high' and current_room.lower() == target_room.lower():
                print(f"ðŸŽ‰ Task completed! Reached {current_room}")
                return True
        
        print("â° Maximum steps reached")
        return False
        
    except Exception as e:
        print(f"âŒ Navigation task failed: {e}")
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
        print(f"ðŸ” BGE readiness check failed: {e}")
        return False

def wait_for_bge_initialization(max_wait_seconds=5):
    """Wait for BGE to be fully initialized - simplified approach"""
    print("â³ Waiting for BGE to fully initialize...")
    
    # Simple fixed delay approach since BGE is actually running
    initial_delay = 3.0  # Give BGE 3 seconds to fully start up
    print(f"â³ Initial BGE startup delay: {initial_delay} seconds...")
    time.sleep(initial_delay)
    
    # Now check if scene is available
    start_time = time.time()
    check_interval = 0.5
    
    while (time.time() - start_time) < max_wait_seconds:
        if check_bge_readiness():
            elapsed = time.time() - start_time + initial_delay
            print(f"✅ BGE ready after {elapsed:.1f} seconds")
            return True
        
        print(f"â³ Waiting for BGE scene... ({time.time() - start_time:.1f}s)")
        time.sleep(check_interval)
    
    # Even if check fails, try to proceed anyway since BGE is running
    print(f"⚠️ ï¸ BGE readiness check unclear, but proceeding since BGE is running...")
    return True

def main():
    """Main BGE navigation function - continuous task execution"""
    global scene_running
    
    # Initialize once
    if not scene_running:
        scene_running = True
        print("ðŸš€ BGE Continuous Navigation System Starting...")
        
        # Initialize BGE state for continuous operation
        if not hasattr(bge.logic, "vesper_continuous_nav"):
            bge.logic.vesper_continuous_nav = True
            
            # CASAS-aligned ADL Task list for comparable evaluation
            # bge.logic.vesper_tasks = [
            #     "Make a phone call",     # t1: Move to phone in dining room
            #     "Wash hands",            # t2: Move to kitchen sink
            #     "Cook oatmeal",          # t3: Cook in kitchen per directions
            #     "Eat meal",              # t4: Take food to dining room
            #     "Clean dishes"           # t5: Take dishes to sink and clean
            # ]
            bge.logic.vesper_tasks = [
                "Go to the kitchen",     # t1: Navigate to kitchen
                "Go to the bedroom",     # t2: Navigate to bedroom  
                "Go to the livingroom"   # t3: Navigate to living room
            ]
            
            bge.logic.current_task_index = 0
            bge.logic.navigation_step = 0
            bge.logic.max_steps_per_task = 20
            bge.logic.llm_initialized = False
            bge.logic.startup_complete = False
            
            print(f"ðŸ“‹ Task List: {bge.logic.vesper_tasks}")
            print("ðŸ”§ Continuous navigation initialized")
        
        # BGE startup delay
        print("â³ Waiting 3 seconds for BGE to stabilize...")
        time.sleep(3.0)
        
        # Initialize LLM
        if not bge.logic.llm_initialized:
            print("ðŸ”§ Initializing LLM client...")
            if initialize_llm_client():
                bge.logic.llm_initialized = True
                print("✅ LLM client ready")
            else:
                print("âŒ LLM initialization failed")
                return False
        
        # Initialize metrics logging
        if not hasattr(bge.logic, 'metrics_logger'):
            bge.logic.metrics_logger = get_metrics_logger()
            print("ðŸ“Š Metrics logging system initialized")
        
        bge.logic.startup_complete = True
        print("ðŸŽ® Starting continuous task execution...")
    
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
            print("ðŸŽ‰ ALL TASKS COMPLETED! Navigation system finished.")
            
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
            print(f"â° Task '{current_task}' exceeded max steps ({bge.logic.max_steps_per_task})")
            print("âž¡ï¸ Moving to next task...")
            
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
        print(f"\nðŸŽ¯ Task {bge.logic.current_task_index + 1}/{len(bge.logic.vesper_tasks)}: '{current_task}'")
        print(f"ðŸ”„ Step {bge.logic.navigation_step + 1}/{bge.logic.max_steps_per_task}")
        
        # Capture dual images (FP view + most recent navigation context map)
        fp_image_path, house_layout_path = capture_dual_images()
        
        # Log screenshot capture
        if hasattr(bge.logic, 'metrics_logger') and fp_image_path and fp_image_path != "dummy_screenshot.png":
            bge.logic.metrics_logger.log_screenshot(fp_image_path, bge.logic.navigation_step + 1)
        
        # Always try VLM analysis first, even with dummy screenshot
        if fp_image_path == "dummy_screenshot.png":
            print("âŒ Dummy screenshot detected - stopping navigation (no fallback)")
            # No position-based navigation - stop if screenshots fail
            navigation_result = None
        elif fp_image_path:
            print("🖼️ Using image-based VLM navigation")
            # Get actor position for context
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            current_position = f"({actor.worldPosition[0]:.1f}, {actor.worldPosition[1]:.1f})" if actor else "unknown"
            
            world_coords = (actor.worldPosition[0], actor.worldPosition[1]) if actor else (0, 0)
            
            # Use standard dual-image analysis (enhanced analysis temporarily disabled)
            navigation_result = None
            if False and POSITION_MAPPING_AVAILABLE and actor:  # Temporarily disabled
                print("ðŸ—ºï¸ Using enhanced position-aware navigation analysis")
                print(f"📍 FP Image: {os.path.basename(fp_image_path) if fp_image_path else 'None'}")
                print(f"🗺️ Map Image: {os.path.basename(house_layout_path) if house_layout_path else 'None'}")
                
                # Extract previously detected room for mapping
                previous_room = None
                if hasattr(bge.logic, 'last_detected_room'):
                    previous_room = bge.logic.last_detected_room
                
                navigation_result = enhanced_analyze_dual_image_navigation(
                    fp_image_path,
                    house_layout_path, 
                    current_task,
                    current_position,
                    bge.logic.navigation_step,
                    world_coords=world_coords,
                    room_detected=previous_room,
                    llm_func=llm_complete_func
                )
                
                # Store detected room for next iteration
                if navigation_result and 'current_room' in navigation_result:
                    bge.logic.last_detected_room = navigation_result['current_room']
            
            # Use standard dual-image analysis 
            if not navigation_result:
                print("🖼️ Using standard dual-image navigation analysis")
                print(f"📍 FP Image: {os.path.basename(fp_image_path) if fp_image_path else 'None'}")
                print(f"🗺️ Map Image: {os.path.basename(house_layout_path) if house_layout_path else 'None'}")
                navigation_result = analyze_dual_image_navigation(
                    fp_image_path, 
                    house_layout_path, 
                    current_task, 
                    current_position,
                    bge.logic.navigation_step
                )
        else:
            print("âŒ Complete image capture failure - stopping navigation (no fallback)")
            navigation_result = None
        
        # Execute navigation decision
        if navigation_result and 'movement_decision' in navigation_result:
            action = navigation_result.get('movement_decision', '')
            reasoning = navigation_result.get('reasoning', 'No reasoning provided')
            task_complete = navigation_result.get('task_complete', False)
            
            print(f"ðŸ¤– VLM Decision: {action}")
            print(f"ðŸ’­ VLM Reasoning: {reasoning}")
            
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
            if action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'NORTH', 'SOUTH', 'EAST', 'WEST']:
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
                        
                    print(f"ðŸ“ Movement history: {bge.logic.recent_movements}")
                else:
                    print(f"âŒ Movement failed: {action}")
            else:
                print(f"⚠️ ï¸ Invalid VLM action: {action}")
                
        else:
            print("âŒ No valid navigation result - stopping navigation (no fallback)")
            print("ðŸ›‘ Navigation halted due to VLM failure")
            return
        
        # Navigation result already obtained from VLM analysis above
        
        # Execute VLM decision
        action = navigation_result.get('movement_decision', '')
        reasoning = navigation_result.get('reasoning', 'No reasoning provided')
        task_complete = navigation_result.get('task_complete', False)
        
        print(f"ðŸ¤– VLM Decision: {action}")
        print(f"ðŸ’­ VLM Reasoning: {reasoning}")
        
        # Check if VLM thinks task is complete
        if task_complete:
            print(f"✅ VLM reports task '{current_task}' is COMPLETE!")
            bge.logic.current_task_index += 1
            bge.logic.navigation_step = 0
            time.sleep(3.0)  # Pause to appreciate completion
            return
        
        # Execute movement
        if action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'NORTH', 'SOUTH', 'EAST', 'WEST']:
            success = execute_movement(action)
            if success:
                print(f"✅ Movement executed: {action}")
            else:
                print(f"âŒ Movement failed: {action}")
        else:
            print(f"⚠️ ï¸ Invalid VLM action: {action}")
        
        # Increment step and continue
        bge.logic.navigation_step += 1
        
        # BGE-STYLE TIMING: Return control to BGE render loop
        # No recursive calls - let BGE timer system handle next iteration
        print("ðŸ”„ Movement completed, yielding to BGE render cycle")
        return  # CRITICAL: Let BGE render the next frame before continuing
        
    except Exception as e:
        print(f"âŒ Continuous navigation error: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(2.0)

def capture_dual_images():
    """Capture both first-person view and generate navigation context map with actor position"""
    try:
        # Capture first-person screenshot
        fp_image_path = take_enhanced_screenshot()
        
        # Generate navigation context map with actor position using position mapper
        map_context_path = None
        
        # Try position mapper to generate map with actor position marked
        if POSITION_MAPPING_AVAILABLE:
            try:
                # Get current actor position for map generation
                scene = bge.logic.getCurrentScene()
                actor = scene.objects.get("Actor")
                if actor:
                    # Extract individual coordinates
                    world_x = actor.worldPosition.x
                    world_y = actor.worldPosition.y
                    
                    # Get actor orientation (Z-axis rotation)
                    orientation = actor.worldOrientation.to_euler().z
                    
                    # Get current task info for context
                    current_task = getattr(bge.logic, 'current_task', 'Navigate')
                    current_room = getattr(bge.logic, 'current_room', None)
                    
                    orientation_deg = orientation * (180 / 3.14159)
                    print(f"🗺️ Generating position map for Actor at ({world_x:.2f}, {world_y:.2f}), facing {orientation_deg:.1f}°")
                    print(f"🎯 Task: {current_task}, Room: {current_room}")
                    
                    # Update position map and generate context with actor marker
                    map_context_path = update_actor_position_map(
                        world_x, world_y, 
                        room=current_room, 
                        task=current_task,
                        orientation=orientation
                    )
                    
                    if map_context_path and os.path.exists(map_context_path):
                        print(f"✅ Generated navigation map: {os.path.basename(map_context_path)}")
                    else:
                        print(f"⚠️ Position mapper returned: {map_context_path}")
                        map_context_path = None
                else:
                    print("⚠️ No Actor found for position mapping")
            except Exception as e:
                print(f"⚠️ Position mapper generation failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback: Use static house layout if position map generation failed
        if not map_context_path:
            map_context_path = load_house_plan()
            print("🔍 Using static house layout as fallback")
        
        return fp_image_path, map_context_path
        
    except Exception as e:
        print(f"❌ Dual image capture failed: {e}")
        return None, None

def get_most_recent_navigation_map():
    """Get the most recent navigation context map generated by the position mapper"""
    try:
        import os
        
        # Look for navigation context maps in the map output directory
        map_output_dir = r"C:\Users\hbui11\Desktop\vesper_llm\map\generated_maps"
        
        if not os.path.exists(map_output_dir):
            print(f"⚠️ Map output directory not found: {map_output_dir}")
            return None
        
        # Find all navigation context maps (both numbered and timestamped)
        context_maps = []
        numbered_maps = []
        
        for filename in os.listdir(map_output_dir):
            if filename.startswith("navigation_context_") and filename.endswith(".png"):
                filepath = os.path.join(map_output_dir, filename)
                
                # Check if it's a numbered map (navigation_context_001.png)
                try:
                    number_part = filename.replace("navigation_context_", "").replace(".png", "")
                    if number_part.isdigit():
                        numbered_maps.append((filepath, int(number_part)))
                    else:
                        # Timestamped map - use modification time
                        context_maps.append((filepath, os.path.getmtime(filepath)))
                except:
                    # Fallback to modification time
                    context_maps.append((filepath, os.path.getmtime(filepath)))
        
        # Prefer numbered maps (return highest number), fallback to timestamped maps
        if numbered_maps:
            most_recent_map = max(numbered_maps, key=lambda x: x[1])[0]
            print(f"🎯 Found most recent numbered navigation map: {os.path.basename(most_recent_map)}")
            return most_recent_map
        elif context_maps:
            most_recent_map = max(context_maps, key=lambda x: x[1])[0]
            print(f"🎯 Found most recent timestamped navigation map: {os.path.basename(most_recent_map)}")
            return most_recent_map
        else:
            print("📍 No navigation context maps found")
            return None
        
    except Exception as e:
        print(f"❌ Failed to get navigation map: {e}")
        return None

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
            print("âŒ No camera found")
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
            # PRESERVE ALL SCREENSHOTS: No cleanup - keeping complete visual history
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
            
            print(f"ðŸ“¸ Capturing: {filename} (#{bge.logic.screenshot_counter-1})")
            
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
        print(f"âŒ Screenshot error: {e}")
        return None

# Position-based navigation removed - only image-based VLM navigation allowed

def analyze_dual_image_navigation(fp_image_path, house_layout_path, task, current_position, step_number):
    """Analyze navigation using BOTH first-person view AND house layout reference with obstacle avoidance"""
    try:
        global llm_complete_func
        
        if not fp_image_path:
            print("âŒ No first-person image path provided")
            return None
        
        # Wait briefly for BGE's async screenshot to complete
        max_wait = 3  # Maximum 3 seconds (increased for reliability)
        wait_interval = 0.5  # Check every 0.5 seconds
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
            print(f"â³ Current screenshot not ready, checking for recent screenshots...")
            captures_dir = os.path.dirname(fp_image_path)
            if os.path.exists(captures_dir):
                # Find most recent fp_view screenshot
                existing_files = [f for f in os.listdir(captures_dir) if f.startswith("fp_view_") and f.endswith(".png")]
                if existing_files:
                    # Sort by file modification time (most recent first)
                    existing_files_with_time = [(f, os.path.getmtime(os.path.join(captures_dir, f))) for f in existing_files]
                    existing_files_with_time.sort(key=lambda x: x[1], reverse=True)
                    recent_screenshot = os.path.join(captures_dir, existing_files_with_time[0][0])
                    
                    # Check if we're about to use the same screenshot as last time
                    if hasattr(bge.logic, 'last_used_screenshot') and recent_screenshot == bge.logic.last_used_screenshot:
                        print(f"⚠️ ï¸ Would reuse same screenshot: {os.path.basename(recent_screenshot)}")
                        print(f"ðŸ”„ Waiting longer for new screenshot...")
                        time.sleep(2.0)  # Wait longer for new screenshot
                        
                        # Check again for newer screenshots
                        existing_files = [f for f in os.listdir(captures_dir) if f.startswith("fp_view_") and f.endswith(".png")]
                        if existing_files:
                            existing_files_with_time = [(f, os.path.getmtime(os.path.join(captures_dir, f))) for f in existing_files]
                            existing_files_with_time.sort(key=lambda x: x[1], reverse=True)
                            newer_screenshot = os.path.join(captures_dir, existing_files_with_time[0][0])
                            if newer_screenshot != bge.logic.last_used_screenshot:
                                recent_screenshot = newer_screenshot
                                print(f"ðŸ“¸ Found newer screenshot: {os.path.basename(recent_screenshot)}")
                    
                    if os.path.exists(recent_screenshot):
                        file_size = os.path.getsize(recent_screenshot)
                        if file_size > 1000:
                            print(f"ðŸ“¸ Using recent screenshot: {os.path.basename(recent_screenshot)} ({file_size:,} bytes)")
                            fp_image_path = recent_screenshot
                            bge.logic.last_used_screenshot = recent_screenshot  # Track usage
                            screenshot_ready = True
        
        if not screenshot_ready:
            print(f"âŒ No valid screenshots available")
            return None
        
        if not llm_complete_func:
            print("âŒ LLM client not available")
            return None
        
        # Track recent movements to avoid turning loops
        if not hasattr(bge.logic, 'recent_movements'):
            bge.logic.recent_movements = []
        
        # Check for excessive turning - encourage forward movement
        recent_turns = [m for m in bge.logic.recent_movements[-4:] if m in ['LEFT', 'RIGHT']]
        turn_warning = ""
        if len(recent_turns) >= 3:
            turn_warning = f"\n\nðŸš¨ CRITICAL ANTI-LOOP WARNING: You have been turning {len(recent_turns)} times recently: {recent_turns}. You MUST try FORWARD movement if you see any clear space, doorway, or open area ahead. Stop turning and start moving forward to make progress!"
        elif len(recent_turns) >= 2:
            turn_warning = f"\n\n⚠️ ï¸ MOVEMENT WARNING: Recent turns: {recent_turns}. Look for opportunities to move FORWARD instead of continuing to turn."
        # Get world coordinates from BGE actor for loop detection
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        if actor:
            world_coords = [actor.worldPosition.x, actor.worldPosition.y]
        else:
            world_coords = [0.0, 0.0]  # Fallback if actor not found
        
        # EMERGENCY ANTI-LOOP INTERVENTION (disabled - using VLM training instead)
        # loop_result = check_navigation_loops_emergency(world_coords, recent_turns, bge, llm_complete_func, fp_image_path)
        # if loop_result:
        #     return loop_result
        
        # Enhanced prompt for spatial awareness and obstacle avoidance
# ...existing code...
        prompt = f"""You are an AI navigation assistant controlling a character in a 3D house environment. You have access to TWO CRITICAL IMAGES:

🏠 IMAGE 1 - HOUSE LAYOUT: Top-down floor plan showing the complete house structure
👁️ IMAGE 2 - FIRST-PERSON VIEW: What the character currently sees from their perspective

CURRENT MISSION: {task}
CURRENT POSITION: {current_position}
STEP: {step_number + 1}

CRITICAL NAVIGATION RULES:
� DOOR-FIRST NAVIGATION (MOST IMPORTANT):
- **WALLS ARE SOLID**: You CANNOT walk through walls under any circumstances
- **DOORS ARE REQUIRED**: Every room transition requires finding and using a door
- **Check Map for Doors**: Look at floor plan (IMAGE 2) - doorways appear as openings/gaps
- **Face the Door**: Before moving forward, ensure you're aligned with a doorway opening
- **Turn to Find Doors**: If blocked by wall, turn LEFT or RIGHT to locate the door

�🚧 OBSTACLE AVOIDANCE: 
- Do NOT walk through walls, furniture, or objects
- ALWAYS look for doorway openings before entering rooms
- If you see a wall directly ahead, you MUST turn to find the door
- Furniture blocks movement - navigate around it or through available doorways
- Use the floor plan to identify where doors are located before attempting to enter

🗺️ HOUSE LAYOUT WITH LABELED OBJECTS:
**CRITICAL**: The floor plan (IMAGE 2) shows the complete house layout with DIRECT LABELS on all furniture
- Each piece of furniture has its name labeled directly on it (e.g., "Sofa", "Stove", "Bed", "Toilet")
- Room names may be labeled in their respective areas
- Wall boundaries and doorway openings are clearly marked with gaps in the walls
- Use these furniture labels to identify which room you're in and plan your navigation route

📋 ROOM IDENTIFICATION USING LABELED OBJECTS:

**LIVING ROOM - Look for these labeled objects:**
- **Labeled furniture**: "Sofa", "Chair", "Coffee Table", "Dining Table", "TV"
- **Visual characteristics**: Large open space with multiple furniture pieces
- **Location on map**: Check where these furniture labels cluster together
- **First-person verification**: Match what you see (sofa, chairs, dining table) with map labels

**KITCHEN - Look for these labeled objects:**
- **Labeled appliances**: "Stove", "Oven", "Refrigerator", "Sink", "Counter"
- **Visual characteristics**: Compact space with appliances along walls
- **Location on map**: Find where cooking-related labels are grouped
- **First-person verification**: Match what you see (stove, counters, cabinets) with map labels

**BEDROOM - Look for these labeled objects:**
- **Labeled furniture**: "Bed", "Dresser", "Nightstand", "Closet"
- **Visual characteristics**: Private space with bed as primary furniture
- **Location on map**: Find where "Bed" label is positioned
- **First-person verification**: Match what you see (bed, dresser) with map labels

**BATHROOM - Look for these labeled objects:**
- **Labeled fixtures**: "Toilet", "Bathtub", "Shower", "Sink", "Mirror"
- **Visual characteristics**: Small enclosed space with plumbing fixtures
- **Location on map**: Find where bathroom fixture labels are grouped
- **First-person verification**: Match what you see (toilet, tub, sink) with map labels

🚪 CRITICAL DOOR NAVIGATION RULES:
**YOU MUST USE DOORS - CANNOT WALK THROUGH WALLS!**
1. **Identify Doors on Map**: Look for doorway openings/gaps in walls on floor plan
2. **Align with Doorway**: Position yourself to face the door opening directly
3. **Navigate Through Opening**: Move FORWARD only when facing a doorway
4. **Wall Detection**: If you see a solid wall, you MUST turn to find the door
5. **Room Transitions**: Each room change requires going through a doorway

**Common Door Locations (check your map):**
- Living Room ↔ Kitchen: Central doorway/opening between rooms
- Living Room ↔ Hallway: Corridor entrance from living area
- Hallway ↔ Bedroom: Door opening to bedroom
- Bedroom ↔ Bathroom: Private door connection
- Look for doorway indicators (gaps/openings) on the floor plan

🧭 NAVIGATION STRATEGY WITH LABELED OBJECTS:
**Step 1 - Read Object Labels on Map:**
- Examine IMAGE 2 (floor plan) for furniture name labels
- Identify which furniture labels are around you
- Match visible furniture with labeled objects on map

**Step 2 - Identify Current Room:**
- Look at what furniture you see in first-person view (IMAGE 1)
- Find those same furniture labels on the floor plan (IMAGE 2)
- Group of related labels indicates your room type:
  * "Sofa" + "Coffee Table" + "TV" = LIVING_ROOM
  * "Stove" + "Sink" + "Refrigerator" = KITCHEN
  * "Bed" + "Dresser" + "Nightstand" = BEDROOM
  * "Toilet" + "Bathtub" + "Sink" = BATHROOM

**Step 3 - Find Target Room on Map:**
- Locate the target room's characteristic furniture labels
- Example: To find kitchen, look for "Stove" and "Sink" labels on map
- Note the position relative to your current location

**Step 4 - Plan Door-Based Route:**
- Trace a path from your position to target using doorways only
- Doorways are shown as GAPS in the walls on the map
- Identify which doors you need to pass through
- NEVER plan a route that goes through solid walls

**Step 5 - Navigate to Nearest Door:**
- If not facing a door, turn LEFT or RIGHT to find doorway opening
- Use FORWARD to approach the door opening
- Align yourself with the doorway before proceeding

**Step 6 - Verify Room Transitions:**
- After passing through door, check new room's furniture labels
- Confirm labels match expected room type
- Update your mental map of your position

📐 POSITION AWARENESS USING MAP:
- Use furniture labels around you to identify your location
- Compare visible furniture with labeled objects on the floor plan
- Use furniture groups to triangulate exact room location
- Doorways are the ONLY valid transition points between rooms
- If position seems wrong, reorient using visible furniture labels and map layout

🎯 TASK-SPECIFIC ROOM TARGETS WITH LABELED OBJECTS:
**Process: Check Object Labels → Find Door → Navigate Through Door → Verify Room**

- **"Go to kitchen"**: 
  1. Find "Stove" and "Sink" labels on floor plan (IMAGE 2)
  2. Locate doorway opening between your position and kitchen area
  3. Navigate through door (NOT through walls)
  4. Verify by seeing stove/sink/counters in first-person view
  
- **"Go to bedroom"**:
  1. Find "Bed" label on floor plan (IMAGE 2)
  2. May need to pass through hallway first
  3. Use bedroom door opening
  4. Verify by seeing bed and dresser in first-person view
  
- **"Go to livingroom"**:
  1. Find "Sofa" and "Dining Table" labels on floor plan (IMAGE 2)
  2. Usually central area with multiple doorways
  3. Navigate through nearest doorway
  4. Verify by seeing sofa/chairs/dining table in first-person view

- **"Wash hands"**: 
  * Kitchen option: Find "Sink" label in kitchen area (with "Stove" nearby)
  * Bathroom option: Find "Sink" label in bathroom area (with "Toilet" nearby)
  * Navigate through doors to reach the appropriate sink

- **"Cook oatmeal"**: 
  * Find "Stove" label on map (indicates kitchen)
  * Navigate through doors to kitchen
  * Verify by seeing stove/oven in first-person view

📋 CASAS TASK COMPLETION CRITERIA:
- **Room Navigation Tasks**: COMPLETE when you:
  1. Successfully passed through the appropriate doorway
  2. Are inside the target room (verified by map indicators)
  3. Can see matching furniture from first-person view
  4. Room label on map matches your target room

- **Activity Tasks**: COMPLETE when you reach the correct room AND see required furniture:
  - "Wash hands": Kitchen/bathroom with sink visible
  - "Cook": Kitchen with stove visible  
  - "Make call": Dining area with table visible

🚨 TASK COMPLETION RULE: Set "task_complete": true ONLY when:
1. You used DOORS to enter the room (not walls)
2. Map indicators confirm you're in the correct room
3. First-person view shows expected furniture for the task

MOVEMENT COMMANDS - DIRECTIONAL NAVIGATION SYSTEM:

🧭 **PRIMARY COMMANDS (RECOMMENDED)** - Cardinal Directional Movement:
- **NORTH**: Turn to face NORTH (up on map) then move forward in that direction
- **SOUTH**: Turn to face SOUTH (down on map) then move forward in that direction  
- **EAST**: Turn to face EAST (right on map) then move forward in that direction
- **WEST**: Turn to face WEST (left on map) then move forward in that direction

📍 **ORIENTATION INDICATOR ON MAP**:
- The red arrow/triangle on the navigation map shows which direction the actor is currently facing
- **CRITICAL**: Look at the arrow direction carefully - it changes as actor turns
- Arrow directions: UP=North, RIGHT=East, DOWN=South, LEFT=West
- Use this arrow to understand current orientation before choosing movement
- **Do NOT assume arrow direction** - analyze it fresh in each image

✅ **DIRECTIONAL MOVEMENT BENEFITS**:
- More efficient than multiple turn + forward combinations
- Actor automatically turns to face direction then moves forward
- Clear spatial understanding using cardinal directions
- Map arrow helps you plan the most efficient route

🔧 **MANUAL COMMANDS (LEGACY SUPPORT)** - For fine adjustments only:
- FORWARD: Move straight ahead in current facing direction (only if path is clear!)
- BACKWARD: Move backward (use when stuck or need to retreat)
- LEFT: Turn body left (human-like rotation, no forward movement)
- RIGHT: Turn body right (human-like rotation, no forward movement)

💡 **WHEN TO USE EACH SYSTEM**:
- Use NORTH/SOUTH/EAST/WEST when navigating between rooms or moving toward specific locations
- Use FORWARD/BACKWARD/LEFT/RIGHT for minor adjustments or exploring within a room
- PREFER directional commands for efficiency

🚨 CRITICAL LOOP PREVENTION TRAINING:

**MOVEMENT PATTERN RULES (MANDATORY):**
✅ CORRECT: TURN → FORWARD (when clear space seen)
✅ CORRECT: FORWARD → TURN → FORWARD (natural navigation flow)
❌ FORBIDDEN: LEFT → RIGHT → LEFT → RIGHT (spinning in circles)
❌ FORBIDDEN: Multiple turns without attempting FORWARD movement

**FORWARD BIAS PRINCIPLE:**
- When you see ANY open space ahead, choose FORWARD over additional turning
- FORWARD movement always makes progress, turning alone does not
- After each turn, immediately look for opportunities to move FORWARD
- Accept minor obstacles rather than turning indefinitely

**ANTI-LOOP DECISION TRAINING:**
1. **Before each LEFT/RIGHT turn, ask**: "Have I turned recently?"
2. **After each turn, ask**: "Can I see any clear space to move FORWARD?"
3. **If turning twice in a row, ask**: "Why am I not moving FORWARD?"
4. **If view looks familiar, ask**: "Am I repeating previous positions?"

**LOOP BREAK COMMITMENT:**
- If you've turned 2+ times recently, your next move MUST be FORWARD (unless solid wall)
- If the first-person view looks identical to 2 steps ago, force FORWARD movement
- When uncertain between TURN and FORWARD, always choose FORWARD
- Prioritize spatial progress over perfect obstacle avoidance

**MOVEMENT DECISION HIERARCHY:**
1. **FORWARD**: If any clear space visible ahead (even partial clearing)
2. **TURN**: Only if completely blocked by wall/large obstacle directly ahead
3. **BACKWARD**: Only for complete dead-ends or recovery situations
4. **Post-turn rule**: After any turn, immediately evaluate FORWARD option

DECISION PROCESS:
1. **IDENTIFY CURRENT ROOM**: Look at first-person view and match with floor plan layout
   - What furniture do you see? Match with room identification guide above
   - Cross-reference with floor plan to confirm room location
   - Be confident in your identification - avoid UNKNOWN unless truly unclear

2. **LOCATE TARGET ROOM**: Find target room on floor plan (Living Room, Kitchen, Bedroom, Bathroom)
   - Use CASAS task mapping to know where to go
   - Find the target room's position on the floor plan

3. **PLAN ROUTE**: Trace path from current room to target using doorways shown on floor plan
   - Look at floor plan to see how rooms connect
   - Identify which direction leads toward target room

4. **CHECK IMMEDIATE VIEW**: Look for obstacles, walls, furniture in first-person view
   - Is the path ahead clear or blocked?
   - Can you see a doorway or opening?
   - Are there walls or furniture blocking movement?

5. **EXECUTE SAFE MOVEMENT**: Choose action that progresses toward target while avoiding collisions
   - If path is clear AND facing a doorway → FORWARD
   - If wall ahead → LEFT or RIGHT to find door opening
   - If stuck → BACKWARD then try different direction
   - Always explain reasoning including: map indicators seen, doors identified, current room confirmed

**REASONING MUST INCLUDE:**
- "Map shows [ROOM NAME] label at [direction]"
- "See [furniture indicator] on map matching [furniture] in view"
- "Door opening visible on map at [location], turning to align"
- "Passed through doorway, now in [ROOM] confirmed by [furniture indicators]"

🚀 NAVIGATION STRATEGY (CRITICAL):
- **Read Map Labels First**: Look for room name text on floor plan IMAGE 1
- **Match Furniture Indicators**: Compare map icons with first-person view furniture
- **Locate Door Openings**: Find doorway gaps on map before attempting room transitions
- **Never Cross Walls**: All room changes require going through marked doorways
- **Wall Detection**: If you see a WALL directly ahead → Turn LEFT or RIGHT to find clear path
- **Forward Progress**: If you see an OPEN DOORWAY or clear space → Move FORWARD immediately
- **Room Identification**: Match what you see in first-person view with the floor plan layout
- AVOID endless turning - after 1-2 turns, you should try FORWARD
- Look for doorways, hallways, and open pathways to move through
- Don't just spin in place - FORWARD movement is essential for progress

🏠 ENHANCED ROOM IDENTIFICATION GUIDE (CRITICAL):
**STEP 1: ANALYZE FIRST-PERSON VIEW**
Look for these distinctive furniture/features:
- **LIVING ROOM**: Sofas, couch, TV, coffee table, large open space
- **KITCHEN**: Stove, refrigerator, sink, counters, cabinets, cooking appliances
- **DINING ROOM**: Dining table, chairs, possibly phone on table/wall
- **BEDROOM**: Bed, dresser, nightstand, closet, personal items
- **BATHROOM**: Toilet, bathtub, sink, mirror, tiles, small space
- **HALLWAY**: Narrow corridor, doors on sides, no major furniture

**STEP 2: CROSS-REFERENCE WITH FLOOR PLAN**
- Match furniture patterns you see with room locations on the floor plan
- Use the floor plan to confirm which room the furniture pattern indicates
- Look for architectural features (walls, openings, room size) that match the floor plan

**STEP 3: MAKE CONFIDENT ROOM IDENTIFICATION**
- If you see a sofa/couch → likely LIVING_ROOM
- If you see stove/refrigerator → likely KITCHEN  
- If you see bed → likely BEDROOM
- If you see toilet/bathtub → likely BATHROOM
- If you see dining table → likely DINING_ROOM
- If you see narrow corridor → likely HALLWAY
- Only use UNKNOWN if absolutely no identifying features visible

**STEP 4: VALIDATE WITH FLOOR PLAN POSITION**
- Check if your identified room matches the expected position on floor plan
- Ensure the room connection makes sense based on previous movements
- Use the floor plan as ground truth for room layout and connections

RESPOND WITH JSON ONLY:
{{
    "current_room": "LIVING_ROOM",
    "target_room": "KITCHEN", 
    "casas_task": "Go to the kitchen",
    "visible_obstacles": ["wall ahead", "chair on left"],
    "clear_directions": ["doorway visible at 2 o'clock", "opening on right"],
    "relevant_furniture": ["sofa", "coffee table", "TV"],
    "floor_plan_analysis": "Map shows 'Sofa' and 'Coffee Table' labels at my position - confirms LIVING_ROOM. 'Stove' and 'Sink' labels visible to the north - indicates KITCHEN. Doorway gap visible on map between rooms.",
    "route_plan": "See doorway opening on floor plan between 'Sofa' labels (living room) and 'Stove' labels (kitchen). Need to align with door then move forward through it.",
    "movement_decision": "NORTH",
    "reasoning": "Navigation map shows red orientation arrow indicating current facing direction. Target kitchen is NORTH from current position based on floor plan. Using directional command to turn toward kitchen and move forward through doorway. Must use door - cannot go through walls.",
    "doorway_visible": "yes",
    "task_complete": false,
    "casas_completion_reason": "Still in living room, need to pass through doorway to enter kitchen",
    "confidence": "high"
}}

IMPORTANT JSON RULES:
- "current_room": Use ONLY ONE of: LIVING_ROOM, KITCHEN, BEDROOM, BATHROOM, DINING_ROOM, HALLWAY, UNKNOWN
- "movement_decision": Use ONLY ONE of: NORTH, SOUTH, EAST, WEST (preferred) or FORWARD, BACKWARD, LEFT, RIGHT (legacy)
- "doorway_visible": Use ONLY: "yes" or "no"
- "task_complete": Use ONLY: true or false
- "confidence": Use ONLY ONE of: high, medium, low

**ADDITIONAL DOOR-BASED NAVIGATION EXAMPLES:**

SCENARIO 1 - Directional navigation to kitchen (BEST):
"reasoning": "Map shows kitchen is NORTH of current position. Red arrow shows current orientation. Need to turn toward kitchen and move through doorway."
"movement_decision": "NORTH"
"doorway_visible": "yes"

SCENARIO 2 - Navigating to bedroom (GOOD):  
"reasoning": "Map shows bedroom is EAST of living room. Red arrow indicates current facing direction. Need to go EAST toward bedroom area."
"movement_decision": "EAST"
"doorway_visible": "no"

SCENARIO 3 - Direct path to target room (GOOD):
"reasoning": "Map shows bathroom is WEST from current position. First-person view shows clear path. Red orientation arrow confirms direction needed."
"movement_decision": "WEST"
"doorway_visible": "yes"

SCENARIO 4 - Wrong - ignoring map orientation (AVOID):
"reasoning": "Kitchen is straight ahead according to first-person view, moving north to reach it."
"movement_decision": "NORTH" 
[BAD - should verify map orientation and doorway access first!]

SCENARIO 5 - Room transition complete (COMPLETE TASK):
"reasoning": "Passed through doorway. Map shows KITCHEN label at my position. See stove and counters (matching stove indicator on map). Task: Go to kitchen - COMPLETE."
"task_complete": true

**KEY PRINCIPLES:**
1. **Always check map for door locations before moving FORWARD**
2. **Turn to align with doorway opening if not facing it**
3. **Move FORWARD only when facing a door or open space**
4. **Verify room entry by matching map labels with furniture indicators**

The above are EXAMPLES - analyze YOUR actual images and provide YOUR specific observations!

REMEMBER: After turning to avoid obstacles, you should move FORWARD when you see clear space or doorways. Don't keep turning forever!{turn_warning}"""
# ...existing code...
        # Prepare images for VLM
        images = [fp_image_path]
        if house_layout_path and os.path.exists(house_layout_path):
            images.append(house_layout_path)
            print(f"ðŸ” VLM analyzing: FP view + house layout for '{task}' (obstacle-aware)")
        else:
            print(f"ðŸ” VLM analyzing: FP view only for '{task}' (obstacle-aware)")
        
        # Call VLM with dual images
        response = llm_complete_func(prompt, images)
        
        if not response:
            print("âŒ VLM returned no response")
            return None
        
        print("✅ VLM spatial analysis completed")
        
        # Parse VLM response
        return parse_navigation_response(response)
        
    except Exception as e:
        print(f"âŒ Dual image navigation analysis failed: {e}")
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
            print("âŒ No camera found")
            return None
        
        print(f"🖼️ Using camera: {fp_camera.name}")
        
        # Set active camera
        original_camera = scene.active_camera
        scene.active_camera = fp_camera
        
        try:
            # Create capture directory
            captures_dir = os.path.join(os.path.dirname(__file__), "captures")
            os.makedirs(captures_dir, exist_ok=True)
            
            # Use step number for filename
            screenshot_path = os.path.join(captures_dir, f"first_person_{step_number:03d}.png")
            
            print(f"ðŸ“ Screenshot path: {screenshot_path}")
            
            # Request screenshot
            print("ðŸ“¸ Taking screenshot...")
            result = bge.render.makeScreenshot(screenshot_path)
            print(f"ðŸ” makeScreenshot returned: {result}")
            
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
                        print(f"â³ File growing: {file_size} bytes...")
                
                time.sleep(0.5)  # Check every 500ms
            
            print("âŒ Screenshot timeout")
            return None
            
        finally:
            # Restore original camera
            if original_camera:
                scene.active_camera = original_camera
                
    except Exception as e:
        print(f"âŒ Screenshot error: {e}")
        return None

def run_frame_based_navigation():
    """Frame-based navigation - called every frame, doesn't block"""
    
    # Check if we've reached max steps
    if bge.logic.vesper_step >= bge.logic.vesper_max_steps:
        print("â° Maximum steps reached")
        return
    
    # State: Need screenshot
    if not bge.logic.vesper_screenshot_pending and not bge.logic.vesper_screenshot_path:
        print(f"\nðŸ”„ Navigation Step {bge.logic.vesper_step + 1}/{bge.logic.vesper_max_steps}")
        print("ðŸ“¸ Requesting screenshot...")
        
        # Request screenshot (non-blocking)
        if request_screenshot_async():
            bge.logic.vesper_screenshot_pending = True
        
        return  # Allow frame to render
    
    # State: Screenshot pending - check if ready
    if bge.logic.vesper_screenshot_pending:
        screenshot_path = check_screenshot_ready()
        
        if screenshot_path == "TIMEOUT":
            print("âŒ Screenshot timeout, retrying...")
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
        print("ðŸ” Analyzing navigation...")
        
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
            if action in ['NORTH', 'SOUTH', 'EAST', 'WEST']:
                print(f"🎯 Directional Movement: {action}")
                print(f"💭 Reasoning: {result.get('reasoning', 'No reasoning')}")
                execute_directional_movement(action)
            elif action in ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT']:
                print(f"🎯 Movement: {action}")
                print(f"💭 Reasoning: {result.get('reasoning', 'No reasoning')}")
                execute_movement(action)
            else:
                print(f"⚠️ ï¸ Invalid action: {action}")
        else:
            print("âŒ Navigation analysis failed")
        
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
            print("âŒ No camera found")
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
        print(f"ðŸ“¸ Screenshot requested: {os.path.basename(screenshot_path)} (result: {result})")
        
        return True
        
    except Exception as e:
        print(f"âŒ Screenshot request failed: {e}")
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
                print(f"âŒ Navigation update error: {e}")
        
        # Store the function reference for potential BGE logic brick usage
        bge.logic.vesper_main_function = continuous_navigation
        
        print("ðŸ”§ Continuous navigation setup complete")
        
except Exception as e:
    print(f"⚠️ ï¸ Continuous setup failed: {e}")
    # Fallback: just run main once
    main()


def _parse_navigation_result_with_fallback(llm_result, fallback_action="FORWARD"):
    """Parse LLM result with aggressive fallback for stuck situations"""
    if not llm_result:
        return {
            "movement_decision": fallback_action,
            "reasoning": "No LLM response - using fallback",
            "current_room": "UNKNOWN",
            "confidence": 0.3,
            "task_complete": False
        }
        
    import json
    import re
    
    try:
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*?\}', llm_result, re.DOTALL)
        if json_match:
            result_data = json.loads(json_match.group())
            
            # Validate required fields
            if "movement_decision" not in result_data:
                result_data["movement_decision"] = fallback_action
            if "reasoning" not in result_data:
                result_data["reasoning"] = "Parsed from LLM with fallback"
            if "current_room" not in result_data:
                result_data["current_room"] = "UNKNOWN"
                
            return result_data
        else:
            # No JSON found - create from text analysis
            movement = "FORWARD"
            if "LEFT" in llm_result.upper():
                movement = "LEFT" 
            elif "RIGHT" in llm_result.upper():
                movement = "RIGHT"
            elif "BACKWARD" in llm_result.upper():
                movement = "BACKWARD"
            
            return {
                "movement_decision": movement,
                "reasoning": "Extracted from text response",
                "current_room": "UNKNOWN", 
                "confidence": 0.5,
                "task_complete": False
            }
        
    except Exception as e:
        print(f"⚠️ JSON parsing failed: {e}")
        return {
            "movement_decision": fallback_action,
            "reasoning": f"Parse error - using {fallback_action}",
            "current_room": "UNKNOWN",
            "confidence": 0.2,
            "task_complete": False
        }


def check_navigation_loops_emergency(world_coords, recent_turns, bge, llm_complete_func, fp_image_path):
    """Emergency loop detection with immediate forced movement"""
    
    # Track position history for stuck detection
    current_pos_str = f"[{world_coords[0]:.1f}, {world_coords[1]:.1f}]"
    if not hasattr(bge.logic, 'position_history'):
        bge.logic.position_history = []
    bge.logic.position_history.append(current_pos_str)
    
    # Keep history manageable
    if len(bge.logic.position_history) > 8:
        bge.logic.position_history = bge.logic.position_history[-8:]
    
    # Check if stuck in same position for 3+ steps
    if len(bge.logic.position_history) >= 3:
        recent_positions = bge.logic.position_history[-3:]
        if len(set(recent_positions)) == 1:  # All same position
            print(f"🚨 EMERGENCY: Actor stuck at {current_pos_str} for 3+ steps!")
            return force_emergency_forward_movement(llm_complete_func, fp_image_path, current_pos_str)
    
    # Check for excessive turning (4+ turns or 2+ with no forward)
    recent_forwards = [m for m in bge.logic.recent_movements[-8:] if m == 'FORWARD']
    if len(recent_turns) >= 3 or (len(recent_turns) >= 2 and len(recent_forwards) == 0):
        print(f"🚨 TURNING LOOP DETECTED: {len(recent_turns)} turns, {len(recent_forwards)} forwards")
        return force_emergency_forward_movement(llm_complete_func, fp_image_path, current_pos_str)
    
    return None  # No emergency intervention needed

def analyze_position_only_navigation(world_coords, task, step_number):
    """Fallback navigation based on position only when screenshots fail"""
    
    print("🗺️ Using position-only navigation fallback")
    
    # Simple position-based logic
    x, y = world_coords[0], world_coords[1]
    
    # Use consistent room detection logic
    current_room = detect_current_room(x, y).lower()
    
    # Simple movement decision - try to move toward task goal
    if "kitchen" in task.lower() and current_room != "kitchen":
        decision = "LEFT" if x > 0 else "RIGHT"
    elif "bathroom" in task.lower() and current_room != "bathroom": 
        decision = "FORWARD" if y < 0.5 else "BACKWARD"
    else:
        # Default exploration - move forward
        decision = "FORWARD"
    
    return {
        "movement_decision": decision,
        "reasoning": f"Position-only navigation: at {current_room}, moving {decision} toward goal",
        "current_room": current_room,
        "confidence": 0.4,
        "task_complete": False
    }

def force_emergency_forward_movement(llm_complete_func, fp_image_path, position):
    """Force FORWARD movement to break loops"""
    
    emergency_prompt = f"""CRITICAL NAVIGATION EMERGENCY - IMMEDIATE ACTION REQUIRED

You are stuck in a navigation loop at position {position}. This is an EMERGENCY OVERRIDE.

MANDATORY RESPONSE: You MUST respond with FORWARD movement immediately.
- Do NOT analyze obstacles or rooms
- Do NOT consider turning options  
- ONLY respond with FORWARD movement
- This is required to escape the navigation loop

EXACT REQUIRED JSON RESPONSE:
{{
    "movement_decision": "NORTH",
    "reasoning": "Emergency loop break - moving north to reset position",
    "current_room": "unknown", 
    "confidence": "0.9",
    "task_complete": false
}}

NO OTHER RESPONSE IS ACCEPTABLE. Respond with the exact JSON above."""
    
    try:
        print("🚀 Sending emergency directional command...")
        emergency_result = llm_complete_func(emergency_prompt, [fp_image_path] if fp_image_path else [])
        
        if emergency_result:
            print(f"📥 Emergency response: {emergency_result[:100]}...")
            return _parse_navigation_result_with_fallback(emergency_result, "FORWARD")
        else:
            print("⚠️ No emergency response - using direct fallback")
            
    except Exception as e:
        print(f"❌ Emergency command failed: {e}")
    
    # Ultimate fallback - direct movement command
    print("🔧 Using ultimate fallback: NORTH")
    return {
        "movement_decision": "NORTH",
        "reasoning": "Ultimate emergency fallback - moving north to reset position",
        "current_room": "unknown",
        "confidence": 0.6,
        "task_complete": False
    }
