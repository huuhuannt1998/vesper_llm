# Direct Debug Test - Create Sensor + Detection Area Step by Step
# Run this in Blender Console to debug the issue

import bpy
import bmesh
import math
from mathutils import Vector

def clear_test_objects():
    """Clear all test objects"""
    to_remove = []
    for obj in bpy.data.objects:
        if ("test" in obj.name.lower() or 
            "motion_" in obj.name.lower() or 
            "detectionarea_" in obj.name.lower()):
            to_remove.append(obj)
    
    for obj in to_remove:
        bpy.data.objects.remove(obj, do_unlink=True)
    print(f"🧹 Cleared {len(to_remove)} test objects")

def create_sensor_object(sensor_id, position):
    """Create the physical sensor object"""
    print(f"📍 Creating sensor object: {sensor_id}")
    
    # Create sensor as a small red sphere
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, location=position)
    sensor_obj = bpy.context.active_object
    sensor_obj.name = f"Motion_{sensor_id}"
    
    # Create red material for sensor
    mat = bpy.data.materials.new(name=f"Motion_Material_{sensor_id}")
    mat.use_nodes = True
    if mat.node_tree and mat.node_tree.nodes.get("Principled BSDF"):
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red
    sensor_obj.data.materials.append(mat)
    
    print(f"✅ Sensor object created: {sensor_obj.name} at {sensor_obj.location}")
    return sensor_obj

def create_detection_triangle_direct(sensor_id, position, orientation=0.0):
    """Create detection triangle directly without any dependencies"""
    print(f"🎯 Creating detection triangle for {sensor_id}")
    print(f"   📍 Position: {position}")
    print(f"   🧭 Orientation: {orientation}°")
    
    try:
        # Detection specifications
        detection_range = 5.0  # 5 meters
        fov_angle = 120.0     # 120 degrees
        
        # Create mesh
        mesh = bpy.data.meshes.new(f"DetectionTriangle_{sensor_id}")
        bm = bmesh.new()
        
        # Calculate triangle vertices
        orientation_rad = math.radians(orientation)
        half_fov_rad = math.radians(fov_angle / 2)
        
        # Apex at sensor (origin in local coordinates)
        apex = (0, 0, 0)
        
        # Left and right points of triangle base
        left_x = detection_range * math.sin(orientation_rad - half_fov_rad)
        left_y = detection_range * math.cos(orientation_rad - half_fov_rad)
        left_point = (left_x, left_y, 0)
        
        right_x = detection_range * math.sin(orientation_rad + half_fov_rad)
        right_y = detection_range * math.cos(orientation_rad + half_fov_rad)
        right_point = (right_x, right_y, 0)
        
        print(f"   📐 Triangle vertices:")
        print(f"      Apex: {apex}")
        print(f"      Left: {left_point}")
        print(f"      Right: {right_point}")
        
        # Create vertices
        v_apex = bm.verts.new(apex)
        v_left = bm.verts.new(left_point)
        v_right = bm.verts.new(right_point)
        
        # Create edges (wireframe)
        bm.edges.new([v_apex, v_left])
        bm.edges.new([v_apex, v_right])
        bm.edges.new([v_left, v_right])
        
        # Create face for visibility
        bm.faces.new([v_apex, v_left, v_right])
        
        # Update mesh
        bm.to_mesh(mesh)
        bm.free()
        
        # Create object
        detection_obj = bpy.data.objects.new(f"DetectionTriangle_{sensor_id}", mesh)
        detection_obj.location = position
        
        # Add to scene
        bpy.context.collection.objects.link(detection_obj)
        
        # Create very visible blue material
        material = bpy.data.materials.new(f"DetectionMaterial_{sensor_id}")
        material.use_nodes = True
        
        # Make it bright blue and visible
        if material.node_tree and material.node_tree.nodes.get("Principled BSDF"):
            bsdf = material.node_tree.nodes["Principled BSDF"]
            bsdf.inputs[0].default_value = (0.0, 0.5, 1.0, 1.0)  # Bright blue
            bsdf.inputs[21].default_value = 1.0  # Fully opaque
        
        detection_obj.data.materials.append(material)
        
        # Set display properties for maximum visibility
        detection_obj.display_type = 'SOLID'  # Try solid first instead of wireframe
        detection_obj.color = (0.0, 0.5, 1.0, 1.0)  # Bright blue
        detection_obj.show_in_front = True
        
        # Custom properties
        detection_obj["vesper_detection_area"] = True
        detection_obj["sensor_id"] = sensor_id
        
        print(f"✅ Detection triangle created: {detection_obj.name}")
        print(f"   📍 Location: {detection_obj.location}")
        print(f"   🎨 Material: Bright blue solid")
        print(f"   👁️ Display: Solid, show in front")
        
        return detection_obj
        
    except Exception as e:
        print(f"❌ Failed to create detection triangle: {e}")
        import traceback
        traceback.print_exc()
        return None

