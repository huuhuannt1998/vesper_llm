#!/usr/bin/env python3
"""
Verify AppData Addon Update
===========================

Verify that the AppData version of the Blender addon has been updated with the enhanced port allocation system.
"""

import sys
import os

def check_appdata_addon():
    """Check if the AppData addon has the enhanced port allocation system"""
    
    print("🔍 Verifying AppData Blender Addon Update")
    print("=" * 45)
    
    appdata_file = r"c:\Users\hbui11\AppData\Roaming\UPBGE\Blender\4.4\scripts\addons\vesper_smart_home\__init__.py"
    
    if not os.path.exists(appdata_file):
        print(f"❌ AppData addon file not found: {appdata_file}")
        return False
    
    print(f"✅ Found AppData addon file")
    
    # Check for key features of the enhanced system
    features_to_check = [
        ("device_port_ranges", "Port range system"),
        ("allocated_ports", "Port tracking system"),
        ("find_available_port_in_range", "Enhanced port finding"),
        ("bind(('0.0.0.0'", "Docker-compatible port binding"),
        ("docker.*ps.*publish", "Docker container inspection"),
        ("motion-sensor.*9000.*9199", "Motion sensor port range")
    ]
    
    try:
        with open(appdata_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📋 Checking Enhanced Features:")
        all_found = True
        
        for feature_code, feature_name in features_to_check:
            if feature_code in content:
                print(f"   ✅ {feature_name}")
            else:
                print(f"   ❌ {feature_name} - NOT FOUND")
                all_found = False
        
        if all_found:
            print(f"\n🎉 All enhanced features found in AppData addon!")
            print(f"   The port allocation system is ready to use in Blender.")
        else:
            print(f"\n⚠️ Some features missing from AppData addon.")
            
        # Check specific port ranges
        print(f"\n🎯 Port Range Configuration:")
        if '"motion-sensor": {"start": 9000, "end": 9199}' in content:
            print(f"   ✅ Motion sensors: 9000-9199 (200 ports)")
        else:
            print(f"   ❌ Motion sensor range not configured")
            
        if '"item-sensor": {"start": 9200, "end": 9299}' in content:
            print(f"   ✅ Item sensors: 9200-9299 (100 ports)")
        else:
            print(f"   ❌ Item sensor range not configured")
            
        return all_found
        
    except Exception as e:
        print(f"❌ Error reading AppData addon file: {e}")
        return False

def compare_with_source():
    """Compare key features between source and AppData versions"""
    
    print(f"\n🔄 Comparing Source vs AppData Versions:")
    print("=" * 40)
    
    source_file = r"C:\Users\hbui11\Desktop\vesper_llm\blender\addons\vesper_smart_home\__init__.py"
    appdata_file = r"c:\Users\hbui11\AppData\Roaming\UPBGE\Blender\4.4\scripts\addons\vesper_smart_home\__init__.py"
    
    if not os.path.exists(source_file):
        print(f"⚠️ Source file not found: {source_file}")
        return
        
    if not os.path.exists(appdata_file):
        print(f"❌ AppData file not found: {appdata_file}")
        return
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        with open(appdata_file, 'r', encoding='utf-8') as f:
            appdata_content = f.read()
        
        # Check key methods
        key_methods = [
            "find_available_port_in_range",
            "device_port_ranges",
            "allocated_ports"
        ]
        
        for method in key_methods:
            source_has = method in source_content
            appdata_has = method in appdata_content
            
            if source_has and appdata_has:
                print(f"   ✅ {method}: Both versions have it")
            elif source_has and not appdata_has:
                print(f"   ⚠️ {method}: Source has it, AppData missing")
            elif not source_has and appdata_has:
                print(f"   🔄 {method}: AppData has it, Source missing")
            else:
                print(f"   ❌ {method}: Both versions missing")
                
    except Exception as e:
        print(f"❌ Error comparing files: {e}")

def main():
    print("🚀 AppData Addon Verification Tool")
    print("=" * 35)
    
    # Check if AppData addon is updated
    addon_updated = check_appdata_addon()
    
    # Compare with source
    compare_with_source()
    
    print(f"\n📊 Summary:")
    if addon_updated:
        print(f"   ✅ AppData addon successfully updated")
        print(f"   ✅ Enhanced port allocation system active")
        print(f"   ✅ Ready to test multiple motion sensors in Blender")
        print(f"\n🎮 Next Steps:")
        print(f"   1. Restart Blender/UPBGE to reload the addon")
        print(f"   2. Open your smart home scene")
        print(f"   3. Try spawning multiple motion sensors")
        print(f"   4. Each should get unique ports (9000, 9001, 9002...)")
    else:
        print(f"   ⚠️ AppData addon needs manual verification")
        print(f"   🔧 Some features may not be fully updated")
    
    print(f"\n🎯 Expected Behavior:")
    print(f"   • Motion Sensor 1 → Port 9000")
    print(f"   • Motion Sensor 2 → Port 9001") 
    print(f"   • Motion Sensor 3 → Port 9002")
    print(f"   • No port conflicts!")

if __name__ == "__main__":
    main()
