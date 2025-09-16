"""
Debug First-Person Camera Position and Orientation
=================================================

This script helps diagnose Actor_FPCamera positioning issues by:
1. Checking the current camera setup
2. Verifying actor position 
3. Testing camera orientation
4. Comparing with expected first-person view
"""

import bge
import time

def debug_first_person_camera():
    """Debug the first-person camera setup"""
    
    scene = bge.logic.getCurrentScene()
    
    print("=" * 60)
    print("🔍 FIRST-PERSON CAMERA DEBUG")
    print("=" * 60)
    
    # Find all cameras
    print("\n📹 ALL CAMERAS IN SCENE:")
    cameras = []
    for obj in scene.objects:
        if hasattr(obj, 'camera') or 'Camera' in obj.name or 'camera' in obj.name.lower():
            cameras.append(obj)
            print(f"   📷 {obj.name}")
            print(f"      Position: [{obj.worldPosition.x:.2f}, {obj.worldPosition.y:.2f}, {obj.worldPosition.z:.2f}]")
            print(f"      Orientation: [{obj.worldOrientation[0][0]:.2f}, {obj.worldOrientation[0][1]:.2f}, {obj.worldOrientation[0][2]:.2f}]")
            if hasattr(obj, 'lens'):
                print(f"      Lens: {obj.lens}")
    
    # Find Actor
    print("\n👤 ACTOR STATUS:")
    actor = scene.objects.get("Actor")
    if actor:
        print(f"   Position: [{actor.worldPosition.x:.2f}, {actor.worldPosition.y:.2f}, {actor.worldPosition.z:.2f}]")
        print(f"   Orientation: [{actor.worldOrientation[0][0]:.2f}, {actor.worldOrientation[0][1]:.2f}, {actor.worldOrientation[0][2]:.2f}]")
    else:
        print("   ❌ Actor not found!")
    
    # Check Actor_FPCamera specifically
    print("\n🎥 ACTOR_FPCAMERA ANALYSIS:")
    fp_camera = scene.objects.get("Actor_FPCamera")
    if fp_camera:
        print(f"   ✅ Found: {fp_camera.name}")
        print(f"   Position: [{fp_camera.worldPosition.x:.2f}, {fp_camera.worldPosition.y:.2f}, {fp_camera.worldPosition.z:.2f}]")
        print(f"   Orientation Matrix:")
        for i, row in enumerate(fp_camera.worldOrientation):
            print(f"      Row {i}: [{row[0]:.3f}, {row[1]:.3f}, {row[2]:.3f}]")
        
        if hasattr(fp_camera, 'lens'):
            print(f"   Lens: {fp_camera.lens}")
        
        # Check if it's properly configured as a camera
        if hasattr(fp_camera, 'camera'):
            print(f"   ✅ Has camera component")
        else:
            print(f"   ❌ Missing camera component!")
        
        # Calculate expected position relative to actor
        if actor:
            expected_pos = [
                actor.worldPosition.x + 0.2,  # forward offset
                actor.worldPosition.y,
                actor.worldPosition.z + 1.8   # head height
            ]
            print(f"   Expected position: [{expected_pos[0]:.2f}, {expected_pos[1]:.2f}, {expected_pos[2]:.2f}]")
            
            # Check distance from expected
            import math
            distance = math.sqrt(
                (fp_camera.worldPosition.x - expected_pos[0])**2 +
                (fp_camera.worldPosition.y - expected_pos[1])**2 +
                (fp_camera.worldPosition.z - expected_pos[2])**2
            )
            print(f"   Distance from expected: {distance:.2f}")
            
            if distance > 0.5:
                print("   ⚠️ Camera position seems incorrect!")
    else:
        print("   ❌ Actor_FPCamera not found!")
    
    # Check active camera
    print(f"\n🎬 CURRENT ACTIVE CAMERA:")
    active_cam = scene.active_camera
    if active_cam:
        print(f"   Name: {active_cam.name}")
        print(f"   Position: [{active_cam.worldPosition.x:.2f}, {active_cam.worldPosition.y:.2f}, {active_cam.worldPosition.z:.2f}]")
    else:
        print("   ❌ No active camera!")
    
    # Test camera switching
    print(f"\n🔄 TESTING CAMERA SWITCH:")
    if fp_camera:
        original_camera = scene.active_camera
        try:
            scene.active_camera = fp_camera
            new_active = scene.active_camera
            print(f"   Switch result: {new_active.name if new_active else 'None'}")
            print(f"   Success: {new_active == fp_camera}")
            
            # Restore
            if original_camera:
                scene.active_camera = original_camera
                print(f"   Restored to: {scene.active_camera.name}")
        except Exception as e:
            print(f"   ❌ Switch failed: {e}")
    
    print("\n" + "=" * 60)

def test_fp_camera_capture():
    """Test immediate first-person capture"""
    
    print("\n🧪 TESTING FIRST-PERSON CAPTURE:")
    
    scene = bge.logic.getCurrentScene()
    fp_camera = scene.objects.get("Actor_FPCamera")
    actor = scene.objects.get("Actor")
    
    if not fp_camera:
        print("❌ No Actor_FPCamera found!")
        return
    
    if not actor:
        print("❌ No Actor found!")
        return
    
    # Position camera at actor's eye level
    eye_height = 1.7
    fp_camera.worldPosition = [
        actor.worldPosition.x,
        actor.worldPosition.y, 
        actor.worldPosition.z + eye_height
    ]
    
    # Set camera to look forward (0 degree rotation)
    import mathutils
    fp_camera.worldOrientation = mathutils.Matrix.Identity(3)
    
    print(f"📍 Positioned camera at: [{fp_camera.worldPosition.x:.2f}, {fp_camera.worldPosition.y:.2f}, {fp_camera.worldPosition.z:.2f}]")
    
    # Switch to FP camera
    original_camera = scene.active_camera
    scene.active_camera = fp_camera
    
    print(f"🎥 Active camera: {scene.active_camera.name}")
    
    # Take screenshot
    import os
    captures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures", "debug")
    os.makedirs(captures_dir, exist_ok=True)
    
    test_path = os.path.join(captures_dir, f"fp_debug_test_{int(time.time())}.png")
    
    try:
        bge.render.makeScreenshot(test_path)
        print(f"📸 Screenshot saved: {test_path}")
        
        # Wait for file
        for i in range(50):  # 5 seconds max
            if os.path.exists(test_path):
                size = os.path.getsize(test_path)
                if size > 1000:
                    print(f"✅ Screenshot ready: {size} bytes")
                    break
            time.sleep(0.1)
        else:
            print("⏰ Screenshot timeout")
    
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
    
    # Restore original camera
    if original_camera:
        scene.active_camera = original_camera
        print(f"🔄 Restored camera: {original_camera.name}")

# Run the debug
if __name__ == "__main__":
    debug_first_person_camera()
    test_fp_camera_capture()
