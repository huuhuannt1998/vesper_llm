"""
Complete navigation system test with different actor orientations
Tests the full pipeline from BGE orientation to map generation
"""

import math
import sys
import os

# Simulate the BGE environment with different orientations
class MockBGE:
    class MockActor:
        def __init__(self, orientation_radians=0.0):
            class MockPosition:
                x = -1.8
                y = -2.4
                z = -1.0
            self.worldPosition = MockPosition()
            
            # Mock orientation with Euler angles
            class MockOrientation:
                def to_euler(self):
                    # Return (x, y, z) Euler angles - z is the yaw (facing direction)
                    return (0.0, 0.0, orientation_radians)
            
            self.worldOrientation = MockOrientation()
    
    class MockScene:
        def __init__(self, actor_orientation=0.0):
            self.objects = {"Actor": MockBGE.MockActor(actor_orientation)}
        
        def get(self, name):
            return self.objects.get(name)
    
    class MockLogic:
        def __init__(self, orientation=0.0):
            self.scene = MockBGE.MockScene(orientation)
        
        def getCurrentScene(self):
            return self.scene
        
        current_task = "Testing orientation"
        current_room = "LIVING_ROOM"

def test_navigation_orientations():
    """Test navigation system with different actor orientations"""
    
    print("🧭 Testing Navigation System Orientation Alignment")
    print("=" * 70)
    
    # Add map directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_dir = os.path.join(os.path.dirname(current_dir), 'map')
    if map_dir not in sys.path:
        sys.path.insert(0, map_dir)
    
    from bge_integration import update_actor_position_map
    
    # Test different orientations
    orientations = [
        (0,           "East  (Right)"),
        (math.pi/2,   "North (Up)"),
        (math.pi,     "West  (Left)"),
        (3*math.pi/2, "South (Down)"),
    ]
    
    for i, (orientation, direction) in enumerate(orientations):
        print(f"\n🎯 Test {i+1}: Actor facing {direction}")
        print("-" * 50)
        
        # Create mock BGE environment
        mock_bge = MockBGE()
        mock_logic = MockBGE.MockLogic(orientation)
        
        # Replace bge modules for this test
        sys.modules['bge'] = mock_bge
        sys.modules['bge.logic'] = mock_logic
        
        try:
            # Test map generation with actor position and orientation
            result = update_actor_position_map(
                world_x=-1.8, 
                world_y=-2.4, 
                room="LIVING_ROOM",
                task=f"Testing {direction} orientation",
                orientation=orientation
            )
            
            if result:
                print(f"✅ Map generated successfully for {direction} orientation")
                print(f"📍 Generated: {result}")
            else:
                print(f"❌ Map generation failed for {direction} orientation")
                
        except Exception as e:
            print(f"❌ Error testing {direction} orientation: {e}")
    
    print(f"\n🎉 Navigation orientation testing complete!")
    print(f"🗺️ Check generated maps in: map/generated_maps/")
    print(f"🧭 Orientation arrows should now point in the correct direction!")

if __name__ == "__main__":
    test_navigation_orientations()