"""
Camera Diagnosis - Check Available Cameras
==========================================

This script will help diagnose camera issues by:
1. Listing all cameras in the scene
2. Checking which camera is currently being used for first-person
3. Verifying camera positioning and properties
4. Testing camera switching
"""

import bge

def list_all_scene_objects():
    """List all objects in the scene to see what cameras exist"""
    
    print("🔍 COMPLETE SCENE ANALYSIS")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        all_objects = []
        camera_objects = []
        potential_cameras = []
        
        print("📋 ALL SCENE OBJECTS:")
        for obj in scene.objects:
            all_objects.append(obj.name)
            
            # Check if it's definitely a camera
            if hasattr(obj, 'camera') or 'Camera' in obj.name:
                camera_objects.append(obj)
                print(f"   🎥 CAMERA: {obj.name} at [{obj.worldPosition.x:.2f}, {obj.worldPosition.y:.2f}, {obj.worldPosition.z:.2f}]")
            
            # Check for potential first-person related objects
            elif any(keyword in obj.name.lower() for keyword in ['fp', 'first', 'person', 'actor']):
                potential_cameras.append(obj)
                print(f"   🔸 POTENTIAL: {obj.name} at [{obj.worldPosition.x:.2f}, {obj.worldPosition.y:.2f}, {obj.worldPosition.z:.2f}]")
            
            else:
                print(f"   📦 OBJECT: {obj.name}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total objects: {len(all_objects)}")
        print(f"   Camera objects: {len(camera_objects)}")
        print(f"   Potential first-person: {len(potential_cameras)}")
        
        return camera_objects, potential_cameras
        
    except Exception as e:
        print(f"❌ Scene analysis failed: {e}")
        return [], []

