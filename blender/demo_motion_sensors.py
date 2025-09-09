"""
VESPER Motion Sensor Demo Script
===============================

Quick demonstration of the realistic Aeotec SmartThings Motion Sensor detection system.
This script shows how to:

1. Set up motion sensors with realistic specifications
2. Monitor Actor movement and trigger detections
3. Integrate with SmartThings app simulation
4. View real-time detection events

Run this in Blender Game Engine (BGE) to see motion sensors in action.
"""

import bge
import mathutils
from mathutils import Vector
import time

def run_motion_sensor_demo():
    """Run interactive motion sensor demonstration"""
    
    scene = bge.logic.getCurrentScene()
    
    # Initialize demo only once
    if not hasattr(bge.logic, 'motion_demo_initialized'):
        print("🎬 VESPER Motion Sensor Detection Demo")
        print("=" * 50)
        
        # Check for Actor
        actor = scene.objects.get("Actor") 
        if not actor:
            print("❌ No Actor object found! Please add an Actor to the scene.")
            return
        
        print("🎯 Demo Features:")
        print("   • Aeotec SmartThings Motion Sensor specs (120° FOV, 5m range)")
        print("   • Real-time Actor position tracking")
        print("   • Realistic detection zones and cooldown periods")
        print("   • SmartThings app integration simulation")
        
        # Set up demo sensors
        try:
            # Import device manager
            import sys
            import os
            addon_path = os.path.join(os.path.dirname(__file__), "addons", "vesper_smart_home") 
            if addon_path not in sys.path:
                sys.path.append(addon_path)
            
            from addons.vesper_smart_home import device_manager
            scene.vesper_device_manager = device_manager
            
            # Add demo sensors
            demo_sensors = [
                {"id": "DEMO_Center", "pos": Vector((0, 0, 2)), "room": "center", "angle": 0},
                {"id": "DEMO_Corner", "pos": Vector((3, 3, 2)), "room": "corner", "angle": 225},
                {"id": "DEMO_Wall", "pos": Vector((-2, 4, 2)), "room": "wall", "angle": 180}
            ]
            
            sensors_added = 0
            for sensor in demo_sensors:
                success = device_manager.add_motion_sensor(
                    sensor["id"], sensor["room"], sensor["pos"], sensor["angle"]
                )
                if success:
                    sensors_added += 1
            
            print(f"✅ Demo setup complete: {sensors_added} sensors active")
            
            # Store demo state
            bge.logic.motion_demo_initialized = True
            bge.logic.demo_start_time = time.time()
            bge.logic.last_position = Vector((actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z))
            bge.logic.detection_events = []
            bge.logic.frame_counter = 0
            
            print("\n🎮 DEMO CONTROLS:")
            print("   🠉🠇🠈🠊 Arrow keys: Move Actor around")
            print("   🔍 Watch console for detection events")
            print("   📱 SmartThings notifications will be simulated")
            print("\n🚀 Demo started! Move the Actor to trigger motion sensors...")
            
        except Exception as e:
            print(f"❌ Demo setup failed: {e}")
            return
    
    # Update motion detection every frame
    if hasattr(scene, 'vesper_device_manager'):
        device_manager = scene.vesper_device_manager
        device_manager.update_motion_detection()
        
        # Get current Actor position
        actor = scene.objects.get("Actor")
        if actor:
            current_pos = Vector((actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z))
            
            # Check if Actor moved significantly
            if hasattr(bge.logic, 'last_position'):
                movement = (current_pos - bge.logic.last_position).length
                if movement > 0.5:  # Significant movement
                    bge.logic.last_position = current_pos.copy()
                    
                    # Display position update
                    if bge.logic.frame_counter % 30 == 0:  # Every 0.5 seconds at 60fps
                        print(f"📍 Actor moved to: [{current_pos.x:.1f}, {current_pos.y:.1f}]")
            
            bge.logic.frame_counter += 1
            
            # Display status every 5 seconds
            if bge.logic.frame_counter % 300 == 0:
                status = device_manager.get_motion_detection_status()
                detecting_count = status.get('sensors_detecting', 0)
                total_detections = sum(
                    s.get('detection_count', 0) 
                    for s in status.get('sensors', {}).values()
                )
                
                demo_time = time.time() - bge.logic.demo_start_time
                print(f"\n📊 Demo Status ({demo_time:.1f}s):")
                print(f"   🔍 Sensors Currently Detecting: {detecting_count}")
                print(f"   📈 Total Detection Events: {total_detections}")
                print(f"   📍 Actor Position: [{current_pos.x:.1f}, {current_pos.y:.1f}]")

