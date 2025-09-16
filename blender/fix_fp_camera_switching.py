"""
First-Person Camera Issue Fix
============================

Based on user screenshots showing bird-eye view instead of first-person view,
this script diagnoses and fixes the camera switching issue.
"""

import bge
import time

def diagnose_camera_switching_issue():
    """Diagnose why first-person captures are showing bird-eye view"""
    
    print("🔍 DIAGNOSING CAMERA SWITCHING ISSUE")
    print("=" * 40)
    print("User reports: First-person images show bird-eye view instead")
    print()
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Check what cameras exist
        print("📷 AVAILABLE CAMERAS:")
        cameras_found = {}
        
        for obj in scene.objects:
            if hasattr(obj, 'camera') or 'Camera' in obj.name:
                cameras_found[obj.name] = obj
                pos = obj.worldPosition
                print(f"   {obj.name}: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
                
                # Check if it's actually a camera
                if hasattr(obj, 'camera'):
                    print(f"      ✅ Valid camera object")
                else:
                    print(f"      ❌ Not a camera object (missing camera property)")
        
        # Check current active camera
        active_camera = scene.active_camera
        if active_camera:
            print(f"\n🎥 CURRENT ACTIVE CAMERA: {active_camera.name}")
            pos = active_camera.worldPosition
            print(f"   Position: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
        else:
            print(f"\n❌ NO ACTIVE CAMERA")
        
        # Check specific cameras we need
        bird_eye_camera = scene.objects.get("BirdEyeCamera")
        actor_fp_camera = scene.objects.get("Actor_FPCamera")
        
        print(f"\n🔍 EXPECTED CAMERAS:")
        print(f"   BirdEyeCamera: {'✅ Found' if bird_eye_camera else '❌ Missing'}")
        print(f"   Actor_FPCamera: {'✅ Found' if actor_fp_camera else '❌ Missing'}")
        
        if bird_eye_camera and actor_fp_camera:
            # Compare positions to see if they're the same camera
            bird_pos = bird_eye_camera.worldPosition
            fp_pos = actor_fp_camera.worldPosition
            
            distance = ((bird_pos.x - fp_pos.x)**2 + (bird_pos.y - fp_pos.y)**2 + (bird_pos.z - fp_pos.z)**2)**0.5
            
            print(f"\n📏 CAMERA COMPARISON:")
            print(f"   BirdEyeCamera: [{bird_pos.x:.2f}, {bird_pos.y:.2f}, {bird_pos.z:.2f}]")
            print(f"   Actor_FPCamera: [{fp_pos.x:.2f}, {fp_pos.y:.2f}, {fp_pos.z:.2f}]")
            print(f"   Distance between them: {distance:.2f} units")
            
            if distance < 0.1:
                print(f"   ❌ PROBLEM: Both cameras are at the same position!")
                print(f"   💡 Actor_FPCamera needs to be moved to Actor location")
                return "same_position"
            elif fp_pos.z > 5.0:
                print(f"   ❌ PROBLEM: Actor_FPCamera is too high (Z={fp_pos.z:.2f})")
                print(f"   💡 First-person camera should be at eye level (~1.7 units)")
                return "fp_too_high"
            else:
                print(f"   ✅ Cameras are in different positions")
                return "position_ok"
        
        elif not actor_fp_camera:
            print(f"\n❌ CRITICAL: Actor_FPCamera does not exist!")
            print(f"   💡 This is why first-person captures show bird-eye view")
            return "no_fp_camera"
        
        else:
            return "missing_cameras"
        
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        return "error"

def fix_camera_positioning():
    """Fix Actor_FPCamera positioning to be near Actor"""
    
    print(f"\n🔧 FIXING CAMERA POSITIONING")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find Actor and Actor_FPCamera
        actor = scene.objects.get("Actor")
        actor_fp_camera = scene.objects.get("Actor_FPCamera")
        
        if not actor:
            print("❌ Actor not found - cannot fix positioning")
            return False
        
        if not actor_fp_camera:
            print("❌ Actor_FPCamera not found - cannot fix positioning")
            return False
        
        # Get Actor position
        actor_pos = actor.worldPosition
        print(f"🚶 Actor position: [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
        
        # Position camera at Actor location with eye-level offset
        new_camera_pos = [
            actor_pos.x,          # Same X as Actor
            actor_pos.y,          # Same Y as Actor  
            actor_pos.z + 1.7     # Eye level height above Actor
        ]
        
        print(f"📍 Moving Actor_FPCamera to: [{new_camera_pos[0]:.2f}, {new_camera_pos[1]:.2f}, {new_camera_pos[2]:.2f}]")
        
        # Apply new position
        actor_fp_camera.worldPosition = new_camera_pos
        
        # Verify the move worked
        actual_pos = actor_fp_camera.worldPosition
        print(f"✅ Camera now at: [{actual_pos.x:.2f}, {actual_pos.y:.2f}, {actual_pos.z:.2f}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Camera positioning fix failed: {e}")
        return False

def test_camera_switching():
    """Test switching between cameras to verify they work"""
    
    print(f"\n🔄 TESTING CAMERA SWITCHING")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Store original camera
        original_camera = scene.active_camera
        original_name = original_camera.name if original_camera else "None"
        
        print(f"🎥 Original active camera: {original_name}")
        
        # Test switching to BirdEyeCamera
        bird_eye_camera = scene.objects.get("BirdEyeCamera")
        if bird_eye_camera:
            scene.active_camera = bird_eye_camera
            if scene.active_camera == bird_eye_camera:
                print(f"✅ Successfully switched to BirdEyeCamera")
            else:
                print(f"❌ Failed to switch to BirdEyeCamera")
        
        # Test switching to Actor_FPCamera  
        actor_fp_camera = scene.objects.get("Actor_FPCamera")
        if actor_fp_camera:
            scene.active_camera = actor_fp_camera
            if scene.active_camera == actor_fp_camera:
                print(f"✅ Successfully switched to Actor_FPCamera")
                
                # Check if it's a valid camera
                if hasattr(actor_fp_camera, 'camera'):
                    print(f"✅ Actor_FPCamera has valid camera properties")
                else:
                    print(f"❌ Actor_FPCamera missing camera properties")
                    
                # Check positioning
                pos = actor_fp_camera.worldPosition
                if pos.z < 3.0:  # Should be at eye level, not high up
                    print(f"✅ Camera at reasonable height (Z={pos.z:.2f})")
                else:
                    print(f"⚠️ Camera very high (Z={pos.z:.2f}) - might be bird-eye position")
                    
            else:
                print(f"❌ Failed to switch to Actor_FPCamera")
        else:
            print(f"❌ Actor_FPCamera not found for switching test")
        
        # Restore original camera
        if original_camera:
            scene.active_camera = original_camera
            print(f"🔄 Restored original camera: {original_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Camera switching test failed: {e}")
        return False

def create_actor_fp_camera_if_missing():
    """Create Actor_FPCamera if it doesn't exist"""
    
    print(f"\n🛠️ CREATING ACTOR_FP_CAMERA")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Check if it already exists
        if scene.objects.get("Actor_FPCamera"):
            print("✅ Actor_FPCamera already exists")
            return True
        
        # Find Actor
        actor = scene.objects.get("Actor")
        if not actor:
            print("❌ Cannot create Actor_FPCamera - Actor not found")
            return False
        
        # Find a camera we can duplicate/rename
        available_cameras = []
        for obj in scene.objects:
            if hasattr(obj, 'camera') and obj.name != "BirdEyeCamera":
                available_cameras.append(obj)
        
        if available_cameras:
            # Use first available camera as template
            template_camera = available_cameras[0]
            print(f"📷 Found template camera: {template_camera.name}")
            print(f"💡 Rename {template_camera.name} to 'Actor_FPCamera' in Blender")
            print(f"   Or duplicate BirdEyeCamera and rename the copy")
        else:
            print("❌ No available cameras to use as template")
            print("💡 In Blender: Add > Camera, then rename to 'Actor_FPCamera'")
        
        return False
        
    except Exception as e:
        print(f"❌ Camera creation check failed: {e}")
        return False

def run_first_person_camera_fix():
    """Run complete first-person camera fix based on user's issue"""
    
    print("🔧 FIRST-PERSON CAMERA FIX")
    print("=" * 30)
    print("Issue: First-person captures showing bird-eye view")
    print("Goal: Fix Actor_FPCamera to show actual first-person view")
    print()
    
    # Step 1: Diagnose the issue
    issue_type = diagnose_camera_switching_issue()
    
    # Step 2: Apply appropriate fix
    if issue_type == "no_fp_camera":
        print(f"\n🛠️ FIXING: Missing Actor_FPCamera")
        create_actor_fp_camera_if_missing()
        
    elif issue_type == "same_position" or issue_type == "fp_too_high":
        print(f"\n🛠️ FIXING: Actor_FPCamera positioning")
        fix_camera_positioning()
        
    elif issue_type == "position_ok":
        print(f"\n🛠️ TESTING: Camera switching functionality")
        test_camera_switching()
    
    # Step 3: Final verification
    print(f"\n✅ VERIFICATION")
    print("=" * 15)
    
    scene = bge.logic.getCurrentScene()
    actor_fp_camera = scene.objects.get("Actor_FPCamera")
    
    if actor_fp_camera:
        pos = actor_fp_camera.worldPosition
        print(f"📷 Actor_FPCamera exists at: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
        
        if hasattr(actor_fp_camera, 'camera'):
            print(f"✅ Has camera properties")
        else:
            print(f"❌ Missing camera properties - fix in Blender")
        
        if pos.z < 3.0:
            print(f"✅ At reasonable first-person height")
        else:
            print(f"⚠️ Still at bird-eye height - run fix_camera_positioning()")
    else:
        print(f"❌ Actor_FPCamera still missing - create in Blender")
    
    print(f"\n💡 NEXT STEPS:")
    print("1. Run diagnostic script to verify fixes")
    print("2. Test first-person capture again") 
    print("3. Check if images now show first-person view instead of bird-eye")

# Auto-run if executed directly
if __name__ == "__main__":
    run_first_person_camera_fix()

print("✅ First-person camera fix loaded - call run_first_person_camera_fix() to execute")
