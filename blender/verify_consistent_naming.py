#!/usr/bin/env python3
"""
Consistent Naming Verification Script for VESPER Navigation

This script verifies that the navigation system uses consistent naming:
- Actor object named "Actor"  
- Camera named "BirdEyeCamera"

Run this in Blender's Text Editor after importing a new glTF layout.
"""

import bpy

def verify_consistent_naming():
    """Verify that navigation objects use consistent naming"""
    
    print("🔍 Verifying Consistent Naming for VESPER Navigation...")
    print("="*55)
    
    scene = bpy.context.scene
    objects = scene.objects
    
    # Check for Actor
    actor_found = False
    actor_candidates = []
    
    for obj in objects:
        if obj.name == "Actor":
            actor_found = True
            print(f"✅ ACTOR: Found 'Actor' object at position [{obj.location.x:.2f}, {obj.location.y:.2f}, {obj.location.z:.2f}]")
            break
        elif obj.type == 'MESH' and any(keyword in obj.name.lower() for keyword in ['player', 'character', 'human', 'person', 'cube']):
            actor_candidates.append(obj.name)
    
    if not actor_found:
        if actor_candidates:
            print(f"⚠️ ACTOR: No 'Actor' object found, but candidates available: {actor_candidates}")
            print(f"💡 ACTOR: Run navigation script to auto-rename one of these to 'Actor'")
        else:
            print(f"❌ ACTOR: No suitable objects found for actor")
            print(f"💡 ACTOR: Add a movable object (cube, character, etc.) to the scene")
    
    # Check for BirdEyeCamera
    camera_found = False
    camera_candidates = []
    
    for obj in objects:
        if obj.name == "BirdEyeCamera":
            camera_found = True
            print(f"✅ CAMERA: Found 'BirdEyeCamera' at position [{obj.location.x:.2f}, {obj.location.y:.2f}, {obj.location.z:.2f}]")
            if obj.location.z > 5:  # Check if positioned above scene
                print(f"✅ CAMERA: Camera is positioned above scene (Z: {obj.location.z:.2f}) - good for bird's eye view")
            else:
                print(f"⚠️ CAMERA: Camera might be too low (Z: {obj.location.z:.2f}) - consider raising for better bird's eye view")
            break
        elif obj.type == 'CAMERA':
            camera_candidates.append(obj.name)
    
    if not camera_found:
        if camera_candidates:
            print(f"⚠️ CAMERA: No 'BirdEyeCamera' found, but cameras available: {camera_candidates}")
            print(f"💡 CAMERA: Run navigation script to auto-rename one to 'BirdEyeCamera'")
        else:
            print(f"❌ CAMERA: No cameras found in scene")
            print(f"💡 CAMERA: Add a camera positioned above the house for bird's eye screenshots")
    
    # Overall readiness check
    print(f"\n🎯 Navigation Readiness:")
    if actor_found and camera_found:
        print(f"  ✅ READY - Both 'Actor' and 'BirdEyeCamera' are properly named")
        print(f"  ✅ You can start navigation immediately")
    elif actor_found or camera_found:
        missing = []
        if not actor_found:
            missing.append("Actor")
        if not camera_found:
            missing.append("BirdEyeCamera")
        print(f"  ⚠️ PARTIAL - Missing: {', '.join(missing)}")
        print(f"  🔧 Run navigation script to auto-setup missing objects")
    else:
        print(f"  ❌ NOT READY - Both Actor and BirdEyeCamera need setup")
        print(f"  🔧 Run navigation script for automatic setup")
    
    # Layout information
    print(f"\n📊 Scene Information:")
    print(f"  Total objects: {len(objects)}")
    mesh_objects = [obj for obj in objects if obj.type == 'MESH']
    cameras = [obj for obj in objects if obj.type == 'CAMERA']
    print(f"  Mesh objects: {len(mesh_objects)}")
    print(f"  Cameras: {len(cameras)}")
    
    # Scene bounds for context
    if mesh_objects:
        min_x = min(obj.location.x for obj in mesh_objects)
        max_x = max(obj.location.x for obj in mesh_objects)
        min_y = min(obj.location.y for obj in mesh_objects)
        max_y = max(obj.location.y for obj in mesh_objects)
        
        width = max_x - min_x
        height = max_y - min_y
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        print(f"\n📐 Scene Layout:")
        print(f"  X range: {min_x:.1f} to {max_x:.1f} (width: {width:.1f})")
        print(f"  Y range: {min_y:.1f} to {max_y:.1f} (height: {height:.1f})")
        print(f"  Center: ({center_x:.1f}, {center_y:.1f})")
    
    print(f"\n💡 Next Steps:")
    print(f"  1. If setup needed: Run llm_bge_navigation.py (it will auto-rename objects)")
    print(f"  2. Verify console messages show 'Renamed X to Actor/BirdEyeCamera'")
    print(f"  3. Press P to start BGE and test navigation")
    print(f"  4. Objects will always be consistently named across different glTF layouts")

def check_naming_conflicts():
    """Check for potential naming conflicts"""
    
    print(f"\n🔍 Checking for Naming Conflicts...")
    
    scene = bpy.context.scene
    
    # Count objects with similar names
    actor_like = [obj.name for obj in scene.objects if 'actor' in obj.name.lower()]
    camera_like = [obj.name for obj in scene.objects if 'camera' in obj.name.lower() and obj.type == 'CAMERA']
    
    if len(actor_like) > 1:
        print(f"⚠️ Multiple actor-like objects found: {actor_like}")
        print(f"💡 Navigation will use/rename the first suitable one to 'Actor'")
    
    if len(camera_like) > 1:
        print(f"⚠️ Multiple cameras found: {camera_like}")
        print(f"💡 Navigation will use/rename the first one to 'BirdEyeCamera'")
    
    if len(actor_like) <= 1 and len(camera_like) <= 1:
        print(f"✅ No naming conflicts detected")

if __name__ == "__main__":
    verify_consistent_naming()
    check_naming_conflicts()
    
    print(f"\n" + "="*55)
    print(f"🏠 Consistent naming ensures easy testing across glTF layouts!")
    print(f"📋 Always: Actor = 'Actor', Camera = 'BirdEyeCamera'")
