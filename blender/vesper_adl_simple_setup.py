# -*- coding: utf-8 -*-
"""
VESPER ADL Simple Setup for Blender

Run this script in Blender's Scripting tab to setup VESPER ADL.
This prepares the system for Game Engine testing.
"""

import bpy
import sys
import os
from pathlib import Path

def setup_vesper_adl_simple():
    """Simple VESPER ADL setup in Blender"""
    
    print("Setting up VESPER ADL for Blender...")
    
    # Add VESPER ADL path
    vesper_path = r"C:\Users\hbui11\Desktop\vesper_llm\blender"
    if vesper_path not in sys.path:
        sys.path.append(vesper_path)
        print(f"Added path: {vesper_path}")
    
    # Create the BGE initialization script (without special characters)
    bge_init_script = '''
import bge
import sys
import os

# Add VESPER ADL path
vesper_path = r"C:\\Users\\hbui11\\Desktop\\vesper_llm\\blender"
if vesper_path not in sys.path:
    sys.path.append(vesper_path)

# Initialize VESPER ADL when BGE starts
try:
    from vesper_adl_game_engine_integration import VESPERADLGameEngineIntegration
    
    # Only initialize once
    if not hasattr(bge.logic, 'vesper_adl_initialized'):
        print("Initializing VESPER ADL in Game Engine...")
        
        # Create integration instance
        integration = VESPERADLGameEngineIntegration()
        success = integration.initialize_for_game_engine()
        
        if success:
            bge.logic.vesper_adl_initialized = True
            print("VESPER ADL ready in Game Engine!")
            print("Use F6-F9 keys for ADL testing")
        else:
            print("VESPER ADL initialization failed")
    
    # Handle keyboard input
    keyboard = bge.logic.getCurrentController().sensors.get('Keyboard')
    if keyboard and keyboard.positive:
        for key in keyboard.events:
            if keyboard.events[key] == bge.logic.KX_INPUT_JUST_ACTIVATED:
                
                if key == bge.events.F6KEY:
                    print("F6: Starting cooking task...")
                    if hasattr(bge.logic, 'queue_adl_cooking'):
                        bge.logic.queue_adl_cooking()
                
                elif key == bge.events.F7KEY:
                    print("F7: Starting medication task...")
                    if hasattr(bge.logic, 'queue_adl_medication'):
                        bge.logic.queue_adl_medication()
                
                elif key == bge.events.F8KEY:
                    print("F8: Starting communication task...")
                    if hasattr(bge.logic, 'queue_adl_communication'):
                        bge.logic.queue_adl_communication()
                
                elif key == bge.events.F9KEY:
                    print("F9: VESPER ADL status...")
                    if hasattr(bge.logic, 'get_vesper_adl_status'):
                        status = bge.logic.get_vesper_adl_status()
                        print(f"Status: {status}")

except Exception as e:
    print(f"VESPER ADL error: {e}")
'''
    
    # Create or update the BGE script
    script_name = "vesper_adl_bge_main"
    
    if script_name in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts[script_name])
    
    bge_script = bpy.data.texts.new(script_name)
    bge_script.write(bge_init_script)
    
    print(f"Created BGE script: '{script_name}'")
    
    # Setup Actor if needed
    setup_actor_simple()
    
    # Create CASAS test objects
    create_casas_objects_simple()
    
    print("")
    print("VESPER ADL Setup Complete!")
    print("Next Steps:")
    print("1. Press 'P' to start Game Engine")
    print("2. Wait for 'VESPER ADL ready in Game Engine!' message")
    print("3. Use F6-F9 keys to test ADL tasks")
    
    return True

def setup_actor_simple():
    """Setup Actor object if needed"""
    
    # Find Actor object
    actor = None
    for obj in bpy.data.objects:
        if obj.name == "Actor":
            actor = obj
            break
    
    if not actor:
        print("No Actor found, creating simple Actor cube...")
        
        # Create a simple actor
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
        actor = bpy.context.active_object
        actor.name = "Actor"
        
        # Make it blue for visibility
        mat = bpy.data.materials.new(name="Actor_mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.3, 1.0, 1.0)
        actor.data.materials.append(mat)
    
    print(f"Actor ready: {actor.name}")

def create_casas_objects_simple():
    """Create simple objects for CASAS ADL testing"""
    
    # CASAS objects for ADL tasks
    casas_objects = [
        ("oatmeal", (2, 1, 0.5), (0.8, 0.7, 0.5)),      # Kitchen - beige
        ("bowl", (1.8, 1, 0.5), (0.9, 0.9, 0.9)),       # Kitchen - white  
        ("medicine", (0, 2, 0.8), (1, 0.3, 0.3)),       # Bathroom - red
        ("phone_book", (-1, 1, 0.8), (1, 1, 0.3))       # Living room - yellow
    ]
    
    created_count = 0
    
    for obj_name, location, color in casas_objects:
        # Check if object already exists
        if obj_name in bpy.data.objects:
            print(f"CASAS object exists: {obj_name}")
            continue
        
        # Create simple cube
        bpy.ops.mesh.primitive_cube_add(location=location, scale=(0.15, 0.15, 0.15))
        cube = bpy.context.active_object
        cube.name = obj_name
        
        # Add material
        mat = bpy.data.materials.new(name=f"{obj_name}_mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*color, 1.0)
        cube.data.materials.append(mat)
        
        created_count += 1
        print(f"Created CASAS object: {obj_name}")
    
    print(f"CASAS objects ready: {created_count} created, {4-created_count} existing")

# Main execution
def main():
    """Main setup function"""
    
    print("VESPER ADL Blender Setup")
    print("=" * 30)
    
    try:
        # Run setup
        setup_success = setup_vesper_adl_simple()
        
        if setup_success:
            print("")
            print("=" * 40)
            print("   VESPER ADL Setup Complete!")
            print("   Press 'P' to test in Game Engine")
            print("=" * 40)
        else:
            print("Setup failed")
    
    except Exception as e:
        print(f"Setup error: {e}")
        print("Make sure you're running this in Blender")

if __name__ == "__main__":
    main()

# Auto-run when executed in Blender
main()