def check_current_camera_usage():
    """Check which camera is currently active and being used"""
    
    print("\n🎯 CURRENT CAMERA USAGE")
    print("=" * 25)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Check active camera
        active_camera = scene.active_camera
        if active_camera:
            print(f"📹 Active camera: {active_camera.name}")
            print(f"   Position: [{active_camera.worldPosition.x:.2f}, {active_camera.worldPosition.y:.2f}, {active_camera.worldPosition.z:.2f}]")
        else:
            print("❌ No active camera found")
        
        # Check for specific cameras our code looks for
        cameras_to_check = {
            "BirdEyeCamera": "Bird-eye view camera",
            "Actor_FPCamera": "First-person camera", 
            "FPCamera": "Alternative FP camera",
            "FirstPersonCamera": "Alternative first-person camera",
            "ActorCamera": "Alternative actor camera"
        }
        
        print(f"\n🔍 EXPECTED CAMERA CHECK:")
        found_cameras = {}
        
        for camera_name, description in cameras_to_check.items():
            camera = scene.objects.get(camera_name)
            if camera:
                found_cameras[camera_name] = camera
                pos = camera.worldPosition
                print(f"   ✅ {camera_name}: {description} at [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
                
                # Check if it's actually a camera object
                if hasattr(camera, 'camera'):
                    print(f"      🎥 Confirmed camera object")
                else:
                    print(f"      ⚠️ Not a camera object (missing camera property)")
            else:
                print(f"   ❌ {camera_name}: {description} - NOT FOUND")
        
        return found_cameras
        
    except Exception as e:
        print(f"❌ Camera usage check failed: {e}")
        return {}

def test_camera_switching():
    """Test switching between cameras to see which one actually works"""
    
    print("\n🔄 CAMERA SWITCHING TEST")
    print("=" * 25)
    
    try:
        scene = bge.logic.getCurrentScene()
        original_camera = scene.active_camera
        
        print(f"📹 Original active camera: {original_camera.name if original_camera else 'None'}")
        
        # Test each camera we can find
        test_cameras = ["BirdEyeCamera", "Actor_FPCamera", "FPCamera", "FirstPersonCamera"]
        
        for camera_name in test_cameras:
            camera = scene.objects.get(camera_name)
            if camera:
                print(f"\n🧪 Testing {camera_name}:")
                
                try:
                    # Try to make it active
                    scene.active_camera = camera
                    
                    # Check if switch was successful
                    if scene.active_camera == camera:
                        pos = camera.worldPosition
                        print(f"   ✅ Successfully switched to {camera_name}")
                        print(f"   📍 Position: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
                        
                        # Check camera properties
                        if hasattr(camera, 'camera'):
                            print(f"   🎥 Camera properties available")
                        else:
                            print(f"   ⚠️ No camera properties - might not be a real camera")
                    else:
                        print(f"   ❌ Failed to switch to {camera_name}")
                        
                except Exception as e:
                    print(f"   ❌ Error switching to {camera_name}: {e}")
            else:
                print(f"\n❌ {camera_name}: Not found in scene")
        
        # Restore original camera
        if original_camera:
            scene.active_camera = original_camera
            print(f"\n🔄 Restored original camera: {original_camera.name}")
        
    except Exception as e:
        print(f"❌ Camera switching test failed: {e}")

def check_first_person_implementation():
    """Check what the first-person code is actually using"""
    
    print("\n🕵️ FIRST-PERSON IMPLEMENTATION CHECK")
    print("=" * 35)
    
    try:
        # Try to import and initialize first-person camera
        import sys
        sys.path.append("c:/Users/hbui11/Desktop/vesper_llm/blender")
        
        from first_person_camera import FirstPersonCameraManager
        
        print("✅ FirstPersonCameraManager imported")
        
        # Create instance and see what camera it finds
        fp_manager = FirstPersonCameraManager()
        
        if fp_manager.camera_object:
            camera = fp_manager.camera_object
            print(f"✅ FirstPersonCameraManager found camera: {camera.name}")
            print(f"   📍 Position: [{camera.worldPosition.x:.2f}, {camera.worldPosition.y:.2f}, {camera.worldPosition.z:.2f}]")
            
            # Check if this is the right camera for first-person view
            if camera.name == "Actor_FPCamera":
                print(f"   ✅ Using correct Actor_FPCamera")
            else:
                print(f"   ⚠️ Using {camera.name} instead of Actor_FPCamera")
                
            # Check camera positioning relative to actor
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            if actor:
                actor_pos = actor.worldPosition
                camera_pos = camera.worldPosition
                distance = ((camera_pos.x - actor_pos.x)**2 + (camera_pos.y - actor_pos.y)**2 + (camera_pos.z - actor_pos.z)**2)**0.5
                
                print(f"   📏 Distance from Actor: {distance:.2f} units")
                if distance < 2.0:
                    print(f"   ✅ Camera is close to Actor (good for first-person)")
                else:
                    print(f"   ⚠️ Camera is far from Actor (might not be first-person view)")
        else:
            print("❌ FirstPersonCameraManager could not find any camera")
            
    except ImportError as e:
        print(f"❌ Failed to import FirstPersonCameraManager: {e}")
    except Exception as e:
        print(f"❌ First-person implementation check failed: {e}")

def run_camera_diagnosis():
    """Run complete camera diagnosis"""
    
    print("🔧 CAMERA DIAGNOSIS SUITE")
    print("=" * 30)
    print("Checking camera setup and first-person view issues...")
    print()
    
    # Run all diagnostic tests
    camera_objects, potential_cameras = list_all_scene_objects()
    found_cameras = check_current_camera_usage()
    test_camera_switching()
    check_first_person_implementation()
    
    # Provide recommendations
    print("\n💡 DIAGNOSIS RECOMMENDATIONS")
    print("=" * 30)
    
    scene = bge.logic.getCurrentScene()
    actor_fp_camera = scene.objects.get("Actor_FPCamera")
    
    if actor_fp_camera:
        print("✅ Actor_FPCamera exists in scene")
        
        if hasattr(actor_fp_camera, 'camera'):
            print("✅ Actor_FPCamera is a valid camera object")
        else:
            print("❌ Actor_FPCamera exists but is NOT a camera object")
            print("   💡 Fix: In Blender, ensure Actor_FPCamera has camera data")
        
        # Check positioning
        actor = scene.objects.get("Actor")
        if actor:
            camera_pos = actor_fp_camera.worldPosition  
            actor_pos = actor.worldPosition
            distance = ((camera_pos.x - actor_pos.x)**2 + (camera_pos.y - actor_pos.y)**2 + (camera_pos.z - actor_pos.z)**2)**0.5
            
            if distance > 3.0:
                print(f"⚠️ Actor_FPCamera is {distance:.2f} units from Actor")
                print("   💡 Fix: Move Actor_FPCamera closer to Actor for first-person view")
            else:
                print(f"✅ Actor_FPCamera is properly positioned ({distance:.2f} units from Actor)")
    else:
        print("❌ Actor_FPCamera does NOT exist in scene")
        print("   💡 Fix: Create a camera named 'Actor_FPCamera' in Blender")
        
        if camera_objects:
            print(f"   📋 Available cameras to rename: {[cam.name for cam in camera_objects]}")

# Auto-run if executed directly
if __name__ == "__main__":
    run_camera_diagnosis()

print("✅ Camera diagnosis script loaded - call run_camera_diagnosis() to execute")
