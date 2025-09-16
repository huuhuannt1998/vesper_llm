"""
Quick Sequential Dual Camera Integration
=======================================

Simple integration for capturing both camera views rapidly in sequence
"""

import bge
import os
import time
from typing import Dict, Tuple, Optional

def capture_dual_views_quick(actor_position: Tuple[float, float, float], 
                           actor_orientation: Tuple[float, float, float]) -> Dict[str, any]:
    """
    Quick sequential capture of both bird-eye and first-person views
    
    This happens fast enough (within ~2 frames) to be considered simultaneous
    """
    
    scene = bge.logic.getCurrentScene()
    original_camera = scene.active_camera
    
    result = {
        "success": False,
        "bird_eye_path": None,
        "first_person_path": None,
        "timing": {},
        "error": None
    }
    
    start_time = time.time()
    
    try:
        # === BIRD-EYE CAPTURE ===
        t1 = time.time()
        
        bird_camera = scene.objects.get("BirdEyeCamera")
        if not bird_camera:
            raise Exception("BirdEyeCamera not found")
        
        scene.active_camera = bird_camera
        
        # Generate bird-eye path
        captures_dir = os.path.join(os.path.dirname(__file__), "captures")
        bird_dir = os.path.join(captures_dir, "bird_eye")
        os.makedirs(bird_dir, exist_ok=True)
        
        # Find next number
        existing = [f for f in os.listdir(bird_dir) if f.startswith("bird-eye_")]
        next_num = len(existing) + 1
        bird_path = os.path.join(bird_dir, f"bird-eye_{next_num:03d}.png")
        
        bge.render.makeScreenshot(bird_path)
        result["bird_eye_path"] = bird_path
        
        t2 = time.time()
        result["timing"]["bird_eye"] = t2 - t1
        
        # === FIRST-PERSON CAPTURE ===
        fp_camera = scene.objects.get("Actor_FPCamera") 
        if not fp_camera:
            raise Exception("Actor_FPCamera not found")
        
        # Position first-person camera
        fp_camera.worldPosition = [
            actor_position[0],
            actor_position[1], 
            actor_position[2] + 1.7  # Eye level
        ]
        fp_camera.worldOrientation = actor_orientation
        
        if hasattr(fp_camera, 'lens'):
            fp_camera.lens = 50.0
        
        scene.active_camera = fp_camera
        
        # Generate first-person path  
        fp_dir = os.path.join(captures_dir, "first_person")
        os.makedirs(fp_dir, exist_ok=True)
        
        existing = [f for f in os.listdir(fp_dir) if f.startswith("first-person_")]
        next_num = len(existing) + 1
        fp_path = os.path.join(fp_dir, f"first-person_{next_num:04d}.png")
        
        bge.render.makeScreenshot(fp_path)
        result["first_person_path"] = fp_path
        
        t3 = time.time()
        result["timing"]["first_person"] = t3 - t2
        result["timing"]["total"] = t3 - start_time
        
        result["success"] = True
        
        print(f"✅ Dual capture complete in {result['timing']['total']:.3f}s")
        print(f"   🐦 Bird-eye: {os.path.basename(bird_path)}")
        print(f"   👁️ First-person: {os.path.basename(fp_path)}")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Dual capture failed: {e}")
        
    finally:
        # Always restore original camera
        try:
            scene.active_camera = original_camera
        except Exception:
            pass
    
    return result


def wait_for_files(paths: list, timeout: float = 5.0, min_size: int = 1000) -> bool:
    """Wait for screenshot files to be written"""
    start = time.time()
    
    while time.time() - start < timeout:
        all_ready = True
        for path in paths:
            if not os.path.exists(path) or os.path.getsize(path) < min_size:
                all_ready = False
                break
        
        if all_ready:
            return True
        
        time.sleep(0.05)  # Check every 50ms
    
    return False


# === INTEGRATION WRAPPER ===

def request_dual_capture_immediate(actor_position: Tuple[float, float, float], 
                                 actor_orientation: Tuple[float, float, float]) -> Dict[str, any]:
    """
    Main entry point for immediate dual camera capture
    Use this in your navigation loop when you want both perspectives
    """
    
    result = capture_dual_views_quick(actor_position, actor_orientation)
    
    if result["success"]:
        # Wait for both files to be ready
        paths = [result["bird_eye_path"], result["first_person_path"]]
        if wait_for_files(paths):
            print("📁 Both screenshots verified ready")
            return result
        else:
            print("⚠️ Screenshot verification timeout")
            result["success"] = False
            result["error"] = "File verification timeout"
    
    return result
