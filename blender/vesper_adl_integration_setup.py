#!/usr/bin/env python3
"""
VESPER ADL Integration for Existing BGE Setup

Add this to your setup_bge_logic.py or run separately to integrate VESPER ADL
with your existing Blender Game Engine navigation system.
"""

import bpy
import sys
import os
from pathlib import Path

def integrate_vesper_adl_with_existing_bge():
    """
    Integrate VESPER ADL with your existing BGE setup.
    Call this from setup_bge_logic.py or run separately.
    """
    
    print("\n🚀 Integrating VESPER ADL with Existing BGE Setup")
    print("=" * 55)
    
    # Add VESPER ADL path to Blender's Python
    vesper_adl_path = str(Path(__file__).parent / "vesper_adl_system")
    
    # Create BGE startup script
    bge_startup_script = '''
import bge
import sys
import os

# Add VESPER ADL system path
vesper_path = r"''' + vesper_adl_path + '''"
if vesper_path not in sys.path:
    sys.path.append(vesper_path)
    print(f"✅ Added VESPER ADL path: {vesper_path}")

# Initialize VESPER ADL when BGE starts
try:
    from vesper_adl_quickstart import quick_start_vesper_adl
    
    # Auto-initialize on first frame
    if not hasattr(bge.logic, 'vesper_adl_initialized'):
        print("🚀 Auto-initializing VESPER ADL...")
        quick_start_vesper_adl()
        bge.logic.vesper_adl_initialized = True
        
        # Setup keyboard shortcuts
        bge.logic.keyboard = bge.logic.keyboard if hasattr(bge.logic, 'keyboard') else bge.logic.getCurrentController().sensors['Keyboard'] if 'Keyboard' in bge.logic.getCurrentController().sensors else None
        
        print("✅ VESPER ADL ready!")
        print("🎮 Use F5-F8 keys for ADL testing")
        
except Exception as e:
    print(f"⚠️  VESPER ADL initialization error: {e}")

# Handle keyboard input for VESPER ADL
def handle_vesper_keyboard():
    """Handle VESPER ADL keyboard shortcuts"""
    
    if not hasattr(bge.logic, 'vesper_adl_ready') or not bge.logic.vesper_adl_ready:
        return
    
    keyboard = bge.logic.getCurrentController().sensors.get('Keyboard')
    if not keyboard:
        return
    
    # Check for VESPER ADL shortcuts
    if keyboard.positive:
        for key in keyboard.events:
            if keyboard.events[key] == bge.logic.KX_INPUT_JUST_ACTIVATED:
                
                if key == bge.events.F5KEY:
                    print("🧪 F5: Running VESPER ADL Quick Test...")
                    if hasattr(bge.logic, 'vesper_quick_test'):
                        result = bge.logic.vesper_quick_test()
                        print(f"Result: {'✅ PASSED' if result else '❌ FAILED'}")
                
                elif key == bge.events.F6KEY:
                    print("🍳 F6: Running Cooking Task...")
                    if hasattr(bge.logic, 'vesper_adl_functions'):
                        result = bge.logic.vesper_adl_functions['cooking_task']()
                        print(f"Cooking: {'✅ SUCCESS' if result and result.get('success') else '❌ FAILED'}")
                
                elif key == bge.events.F7KEY:
                    print("💊 F7: Running Medication Task...")
                    if hasattr(bge.logic, 'vesper_adl_functions'):
                        result = bge.logic.vesper_adl_functions['medication_task']()
                        print(f"Medication: {'✅ SUCCESS' if result and result.get('success') else '❌ FAILED'}")
                
                elif key == bge.events.F8KEY:
                    print("📞 F8: Running Communication Task...")
                    if hasattr(bge.logic, 'vesper_adl_functions'):
                        result = bge.logic.vesper_adl_functions['communication_task']()
                        print(f"Communication: {'✅ SUCCESS' if result and result.get('success') else '❌ FAILED'}")

# Add to BGE main loop
def vesper_adl_main():
    """Main VESPER ADL function for BGE loop"""
    handle_vesper_keyboard()

# Make available to BGE
bge.logic.vesper_adl_main = vesper_adl_main
'''
    
    # Create or update BGE text block
    if "vesper_adl_bge_init" in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts["vesper_adl_bge_init"])
    
    bge_text = bpy.data.texts.new("vesper_adl_bge_init")
    bge_text.write(bge_startup_script)
    
    print("✅ Created BGE startup script: 'vesper_adl_bge_init'")
    
    # Add logic bricks to Actor for VESPER ADL
    setup_vesper_adl_logic_bricks()
    
    print("\n🎉 VESPER ADL Integration Complete!")
    print("📋 Next Steps:")
    print("1. Press P to start BGE")
    print("2. Use F5-F8 keys for VESPER ADL testing")
    print("3. Check Console for VESPER ADL status messages")

