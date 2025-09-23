import bge
import mathutils
import os
import sys
import json
import time
import re
import queue
import threading

# Import enhanced VLM extensions
try:
    from enhanced_vlm_extensions import (
        get_enhanced_vlm_manager, 
        get_casas_subtask_manager,
        EnhancedVLMManager,
        CASASSubtaskManager
    )
    from first_person_camera import (
        get_first_person_camera,
        get_multimodal_vlm_context,
        initialize_first_person_system
    )
    ENHANCED_VLM_AVAILABLE = True
    status_print("✅ Enhanced VLM extensions loaded successfully")
except ImportError as e:
    ENHANCED_VLM_AVAILABLE = False
    debug_print(f"Enhanced VLM features not available: {e}")

# Import MCP Integration for BGE
try:
    from bge_mcp_integration import (
        initialize_mcp_for_bge,
        get_enhanced_context_for_navigation,
        capture_scene_images,
        get_navigation_context,
        execute_navigation_action,
        create_llm_prompt_for_task,
        execute_llm_tool_suggestion,
        check_mcp_services_status,
        get_mcp_integration_info
    )
    MCP_INTEGRATION_AVAILABLE = True
    status_print("✅ MCP integration loaded for BGE")
except ImportError as e:
    MCP_INTEGRATION_AVAILABLE = False
    print(f"⚠️ MCP integration not available: {e}")

# Import Intelligent Camera Selection
try:
    from intelligent_camera_selection import (
        select_camera_intelligently,
        capture_with_intelligent_camera,
        get_camera_selection_stats
    )
    INTELLIGENT_CAMERA_AVAILABLE = True
    status_print("✅ Intelligent camera selection loaded")
except ImportError as e:
    INTELLIGENT_CAMERA_AVAILABLE = False
    print(f"⚠️ Intelligent camera selection not available: {e}")

def setup_python_path():
    """Setup path to access LLM client"""
    try:
        vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"

        if vesper_root not in sys.path:
            sys.path.insert(0, vesper_root)
            status_print(f"✅ BGE: Path setup complete")

        # Load environment variables
        env_path = os.path.join(vesper_root, "backend", "app", "llm", ".env")
        if os.path.exists(env_path):
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
                status_print(f"✅ BGE: Environment loaded")
            except ImportError:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()

        return True
    except Exception as e:
        status_print(f"❌ BGE: Path setup failed: {e}")
    return False

path_ok = setup_python_path()

# =============================
# LLM client import
# =============================
LLM_AVAILABLE = False
few_shot_system = None

if path_ok:
    try:
        from backend.app.llm.client import chat_completion, chat_completion_with_vision
        from backend.app.llm.few_shot_navigation import VESPERFewShotPrompts, validate_json_response
        LLM_AVAILABLE = True
        print("🔗 LLM: Connected")
        
        # CASAS Dataset Integration
        from casas_testbed.vesper_casas_dataset_generator import (
            init_vesper_casas_session, execute_vesper_task, 
            finalize_vesper_casas_session, VESPERCASASDatasetGenerator
        )
        CASAS_AVAILABLE = True
        print("🏠 CASAS: Dataset generator connected")
    except ImportError as casas_e:
        CASAS_AVAILABLE = False
        print(f"⚠️ CASAS: Dataset generator not available - {casas_e}")
        try:
            # Continue with LLM setup even if CASAS fails
            pass
        except Exception as llm_e:
            LLM_AVAILABLE = False
            print(f"❌ LLM: Setup failed - {llm_e}")
    except Exception as e:
        LLM_AVAILABLE = False
        CASAS_AVAILABLE = False
        status_print(f"❌ BGE: Import failed: {e}")
        
    # Initialize few-shot system regardless of CASAS status
    if LLM_AVAILABLE:
        try:
            # Initialize few-shot system - define captures_dir inline to avoid ordering issues
            vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
            captures_dir = os.path.join(vesper_root, "blender", "captures")
            os.makedirs(captures_dir, exist_ok=True)
            
            few_shot_system = VESPERFewShotPrompts(captures_dir)
            print("🎯 Few-shot navigation system initialized")
        except Exception as fs_e:
            print(f"⚠️ Few-shot system failed: {fs_e}")
            few_shot_system = None
    else:
        few_shot_system = None
            
else:
    LLM_AVAILABLE = False
    CASAS_AVAILABLE = False
    status_print("❌ BGE: Path setup failed - LLM and CASAS unavailable")
    few_shot_system = None

# =============================
# Motion Validation System
# =============================
MOTION_VALIDATION_AVAILABLE = False
try:
    from blender.vesper_motion_validation import (
        initialize_motion_validation, validate_actor_movement,
        validate_vlm_decision, generate_validated_casas_data,
        cleanup_motion_validation
    )
    MOTION_VALIDATION_AVAILABLE = True
    print("🎯 Motion Validation: System loaded")
except ImportError as mv_e:
    MOTION_VALIDATION_AVAILABLE = False
    print(f"⚠️ Motion Validation: Not available - {mv_e}")

