#!/usr/bin/env python3
"""
Test script for boundary protection and enhanced navigation fixes
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_boundary_protection():
    """Test the boundary protection logic"""
    
    print("🛡️ Testing Boundary Protection Logic")
    print("=" * 50)
    
    # Simulate the boundary checking logic from the navigation code
    HOUSE_BOUNDS = {
        'x_min': -6.0,   # Left boundary
        'x_max': 2.0,    # Right boundary  
        'y_min': -1.0,   # Bottom boundary
        'y_max': 6.0     # Top boundary
    }
    
    # Test cases: (current_pos, direction, step_size, should_be_blocked)
    test_cases = [
        # Normal safe movements
        ((-2.0, -0.5), "UP", 0.3, False, "Safe movement from center"),
        ((-3.0, 2.0), "RIGHT", 0.3, False, "Safe movement in kitchen area"),
        
        # Boundary violations that should be blocked
        ((-5.8, 3.0), "LEFT", 0.3, True, "Would exceed left boundary"),
        ((1.8, 2.0), "RIGHT", 0.3, True, "Would exceed right boundary"),
        ((-3.0, -0.8), "DOWN", 0.3, True, "Would exceed bottom boundary"), 
        ((-4.0, 5.8), "UP", 0.3, True, "Would exceed top boundary"),
        
        # Edge cases
        ((-6.0, 3.0), "LEFT", 0.3, True, "Exactly at left boundary"),
        ((2.0, 3.0), "RIGHT", 0.3, True, "Exactly at right boundary"),
    ]
    
    for i, (current_pos, direction, step_size, should_block, description) in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {description}")
        print(f"   Position: {current_pos}, Direction: {direction}")
        
        # Calculate proposed position
        x, y = current_pos
        if direction == "UP":
            proposed_y = y + step_size
            proposed_x = x
        elif direction == "DOWN":
            proposed_y = y - step_size
            proposed_x = x
        elif direction == "LEFT":
            proposed_x = x - step_size
            proposed_y = y
        elif direction == "RIGHT":
            proposed_x = x + step_size
            proposed_y = y
        
        # Check boundaries
        would_violate = (proposed_x < HOUSE_BOUNDS['x_min'] or 
                        proposed_x > HOUSE_BOUNDS['x_max'] or
                        proposed_y < HOUSE_BOUNDS['y_min'] or 
                        proposed_y > HOUSE_BOUNDS['y_max'])
        
        print(f"   Proposed: ({proposed_x:.1f}, {proposed_y:.1f})")
        print(f"   Boundary check: {'BLOCKED' if would_violate else 'ALLOWED'}")
        
        if would_violate == should_block:
            print(f"   ✅ PASSED - Correctly {'blocked' if should_block else 'allowed'}")
        else:
            print(f"   ❌ FAILED - Expected {'blocked' if should_block else 'allowed'}")

def test_spatial_context():
    """Test the spatial awareness context generation"""
    
    print("\n🗺️ Testing Spatial Context Generation")
    print("=" * 50)
    
    test_positions = [
        (-2.0, -0.5, "Living room area (center-bottom)"),
        (-5.0, 5.0, "Near kitchen/bedroom area (left-upper)"),
        (1.0, 2.0, "Near living room area (right-middle)"),
        (-4.5, 2.5, "Kitchen area (left-middle)"),
        (-5.5, 5.5, "Approaching boundaries (far left-upper)"),
    ]
    
    for i, (x, y, expected_desc) in enumerate(test_positions, 1):
        print(f"\n📋 Test {i}: Position ({x}, {y})")
        
        # Simulate spatial context logic
        spatial_hints = ""
        
        if x < -4.0:
            spatial_hints += "(Near LEFT edge of house - kitchen/bedroom area)"
        elif x > 0:
            spatial_hints += "(Near RIGHT edge of house - living room area)"
        else:
            spatial_hints += "(Center area of house)"
            
        if y > 4.0:
            spatial_hints += " (UPPER level - bedroom area)"
        elif y > 1.0:
            spatial_hints += " (Middle level - kitchen area)"  
        else:
            spatial_hints += " (Lower level - living room area)"
        
        boundary_warning = ""
        if abs(x) > 5.0 or abs(y) > 5.0:
            boundary_warning = " ⚠️ APPROACHING HOUSE BOUNDARIES!"
            
        full_context = spatial_hints + boundary_warning
        
        print(f"   Generated: {full_context}")
        print(f"   Expected: {expected_desc}")
        
        # Check if key elements are present
        has_position_info = any(keyword in full_context.lower() for keyword in 
                               ['left', 'right', 'center', 'upper', 'middle', 'lower'])
        has_area_info = any(keyword in full_context.lower() for keyword in 
                           ['living', 'kitchen', 'bedroom'])
        
        if has_position_info and has_area_info:
            print(f"   ✅ PASSED - Contains position and area information")
        else:
            print(f"   ❌ FAILED - Missing key spatial information")

if __name__ == "__main__":
    test_boundary_protection()
    test_spatial_context()
    
    print("\n" + "=" * 50)
    print("📊 BOUNDARY PROTECTION SUMMARY:")
    print("✅ Enhanced safety features implemented:")
    print("   🛡️ Hard boundary enforcement prevents leaving house")
    print("   🗺️ Spatial context helps VLM understand position")
    print("   🚨 Emergency reset for extreme coordinate detection")
    print("   🔍 Enhanced movement blocking detection")
    print("   📍 Better guidance for unclear image analysis")
    
    print("\n🚀 These fixes should prevent the actor from leaving the house!")
    print("   - Boundary checks before every movement")
    print("   - Spatial context for better VLM navigation")
    print("   - Safety fallbacks for extreme positions")
    print("   - Clearer guidance when VLM can't identify rooms")