def show_detection_zones():
    """Show visual representation of detection zones (for debugging)"""
    
    scene = bge.logic.getCurrentScene()
    
    if hasattr(scene, 'vesper_device_manager'):
        status = scene.vesper_device_manager.get_motion_detection_status()
        sensors = status.get('sensors', {})
        
        print("\n🎯 MOTION SENSOR DETECTION ZONES:")
        print("=" * 45)
        
        for sensor_id, sensor_data in sensors.items():
            pos = sensor_data.get('position', [0, 0, 0])
            room = sensor_data.get('room', 'unknown')
            detecting = sensor_data.get('detecting', False)
            count = sensor_data.get('detection_count', 0)
            
            status_icon = "🔴" if detecting else "⚪"
            
            print(f"{status_icon} {sensor_id}:")
            print(f"     🏠 Room: {room}")
            print(f"     📍 Position: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]")
            print(f"     📏 Range: 5.0m, FOV: 120°")
            print(f"     🔢 Detections: {count}")
            
            # Calculate detection zone bounds (approximate)
            x, y = pos[0], pos[1]
            print(f"     🎯 Zone: X({x-5:.1f} to {x+5:.1f}), Y({y-5:.1f} to {y+5:.1f})")

def demo_sensor_placement_guide():
    """Show optimal sensor placement recommendations"""
    
    print("\n📐 OPTIMAL MOTION SENSOR PLACEMENT GUIDE:")
    print("=" * 55)
    print("🏠 Aeotec SmartThings Motion Sensor Specifications:")
    print("   📏 Detection Range: 5 meters (16 feet)")
    print("   👁️ Field of View: 120° (wide angle)")
    print("   📡 Technology: PIR (Passive Infrared)")
    print("   🔋 Power: CR2 3V Lithium Battery")
    print("   ⏱️ Cooldown: 3 seconds between detections")
    
    print("\n🎯 Placement Best Practices:")
    print("   📍 Height: 2-2.5 meters (6-8 feet) for optimal coverage")
    print("   🌡️ Avoid: Direct sunlight, heating vents, hot appliances")
    print("   👀 Position: Clear line of sight to main traffic areas")
    print("   🔄 Overlap: Multiple sensors for seamless coverage")
    print("   🔒 Security: Cover all entry points and valuable areas")
    
    print("\n🏠 Room-Specific Recommendations:")
    print("   🛋️ Living Room: Corner placement facing seating areas")
    print("   🍳 Kitchen: Above prep areas, facing counters/stove")
    print("   🛏️ Bedroom: Corner facing bed and entrance")
    print("   🚪 Hallway: Central position for traffic monitoring")
    print("   🚿 Bathroom: Near entrance, respecting privacy")
    print("   🏠 Entry: High priority for security monitoring")

def run_comprehensive_demo():
    """Run the complete motion sensor demonstration"""
    
    # Main demo loop
    run_motion_sensor_demo()
    
    # Show detection zones every 10 seconds
    if hasattr(bge.logic, 'frame_counter') and bge.logic.frame_counter % 600 == 0:
        show_detection_zones()
    
    # Show placement guide at start
    if hasattr(bge.logic, 'motion_demo_initialized') and hasattr(bge.logic, 'frame_counter'):
        if bge.logic.frame_counter == 60:  # Show after 1 second
            demo_sensor_placement_guide()

# Main entry point for BGE
if __name__ == "__main__":
    run_comprehensive_demo()

"""
INTEGRATION INSTRUCTIONS:
========================

1. Add this script to your Blender BGE project
2. Attach to a Game Logic sensor (Always sensor recommended)
3. Set Logic Frequency to 60Hz for smooth updates
4. Ensure Actor object exists in scene
5. Run game engine and move Actor around to see detection

Alternative: Add to existing navigation script:
```python
from blender.demo_motion_sensors import run_comprehensive_demo

# In your main game loop:
run_comprehensive_demo()
```
"""
