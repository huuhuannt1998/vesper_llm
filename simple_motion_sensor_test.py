# Simple Motion Sensor Test - Run this in Blender Console
# This will create a motion sensor with visible triangular detection area

import bpy
from mathutils import Vector

# Clear any existing test sensors
for obj in bpy.data.objects:
    if "test_motion" in obj.name.lower() or "detectionarea_test" in obj.name:
        bpy.data.objects.remove(obj, do_unlink=True)

print("🧹 Cleared existing test sensors")

try:
    # Import the device manager
    from vesper_smart_home import device_manager
    
    # Test sensor parameters
    sensor_id = "TEST_MOTION_01"
    position = Vector((0, 0, 2.0))  # At origin, 2m high
    room = "living_room"
    orientation = 0.0  # North facing
    
    print(f"🎯 Creating test motion sensor: {sensor_id}")
    print(f"   📍 Position: {position}")
    print(f"   🧭 Orientation: {orientation}° (North)")
    
    # Create the motion sensor with automatic detection area
    success = device_manager.add_motion_sensor(sensor_id, room, position, orientation)
    
    if success:
        print(f"✅ Motion sensor {sensor_id} created successfully!")
        print(f"🔍 Look for:")
        print(f"   • BLUE TRIANGLE in 3D viewport")
        print(f"   • Triangle apex at sensor position (0, 0, 2)")
        print(f"   • Two sides extending 5 meters North with 120° spread")
        print(f"   • Object named 'DetectionArea_{sensor_id}' in outliner")
        
        # Check if detection area was created
        detection_area_name = f"DetectionArea_{sensor_id}"
        if detection_area_name in bpy.data.objects:
            detection_obj = bpy.data.objects[detection_area_name]
            print(f"✅ Detection area object found: {detection_obj.name}")
            print(f"   📍 Location: {detection_obj.location}")
            print(f"   🎨 Material count: {len(detection_obj.data.materials)}")
            print(f"   👁️ Display type: {detection_obj.display_type}")
            
            # Select it for visibility
            bpy.context.view_layer.objects.active = detection_obj
            detection_obj.select_set(True)
            
        else:
            print(f"❌ Detection area object not found: {detection_area_name}")
    else:
        print(f"❌ Failed to create motion sensor {sensor_id}")
        
        # Try creating just the detection area directly
        print("🔄 Trying to create detection area directly...")
        direct_success = device_manager.create_automatic_detection_area(sensor_id, position, orientation)
        
        if direct_success:
            print("✅ Direct detection area creation succeeded!")
        else:
            print("❌ Direct detection area creation also failed")
    
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()

print("\n📋 If you still don't see the detection area:")
print("   1. Check wireframe overlay is enabled (Alt+Shift+Z)")
print("   2. Switch viewport shading to 'Wireframe' or 'Solid'")
print("   3. Zoom out - the triangle extends 5 meters")
print("   4. Check outliner for 'DetectionArea_TEST_MOTION_01'")
print("   5. Enable 'Show in Front' for the detection area object")
