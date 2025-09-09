"""
VESPER Motion Sensor Auto-Setup Script
======================================

This script demonstrates how to easily create motion sensors that automatically
create their own 120° field of view detection areas in Blender.

Features:
- Automatic visual detection cone creation (5m range, 120° FOV)
- Semi-transparent blue visualization 
- Real-time color changes (blue = idle, red = detecting)
- Non-collidable wireframe display
- Automatic registration with detection system

Usage in Blender BGE:
1. Load this script in Blender Text Editor
2. Run the script to create motion sensors
3. Each sensor automatically gets a visual detection area
4. Move Actor around to see detection areas change color
"""

import bpy
from mathutils import Vector
import math

def setup_automatic_motion_sensors():
    """Setup motion sensors with automatic detection area creation"""
    
    print("🏠 Setting up motion sensors with automatic detection areas...")
    
    try:
        # Import the VESPER device manager
        import sys
        import os
        
        # Add motion_sensors to path
        vesper_root = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else "/path/to/vesper_llm"
        motion_sensors_path = os.path.join(vesper_root, "motion_sensors")
        addon_path = os.path.join(vesper_root, "blender", "addons", "vesper_smart_home")
        
        if motion_sensors_path not in sys.path:
            sys.path.append(motion_sensors_path)
        if addon_path not in sys.path:
            sys.path.append(addon_path)
        
        # Import device manager
        from addons.vesper_smart_home import device_manager
        
        print("✅ Device manager loaded")
        
        # Define motion sensors with optimal placement
        motion_sensors = [
            {
                "id": "M01_LivingRoom",
                "position": Vector((3.0, 4.0, 2.2)),
                "room": "living_room",
                "orientation": 225.0,  # Diagonal into room
                "description": "Main living area coverage"
            },
            {
                "id": "M02_Kitchen",
                "position": Vector((-1.5, 5.0, 2.3)),
                "room": "kitchen", 
                "orientation": 270.0,  # Towards cooking area
                "description": "Kitchen prep and cooking area"
            },
            {
                "id": "M03_Hallway",
                "position": Vector((0.0, 0.0, 2.4)),
                "room": "hallway",
                "orientation": 0.0,    # Down the hallway
                "description": "Main traffic monitoring"
            },
            {
                "id": "M04_Bedroom",
                "position": Vector((4.0, -2.0, 2.2)),
                "room": "bedroom",
                "orientation": 315.0,  # Towards bed and entrance
                "description": "Bedroom occupancy detection"
            },
            {
                "id": "M05_Entry",
                "position": Vector((1.0, 2.0, 2.5)),
                "room": "entry",
                "orientation": 0.0,    # Towards front door
                "description": "Security entrance monitoring"
            }
        ]
        
        # Create each motion sensor with automatic detection area
        sensors_created = 0
        for sensor in motion_sensors:
            try:
                success = device_manager.add_motion_sensor(
                    sensor["id"],
                    sensor["room"],
                    sensor["position"],
                    sensor["orientation"]
                )
                
                if success:
                    sensors_created += 1
                    print(f"✅ {sensor['id']}: {sensor['description']}")
                    print(f"   📍 Position: {sensor['position']}")
                    print(f"   🧭 Orientation: {sensor['orientation']}°")
                    print(f"   🎯 Detection area created automatically")
                else:
                    print(f"❌ Failed to create {sensor['id']}")
                    
            except Exception as e:
                print(f"❌ Error creating {sensor['id']}: {e}")
        
        print(f"\n🎉 Motion sensor setup complete!")
        print(f"   ✅ Sensors created: {sensors_created}/{len(motion_sensors)}")
        print(f"   🎯 Visual detection areas: Automatic 120° cones")
        print(f"   📐 Detection range: 5 meters (Aeotec SmartThings specs)")
        print(f"   🎨 Visualization: Blue (idle) → Red (detecting)")
        
        if sensors_created > 0:
            print(f"\n🎮 How to test:")
            print(f"   1. Switch to Game Engine mode (Blender BGE)")
            print(f"   2. Press P to start game")
            print(f"   3. Move the Actor around the scene")
            print(f"   4. Watch detection cones turn red when Actor enters")
            print(f"   5. Check console for detection events")
            
            print(f"\n🔍 Visual Detection Areas:")
            print(f"   👁️ Blue wireframe cones = sensor coverage")
            print(f"   🔴 Red cones = actively detecting motion")
            print(f"   📏 5m radius, 120° field of view")
            print(f"   🎯 Semi-transparent, non-collidable")
        
        return sensors_created
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"💡 Make sure VESPER motion sensor system is installed")
        return 0
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return 0

def create_simple_motion_sensor(sensor_id: str, x: float, y: float, z: float = 2.2, orientation: float = 0.0, room: str = "room"):
    """Create a single motion sensor with automatic detection area
    
    Args:
        sensor_id: Unique sensor identifier (e.g., "M01_Kitchen")
        x, y, z: 3D position coordinates
        orientation: Sensor facing direction in degrees (0 = +Y axis)
        room: Room name
    
    Returns:
        bool: True if sensor created successfully
    """
    try:
        from addons.vesper_smart_home import device_manager
        
        position = Vector((x, y, z))
        success = device_manager.add_motion_sensor(sensor_id, room, position, orientation)
        
        if success:
            print(f"✅ Motion sensor {sensor_id} created at ({x}, {y}, {z})")
            print(f"   🎯 Automatic detection area: 120° FOV, 5m range")
            print(f"   🧭 Facing: {orientation}° | Room: {room}")
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to create sensor {sensor_id}: {e}")
        return False

def demo_detection_areas():
    """Quick demo of motion sensor detection areas"""
    print("🎬 Motion Sensor Detection Area Demo")
    print("=" * 50)
    
    # Create a few demo sensors
    demo_sensors = [
        ("DEMO_Center", 0, 0, 2.2, 0, "center"),
        ("DEMO_Corner", 3, 3, 2.2, 225, "corner"),
        ("DEMO_Wall", -2, 4, 2.2, 180, "wall")
    ]
    
    for sensor_id, x, y, z, orientation, room in demo_sensors:
        create_simple_motion_sensor(sensor_id, x, y, z, orientation, room)
    
    print(f"\n🎯 Demo sensors created with automatic detection areas!")
    print(f"📋 Each sensor shows a blue wireframe cone (120° FOV, 5m range)")
    print(f"🔴 Cones turn red when Actor enters detection zone")

# Run the setup when script is executed
if __name__ == "__main__":
    # Full automatic setup
    setup_automatic_motion_sensors()
    
    # Or create individual sensors:
    # create_simple_motion_sensor("M_Custom", 2.0, 3.0, 2.2, 45.0, "custom_room")

"""
QUICK USAGE EXAMPLES:
====================

# Example 1: Full automatic setup
setup_automatic_motion_sensors()

# Example 2: Create individual sensors
create_simple_motion_sensor("M01_Kitchen", -2.0, 5.0, 2.3, 270.0, "kitchen")
create_simple_motion_sensor("M02_LivingRoom", 3.0, 3.0, 2.2, 225.0, "living_room")

# Example 3: Demo setup
demo_detection_areas()

# Each sensor automatically gets:
# - 120° field of view cone (blue wireframe)
# - 5-meter detection range 
# - Real-time color changes (red when detecting)
# - Integration with VESPER motion detection system
# - SmartThings connectivity
"""
