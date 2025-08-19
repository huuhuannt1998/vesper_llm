#!/usr/bin/env python3
"""
Actor Shape Preservation Utility for VESPER Navigation

This script helps preserve the Actor's appearance when working with different blend files.
It can copy actor properties and suggest how to maintain consistent character appearance.
"""

import bpy
import bmesh

def save_actor_template():
    """Save current Actor's properties as a template for other blend files"""
    
    if "Actor" not in bpy.data.objects:
        print("❌ No 'Actor' object found to save as template")
        return False
    
    actor = bpy.data.objects["Actor"]
    
    # Gather actor properties
    template = {
        "name": actor.name,
        "type": actor.type,
        "location": list(actor.location),
        "rotation": list(actor.rotation_euler),
        "scale": list(actor.scale),
        "mesh_name": actor.data.name if actor.data else None,
        "vertex_count": len(actor.data.vertices) if hasattr(actor.data, 'vertices') else 0,
        "material_count": len(actor.data.materials) if hasattr(actor.data, 'materials') else 0,
        "material_names": [mat.name for mat in actor.data.materials] if hasattr(actor.data, 'materials') else []
    }
    
    print(f"📋 Actor Template Saved:")
    print(f"   Name: {template['name']}")
    print(f"   Type: {template['type']}")
    print(f"   Mesh: {template['mesh_name']}")
    print(f"   Vertices: {template['vertex_count']}")
    print(f"   Materials: {template['material_names']}")
    print(f"   Location: [{template['location'][0]:.2f}, {template['location'][1]:.2f}, {template['location'][2]:.2f}]")
    
    # Save to file for reference
    import json
    import os
    
    script_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.path.dirname(__file__)
    template_file = os.path.join(script_dir, "actor_template.json")
    
    try:
        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)
        print(f"✅ Template saved to: {template_file}")
    except Exception as e:
        print(f"⚠️ Could not save template file: {e}")
    
    return template

def load_actor_template():
    """Load actor template from file"""
    
    import json
    import os
    
    script_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.path.dirname(__file__)
    template_file = os.path.join(script_dir, "actor_template.json")
    
    if not os.path.exists(template_file):
        print(f"⚠️ No actor template found at: {template_file}")
        return None
    
    try:
        with open(template_file, 'r') as f:
            template = json.load(f)
        print(f"✅ Loaded actor template: {template['mesh_name']} ({template['vertex_count']} vertices)")
        return template
    except Exception as e:
        print(f"❌ Could not load template: {e}")
        return None

def create_actor_from_template(template=None):
    """Create an Actor object based on template or create a character-like default"""
    
    if template is None:
        template = load_actor_template()
    
    # If we have a template, try to recreate similar object
    if template and template.get('mesh_name'):
        mesh_name = template['mesh_name']
        
        # Try to create similar object based on mesh name
        if 'suzanne' in mesh_name.lower() or 'monkey' in mesh_name.lower():
            print(f"🐵 Creating Suzanne (monkey head) Actor based on template")
            bpy.ops.mesh.primitive_monkey_add()
        elif 'cube' in mesh_name.lower():
            print(f"🟦 Creating Cube Actor based on template")
            bpy.ops.mesh.primitive_cube_add()
        elif 'sphere' in mesh_name.lower():
            print(f"🔮 Creating Sphere Actor based on template")
            bpy.ops.mesh.primitive_uv_sphere_add()
        elif 'cylinder' in mesh_name.lower():
            print(f"🥫 Creating Cylinder Actor based on template")
            bpy.ops.mesh.primitive_cylinder_add()
        else:
            print(f"🎭 Creating character-like Actor (Suzanne) as default")
            bpy.ops.mesh.primitive_monkey_add()
        
        # Set up the new actor
        actor = bpy.context.active_object
        actor.name = "Actor"
        
        # Apply template properties
        if template.get('location'):
            actor.location = template['location']
        if template.get('rotation'):
            actor.rotation_euler = template['rotation']
        if template.get('scale'):
            actor.scale = template['scale']
        
        print(f"✅ Created Actor from template with preserved shape")
        return actor
    
    else:
        # Create default character-like actor
        print(f"🎭 Creating default character Actor (Suzanne)")
        bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1))
        actor = bpy.context.active_object
        actor.name = "Actor"
        return actor

