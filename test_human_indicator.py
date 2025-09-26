#!/usr/bin/env python3
"""
Test script for the human indicator system
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from map.position_mapper import VESPERPositionMapper


def test_human_indicator():
    """Test the human indicator visualization"""
    
    # Use the existing house layout if available
    house_layout_path = "data/house_layouts/B102.png"  # or wherever your house layout is
    
    # Check if file exists, if not create a dummy one
    if not os.path.exists(house_layout_path):
        print(f"House layout not found at {house_layout_path}")
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(house_layout_path), exist_ok=True)
        
        # Create a simple test layout
        from PIL import Image, ImageDraw
        
        # Create a simple house layout for testing
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw some rooms
        draw.rectangle([50, 50, 300, 250], outline='black', width=2)  # Living room
        draw.text((60, 60), "Living Room", fill='black')
        
        draw.rectangle([300, 50, 550, 250], outline='black', width=2)  # Kitchen
        draw.text((310, 60), "Kitchen", fill='black')
        
        draw.rectangle([50, 250, 300, 450], outline='black', width=2)  # Bedroom
        draw.text((60, 260), "Bedroom", fill='black')
        
        draw.rectangle([300, 250, 550, 450], outline='black', width=2)  # Bathroom
        draw.text((310, 260), "Bathroom", fill='black')
        
        img.save(house_layout_path)
        print(f"Created test house layout at {house_layout_path}")
    
    # Initialize the position mapper
    mapper = VESPERPositionMapper(house_layout_path)
    
    # Add some movement history by updating position multiple times
    history_positions = [
        (150, 140),  # Previous position 1
        (160, 145),  # Previous position 2  
        (170, 148),  # Previous position 3
        (175, 150),  # Final position (current)
    ]
    
    for i, pos in enumerate(history_positions):
        mapper.update_actor_position(
            world_x=pos[0], 
            world_y=pos[1],
            room="Living Room",
            task=f"Step {i+1}: Walking to the kitchen",
            target_room="Kitchen"
        )
    
    # Set direction manually (since it's not part of update_actor_position)
    mapper.direction = 45  # Northeast direction
    
    print("Generating navigation context map with human indicator...")
    
    # Generate navigation context map
    map_path = mapper.generate_navigation_context_map()
    
    if map_path and os.path.exists(map_path):
        print(f"✅ Navigation context map generated: {map_path}")
        print(f"   - Human figure at position ({mapper.current_position[0]}, {mapper.current_position[1]})")
        print(f"   - Direction: {mapper.direction}°")
        print(f"   - Position history: {len(mapper.position_history)} footprints")
        print(f"   - Current room: {mapper.current_room}")
        print(f"   - Target room: {mapper.target_room}")
        
        # Try to open the file to verify it was created correctly
        try:
            from PIL import Image
            img = Image.open(map_path)
            print(f"   - Image size: {img.size}")
            print(f"   - Image mode: {img.mode}")
            img.close()
        except Exception as e:
            print(f"   ⚠️ Warning: Could not verify image: {e}")
            
    else:
        print("❌ Failed to generate navigation context map")
        return False
    
    print("\nTesting current position map generation...")
    
    # Test full map generation
    full_map_path = mapper.generate_current_position_map(include_history=True)
    
    if full_map_path and os.path.exists(full_map_path):
        print(f"✅ Current position map generated: {full_map_path}")
    else:
        print("❌ Failed to generate current position map")
        
    print("\nTesting position data JSON...")
    
    # Test position data by accessing the attributes directly
    print(f"Current position: {mapper.current_position}")
    print(f"Direction: {mapper.direction}")
    print(f"History count: {len(mapper.position_history)}")
    print(f"Current room: {mapper.current_room}")
    print(f"Target room: {mapper.target_room}")
    
    print("\n🎉 Human indicator system test completed!")
    print(f"Check the generated maps in the map/generated_maps/ directory:")
    print(f"  - Navigation context: {map_path}")
    if full_map_path:
        print(f"  - Current position map: {full_map_path}")
    
    return True


if __name__ == "__main__":
    test_human_indicator()