# VESPER Motion Sensor Detection Area Test Script
# Run this in Blender's Scripting workspace to test automatic detection areas

import bpy
import sys
import os
from mathutils import Vector

# Clear existing motion sensors and detection areas
def clear_existing_sensors():
    """Remove existing motion sensors and detection areas"""
    objects_to_remove = []
    for obj in bpy.data.objects:
        if (obj.name.startswith("Motion_") or 
            obj.name.endswith("_detection_area") or
            "vesper_device_id" in obj or
            "vesper_detection_area" in obj):
            objects_to_remove.append(obj)
    
    for obj in objects_to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)
    
    print("🧹 Cleared existing sensors and detection areas")

# Add VESPER paths and import
def setup_vesper():
    """Setup VESPER system paths and imports"""
    try:
        # Add paths
        vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
        addon_path = r"C:\Users\hbui11\AppData\Roaming\UPBGE\Blender\4.4\scripts\addons"
        
        if vesper_root not in sys.path:
            sys.path.append(vesper_root)
        if addon_path not in sys.path:
            sys.path.append(addon_path)
        
        # Import device manager
        from vesper_smart_home import device_manager
        print("✅ VESPER device manager imported successfully")
        return device_manager
        
    except Exception as e:
        print(f"❌ Failed to import VESPER: {e}")
        return None

# Test detection area creation
def test_detection_areas():
    """Test automatic detection area creation"""
    
    # Clear existing sensors first
    clear_existing_sensors()
    
    # Setup VESPER
    device_manager = setup_vesper()
    if not device_manager:
        print("❌ Cannot proceed without device manager")
        return
    
    # Test sensors with different orientations
    test_sensors = [
        {
            "id": "M01_LivingRoom",
            "room": "living_room", 
            "position": Vector((3.0, 4.0, 2.2)),
            "orientation": 225.0,  # Southwest facing
            "description": "Living room corner sensor"
        },
        {
            "id": "M02_Kitchen", 
            "room": "kitchen",
            "position": Vector((-2.0, 5.0, 2.3)),
            "orientation": 270.0,  # West facing  
            "description": "Kitchen prep area sensor"
        },
        {
            "id": "M03_Hallway",
            "room": "hallway", 
            "position": Vector((0.0, 0.0, 2.4)),
            "orientation": 0.0,    # North facing
            "description": "Main hallway sensor"
        },
        {
            "id": "M04_Bedroom",
            "room": "bedroom",
            "position": Vector((6.0, -3.0, 2.2)),
            "orientation": 180.0,  # South facing
            "description": "Bedroom entrance sensor" 
        },
        {
            "id": "M05_Entry",
            "room": "entry",
            "position": Vector((-4.0, -2.0, 2.5)),
            "orientation": 90.0,   # East facing
            "description": "Front door entry sensor"
        }
    ]
    
    print("🎯 Creating motion sensors with automatic detection areas...")
    print("=" * 60)
    
    success_count = 0
    for sensor in test_sensors:
        print(f"\n📍 Creating: {sensor['id']}")
        print(f"   🏠 Room: {sensor['room']}")
        print(f"   📍 Position: {sensor['position']}")
        print(f"   🧭 Orientation: {sensor['orientation']}°")
        print(f"   📝 Description: {sensor['description']}")
        
        # Create the sensor with automatic detection area
        success = device_manager.add_motion_sensor(
            sensor['id'],
            sensor['room'], 
            sensor['position'],
            sensor['orientation']
        )
        
        if success:
            success_count += 1
            print(f"   ✅ Successfully created with detection area")
        else:
            print(f"   ❌ Failed to create sensor")
    
    print("=" * 60)
    print(f"🎉 Test Complete: {success_count}/{len(test_sensors)} sensors created")
    print("\n🔍 Expected Results:")
    print("   • Blue triangular detection cones visible in 3D viewport")
    print("   • Each cone extends 5 meters from sensor position")
    print("   • Each cone has 120° field of view")
    print("   • Cones face the specified orientation direction")
    print("   • Objects named '<SensorID>_detection_area' in outliner")
    print("\n🎮 To Test Motion Detection:")
    print("   1. Ensure you have an 'Actor' object in the scene")
    print("   2. Press P to start BGE (Blender Game Engine)")
    print("   3. Move Actor through detection cones")
    print("   4. Watch cones change from blue to red when detecting")
    
    # Verification 
    detection_areas = [obj for obj in bpy.data.objects if obj.name.endswith("_detection_area")]
    print(f"\n📊 Verification: Found {len(detection_areas)} detection area objects")
    
    for area in detection_areas:
        sensor_id = area.get("sensor_id", "Unknown")
        detection_range = area.get("detection_range", "Unknown")
        fov_angle = area.get("fov_angle", "Unknown")
        print(f"   🎯 {area.name}: Sensor={sensor_id}, Range={detection_range}m, FOV={fov_angle}°")

# Run the test
if __name__ == "__main__":
    test_detection_areas()

# You can also call these functions individually:
# clear_existing_sensors()  # To clear all sensors
# test_detection_areas()    # To create test sensors
