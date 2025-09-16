"""
Sequential Dual Camera Capture for BGE
======================================

Since BGE can only have one active camera at a time, this module captures:
1. Bird-eye view first
2. Immediately switches to first-person 
3. Captures first-person view
4. Returns both paths

This happens fast enough to be considered "simultaneous" for VLM purposes.
"""

import bge
import time
import os
from typing import Dict, Optional, Tuple

def capture_both_views_sequential(actor_position: Tuple[float, float, float], 
                                actor_orientation: Tuple[float, float, float]) -> Dict[str, any]:
    """
    Capture both bird-eye and first-person views sequentially in rapid succession
    
    Returns:
        {
            "success": bool,
            "bird_eye_path": str or None,
            "first_person_path": str or None,
            "error": str or None
        }
    """
    
    scene = bge.logic.getCurrentScene()
    original_camera = scene.active_camera
    
    result = {
        "success": False,
        "bird_eye_path": None,
        "first_person_path": None,
        "error": None
    }
    
    try:
        # === STEP 1: Capture Bird-Eye View ===
        print("📸 Sequential: Capturing bird-eye view...")
        
        bird_eye_camera = scene.objects.get("BirdEyeCamera")
        if not bird_eye_camera:
            raise Exception("BirdEyeCamera not found")
        
        # Switch to bird-eye camera
        scene.active_camera = bird_eye_camera
        
        # Generate bird-eye path
        bird_eye_dir = os.path.join(os.path.dirname(__file__), "captures", "bird_eye")
        os.makedirs(bird_eye_dir, exist_ok=True)
        
        existing_bird = [f for f in os.listdir(bird_eye_dir) if f.startswith("bird-eye_") and f.endswith(".png")]
        if existing_bird:
            nums = []
            for f in existing_bird:
                try:
                    nums.append(int(f.replace("bird-eye_", "").replace(".png", "")))
                except ValueError:
                    pass
            next_num = max(nums) + 1 if nums else 1
        else:
            next_num = 1
        
        bird_eye_path = os.path.join(bird_eye_dir, f"bird-eye_{next_num:03d}.png")
        
        # Capture bird-eye
        bge.render.makeScreenshot(bird_eye_path)
        print(f"🐦 Bird-eye captured: {os.path.basename(bird_eye_path)}")
        
        # === STEP 2: Capture First-Person View ===
        print("📸 Sequential: Capturing first-person view...")
        
        first_person_camera = scene.objects.get("Actor_FPCamera")
        if not first_person_camera:
            raise Exception("Actor_FPCamera not found")
        
        # Position first-person camera at actor location
        if actor_position:
            first_person_camera.worldPosition = [
                actor_position[0],
                actor_position[1], 
                actor_position[2] + 1.7  # Eye level
            ]
        
        if actor_orientation:
            first_person_camera.worldOrientation = actor_orientation
        
        # Configure camera
        if hasattr(first_person_camera, 'lens'):
            first_person_camera.lens = 50.0  # Natural perspective
        
        # Switch to first-person camera
        scene.active_camera = first_person_camera
        
        # Generate first-person path
        fp_dir = os.path.join(os.path.dirname(__file__), "captures", "first_person")
        os.makedirs(fp_dir, exist_ok=True)
        
        existing_fp = [f for f in os.listdir(fp_dir) if f.startswith("first-person_") and f.endswith(".png")]
        if existing_fp:
            nums = []
            for f in existing_fp:
                try:
                    nums.append(int(f.replace("first-person_", "").replace(".png", "")))
                except ValueError:
                    pass
            next_num = max(nums) + 1 if nums else 1
        else:
            next_num = 1
        
        fp_path = os.path.join(fp_dir, f"first-person_{next_num:04d}.png")
        
        # Capture first-person
        bge.render.makeScreenshot(fp_path)
        print(f"👁️ First-person captured: {os.path.basename(fp_path)}")
        
        # === SUCCESS ===
        result.update({
            "success": True,
            "bird_eye_path": bird_eye_path,
            "first_person_path": fp_path
        })
        
        print(f"✅ Sequential dual capture complete!")
        
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ Sequential capture failed: {e}")
    
    finally:
        # Always restore original camera
        try:
            if original_camera:
                scene.active_camera = original_camera
                print("🔄 Original camera restored")
        except Exception:
            pass
    
    return result


def wait_for_both_screenshots(bird_eye_path: str, fp_path: str, timeout: float = 10.0) -> bool:
    """
    Wait for both screenshot files to be written and have reasonable size
    """
    start_time = time.time()
    min_size = 1000  # Minimum file size in bytes
    
    while time.time() - start_time < timeout:
        bird_ready = (os.path.exists(bird_eye_path) and 
                     os.path.getsize(bird_eye_path) > min_size)
        fp_ready = (os.path.exists(fp_path) and 
                   os.path.getsize(fp_path) > min_size)
        
        if bird_ready and fp_ready:
            print(f"✅ Both screenshots ready!")
            print(f"   🐦 Bird-eye: {os.path.getsize(bird_eye_path)} bytes")
            print(f"   👁️ First-person: {os.path.getsize(fp_path)} bytes")
            return True
        
        time.sleep(0.1)
    
    print(f"⏰ Screenshot timeout after {timeout}s")
    return False


# === Integration Functions ===

def request_dual_screenshot(actor_position: Tuple[float, float, float], 
                          actor_orientation: Tuple[float, float, float]) -> Dict[str, any]:
    """
    Main entry point for dual camera capture
    """
    return capture_both_views_sequential(actor_position, actor_orientation)


def get_latest_screenshots() -> Dict[str, str]:
    """
    Get paths to the most recent screenshots from both cameras
    """
    result = {"bird_eye": None, "first_person": None}
    
    # Get latest bird-eye
    bird_dir = os.path.join(os.path.dirname(__file__), "captures", "bird_eye")
    if os.path.exists(bird_dir):
        bird_files = [f for f in os.listdir(bird_dir) if f.startswith("bird-eye_") and f.endswith(".png")]
        if bird_files:
            latest_bird = max(bird_files, key=lambda f: os.path.getctime(os.path.join(bird_dir, f)))
            result["bird_eye"] = os.path.join(bird_dir, latest_bird)
    
    # Get latest first-person
    fp_dir = os.path.join(os.path.dirname(__file__), "captures", "first_person")
    if os.path.exists(fp_dir):
        fp_files = [f for f in os.listdir(fp_dir) if f.startswith("first-person_") and f.endswith(".png")]
        if fp_files:
            latest_fp = max(fp_files, key=lambda f: os.path.getctime(os.path.join(fp_dir, f)))
            result["first_person"] = os.path.join(fp_dir, latest_fp)
    
    return result