# =============================
# Task loading helpers
# =============================
def load_vesper_tasks():
    """Load CASAS-aligned tasks for dataset generation"""
    try:
        # Priority: CASAS-aligned tasks first
        casas_task_files = [
            os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\blender", "vesper_casas_tasks.txt"),
            os.path.join(os.path.dirname(__file__), "vesper_casas_tasks.txt")
        ]
        
        # Try CASAS-aligned tasks first
        for task_file in casas_task_files:
            if os.path.exists(task_file):
                status_print(f"🎯 BGE: Loading CASAS-aligned tasks from {task_file}")
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Parse CASAS task format: Extract clean task names from markdown
                        casas_tasks = []
                        for line in content.split('\n'):
                            line = line.strip()
                            # Skip comments, empty lines, markdown headers, and decorative lines
                            if (line and 
                                not line.startswith('#') and 
                                not line.startswith('##') and 
                                not line.startswith('###') and 
                                not line.startswith('```') and
                                not line.startswith('-') and
                                not line.startswith('*') and
                                '**t' in line and ':' in line):
                                
                                # Extract task name from markdown format like "1. **t1: Make a phone call**"
                                if '**t' in line and ':' in line:
                                    # Find the task description between : and **
                                    start = line.find(':') + 1
                                    end = line.find('**', start)
                                    if end == -1:
                                        end = len(line)
                                    task_name = line[start:end].strip()
                                    if task_name and len(task_name) > 3:  # Valid task name
                                        casas_tasks.append(task_name)
                        
                        # If no clean tasks found, use fallback
                        if not casas_tasks:
                            status_print("⚠️ BGE: No clean tasks extracted from CASAS file, using fallback")
                            casas_tasks = ["Make a phone call", "Wash hands", "Cook oatmeal", "Eat meal", "Clean dishes"]
                        
                        status_print(f"✅ BGE: Loaded {len(casas_tasks)} CASAS tasks: {casas_tasks}")
                        return casas_tasks
        
        # Fallback to regular task files
        task_files = [
            r"C:\Users\hbui11\AppData\Roaming\UPBGE\Blender\4.4\scripts\addons\vesper_tools\..\..\vesper_tasks.txt",
            r"C:\Users\hbui11\AppData\Roaming\UPBGE\Blender\4.4\scripts\vesper_tasks.txt",
            os.path.join(os.path.dirname(__file__), "vesper_tasks.txt"),
            os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\blender", "vesper_tasks.txt")
        ]
        
        for task_file in task_files:
            if os.path.exists(task_file):
                print(f"📝 BGE: Loading tasks from {task_file}")
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Parse tasks - try both comma and pipe separation
                        if '|' in content:
                            tasks = [task.strip() for task in content.split('|') if task.strip()]
                        else:
                            tasks = [task.strip() for task in content.split(',') if task.strip()]
                        status_print(f"✅ BGE: Loaded {len(tasks)} tasks: {tasks}")
                        return tasks
        
        status_print("⚠️ BGE: No task files found, using CASAS defaults")
        return ["Make phone call", "Wash hands", "Cook oatmeal", "Eat meal", "Clean dishes"]
        
    except Exception as e:
        status_print(f"❌ BGE: Error loading tasks: {e}")
        return None

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
        self.current_task_start_time = time.time()
        self.current_task_data = {
            "task_name": task_name,
            "task_index": task_index,
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
            avg_time = sum(task["completion_time"] for task in self.session_data["task_details"]) / len(self.session_data["task_details"])
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

# Initialize enhanced VLM managers
enhanced_vlm_manager = None
casas_subtask_manager = None
first_person_camera = None
multimodal_vlm_context = None

def get_enhanced_managers():
    """Get or create enhanced VLM managers"""
    global enhanced_vlm_manager, casas_subtask_manager, first_person_camera, multimodal_vlm_context
    
    if ENHANCED_VLM_AVAILABLE and enhanced_vlm_manager is None:
        try:
            enhanced_vlm_manager = get_enhanced_vlm_manager()
            casas_subtask_manager = get_casas_subtask_manager()
            
            # Initialize first-person system
            if initialize_first_person_system():
                first_person_camera = get_first_person_camera()
                multimodal_vlm_context = get_multimodal_vlm_context()
                print("🎥 Enhanced VLM system initialized")
            else:
                status_print("⚠️ First-person system initialization failed")
                
        except Exception as e:
            print(f"❌ Enhanced VLM initialization failed: {e}")
    
    return {
        "vlm_manager": enhanced_vlm_manager,
        "subtask_manager": casas_subtask_manager,
        "first_person_camera": first_person_camera,
        "multimodal_context": multimodal_vlm_context
    }

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
    existing_files = [f for f in os.listdir(captures_dir) if f.startswith("bird-eye_") and f.endswith(".png")]
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
    p = os.path.join(captures_dir, f"bird-eye_{n:03d}.png")
    while os.path.exists(p):
        n += 1
        p = os.path.join(captures_dir, f"bird-eye_{n:03d}.png")
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
        status_print("⚠️ BGE: No BirdEyeCamera found. Searching for camera-like object...")
        for obj in scene.objects:
            if 'camera' in obj.name.lower() or 'cam' in obj.name.lower():
                camera = obj
                break
        if not camera:
            status_print("❌ BGE: No camera available")
            return None

    # ENHANCED: Optimize camera settings for better screenshot quality
    try:
        scene.active_camera = camera
        
        # Ensure camera has optimal settings for screenshots
        if hasattr(camera, 'lens'):
            # Adjust camera properties for better coverage and clarity
            original_lens = camera.lens
            # Use a wider lens for better room coverage in bird's eye view
            if camera.lens < 35:
                camera.lens = 35  # Wider view for better room visibility
                print(f"📷 BGE: Adjusted camera lens from {original_lens} to {camera.lens}")
        
        # Optimize camera position if needed (bird's eye view should be high up)
        cam_pos = camera.worldPosition
        if cam_pos.z < 5.0:  # Camera should be high up for bird's eye view
            status_print(f"⚠️ BGE: Camera height may be too low: {cam_pos.z}")
            print("💡 BGE: Consider positioning BirdEyeCamera higher (Z > 8) for better overview")
            
    except Exception as e:
        status_print(f"⚠️ BGE: Camera optimization error: {e}")

    # Ensure we capture from the right camera
    try:
        scene.active_camera = camera
    except Exception as e:
        status_print(f"⚠️ BGE: Camera error: {e}")

    capdir = _captures_dir()
    shot_path = _next_screenshot_path(capdir)

    # ENHANCED: Take high-quality screenshot for better VLM analysis
    try:        
        status_print(f"📸 BGE: Capturing high-quality screenshot...")
        
        # Standard BGE screenshot method (no world attribute access)
        bge.render.makeScreenshot(shot_path)
        
        # Additional quality enhancement: Check viewport info if available
        try:
            import bgl
            # Get viewport dimensions for reference
            viewport = bgl.glGetIntegerv(bgl.GL_VIEWPORT)
            debug_print(f"📐 BGE: Current viewport: {viewport[2]}x{viewport[3]}")
        except Exception:
            pass  # Not all BGE versions have bgl access
            
    except Exception as e:
        status_print(f"❌ BGE: Screenshot capture failed: {e}")
        return None

    st = bge.logic._vesper_shot
    st["pending"] = True
    st["path"] = shot_path
    st["start_time"] = time.time()
    st["tries"] += 1

    return shot_path

def poll_screenshot_ready(min_bytes: int = 2500, timeout_s: float = 5.0):  # Increased min_bytes for higher quality
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
                print(f"📸 Screenshot ready: {filename} ({size} bytes)")
                return p
            else:
                debug_print(f"⏳ BGE: Screenshot still rendering... ({size}/{min_bytes} bytes)")
        except Exception as e:
            status_print(f"⚠️ BGE: Screenshot error: {e}")

    # timeout -> caller may re-request
    if time.time() - st["start_time"] > timeout_s:
        st["pending"] = False
        return "TIMEOUT"

    return None



# =============================
# JSON parsing helpers
# =============================
def extract_and_fix_json(response):
    """Extract and attempt to fix JSON from LLM response"""
    import re
    
    # First, try standard extraction
    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        debug_print(f"📦 BGE: Extracted from markdown: {len(json_str)} chars")
    else:
        # Fallback: look for JSON object boundaries
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            debug_print(f"📦 BGE: Extracted from boundaries: {len(json_str)} chars")
        else:
            return None
    
    if not json_str:
        return None
    
    # Clean up control characters first
    json_str = re.sub(r'[\x00-\x1f\x7f]', '', json_str)
    
    # Try to parse as-is first
    try:
        import json
        json.loads(json_str)
        debug_print(f"🧹 BGE: JSON is valid as-is: {json_str[:100]}...")
        return json_str
    except json.JSONDecodeError as e:
        debug_print(f"🔧 BGE: JSON needs repair - {e}")
        pass
    
    # Apply targeted fixes for common LLM errors
    try:
        original_json = json_str
        
        # Fix 1: The main issue - missing closing quote before comma
        # Pattern: "Based on furniture around pink dot: [LIVING_ROOM],
        # Should be: "Based on furniture around pink dot: [LIVING_ROOM]",
        json_str = re.sub(r':\s*"([^"]*\[[A-Z_]+\]),', r': "\1",', json_str)
        
        # Fix 2: Handle other missing closing quotes before comma
        # Pattern: "text,   -> "text",
        json_str = re.sub(r':\s*"([^"]*),(\s*"[^"]*"\s*:)', r': "\1",\2', json_str)
        
        # Fix 3: Room names in brackets without quotes
        json_str = re.sub(r'\[([A-Z_]+)\]', r'"\1"', json_str)
        
        if json_str != original_json:
            debug_print(f"🔧 BGE: Applied JSON repairs")
        
        debug_print(f"🧹 BGE: Repaired JSON preview: {json_str[:150]}...")
        return json_str
        
    except Exception as e:
        status_print(f"❌ BGE: JSON repair failed: {e}")
        return json_str  # Return original if repair fails

def parse_vlm_response(response, current_task=None):
    """Parse VLM response with robust JSON handling and task validation"""
    import json
    
    debug_print(f"📏 BGE: Full response length: {len(response)} characters")
    
    json_str = extract_and_fix_json(response)
    
    if json_str:
        try:
            result = json.loads(json_str)
            status_print(f"✅ BGE: JSON parsed successfully")
            
            # Check if task is complete based on room analysis
            task_complete = result.get("task_complete", False)
            current_room = result.get("current_room", "UNKNOWN")
            furniture_visible = result.get("furniture_visible", "None specified")
            
            # SERVER-SIDE TASK VALIDATION: Double-check VLM's task completion decision
            if task_complete and current_task:
                task_validated = False
                task_lower = current_task.lower()
                
                # Comprehensive room validation for all supported room types
                if ("kitchen" in task_lower or "cook" in task_lower) and current_room == "KITCHEN":
                    task_validated = True
                elif ("living room" in task_lower or "living" in task_lower or "relax" in task_lower) and current_room == "LIVING_ROOM":
                    task_validated = True
                elif ("bathroom" in task_lower or "prepare" in task_lower or "wash" in task_lower) and current_room == "BATHROOM":
                    task_validated = True
                elif ("bedroom" in task_lower or "sleep" in task_lower or "rest" in task_lower) and current_room == "BEDROOM":
                    task_validated = True
                elif ("office" in task_lower or "work" in task_lower or "study" in task_lower) and current_room == "OFFICE":
                    task_validated = True
                elif ("garage" in task_lower or "car" in task_lower or "park" in task_lower) and current_room == "GARAGE":
                    task_validated = True
                # Also allow generic room name matching
                elif "kitchen" in task_lower and current_room == "KITCHEN":
                    task_validated = True
                elif "living" in task_lower and current_room == "LIVING_ROOM":
                    task_validated = True
                elif "bathroom" in task_lower and current_room == "BATHROOM":
                    task_validated = True
                elif "bedroom" in task_lower and current_room == "BEDROOM":
                    task_validated = True
                elif "office" in task_lower and current_room == "OFFICE":
                    task_validated = True
                elif "garage" in task_lower and current_room == "GARAGE":
                    task_validated = True
                
                if not task_validated:
                    print(f"🚨 BGE: SERVER VALIDATION FAILED!")
                    print(f"   Task: '{current_task}' vs Room: '{current_room}'")
                    print(f"   VLM incorrectly marked task complete - overriding to FALSE")
                    task_complete = False
                    # Force movement to find correct room
                    if "movement_sequence" in result:
                        result["movement_sequence"] = ["UP"]  # Try moving to find correct room
                else:
                    status_print(f"✅ BGE: SERVER VALIDATION PASSED - Task '{current_task}' matches room '{current_room}'")
                    
                    # ENHANCED: Handle device interactions when task is validated
                    managers = get_enhanced_managers()
                    enhanced_vlm_manager = managers.get("vlm_manager")
                    casas_subtask_manager = managers.get("subtask_manager")
                    
                    if enhanced_vlm_manager and casas_subtask_manager:
                        # Check for device interaction suggestions in the reasoning
                        reasoning = result.get("reasoning", "")
                        
                        # Process device interactions based on task and room
                        scene = bge.logic.getCurrentScene()
                        actor = scene.objects.get("Actor")
                        
                        if actor:
                            actor_position = (actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z)
                            
                            # Determine which devices to interact with based on task
                            device_interactions = []
                            
                            if "kitchen" in current_task.lower():
                                if "cook" in current_task.lower():
                                    device_interactions = ["water_control", "stove_burner"]
                                elif "wash" in current_task.lower():
                                    device_interactions = ["water_control"]
                                device_interactions.append("kitchen_light_switch")
                                
                            elif "phone" in current_task.lower() and current_room == "DININGROOM":
                                device_interactions = ["phone", "dining_light_switch"]
                            
                            # Execute device interactions
                            for device_id in device_interactions:
                                if device_id in enhanced_vlm_manager.devices:
                                    interaction_type = "turn_on" if "switch" in device_id or "control" in device_id else "pickup"
                                    if device_id == "phone":
                                        interaction_type = "pickup"
                                    elif device_id == "water_control":
                                        interaction_type = "turn_on_hot"
                                    elif device_id == "stove_burner":
                                        interaction_type = "turn_on"
                                    elif "light_switch" in device_id:
                                        interaction_type = "toggle"
                                    
                                    interaction_result = enhanced_vlm_manager.interact_with_device(
                                        device_id, interaction_type, actor_position
                                    )
                                    
                                    if interaction_result.get("success"):
                                        print(f"🎮 Device interaction successful: {device_id}")
                                        
                                        # Mark checkpoint as completed
                                        checkpoint_id = f"interact_with_{device_id}"
                                        casas_subtask_manager.complete_checkpoint(checkpoint_id)
                                    else:
                                        print(f"❌ Device interaction failed: {device_id}")
                            
                            # Check if current subtask can be completed
                            if casas_subtask_manager.check_subtask_completion():
                                casas_subtask_manager.advance_subtask()
                                
                                # Check if entire task is complete
                                next_subtask = casas_subtask_manager.get_current_subtask()
                                if not next_subtask:
                                    print("🎉 All CASAS subtasks completed!")
                                    result["casas_task_complete"] = True
                                else:
                                    print(f"📋 Advanced to next subtask: {next_subtask['description']}")
                                    result["casas_task_complete"] = False
            
            print(f"🏠 BGE: Current room identified: {current_room}")
            print(f"🪑 BGE: Furniture visible: {furniture_visible}")
            status_print(f"✅ BGE: Task complete: {task_complete}")

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
                        
                        # If we found directions, add them; otherwise add the raw move
                        if directions_found:
                            sequence.extend(directions_found)
                        else:
                            # Maybe it's already a clean direction
                            clean_move = move.strip().upper()
                            if clean_move in ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]:
                                sequence.append(clean_move)
                            else:
                                status_print(f"⚠️ BGE: Unrecognized move format: '{move}', defaulting to STAY")
                                sequence.append("STAY")
                    else:
                        status_print(f"⚠️ BGE: Non-string move: {move}, defaulting to STAY")
                        sequence.append("STAY")
                
                print(f"🔄 BGE: Raw sequence: {raw_sequence}")
                status_print(f"🎯 BGE: Extracted sequence: {sequence}")
                
                if sequence:
                    return {
                        "movement_sequence": sequence, 
                        "reasoning": result.get('reasoning', ''),
                        "task_complete": task_complete,
                        "current_room": current_room,
                        "furniture_visible": furniture_visible
                    }
                else:
                    status_print(f"❌ BGE: No valid movements extracted from: {raw_sequence}")
                    
                    # Check for oscillation patterns (template responses)
                    furniture_str = str(furniture_visible).lower()
                    reasoning_str = str(result.get('reasoning', '')).lower()
                    
                    if ("list specific furniture" in furniture_str or 
                        "list furniture near pink dot" in reasoning_str or
                        current_room == "UNKNOWN" and len(raw_sequence) > 2):
                        print("🔄 BGE: Detected template/oscillation response - forcing STAY")
                        return {
                            "movement_sequence": ["STAY"], 
                            "reasoning": "Template response detected - staying put to avoid oscillation",
                            "task_complete": False,
                            "current_room": "UNKNOWN",
                            "furniture_visible": ["unclear_image"]
                        }
                    
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
                status_print(f"❌ BGE: Missing or invalid movement_sequence in result: {list(result.keys())}")
                
        except json.JSONDecodeError as e:
            status_print(f"⚠️ BGE: JSON parsing error: {e}")
            print(f"📝 BGE: Problematic JSON: {json_str}")
    else:
        status_print("❌ BGE: No JSON string extracted from response")

    # Show full response for debugging
    debug_print(f"🔍 BGE: FULL VLM RESPONSE DEBUG:")
    print(f"'{response}'")
    
    raise Exception(f"❌ Vision analysis failed - see debug output above")

