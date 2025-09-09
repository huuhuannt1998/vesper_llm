# Test Synchronized Movement - Detection Area follows Sensor
# Run this in Blender Console to test parented detection areas

import bpy
from mathutils import Vector

def test_synchronized_movement():
    """Test that detection areas move with their sensors"""
    
    print("🔗 Testing Synchronized Movement - Detection Area with Sensor")
    print("=" * 60)
    
    # Clear existing test objects
    for obj in bpy.data.objects:
        if "test_sync" in obj.name.lower() or "detectionarea_test_sync" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
    
    try:
        # Import device manager
        from vesper_smart_home import device_manager
        
        # Test parameters
        sensor_id = "TEST_SYNC_01"
        initial_position = Vector((2, 3, 2.0))
        room = "living_room"
        orientation = 45.0  # Northeast facing
        
        print(f"🎯 Step 1: Creating motion sensor with detection area")
        print(f"   📍 Initial position: {initial_position}")
        print(f"   🧭 Orientation: {orientation}° (Northeast)")
        
        # Create motion sensor with detection area
        success = device_manager.add_motion_sensor(sensor_id, room, initial_position, orientation)
        
        if not success:
            print("❌ Failed to create motion sensor")
            return False
        
        # Find the sensor and detection area objects
        sensor_obj_name = f"Motion_{sensor_id}"
        detection_obj_name = f"DetectionArea_{sensor_id}"
        
        sensor_obj = bpy.data.objects.get(sensor_obj_name)
        detection_obj = bpy.data.objects.get(detection_obj_name)
        
        if not sensor_obj:
            print(f"❌ Sensor object not found: {sensor_obj_name}")
            return False
            
        if not detection_obj:
            print(f"❌ Detection area not found: {detection_obj_name}")
            return False
        
        print(f"✅ Objects found:")
        print(f"   📍 Sensor: {sensor_obj.name} at {sensor_obj.location}")
        print(f"   🎯 Detection area: {detection_obj.name} at {detection_obj.location}")
        print(f"   🔗 Parented: {detection_obj.parent is not None}")
        
        if detection_obj.parent:
            print(f"   👨‍👧 Parent object: {detection_obj.parent.name}")
        
        # Test movement - move the sensor to different positions
        test_positions = [
            Vector((5, 5, 2.5)),   # Move northeast
            Vector((-2, 4, 3.0)),  # Move to kitchen area
            Vector((0, -3, 2.2)),  # Move to bedroom area
            Vector((initial_position.x, initial_position.y, initial_position.z))  # Back to start
        ]
        
        print(f"\n🚀 Step 2: Testing synchronized movement")
        print(f"   Moving sensor to {len(test_positions)} different positions...")
        
        for i, new_pos in enumerate(test_positions, 1):
            print(f"\n   📍 Move {i}: Sensor → {new_pos}")
            
            # Move the sensor
            sensor_obj.location = new_pos
            
            # Force viewport update
            bpy.context.view_layer.update()
            
            # Check detection area position
            detection_world_pos = detection_obj.matrix_world.translation
            print(f"      🎯 Detection area world position: {detection_world_pos}")
            print(f"      📏 Distance from sensor: {(detection_world_pos - new_pos).length:.2f}m")
            
            # Check if detection area moved with sensor
            if (detection_world_pos - new_pos).length < 0.1:  # Within 10cm
                print(f"      ✅ Detection area moved with sensor!")
            else:
                print(f"      ❌ Detection area NOT synchronized with sensor")
        
        # Final test: rotate the sensor
        print(f"\n🔄 Step 3: Testing rotation synchronization")
        original_rotation = sensor_obj.rotation_euler.copy()
        test_rotations = [45, 90, 180, 270, 0]  # degrees
        
        for angle in test_rotations:
            import math
            sensor_obj.rotation_euler.z = math.radians(angle)
            bpy.context.view_layer.update()
            
            print(f"   🧭 Rotated sensor to {angle}° - detection area should follow")
        
        # Restore original rotation
        sensor_obj.rotation_euler = original_rotation
        bpy.context.view_layer.update()
        
        print(f"\n🎉 Synchronized movement test completed!")
        print(f"\n📋 Manual Test Instructions:")
        print(f"   1. Select sensor object: {sensor_obj.name}")
        print(f"   2. Press 'G' to grab/move the sensor")
        print(f"   3. Move mouse to relocate sensor")
        print(f"   4. Click to confirm - detection area should follow!")
        print(f"   5. Press 'R' then 'Z' to rotate around Z-axis")
        print(f"   6. Detection area should rotate with sensor")
        
        # Select sensor for manual testing
        bpy.context.view_layer.objects.active = sensor_obj
        sensor_obj.select_set(True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during synchronized movement test: {e}")
        import traceback
        traceback.print_exc()
        return False

def parent_existing_detection_areas():
    """Parent any existing detection areas to their sensors"""
    try:
        from vesper_smart_home import device_manager
        
        print("🔗 Parenting existing detection areas to sensors...")
        parented_count = device_manager.parent_detection_areas_to_sensors()
        
        if parented_count > 0:
            print(f"✅ {parented_count} detection areas now move with their sensors!")
        else:
            print("ℹ️ No detection areas needed parenting")
            
    except Exception as e:
        print(f"❌ Error parenting detection areas: {e}")

# Run the tests
if __name__ == "__main__":
    # First, parent any existing detection areas
    parent_existing_detection_areas()
    
    # Then test synchronized movement
    test_synchronized_movement()

print("\n💡 Quick Commands:")
print("   parent_existing_detection_areas()  # Parent existing areas")
print("   test_synchronized_movement()       # Full movement test")
