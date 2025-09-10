#!/usr/bin/env python3
"""
Add VESPER ADL to Existing BGE Navigation

Add this code to your existing setup_bge_logic.py or run it separately
to integrate VESPER ADL with your VLM navigation system.
"""

# Add this to your existing setup_bge_logic.py file:

def add_vesper_adl_to_existing_navigation():
    """
    Add VESPER ADL to your existing VLM navigation setup.
    Call this after your existing setup_bge_logic_for_navigation().
    """
    
    print("\n🔗 Adding VESPER ADL to existing navigation...")
    
    # Create BGE script for VESPER ADL integration
    vesper_bge_script = '''
import bge
import sys
import os

# Add VESPER ADL path
vesper_path = r"C:\\Users\\hbui11\\Desktop\\vesper_llm\\blender"
if vesper_path not in sys.path:
    sys.path.append(vesper_path)

# Initialize VESPER ADL Game Engine integration
try:
    from vesper_adl_game_engine_integration import (
        initialize_vesper_adl_for_game_engine,
        handle_vesper_adl_keyboard_in_game
    )
    
    # Auto-initialize on first frame
    if not hasattr(bge.logic, 'vesper_adl_game_initialized'):
        print("🎮 Initializing VESPER ADL for Game Engine...")
        success = initialize_vesper_adl_for_game_engine()
        
        if success:
            bge.logic.vesper_adl_game_initialized = True
            print("✅ VESPER ADL Game Engine ready!")
            print("🎯 F6: Cooking | F7: Medication | F8: Communication | F9: Status")
        else:
            print("❌ VESPER ADL Game Engine initialization failed")
    
    # Handle keyboard input every frame
    handle_vesper_adl_keyboard_in_game()
    
    # Call frame monitor if available
    if hasattr(bge.logic, 'vesper_adl_frame_monitor'):
        bge.logic.vesper_adl_frame_monitor()

except Exception as e:
    print(f"⚠️  VESPER ADL Game Engine error: {e}")
'''
    
    # Add to Blender text blocks
    import bpy
    
    if "vesper_adl_game_logic" in bpy.data.texts:
        bpy.data.texts.remove(bpy.data.texts["vesper_adl_game_logic"])
    
    bge_text = bpy.data.texts.new("vesper_adl_game_logic")
    bge_text.write(vesper_bge_script)
    
    print("✅ Created 'vesper_adl_game_logic' text block")
    print("📋 Next steps:")
    print("1. Add logic brick to Actor:")
    print("   - Always sensor → Python controller → 'vesper_adl_game_logic'")
    print("2. Press 'P' to start Game Engine")
    print("3. Use F6-F9 during VLM navigation")

# Add to your existing setup_bge_logic.py:
if __name__ == "__main__":
    # Your existing setup code here
    setup_bge_logic_for_navigation()
    
    # Add VESPER ADL integration
    add_vesper_adl_to_existing_navigation()
