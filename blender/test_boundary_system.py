#!/usr/bin/env python3
"""
Test script for boundary checking system
"""

def is_position_inside_house(x, y):
    """Check if position is within house boundaries based on the floor plan"""
    MIN_X = -6.0   # Leftmost wall
    MAX_X = 2.0    # Rightmost wall  
    MIN_Y = -3.0   # Bottom wall
    MAX_Y = 4.0    # Top wall
    
    return MIN_X <= x <= MAX_X and MIN_Y <= y <= MAX_Y

def test_boundary_checking():
    """Test the boundary checking with various positions"""
    
    test_positions = [
        # Inside house (should be True)
        (-2.98, 1.0, "Inside house center"),
        (-1.0, 0.0, "Inside house middle"),
        (-5.0, 2.0, "Inside house left side"),
        (1.0, 3.0, "Inside house right side"),
        
        # Outside house (should be False)
        (-2.98, 7.74, "Outside house (your actor's problem position)"),
        (-7.0, 1.0, "Outside house - too far left"),
        (3.0, 1.0, "Outside house - too far right"),
        (-2.0, -4.0, "Outside house - too far down"),
        (-2.0, 5.0, "Outside house - too far up"),
        
        # Edge cases
        (-6.0, 1.0, "Left boundary edge"),
        (2.0, 1.0, "Right boundary edge"),
        (-2.0, -3.0, "Bottom boundary edge"),
        (-2.0, 4.0, "Top boundary edge"),
    ]
    
    print("🧪 Testing Boundary Checking System\n")
    print("House boundaries:")
    print("  X range: -6.0 to 2.0")
    print("  Y range: -3.0 to 4.0")
    print()
    
    for x, y, description in test_positions:
        inside = is_position_inside_house(x, y)
        status = "✅ INSIDE" if inside else "❌ OUTSIDE"
        print(f"{status} | ({x:5.1f}, {y:5.1f}) | {description}")
    
    print("\n🎯 Key Findings:")
    print(f"  • Your actor at (-2.98, 7.74) is: {'INSIDE' if is_position_inside_house(-2.98, 7.74) else 'OUTSIDE'}")
    print(f"  • Safe center position (-2.0, 1.0) is: {'INSIDE' if is_position_inside_house(-2.0, 1.0) else 'OUTSIDE'}")
    
    print("\n🔧 Boundary System Active:")
    print("  • Actor will be reset to (-2.0, 1.0) when outside bounds")
    print("  • All movement will be validated before execution")
    print("  • VLM timeouts will trigger boundary-aware fallback navigation")

if __name__ == "__main__":
    test_boundary_checking()
