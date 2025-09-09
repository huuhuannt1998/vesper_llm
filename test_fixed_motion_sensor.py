# Fixed Motion Sensor Test - Using the updated add_motion_sensor function
# Run this in Blender Console

import bpy
from mathutils import Vector

def test_fixed_motion_sensor():
    """Test the fixed motion sensor creation"""
    
    print("🔧 Testing Fixed Motion Sensor Creation")
    print("=" * 50)
    
    # Clear existing test objects
    for obj in bpy.data.objects:
        if ("motion_test" in obj.name.lower() or 
            "detectionarea_test" in obj.name.lower() or
            "detectiontriangle_test" in obj.name.lower()):
            bpy.data.objects.remove(obj, do_unlink=True)
    
    try:
        # Import the fixed device manager
        from vesper_smart_home import device_manager
        
        # Test parameters
        sensor_id = "TEST_FIXED_01"
        position = Vector((0, 0, 2.0))
        room = "living_room"
        orientation = 0.0  # North facing
        
        print(f"🎯 Creating motion sensor with fixed function...")
        print(f"   📍 Position: {position}")
        print(f"   🧭 Orientation: {orientation}°")
        print(f"   🏠 Room: {room}")
        
        # This should now work regardless of Docker availability
        success = device_manager.add_motion_sensor(sensor_id, room, position, orientation)
        
        if success:
            print(f"\n✅ Motion sensor creation completed!")
            
            # Check what was created
            sensor_obj_name = f"Motion_{sensor_id}"
            detection_obj_name = f"DetectionArea_{sensor_id}"
            
            sensor_obj = bpy.data.objects.get(sensor_obj_name)
            detection_obj = bpy.data.objects.get(detection_obj_name)
            
            print(f"\n📋 Created objects:")
            if sensor_obj:
                print(f"   ✅ Sensor: {sensor_obj.name} at {sensor_obj.location}")
            else:
                print(f"   ❌ Sensor object not found: {sensor_obj_name}")
            
            if detection_obj:
                print(f"   ✅ Detection area: {detection_obj.name}")
                print(f"      📍 Location: {detection_obj.location}")
                print(f"      🔗 Parented: {detection_obj.parent is not None}")
                if detection_obj.parent:
                    print(f"      👨‍👧 Parent: {detection_obj.parent.name}")
                
                # Select detection area for visibility
                bpy.context.view_layer.objects.active = detection_obj
                detection_obj.select_set(True)
                
                # Make sure it's visible
                detection_obj.hide_viewport = False
                detection_obj.hide_set(False)
                
            else:
                print(f"   ❌ Detection area not found: {detection_obj_name}")
            
            return sensor_obj, detection_obj
            
        else:
            print(f"❌ Motion sensor creation failed")
            return None, None
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_manual_creation():
    """Test creating sensor and detection area manually step by step"""
    print(f"\n🔧 Manual Step-by-Step Creation Test")
    print("=" * 50)
    
    try:
        from vesper_smart_home import device_manager
        
        sensor_id = "MANUAL_TEST_01"
        position = Vector((3, 3, 2.0))
        orientation = 45.0  # Northeast
        
        print(f"Step 1: Creating detection area directly...")
        detection_success = device_manager.create_automatic_detection_area(sensor_id, position, orientation)
        
        if detection_success:
            print(f"✅ Detection area created successfully")
            
            detection_obj_name = f"DetectionArea_{sensor_id}"
            detection_obj = bpy.data.objects.get(detection_obj_name)
            
            if detection_obj:
                print(f"   📦 Object: {detection_obj.name}")
                print(f"   📍 Location: {detection_obj.location}")
                print(f"   🎨 Materials: {len(detection_obj.data.materials)}")
                
                # Make it as visible as possible
                detection_obj.select_set(True)
                bpy.context.view_layer.objects.active = detection_obj
                
                # Check material
                if detection_obj.data.materials:
                    mat = detection_obj.data.materials[0]
                    print(f"   🎨 Material: {mat.name}")
                
                return detection_obj
            else:
                print(f"❌ Detection object not found after creation")
        else:
            print(f"❌ Detection area creation failed")
            
    except Exception as e:
        print(f"❌ Manual creation error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

# Run both tests
if __name__ == "__main__":
    # Test 1: Fixed function
    sensor_obj, detection_obj = test_fixed_motion_sensor()
    
    # Test 2: Manual creation
    manual_detection = test_manual_creation()
    
    print(f"\n🎉 Test Summary:")
    print(f"   Fixed function: {'✅' if detection_obj else '❌'}")
    print(f"   Manual creation: {'✅' if manual_detection else '❌'}")
    
    if detection_obj or manual_detection:
        print(f"\n🔍 You should now see:")
        print(f"   • Red sphere(s) for sensor(s)")
        print(f"   • Blue triangle(s) for detection area(s)")
        print(f"   • Objects selected in outliner")
        
        print(f"\n💡 If still not visible:")
        print(f"   1. Switch to Solid shading (Z → 2)")
        print(f"   2. Check outliner for 'DetectionArea_' objects")
        print(f"   3. Select detection objects in outliner")
        print(f"   4. Zoom out to see 5-meter triangles")
    else:
        print(f"\n❌ No detection areas created - check console for errors")

# Quick commands
print(f"\n💡 Quick commands to run:")
print(f"   test_fixed_motion_sensor()  # Test fixed function")
print(f"   test_manual_creation()      # Test manual creation")