def parent_objects(sensor_obj, detection_obj):
    """Parent detection area to sensor"""
    if sensor_obj and detection_obj:
        print(f"🔗 Parenting {detection_obj.name} to {sensor_obj.name}")
        
        # Store current world position
        world_pos = detection_obj.matrix_world.translation.copy()
        
        # Set parent
        detection_obj.parent = sensor_obj
        detection_obj.parent_type = 'OBJECT'
        
        # Reset to local origin (centered on sensor)
        detection_obj.location = (0, 0, 0)
        
        print(f"✅ Parenting complete - detection area will move with sensor")
        return True
    return False

def test_step_by_step():
    """Test everything step by step"""
    print("=" * 60)
    print("🧪 STEP-BY-STEP DEBUG TEST")
    print("=" * 60)
    
    # Clear existing objects
    clear_test_objects()
    
    # Test parameters
    sensor_id = "DEBUG_TEST"
    position = Vector((0, 0, 2.0))
    orientation = 0.0  # North facing
    
    print(f"\n📍 Step 1: Creating sensor object")
    sensor_obj = create_sensor_object(sensor_id, position)
    
    if not sensor_obj:
        print("❌ Failed to create sensor object")
        return False
    
    print(f"\n🎯 Step 2: Creating detection triangle")
    detection_obj = create_detection_triangle_direct(sensor_id, position, orientation)
    
    if not detection_obj:
        print("❌ Failed to create detection triangle")
        return False
    
    print(f"\n🔗 Step 3: Parenting objects")
    parented = parent_objects(sensor_obj, detection_obj)
    
    if not parented:
        print("❌ Failed to parent objects")
        return False
    
    # Select both objects for visibility
    bpy.context.view_layer.objects.active = sensor_obj
    sensor_obj.select_set(True)
    detection_obj.select_set(True)
    
    print(f"\n✅ Test completed successfully!")
    print(f"\n🔍 You should see:")
    print(f"   • RED SPHERE at {position} (the sensor)")
    print(f"   • BLUE TRIANGLE extending north from sensor (detection area)")
    print(f"   • Triangle: 5m long, 120° wide")
    print(f"   • Both objects selected in outliner")
    
    print(f"\n🚀 Manual test:")
    print(f"   1. Press 'G' to move the red sensor sphere")
    print(f"   2. Blue triangle should move with it")
    print(f"   3. Press 'R' + 'Z' to rotate sensor")
    print(f"   4. Triangle should rotate too")
    
    return True

def check_viewport_settings():
    """Check if viewport settings might be hiding objects"""
    print("\n🔍 Checking viewport settings...")
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    print(f"   📺 Shading: {space.shading.type}")
                    print(f"   🔲 Wireframes: {space.overlay.show_wireframes}")
                    print(f"   👁️ Overlays: {space.overlay.show_overlays}")
                    
                    # Enable everything for visibility
                    space.overlay.show_wireframes = True
                    space.overlay.show_overlays = True
                    
                    if space.shading.type == 'RENDERED':
                        space.shading.type = 'SOLID'
                        print("   ✅ Changed from RENDERED to SOLID shading")

# Run the test
if __name__ == "__main__":
    check_viewport_settings()
    test_step_by_step()

print("\n💡 If you still don't see anything:")
print("   1. Try zooming out (scroll wheel)")
print("   2. Switch to wireframe view (Z key)")
print("   3. Check outliner for 'Motion_DEBUG_TEST' and 'DetectionTriangle_DEBUG_TEST'")
print("   4. Select objects in outliner to highlight them")