# =============================
# Enhanced LLM logic with reference image support
# =============================


def vision_only_completion(prompt, image_path):
    """Vision completion that NEVER falls back to text-only"""
    import os
    import base64
    
    if not os.path.exists(image_path):
        raise Exception(f"❌ Image file not found: {image_path}")
    
    start_time = time.time()
    timeout_occurred = False
    
    try:
        # Import required variables
        from backend.app.llm.client import client, HOST, MODEL
        
        debug_print(f"🔍 DEBUG: IMAGES-ONLY completion with HOST='{HOST}', MODEL='{MODEL}'")
        
        # Prepare image for Ollama
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        debug_print(f"🔍 DEBUG: Sending IMAGES-ONLY request...")
        
        # Windows-compatible timeout handling
        import threading
        import queue
        
        result_queue = queue.Queue()
        timeout_occurred = False
        
        def llm_call():
            try:
                response = client.chat(
                    model=MODEL,
                    messages=[
                        {
                            'role': 'user',
                            'content': prompt,
                            'images': [image_data]
                        }
                    ],
                    options={'temperature': 0.3}
                )
                result_queue.put(('success', response))
            except Exception as e:
                result_queue.put(('error', e))
        
        # Start LLM call in separate thread
        llm_thread = threading.Thread(target=llm_call)
        llm_thread.daemon = True
        llm_thread.start()
        
        # Wait for result with timeout
        try:
            result_type, result_data = result_queue.get(timeout=180)  # 180 second timeout
            
            if result_type == 'error':
                raise result_data
            
            response = result_data
            
            response_time = time.time() - start_time
            result = response['message']['content'].strip()
            debug_print(f"🔍 DEBUG: IMAGES-ONLY completion successful, response length: {len(result)}, time: {response_time:.1f}s")
            
            if not result or len(result) < 20:
                raise Exception("❌ VLM returned insufficient response")
                
            return result, response_time, timeout_occurred
            
        except queue.Empty:
            timeout_occurred = True
            print("⏰ WARNING: VLM request timed out after 180 seconds")
            raise Exception("❌ VLM request timed out")
        except Exception as e:
            print(f"❌ ERROR: VLM request failed: {str(e)}")
            raise e
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR in vision_only_completion: {str(e)}")
        raise e

def multimodal_vision_completion(prompt, bird_eye_path, first_person_path):
    """Multi-modal vision completion with both bird-eye and first-person views"""
    import os
    import base64
    
    if not os.path.exists(bird_eye_path):
        raise Exception(f"❌ Bird-eye image file not found: {bird_eye_path}")
    if not os.path.exists(first_person_path):
        raise Exception(f"❌ First-person image file not found: {first_person_path}")
    
    start_time = time.time()
    timeout_occurred = False
    
    try:
        # Import required variables
        from backend.app.llm.client import client, HOST, MODEL
        
        debug_print(f"🔍 DEBUG: MULTI-MODAL completion with HOST='{HOST}', MODEL='{MODEL}'")
        
        # Prepare both images for Ollama
        with open(bird_eye_path, "rb") as img_file:
            bird_eye_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        with open(first_person_path, "rb") as img_file:
            first_person_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Enhanced prompt for dual-image analysis
        multimodal_prompt = f"""🎥 DUAL-VIEW VISUAL ANALYSIS:

IMAGE 1 - BIRD-EYE VIEW: Top-down navigation view showing:
- Pink dot = actor position
- Room layout and furniture placement
- Navigation paths and obstacles
- Overall spatial relationships

IMAGE 2 - FIRST-PERSON VIEW: Actor's eye-level perspective showing:
- Immediate surroundings and furniture details
- Room identification features (appliances, furniture types)
- Obstacles and interaction opportunities
- Direct visual context of current location

{prompt}

🔍 ANALYSIS WORKFLOW:
1. Examine BIRD-EYE view to locate pink dot and understand spatial position
2. Examine FIRST-PERSON view to identify room type and immediate obstacles
3. Cross-reference both views to confirm room identification
4. Use BIRD-EYE for navigation planning and FIRST-PERSON for obstacle detection
5. Make navigation decision based on combined visual information

🚨 RESPOND WITH JSON ONLY - Base analysis on BOTH visual perspectives!"""

        debug_print(f"🔍 DEBUG: Sending MULTI-MODAL request with 2 images...")
        
        # Windows-compatible timeout handling
        result_queue = queue.Queue()
        timeout_occurred = False
        
        def llm_call():
            try:
                response = client.chat(
                    model=MODEL,
                    messages=[
                        {
                            'role': 'user',
                            'content': multimodal_prompt,
                            'images': [bird_eye_data, first_person_data]  # Both images
                        }
                    ],
                    options={'temperature': 0.3}
                )
                result_queue.put(('success', response))
            except Exception as e:
                result_queue.put(('error', e))
        
        # Start LLM call in separate thread
        llm_thread = threading.Thread(target=llm_call)
        llm_thread.daemon = True
        llm_thread.start()
        
        # Wait for result with timeout
        try:
            result_type, result_data = result_queue.get(timeout=200)  # Longer timeout for dual images
            
            if result_type == 'error':
                raise result_data
            
            response = result_data
            
            response_time = time.time() - start_time
            result = response['message']['content'].strip()
            debug_print(f"🔍 DEBUG: MULTI-MODAL completion successful, response length: {len(result)}, time: {response_time:.1f}s")
            
        except queue.Empty:
            timeout_occurred = True
            response_time = time.time() - start_time
            print(f"⏰ DEBUG: MULTI-MODAL completion timeout after {response_time:.1f}s")
            
            # Fallback to bird-eye only
            print("🔄 DEBUG: Falling back to bird-eye only analysis...")
            return vision_only_completion(prompt, bird_eye_path)
        
    except Exception as e:
        response_time = time.time() - start_time
        print(f"❌ DEBUG: MULTI-MODAL completion error after {response_time:.1f}s: {e}")
        
        # Fallback to bird-eye only
        print("🔄 DEBUG: Falling back to bird-eye only analysis...")
        return vision_only_completion(prompt, bird_eye_path)
    
    return result, response_time, timeout_occurred

def enhanced_multi_call_vlm_completion(prompt, bird_eye_path, first_person_path):
    """Enhanced multi-modal VLM completion with fallback handling"""
    
    try:
        # Try multimodal completion first
        result, response_time, timeout_occurred = multimodal_vision_completion(prompt, bird_eye_path, first_person_path)
        return result, response_time, timeout_occurred
        
    except Exception as e:
        response_time = 0.0
        print(f"❌ IMAGES-ONLY completion failed after {response_time:.1f}s: {e}")
        debug_print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        raise Exception(f"❌ Vision analysis failed - no text fallback allowed: {e}")

