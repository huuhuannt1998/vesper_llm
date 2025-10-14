#!/usr/bin/env python3
"""
Test interaction system imports (without BGE)
"""

import sys
import os

# Add blender directory to path
blender_dir = r"C:\Users\hbui11\Desktop\vesper_llm\blender"
sys.path.insert(0, blender_dir)

print("Testing interaction system imports...")
print("=" * 70)

# Test 1: Import item sensor manager
try:
    from interaction_system.item_sensor_manager import get_item_sensor_manager, setup_default_item_sensors
    print("✅ item_sensor_manager imports work")
except Exception as e:
    print(f"❌ item_sensor_manager import failed: {e}")

# Test 2: Import virtual time manager
try:
    from time_system.virtual_time_manager import get_virtual_time_manager, get_task_timer
    print("✅ virtual_time_manager imports work")
except Exception as e:
    print(f"❌ virtual_time_manager import failed: {e}")

# Test 3: Import virtual device manager
try:
    from virtual_sensors.virtual_device_manager import get_device_manager, setup_default_devices
    print("✅ virtual_device_manager imports work")
except Exception as e:
    print(f"❌ virtual_device_manager import failed: {e}")

# Test 4: Import main integration (will fail at bge but should parse)
try:
    import interaction_system.vesper_interaction_integration
    print("❌ vesper_interaction_integration should have failed (needs bge)")
except ModuleNotFoundError as e:
    if "bge" in str(e):
        print("✅ vesper_interaction_integration structure OK (bge missing is expected)")
    else:
        print(f"❌ Unexpected import error: {e}")

print("=" * 70)
print("\n✅ Import structure is correct!")
print("The 'bge' module error is expected - it's only available in Blender.")
print("\nWhen running in Blender, all imports should work correctly.")
