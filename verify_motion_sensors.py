#!/usr/bin/env python3
"""
Verify motion sensor folder structure and basic functionality
"""

import os
import json

def verify_structure():
    """Verify the motion sensor folder structure"""
    print("🔍 Verifying motion sensor organization...")
    
    base_path = "motion_sensors"
    expected_structure = {
        "": ["__init__.py", "README.md"],
        "core": ["__init__.py", "motion_sensor_detection.py"],
        "setup": ["__init__.py", "setup_motion_sensors.py"],
        "demos": ["__init__.py", "test_motion_sensors.py", "demo_motion_sensors.py"],
        "configs": ["__init__.py", "sensor_layouts.json", "device_specs.json"],
        "documentation": ["API_REFERENCE.md", "INTEGRATION_GUIDE.md", "PLACEMENT_GUIDE.md"]
    }
    
    missing_files = []
    found_files = []
    
    for folder, files in expected_structure.items():
        folder_path = os.path.join(base_path, folder) if folder else base_path
        
        if not os.path.exists(folder_path):
            print(f"❌ Missing folder: {folder_path}")
            continue
            
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.exists(file_path):
                found_files.append(file_path)
                print(f"✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"❌ Missing: {file_path}")
    
    print(f"\n📊 Structure verification:")
    print(f"   ✅ Found: {len(found_files)} files")
    print(f"   ❌ Missing: {len(missing_files)} files")
    
    return len(missing_files) == 0

def verify_configs():
    """Verify configuration files"""
    print("\n⚙️ Verifying configuration files...")
    
    # Check sensor layouts
    layouts_file = "motion_sensors/configs/sensor_layouts.json"
    if os.path.exists(layouts_file):
        with open(layouts_file, 'r') as f:
            layouts = json.load(f)
        
        print(f"✅ Sensor layouts: {list(layouts.keys())}")
        
        for layout_name, layout_data in layouts.items():
            sensor_count = layout_data.get('total_sensors', 0)
            description = layout_data.get('description', 'No description')
            print(f"   🏠 {layout_name}: {sensor_count} sensors - {description}")
    
    # Check device specs
    specs_file = "motion_sensors/configs/device_specs.json"
    if os.path.exists(specs_file):
        with open(specs_file, 'r') as f:
            specs = json.load(f)
        
        print(f"✅ Device specifications: {list(specs.keys())}")
        
        for device_name, device_data in specs.items():
            model = device_data.get('model', 'Unknown')
            fov = device_data.get('specifications', {}).get('field_of_view', {}).get('horizontal', 'Unknown')
            range_m = device_data.get('specifications', {}).get('detection_range', {}).get('maximum', 'Unknown')
            print(f"   🔧 {device_name}: {model} ({fov}° FOV, {range_m}m range)")

def verify_documentation():
    """Verify documentation files"""
    print("\n📚 Verifying documentation...")
    
    doc_files = [
        "motion_sensors/documentation/API_REFERENCE.md",
        "motion_sensors/documentation/INTEGRATION_GUIDE.md", 
        "motion_sensors/documentation/PLACEMENT_GUIDE.md",
        "motion_sensors/README.md"
    ]
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            size = os.path.getsize(doc_file)
            print(f"✅ {doc_file} ({size:,} bytes)")
        else:
            print(f"❌ Missing: {doc_file}")

def main():
    print("🏠" + "="*50 + "🏠")
    print("  VESPER Motion Sensor Organization Test")
    print("="*54)
    
    structure_ok = verify_structure()
    verify_configs()
    verify_documentation()
    
    print("\n🎯 Motion Sensor System Organization:")
    print("   📁 Core detection engine: motion_sensors/core/")
    print("   ⚙️ Setup and deployment: motion_sensors/setup/")
    print("   🎬 Demos and testing: motion_sensors/demos/")
    print("   📋 Configurations: motion_sensors/configs/")
    print("   📚 Documentation: motion_sensors/documentation/")
    
    print("\n🚀 Quick Start Commands:")
    print("   python motion_sensor_launcher.py setup --layout medium_house")
    print("   python motion_sensor_launcher.py demo")
    print("   python motion_sensor_launcher.py config --list-layouts")
    
    if structure_ok:
        print("\n🎉 Motion sensor organization verified successfully!")
    else:
        print("\n⚠️ Some files are missing - check the structure above")

if __name__ == "__main__":
    main()