def get_navigation_sequence_with_vlm(screenshot_path, current_task):
    """Get movement sequence from VLM using runtime screenshot + detailed reference image"""
    global LLM_AVAILABLE
    
    # Import required modules at function start
    import bge
    import os
    from backend.app.llm.client import chat_completion, HOST, MODEL
    import base64
    
    if not LLM_AVAILABLE:
        raise Exception("❌ LLM not available - cannot proceed without vision capabilities")

    if not screenshot_path or not os.path.exists(screenshot_path):
        raise Exception(f"❌ No valid screenshot available at: {screenshot_path}")

    # Check for detailed reference image
    vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
    reference_image_path = os.path.join(vesper_root, "blender", "house_layout_reference2.png")
    has_reference = os.path.exists(reference_image_path)
    
    print(f"🖼️ BGE: Reference image available: {has_reference}")
    if has_reference:
        status_print(f"📋 BGE: Using detailed reference + runtime screenshot for enhanced analysis")
    
    # Add imports for enhanced vision handling
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
            # Convert list positions to tuples for hashing
            recent_tuples = [tuple(pos) for pos in recent_positions]
            unique_positions = len(set(recent_tuples))
            if unique_positions <= 3:
                print(f"🔄 BGE: LOOP DETECTED - Only {unique_positions} unique positions in last 6 moves")
                print(f"📍 BGE: Recent path: {recent_positions}")
                
                # Add oscillation detection for same room + repeated movements
                if bge.logic.analysis_count > 8:
                    print(f"🚨 BGE: EXCESSIVE ANALYSIS - {bge.logic.analysis_count} attempts, forcing exploration")
                    # Force the VLM to try a different strategy
                    exploration_context = f"\n\n🚨 CRITICAL: {bge.logic.analysis_count} analysis attempts made. Current room: LIVING_ROOM repeatedly detected. Actor position: {current_pos}. Recent positions: {recent_positions}. MUST try completely different movement direction to escape current area."
                else:
                    exploration_context = ""
            else:
                exploration_context = ""
        else:
            exploration_context = ""
            
        # Check if actor is drifting toward extreme coordinates
        if abs(actor.worldPosition.x) > 10 or abs(actor.worldPosition.y) > 10:
            status_print(f"⚠️ BGE: POSITION ALERT - Actor at extreme coordinates: {current_pos}")

    # Show which image we're analyzing
    image_filename = os.path.basename(screenshot_path)
    debug_print(f"🔍 BGE: Analyzing image: {image_filename} - Actor at {current_pos}")

    # Add context about analysis frequency for VLM
    analysis_context = f"ANALYSIS #{bge.logic.analysis_count}"
    if bge.logic.analysis_count > 10:
        analysis_context += " - MANY ATTEMPTS! Focus on task completion."

    # Create enhanced system prompt based on available images
    if has_reference:
        system_prompt = """You are VESPER navigation AI with access to TWO images:
1. REFERENCE IMAGE: Detailed house layout showing all rooms and furniture clearly
2. RUNTIME IMAGE: Current bird's eye view with pink dot showing actor position

ANALYSIS STRATEGY:
- Use REFERENCE IMAGE to understand overall house layout and identify furniture
- Use RUNTIME IMAGE to locate the pink dot (actor) and determine current room
- Cross-reference between images to make accurate room identification

DUAL-IMAGE ROOM IDENTIFICATION:
REFERENCE IMAGE shows you:
- Complete house layout with all rooms
- Clear furniture details and placement
- Room boundaries and connections
- Kitchen appliances, bedroom furniture, living room setup

RUNTIME IMAGE shows you:
- Pink dot (actor) current position
- Real-time room view (may be lower quality)
- Actual navigation context

CRITICAL PROCESS:
1. Study REFERENCE IMAGE to understand house layout
2. Find pink dot in RUNTIME IMAGE
3. Match pink dot location to room in REFERENCE IMAGE
4. Identify specific furniture near pink dot using both images
5. Navigate based on comprehensive understanding"""
    else:
        system_prompt = """You are VESPER navigation AI. Analyze this bird's eye view screenshot to identify the current room and navigate efficiently."""

    system_prompt += """

CRITICAL ROOM IDENTIFICATION RULES:
BEDROOM = Look for: bed (rectangular furniture), dresser, nightstand, wardrobe, pillows
KITCHEN = Look for: stove/oven, refrigerator (large appliance), sink, countertops, cabinets
LIVING_ROOM = Look for: sofa/couch, coffee table, TV, chairs, entertainment center
OFFICE = Look for: desk, computer, office chair, bookshelf, work area
BATHROOM = Look for: toilet, sink, bathtub, shower, mirror
GARAGE = Look for: car, garage door, tools, workbench
UNKNOWN = If furniture is unclear or you cannot identify room type

FURNITURE RECOGNITION GUIDE:
- BED: Large rectangular furniture, usually with pillows/bedding
- SOFA: Long seating furniture, often L-shaped or rectangular
- STOVE: Cooking appliance with burners/cooking surface
- REFRIGERATOR: Large box-shaped appliance (usually white/metallic)
- TABLE: Flat surface furniture (coffee table = small, dining table = large)
- DRESSER: Tall furniture with drawers (bedroom storage)

The pink dot shows the actor's current position. Identify the room by analyzing furniture NEAR the pink dot."""

    # Add enhanced position context with spatial awareness
    position_context = ""
    if hasattr(bge.logic, 'position_history') and len(bge.logic.position_history) > 1:
        recent_positions = bge.logic.position_history[-3:]  
        position_context = f"\nRECENT POSITIONS: {recent_positions}"
        

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
        
 
        if abs(x) > 5.0 or abs(y) > 5.0:
            position_context += " ⚠️ APPROACHING HOUSE BOUNDARIES!"


    if "bedroom" in current_task.lower():
        target_features = "BED (rectangular furniture), DRESSER/WARDROBE (tall furniture), PILLOWS, or bedroom-specific items"
        completion_criteria = "You must see a BED or bedroom furniture near the pink dot"
    elif "kitchen" in current_task.lower():
        target_features = "STOVE/OVEN (cooking appliances), REFRIGERATOR (large box), SINK, COUNTERTOPS, or kitchen cabinets"
        completion_criteria = "You must see kitchen appliances (stove, oven, fridge) or countertops near the pink dot"
    elif "living room" in current_task.lower() or "living" in current_task.lower():
        target_features = "SOFA/COUCH (seating furniture), COFFEE TABLE, TV, or living room furniture"
        completion_criteria = "You must see living room furniture near the pink dot"
    elif "office" in current_task.lower():
        target_features = "DESK (work surface), COMPUTER, OFFICE CHAIR, BOOKSHELF, or office equipment"
        completion_criteria = "You must see a DESK or office furniture near the pink dot"
    elif "bathroom" in current_task.lower():
        target_features = "TOILET (white porcelain), BATHTUB, SINK, SHOWER, or bathroom fixtures"
        completion_criteria = "You must see bathroom fixtures (toilet, bathtub, sink) near the pink dot"
    elif "garage" in current_task.lower():
        target_features = "CAR (vehicle), GARAGE DOOR, TOOLS, WORKBENCH, or garage equipment"
        completion_criteria = "You must see a CAR or garage equipment near the pink dot"
    else:
        target_features = "Any furniture or room-specific items"
        completion_criteria = "You must identify the correct room type and see appropriate furniture near the pink dot"

    # Create enhanced user prompt with image context
    image_context = ""
    if has_reference:
        image_context = f"""
DUAL-IMAGE ANALYSIS AVAILABLE:
- REFERENCE IMAGE: Detailed house layout (use for furniture identification)
- RUNTIME IMAGE: Current view with pink dot (use for position)

ENHANCED ANALYSIS PROCESS:
1. Study REFERENCE IMAGE to understand complete house layout
2. Identify all furniture and room boundaries in REFERENCE IMAGE
3. Locate pink dot in RUNTIME IMAGE
4. Cross-reference position with REFERENCE IMAGE layout
5. Use both images together for accurate room and furniture identification
"""
    else:
        image_context = "\nSINGLE IMAGE ANALYSIS: Using runtime screenshot only\n"

    user_prompt = f'''TASK: {current_task}
ANALYSIS #{bge.logic.analysis_count} | POSITION: {current_pos}{position_context}
{image_context}
STEP-BY-STEP VISUAL ANALYSIS:

1️. LOCATE PINK DOT: Find the pink/red dot showing actor position
   {f"(Use RUNTIME IMAGE to find pink dot, REFERENCE IMAGE for context)" if has_reference else ""}

2️. FURNITURE SCAN: Look at furniture immediately around the pink dot
   - What furniture is within 2-3 units of the pink dot?
   {f"- Cross-reference furniture details from REFERENCE IMAGE" if has_reference else ""}
   - Is it a BED (bedroom), SOFA (living room), STOVE (kitchen), or unclear?
   - CRITICAL: If image is blurry/unclear, describe what you actually see instead of using template text!

3️. ROOM IDENTIFICATION: Based on furniture near pink dot:
   🛏️ If you see BED/dresser/nightstand → BEDROOM
   🍳 If you see STOVE/refrigerator/sink/counters → KITCHEN  
   🛋️ If you see SOFA/couch/coffee table/TV → LIVING_ROOM
   🏢 If you see DESK/computer/office chair/bookshelf → OFFICE
   🚿 If you see TOILET/bathtub/sink/shower → BATHROOM
   🚗 If you see CAR/garage door/tools/workbench → GARAGE
   ❓ If furniture is unclear/blurry → UNKNOWN

3.5️. OBSTACLE & BOUNDARY CHECK: Before choosing movement direction:
   🚧 OBSTACLE SCAN: Look for furniture, walls, or barriers that block movement paths
   🏠 BOUNDARY CHECK: Ensure pink dot stays inside house walls/enclosed areas
   🚪 PATH FINDING: Identify open floor spaces where movement is safe
   ⚠️ COLLISION AVOIDANCE: Do NOT move through/over furniture pieces
   🔄 ALTERNATE ROUTES: If direct path blocked, find way around obstacles

4️. TASK CHECK: Does current room match task requirement?
   CURRENT TASK: "{current_task}"
   
   COMPREHENSIVE TASK-ROOM MATCHING:
   - Kitchen tasks ("cook", "kitchen") → MUST be in KITCHEN (see stove/refrigerator/sink)
   - Living room tasks ("relax", "living") → MUST be in LIVING_ROOM (see sofa/TV/coffee table)
   - Bathroom tasks ("prepare", "bathroom", "wash") → MUST be in BATHROOM (see toilet/bathtub/sink)
   - Bedroom tasks ("sleep", "bedroom", "rest") → MUST be in BEDROOM (see bed/dresser/nightstand)
   - Office tasks ("work", "office", "study") → MUST be in OFFICE (see desk/computer/chair)
   - Garage tasks ("car", "garage", "park") → MUST be in GARAGE (see car/garage door/tools)
   
5️. NAVIGATION DECISION:
   TASK COMPLETE ONLY IF: Current room type EXACTLY matches task requirement
      - Kitchen task + KITCHEN room + kitchen furniture = task_complete: true
      - Bathroom task + BATHROOM room + bathroom fixtures = task_complete: true
      - Living room task + LIVING_ROOM room + living room furniture = task_complete: true
      - Bedroom task + BEDROOM room + bedroom furniture = task_complete: true
      - Office task + OFFICE room + office furniture = task_complete: true
      - Garage task + GARAGE room + garage equipment = task_complete: true
   
   TASK INCOMPLETE IF: Wrong room or unclear room
      - Kitchen task but in BEDROOM/BATHROOM/LIVING_ROOM/OFFICE/GARAGE = task_complete: false
      - Bathroom task but in KITCHEN/BEDROOM/LIVING_ROOM/OFFICE/GARAGE = task_complete: false
      - Any task but UNKNOWN room = task_complete: false, try movement for clarity

   CRITICAL: NEVER set task_complete: true unless room type perfectly matches task!

FURNITURE EXAMPLES TO RECOGNIZE:
BED: Large rectangular shape, often with pillows/headboard
SOFA: L-shaped or long rectangular seating, multiple cushions
STOVE: Square/rectangular with cooking surfaces/burners
TV: Flat rectangular screen, often on stand or wall
TABLE: Flat surface (coffee table = small round/square, dining = large)
DESK: Flat work surface, often with computer or papers
TOILET: White porcelain fixture, bowl shape
BATHTUB: Large white rectangular basin
CAR: Large vehicle shape in enclosed space
TOOLS: Hanging implements, workbench, garage equipment

CRITICAL: Focus on furniture IMMEDIATELY AROUND the pink dot to determine room type!

NAVIGATION RULES:
- If current room matches task: Use ["STAY"] and set task_complete: true
- If in wrong room but know which direction to go: Use ONE direction like ["LEFT"] or ["UP"]
- From LIVING_ROOM to KITCHEN: Try ["LEFT"] or ["UP"] (kitchen typically connected to living area)
- From any room to BATHROOM: Try ["UP"] or ["RIGHT"] (bathrooms often upstairs/corners)
- From any room to BEDROOM: Try ["UP"] or ["RIGHT"] (bedrooms often upstairs/sides)
- If completely lost or image unclear: Use ["STAY"] and request better view
- NEVER use multiple directions in sequence like ["UP", "DOWN", "LEFT", "RIGHT"]
- ALWAYS try ONE direction at a time for exploration

🚨 CRITICAL SAFETY CONSTRAINTS:
- STAY INSIDE THE HOUSE: Pink dot must remain within indoor areas with visible walls/ceilings
- AVOID FURNITURE OVERLAP: Do NOT move pink dot directly through/over furniture pieces
- RESPECT PHYSICAL BARRIERS: Walls, large furniture, and appliances block movement
- NAVIGATE AROUND OBSTACLES: Move along open floor spaces between furniture
- IF APPROACHING HOUSE EDGE: Immediately change direction to stay inside
- IF FURNITURE BLOCKS PATH: Find alternate route around obstacles

ANTI-OSCILLATION RULES:
- NEVER use template text like "list specific furniture you see near pink dot"
- ALWAYS describe what you actually observe, even if unclear
- If image is blurry, try ONE direction only to get better view
- If stuck for 3+ cycles, try a DIFFERENT direction
- NEVER suggest staying when not in correct room - ALWAYS try movement

JSON Response (REQUIRED FORMAT):
{{
  "current_room": "BEDROOM|KITCHEN|LIVING_ROOM|OFFICE|BATHROOM|GARAGE|UNKNOWN",
  "furniture_visible": ["describe actual furniture you see, not template text"],
  "task_complete": true/false,
  "movement_sequence": ["SINGLE_DIRECTION"] or ["STAY"],
  "reasoning": "FURNITURE SEEN: [actual items]. OBSTACLES: [any blocking furniture/walls]. ROOM: [determined room]. SAFE PATH: [clear direction or blocked]. TASK: [complete/need to move to X]"
}}

🚨 MOVEMENT SAFETY REQUIREMENTS:
- BEFORE choosing direction: Check if path is clear of furniture/walls
- AVOID moving pink dot through solid objects (tables, sofas, appliances, walls)
- STAY within enclosed house areas - do not exit to outdoor/void spaces
- If furniture blocks desired direction, choose alternate route around obstacles
- When in doubt about clear path, use ["STAY"] to avoid collision

⚠️ CRITICAL: YOU MUST RESPOND WITH VALID JSON ONLY - NO ADDITIONAL TEXT!
⚠️ Start your response with {{ and end with }}
⚠️ Do not include explanations outside the JSON structure
⚠️ EXAMPLE: {{"current_room": "LIVING_ROOM", "furniture_visible": ["sofa"], "task_complete": false, "movement_sequence": ["UP"], "reasoning": "In living room, need kitchen, moving UP"}}

Movement options: "UP", "DOWN", "LEFT", "RIGHT", "STAY" ONLY (use ONE direction when unclear!)'''

    # ENHANCED: Get enhanced VLM managers for device interactions and subtasks
    managers = get_enhanced_managers()
    enhanced_vlm_manager = managers.get("vlm_manager")
    casas_subtask_manager = managers.get("subtask_manager")
    first_person_camera = managers.get("first_person_camera")
    multimodal_context = managers.get("multimodal_context")
    
    # Initialize CASAS task if enhanced VLM is available
    task_context = ""
    device_prompts = ""
    if enhanced_vlm_manager and casas_subtask_manager:
        # Start CASAS task tracking
        if not casas_subtask_manager.current_task:
            casas_subtask_manager.start_task(current_task)
        
        # Get current subtask information
        current_subtask = casas_subtask_manager.get_current_subtask()
        task_progress = casas_subtask_manager.get_task_progress()
        
        if current_subtask:
            task_context = f"""
🎯 CASAS SUBTASK TRACKING:
   Current Task: {task_progress['task']}
   Subtask {task_progress['subtask_index'] + 1}/{task_progress['total_subtasks']}: {current_subtask['description']}
   Required Checkpoints: {current_subtask.get('checkpoints', [])}
   Completed Checkpoints: {task_progress['completed_checkpoints']}
   Progress: {task_progress['progress_percentage']:.1f}%
   Estimated Time Remaining: {task_progress['estimated_remaining_time']}s
"""
        
        # Get room-specific device interaction prompts
        if actor:
            # Determine current room for device interactions
            x, y = actor.worldPosition.x, actor.worldPosition.y
            current_room = "Unknown"
            
            if x < -2.0 and y > 1.0:
                current_room = "Kitchen"
            elif x > -1.0 and y > 1.0:
                current_room = "DiningRoom"
            elif x < 0 and y < 1.0:
                current_room = "LivingRoom"
            elif x > 0 and y < 1.0:
                current_room = "Bedroom"
            
            device_prompts = enhanced_vlm_manager.get_interaction_prompts_for_room(current_room)
    
    # Enhanced multi-modal vision context (if available)
    multimodal_visual_context = ""
    first_person_screenshot_path = None
    
    if multimodal_context and first_person_camera:
        try:
            # Get actor orientation for first-person view
            actor_orientation = (0.0, 0.0, 0.0)  # Default
            if actor:
                # Convert BGE orientation to tuple
                orientation_matrix = actor.worldOrientation
                actor_orientation = orientation_matrix.to_euler()
                actor_orientation = (actor_orientation.x, actor_orientation.y, actor_orientation.z)
            
            # Request first-person screenshot (follows bird-eye pattern)
            actor_pos = (actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z) if actor else (0, 0, 0)
            
            # Request first-person screenshot using the same pattern as bird-eye
            from first_person_camera import request_multimodal_navigation_screenshots
            multimodal_capture = request_multimodal_navigation_screenshots(actor_pos, actor_orientation)
            
            if multimodal_capture.get("first_person_path"):
                # Poll for first-person screenshot to be ready
                from first_person_camera import poll_multimodal_navigation_ready
                ready_status = poll_multimodal_navigation_ready(multimodal_capture, timeout_s=8.0)
                
                if ready_status.get("first_person_ready") and ready_status.get("first_person_path"):
                    first_person_screenshot_path = ready_status["first_person_path"]
                    print(f"✅ First-person screenshot ready: {os.path.basename(first_person_screenshot_path)}")
                    
                    multimodal_visual_context = f"""
🎥 ENHANCED MULTI-MODAL VISUAL ANALYSIS:
   • First-person view: Available at actor's eye level ({actor_pos[2] + 1.8:.1f}m height)
   • Bird-eye view: Available from overhead perspective (runtime screenshot)
   • Reference layout: House layout with room labels for spatial understanding
   
📍 VISUAL PERSPECTIVE COMBINATION:
   Actor Position: {actor_pos}
   Actor Orientation: {actor_orientation}
   
🔍 DUAL-VIEW ANALYSIS INSTRUCTIONS:
   1. Use FIRST-PERSON view to identify immediate obstacles, furniture, and room details
   2. Use BIRD-EYE view (pink dot) to understand spatial position and navigation options
   3. Combine both views for comprehensive spatial awareness and obstacle avoidance
   4. First-person shows what actor can actually see and interact with
   5. Bird-eye shows overall position and movement possibilities
   
💡 NAVIGATION ADVANTAGE:
   - First-person: Detailed room identification, obstacle detection, device visibility
   - Bird-eye: Spatial relationships, room transitions, position tracking
   - Combined: Optimal navigation decisions with full environmental awareness
"""
                else:
                    status_print("⚠️ First-person screenshot not ready, using bird-eye only")
            else:
                status_print("⚠️ First-person screenshot request failed, using bird-eye only")
                
        except Exception as e:
            print(f"⚠️ Multi-modal context generation failed: {e}")
            multimodal_visual_context = ""
    
    # ENHANCED: Use IMAGES ONLY - no text fallback
    if has_reference:
        print("🔍 BGE: IMAGES-ONLY Analysis - Using runtime screenshot with reference context...")
        
        # Skip problematic reference image analysis - use runtime image only with enhanced context
        enhanced_prompt = f"""IMPORTANT: You have access to a detailed house layout that shows:
- LIVING ROOM: Contains sofa, coffee table, TV (typically in center-right area)  
- KITCHEN: Contains stove, refrigerator, sink, counters (typically in left area, connected to living room)
- BEDROOM: Contains bed, dresser, nightstand (typically in upper areas)
- BATHROOM: Contains toilet, bathtub, sink (typically smaller rooms, often upstairs)
- OFFICE: Contains desk, computer, office chair (if present)
- GARAGE: Contains car, tools, garage door (if present)

{multimodal_visual_context}

{task_context}

{device_prompts}

{exploration_context}

NAVIGATION HINTS FOR TASK "{current_task}":
🏠 House Layout: Kitchen is typically LEFT or UP from living room center
🎯 Your Goal: Navigate FROM current room TO target room for task completion
📍 Current Analysis: Look at furniture around pink dot to identify current room
🧭 Movement Strategy: If wrong room, try ONE direction toward target (LEFT/UP for kitchen from living room)

CURRENT TASK: {current_task}

NOW ANALYZE this runtime image with the pink dot:

{system_prompt}

{user_prompt}

CRITICAL: Use the runtime image to:
1. Locate the pink dot (actor position)  
2. Identify furniture around the pink dot
3. Match furniture to room type
4. Check for clear movement paths (avoid furniture/walls)
5. Stay inside house boundaries (walls/ceiling visible)
6. Consider device interactions if in correct room for task
7. Make SAFE navigation decision avoiding obstacles

🎮 ENHANCED FEATURES:
- Device Interaction: If in correct room, consider interacting with relevant devices
- Subtask Progress: Track completion of task components and checkpoints
- Multi-Modal Analysis: Use all available visual perspectives for navigation

🚨 RESPOND WITH JSON ONLY - NO EXPLANATORY TEXT OUTSIDE JSON!
🚨 FORMAT: {{"current_room": "ROOM", "furniture_visible": ["items"], "task_complete": false, "movement_sequence": ["DIRECTION"], "reasoning": "brief analysis"}}

IMAGES-ONLY ANALYSIS: Base your response entirely on what you see in this runtime image."""

        print("🔍 BGE: Analyzing runtime image with enhanced layout context...")
        
        # ENHANCED: Always attempt multi-modal analysis for better navigation
        # Try to capture first-person view with shorter timeout
        try:
            # Use off-screen FP capture system first (ChatGPT's solution)
            print("🎥 BGE: Attempting off-screen first-person capture...")
            
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            if actor:
                # Try off-screen capture first
                first_person_screenshot_path = _capture_fp_offscreen(actor, scene, captures_dir)
                
                if not first_person_screenshot_path:
                    print("🔄 BGE: Off-screen capture failed, trying direct camera approach...")
                    # Find the Actor_FPCamera child - try multiple methods
                    fp_camera = None
                    
                    # Method 1: Direct scene lookup
                    fp_camera = scene.objects.get("Actor_FPCamera")
                    if fp_camera:
                        status_print(f"✅ BGE: Found FP camera in scene: {fp_camera.name}")
                    else:
                        # Method 2: Search through actor children
                        if hasattr(actor, 'children'):
                            for child in actor.children:
                                if child.name == "Actor_FPCamera":
                                    fp_camera = child
                                    status_print(f"✅ BGE: Found FP camera child: {child.name}")
                                    break
                        
                        # Method 3: Search all scene objects for camera with Actor_ prefix
                        if not fp_camera:
                            for obj in scene.objects:
                                if obj.name == "Actor_FPCamera" and hasattr(obj, 'camera'):
                                    fp_camera = obj
                                    status_print(f"✅ BGE: Found FP camera in scene objects: {obj.name}")
                                    break
                    
                    if fp_camera and hasattr(fp_camera, 'camera') and fp_camera.camera:
                        status_print(f"✅ BGE: Valid camera object found: {fp_camera.name}")
                        # Continue with camera switching approach
                        first_person_screenshot_path = _capture_with_valid_camera(fp_camera, actor, captures_dir, scene)
                    else:
                        status_print(f"⚠️ BGE: No valid Actor_FPCamera found - first-person view unavailable")
                        first_person_screenshot_path = None
                else:
                    status_print(f"✅ BGE: Off-screen first-person capture successful")
            else:
                status_print("⚠️ BGE: Actor not found - using bird-eye only")
                first_person_screenshot_path = None
        except Exception as e:
            status_print(f"⚠️ BGE: First-person capture error: {e} - using bird-eye only")
            first_person_screenshot_path = None
        
        # Use multi-modal analysis if first-person view is available
        if first_person_screenshot_path and os.path.exists(first_person_screenshot_path):
            print("🎥 BGE: Using DUAL-VIEW analysis (first-person + bird-eye)")
            print(f"   🐦 Bird-eye: {screenshot_path}")
            print(f"   👁️ First-person: {first_person_screenshot_path}")
            response, response_time, timeout_occurred = multimodal_vision_completion(
                enhanced_prompt, screenshot_path, first_person_screenshot_path
            )
        else:
            print("🐦 BGE: Using single bird-eye view analysis")
            response, response_time, timeout_occurred = vision_only_completion(enhanced_prompt, screenshot_path)
        
        status_print("✅ BGE: Enhanced visual analysis completed successfully")
    else:
        # Standard single-image analysis
        print("🔍 BGE: Standard images-only analysis...")
        
        # Build prompt with exploration context
        standard_prompt = f"{system_prompt}\n\n{exploration_context}\n\n{user_prompt}"
        
        response, response_time, timeout_occurred = vision_only_completion(
            standard_prompt,
            screenshot_path
        )
        
        status_print("✅ BGE: Standard vision analysis completed")

    debug_print(f"🔍 BGE: VLM Response → {response[:300]}...")  # Show first 300 chars

    # Parse response with improved error handling and task validation
    result = parse_vlm_response(response, current_task)
    
    # Add timing information to the result
    result['response_time'] = response_time
    result['timeout_occurred'] = timeout_occurred
    
    return result

