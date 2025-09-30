"""
Test script to verify map generation integration works
"""

# Simulate the BGE environment
class MockBGE:
    class MockActor:
        def __init__(self):
            class MockPosition:
                x = -1.8
                y = -2.4
                z = -1.0
            self.worldPosition = MockPosition()
    
    class MockScene:
        def __init__(self):
            self.objects = {"Actor": MockBGE.MockActor()}
        
        def get(self, name):
            return self.objects.get(name)
    
    class MockLogic:
        @staticmethod
        def getCurrentScene():
            return MockBGE.MockScene()
        
        current_task = "Go to kitchen"
        current_room = "LIVING_ROOM"

# Mock bge module for testing
import sys
sys.modules['bge'] = MockBGE()
sys.modules['bge.logic'] = MockBGE.MockLogic()

# Test the map generation
def test_map_generation():
    try:
        # Import the position mapper functions
        import os
        import sys
        
        # Add map directory to path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        map_dir = os.path.join(os.path.dirname(current_dir), 'map')
        if map_dir not in sys.path:
            sys.path.insert(0, map_dir)
        
        from bge_integration import update_actor_position_map
        
        print("🧪 Testing Map Generation Integration")
        print("=" * 40)
        
        # Test with sample actor position
        world_x = -1.8
        world_y = -2.4
        current_room = "LIVING_ROOM"
        current_task = "Go to kitchen"
        
        print(f"📍 Actor Position: ({world_x}, {world_y})")
        print(f"🏠 Current Room: {current_room}")
        print(f"🎯 Current Task: {current_task}")
        
        # Generate map
        map_path = update_actor_position_map(
            world_x, world_y,
            room=current_room,
            task=current_task
        )
        
        if map_path and os.path.exists(map_path):
            print(f"✅ Map generated successfully: {os.path.basename(map_path)}")
            print(f"📂 Full path: {map_path}")
            return True
        else:
            print("❌ Map generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_map_generation()
    if success:
        print("\n🎉 Map generation integration test PASSED!")
        print("✅ BGE navigation should now generate dynamic maps")
    else:
        print("\n💥 Map generation integration test FAILED!")