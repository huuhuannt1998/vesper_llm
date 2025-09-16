"""
Frame-Based Dual Camera System
==============================

Alternative approach: Capture different camera views on alternating frames
to work around BGE's single active camera limitation.
"""

import bge
import time
import os
from typing import Dict, Optional, Tuple

class FrameBasedDualCapture:
    """
    Manages dual camera capture across multiple frames
    """
    
    def __init__(self):
        self.capture_state = {
            "active": False,
            "frame_count": 0,
            "bird_eye_captured": False,
            "first_person_captured": False,
            "bird_eye_path": None,
            "first_person_path": None,
            "actor_position": None,
            "actor_orientation": None,
            "original_camera": None
        }
    
    def start_frame_capture(self, actor_position: Tuple[float, float, float], 
                           actor_orientation: Tuple[float, float, float]) -> bool:
        """
        Start frame-based dual capture
        Call this once, then call update_frame_capture() each frame until complete
        """
        if self.capture_state["active"]:
            return False
        
        scene = bge.logic.getCurrentScene()
        
        self.capture_state.update({
            "active": True,
            "frame_count": 0,
            "bird_eye_captured": False,
            "first_person_captured": False,
            "bird_eye_path": None,
            "first_person_path": None,
            "actor_position": actor_position,
            "actor_orientation": actor_orientation,
            "original_camera": scene.active_camera
        })
        
        print("🎬 Starting frame-based dual capture...")
        return True
    
    def update_frame_capture(self) -> Dict[str, any]:
        """
        Call this every frame until capture is complete
        
        Returns:
            {
                "complete": bool,
                "bird_eye_path": str or None,
                "first_person_path": str or None,
                "frame": int
            }
        """
        if not self.capture_state["active"]:
            return {"complete": True, "bird_eye_path": None, "first_person_path": None, "frame": 0}
        
        frame = self.capture_state["frame_count"]
        scene = bge.logic.getCurrentScene()
        
        try:
            # Frame 0: Capture bird-eye
            if frame == 0 and not self.capture_state["bird_eye_captured"]:
                self._capture_bird_eye_frame(scene)
            
            # Frame 2: Capture first-person (give 1 frame gap)
            elif frame == 2 and not self.capture_state["first_person_captured"]:
                self._capture_first_person_frame(scene)
            
            # Frame 4: Check completion and cleanup
            elif frame >= 4:
                return self._finalize_capture(scene)
        
        except Exception as e:
            print(f"❌ Frame capture error: {e}")
            self._reset_capture(scene)
            return {"complete": True, "bird_eye_path": None, "first_person_path": None, "error": str(e)}
        
        self.capture_state["frame_count"] += 1
        
        return {
            "complete": False,
            "bird_eye_path": self.capture_state["bird_eye_path"],
            "first_person_path": self.capture_state["first_person_path"],
            "frame": frame
        }
    
    def _capture_bird_eye_frame(self, scene):
        """Capture bird-eye view on current frame"""
        bird_camera = scene.objects.get("BirdEyeCamera")
        if not bird_camera:
            raise Exception("BirdEyeCamera not found")
        
        scene.active_camera = bird_camera
        
        # Generate path
        bird_dir = os.path.join(os.path.dirname(__file__), "captures", "bird_eye")
        os.makedirs(bird_dir, exist_ok=True)
        
        existing = [f for f in os.listdir(bird_dir) if f.startswith("bird-eye_") and f.endswith(".png")]
        next_num = len(existing) + 1
        
        bird_path = os.path.join(bird_dir, f"bird-eye_{next_num:03d}.png")
        
        bge.render.makeScreenshot(bird_path)
        
        self.capture_state["bird_eye_captured"] = True
        self.capture_state["bird_eye_path"] = bird_path
        
        print(f"🐦 Frame {self.capture_state['frame_count']}: Bird-eye captured")
    
    def _capture_first_person_frame(self, scene):
        """Capture first-person view on current frame"""
        fp_camera = scene.objects.get("Actor_FPCamera")
        if not fp_camera:
            raise Exception("Actor_FPCamera not found")
        
        # Position camera
        pos = self.capture_state["actor_position"]
        orient = self.capture_state["actor_orientation"]
        
        if pos:
            fp_camera.worldPosition = [pos[0], pos[1], pos[2] + 1.7]
        if orient:
            fp_camera.worldOrientation = orient
        if hasattr(fp_camera, 'lens'):
            fp_camera.lens = 50.0
        
        scene.active_camera = fp_camera
        
        # Generate path
        fp_dir = os.path.join(os.path.dirname(__file__), "captures", "first_person")
        os.makedirs(fp_dir, exist_ok=True)
        
        existing = [f for f in os.listdir(fp_dir) if f.startswith("first-person_") and f.endswith(".png")]
        next_num = len(existing) + 1
        
        fp_path = os.path.join(fp_dir, f"first-person_{next_num:04d}.png")
        
        bge.render.makeScreenshot(fp_path)
        
        self.capture_state["first_person_captured"] = True
        self.capture_state["first_person_path"] = fp_path
        
        print(f"👁️ Frame {self.capture_state['frame_count']}: First-person captured")
    
    def _finalize_capture(self, scene):
        """Complete the capture process"""
        result = {
            "complete": True,
            "bird_eye_path": self.capture_state["bird_eye_path"],
            "first_person_path": self.capture_state["first_person_path"],
            "frame": self.capture_state["frame_count"]
        }
        
        if self.capture_state["bird_eye_captured"] and self.capture_state["first_person_captured"]:
            print("✅ Frame-based dual capture complete!")
        else:
            print("⚠️ Frame-based capture incomplete")
        
        self._reset_capture(scene)
        return result
    
    def _reset_capture(self, scene):
        """Reset capture state and restore original camera"""
        try:
            if self.capture_state["original_camera"]:
                scene.active_camera = self.capture_state["original_camera"]
        except Exception:
            pass
        
        self.capture_state["active"] = False

# Global instance
frame_capture_manager = FrameBasedDualCapture()

def start_frame_based_capture(actor_position, actor_orientation):
    """Start frame-based capture"""
    return frame_capture_manager.start_frame_capture(actor_position, actor_orientation)

def update_frame_based_capture():
    """Update frame-based capture (call every frame)"""
    return frame_capture_manager.update_frame_capture()