# =============================
# Enhanced Movement System with Realistic Turning
# =============================

def get_actor_forward_direction(actor):
    """Get the actor's current forward direction vector"""
    # Get the actor's orientation matrix
    orientation = actor.worldOrientation
    # In Blender, the Y-axis points forward in local coordinates
    forward_vector = orientation.col[1]  # Y column is forward
    return forward_vector

def get_actor_heading_angle(actor):
    """Get the actor's heading angle in degrees (0° = North, 90° = East, etc.)"""
    forward_vector = get_actor_forward_direction(actor)
    import math
    # Calculate angle from forward vector
    angle_rad = math.atan2(forward_vector.x, forward_vector.y)
    angle_deg = math.degrees(angle_rad)
    # Normalize to 0-360 degrees
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg

def set_actor_heading_angle(actor, target_angle_deg):
    """Set the actor's heading to a specific angle"""
    import math
    
    # Convert angle to radians
    target_angle_rad = math.radians(target_angle_deg)
    
    # Create rotation matrix for Z-axis rotation (yaw)
    cos_angle = math.cos(target_angle_rad)
    sin_angle = math.sin(target_angle_rad)
    
    # Set the actor's orientation matrix
    # In Blender BGE, orientation matrix columns represent [right, forward, up]
    orientation = actor.worldOrientation
    
    # Set forward direction (Y column)
    orientation.col[1] = [sin_angle, cos_angle, 0]
    # Set right direction (X column) 
    orientation.col[0] = [cos_angle, -sin_angle, 0]
    # Keep up direction (Z column) unchanged
    orientation.col[2] = [0, 0, 1]
    
    actor.worldOrientation = orientation
    print(f"🧭 BGE: Actor heading set to {target_angle_deg:.1f}°")

