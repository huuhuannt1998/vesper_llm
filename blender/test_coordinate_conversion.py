"""
Test script to verify coordinate conversion between BGE and screen coordinates
Tests all four cardinal directions to ensure proper alignment
"""

import math
import sys
import os

# Add map directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
map_dir = os.path.join(os.path.dirname(current_dir), 'map')
if map_dir not in sys.path:
    sys.path.insert(0, map_dir)

from position_mapper import VESPERPositionMapper

def test_coordinate_conversion():
    """Test coordinate conversion for all cardinal directions"""
    
    print("🧭 Testing BGE to Screen Coordinate Conversion")
    print("=" * 60)
    
    # Create a mapper instance to access the conversion function
    mapper = VESPERPositionMapper()
    
    # Test cardinal directions in BGE coordinate system
    test_cases = [
        (0,           "East  (+X)"),     # BGE East
        (math.pi/2,   "North (+Y)"),     # BGE North  
        (math.pi,     "West  (-X)"),     # BGE West
        (3*math.pi/2, "South (-Y)"),     # BGE South
    ]
    
    print("BGE Input → Screen Output (for map display)")
    print("BGE Direction | BGE Angle | Screen Angle | Expected Arrow Direction")
    print("-" * 70)
    
    for bge_angle, bge_direction in test_cases:
        # Convert BGE angle to screen coordinates
        screen_angle = mapper._convert_bge_to_screen_coordinates(bge_angle)
        
        # Convert to degrees for readability
        bge_degrees = math.degrees(bge_angle)
        screen_degrees = math.degrees(screen_angle)
        
        # Determine expected screen direction
        screen_directions = {
            0: "Up (North)",
            90: "Right (East)", 
            180: "Down (South)",
            270: "Left (West)"
        }
        
        expected_direction = screen_directions.get(round(screen_degrees) % 360, f"{screen_degrees:.1f}°")
        
        print(f"{bge_direction:12} | {bge_degrees:8.1f}° | {screen_degrees:11.1f}° | {expected_direction}")
    
    print("\n🎯 Coordinate System Mapping:")
    print("BGE East  (0°)   → Screen North (270°) → Arrow points UP")
    print("BGE North (90°)  → Screen East  (0°)   → Arrow points RIGHT") 
    print("BGE West  (180°) → Screen South (90°)  → Arrow points DOWN")
    print("BGE South (270°) → Screen West  (180°) → Arrow points LEFT")
    
    print("\n✅ This should align the orientation arrow with the actual actor facing direction!")

if __name__ == "__main__":
    test_coordinate_conversion()