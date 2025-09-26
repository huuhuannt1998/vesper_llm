#!/usr/bin/env python3
"""
Test to compare different actor sizes
"""

import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from map.position_mapper import VESPERPositionMapper


def test_actor_sizes():
    """Test different actor sizes to show the difference"""
    
    print("🎭 Testing Different Actor Sizes")
    print("=" * 40)
    
    # Test different sizes
    sizes_to_test = [
        (12, "Original size"),
        (16, "Medium size"), 
        (20, "Current size (bigger)"),
        (24, "Extra large size")
    ]
    
    house_layout_path = "blender/house_layout_reference2.png"
    
    for size, description in sizes_to_test:
        print(f"\n🧑 Testing {description} (size={size})...")
        
        # Create mapper with custom size
        mapper = VESPERPositionMapper(house_layout_path)
        mapper.actor_marker_size = size  # Override size
        
        # Set a test position in the center
        mapper.update_actor_position(
            world_x=0.0, 
            world_y=0.0,
            room=f"TestRoom_Size{size}",
            task=f"Testing actor size {size}",
            target_room="Target"
        )
        
        # Set direction
        mapper.direction = 45
        
        # Generate map with this size
        map_path = mapper.generate_navigation_context_map()
        
        if map_path:
            new_name = f"size_test_{size}_{os.path.basename(map_path)}"
            new_path = os.path.join(os.path.dirname(map_path), new_name)
            
            try:
                os.rename(map_path, new_path)
                print(f"  ✅ Generated: {new_name}")
            except Exception as e:
                print(f"  ⚠️ Generated: {os.path.basename(map_path)} (rename failed: {e})")
        else:
            print(f"  ❌ Failed to generate map")
    
    print(f"\n📊 Size Comparison Complete!")
    print(f"Check the generated maps to see the size differences:")
    print(f"  - size_test_12_*.png (Original size)")
    print(f"  - size_test_16_*.png (Medium size)")
    print(f"  - size_test_20_*.png (Current bigger size)")
    print(f"  - size_test_24_*.png (Extra large size)")


if __name__ == "__main__":
    test_actor_sizes()