def update_first_person_camera(actor):
    """Update first-person camera to follow actor movement and rotation"""
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find the first-person camera - try multiple methods
        fp_camera = None
        
        # Method 1: Look for Actor_FPCamera directly in scene
        fp_camera = scene.objects.get("Actor_FPCamera")
        
        # Method 2: Look through actor's children
        if not fp_camera and hasattr(actor, 'children'):
            for child in actor.children:
                if child.name == "Actor_FPCamera":
                    fp_camera = child
                    break
        
        # Method 3: Search all scene objects for FP camera
        if not fp_camera:
            for obj in scene.objects:
                if obj.name == "Actor_FPCamera" and hasattr(obj, 'camera'):
                    fp_camera = obj
                    break
        
        if fp_camera:
            # Update camera position to match actor position with slight height offset
            fp_camera.worldPosition = [
                actor.worldPosition.x,
                actor.worldPosition.y, 
                actor.worldPosition.z + 0.5  # Eye height offset
            ]
            
            # Update camera orientation to match actor orientation
            fp_camera.worldOrientation = actor.worldOrientation.copy()
            
            debug_print(f"🎥 BGE: FP camera updated - pos: [{fp_camera.worldPosition.x:.2f}, {fp_camera.worldPosition.y:.2f}, {fp_camera.worldPosition.z:.2f}]")
            return True
        else:
            debug_print("⚠️ BGE: Actor_FPCamera not found for update")
            return False
            
    except Exception as e:
        debug_print(f"❌ BGE: Failed to update first-person camera: {e}")
        return False

def turn_actor_degrees(actor, degrees):
    """Turn the actor by a specific number of degrees (positive = clockwise)"""
    current_angle = get_actor_heading_angle(actor)
    target_angle = (current_angle + degrees) % 360
    set_actor_heading_angle(actor, target_angle)
    print(f"🔄 BGE: Turned {degrees}° from {current_angle:.1f}° to {target_angle:.1f}°")
    
    # Update first-person camera to follow actor rotation
    update_first_person_camera(actor)

def move_actor_forward(actor, distance=0.3):
    """Move the actor forward in the direction they're facing"""
    forward_vector = get_actor_forward_direction(actor)
    current_pos = actor.worldPosition.copy()
    
    # Calculate new position
    new_pos = current_pos + forward_vector * distance
    
    # Apply boundary checks - Updated to match actual house layout
    HOUSE_BOUNDS = {
        'x_min': -10.0, 'x_max': 10.0,
        'y_min': -5.0, 'y_max': 8.0
    }
    
    # Check boundaries
    if (new_pos.x < HOUSE_BOUNDS['x_min'] or new_pos.x > HOUSE_BOUNDS['x_max'] or
        new_pos.y < HOUSE_BOUNDS['y_min'] or new_pos.y > HOUSE_BOUNDS['y_max']):
        print(f"🚨 BGE: Forward movement blocked by boundary")
        return False
    
    # Apply movement
    actor.worldPosition = new_pos
    print(f"🚶 BGE: Moved forward {distance:.2f}m to [{new_pos.x:.2f}, {new_pos.y:.2f}]")
    
    # Update first-person camera to follow actor movement
    update_first_person_camera(actor)
    
    return True

