#!/usr/bin/env python3
"""
Test script for the human indicator system using the real house layout
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from map.position_mapper import VESPERPositionMapper


def test_real_house_layout():
    """Test with the actual house layout"""
    
    # Use the real house layout 
    house_layout_path = "blender/house_layout_reference2.png"
    
    if not os.path.exists(house_layout_path):
        print(f"❌ Real house layout not found at {house_layout_path}")
        print("Available house layouts:")
        for layout in ["blender/house_layout_reference.png", 
                      "blender/house_layout_reference2.png",
                      "blender/house_layout_reference3.png",
                      "blender/house_layout_reference2-2.png"]:
            if os.path.exists(layout):
                print(f"  ✅ {layout}")
            else:
                print(f"  ❌ {layout}")
        return False
    
    print(f"🏠 Using real house layout: {house_layout_path}")
    
    # Initialize the position mapper with real house layout
    mapper = VESPERPositionMapper(house_layout_path)
    
    # Use realistic BGE world coordinates (within the expected bounds)
    realistic_positions = [
        (-5.0, -3.0),   # Start in one room
        (-2.0, -3.0),   # Move towards center
        (0.0, 0.0),     # Center of house
        (2.0, 3.0),     # Move to another room
        (4.0, 3.0),     # Final position
    ]
    
    print(f"📍 Testing with realistic coordinates: {realistic_positions}")
    
    # Simulate movement through the house
    for i, (x, y) in enumerate(realistic_positions):
        room = f"Room_{chr(65+i)}"  # Room_A, Room_B, etc.
        target = f"Room_{chr(66+i)}" if i < len(realistic_positions)-1 else "Final"
        
        mapper.update_actor_position(
            world_x=x, 
            world_y=y,
            room=room,
            task=f"Step {i+1}: Navigate to {target}",
            target_room=target
        )
        print(f"  Step {i+1}: World({x}, {y}) → Map{mapper.current_position}")
    
    # Set direction for the final position
    mapper.direction = 90  # North direction
    
    print("\n🗺️ Generating navigation context map...")
    
    # Generate navigation context map
    nav_map_path = mapper.generate_navigation_context_map()
    
    if nav_map_path and os.path.exists(nav_map_path):
        print(f"✅ Navigation context map: {nav_map_path}")
    else:
        print("❌ Failed to generate navigation context map")
        return False
    
    print("\n🗺️ Generating current position map...")
    
    # Generate current position map
    pos_map_path = mapper.generate_current_position_map(include_history=True)
    
    if pos_map_path and os.path.exists(pos_map_path):
        print(f"✅ Current position map: {pos_map_path}")
    else:
        print("❌ Failed to generate current position map")
        return False
    
    # Show final status
    print(f"\n📊 Final Status:")
    print(f"  Current position: {mapper.current_position}")
    print(f"  Direction: {mapper.direction}°")
    print(f"  Movement history: {len(mapper.position_history)} positions")
    print(f"  Current room: {mapper.current_room}")
    print(f"  Target room: {mapper.target_room}")
    
    print(f"\n🎉 Real house layout test completed!")
    print(f"Generated maps should now show human indicators on the actual house layout.")
    
    return True


def test_coordinate_calibration():
    """Test coordinate system calibration"""
    
    print("\n🔧 Testing coordinate calibration...")
    
    mapper = VESPERPositionMapper()
    
    # Test corner coordinates
    test_coords = [
        (-10.0, -8.0, "Bottom-left corner"),
        (10.0, -8.0, "Bottom-right corner"), 
        (-10.0, 8.0, "Top-left corner"),
        (10.0, 8.0, "Top-right corner"),
        (0.0, 0.0, "Center"),
    ]
    
    print("Coordinate mapping test:")
    for world_x, world_y, description in test_coords:
        map_x, map_y = mapper._world_to_map_coordinates(world_x, world_y)
        print(f"  {description}: World({world_x}, {world_y}) → Map({map_x}, {map_y})")
    
    return True


if __name__ == "__main__":
    print("🏠 VESPER Human Indicator - Real House Layout Test")
    print("=" * 50)
    
    # Test with real house layout
    success1 = test_real_house_layout()
    
    # Test coordinate calibration
    success2 = test_coordinate_calibration()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")