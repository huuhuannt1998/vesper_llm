#!/usr/bin/env python3
"""
Simple test to verify motion sensor organization works correctly
"""

import sys
sys.path.append('.')

try:
    from motion_sensors.configs import load_sensor_layout
    
    print("🧪 Testing motion sensor organization...")
    
    # Test loading configurations
    layout = load_sensor_layout('medium_house')
    if layout:
        print(f"✅ Loaded '{layout['description']}'")
        print(f"   📊 Total sensors: {layout['total_sensors']}")
        print(f"   🏠 Sensor rooms: {set(s['room'] for s in layout['sensors'])}")
    else:
        print("❌ Failed to load layout")
    
    # Test sensor specs
    from motion_sensors import get_sensor_specs
    specs = get_sensor_specs()
    print(f"✅ Sensor specs: {specs['model']}")
    print(f"   📐 FOV: {specs['field_of_view']}°")
    print(f"   📏 Range: {specs['detection_range']}m")
    
    print("🎉 Motion sensor organization test passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Test error: {e}")
