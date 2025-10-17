"""
VESPER Interaction System - Object Discovery Tool
Automatically discovers objects in the Blender scene and creates appropriate configuration
"""

import bge
import json
import re
from pathlib import Path


def discover_scene_objects():
    """
    Discover all objects in the current Blender scene
    Returns dictionary of object names and their properties
    """
    scene = bge.logic.getCurrentScene()
    discovered_objects = {}
    
    for obj in scene.objects:
        name = obj.name
        position = (obj.worldPosition.x, obj.worldPosition.y, obj.worldPosition.z)
        
        discovered_objects[name] = {
            "name": name,
            "position": position,
            "has_mesh": hasattr(obj, 'meshes') and len(obj.meshes) > 0
        }
    
    return discovered_objects


def categorize_objects(objects_dict):
    """
    Categorize objects based on naming patterns
    Returns dict organized by room/category
    """
    categorized = {
        "kitchen": [],
        "dining": [],
        "bathroom": [],
        "bedroom": [],
        "living": [],
        "other": []
    }
    
    for name, info in objects_dict.items():
        name_lower = name.lower()
        
        # Skip cameras, lights, empties
        if any(skip in name_lower for skip in ['camera', 'light', 'empty', 'lamp', 'sun']):
            continue
        
        # Categorize by room keywords
        if any(kw in name_lower for kw in ['kitchen', 'sink', 'stove', 'fridge', 'microwave']):
            categorized["kitchen"].append(name)
        elif any(kw in name_lower for kw in ['dining', 'table', 'phone']):
            categorized["dining"].append(name)
        elif any(kw in name_lower for kw in ['bath', 'shower', 'toilet']):
            categorized["bathroom"].append(name)
        elif any(kw in name_lower for kw in ['bed', 'closet']):
            categorized["bedroom"].append(name)
        elif any(kw in name_lower for kw in ['living', 'couch', 'sofa', 'tv']):
            categorized["living"].append(name)
        else:
            categorized["other"].append(name)
    
    return categorized


def generate_interaction_config(categorized_objects):
    """
    Generate interaction configuration based on discovered objects
    """
    config_lines = []
    config_lines.append("# Auto-generated interaction configuration")
    config_lines.append("# Generated from actual Blender scene objects")
    config_lines.append("")
    config_lines.append("INTERACTIVE_OBJECTS = {")
    
    # Kitchen objects
    if categorized_objects["kitchen"]:
        config_lines.append("    # Kitchen")
        for obj_name in categorized_objects["kitchen"]:
            config_lines.append(f'    "{obj_name}": {{"distance": 1.5, "type": "auto", "duration": 5.0}},')
    
    # Dining objects
    if categorized_objects["dining"]:
        config_lines.append("    # Dining Room")
        for obj_name in categorized_objects["dining"]:
            config_lines.append(f'    "{obj_name}": {{"distance": 1.2, "type": "auto", "duration": 10.0}},')
    
    # Bathroom objects
    if categorized_objects["bathroom"]:
        config_lines.append("    # Bathroom")
        for obj_name in categorized_objects["bathroom"]:
            config_lines.append(f'    "{obj_name}": {{"distance": 1.3, "type": "auto", "duration": 5.0}},')
    
    # Bedroom objects
    if categorized_objects["bedroom"]:
        config_lines.append("    # Bedroom")
        for obj_name in categorized_objects["bedroom"]:
            config_lines.append(f'    "{obj_name}": {{"distance": 1.5, "type": "auto", "duration": 10.0}},')
    
    # Living room objects
    if categorized_objects["living"]:
        config_lines.append("    # Living Room")
        for obj_name in categorized_objects["living"]:
            config_lines.append(f'    "{obj_name}": {{"distance": 1.5, "type": "auto", "duration": 15.0}},')
    
    config_lines.append("}")
    
    return "\n".join(config_lines)


def run_object_discovery():
    """Main function to run object discovery and generate config"""
    print("="*70)
    print("🔍 VESPER Object Discovery")
    print("="*70)
    
    # Discover objects
    objects = discover_scene_objects()
    print(f"\n📊 Found {len(objects)} total objects in scene")
    
    # Categorize
    categorized = categorize_objects(objects)
    
    print("\n📋 Objects by Category:")
    for category, obj_list in categorized.items():
        if obj_list:
            print(f"\n  {category.upper()} ({len(obj_list)} objects):")
            for obj_name in obj_list:
                print(f"    - {obj_name}")
    
    # Generate config
    config_text = generate_interaction_config(categorized)
    
    # Save to file
    output_path = Path(bge.logic.expandPath("//")) / "discovered_interaction_config.py"
    with open(output_path, 'w') as f:
        f.write(config_text)
    
    print(f"\n✅ Configuration saved to: {output_path}")
    print("\n💡 Next steps:")
    print("   1. Review the generated configuration")
    print("   2. Adjust distances and durations as needed")
    print("   3. Copy relevant sections to interaction_config.py")
    
    # Also print to console
    print("\n" + "="*70)
    print("GENERATED CONFIGURATION:")
    print("="*70)
    print(config_text)
    print("="*70)
    
    return categorized, config_text


# Run when imported
if __name__ == "__main__":
    run_object_discovery()
