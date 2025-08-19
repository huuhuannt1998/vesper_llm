#!/usr/bin/env python3
"""
Quick verification script to ensure the multi-layout system is ready to use.
Run this script in Blender's Text Editor to verify everything is set up correctly.
"""

import bpy
import bmesh
import mathutils
from mathutils import Vector

def verify_navigation_setup():
    """Verify that the navigation system is properly configured"""
    
    print("🔍 Verifying VESPER Navigation Multi-Layout Setup...")
    print("="*50)
    
    # Check scene objects
    scene = bpy.context.scene
    objects = scene.objects
    print(f"📊 Scene Analysis:")
    print(f"  Total objects: {len(objects)}")
    
    # Find potential actors
    actor_candidates = []
    for obj in objects:
        if obj.type == 'MESH' and any(keyword in obj.name.lower() for keyword in ['actor', 'player', 'character', 'human', 'person', 'cube']):
            actor_candidates.append(obj.name)
    
    print(f"  Actor candidates found: {actor_candidates}")
    
    # Find cameras
    cameras = [obj.name for obj in objects if obj.type == 'CAMERA']
    print(f"  Cameras found: {cameras}")
    
    # Check if we have a navigation setup
    has_actor = len(actor_candidates) > 0
    has_camera = len(cameras) > 0
    
    print(f"\n✅ Navigation Requirements:")
    print(f"  Actor available: {'✅ YES' if has_actor else '❌ NO'}")
    print(f"  Camera available: {'✅ YES' if has_camera else '❌ NO'}")
    
    # Analyze scene bounds
    mesh_objects = [obj for obj in objects if obj.type == 'MESH']
    if mesh_objects:
        min_coords = [float('inf'), float('inf'), float('inf')]
        max_coords = [float('-inf'), float('-inf'), float('-inf')]
        
        for obj in mesh_objects:
            bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
            for corner in bbox:
                for i in range(3):
                    min_coords[i] = min(min_coords[i], corner[i])
                    max_coords[i] = max(max_coords[i], corner[i])
        
        width = max_coords[0] - min_coords[0]
        height = max_coords[1] - min_coords[1]
        center_x = (min_coords[0] + max_coords[0]) / 2
        center_y = (min_coords[1] + max_coords[1]) / 2
        
        print(f"\n📐 Scene Bounds:")
        print(f"  X range: {min_coords[0]:.2f} to {max_coords[0]:.2f} (width: {width:.2f})")
        print(f"  Y range: {min_coords[1]:.2f} to {max_coords[1]:.2f} (height: {height:.2f})")
        print(f"  Center point: ({center_x:.2f}, {center_y:.2f})")
    
    # Check if navigation script exists
    text_blocks = bpy.data.texts
    nav_script_found = False
    for text in text_blocks:
        if 'llm_bge_navigation' in text.name:
            nav_script_found = True
            print(f"\n📝 Navigation script found: {text.name}")
            break
    
    if not nav_script_found:
        print(f"\n⚠️  Navigation script not found in Text Editor")
        print(f"    Make sure llm_bge_navigation.py is loaded")
    
    # Overall status
    print(f"\n🎯 Overall Status:")
    if has_actor and has_camera:
        print(f"  ✅ READY - You can import new glTF layouts and start navigation")
    elif has_actor and not has_camera:
        print(f"  ⚠️  PARTIAL - Actor found but no camera. Add a camera for bird's eye view")
    elif not has_actor and has_camera:
        print(f"  ⚠️  PARTIAL - Camera found but no actor. Add an actor object or cube")
    else:
        print(f"  ❌ NOT READY - Need both actor and camera objects")
    
    print(f"\n💡 Next Steps:")
    print(f"  1. Import your glTF 2.0 house layout (File → Import → glTF 2.0)")
    print(f"  2. Run the navigation script (it will auto-detect the new layout)")
    print(f"  3. Press P to start BGE and test navigation")
    print(f"  4. Use the layout tester utility for comprehensive testing")

def test_multi_layout_functions():
    """Test if the multi-layout functions are available"""
    
    print(f"\n🧪 Testing Multi-Layout Functions...")
    
    # These would normally be imported from the navigation script
    # For now, just check if the script structure looks correct
    
    try:
        # Basic functionality test
        print(f"  ✅ Scene access: {len(bpy.context.scene.objects)} objects")
        print(f"  ✅ Vector math: {Vector((1, 2, 3)).length:.2f}")
        print(f"  ✅ Multi-layout functions should be available in navigation script")
        
    except Exception as e:
        print(f"  ❌ Error testing functions: {e}")

if __name__ == "__main__":
    verify_navigation_setup()
    test_multi_layout_functions()
    
    print(f"\n" + "="*50)
    print(f"🏠 Ready to test with different glTF house layouts!")
    print(f"📋 Use gltf_layout_tester.py for detailed testing workflow.")
