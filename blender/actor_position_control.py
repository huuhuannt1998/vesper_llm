#!/usr/bin/env python3
"""
Actor Position Control Utility for VESPER Navigation

This script helps you control where the Actor starts when you press P in BGE.
Use this to set specific starting positions or preserve current positions.
"""

import bpy

def save_actor_position():
    """Save the current Actor position as the preferred starting position"""
    
    if "Actor" not in bpy.data.objects:
        print("❌ No 'Actor' object found")
        return None
    
    actor = bpy.data.objects["Actor"]
    position = [actor.location.x, actor.location.y, actor.location.z]
    
    # Store position in scene custom properties
    scene = bpy.context.scene
    scene["vesper_actor_start_x"] = position[0]
    scene["vesper_actor_start_y"] = position[1] 
    scene["vesper_actor_start_z"] = position[2]
    
    print(f"✅ Saved Actor starting position: [{position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}]")
    print(f"💡 Actor will start at this position when you press P")
    
    return position

def load_actor_position():
    """Load and apply the saved Actor starting position"""
    
    if "Actor" not in bpy.data.objects:
        print("❌ No 'Actor' object found")
        return False
    
    scene = bpy.context.scene
    
    # Check if saved position exists
    if ("vesper_actor_start_x" in scene and 
        "vesper_actor_start_y" in scene and 
        "vesper_actor_start_z" in scene):
        
        actor = bpy.data.objects["Actor"]
        saved_pos = [
            scene["vesper_actor_start_x"],
            scene["vesper_actor_start_y"], 
            scene["vesper_actor_start_z"]
        ]
        
        actor.location = saved_pos
        print(f"✅ Restored Actor to saved position: [{saved_pos[0]:.2f}, {saved_pos[1]:.2f}, {saved_pos[2]:.2f}]")
        return True
    else:
        print("⚠️ No saved Actor position found")
        return False

def set_actor_position(x, y, z=None):
    """Set Actor to specific coordinates"""
    
    if "Actor" not in bpy.data.objects:
        print("❌ No 'Actor' object found")
        return False
    
    actor = bpy.data.objects["Actor"]
    
    if z is None:
        z = actor.location.z  # Keep current Z position
    
    actor.location = (x, y, z)
    print(f"✅ Set Actor position to: [{x:.2f}, {y:.2f}, {z:.2f}]")
    
    # Also save this as the preferred starting position
    save_actor_position()
    
    return True

def get_scene_center():
    """Calculate the center of the scene based on mesh objects"""
    
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name != "Actor"]
    
    if not mesh_objects:
        print("⚠️ No mesh objects found to calculate scene center")
        return (0, 0, 0)
    
    # Calculate bounding box of all mesh objects
    min_x = min(obj.location.x for obj in mesh_objects)
    max_x = max(obj.location.x for obj in mesh_objects)
    min_y = min(obj.location.y for obj in mesh_objects)
    max_y = max(obj.location.y for obj in mesh_objects)
    min_z = min(obj.location.z for obj in mesh_objects)
    max_z = max(obj.location.z for obj in mesh_objects)
    
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2
    
    print(f"📐 Scene bounds:")
    print(f"   X: {min_x:.1f} to {max_x:.1f}")
    print(f"   Y: {min_y:.1f} to {max_y:.1f}")
    print(f"   Z: {min_z:.1f} to {max_z:.1f}")
    print(f"📍 Scene center: [{center_x:.1f}, {center_y:.1f}, {center_z:.1f}]")
    
    return (center_x, center_y, center_z)

def move_actor_to_center():
    """Move Actor to the center of the scene"""
    
    center = get_scene_center()
    # Place actor slightly above ground level
    set_actor_position(center[0], center[1], center[2] + 1)

def move_actor_to_corner():
    """Move Actor to a corner of the scene (good starting position)"""
    
    mesh_objects = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.name != "Actor"]
    
    if not mesh_objects:
        print("⚠️ No mesh objects found")
        return
    
    # Find corner position (min X, min Y)
    min_x = min(obj.location.x for obj in mesh_objects)
    min_y = min(obj.location.y for obj in mesh_objects)
    
    # Move actor to corner with some offset to avoid walls
    corner_x = min_x + 2
    corner_y = min_y + 2
    
    set_actor_position(corner_x, corner_y, 1)
    print(f"📍 Moved Actor to corner position")

def show_current_position():
    """Display current Actor position"""
    
    if "Actor" not in bpy.data.objects:
        print("❌ No 'Actor' object found")
        return
    
    actor = bpy.data.objects["Actor"]
    pos = actor.location
    
    print(f"📍 Current Actor position: [{pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}]")
    
    # Check if there's a saved position
    scene = bpy.context.scene
    if "vesper_actor_start_x" in scene:
        saved_pos = [
            scene["vesper_actor_start_x"],
            scene["vesper_actor_start_y"],
            scene["vesper_actor_start_z"]
        ]
        print(f"💾 Saved starting position: [{saved_pos[0]:.2f}, {saved_pos[1]:.2f}, {saved_pos[2]:.2f}]")
        
        # Check if current position matches saved position
        if (abs(pos.x - saved_pos[0]) < 0.1 and 
            abs(pos.y - saved_pos[1]) < 0.1 and 
            abs(pos.z - saved_pos[2]) < 0.1):
            print("✅ Current position matches saved starting position")
        else:
            print("⚠️ Current position differs from saved starting position")
    else:
        print("⚠️ No saved starting position found")

def disable_auto_positioning():
    """Disable automatic actor repositioning in navigation script"""
    
    scene = bpy.context.scene
    scene["vesper_disable_auto_position"] = True
    print("✅ Disabled automatic actor repositioning")
    print("💡 Actor will stay exactly where you place it when you press P")

def enable_auto_positioning():
    """Enable automatic actor repositioning in navigation script"""
    
    scene = bpy.context.scene
    if "vesper_disable_auto_position" in scene:
        del scene["vesper_disable_auto_position"]
    print("✅ Enabled automatic actor repositioning") 
    print("💡 Actor may be moved to scene center if at origin or outside bounds")

def setup_position_control():
    """Quick setup for position control"""
    
    print("🎯 Actor Position Control Setup")
    print("="*35)
    
    show_current_position()
    
    print(f"\n📋 Available Commands:")
    print(f"   save_actor_position() - Save current position as starting point")
    print(f"   load_actor_position() - Restore saved position")
    print(f"   set_actor_position(x, y, z) - Set specific coordinates")
    print(f"   move_actor_to_center() - Move to scene center")
    print(f"   move_actor_to_corner() - Move to scene corner")
    print(f"   disable_auto_positioning() - Prevent automatic repositioning")
    print(f"   enable_auto_positioning() - Allow automatic repositioning")
    
    print(f"\n💡 Recommendation:")
    print(f"   1. Position Actor where you want it to start")
    print(f"   2. Run save_actor_position()")
    print(f"   3. Run disable_auto_positioning() if needed")
    print(f"   4. Press P - Actor starts at your chosen position")

if __name__ == "__main__":
    setup_position_control()
