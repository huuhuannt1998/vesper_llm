"""
Simple First-Person Camera Setup
================================

Creates a child camera object of the actor that mimics normal human view.
Simple and clean - no environment destruction!
"""

import bpy
from mathutils import Vector
from math import radians

def create_simple_first_person_camera(actor_name="Actor"):
    """
    Create a simple first-person camera as child of actor.
    
    Args:
        actor_name: Name of the actor object
    
    Returns:
        dict: Result with success status
    """
    print(f"👁️  Creating simple first-person camera for {actor_name}...")
    
    # Find the actor
    actor = bpy.data.objects.get(actor_name)
    if not actor:
        print(f"❌ Actor '{actor_name}' not found")
        return {"success": False, "error": f"Actor '{actor_name}' not found"}
    
    camera_name = f"{actor_name}_FPCamera"
    
    # Remove existing camera if it exists
    existing_camera = bpy.data.objects.get(camera_name)
    if existing_camera:
        print(f"🗑️  Removing existing camera: {camera_name}")
        bpy.data.objects.remove(existing_camera, do_unlink=True)
    
    # Create camera
    print("📷 Creating camera...")
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = camera_name
    
    # Set camera properties for natural view
    camera.data.lens = 30  # 50mm lens for natural perspective
    camera.data.clip_start = 0.01
    camera.data.clip_end = 1000.0
    
    # Make camera child of actor
    print("🔗 Making camera child of actor...")
    camera.parent = actor
    camera.parent_type = 'OBJECT'
    
    # Position camera at eye level (relative to actor)
    # Assuming actor is 1.8m tall, eyes at about 90% height = 1.62m
    # If actor origin is at center, eyes are 0.81m above center
    eye_height = 0.8  # Adjust this based on your actor's proportions
    forward_offset = 0.0  # No forward offset, camera at actor center
    
    camera.location = Vector((0, forward_offset, eye_height))
    
    # Point camera forward (assuming actor faces +Y direction)
    # Camera's -Z axis should point forward (+Y in world)
    camera.rotation_euler = (radians(90), 0, 0)  # Rotate 90° around X to point forward
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    print("✅ Simple first-person camera created!")
    print(f"   Camera: {camera_name}")
    print(f"   Parent: {actor_name}")
    print(f"   Local position: {camera.location}")
    print(f"   Rotation: {camera.rotation_euler}")
    
    return {
        "success": True,
        "camera": camera_name,
        "actor": actor_name,
        "message": "Simple first-person camera created as child of actor"
    }

def test_camera_movement(actor_name="Actor"):
    """Test that camera follows actor when actor moves."""
    print("\n🧪 Testing camera follows actor...")
    
    actor = bpy.data.objects.get(actor_name)
    camera = bpy.data.objects.get(f"{actor_name}_FPCamera")
    
    if not actor or not camera:
        print("❌ Actor or camera not found")
        return False
    
    # Test parent-child relationship
    if camera.parent == actor:
        print("✅ Camera is child of actor")
        print("   Move actor with G key - camera will follow automatically")
        return True
    else:
        print("❌ Camera is not child of actor")
        return False

# Simple usage functions
def setup_camera_for_actor(actor_name="Actor"):
    """Simple function to set up camera for any actor."""
    return create_simple_first_person_camera(actor_name)

def main():
    """Main function - creates simple first-person camera."""
    print("👁️  SIMPLE FIRST-PERSON CAMERA SETUP")
    print("=" * 40)
    
    # Set up camera for Actor
    result = create_simple_first_person_camera("Actor")
    
    if result["success"]:
        print(f"\n✅ SUCCESS: {result['message']}")
        
        # Test the setup
        test_camera_movement("Actor")
        
        print(f"\n🎮 HOW TO USE:")
        print(f"   1. Press Numpad 0 to switch to camera view")
        print(f"   2. Select Actor and press G to move")
        print(f"   3. Camera follows automatically!")
        print(f"   4. Rotate Actor with R key to change view direction")
        
    else:
        print(f"❌ Failed: {result['error']}")
        print("💡 Make sure you have an object named 'Actor' in your scene")

if __name__ == "__main__":
    main()
