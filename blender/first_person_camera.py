"""
First-Person Camera Integration for VESPER VLM
==============================================

Provides first-person view capture and integration with the existing VLM system.
Works alongside bird-eye and reference images to provide comprehensive visual context.

IMPLEMENTATION FOLLOWS BIRD-EYE VIEW PATTERN:
- Non-blocking screenshot capture using BGE render
- File-based image storage and retrieval
- Integration with existing vision_only_completion function
"""

import bge
import bge.render
import time
import os
import base64
from typing import Optional, Dict, Any, Tuple, List

class FirstPersonCameraManager:
    """Manages first-person camera for VLM visual input - follows bird-eye pattern"""
    
    def __init__(self):
        self.camera_object = None
        self.capture_width = 1024  # Higher resolution for better VLM analysis
        self.capture_height = 768
        self.last_capture_path = None
        self.capture_history: List[Dict[str, Any]] = []
        self.max_history = 10
        
        # Initialize camera setup
        self._setup_first_person_camera()
        self._init_first_person_shot_state()
    
    def _init_first_person_shot_state(self):
        """Initialize first-person shot state (mirrors bird-eye shot state exactly)"""
        if not hasattr(bge.logic, "_vesper_first_person_shot"):
            bge.logic._vesper_first_person_shot = {
                "pending": False,
                "path": None,
                "start_time": 0.0,
                "tries": 0,
            }
    
    def _setup_first_person_camera(self):
        """Set up first-person camera attached to actor"""
        try:
            # Get the current scene
            scene = bge.logic.getCurrentScene()
            
            # Find the specific Actor_FPCamera for first-person view
            camera_name = "Actor_FPCamera"
            self.camera_object = scene.objects.get(camera_name)
            
            if self.camera_object:
                print(f"🎥 Found Actor_FPCamera for first-person: {self.camera_object.name}")
            else:
                # Try alternative names for first-person camera
                alternative_names = ["FirstPersonCamera", "FPCamera", "ActorCamera"]
                for name in alternative_names:
                    self.camera_object = scene.objects.get(name)
                    if self.camera_object:
                        print(f"🎥 Using alternative first-person camera: {self.camera_object.name}")
                        break
                
                if not self.camera_object:
                    # Look for cameras with FP in the name
                    for obj in scene.objects:
                        if "FP" in obj.name and (hasattr(obj, 'camera') or 'Camera' in obj.name):
                            self.camera_object = obj
                            print(f"🎥 Found FP camera: {self.camera_object.name}")
                            break
                
                if not self.camera_object:
                    print("⚠️ Actor_FPCamera not found - first-person view not available")
                    return
            
            # Configure camera for first-person view
            if self.camera_object:
                print("🎥 First-person camera configured")
                self._attach_camera_to_actor()
            
        except Exception as e:
            print(f"❌ Error setting up first-person camera: {e}")
    
    def _attach_camera_to_actor(self):
        """Attach camera to actor for first-person view"""
        try:
            scene = bge.logic.getCurrentScene()
            
            # Find the actor object
            actor = scene.objects.get("Actor")
            if not actor:
                # Try alternative actor names
                for obj in scene.objects:
                    if "actor" in obj.name.lower() or obj.get("is_actor"):
                        actor = obj
                        break
            
            if actor and self.camera_object:
                # Position camera at actor's head height
                actor_pos = actor.worldPosition
                actor_orient = actor.worldOrientation
                
                # Set camera position slightly above and forward from actor
                head_offset_z = 1.8  # Head height offset
                forward_offset_x = 0.3  # Slight forward offset
                
                camera_position = [
                    actor_pos[0] + forward_offset_x,
                    actor_pos[1],
                    actor_pos[2] + head_offset_z
                ]
                
                self.camera_object.worldPosition = camera_position
                self.camera_object.worldOrientation = actor_orient
                
                print(f"🎥 First-person camera positioned at: {camera_position}")
                
        except Exception as e:
            print(f"❌ Error attaching camera to actor: {e}")

    @staticmethod
    def _try_offscreen_first_person_capture(camera_obj, output_path: str, width: int = 1024, height: int = 768) -> bool:
        """Render first-person view from a specific camera without switching active camera.
        Uses UPBGE/BGE video texture offscreen rendering if available.

        Returns True on success, False otherwise.
        """
        try:
            # Some builds expose offscreen via bge.texture or VideoTexture
            vt = None
            try:
                from bge import texture as vt  # type: ignore
            except Exception:
                try:
                    import VideoTexture as vt  # type: ignore
                except Exception:
                    print("⚠️ VideoTexture not available in this BGE build")
                    return False
            
            if vt is None:
                return False
                
            scene = bge.logic.getCurrentScene()

            # Create offscreen renderer bound to the given camera
            try:
                renderer = vt.ImageRender(scene, camera_obj, width, height)
            except (TypeError, AttributeError):
                try:
                    # Older API without explicit width/height
                    renderer = vt.ImageRender(scene, camera_obj)
                except Exception as e:
                    print(f"⚠️ Failed to create ImageRender: {e}")
                    return False

            # Force one render into the offscreen buffer
            renderer.refresh(True)

            # Try direct save if available
            if hasattr(renderer, 'save'):
                try:
                    renderer.save(output_path)
                    return os.path.exists(output_path) and os.path.getsize(output_path) > 0
                except Exception as e:
                    print(f"⚠️ renderer.save() failed: {e}")

            # Fallback: write raw image buffer if exposed
            if hasattr(renderer, 'image') and renderer.image:
                # Some builds expose vt.saveImage
                if hasattr(vt, 'saveImage'):
                    try:
                        vt.saveImage(renderer.image, output_path)
                        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
                    except Exception as e:
                        print(f"⚠️ vt.saveImage() failed: {e}")

            print("⚠️ Offscreen renderer present but no save method; falling back to active-camera screenshot")
            return False

        except Exception as e:
            print(f"⚠️ Offscreen capture not available: {e}")
            return False
    
    def _captures_dir_first_person(self):
        """Get captures directory for first-person images"""
        vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
        captures_dir = os.path.join(vesper_root, "blender", "captures", "first_person")
        os.makedirs(captures_dir, exist_ok=True)
        return captures_dir
    
    def _next_first_person_screenshot_path(self):
        """Generate next screenshot path for first-person capture"""
        captures_dir = self._captures_dir_first_person()
        existing_files = [f for f in os.listdir(captures_dir) if f.startswith("first-person_") and f.endswith(".png")]
        
        if existing_files:
            # Extract numbers and find the highest
            numbers = []
            for f in existing_files:
                try:
                    num_str = f.replace("first-person_", "").replace(".png", "")
                    numbers.append(int(num_str))
                except ValueError:
                    continue
            
            next_num = max(numbers) + 1 if numbers else 1
        else:
            next_num = 1
        
        return os.path.join(captures_dir, f"first-person_{next_num:04d}.png")
    
    def request_first_person_screenshot(self, actor_position: Tuple[float, float, float], 
                                      actor_orientation: Tuple[float, float, float]) -> Optional[str]:
        """
        Request first-person screenshot using the EXACT same pattern as bird-eye
        Non-blocking: returns path immediately; result is polled via poll_first_person_ready()
        """
        self._init_first_person_shot_state()
        scene = bge.logic.getCurrentScene()
        
        # Update camera position to match actor
        self._update_camera_position(actor_position, actor_orientation)
        
        # Find or setup first-person camera
        if not self.camera_object:
            print("⚠️ BGE: No first-person camera available for screenshot")
            return None

        # Same pattern as bird-eye: optimize camera settings
        try:
            # Enhanced camera switching with retry logic
            switch_attempts = 0
            max_switch_attempts = 3
            switch_success = False
            
            while switch_attempts < max_switch_attempts:
                try:
                    # Find camera with robust search
                    camera_found = None
                    for obj in scene.objects:
                        if obj.name == self.camera_object.name:
                            camera_found = obj
                            break
                    
                    if camera_found:
                        # Set as active camera
                        scene.active_camera = camera_found
                        
                        # Add processing delay
                        import time
                        time.sleep(0.05)
                        
                        # Verify switch worked
                        if scene.active_camera == camera_found:
                            switch_success = True
                            print(f"✅ BGE: First-person camera switch successful (attempt {switch_attempts + 1})")
                            break
                        else:
                            print(f"⚠️ BGE: Camera switch verification failed (attempt {switch_attempts + 1})")
                    else:
                        print(f"⚠️ BGE: Camera not found in scene (attempt {switch_attempts + 1})")
                        
                except Exception as e:
                    print(f"⚠️ BGE: Camera switch attempt {switch_attempts + 1} failed: {e}")
                
                switch_attempts += 1
                if switch_attempts < max_switch_attempts:
                    import time
                    time.sleep(0.1)
            
            if not switch_success:
                print(f"❌ BGE: Failed to switch to first-person camera after {max_switch_attempts} attempts")
                return None
            
            # Optimize camera lens (same as bird-eye optimization)
            if hasattr(self.camera_object, 'lens'):
                original_lens = getattr(self.camera_object, 'lens', 50)
                if self.camera_object.lens != 50:
                    self.camera_object.lens = 50
                    print(f"📷 BGE: Set first-person camera lens to 50mm (was {original_lens})")
            
            # Log camera position (same as bird-eye)
            cam_pos = self.camera_object.worldPosition
            print(f"📷 BGE: First-person camera at [{cam_pos.x:.2f}, {cam_pos.y:.2f}, {cam_pos.z:.2f}]")
            
        except Exception as e:
            print(f"⚠️ BGE: First-person camera optimization error: {e}")
            return None

        # Generate screenshot path (same as bird-eye)
        shot_path = self._next_first_person_screenshot_path()

        # Take screenshot with enhanced retry logic
        try:
            print(f"📸 BGE: Capturing first-person screenshot...")
            print(f"🗂️ BGE: Intended first-person path: {shot_path}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(shot_path), exist_ok=True)
            
            # Enhanced screenshot capture with retry
            capture_attempts = 0
            max_capture_attempts = 3
            capture_success = False
            
            while capture_attempts < max_capture_attempts:
                try:
                    # Force frame processing before screenshot (BGE compatible)
                    # Cannot use scene.render in BGE - use logic updates instead
                    bge.logic.getLogicTicRate()  # Trigger logic update
                    
                    # Wait for rendering to stabilize
                    import time
                    time.sleep(0.1)
                    
                    # Use BGE screenshot method with result tracking
                    screenshot_result = bge.render.makeScreenshot(shot_path)
                    
                    # Check if makeScreenshot returned False (common BGE issue)
                    if screenshot_result is False:
                        print(f"⚠️ BGE: makeScreenshot returned False (attempt {capture_attempts + 1})")
                        # Try alternative screenshot method
                        try:
                            # Force a frame update
                            bge.logic.NextFrame()
                            screenshot_result = bge.render.makeScreenshot(shot_path)
                        except:
                            pass
                    
                    # Extended wait for file write (BGE can be slow)
                    time.sleep(0.3)
                    
                    # Verify file exists and has content
                    if os.path.exists(shot_path) and os.path.getsize(shot_path) > 0:
                        file_size = os.path.getsize(shot_path)
                        print(f"✅ BGE: First-person screenshot captured: {file_size} bytes (attempt {capture_attempts + 1})")
                        capture_success = True
                        break
                    else:
                        print(f"⚠️ BGE: Screenshot file not created or empty (attempt {capture_attempts + 1}, result: {screenshot_result})")
                        print(f"📄 BGE: Exists={os.path.exists(shot_path)} Size={(os.path.getsize(shot_path) if os.path.exists(shot_path) else 0)} Path={shot_path}")
                        # Clean up empty file if it exists
                        if os.path.exists(shot_path):
                            try:
                                os.remove(shot_path)
                            except:
                                pass
                        
                except Exception as e:
                    print(f"⚠️ BGE: Screenshot capture attempt {capture_attempts + 1} failed: {e}")
                
                capture_attempts += 1
                if capture_attempts < max_capture_attempts:
                    import time
                    time.sleep(0.5)  # Longer delay between attempts
            
            if not capture_success:
                print(f"❌ BGE: First-person screenshot capture failed after {max_capture_attempts} attempts")
                return None
            
        except Exception as e:
            print(f"❌ BGE: First-person screenshot capture failed: {e}")
            return None

        # Update shot state (mirrors bird-eye implementation exactly)
        st = bge.logic._vesper_first_person_shot
        st["pending"] = True
        st["path"] = shot_path
        st["start_time"] = time.time()
        st["tries"] += 1

        return shot_path
    
    def poll_first_person_ready(self, min_bytes: int = 2500, timeout_s: float = 5.0) -> Optional[str]:
        """
        Poll for first-person screenshot completion using EXACT same pattern as bird-eye
        Returns: screenshot path if ready, None if still pending, "TIMEOUT" if timed out
        """
        self._init_first_person_shot_state()
        st = bge.logic._vesper_first_person_shot
        
        if not st["pending"]:
            return None

        # Check if file exists and is ready (same logic as bird-eye)
        p = st["path"]
        if p and os.path.exists(p):
            try:
                size = os.path.getsize(p)
                if size >= min_bytes:
                    st["pending"] = False
                    filename = os.path.basename(p)
                    print(f"📸 First-person screenshot ready: {filename} ({size} bytes)")
                    self.last_capture_path = p
                    
                    # Add to capture history
                    capture_record = {
                        "timestamp": time.time(),
                        "path": p,
                        "size": size
                    }
                    self.capture_history.append(capture_record)
                    if len(self.capture_history) > self.max_history:
                        self.capture_history.pop(0)
                    
                    return p
                else:
                    print(f"⏳ BGE: First-person screenshot still rendering... ({size}/{min_bytes} bytes)")
            except Exception as e:
                print(f"⚠️ BGE: First-person screenshot error: {e}")

        # Check timeout (same as bird-eye)
        if time.time() - st["start_time"] > timeout_s:
            st["pending"] = False
            print(f"⏰ BGE: First-person screenshot timeout after {timeout_s}s")
            return "TIMEOUT"
        
        return None
    
    def _update_camera_position(self, actor_position: Tuple[float, float, float],
                              actor_orientation: Tuple[float, float, float]):
        """Update camera position to match actor's perspective"""
        try:
            if not self.camera_object:
                return
            
            # Calculate head position with proper height
            head_height = 1.8  # Typical human head height
            forward_offset = 0.2  # Slight forward offset to avoid clipping
            
            camera_pos = [
                actor_position[0] + forward_offset,
                actor_position[1], 
                actor_position[2] + head_height
            ]
            
            self.camera_object.worldPosition = camera_pos
            
            # Set camera orientation to match actor's facing direction
            self.camera_object.worldOrientation = actor_orientation
            
        except Exception as e:
            print(f"❌ Error updating first-person camera position: {e}")
    
    def get_last_capture_path(self) -> Optional[str]:
        """Get the path of the last captured first-person screenshot"""
        return self.last_capture_path
    
    def get_capture_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent capture history"""
        return self.capture_history[-limit:]
    
    def generate_first_person_description(self, position: Tuple[float, float, float]) -> str:
        """Generate textual description of what the first-person view should show"""
        
        # Determine room based on position
        x, y, z = position
        
        # Room determination logic (adjust based on your house layout)
        if x < -2.0 and y > 1.0:
            room = "Kitchen"
            description = "First-person view from kitchen showing cabinets, appliances, sink, and counter space. Actor can see cooking equipment and food preparation areas."
        elif x > -1.0 and y > 1.0:
            room = "Dining Room"
            description = "First-person view from dining room showing dining table, chairs, and phone area. Actor can see eating space and communication devices."
        elif x < 0 and y < 1.0:
            room = "Living Room"
            description = "First-person view from living room showing sofa, coffee table, TV, and seating area. Actor can see entertainment and relaxation space."
        elif x > 0 and y < 1.0:
            room = "Bedroom"
            description = "First-person view from bedroom showing bed, dresser, and personal items. Actor can see sleeping and storage areas."
        else:
            room = "Central Area"
            description = "First-person view from central area with multiple room connections visible. Actor can see pathways to different rooms."
        
        return f"{description} Position: ({x:.1f}, {y:.1f}, {z:.1f}) in {room}."

class MultiModalVLMContext:
    """Combines first-person, bird-eye, and reference images for comprehensive VLM input"""
    
    def __init__(self, first_person_manager: FirstPersonCameraManager):
        self.first_person_manager = first_person_manager
        self.bird_eye_cache = None
        self.reference_image_cache = None
    
    def generate_comprehensive_visual_prompt(self, 
                                           actor_position: Tuple[float, float, float],
                                           actor_orientation: Tuple[float, float, float],
                                           bird_eye_path: str,
                                           task_description: str) -> str:
        """Generate VLM prompt that incorporates both first-person and bird-eye views"""
        
        # Get first-person description
        first_person_desc = self.first_person_manager.generate_first_person_description(actor_position)
        
        # Generate comprehensive prompt
        prompt_parts = [
            "🤖 VESPER Multi-Modal Navigation System",
            "=" * 50,
            "",
            f"📋 CURRENT TASK: {task_description}",
            "",
            "👁️ DUAL VISUAL ANALYSIS:",
            f"   🎥 FIRST-PERSON VIEW: {first_person_desc}",
            f"   🐦 BIRD-EYE VIEW: Top-down navigation view with pink dot at ({actor_position[0]:.1f}, {actor_position[1]:.1f})",
            "",
            "🧭 ACTOR STATUS:",
            f"   Position: {actor_position}",
            f"   Orientation: {actor_orientation}",
            "",
            "🔍 ANALYSIS INSTRUCTIONS:",
            "   1. Use FIRST-PERSON view to identify immediate obstacles, furniture, and room details",
            "   2. Use BIRD-EYE view to understand overall position, room layout, and navigation options",  
            "   3. Combine both perspectives for optimal navigation decisions",
            "   4. First-person view shows what actor can see and interact with",
            "   5. Bird-eye view shows spatial relationships and movement options",
            "",
            "💡 NAVIGATION STRATEGY:",
            "   - First-person: Check for obstacles, identify current room features",
            "   - Bird-eye: Plan movement direction, avoid furniture collisions", 
            "   - Combined: Make informed decisions based on both perspectives",
            "",
            "🎯 RESPOND WITH JSON NAVIGATION DECISION:",
            '   {"current_room": "ROOM", "furniture_visible": ["items"], "task_complete": false, "movement_sequence": ["DIRECTION"], "reasoning": "analysis"}',
            ""
        ]
        
        return "\n".join(prompt_parts)
    
    def capture_multimodal_screenshots(self, actor_position: Tuple[float, float, float],
                                     actor_orientation: Tuple[float, float, float]) -> Dict[str, Optional[str]]:
        """Capture both first-person and bird-eye screenshots using sequential system"""
        
        try:
            # Use the new sequential dual camera system
            from sequential_dual_camera import start_dual_camera_capture
            
            result = start_dual_camera_capture(actor_position, actor_orientation)
            
            if result["success"]:
                return {
                    "first_person_path": None,  # Will be available after polling
                    "bird_eye_path": result.get("bird_eye_path"),
                    "status": "sequential_pending",
                    "sequential_status": result["status"]
                }
            else:
                print(f"❌ Sequential dual capture failed to start: {result.get('error', 'Unknown')}")
                return {
                    "first_person_path": None,
                    "bird_eye_path": None,
                    "status": "failed",
                    "error": result.get('error', 'Sequential capture failed')
                }
                
        except ImportError:
            print("⚠️ Sequential dual camera not available, falling back to old method")
            
            # Fallback to original method
            results = {
                "first_person_path": None,
                "bird_eye_path": None,
                "status": "pending"
            }
            
            # Request first-person screenshot
            try:
                fp_path = self.first_person_manager.request_first_person_screenshot(
                    actor_position, actor_orientation
                )
                if fp_path:
                    results["first_person_path"] = fp_path
                    print(f"🎥 First-person screenshot requested: {os.path.basename(fp_path)}")
            except Exception as e:
                print(f"❌ First-person screenshot request failed: {e}")
            
            # Request bird-eye screenshot
            try:
                from llm_bge_navigation import request_bird_eye_screenshot
                be_path = request_bird_eye_screenshot()
                if be_path:
                    results["bird_eye_path"] = be_path
                    print(f"🐦 Bird-eye screenshot requested: {os.path.basename(be_path)}")
            except Exception as e:
                print(f"❌ Bird-eye screenshot request failed: {e}")
            
            return results
    
    def poll_multimodal_ready(self, capture_results: Dict[str, Optional[str]], 
                            timeout_s: float = 10.0) -> Dict[str, Any]:
        """Poll for both screenshots to be ready - supports sequential and legacy modes"""
        
        # Check if using sequential capture system
        if capture_results.get("status") == "sequential_pending":
            return self._poll_sequential_capture(timeout_s)
        
        # Legacy polling for backward compatibility
        return self._poll_legacy_capture(capture_results, timeout_s)
    
    def _poll_sequential_capture(self, timeout_s: float) -> Dict[str, Any]:
        """Poll sequential dual camera capture"""
        
        try:
            from sequential_dual_camera import poll_dual_camera_capture
            
            start_time = time.time()
            
            while time.time() - start_time < timeout_s:
                result = poll_dual_camera_capture()
                
                if result["status"] == "complete":
                    print("🎉 Sequential dual capture completed successfully")
                    return {
                        "first_person_ready": True,
                        "bird_eye_ready": True,
                        "first_person_path": result["first_person_path"],
                        "bird_eye_path": result["bird_eye_path"],
                        "timeout": False,
                        "sequential": True,
                        "capture_time": result.get("capture_time", 0)
                    }
                elif not result["success"]:
                    print(f"❌ Sequential capture failed: {result.get('error', 'Unknown')}")
                    return {
                        "first_person_ready": False,
                        "bird_eye_ready": False,
                        "first_person_path": None,
                        "bird_eye_path": None,
                        "timeout": False,
                        "error": result.get("error", "Sequential capture failed"),
                        "sequential": True
                    }
                
                # Still in progress
                time.sleep(0.2)
            
            # Timeout
            print(f"⏰ Sequential capture timeout after {timeout_s}s")
            return {
                "first_person_ready": False,
                "bird_eye_ready": False,
                "first_person_path": None,
                "bird_eye_path": None,
                "timeout": True,
                "sequential": True
            }
            
        except ImportError:
            print("⚠️ Sequential capture not available during polling")
            return {
                "first_person_ready": False,
                "bird_eye_ready": False,
                "first_person_path": None,
                "bird_eye_path": None,
                "timeout": True,
                "error": "Sequential system unavailable"
            }
    
    def _poll_legacy_capture(self, capture_results: Dict[str, Optional[str]], 
                           timeout_s: float) -> Dict[str, Any]:
        """Legacy polling method for backward compatibility"""
        
        start_time = time.time()
        status = {
            "first_person_ready": False,
            "bird_eye_ready": False,
            "first_person_path": None,
            "bird_eye_path": None,
            "timeout": False
        }
        
        while time.time() - start_time < timeout_s:
            # Check first-person screenshot
            if capture_results["first_person_path"] and not status["first_person_ready"]:
                fp_result = self.first_person_manager.poll_first_person_ready()
                if fp_result and fp_result != "TIMEOUT":
                    status["first_person_ready"] = True
                    status["first_person_path"] = fp_result
                    print("✅ First-person screenshot ready")
            
            # Check bird-eye screenshot
            if capture_results["bird_eye_path"] and not status["bird_eye_ready"]:
                try:
                    from llm_bge_navigation import poll_screenshot_ready
                    be_result = poll_screenshot_ready()
                    if be_result and be_result != "TIMEOUT":
                        status["bird_eye_ready"] = True
                        status["bird_eye_path"] = be_result
                        print("✅ Bird-eye screenshot ready")
                except Exception as e:
                    print(f"⚠️ Bird-eye poll error: {e}")
            
            # Check if both are ready
            if status["first_person_ready"] and status["bird_eye_ready"]:
                print("🎉 Both screenshots ready for multi-modal analysis")
                return status
            
            time.sleep(0.1)  # Brief pause before next check
        
        # Timeout occurred
        status["timeout"] = True
        print(f"⏰ Multi-modal screenshot polling timeout after {timeout_s}s")
        return status

# Global first-person camera manager
first_person_camera = FirstPersonCameraManager()
multimodal_vlm_context = MultiModalVLMContext(first_person_camera)

def get_first_person_camera():
    """Get the global first-person camera manager"""
    return first_person_camera

def get_multimodal_vlm_context():
    """Get the global multi-modal VLM context manager"""
    return multimodal_vlm_context

def initialize_first_person_system():
    """Initialize the first-person camera system"""
    global first_person_camera, multimodal_vlm_context
    
    try:
        first_person_camera = FirstPersonCameraManager()
        multimodal_vlm_context = MultiModalVLMContext(first_person_camera)
        print("🎥 First-person camera system initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize first-person system: {e}")
        return False

# ===== INTEGRATION FUNCTIONS FOR MAIN NAVIGATION SYSTEM =====

def request_multimodal_navigation_screenshots(actor_position: Tuple[float, float, float],
                                            actor_orientation: Tuple[float, float, float]) -> Dict[str, Any]:
    """
    Request both first-person and bird-eye screenshots for enhanced VLM navigation
    Returns capture request results that can be polled for completion
    """
    global multimodal_vlm_context
    
    if not multimodal_vlm_context:
        # Fallback to bird-eye only
        try:
            from llm_bge_navigation import request_bird_eye_screenshot
            be_path = request_bird_eye_screenshot()
            return {
                "first_person_path": None,
                "bird_eye_path": be_path,
                "multimodal_available": False,
                "status": "bird_eye_only"
            }
        except Exception as e:
            print(f"❌ Fallback bird-eye screenshot failed: {e}")
            return {"status": "failed"}
    
    # Request both screenshots
    return multimodal_vlm_context.capture_multimodal_screenshots(actor_position, actor_orientation)

def poll_multimodal_navigation_ready(capture_results: Dict[str, Any], 
                                   timeout_s: float = 10.0) -> Dict[str, Any]:
    """
    Poll for multi-modal screenshots to be ready
    Returns status with paths to ready screenshots
    """
    global multimodal_vlm_context
    
    if not multimodal_vlm_context or capture_results.get("status") == "bird_eye_only":
        # Fallback to bird-eye polling only
        try:
            from llm_bge_navigation import poll_screenshot_ready
            be_result = poll_screenshot_ready(timeout_s=timeout_s)
            return {
                "bird_eye_ready": be_result is not None and be_result != "TIMEOUT",
                "bird_eye_path": be_result if be_result != "TIMEOUT" else None,
                "first_person_ready": False,
                "first_person_path": None,
                "multimodal_available": False
            }
        except Exception as e:
            print(f"❌ Fallback bird-eye polling failed: {e}")
            return {"bird_eye_ready": False, "first_person_ready": False}
    
    # Poll for both screenshots
    return multimodal_vlm_context.poll_multimodal_ready(capture_results, timeout_s)


def capture_immediate_first_person_view(actor_position, actor_orientation):
    """Immediate first-person capture that uses one-frame deferred request/poll.
    Tries offscreen first; if unavailable, switches active camera, defers 1 frame, then captures.
    """
    import time

    try:
        # Reset any stuck sequential dual camera capture states
        try:
            from sequential_dual_camera import force_reset_dual_camera_capture
            force_reset_dual_camera_capture()
            print("🔄 BGE: Reset sequential dual camera system")
        except:
            pass  # Ignore if not available
        
        scene = bge.logic.getCurrentScene()

        # Locate the FP camera
        first_person_camera = scene.objects.get("Actor_FPCamera")
        if not first_person_camera:
            for name in ["FPCamera", "FirstPersonCamera", "ActorCamera"]:
                first_person_camera = scene.objects.get(name)
                if first_person_camera:
                    print(f"🎥 Using alternative first-person camera: {name}")
                    break
        if not first_person_camera:
            for obj in scene.objects:
                if "FP" in obj.name and (hasattr(obj, 'camera') or 'Camera' in obj.name):
                    first_person_camera = obj
                    print(f"🎥 Found FP camera: {obj.name}")
                    break
        if not first_person_camera:
            print("⚠️ First-person camera not found")
            return {"success": False, "error": "Camera not found"}

        # Position and lens
        if hasattr(actor_position, '__iter__'):
            first_person_camera.worldPosition = [actor_position[0], actor_position[1], actor_position[2] + 1.7]
        if hasattr(actor_orientation, '__iter__'):
            first_person_camera.worldOrientation = actor_orientation
        if hasattr(first_person_camera, 'lens'):
            try:
                if first_person_camera.lens != 50.0:
                    first_person_camera.lens = 50.0
            except Exception:
                pass

        # Try offscreen first
        captures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures", "first_person")
        os.makedirs(captures_dir, exist_ok=True)
        existing = [f for f in os.listdir(captures_dir) if f.startswith("first-person_") and f.endswith(".png")]
        if existing:
            nums = []
            for f in existing:
                try:
                    nums.append(int(f.replace("first-person_", "").replace(".png", "")))
                except ValueError:
                    pass
            next_num = max(nums) + 1 if nums else 1
        else:
            next_num = 1
        output_path = os.path.join(captures_dir, f"first-person_{next_num:04d}.png")

        # Skip offscreen capture - it's causing "bytes-like object" errors in BGE
        # if FirstPersonCameraManager._try_offscreen_first_person_capture(first_person_camera, output_path, 1024, 768):
        #     print(f"📸 Offscreen first-person capture saved: {output_path}")
        #     return {"success": True, "path": output_path}
        
        print("🎯 Using BGE screenshot method instead of offscreen capture")

        # Use staged request/poll approach
        mgr = get_first_person_camera()
        req_path = mgr.request_first_person_screenshot(actor_position, actor_orientation)
        if not req_path:
            return {"success": False, "error": "Request failed"}

        # Poll synchronously for a short timeout
        start = time.time()
        while time.time() - start < 5.0:
            result = mgr.poll_first_person_ready()
            if result and result != "TIMEOUT":
                return {"success": True, "path": result}
            if result == "TIMEOUT":
                break
            time.sleep(0.05)
        return {"success": False, "error": "Timeout or invalid file"}

    except Exception as e:
        print(f"❌ First-person capture failed: {e}")
        return {"success": False, "error": str(e)}
