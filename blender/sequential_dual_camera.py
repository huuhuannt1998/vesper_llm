"""
Sequential Dual Camera Capture System for BGE
============================================

BGE limitation: Only one active camera can capture screenshots at a time.
Solution: Sequential capture with proper timing and camera switching.

This module provides a robust dual-camera capture system that:
1. Captures bird-eye view first
2. Waits for completion
3. Switches to first-person camera
4. Captures first-person view
5. Restores original camera state
"""

import bge
import time
import os
from typing import Dict, Optional, Tuple, Any

class SequentialDualCameraCapture:
    """Manages sequential capture from two cameras in BGE"""
    
    def __init__(self):
        self.capture_state = {
            "active": False,
            "stage": "idle",  # idle, bird_eye, first_person, complete
            "bird_eye_path": None,
            "first_person_path": None,
            "original_camera": None,
            "start_time": None,
            "actor_position": None,
            "actor_orientation": None
        }
        self.capture_timeout = 15.0  # Total timeout for both captures
    
    def force_reset_capture_state(self):
        """Force reset the capture state - use when system gets stuck"""
        try:
            # Restore original camera if needed
            if self.capture_state["original_camera"]:
                scene = bge.logic.getCurrentScene()
                scene.active_camera = self.capture_state["original_camera"]
                print("🔄 Sequential Camera: Original camera restored")
        except Exception as e:
            print(f"⚠️ Sequential Camera: Error restoring camera: {e}")
        
        # Reset all state
        self.capture_state = {
            "active": False,
            "stage": "idle",
            "bird_eye_path": None,
            "first_person_path": None,
            "original_camera": None,
            "start_time": None,
            "actor_position": None,
            "actor_orientation": None
        }
        print("✅ Sequential Camera: Capture state force reset complete")
        
    def start_dual_capture(self, actor_position: Tuple[float, float, float],
                          actor_orientation: Tuple[float, float, float]) -> Dict[str, Any]:
        """
        Start sequential dual camera capture
        Returns: Initial status dict
        """
        
        if self.capture_state["active"]:
            return {
                "success": False,
                "error": "Capture already in progress",
                "status": "busy"
            }
        
        # Initialize capture state
        scene = bge.logic.getCurrentScene()
        self.capture_state.update({
            "active": True,
            "stage": "bird_eye",
            "bird_eye_path": None,
            "first_person_path": None,
            "original_camera": scene.active_camera,
            "start_time": time.time(),
            "actor_position": actor_position,
            "actor_orientation": actor_orientation
        })
        
        print("🎬 Starting sequential dual camera capture...")
        
        # Start with bird-eye capture
        bird_eye_result = self._capture_bird_eye()
        
        if bird_eye_result["success"]:
            self.capture_state["bird_eye_path"] = bird_eye_result["path"]
            print(f"🐦 Bird-eye capture initiated: {os.path.basename(bird_eye_result['path'])}")
            
            return {
                "success": True,
                "status": "bird_eye_pending",
                "bird_eye_path": bird_eye_result["path"],
                "message": "Bird-eye capture started, use poll_dual_capture() to check progress"
            }
        else:
            self._reset_capture_state()
            return {
                "success": False,
                "error": f"Bird-eye capture failed: {bird_eye_result.get('error', 'Unknown')}",
                "status": "failed"
            }
    
    def poll_dual_capture(self) -> Dict[str, Any]:
        """
        Poll the progress of dual camera capture
        Returns: Current status and paths when ready
        """
        
        if not self.capture_state["active"]:
            return {
                "success": False,
                "error": "No capture in progress",
                "status": "idle"
            }
        
        # Check timeout
        if time.time() - self.capture_state["start_time"] > self.capture_timeout:
            self._reset_capture_state()
            return {
                "success": False,
                "error": "Dual capture timeout",
                "status": "timeout"
            }
        
        current_stage = self.capture_state["stage"]
        
        if current_stage == "bird_eye":
            return self._poll_bird_eye_stage()
        elif current_stage == "first_person":
            return self._poll_first_person_stage()
        elif current_stage == "complete":
            return self._finalize_capture()
        else:
            self._reset_capture_state()
            return {
                "success": False,
                "error": f"Unknown stage: {current_stage}",
                "status": "error"
            }
    
    def _poll_bird_eye_stage(self) -> Dict[str, Any]:
        """Poll bird-eye capture completion"""
        
        # Check if bird-eye screenshot is ready
        bird_eye_path = self.capture_state["bird_eye_path"]
        
        if self._is_screenshot_ready(bird_eye_path):
            print("✅ Bird-eye capture complete, starting first-person capture...")
            
            # Start first-person capture
            self.capture_state["stage"] = "first_person"
            first_person_result = self._capture_first_person()
            
            if first_person_result["success"]:
                self.capture_state["first_person_path"] = first_person_result["path"]
                print(f"👁️ First-person capture initiated: {os.path.basename(first_person_result['path'])}")
                
                return {
                    "success": True,
                    "status": "first_person_pending",
                    "bird_eye_path": bird_eye_path,
                    "bird_eye_ready": True,
                    "first_person_path": first_person_result["path"],
                    "first_person_ready": False,
                    "message": "Bird-eye complete, first-person pending"
                }
            else:
                self._reset_capture_state()
                return {
                    "success": False,
                    "error": f"First-person capture failed: {first_person_result.get('error', 'Unknown')}",
                    "status": "failed",
                    "bird_eye_path": bird_eye_path,
                    "bird_eye_ready": True
                }
        else:
            return {
                "success": True,
                "status": "bird_eye_pending", 
                "bird_eye_path": bird_eye_path,
                "bird_eye_ready": False,
                "message": "Bird-eye capture still pending"
            }
    
    def _poll_first_person_stage(self) -> Dict[str, Any]:
        """Poll first-person capture completion"""
        
        first_person_path = self.capture_state["first_person_path"]
        
        if self._is_screenshot_ready(first_person_path):
            print("✅ First-person capture complete!")
            self.capture_state["stage"] = "complete"
            return self._finalize_capture()
        else:
            return {
                "success": True,
                "status": "first_person_pending",
                "bird_eye_path": self.capture_state["bird_eye_path"],
                "bird_eye_ready": True,
                "first_person_path": first_person_path,
                "first_person_ready": False,
                "message": "First-person capture still pending"
            }
    
    def _finalize_capture(self) -> Dict[str, Any]:
        """Finalize and return both capture results"""
        
        result = {
            "success": True,
            "status": "complete",
            "bird_eye_path": self.capture_state["bird_eye_path"],
            "bird_eye_ready": True,
            "first_person_path": self.capture_state["first_person_path"],
            "first_person_ready": True,
            "message": "Both captures completed successfully",
            "capture_time": time.time() - self.capture_state["start_time"]
        }
        
        print(f"🎉 Dual camera capture complete in {result['capture_time']:.1f}s")
        print(f"   🐦 Bird-eye: {os.path.basename(result['bird_eye_path'])}")
        print(f"   👁️ First-person: {os.path.basename(result['first_person_path'])}")
        
        self._reset_capture_state()
        return result
    
    def _capture_bird_eye(self) -> Dict[str, Any]:
        """Capture bird-eye screenshot using existing system"""
        
        try:
            # Use existing bird-eye capture function
            from llm_bge_navigation import request_bird_eye_screenshot
            
            shot_path = request_bird_eye_screenshot()
            
            if shot_path:
                return {
                    "success": True,
                    "path": shot_path
                }
            else:
                return {
                    "success": False,
                    "error": "Bird-eye screenshot request failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Bird-eye capture exception: {e}"
            }
    
    def _capture_first_person(self) -> Dict[str, Any]:
        """Capture first-person screenshot with proper camera positioning"""
        
        try:
            scene = bge.logic.getCurrentScene()
            
            # Find Actor_FPCamera
            first_person_camera = scene.objects.get("Actor_FPCamera")
            
            if not first_person_camera:
                # Try alternatives
                for name in ["FPCamera", "FirstPersonCamera", "ActorCamera"]:
                    first_person_camera = scene.objects.get(name)
                    if first_person_camera:
                        break
                
                # Last resort: search for FP cameras
                if not first_person_camera:
                    for obj in scene.objects:
                        if "FP" in obj.name and (hasattr(obj, 'camera') or 'Camera' in obj.name):
                            first_person_camera = obj
                            break
            
            if not first_person_camera:
                return {
                    "success": False,
                    "error": "First-person camera not found"
                }
            
            # Position camera at actor eye level
            actor_pos = self.capture_state["actor_position"]
            actor_orient = self.capture_state["actor_orientation"]
            
            if actor_pos:
                # Set camera position (eye level)
                first_person_camera.worldPosition = [
                    actor_pos[0],
                    actor_pos[1], 
                    actor_pos[2] + 1.7  # Human eye height
                ]
            
            if actor_orient:
                # Set camera orientation to match actor
                first_person_camera.worldOrientation = actor_orient
            
            # Switch to first-person camera
            scene.active_camera = first_person_camera
            
            # Configure camera for realistic first-person view
            if hasattr(first_person_camera, 'lens'):
                first_person_camera.lens = 50.0  # Standard 50mm lens
            
            # Generate file path
            captures_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "captures", 
                "first_person"
            )
            os.makedirs(captures_dir, exist_ok=True)
            
            # Find next available number
            existing_files = [f for f in os.listdir(captures_dir) 
                            if f.startswith("first-person_") and f.endswith(".png")]
            
            if existing_files:
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
            
            shot_path = os.path.join(captures_dir, f"first-person_{next_num:04d}.png")
            
            # Capture screenshot
            bge.render.makeScreenshot(shot_path)
            
            print(f"📷 First-person screenshot requested: {shot_path}")
            
            return {
                "success": True,
                "path": shot_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"First-person capture exception: {e}"
            }
    
    def _is_screenshot_ready(self, path: Optional[str], min_bytes: int = 2500) -> bool:
        """Check if screenshot file is ready and has sufficient content"""
        
        if not path or not os.path.exists(path):
            return False
        
        try:
            size = os.path.getsize(path)
            return size >= min_bytes
        except:
            return False
    
    def _reset_capture_state(self):
        """Reset capture state and restore original camera"""
        
        try:
            # Restore original camera if needed
            if self.capture_state["original_camera"]:
                scene = bge.logic.getCurrentScene()
                scene.active_camera = self.capture_state["original_camera"]
                print("🔄 Original camera restored")
        except Exception as e:
            print(f"⚠️ Error restoring camera: {e}")
        
        self.capture_state = {
            "active": False,
            "stage": "idle",
            "bird_eye_path": None,
            "first_person_path": None,
            "original_camera": None,
            "start_time": None,
            "actor_position": None,
            "actor_orientation": None
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current capture status"""
        
        return {
            "active": self.capture_state["active"],
            "stage": self.capture_state["stage"],
            "bird_eye_ready": bool(self.capture_state["bird_eye_path"] and 
                                 self._is_screenshot_ready(self.capture_state["bird_eye_path"])),
            "first_person_ready": bool(self.capture_state["first_person_path"] and 
                                     self._is_screenshot_ready(self.capture_state["first_person_path"])),
            "elapsed_time": time.time() - self.capture_state["start_time"] if self.capture_state["start_time"] else 0
        }

# Global instance for BGE
sequential_dual_camera = SequentialDualCameraCapture()

def force_reset_dual_camera_capture():
    """Force reset the dual camera capture system when stuck"""
    sequential_dual_camera.force_reset_capture_state()

def start_dual_camera_capture(actor_position: Tuple[float, float, float],
                            actor_orientation: Tuple[float, float, float]) -> Dict[str, Any]:
    """
    Start sequential dual camera capture
    
    Args:
        actor_position: (x, y, z) position of actor
        actor_orientation: (rx, ry, rz) orientation of actor
    
    Returns:
        Status dict with success/error information
    """
    return sequential_dual_camera.start_dual_capture(actor_position, actor_orientation)

def poll_dual_camera_capture() -> Dict[str, Any]:
    """
    Poll dual camera capture progress
    
    Returns:
        Status dict with current progress and paths when ready
    """
    return sequential_dual_camera.poll_dual_capture()

def get_dual_camera_status() -> Dict[str, Any]:
    """Get current dual camera capture status"""
    return sequential_dual_camera.get_status()

def is_dual_capture_active() -> bool:
    """Check if dual capture is currently active"""
    return sequential_dual_camera.capture_state["active"]

# Convenience function for simple usage
def capture_dual_view_blocking(actor_position: Tuple[float, float, float],
                             actor_orientation: Tuple[float, float, float],
                             timeout: float = 15.0) -> Dict[str, Any]:
    """
    Blocking dual camera capture with automatic polling
    
    Args:
        actor_position: Actor position
        actor_orientation: Actor orientation  
        timeout: Maximum wait time
    
    Returns:
        Final result with both image paths or error
    """
    
    # Start capture
    start_result = start_dual_camera_capture(actor_position, actor_orientation)
    
    if not start_result["success"]:
        return start_result
    
    # Poll until complete or timeout
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        poll_result = poll_dual_camera_capture()
        
        if poll_result["status"] == "complete":
            return poll_result
        elif not poll_result["success"]:
            return poll_result
        
        time.sleep(0.2)  # Brief pause between polls
    
    # Timeout
    return {
        "success": False,
        "error": "Blocking capture timeout",
        "status": "timeout"
    }

print("✅ Sequential Dual Camera Capture System loaded")
