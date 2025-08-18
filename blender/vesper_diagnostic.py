import bpy
import addon_utils

print("🔍 VESPER Tools Registration Diagnostic")
print("=" * 50)

# Check 1: Module presence
print("1. Checking for VESPER Tools module...")
vesper_found = False
for module in addon_utils.modules():
    if "vesper_tools" in module.__name__:
        print(f"   ✅ Found: {module.__name__}")
        vesper_found = True
        
        # Check bl_info
        if hasattr(module, 'bl_info'):
            bl_info = module.bl_info
            print(f"   📋 Name: {bl_info.get('name')}")
            print(f"   📋 Version: {bl_info.get('version')}")
            print(f"   📋 Category: {bl_info.get('category')}")
        break

if not vesper_found:
    print("   ❌ VESPER Tools module not found!")

# Check 2: Addon enabled status
print("\n2. Checking addon enabled status...")
is_enabled = addon_utils.check("vesper_tools")[0]
print(f"   Enabled: {is_enabled}")

# Check 3: Operator registration
print("\n3. Checking operator registration...")
operators_to_check = [
    ("vesper", "llm_navigation"),
    ("vesper", "tag_device"),
    ("vesper", "export_evaluation"),
    ("vesper", "game_engine_test")
]

for namespace, op_name in operators_to_check:
    try:
        ns = getattr(bpy.ops, namespace, None)
        if ns and hasattr(ns, op_name):
            print(f"   ✅ {namespace}.{op_name}")
        else:
            print(f"   ❌ {namespace}.{op_name}")
    except Exception as e:
        print(f"   ❌ {namespace}.{op_name} - Error: {e}")

# Check 4: Panel registration
print("\n4. Checking panel registration...")
try:
    # Check if VESPER panel is in the UI
    panels = [panel for panel in bpy.types.Panel.__subclasses__() 
              if "VESPER" in panel.__name__]
    print(f"   VESPER Panels found: {len(panels)}")
    for panel in panels:
        print(f"   ✅ {panel.__name__}")
except Exception as e:
    print(f"   ❌ Panel check error: {e}")

# Check 5: Console for registration messages
print("\n5. Manual registration test...")
try:
    # Try to manually register if needed
    import sys
    import os
    
    vesper_path = r"c:\Users\hbui11\Desktop\vesper_llm\blender\addons\vesper_tools"
    if os.path.exists(vesper_path):
        print(f"   ✅ VESPER path exists: {vesper_path}")
        
        # Try importing the module
        if vesper_path not in sys.path:
            sys.path.insert(0, os.path.dirname(vesper_path))
        
        try:
            import vesper_tools
            print("   ✅ VESPER Tools module imported successfully")
            
            # Check if register function exists
            if hasattr(vesper_tools, 'register'):
                print("   ✅ register() function found")
            else:
                print("   ❌ register() function not found")
                
        except Exception as e:
            print(f"   ❌ Import error: {e}")
    else:
        print(f"   ❌ VESPER path not found: {vesper_path}")
        
except Exception as e:
    print(f"   ❌ Manual test error: {e}")

print("\n" + "=" * 50)
print("🎯 DIAGNOSTIC COMPLETE")
print("💡 If issues found, try:")
print("   1. Disable and re-enable the add-on")
print("   2. Restart UPBGE")
print("   3. Check console for error messages")
print("   4. Verify file permissions")
