#!/usr/bin/env python3
"""
BGE Logic Setup Script for VESPER Navigation

This script automatically sets up the BGE Logic Bricks needed for navigation.
Run this in Blender's Text Editor BEFORE starting the game engine (pressing P).
"""

import bpy
import bmesh

def setup_bge_logic_for_navigation():
    """Set up BGE Logic Bricks for VESPER navigation system"""
    
    print("🔧 Setting up BGE Logic for VESPER Navigation...")
    
    scene = bpy.context.scene
    
    # First, make sure we have an Actor object
    actor = None
    
    # Look for existing Actor
    if "Actor" in bpy.data.objects:
        actor = bpy.data.objects["Actor"]
        print(f"✅ Found existing Actor: {actor.name}")
        print(f"📐 Actor shape: {actor.type} with {len(actor.data.vertices) if hasattr(actor.data, 'vertices') else 'N/A'} vertices")
    else:
        # Look for suitable objects to use as Actor (prioritize character-like objects)
        suitable_objects = []
        character_objects = []
        
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                not obj.name.lower().startswith(('camera', 'light', 'lamp', 'floor', 'wall', 'ceiling'))):
                suitable_objects.append(obj)
                
                # Prioritize character-like objects
                if any(keyword in obj.name.lower() for keyword in ['character', 'player', 'human', 'person', 'suzanne', 'monkey']):
                    character_objects.append(obj)
        
        # Use character object if available, otherwise use first suitable object
        if character_objects:
            actor = character_objects[0]
            old_name = actor.name
            actor.name = "Actor"
            print(f"✅ Renamed character '{old_name}' to 'Actor' for navigation")
            print(f"📐 Preserved character shape: {actor.type}")
        elif suitable_objects:
            # Use the first suitable object and rename it to Actor
            actor = suitable_objects[0]
            old_name = actor.name
            actor.name = "Actor"
            print(f"✅ Renamed '{old_name}' to 'Actor' for navigation")
            print(f"📐 Preserved shape: {actor.type}")
        else:
            # Create a character-like object instead of a cube
            print(f"🎭 No suitable actor found - creating Suzanne (monkey head) as Actor")
            bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1))
            actor = bpy.context.active_object
            actor.name = "Actor"
            print(f"✅ Created new Actor with character-like shape (Suzanne)")
    
    # Make sure we have a camera for screenshots
    camera = None
    if "BirdEyeCamera" in bpy.data.objects:
        camera = bpy.data.objects["BirdEyeCamera"]
        print(f"✅ Found existing BirdEyeCamera: {camera.name}")
    else:
        # Look for any camera to rename
        cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
        if cameras:
            camera = cameras[0]
            old_name = camera.name
            camera.name = "BirdEyeCamera"
            print(f"✅ Renamed camera '{old_name}' to 'BirdEyeCamera'")
        else:
            # Create a new camera positioned above the scene
            bpy.ops.object.camera_add(location=(0, 0, 10))
            camera = bpy.context.active_object
            camera.name = "BirdEyeCamera"
            # Point camera downward
            camera.rotation_euler = (0, 0, 0)  # Adjust as needed
            print(f"✅ Created new BirdEyeCamera above scene")
    
    # Select the actor for logic setup
    bpy.context.view_layer.objects.active = actor
    actor.select_set(True)
    
    # Clear existing game properties and logic
    actor.game.properties.clear()
    actor.game.sensors.clear()
    actor.game.controllers.clear()
    actor.game.actuators.clear()
    
    # Add an Always sensor
    bpy.ops.logic.sensor_add(type='ALWAYS', name='AlwaysSensor')
    always_sensor = actor.game.sensors[-1]
    always_sensor.use_pulse_true_level = True
    always_sensor.frequency = 60  # Run every frame
    
    # Add a Python controller
    bpy.ops.logic.controller_add(type='PYTHON', name='NavigationController')
    python_controller = actor.game.controllers[-1]
    
    # Check if navigation script is loaded in Text Editor
    nav_script = None
    for text in bpy.data.texts:
        if 'llm_bge_navigation' in text.name:
            nav_script = text
            break
    
    if nav_script:
        python_controller.text = nav_script
        print(f"✅ Connected navigation script: {nav_script.name}")
    else:
        print(f"⚠️ Navigation script not found in Text Editor!")
        print(f"💡 Load 'llm_bge_navigation.py' in Text Editor first")
        return False
    
    # Link sensor to controller
    always_sensor.link(python_controller)
    
    # Set actor as physics object for movement
    actor.game.physics_type = 'DYNAMIC'
    actor.game.use_collision_bounds = True
    actor.game.collision_bounds_type = 'BOX'
    
    # Store original position to preserve it
    original_location = actor.location.copy()
    
    print(f"✅ BGE Logic setup complete!")
    print(f"📍 Actor: {actor.name} at [{original_location.x:.1f}, {original_location.y:.1f}, {original_location.z:.1f}] (position preserved)")
    print(f"📹 Camera: {camera.name} at [{camera.location.x:.1f}, {camera.location.y:.1f}, {camera.location.z:.1f}]")
    print(f"\n🎮 Ready to start BGE:")
    print(f"   1. Press P to start game engine")
    print(f"   2. Actor will start at current position")
    print(f"   3. Check console for navigation messages")
    print(f"   4. Actor should begin navigation from where you placed it")
    
    return True