def apply_character_materials():
    """Apply character-like materials to the Actor"""
    
    if "Actor" not in bpy.data.objects:
        print("❌ No Actor found to apply materials")
        return
    
    actor = bpy.data.objects["Actor"]
    
    # Create a simple character material if none exists
    if not actor.data.materials:
        # Create new material
        mat = bpy.data.materials.new(name="ActorMaterial")
        mat.use_nodes = True
        
        # Set up basic character color
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs[0].default_value = (0.8, 0.6, 0.4, 1.0)  # Skin-like color
        bsdf.inputs[7].default_value = 0.2  # Roughness
        
        # Assign material to actor
        actor.data.materials.append(mat)
        print(f"✅ Applied character material to Actor")
    else:
        print(f"✅ Actor already has materials: {[mat.name for mat in actor.data.materials]}")

def setup_actor_with_preserved_shape():
    """Complete setup maintaining actor shape from previous sessions"""
    
    print(f"🎭 Setting up Actor with preserved shape...")
    
    # Check if Actor already exists
    if "Actor" in bpy.data.objects:
        actor = bpy.data.objects["Actor"]
        print(f"✅ Found existing Actor: {actor.name}")
        print(f"📐 Current shape: {actor.type}")
        if hasattr(actor.data, 'vertices'):
            print(f"📊 Vertices: {len(actor.data.vertices)}")
        return actor
    
    # Try to load template and create actor
    template = load_actor_template()
    
    if template:
        actor = create_actor_from_template(template)
    else:
        # Look for existing character-like objects in the scene
        character_objects = []
        for obj in bpy.data.objects:
            if (obj.type == 'MESH' and 
                any(keyword in obj.name.lower() for keyword in ['character', 'player', 'human', 'person', 'suzanne', 'monkey'])):
                character_objects.append(obj)
        
        if character_objects:
            # Rename existing character object
            actor = character_objects[0]
            old_name = actor.name
            actor.name = "Actor"
            print(f"✅ Renamed existing character '{old_name}' to 'Actor'")
        else:
            # Create new character-like actor
            actor = create_actor_from_template(None)
    
    # Apply materials
    apply_character_materials()
    
    # Save current setup as template for future use
    save_actor_template()
    
    print(f"✅ Actor setup complete with preserved character-like shape")
    return actor

def copy_actor_between_scenes():
    """Instructions for copying actor between blend files"""
    
    print(f"📋 How to Copy Actor Between Blend Files:")
    print(f"")
    print(f"Method 1 - Using Append:")
    print(f"  1. In new blend file: File → Append")
    print(f"  2. Navigate to your previous .blend file")
    print(f"  3. Go to Object → Select 'Actor'")
    print(f"  4. Click 'Append from Library'")
    print(f"  5. Run setup script to configure BGE logic")
    print(f"")
    print(f"Method 2 - Using Template System:")
    print(f"  1. In original file: Run save_actor_template()")
    print(f"  2. In new file: Run setup_actor_with_preserved_shape()")
    print(f"  3. Actor will be recreated with similar appearance")
    print(f"")
    print(f"Method 3 - Copy/Paste:")
    print(f"  1. Select Actor in original file")
    print(f"  2. Ctrl+C to copy")
    print(f"  3. Switch to new file")
    print(f"  4. Ctrl+V to paste")
    print(f"  5. Rename pasted object to 'Actor'")

if __name__ == "__main__":
    print(f"🎭 Actor Shape Preservation Utility")
    print(f"="*40)
    
    print(f"\n1. Save current Actor as template:")
    print(f"   save_actor_template()")
    
    print(f"\n2. Setup Actor with preserved shape:")
    print(f"   setup_actor_with_preserved_shape()")
    
    print(f"\n3. Get copy instructions:")
    print(f"   copy_actor_between_scenes()")
    
    # Automatically try to setup actor with preserved shape
    setup_actor_with_preserved_shape()
