# Direct Detection Area Test - Run this in Blender Console/Scripting
# This will create a single detection area to test if the system works

import bpy
import bmesh
import math
from mathutils import Vector

def create_test_detection_area():
    """Create a simple test detection area"""
    
    # Clear any existing test objects
    for obj in bpy.data.objects:
        if "test_detection" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Detection area specifications
    sensor_id = "TEST_SENSOR"
    position = Vector((0, 0, 2.0))  # At origin, 2m high
    orientation = 0.0  # North facing
    detection_range = 5.0  # 5 meters
    fov_angle = 120.0     # 120 degrees
    
    print(f"🎯 Creating test detection area...")
    print(f"   📍 Position: {position}")
    print(f"   🧭 Orientation: {orientation}°")
    print(f"   📏 Range: {detection_range}m")
    print(f"   📐 FOV: {fov_angle}°")
    
    try:
        # Create mesh data
        mesh = bpy.data.meshes.new(f"{sensor_id}_test_detection_area")
        bm = bmesh.new()
        
        # Convert orientation to radians
        orientation_rad = math.radians(orientation)
        half_fov_rad = math.radians(fov_angle / 2)
        
        # Create triangular detection area vertices
        # Center point (sensor position)
        center = (0, 0, 0)
        
        # Left edge of detection cone
        left_x = detection_range * math.sin(orientation_rad - half_fov_rad)
        left_y = detection_range * math.cos(orientation_rad - half_fov_rad)
        left_point = (left_x, left_y, 0)
        
        # Right edge of detection cone  
        right_x = detection_range * math.sin(orientation_rad + half_fov_rad)
        right_y = detection_range * math.cos(orientation_rad + half_fov_rad)
        right_point = (right_x, right_y, 0)
        
        print(f"   📐 Triangle vertices:")
        print(f"      Center: {center}")
        print(f"      Left: {left_point}")
        print(f"      Right: {right_point}")
        
        # Add vertices to bmesh
        v_center = bm.verts.new(center)
        v_left = bm.verts.new(left_point)
        v_right = bm.verts.new(right_point)
        
        # Create triangle face
        bm.faces.new([v_center, v_left, v_right])
        
        # Create edges for wireframe visibility
        bm.edges.new([v_center, v_left])
        bm.edges.new([v_center, v_right])
        bm.edges.new([v_left, v_right])
        
        # Update mesh
        bm.to_mesh(mesh)
        bm.free()
        
        # Create object
        detection_obj = bpy.data.objects.new(f"{sensor_id}_test_detection_area", mesh)
        detection_obj.location = position
        
        # Add to scene
        bpy.context.collection.objects.link(detection_obj)
        
        # Create blue wireframe material
        material = bpy.data.materials.new(f"{sensor_id}_test_detection_material")
        material.use_nodes = True
        material.blend_method = 'ALPHA'
        
        # Set material properties for blue wireframe
        bsdf = material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.2, 0.6, 1.0, 1.0)  # Bright blue
        bsdf.inputs["Alpha"].default_value = 0.8  # More visible
        
        # Apply material
        detection_obj.data.materials.append(material)
        
        # Set display properties
        detection_obj.display_type = 'WIRE'  # Wireframe display
        detection_obj.hide_render = True     # Hide from renders
        detection_obj.show_in_front = True   # Show through other objects
        
        # Make it more visible
        detection_obj.color = (0.2, 0.6, 1.0, 1.0)  # Blue color
        
        # Add custom properties
        detection_obj["vesper_detection_area"] = True
        detection_obj["sensor_id"] = sensor_id
        detection_obj["detection_range"] = detection_range
        detection_obj["fov_angle"] = fov_angle
        
        # Select the object so you can see it
        bpy.context.view_layer.objects.active = detection_obj
        detection_obj.select_set(True)
        
        print(f"✅ Test detection area created successfully!")
        print(f"   📦 Object name: {detection_obj.name}")
        print(f"   📍 Location: {detection_obj.location}")
        print(f"   🎨 Material: {material.name}")
        print(f"   👁️ Display type: {detection_obj.display_type}")
        print(f"\n🔍 Look for a BLUE TRIANGLE in your 3D viewport!")
        print(f"   • The triangle should extend from origin towards +Y axis")
        print(f"   • Triangle apex at (0,0,2) - the sensor position")
        print(f"   • Two sides extending 5 meters with 120° spread")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test detection area: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_viewport_settings():
    """Check viewport settings that might hide the detection area"""
    print("\n🔍 Checking viewport settings...")
    
    # Get active viewport
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    print(f"   📺 Viewport shading: {space.shading.type}")
                    print(f"   🔲 Show wireframes: {space.overlay.show_wireframes}")
                    print(f"   👁️ Show overlays: {space.overlay.show_overlays}")
                    
                    # Enable wireframe overlay if not enabled
                    if not space.overlay.show_wireframes:
                        space.overlay.show_wireframes = True
                        print("   ✅ Enabled wireframe overlay")
                    
                    if not space.overlay.show_overlays:
                        space.overlay.show_overlays = True
                        print("   ✅ Enabled overlays")

def clear_test_objects():
    """Clear any test detection areas"""
    cleared = 0
    for obj in bpy.data.objects:
        if "test_detection" in obj.name:
            bpy.data.objects.remove(obj, do_unlink=True)
            cleared += 1
    print(f"🧹 Cleared {cleared} test objects")

# Run the test
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 DETECTION AREA DIRECT TEST")
    print("=" * 60)
    
    # Clear any existing test objects
    clear_test_objects()
    
    # Check viewport settings
    test_viewport_settings()
    
    # Create test detection area
    success = create_test_detection_area()
    
    if success:
        print("\n🎉 Test completed! You should see a BLUE TRIANGLE in 3D viewport")
        print("\n📋 If you don't see it, try:")
        print("   1. Switch viewport shading to 'Wireframe' or 'Solid'")
        print("   2. Enable overlays (toggle with Alt+Shift+Z)")
        print("   3. Check if object is selected in outliner")
        print("   4. Zoom out to see the 5-meter triangle")
    else:
        print("\n❌ Test failed - check console for errors")

# You can also run individual functions:
# clear_test_objects()
# create_test_detection_area()
# test_viewport_settings()