def verify_setup():
    """Verify that everything is set up correctly"""
    
    print(f"\n🔍 Verifying BGE Setup...")
    
    # Check for Actor
    if "Actor" not in bpy.data.objects:
        print(f"❌ No 'Actor' object found")
        return False
    
    actor = bpy.data.objects["Actor"]
    
    # Check for BirdEyeCamera
    if "BirdEyeCamera" not in bpy.data.objects:
        print(f"❌ No 'BirdEyeCamera' found")
        return False
    
    # Check for navigation script
    nav_script_found = False
    for text in bpy.data.texts:
        if 'llm_bge_navigation' in text.name:
            nav_script_found = True
            break
    
    if not nav_script_found:
        print(f"❌ Navigation script not loaded in Text Editor")
        return False
    
    # Check logic bricks
    if len(actor.game.sensors) == 0:
        print(f"❌ No sensors found on Actor")
        return False
    
    if len(actor.game.controllers) == 0:
        print(f"❌ No controllers found on Actor")
        return False
    
    print(f"✅ All components verified!")
    print(f"✅ Ready to press P and start navigation")
    
    return True

def create_simple_test_scene():
    """Create a simple test scene if the scene is empty"""
    
    if len([obj for obj in bpy.data.objects if obj.type == 'MESH']) < 2:
        print(f"🏗️ Creating simple test scene...")
        
        # Add a floor
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        floor = bpy.context.active_object
        floor.name = "Floor"
        
        # Add some walls to make it interesting
        bpy.ops.mesh.primitive_cube_add(size=2, location=(5, 0, 1))
        wall1 = bpy.context.active_object
        wall1.name = "Wall1"
        
        bpy.ops.mesh.primitive_cube_add(size=2, location=(-5, 0, 1))
        wall2 = bpy.context.active_object
        wall2.name = "Wall2"
        
        print(f"✅ Created simple test scene with floor and walls")

if __name__ == "__main__":
    print(f"🚀 VESPER BGE Logic Setup Starting...")
    print(f"="*50)
    
    # Create test scene if needed
    create_simple_test_scene()
    
    # Setup BGE logic
    success = setup_bge_logic_for_navigation()
    
    if success:
        # Verify setup
        verify_setup()
        
        print(f"\n" + "="*50)
        print(f"🎯 Setup Complete! Next Steps:")
        print(f"   1. Make sure 'llm_bge_navigation.py' is loaded in Text Editor")
        print(f"   2. Press P to start BGE")
        print(f"   3. Watch console for navigation messages")
        print(f"   4. Actor should start moving automatically")
        print(f"\n💡 If navigation doesn't start:")
        print(f"   - Check console for error messages")
        print(f"   - Verify VLM server is running")
        print(f"   - Make sure Logic Bricks are connected")
    else:
        print(f"\n❌ Setup failed - check the issues above")