def execute_enhanced_movement(actor, action):
    """
    Execute enhanced movement with realistic turning and forward motion
    
    Actions:
    - TURN_LEFT: Turn 90° left, then move forward
    - TURN_RIGHT: Turn 90° right, then move forward  
    - FORWARD: Move forward in current direction
    - BACKWARD: Move backward in current direction
    - STAY: Stay in place
    """
    if action == "STAY":
        print("🛑 BGE: Actor staying - task complete!")
        return True
    
    status_print(f"🎮 BGE: Executing enhanced movement: {action}")
    
    if action == "TURN_LEFT":
        # Turn 90 degrees counter-clockwise (left)
        turn_actor_degrees(actor, -90)
        # Then move forward
        return move_actor_forward(actor)
        
    elif action == "TURN_RIGHT":
        # Turn 90 degrees clockwise (right)
        turn_actor_degrees(actor, 90)
        # Then move forward
        return move_actor_forward(actor)
        
    elif action == "FORWARD":
        # Move forward in current direction
        return move_actor_forward(actor)
        
    elif action == "BACKWARD":
        # Move backward (reverse direction)
        return move_actor_forward(actor, -0.3)
        
    else:
        status_print(f"⚠️ BGE: Unknown action: {action}")
        return False

def move_actor(actor, direction, step_size=0.3):
    """
    LEGACY SUPPORT: Old movement function with enhanced realistic movement
    
    This maintains backward compatibility while providing better movement
    """
    if direction == "STAY":
        return execute_enhanced_movement(actor, "STAY")
    
    # Map old directions to new enhanced movements
    direction_mapping = {
        "LEFT": "TURN_LEFT",
        "RIGHT": "TURN_RIGHT", 
        "UP": "FORWARD",
        "DOWN": "BACKWARD"
    }
    
    enhanced_action = direction_mapping.get(direction, direction)
    
    if enhanced_action != direction:
        print(f"🔄 BGE: Converting '{direction}' to enhanced action '{enhanced_action}'")
    
    return execute_enhanced_movement(actor, enhanced_action)
        
    return True


def main():
    """Main BGE navigation function with sequence-based movement (non-blocking screenshots, manual camera settings preserved)"""
    global LLM_AVAILABLE, CASAS_AVAILABLE, MOTION_VALIDATION_AVAILABLE, few_shot_system
    
    controller = bge.logic.getCurrentController()
    scene = bge.logic.getCurrentScene()

    # Find actor
    actor = scene.objects.get("Actor")
    if not actor:
        status_print("❌ BGE: No 'Actor' object found!")
        return

    # Init state once
    if not hasattr(bge.logic, "vesper_nav_init"):
        bge.logic.vesper_nav_init = True
        bge.logic.vesper_current_task_index = 0
        
        # Initialize metrics logging
        bge.logic.metrics_logger = get_metrics_logger()
        
        # Load tasks from vesper_tasks.txt (generated by addon)
        vesper_tasks = load_vesper_tasks()
        bge.logic.vesper_tasks = vesper_tasks if vesper_tasks else ["Go to bedroom", "Cook in kitchen", "Rest in bedroom"]
        
        bge.logic.vesper_movement_queue = []  # sequence of moves
        bge.logic.vesper_sequence_step = 0
        bge.logic.last_screenshot_path = None

        print("🧠 BGE: VESPER Navigation initialized!")
        status_print(f"📋 BGE: Tasks: {bge.logic.vesper_tasks}")
        print(f"📍 BGE: LLM Available: {LLM_AVAILABLE}")
        print(f"🏠 BGE: CASAS Available: {CASAS_AVAILABLE}")
        status_print(f"🎯 BGE: Motion Validation Available: {MOTION_VALIDATION_AVAILABLE}")
        print("🔧 BGE: Camera calibration DISABLED - your manual settings preserved!")
        
        # Initialize MCP Integration
        if MCP_INTEGRATION_AVAILABLE:
            mcp_ready = initialize_mcp_for_bge()
            if mcp_ready:
                status_print("✅ BGE: MCP services ready for navigation")
                
                # Check service status
                services_status = check_mcp_services_status()
                healthy_services = sum(1 for status in services_status.values() if status)
                total_services = len(services_status)
                debug_print(f"🔍 BGE: MCP Services: {healthy_services}/{total_services} healthy")
                
                # Store MCP status in game logic
                bge.logic.mcp_services_available = True
                bge.logic.mcp_services_status = services_status
            else:
                status_print("⚠️ BGE: MCP services not ready - using fallback mode")
                bge.logic.mcp_services_available = False
        else:
            status_print("⚠️ BGE: MCP integration not available")
            bge.logic.mcp_services_available = False
        
        # Initialize Motion Validation System
        if MOTION_VALIDATION_AVAILABLE:
            try:
                import asyncio
                # Run motion validation setup asynchronously
                motion_setup_successful = False
                try:
                    loop = asyncio.get_event_loop()
                    motion_setup_successful = loop.run_until_complete(initialize_motion_validation())
                except RuntimeError:
                    # If no event loop exists, create one
                    motion_setup_successful = asyncio.run(initialize_motion_validation())
                
                if motion_setup_successful:
                    bge.logic.motion_validation_enabled = True
                    print("🎯 BGE: Motion validation sensors deployed successfully")
                else:
                    bge.logic.motion_validation_enabled = False
                    status_print("⚠️ BGE: Motion validation setup failed - continuing without validation")
            except Exception as mv_e:
                status_print(f"⚠️ BGE: Motion validation initialization failed: {mv_e}")
                bge.logic.motion_validation_enabled = False
        else:
            bge.logic.motion_validation_enabled = False
        
        # Initialize CASAS dataset generation if available
        if CASAS_AVAILABLE:
            try:
                # Start CASAS session for current run
                participant_id = "p01"  # Can be parameterized later
                task_id = "t1"  # Will be updated based on current task
                bge.logic.casas_session_id = init_vesper_casas_session(participant_id, task_id)
                bge.logic.casas_participant_id = participant_id
                bge.logic.casas_current_task_index = 0
                bge.logic.casas_datasets_generated = []
                print(f"🏠 BGE: CASAS session started - {bge.logic.casas_session_id}")
                print(f"📊 BGE: Will generate CASAS datasets for {len(bge.logic.vesper_tasks)} tasks")
            except Exception as casas_init_e:
                status_print(f"⚠️ BGE: CASAS initialization failed: {casas_init_e}")
                CASAS_AVAILABLE = False
        
        # ENHANCED: Display screenshot quality recommendations
        print("\n📸 BGE: SCREENSHOT QUALITY RECOMMENDATIONS:")
        print("   💡 For best VLM analysis, ensure:")
        print("   🎯 BirdEyeCamera positioned high (Z > 8) for complete room view")
        print("   📐 Camera lens 35mm+ for wide coverage")
        print("   🖥️ BGE window size 1024x768+ for better resolution")
        print("   🎨 Good lighting in all rooms")
        print("   📏 Actor (pink dot) clearly visible against floor")

        # Initialize first-person camera synchronization
        print("\n🎥 BGE: Setting up first-person camera...")
        if update_first_person_camera(actor):
            status_print("✅ BGE: First-person camera synchronized with actor")
        else:
            status_print("⚠️ BGE: First-person camera setup incomplete")

        # Kick off initial screenshot (non-blocking)
        print("\n📸 BGE: Requesting initial intelligent screenshot...")
        request_intelligent_screenshot()
        return  # yield this tick so a frame can render

    # If a screenshot is pending, poll it
    shot_status = poll_intelligent_screenshot_ready()
    if shot_status is None:
        # Not ready yet; let the engine render another frame
        pass
    elif shot_status == "TIMEOUT":
        # Re-request next frame
        request_intelligent_screenshot()
        return
    else:
        # Ready path
        bge.logic.last_screenshot_path = shot_status

    # Stop if all tasks done
    if bge.logic.vesper_current_task_index >= len(bge.logic.vesper_tasks):
        print("🎉 BGE: ALL TASKS COMPLETED!")
        
        # Log session completion
        if hasattr(bge.logic, 'metrics_logger'):
            bge.logic.metrics_logger._print_task_summary()
        
        return

    current_task = bge.logic.vesper_tasks[bge.logic.vesper_current_task_index]
    
    # Check if this is a new task and log it
    if not hasattr(bge.logic, 'current_task_logged') or bge.logic.current_task_logged != bge.logic.vesper_current_task_index:
        bge.logic.metrics_logger.start_task(current_task, bge.logic.vesper_current_task_index)
        bge.logic.current_task_logged = bge.logic.vesper_current_task_index

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
            # Log screenshot capture
            analysis_count = getattr(bge.logic, 'analysis_count', 0)
            bge.logic.metrics_logger.log_screenshot(bge.logic.last_screenshot_path, analysis_count)
            
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
                    
                    status_print(f"🎯 BGE: Loaded sequence: {bge.logic.vesper_movement_queue}")
                    print(f"🏠 BGE: Room Analysis - Current: {bge.logic.vlm_analysis['current_room']}")
                    print(f"🪑 BGE: Furniture: {bge.logic.vlm_analysis['furniture_visible']}")
                    print(f"💭 BGE: {sequence_result.get('reasoning', 'No reasoning provided')}")
                    
                    # Log LLM response
                    bge.logic.metrics_logger.log_llm_call(
                        sequence_result,
                        bge.logic.vlm_analysis['current_room'],
                        bge.logic.vlm_analysis['furniture_visible'],
                        bge.logic.vlm_analysis['task_complete'],
                        response_time=sequence_result.get('response_time'),
                        timeout=sequence_result.get('timeout_occurred', False)
                    )
                    
                    # Check if VLM says task is complete
                    if bge.logic.vlm_analysis["task_complete"]:
                        status_print(f"🎯 BGE: VLM confirms task complete - actor in correct room!")
                else:
                    raise Exception("❌ VLM did not return movement_sequence - critical error")
            finally:
                # Consume this screenshot; next cycle will take a new one
                bge.logic.last_screenshot_path = None

    # Execute next step if we have a plan
    if bge.logic.vesper_movement_queue:
        next_move = bge.logic.vesper_movement_queue.pop(0)
        bge.logic.vesper_sequence_step += 1

        # Show current heading before movement
        current_heading = get_actor_heading_angle(actor)
        status_print(f"🎮 BGE: Step {bge.logic.vesper_sequence_step}: {next_move}")
        print(f"🧭 BGE: Current heading: {current_heading:.1f}° before movement")
        print(f"📍 Queue: {bge.logic.vesper_movement_queue}")

        old_position = [actor.worldPosition.x, actor.worldPosition.y]
        move_success = move_actor(actor, next_move)
        new_position = [actor.worldPosition.x, actor.worldPosition.y]
        
        # Show heading after movement
        if move_success:
            new_heading = get_actor_heading_angle(actor)
            print(f"🧭 BGE: New heading: {new_heading:.1f}° after movement")
            print(f"📍 BGE: Position: [{new_position[0]:.2f}, {new_position[1]:.2f}]")
            
            # Ensure first-person camera stays synchronized
            update_first_person_camera(actor)
        
        # Motion Validation: Update virtual sensors based on actor position
        if MOTION_VALIDATION_AVAILABLE and getattr(bge.logic, 'motion_validation_enabled', False):
            try:
                import asyncio
                actor_position = (new_position[0], new_position[1])
                
                # Update motion sensors asynchronously
                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(validate_actor_movement(actor_position))
                except RuntimeError:
                    asyncio.run(validate_actor_movement(actor_position))
                
            except Exception as mv_e:
                print(f"⚠️ Motion validation error: {mv_e}")
        
        # Update realistic motion sensor detection system
        try:
            if hasattr(scene, 'vesper_device_manager'):
                scene.vesper_device_manager.update_motion_detection()
            else:
                # Try to access global device manager
                try:
                    from addons.vesper_smart_home import device_manager
                    device_manager.update_motion_detection()
                except ImportError:
                    pass  # Motion detection not available
        except Exception as motion_e:
            pass  # Silent fail to avoid disrupting main navigation
        
        # Log movement step
        current_room = getattr(bge.logic, 'vlm_analysis', {}).get('current_room', 'UNKNOWN')
        bge.logic.metrics_logger.log_step(bge.logic.vesper_sequence_step, next_move, old_position, new_position, current_room)

        # Position drift detection - check if actor is moving to extreme coordinates
        if abs(new_position[0]) > 15 or abs(new_position[1]) > 15:
            print(f"🚨 BGE: EXTREME POSITION DETECTED! Actor at [{new_position[0]:.1f}, {new_position[1]:.1f}]")
            print("🔄 BGE: Position appears outside house - requesting immediate visual re-analysis")
            
            # Log potential failure
            if hasattr(bge.logic, 'metrics_logger') and bge.logic.metrics_logger.current_task_data:
                bge.logic.metrics_logger.complete_task(
                    success=False, 
                    failure_reason="Actor moved to extreme position outside house boundaries",
                    final_position=new_position
                )
            
            bge.logic.vesper_movement_queue = []  # clear current plan
            if not bge.logic._vesper_shot["pending"]:
                request_intelligent_screenshot()
            return

        # Detect if stuck (position didn't change)
        moved_distance = ((new_position[0] - old_position[0])**2 + (new_position[1] - old_position[1])**2)**0.5
        if moved_distance < 0.1 and next_move != "STAY":
            status_print("⚠️ BGE: Actor appears stuck or movement blocked by safety boundaries")
            bge.logic.vesper_movement_queue = []  # trigger replanning
            # Request new screenshot immediately
            if not bge.logic._vesper_shot["pending"]:
                request_intelligent_screenshot()
            return

        # If the short sequence is finished, request a new screenshot for the next cycle
        if not bge.logic.vesper_movement_queue:
            print("📸 BGE: Short sequence completed - requesting NEW intelligent screenshot for re-analysis")
            
            # Enhanced task completion validation
            if next_move == "STAY":
                # Validate task completion based on VLM room analysis
                vlm_analysis = getattr(bge.logic, 'vlm_analysis', {})
                task_complete_confirmed = vlm_analysis.get("task_complete", False)
                current_room = vlm_analysis.get("current_room", "UNKNOWN")
                furniture_visible = vlm_analysis.get("furniture_visible", "None")
                
                if task_complete_confirmed:
                    status_print(f"✅ BGE: Task '{current_task}' VALIDATED - Actor confirmed in correct room!")
                    print(f"🏠 BGE: Final location: {current_room}")
                    print(f"🪑 BGE: Furniture confirmation: {furniture_visible}")
                    
                    # Motion Validation: Cross-validate VLM decision with motion sensors
                    if MOTION_VALIDATION_AVAILABLE and getattr(bge.logic, 'motion_validation_enabled', False):
                        try:
                            validation_result = validate_vlm_decision(current_room, (new_position[0], new_position[1]))
                            
                            if validation_result['validation_success']:
                                print(f"🎯 Motion Validation: ✅ VLM decision CONFIRMED by sensors")
                                print(f"   📍 VLM: {validation_result['vlm_intended']} | Sensors: {validation_result['sensor_detected']}")
                            else:
                                print(f"⚠️ Motion Validation: ❌ VLM/Sensor MISMATCH detected")
                                print(f"   📍 VLM: {validation_result['vlm_intended']} | Sensors: {validation_result['sensor_detected']}")
                                
                            # Store validation result for later analysis
                            if not hasattr(bge.logic, 'validation_results'):
                                bge.logic.validation_results = []
                            bge.logic.validation_results.append(validation_result)
                            
                        except Exception as val_e:
                            print(f"⚠️ VLM validation error: {val_e}")
                    
                    # Log successful task completion
                    bge.logic.metrics_logger.complete_task(
                        success=True, 
                        final_position=new_position
                    )
                    
                    # Generate CASAS dataset for completed task
                    if CASAS_AVAILABLE and hasattr(bge.logic, 'casas_session_id'):
                        try:
                            print(f"🏠 BGE: Generating CASAS events for '{current_task}'")
                            events_generated = execute_vesper_task(current_task)
                            
                            # Save current task dataset
                            task_index = bge.logic.vesper_current_task_index
                            task_id = f"t{task_index + 1}"  # CASAS tasks are t1, t2, t3, etc.
                            
                            # Finalize current task session and start new one for next task
                            dataset_file = finalize_vesper_casas_session()
                            if dataset_file:
                                bge.logic.casas_datasets_generated.append(dataset_file)
                                print(f"💾 BGE: CASAS dataset saved - {dataset_file}")
                            
                            # Initialize next task session if more tasks remain
                            next_task_index = bge.logic.vesper_current_task_index + 1
                            if next_task_index < len(bge.logic.vesper_tasks):
                                next_task_id = f"t{next_task_index + 1}"
                                bge.logic.casas_session_id = init_vesper_casas_session(
                                    bge.logic.casas_participant_id, next_task_id
                                )
                                print(f"🏠 BGE: Started CASAS session for next task: {next_task_id}")
                                
                        except Exception as casas_e:
                            status_print(f"⚠️ BGE: CASAS generation failed: {casas_e}")
                    
                    bge.logic.vesper_current_task_index += 1
                    bge.logic.vesper_sequence_step = 0
                    
                    # Clear VLM analysis for next task
                    bge.logic.vlm_analysis = {}
                else:
                    status_print(f"⚠️ BGE: STAY command but task NOT validated!")
                    print(f"🏠 BGE: Current room: {current_room} (target needed for '{current_task}')")
                    print(f"🔄 BGE: Continuing navigation - need to reach correct room")
                    # Don't advance task index - continue navigation
            else:
                print(f"🔄 BGE: Continuing task '{current_task}' with new analysis cycle")

            # Request the next screenshot right away
            if not bge.logic._vesper_shot["pending"]:
                request_bird_eye_screenshot()
            return

