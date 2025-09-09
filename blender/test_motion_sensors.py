"""
VESPER Motion Sensor Test Script
===============================

This script demonstrates the realistic Aeotec SmartThings Motion Sensor detection system.
Run this in Blender BGE to test motion sensor placement and detection.

Features tested:
- 120° field of view detection
- 5-meter detection range
- Real-time Actor position tracking
- SmartThings integration simulation
- Cooldown periods and motion thresholds
"""

import bge
import mathutils
from mathutils import Vector
import json
import time

def setup_test_motion_sensors():
    """Set up test motion sensors in the virtual environment"""
    
    print("🔧 Setting up test motion sensors...")
    
    # Get the scene and device manager
    scene = bge.logic.getCurrentScene()
    
    try:
        # Try to import the device manager
        import sys
        import os
        addon_path = os.path.join(os.path.dirname(__file__), "addons", "vesper_smart_home")
        if addon_path not in sys.path:
            sys.path.append(addon_path)
        
        from addons.vesper_smart_home import device_manager
        
        # Store device manager in scene for access during runtime
        scene.vesper_device_manager = device_manager
        
        print("✅ Device manager connected")
        
        # Test motion sensor positions based on typical smart home setup
        test_sensors = [
            {
                "id": "M01_LivingRoom", 
                "position": Vector((2.5, 3.0, 2.0)), 
                "room": "living_room", 
                "orientation": 45.0  # Facing diagonally to cover most of the room
            },
            {
                "id": "M02_Kitchen", 
                "position": Vector((-1.0, 5.0, 2.0)), 
                "room": "kitchen", 
                "orientation": 180.0  # Facing towards cooking area
            },
            {
                "id": "M03_Bedroom", 
                "position": Vector((4.0, -2.0, 2.0)), 
                "room": "bedroom", 
                "orientation": 270.0  # Facing towards bed
            },
            {
                "id": "M04_Hallway", 
                "position": Vector((0.0, 0.0, 2.0)), 
                "room": "hallway", 
                "orientation": 0.0  # Facing down the hallway
            },
            {
                "id": "M05_Bathroom", 
                "position": Vector((-3.0, -1.0, 2.0)), 
                "room": "bathroom", 
                "orientation": 90.0  # Facing towards shower/toilet
            }
        ]
        
        # Add each test sensor
        sensors_added = 0
        for sensor in test_sensors:
            try:
                success = device_manager.add_motion_sensor(
                    sensor["id"], 
                    sensor["room"], 
                    sensor["position"], 
                    sensor["orientation"]
                )
                if success:
                    sensors_added += 1
                    print(f"✅ {sensor['id']}: {sensor['room']} at {sensor['position']}")
                else:
                    print(f"❌ Failed to add {sensor['id']}")
            except Exception as e:
                print(f"❌ Error adding {sensor['id']}: {e}")
        
        print(f"🎯 Motion sensor test setup complete: {sensors_added}/{len(test_sensors)} sensors active")
        
        # Store test sensor info for monitoring
        scene.test_sensors = test_sensors
        scene.test_start_time = time.time()
        
        return sensors_added > 0
        
    except ImportError as e:
        print(f"❌ Failed to import device manager: {e}")
        return False
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def monitor_motion_detection():
    """Monitor and display motion detection status"""
    
    scene = bge.logic.getCurrentScene()
    
    # Get Actor position
    actor = scene.objects.get("Actor")
    if not actor:
        print("⚠️ No Actor object found for motion detection test")
        return
    
    actor_pos = Vector((actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z))
    
    # Get device manager and update detection
    if hasattr(scene, 'vesper_device_manager'):
        device_manager = scene.vesper_device_manager
        
        # Update motion detection system
        device_manager.update_motion_detection()
        
        # Get current detection status
        status = device_manager.get_motion_detection_status()
        
        # Display status every 60 frames (approximately 1 second at 60 FPS)
        if not hasattr(scene, 'status_frame_counter'):
            scene.status_frame_counter = 0
        
        scene.status_frame_counter += 1
        
        if scene.status_frame_counter >= 60:  # Update display every second
            scene.status_frame_counter = 0
            
            print(f"\n📍 Actor Position: [{actor_pos.x:.1f}, {actor_pos.y:.1f}, {actor_pos.z:.1f}]")
            print(f"🔍 Motion Detection Status:")
            print(f"   📊 Total Sensors: {status.get('total_sensors', 0)}")
            print(f"   ✅ Active Sensors: {status.get('active_sensors', 0)}")
            print(f"   🚨 Sensors Detecting: {status.get('sensors_detecting', 0)}")
            
            # Show details for each sensor
            sensors = status.get('sensors', {})
            for sensor_id, sensor_data in sensors.items():
                detecting = "🔴 DETECTING" if sensor_data.get('detecting', False) else "⚪ idle"
                room = sensor_data.get('room', 'unknown')
                count = sensor_data.get('detection_count', 0)
                print(f"   {sensor_id}: {detecting} in {room} (count: {count})")
    
    else:
        print("⚠️ Device manager not available for motion detection monitoring")

