# Simple First-Person Camera Fix - BGE Compatible
import bge
import os
import time

def simple_first_person_screenshot(actor_position, actor_orientation):
    """
    SIMPLIFIED: First-person screenshot using exact bird-eye pattern
    No complex retry logic, just basic camera switch + screenshot
    """
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find first-person camera
        fp_camera = None
        for obj in scene.objects:
            if obj.name == "Actor_FPCamera":
                fp_camera = obj
                break
        
        if not fp_camera:
            print("❌ Simple FP: Actor_FPCamera not found")
            return None
            
        # Store original camera
        original_camera = scene.active_camera
        
        # Position first-person camera at actor's eye level
        if hasattr(actor_position, '__iter__'):
            fp_camera.worldPosition = [
                actor_position[0], 
                actor_position[1], 
                actor_position[2] + 1.7  # Eye height
            ]
        
        # Set orientation to match actor
        if hasattr(actor_orientation, '__iter__'):
            fp_camera.worldOrientation = actor_orientation
        
        # Switch camera (simple assignment like bird-eye)
        scene.active_camera = fp_camera
        time.sleep(0.05)  # Brief processing delay
        
        # Verify camera switch
        if scene.active_camera != fp_camera:
            print("❌ Simple FP: Camera switch failed")
            scene.active_camera = original_camera
            return None
            
        print(f"✅ Simple FP: Camera switched to first-person")
        print(f"📷 Simple FP: Camera at [{fp_camera.worldPosition.x:.2f}, {fp_camera.worldPosition.y:.2f}, {fp_camera.worldPosition.z:.2f}]")
        
        # Generate screenshot path
        captures_dir = os.path.join(os.path.dirname(__file__), "captures", "first_person")
        os.makedirs(captures_dir, exist_ok=True)
        shot_path = os.path.join(captures_dir, f"simple_fp_{int(time.time())}.png")
        
        print(f"📸 Simple FP: Capturing to {shot_path}")
        
        # Use exact same screenshot method as bird-eye
        bge.render.makeScreenshot(shot_path)
        time.sleep(0.2)  # Wait for file write
        
        # Restore original camera immediately
        scene.active_camera = original_camera
        
        # Check result
        if os.path.exists(shot_path) and os.path.getsize(shot_path) > 1000:
            print(f"✅ Simple FP: Screenshot captured: {os.path.getsize(shot_path)} bytes")
            return shot_path
        else:
            print(f"❌ Simple FP: Screenshot failed - file not created")
            return None
            
    except Exception as e:
        print(f"❌ Simple FP: Error: {e}")
        # Ensure camera is restored
        try:
            scene.active_camera = original_camera
        except:
            pass
        return None
