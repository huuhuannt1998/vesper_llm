"""
Coordinate System Validation Test

This test validates the conversion between BGE Game Engine coordinates
and Map display coordinates to ensure proper synchronization.
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
    """Test coordinate conversion between Game Engine and Map systems"""
    
    print("🧭 COORDINATE SYSTEM VALIDATION TEST")
    print("=" * 60)
    print("Testing conversion from BGE Game Engine to Map coordinates")
    print()
    
    # Create mapper instance
    mapper = VESPERPositionMapper()
    
    # Test cases based on actual coordinate system mapping observed
    test_cases = [
        # (bge_angle_rad, expected_direction, description)
        (0,           "WEST",  "BGE 0° (default forward) → WEST toward sofa"),
        (math.pi/2,   "SOUTH", "BGE 90° (turn left) → SOUTH (corrected mapping)"),
        (math.pi,     "EAST",  "BGE 180° (turn around) → EAST toward wall"),
        (3*math.pi/2, "NORTH", "BGE 270° (turn right) → NORTH (corrected mapping)"),
        (-math.pi/2,  "NORTH", "BGE -90° (turn right) → NORTH (same as 270°)"),
    ]
    
    print("BGE Game Engine Input → Map Display Output")
    print("-" * 60)
    print("BGE Angle | BGE Deg | Map Angle | Map Deg | Expected | Result")
    print("-" * 60)
    
    all_correct = True
    
    for bge_angle, expected_dir, description in test_cases:
        # Convert using the mapper's conversion function
        map_angle = mapper._convert_bge_to_screen_coordinates(bge_angle)
        
        # Convert to degrees
        bge_deg = math.degrees(bge_angle) % 360
        map_deg = math.degrees(map_angle) % 360
        
        # Determine actual direction from map angle
        actual_dir = "UNKNOWN"
        if 315 <= map_deg or map_deg < 45:
            actual_dir = "NORTH"
        elif 45 <= map_deg < 135:
            actual_dir = "EAST"
        elif 135 <= map_deg < 225:
            actual_dir = "SOUTH"
        elif 225 <= map_deg < 315:
            actual_dir = "WEST"
        
        # Check if conversion is correct
        is_correct = (actual_dir == expected_dir)
        result_icon = "✅" if is_correct else "❌"
        
        if not is_correct:
            all_correct = False
        
        print(f"{bge_angle:8.2f} | {bge_deg:6.1f} | {map_angle:8.2f} | {map_deg:6.1f} | {expected_dir:8} | {result_icon} {actual_dir}")
    
    print("-" * 60)
    
    # Summary
    if all_correct:
        print("🎉 ALL TESTS PASSED! Coordinate conversion is working correctly.")
        print()
        print("✅ Game Engine orientations correctly map to expected directions")
        print("✅ First-person view and map arrows should now be synchronized")
    else:
        print("❌ SOME TESTS FAILED! Coordinate conversion needs adjustment.")
        print()
        print("🔧 Review the _convert_bge_to_screen_coordinates function")
        print("🔧 Check the coordinate system conversion logic")
    
    print()
    print("🔍 Key Insight:")
    print("   When actor faces sofa in first-person → should show WEST arrow on map")
    print("   When actor faces wall in first-person → should show EAST arrow on map")
    print()
    print("📋 Usage:")
    print("   - Game Engine: Actor uses LEFT/RIGHT turns + FORWARD movement")
    print("   - Map Display: Shows NORTH/SOUTH/EAST/WEST for VLM spatial understanding")
    print("   - Conversion: Synchronizes both systems for accurate navigation")

def demonstrate_real_scenario():
    """Demonstrate the specific scenario from the user's images"""
    
    print("\n" + "=" * 60)
    print("🏠 REAL SCENARIO DEMONSTRATION")
    print("=" * 60)
    print("Based on the provided images where actor faces sofa but map shows wrong direction")
    print()
    
    # Simulate the scenario from the images
    # Actor is facing the sofa, which should be WEST on the map
    
    mapper = VESPERPositionMapper()
    
    # Assume BGE reports this orientation when actor faces sofa
    # (This would be determined from actual game testing)
    bge_orientation_facing_sofa = 0.0  # This is what BGE reports
    
    converted_angle = mapper._convert_bge_to_screen_coordinates(bge_orientation_facing_sofa)
    converted_deg = math.degrees(converted_angle) % 360
    
    # Determine direction
    if 225 <= converted_deg < 315:
        direction = "WEST (facing sofa) ✅"
        status = "CORRECT"
    else:
        direction = f"Wrong direction ({converted_deg:.1f}°) ❌"
        status = "INCORRECT"
    
    print(f"📊 Scenario: Actor faces sofa in first-person view")
    print(f"🎮 BGE reports: {bge_orientation_facing_sofa:.2f} rad (Game Engine)")
    print(f"🗺️ Map shows: {converted_deg:.1f}° → {direction}")
    print(f"🎯 Status: {status}")
    
    if status == "CORRECT":
        print("\n✅ Fix successful! Map arrow now matches first-person view")
    else:
        print("\n❌ Fix needed! Coordinate conversion requires adjustment")

if __name__ == "__main__":
    # Run both tests
    test_coordinate_conversion()
    demonstrate_real_scenario()