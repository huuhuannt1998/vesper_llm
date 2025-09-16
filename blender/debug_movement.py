"""
Actor Movement Debugging Script
==============================

This script helps debug why the actor is getting stuck at boundaries
and provides movement testing capabilities.
"""

import bge

def debug_actor_position():
    """Debug current actor position and movement constraints"""
    
    print("🔍 ACTOR POSITION DEBUG")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if not actor:
            print("❌ Actor not found")
            return
        
        pos = actor.worldPosition
        orient = actor.worldOrientation
        
        print(f"📍 Actor position: [{pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}]")
        print(f"🧭 Actor orientation: {orient}")
        
        # Check if actor has physics constraints
        if hasattr(actor, 'physics'):
            print(f"⚙️ Physics type: {actor.physics.type}")
        
        # Check for movement boundaries
        print("\n🚧 BOUNDARY CHECKS:")
        
        # Test small movements in each direction
        test_positions = {
            "NORTH": (pos.x, pos.y + 0.1, pos.z),
            "SOUTH": (pos.x, pos.y - 0.1, pos.z), 
            "EAST": (pos.x + 0.1, pos.y, pos.z),
            "WEST": (pos.x - 0.1, pos.y, pos.z)
        }
        
        for direction, test_pos in test_positions.items():
            # Basic boundary check (adjust these based on your house layout)
            x, y, z = test_pos
            
            # Assume house boundaries (adjust based on your layout)
            in_bounds = (-10 <= x <= 10) and (-5 <= y <= 8) and (-2 <= z <= 3)
            
            print(f"   {direction}: [{x:.2f}, {y:.2f}, {z:.2f}] → {'✅ OK' if in_bounds else '❌ OUT OF BOUNDS'}")
        
        # Check room detection
        print(f"\n🏠 ROOM DETECTION:")
        x, y = pos.x, pos.y
        
        # Based on the reference layout from images
        if x < -2.0 and y > 1.0:
            room = "kitchen"
        elif x > -1.0 and y > 1.0:
            room = "dining_room" 
        elif x < 0 and y < 1.0:
            room = "living_room"
        elif x > 0 and y < 1.0:
            room = "bedroom"
        else:
            room = "hallway/unknown"
        
        print(f"   Detected room: {room}")
        
        # Check distance to room centers (based on discovered layout)
        room_centers = {
            "living_room": (-1.0, -1.0),
            "kitchen": (5.0, 1.0), 
            "dining_room": (1.0, 4.0),
            "bedroom": (-4.0, 4.0),
            "bathroom": (6.0, 6.0),
            "hallway": (0.0, 1.0)
        }
        
        print(f"\n📏 DISTANCES TO ROOM CENTERS:")
        for room_name, (cx, cy) in room_centers.items():
            distance = ((pos.x - cx)**2 + (pos.y - cy)**2)**0.5
            print(f"   {room_name}: {distance:.2f} units")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def test_manual_movement():
    """Test manual movement in small increments"""
    
    print("\n🎮 MANUAL MOVEMENT TEST")
    print("=" * 25)
    
    try:
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if not actor:
            print("❌ Actor not found")
            return
        
        original_pos = actor.worldPosition.copy()
        print(f"📍 Starting position: [{original_pos.x:.3f}, {original_pos.y:.3f}, {original_pos.z:.3f}]")
        
        # Test small movements
        movements = [
            ("NORTH", (0, 0.1, 0)),
            ("SOUTH", (0, -0.1, 0)),
            ("EAST", (0.1, 0, 0)),
            ("WEST", (-0.1, 0, 0))
        ]
        
        for direction, (dx, dy, dz) in movements:
            print(f"\n🧪 Testing {direction} movement...")
            
            # Try to move
            new_pos = [original_pos.x + dx, original_pos.y + dy, original_pos.z + dz]
            
            try:
                # Attempt to move actor
                actor.worldPosition = new_pos
                
                # Check if movement succeeded
                actual_pos = actor.worldPosition
                moved = abs(actual_pos.x - original_pos.x) > 0.01 or abs(actual_pos.y - original_pos.y) > 0.01
                
                if moved:
                    print(f"   ✅ {direction}: Moved to [{actual_pos.x:.3f}, {actual_pos.y:.3f}, {actual_pos.z:.3f}]")
                    # Restore original position
                    actor.worldPosition = original_pos
                else:
                    print(f"   ❌ {direction}: Movement blocked or ineffective")
                    
            except Exception as e:
                print(f"   ❌ {direction}: Error - {e}")
        
        print(f"\n🔄 Actor restored to original position: [{original_pos.x:.3f}, {original_pos.y:.3f}, {original_pos.z:.3f}]")
        
    except Exception as e:
        print(f"❌ Movement test failed: {e}")
        import traceback
        traceback.print_exc()

def check_scene_objects():
    """Check scene objects that might be causing boundaries"""
    
    print("\n🔍 SCENE OBJECTS ANALYSIS")
    print("=" * 30)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Look for boundary or collision objects
        boundary_objects = []
        for obj in scene.objects:
            name_lower = obj.name.lower()
            if any(keyword in name_lower for keyword in ['boundary', 'wall', 'collision', 'barrier', 'limit']):
                boundary_objects.append(obj)
        
        if boundary_objects:
            print("🚧 Found potential boundary objects:")
            for obj in boundary_objects:
                pos = obj.worldPosition
                print(f"   {obj.name}: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
        else:
            print("🚧 No obvious boundary objects found")
        
        # Check for physics world constraints
        print(f"\n⚙️ PHYSICS WORLD INFO:")
        if hasattr(bge.logic, 'getPhysicsEnvironment'):
            physics_env = bge.logic.getPhysicsEnvironment()
            if physics_env:
                print("   Physics environment active")
            else:
                print("   No physics environment")
        else:
            print("   Physics environment check not available")
        
    except Exception as e:
        print(f"❌ Scene analysis failed: {e}")

def run_movement_debug():
    """Run complete movement debugging"""
    
    print("🔧 MOVEMENT DEBUGGING SUITE")
    print("=" * 35)
    
    debug_actor_position()
    test_manual_movement() 
    check_scene_objects()
    
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Check if actor is inside a physics boundary")
    print("   2. Verify room layout coordinates match actual scene")
    print("   3. Try increasing movement step size")
    print("   4. Check for invisible collision objects")

# Auto-run if executed directly
if __name__ == "__main__":
    run_movement_debug()

print("✅ Movement debug script loaded - call run_movement_debug() to execute")
