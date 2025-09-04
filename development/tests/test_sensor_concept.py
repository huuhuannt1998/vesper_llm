#!/usr/bin/env python3
"""
Standalone test for single sensor per room deployment (without BGE dependencies)
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Mock the BGE import for standalone testing
class MockBGE:
    def __init__(self):
        pass

import sys
sys.modules['bge'] = MockBGE()

# Now we can import our motion validation system
from blender.vesper_motion_validation import VESPERMotionValidationSystem

async def test_single_sensor_concept():
    """Test the single sensor per room concept"""
    print("🧪 Testing Single Motion Sensor Per Room Concept\n")
    
    # Show the room-to-sensor mapping
    validation_system = VESPERMotionValidationSystem()
    
    print("1. Room-to-CASAS Sensor Mapping (Primary sensor per room):")
    for room_name, sensor_ids in validation_system.room_sensor_mapping.items():
        primary_sensor = sensor_ids[0]  # First sensor is primary
        all_sensors = ', '.join(sensor_ids)
        print(f"   - {room_name}: Primary={primary_sensor} (Available: {all_sensors})")
    
    print(f"\n2. Simulating sensor deployment...")
    
    # Simulate the deployment process
    validation_system._setup_simulation_mode()
    
    print(f"\n3. Deployed sensors (with calculated positions):")
    for room_name, sensor_info in validation_system.deployed_sensors.items():
        casas_id = sensor_info['casas_sensor_id']
        position = sensor_info['position']
        
        # Calculate expected position
        boundaries = validation_system.room_boundaries.get(room_name, {})
        if boundaries:
            expected_x = (boundaries['x_min'] + boundaries['x_max']) / 2
            expected_y = (boundaries['y_min'] + boundaries['y_max']) / 2
            print(f"   - {room_name}: {casas_id} at {position} (should be ({expected_x}, {expected_y}))")
        else:
            print(f"   - {room_name}: {casas_id} at {position} (no boundaries defined)")
    
    print(f"\n3b. Room boundaries for debugging:")
    for room_name, boundaries in validation_system.room_boundaries.items():
        print(f"   - {room_name}: x={boundaries['x_min']} to {boundaries['x_max']}, y={boundaries['y_min']} to {boundaries['y_max']}")
    
    print(f"\n4. Testing room detection and sensor activation...")
    
    # Test positions and expected rooms
    test_positions = [
        (-1, 0, "living_room"),   # Living room center
        (5, 1, "kitchen"),        # Kitchen center  
        (0, 4, "dining_room"),    # Dining room center
        (-4, 4, "bedroom"),       # Bedroom center
        (6, 6, "bathroom"),       # Bathroom center
        (-6, 0, "office"),        # Office center
        (8, -2, "garage")         # Garage center
    ]
    
    print("\n   Movement sequence:")
    for x, y, expected_room in test_positions:
        detected_room = validation_system.detect_actor_room((x, y))
        await validation_system.update_motion_sensors((x, y))
        
        # Show which sensor would be activated
        if detected_room in validation_system.deployed_sensors:
            sensor_info = validation_system.deployed_sensors[detected_room]
            casas_id = sensor_info['casas_sensor_id']
            status = "✅" if detected_room == expected_room else "❌"
            print(f"   {status} Position ({x:2}, {y:2}) → {detected_room:12} (Sensor: {casas_id})")
        else:
            print(f"   ❓ Position ({x:2}, {y:2}) → {detected_room:12} (No sensor)")
        
        await asyncio.sleep(0.1)  # Brief pause
    
    print(f"\n5. Movement history (last 5 moves):")
    for i, event in enumerate(validation_system.actor_location_history[-5:], 1):
        from_room = event['from_room'] or 'start'
        to_room = event['to_room']
        timestamp = event['timestamp'][:19]
        casas_sensors = event['casas_sensors_activated']
        
        print(f"   {i}. {from_room:12} → {to_room:12} at {timestamp}")
        if casas_sensors:
            print(f"      📊 Activated CASAS sensors: {', '.join(casas_sensors)}")
    
    print(f"\n6. Key improvements with single sensor per room:")
    print("   ✅ Simplified deployment: 1 sensor per room instead of multiple")
    print("   ✅ Reduced complexity: Room name as sensor key")
    print("   ✅ Same CASAS compatibility: Uses primary sensor ID from each room")
    print("   ✅ Efficient tracking: Clear room-to-sensor mapping")
    print("   ✅ Graceful fallback: Works in simulation mode when backend unavailable")
    
    print(f"\n7. Virtual device spawning integration:")
    print("   🔧 Uses same device spawning function as your current system")
    print("   🔧 Deploys motion-sensor type with specific CASAS IDs")
    print("   🔧 Room-based naming: e.g., 'M01_living_room', 'M13_kitchen'")
    print("   🔧 Automatic cleanup when sensors no longer needed")

if __name__ == "__main__":
    asyncio.run(test_single_sensor_concept())
