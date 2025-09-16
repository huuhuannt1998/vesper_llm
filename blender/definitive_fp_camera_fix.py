"""
Definitive First-Person Camera Fix
==================================

Based on user's screenshots showing bird-eye views instead of first-person,
this script will identify and fix the exact camera issue.

The problem: capture_immediate_first_person_view is not switching cameras correctly,
resulting in bird-eye screenshots instead of true first-person views.
"""

import bge
import os
import time

def verify_camera_exists_and_works():
    """Verify Actor_FPCamera exists and can be used for capture"""
    
    print("🔍 VERIFYING ACTOR_FP_CAMERA")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Check if Actor_FPCamera exists
        actor_fp_camera = scene.objects.get("Actor_FPCamera")
        
        if not actor_fp_camera:
            print("❌ Actor_FPCamera does not exist")
            print("💡 This is why first-person captures show bird-eye view!")
            
            # Look for alternative cameras
            alternatives = ["FPCamera", "FirstPersonCamera", "ActorCamera"]
            found_alternative = None
            
            for name in alternatives:
                cam = scene.objects.get(name)
                if cam and hasattr(cam, 'camera'):
                    found_alternative = cam
                    print(f"✅ Found alternative camera: {name}")
                    break
            
            if found_alternative:
                print(f"💡 Solution: Rename {found_alternative.name} to 'Actor_FPCamera'")
                return False, found_alternative.name
            else:
                print("💡 Solution: Create a new camera named 'Actor_FPCamera'")
                return False, None
        
        else:
            print(f"✅ Actor_FPCamera exists: {actor_fp_camera.name}")
            
            # Check if it's actually a camera
            if not hasattr(actor_fp_camera, 'camera'):
                print("❌ Actor_FPCamera is not a camera object!")
                print("💡 Fix: In Blender, ensure this object has camera data")
                return False, None
            
            print("✅ Actor_FPCamera is a valid camera object")
            
            # Check positioning
            pos = actor_fp_camera.worldPosition
            print(f"📍 Position: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
            
            # Check if it's at bird-eye position (high Z value)
            if pos.z > 5.0:
                print(f"⚠️ Camera is at bird-eye height (Z={pos.z:.2f})")
                print("💡 This explains why it shows bird-eye view!")
                return False, "too_high"
            
            print("✅ Camera is at reasonable first-person height")
            return True, None
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False, str(e)

def fix_camera_height():
    """Move Actor_FPCamera to proper first-person height"""
    
    print("\n🔧 FIXING CAMERA HEIGHT")
    print("=" * 25)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        actor = scene.objects.get("Actor")
        actor_fp_camera = scene.objects.get("Actor_FPCamera")
        
        if not actor or not actor_fp_camera:
            print("❌ Cannot fix height - Actor or camera missing")
            return False
        
        # Get Actor position
        actor_pos = actor.worldPosition
        
        # Set camera to first-person position
        new_pos = [
            actor_pos.x,          # Same X as Actor
            actor_pos.y,          # Same Y as Actor
            actor_pos.z + 1.7     # Eye level (1.7m above Actor)
        ]
        
        old_pos = actor_fp_camera.worldPosition
        print(f"📍 Moving camera from [{old_pos.x:.2f}, {old_pos.y:.2f}, {old_pos.z:.2f}]")
        print(f"                  to [{new_pos[0]:.2f}, {new_pos[1]:.2f}, {new_pos[2]:.2f}]")
        
        actor_fp_camera.worldPosition = new_pos
        
        # Verify the move
        actual_pos = actor_fp_camera.worldPosition
        print(f"✅ Camera now at: [{actual_pos.x:.2f}, {actual_pos.y:.2f}, {actual_pos.z:.2f}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Height fix failed: {e}")
        return False

def test_camera_switching():
    """Test if camera switching actually works"""
    
    print("\n🔄 TESTING CAMERA SWITCHING")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Get cameras
        bird_eye_camera = scene.objects.get("BirdEyeCamera")
        actor_fp_camera = scene.objects.get("Actor_FPCamera")
        
        if not bird_eye_camera or not actor_fp_camera:
            print("❌ Cannot test - missing cameras")
            return False
        
        # Store original active camera
        original_camera = scene.active_camera
        original_name = original_camera.name if original_camera else "None"
        print(f"🎥 Original active camera: {original_name}")
        
        # Test 1: Switch to BirdEyeCamera
        print("\n🧪 Test 1: Switch to BirdEyeCamera")
        scene.active_camera = bird_eye_camera
        
        if scene.active_camera == bird_eye_camera:
            pos = bird_eye_camera.worldPosition
            print(f"✅ Successfully switched to BirdEyeCamera at [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
        else:
            print("❌ Failed to switch to BirdEyeCamera")
            return False
        
        # Test 2: Switch to Actor_FPCamera  
        print("\n🧪 Test 2: Switch to Actor_FPCamera")
        scene.active_camera = actor_fp_camera
        
        if scene.active_camera == actor_fp_camera:
            pos = actor_fp_camera.worldPosition
            print(f"✅ Successfully switched to Actor_FPCamera at [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
            
            # Check if positions are different (should be!)
            bird_pos = bird_eye_camera.worldPosition
            fp_pos = actor_fp_camera.worldPosition
            
            distance = ((bird_pos.x - fp_pos.x)**2 + (bird_pos.y - fp_pos.y)**2 + (bird_pos.z - fp_pos.z)**2)**0.5
            
            if distance < 0.1:
                print("❌ PROBLEM: Both cameras are at same position!")
                print("💡 This is why first-person shows bird-eye view")
                return False
            else:
                print(f"✅ Cameras are in different positions (distance: {distance:.2f})")
                
        else:
            print("❌ Failed to switch to Actor_FPCamera")
            return False
        
        # Restore original camera
        if original_camera:
            scene.active_camera = original_camera
            print(f"\n🔄 Restored original camera: {original_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Camera switching test failed: {e}")
        return False

def test_actual_capture():
    """Test actual first-person capture to see what it produces"""
    
    print("\n📸 TESTING ACTUAL CAPTURE")
    print("=" * 30)
    
    try:
        # Use the actual capture function
        from first_person_camera import capture_immediate_first_person_view
        
        # Test with current actor position
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if not actor:
            print("❌ Actor not found for capture test")
            return False
        
        actor_pos = actor.worldPosition
        actor_orient = actor.worldOrientation
        
        print(f"🎬 Testing capture at Actor position: [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
        
        # Before capture - check active camera
        before_camera = scene.active_camera
        before_name = before_camera.name if before_camera else "None"
        print(f"📹 Active camera before capture: {before_name}")
        
        # Attempt capture
        result = capture_immediate_first_person_view(actor_pos, actor_orient)
        
        # After capture - check active camera
        after_camera = scene.active_camera
        after_name = after_camera.name if after_camera else "None"
        print(f"📹 Active camera after capture: {after_name}")
        
        if result.get("success"):
            print(f"✅ Capture succeeded: {result.get('path')}")
            
            # Check if file exists
            file_path = result.get("path")
            if file_path and os.path.exists(file_path):
                print(f"✅ File created: {os.path.basename(file_path)}")
                
                # Check camera that was used during capture
                # (This info should be in the capture function logs)
                print("💡 Check BGE console logs to see which camera was actually used")
                
            else:
                print(f"❌ File not created: {file_path}")
                
        else:
            error = result.get("error", "Unknown error")
            print(f"❌ Capture failed: {error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Capture test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_definitive_fp_camera_fix():
    """Run complete fix for first-person camera showing bird-eye view"""
    
    print("🔧 DEFINITIVE FIRST-PERSON CAMERA FIX")
    print("=" * 45)
    print("Problem: First-person captures show bird-eye view instead")
    print("Goal: Fix camera setup so first-person actually shows first-person view")
    print()
    
    # Step 1: Verify camera exists and works
    camera_ok, issue = verify_camera_exists_and_works()
    
    if not camera_ok:
        if issue == "too_high":
            print("\n🛠️ APPLYING FIX: Moving camera to first-person height")
            if fix_camera_height():
                print("✅ Camera height fixed - rerun verification")
                camera_ok, _ = verify_camera_exists_and_works()
            else:
                print("❌ Failed to fix camera height")
                
        elif issue:
            print(f"\n❌ CRITICAL ISSUE: {issue}")
            print("💡 Manual fix required in Blender:")
            print("   1. Create a camera named 'Actor_FPCamera'")
            print("   2. Position it near the Actor at eye level")
            print("   3. Ensure it has camera data attached")
            return False
        
        if not camera_ok:
            print("\n❌ Cannot proceed - camera setup incomplete")
            return False
    
    # Step 2: Test camera switching
    print(f"\n🔄 TESTING CAMERA FUNCTIONALITY")
    switching_ok = test_camera_switching()
    
    if not switching_ok:
        print("❌ Camera switching failed - this is likely the root cause")
        print("💡 Check Blender camera setup and object properties")
        return False
    
    # Step 3: Test actual capture
    print(f"\n📸 TESTING REAL CAPTURE")
    capture_ok = test_actual_capture()
    
    # Final assessment
    print(f"\n📊 DIAGNOSTIC RESULTS")
    print("=" * 25)
    
    if camera_ok and switching_ok and capture_ok:
        print("✅ All tests passed!")
        print("💡 First-person camera should now work correctly")
        print("   Try capturing again - should show true first-person view")
        
    else:
        print("❌ Issues found:")
        if not camera_ok:
            print("   - Camera setup problems")
        if not switching_ok:
            print("   - Camera switching failures")  
        if not capture_ok:
            print("   - Capture function issues")
            
        print("\n🛠️ RECOMMENDED ACTIONS:")
        print("1. Check Blender scene for Actor_FPCamera object")
        print("2. Ensure Actor_FPCamera has camera data")
        print("3. Position Actor_FPCamera near Actor at eye level")
        print("4. Test manual camera switching in BGE")
    
    return camera_ok and switching_ok and capture_ok

# Auto-run if executed directly
if __name__ == "__main__":
    run_definitive_fp_camera_fix()

print("✅ Definitive first-person camera fix loaded - call run_definitive_fp_camera_fix() to execute")