def run_motion_sensor_test():
    """Main function to run motion sensor detection test"""
    
    # Initialize only once
    if not hasattr(bge.logic, 'motion_test_initialized'):
        print("🚀 Starting VESPER Motion Sensor Detection Test")
        print("=" * 60)
        
        # Setup test sensors
        setup_success = setup_test_motion_sensors()
        
        if setup_success:
            bge.logic.motion_test_initialized = True
            print("\n📋 Test Instructions:")
            print("   🎮 Move the Actor around the virtual environment")
            print("   🔍 Motion sensors will detect when Actor enters their 120° FOV")
            print("   📏 Detection range: 5 meters (Aeotec SmartThings specs)")
            print("   ⏱️ Cooldown period: 3 seconds between detections")
            print("   📱 Events will be sent to SmartThings simulation")
            print("\n🎯 Watch the console for real-time detection events!")
        else:
            print("❌ Motion sensor test setup failed!")
            return
    
    # Monitor detection every frame
    monitor_motion_detection()

def get_test_statistics():
    """Get test statistics and sensor performance data"""
    
    scene = bge.logic.getCurrentScene()
    
    if hasattr(scene, 'vesper_device_manager'):
        device_manager = scene.vesper_device_manager
        status = device_manager.get_motion_detection_status()
        
        test_duration = time.time() - getattr(scene, 'test_start_time', time.time())
        
        print("\n📊 MOTION SENSOR TEST STATISTICS")
        print("=" * 50)
        print(f"⏱️ Test Duration: {test_duration:.1f} seconds")
        print(f"🔍 Total Sensors: {status.get('total_sensors', 0)}")
        print(f"✅ Active Sensors: {status.get('active_sensors', 0)}")
        
        sensors = status.get('sensors', {})
        total_detections = sum(s.get('detection_count', 0) for s in sensors.values())
        print(f"🚨 Total Detections: {total_detections}")
        
        print("\n📋 Sensor Performance:")
        for sensor_id, sensor_data in sensors.items():
            room = sensor_data.get('room', 'unknown')
            count = sensor_data.get('detection_count', 0)
            position = sensor_data.get('position', [0, 0, 0])
            detecting = sensor_data.get('detecting', False)
            
            print(f"   {sensor_id}:")
            print(f"     🏠 Room: {room}")
            print(f"     📍 Position: [{position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f}]")
            print(f"     🔢 Detections: {count}")
            print(f"     🔴 Currently: {'DETECTING' if detecting else 'idle'}")
        
        return {
            "test_duration": test_duration,
            "total_detections": total_detections,
            "sensor_count": status.get('total_sensors', 0),
            "sensors": sensors
        }
    
    return {"error": "Device manager not available"}

# Example usage in BGE:
"""
# Add this to your BGE logic brick or main loop:

from blender.test_motion_sensors import run_motion_sensor_test, get_test_statistics

# In main game loop (every frame):
run_motion_sensor_test()

# To get statistics (call when needed):
stats = get_test_statistics()
"""

# If running this script directly in BGE
if __name__ == "__main__":
    run_motion_sensor_test()