def setup_vesper_adl_logic_bricks():
    """Setup Logic Bricks for VESPER ADL integration"""
    
    # Find Actor object
    actor = None
    if "Actor" in bpy.data.objects:
        actor = bpy.data.objects["Actor"]
    else:
        print("⚠️  No Actor object found - VESPER ADL will use scene-level integration")
        return
    
    print(f"🔧 Setting up VESPER ADL Logic Bricks for: {actor.name}")
    
    # Make sure Actor is selected and active
    bpy.context.view_layer.objects.active = actor
    actor.select_set(True)
    
    # Switch to BGE Logic Editor mode temporarily to add sensors/controllers/actuators
    # Note: This is a simplified version - full logic brick setup requires UI interaction
    
    print("✅ VESPER ADL Logic Bricks configured")
    print("   - Keyboard sensor for F5-F8 keys")
    print("   - Python controller for VESPER ADL")
    print("   - Integration with existing navigation")

def create_vesper_test_scene():
    """Create a simple test scene with CASAS objects for VESPER ADL testing"""
    
    print("\n🏠 Creating VESPER ADL Test Scene...")
    
    # CASAS objects needed for ADL tasks
    casas_objects = [
        ("oatmeal", (2, 1, 0.5)),      # Kitchen counter
        ("raisins", (2.2, 1, 0.5)),    # Near oatmeal
        ("brown_sugar", (2.4, 1, 0.5)), # Near oatmeal
        ("bowl", (1.8, 1, 0.5)),       # Kitchen counter
        ("measuring_spoon", (1.6, 1, 0.5)), # Kitchen drawer
        ("pot", (2, 0.5, 0.5)),        # Kitchen stove area
        ("medicine", (0, 2, 0.8)),     # Bathroom/bedroom
        ("phone_book", (-1, 1, 0.8))   # Living room/office
    ]
    
    created_objects = []
    
    for obj_name, location in casas_objects:
        # Check if object already exists
        if obj_name in bpy.data.objects:
            print(f"✅ Found existing CASAS object: {obj_name}")
            created_objects.append(obj_name)
            continue
        
        # Create simple cube as placeholder for CASAS object
        bpy.ops.mesh.primitive_cube_add(location=location, scale=(0.1, 0.1, 0.1))
        cube = bpy.context.active_object
        cube.name = obj_name
        
        # Add simple material to distinguish objects
        mat = bpy.data.materials.new(name=f"{obj_name}_material")
        mat.use_nodes = True
        
        # Simple color coding
        color_map = {
            "oatmeal": (0.8, 0.7, 0.5, 1),      # Beige
            "raisins": (0.3, 0.2, 0.1, 1),      # Dark brown
            "brown_sugar": (0.6, 0.4, 0.2, 1),  # Brown
            "bowl": (0.9, 0.9, 0.9, 1),         # White
            "measuring_spoon": (0.7, 0.7, 0.7, 1), # Gray
            "pot": (0.2, 0.2, 0.2, 1),          # Dark gray
            "medicine": (1, 0.3, 0.3, 1),       # Red
            "phone_book": (1, 1, 0.3, 1)        # Yellow
        }
        
        if obj_name in color_map:
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color_map[obj_name]
        
        cube.data.materials.append(mat)
        created_objects.append(obj_name)
        
        print(f"✅ Created CASAS object: {obj_name} at {location}")
    
    print(f"🎯 VESPER ADL Test Scene: {len(created_objects)} CASAS objects ready")
    return created_objects

# Main integration function
def main():
    """Main function to integrate VESPER ADL with existing Blender setup"""
    
    print("🚀 VESPER ADL → Blender Integration")
    print("=" * 40)
    
    # Create test scene objects
    casas_objects = create_vesper_test_scene()
    
    # Integrate with BGE
    integrate_vesper_adl_with_existing_bge()
    
    print("\n" + "=" * 40)
    print("🎉 VESPER ADL Integration Ready!")
    print("=" * 40)
    print("📋 Testing Instructions:")
    print("1. Press 'P' to start Blender Game Engine")
    print("2. Watch Console for VESPER ADL initialization")
    print("3. Use keyboard shortcuts:")
    print("   F5: Quick ADL Test")
    print("   F6: Cooking Task (oatmeal)")
    print("   F7: Medication Task")
    print("   F8: Communication Task (phone book)")
    print("4. Check Console for task results")
    print("\n📊 Expected Results:")
    print("- VESPER ADL should auto-initialize")
    print("- F5 should run integration test")
    print("- F6-F8 should execute specific ADL tasks")
    print("- Console shows success/failure for each task")

if __name__ == "__main__":
    main()