def cleanup_casas_session():
    """Cleanup and finalize CASAS session when navigation ends"""
    global CASAS_AVAILABLE, MOTION_VALIDATION_AVAILABLE
    
    # Cleanup Motion Validation System
    if MOTION_VALIDATION_AVAILABLE and getattr(bge.logic, 'motion_validation_enabled', False):
        try:
            print("🎯 BGE: Cleaning up motion validation system...")
            import asyncio
            
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(cleanup_motion_validation())
            except RuntimeError:
                asyncio.run(cleanup_motion_validation())
                
            status_print("✅ BGE: Motion validation cleanup complete")
            
            # Generate validation report if we have results
            if hasattr(bge.logic, 'validation_results') and bge.logic.validation_results:
                print(f"📊 BGE: VLM Validation Summary:")
                successful_validations = sum(1 for r in bge.logic.validation_results if r['validation_success'])
                total_validations = len(bge.logic.validation_results)
                accuracy = (successful_validations / total_validations) * 100 if total_validations > 0 else 0
                
                print(f"   ✅ Successful validations: {successful_validations}/{total_validations} ({accuracy:.1f}%)")
                print(f"   📍 VLM navigation accuracy validated by motion sensors")
                
        except Exception as mv_cleanup_e:
            status_print(f"⚠️ BGE: Motion validation cleanup error: {mv_cleanup_e}")
    
    if CASAS_AVAILABLE and hasattr(bge.logic, 'casas_session_id') and bge.logic.casas_session_id:
        try:
            print("🏠 BGE: Finalizing CASAS session...")
            dataset_file = finalize_vesper_casas_session()
            if dataset_file:
                bge.logic.casas_datasets_generated.append(dataset_file)
                print(f"💾 BGE: Final CASAS dataset saved - {dataset_file}")
            
            # Show summary of generated datasets
            if hasattr(bge.logic, 'casas_datasets_generated') and bge.logic.casas_datasets_generated:
                print(f"\n📊 BGE: CASAS Generation Summary:")
                print(f"   Generated {len(bge.logic.casas_datasets_generated)} datasets:")
                for i, dataset in enumerate(bge.logic.casas_datasets_generated):
                    dataset_name = os.path.basename(dataset) if dataset else f"dataset_{i+1}"
                    print(f"     {i+1}. {dataset_name}")
                print(f"   📁 Location: casas_testbed/data/vesper_generated/")
                print(f"   🎯 Ready for CASAS evaluation and comparison!")
        except Exception as e:
            status_print(f"⚠️ BGE: CASAS cleanup failed: {e}")



if __name__ == "__main__":
    try:
        main()
    finally:
        # Ensure CASAS session is properly closed
        cleanup_casas_session()
