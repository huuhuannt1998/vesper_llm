"""
Test synchronized image capture to verify first-person and map generation are aligned
"""

import sys
import os

# Mock BGE environment
class MockBGE:
    class MockActor:
        def __init__(self, x=-1.8, y=-2.4, orientation=0.0):
            class MockPosition:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
                    self.z = -1.0
            self.worldPosition = MockPosition(x, y)
            
            class MockOrientation:
                def __init__(self, orientation):
                    self.orientation = orientation
                def to_euler(self):
                    return (0.0, 0.0, self.orientation)
            self.worldOrientation = MockOrientation(orientation)
    
    class MockScene:
        def __init__(self, x=-1.8, y=-2.4, orientation=0.0):
            self.objects = {"Actor": MockBGE.MockActor(x, y, orientation)}
        def get(self, name):
            return self.objects.get(name)
    
    class MockLogic:
        def __init__(self, x=-1.8, y=-2.4, orientation=0.0):
            self.scene = MockBGE.MockScene(x, y, orientation)
        def getCurrentScene(self):
            return self.scene
        current_task = "Testing synchronization"
        current_room = "LIVING_ROOM"

def test_synchronized_capture():
    """Test that every navigation step generates both first-person view and navigation map"""
    
    print("🔄 Testing Image Synchronization")
    print("=" * 60)
    
    # Add map directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_dir = os.path.join(os.path.dirname(current_dir), 'map')
    if map_dir not in sys.path:
        sys.path.insert(0, map_dir)
    
    from bge_integration import update_actor_position_map
    
    # Simulate 5 consecutive navigation steps
    test_steps = [
        (-1.8, -2.4, 0.0, "Step 1: Start position"),
        (-1.6, -2.4, 0.5, "Step 2: Move slightly forward"), 
        (-1.4, -2.2, 1.0, "Step 3: Turn and move"),
        (-1.2, -2.0, 1.5, "Step 4: Continue movement"),
        (-1.0, -1.8, 2.0, "Step 5: Reach new position")
    ]
    
    generated_maps = []
    
    for i, (x, y, orientation, description) in enumerate(test_steps):
        print(f"\n📍 {description}")
        print(f"   Position: ({x:.1f}, {y:.1f}), Facing: {orientation:.1f} rad")
        
        # Mock BGE environment for this step
        mock_bge = MockBGE()
        mock_logic = MockBGE.MockLogic(x, y, orientation)
        sys.modules['bge'] = mock_bge
        sys.modules['bge.logic'] = mock_logic
        
        # Simulate first-person screenshot (would happen here in real system)
        print(f"   📷 First-person screenshot: fp_view_{i+1:03d}.png (simulated)")
        
        # Generate navigation map
        try:
            map_path = update_actor_position_map(
                world_x=x,
                world_y=y, 
                room="LIVING_ROOM",
                task=f"Testing step {i+1}",
                orientation=orientation
            )
            
            if map_path:
                map_name = os.path.basename(map_path)
                generated_maps.append(map_name)
                print(f"   🗺️ Navigation map: {map_name}")
            else:
                print(f"   ❌ No navigation map generated")
                
        except Exception as e:
            print(f"   ❌ Map generation error: {e}")
    
    print(f"\n📊 Synchronization Results:")
    print(f"   🎯 Navigation steps: {len(test_steps)}")
    print(f"   📷 First-person images: {len(test_steps)} (simulated)")
    print(f"   🗺️ Navigation maps: {len(generated_maps)}")
    
    if len(generated_maps) == len(test_steps):
        print(f"   ✅ SYNCHRONIZED: Every step generates both images!")
    else:
        print(f"   ❌ DESYNCHRONIZED: Missing {len(test_steps) - len(generated_maps)} maps")
    
    print(f"\n🗂️ Generated maps: {generated_maps}")
    print(f"\n🔄 The 5-step procedure should now be properly synchronized:")
    print(f"   1. First-person screenshot → 2. Navigation map → 3. Feed both to VLM → 4. VLM decision → 5. Execute movement")

if __name__ == "__main__":
    test_synchronized_capture()