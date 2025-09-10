#!/usr/bin/env python3
"""
VESPER ADL Testing Launcher

This script helps you set up and test VESPER ADL in Blender properly.
Run this outside Blender to get setup instructions.
"""

import os
import sys
from pathlib import Path

def check_blender_setup():
    """Check if Blender setup is ready for VESPER ADL testing"""
    
    print("🔍 VESPER ADL Testing Setup Check")
    print("=" * 40)
    
    base_path = Path(__file__).parent
    
    # Check required files
    required_files = [
        "vesper_adl_system/vesper_adl_quickstart.py",
        "vesper_adl_system/vesper_adl_blender_integration.py", 
        "vesper_adl_game_engine_integration.py",
        "llm_bge_navigation.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    # Check Blender scene files
    blend_files = list(base_path.glob("*.blend"))
    if blend_files:
        print(f"✅ Found {len(blend_files)} Blender scene(s)")
        for blend_file in blend_files:
            print(f"   📁 {blend_file.name}")
    else:
        print("⚠️  No .blend files found")
    
    # Check if this is being run in Blender
    try:
        import bge
        print("✅ Running inside Blender BGE - ready for testing!")
        return True
    except ImportError:
        print("📋 Running outside Blender - setup mode")
        return False

def show_blender_testing_instructions():
    """Show instructions for testing in Blender"""
    
    print("\n🎮 How to Test VESPER ADL in Blender")
    print("=" * 40)
    
    print("\n📋 Step-by-Step Instructions:")
    print("1. 🖥️  Open Blender")
    print("2. 📁 Open your house scene (house_2.blend or house_3.blend)")
    print("3. 🐍 Go to Scripting tab in Blender")
    print("4. 📝 Create new text block or open existing")
    print("5. 📋 Copy and paste this code:")
    
    print("\n" + "="*50)
    print("# VESPER ADL Test Code - Run in Blender")
    print("="*50)
    
    blender_code = '''
import sys
import os

# Add VESPER ADL path
vesper_path = r"C:\\Users\\hbui11\\Desktop\\vesper_llm\\blender"
if vesper_path not in sys.path:
    sys.path.append(vesper_path)

print("🚀 Loading VESPER ADL Game Engine Integration...")

try:
    from vesper_adl_game_engine_integration import initialize_vesper_adl_for_game_engine
    
    # Initialize VESPER ADL
    success = initialize_vesper_adl_for_game_engine()
    
    if success:
        print("✅ VESPER ADL ready for Game Engine testing!")
        print("📋 Next steps:")
        print("1. Press 'P' to start Game Engine")
        print("2. Wait for VLM navigation to initialize")
        print("3. Use keyboard shortcuts:")
        print("   F6: Test cooking task")
        print("   F7: Test medication task")
        print("   F8: Test communication task")
        print("   F9: Show status")
    else:
        print("❌ VESPER ADL initialization failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure all VESPER ADL files are in place")
'''
    
    print(blender_code)
    print("="*50)
    
    print("\n6. 🔵 Click 'Run Script' button in Blender")
    print("7. 🎮 Press 'P' to start Game Engine")
    print("8. 🧪 Use F6-F9 keys to test ADL tasks")

def show_expected_results():
    """Show what to expect during testing"""
    
    print("\n📊 Expected Test Results")
    print("=" * 30)
    
    print("\n🎯 When you press 'P' (Game Engine starts):")
    print("- VLM navigation system initializes")
    print("- Screenshot capture begins")
    print("- VESPER ADL auto-initializes")
    print("- Console shows: '✅ VESPER ADL Game Engine ready!'")
    
    print("\n🧪 When you press F6 (Cooking task):")
    print("- Task gets queued: '🍳 Queued cooking task'")
    print("- VLM analyzes screenshots for kitchen objects")
    print("- Actor moves toward oatmeal, bowl, etc.")
    print("- Task completes: '✅ SUCCESS ADL Task: Make oatmeal...'")
    
    print("\n📈 Performance Indicators:")
    print("- Task completion time: 10-30 seconds")
    print("- Success rate: 60%+ (target 70%+)")
    print("- VLM responses integrated with ADL execution")
    print("- Real-time console feedback")

def troubleshooting_guide():
    """Show troubleshooting guide"""
    
    print("\n🔧 Troubleshooting Guide")
    print("=" * 25)
    
    print("\n❌ 'No module named bge':")
    print("   → You're running outside Blender")
    print("   → Must run the script inside Blender's text editor")
    
    print("\n❌ 'VESPER ADL functions not found':")
    print("   → Check file paths in the script")
    print("   → Make sure vesper_adl_system folder exists")
    
    print("\n❌ 'Actor object not found':")
    print("   → Make sure your scene has an 'Actor' object")
    print("   → Run setup_bge_logic.py first if needed")
    
    print("\n❌ VLM not responding:")
    print("   → Check if VLM service is running")
    print("   → Verify llm_bge_navigation.py works standalone")
    
    print("\n⚠️  Tasks failing:")
    print("   → Check console for specific error messages")
    print("   → Verify CASAS objects exist in scene")
    print("   → Test individual components first")

def create_quick_test_file():
    """Create a quick test file for Blender"""
    
    quick_test_content = '''
# VESPER ADL Quick Test - Run in Blender
import sys
sys.path.append(r"C:\\Users\\hbui11\\Desktop\\vesper_llm\\blender")

try:
    from vesper_adl_game_engine_integration import initialize_vesper_adl_for_game_engine
    success = initialize_vesper_adl_for_game_engine()
    print(f"VESPER ADL Ready: {success}")
except Exception as e:
    print(f"Error: {e}")
'''
    
    test_file_path = Path(__file__).parent / "vesper_adl_quick_test.py"
    
    with open(test_file_path, 'w') as f:
        f.write(quick_test_content)
    
    print(f"\n📝 Created quick test file: {test_file_path}")
    print("💡 You can open this file in Blender's text editor and run it")

def main():
    """Main launcher function"""
    
    print("🚀 VESPER ADL Testing Launcher")
    print("🎯 Goal: Test ADL capabilities in Blender Game Engine")
    print()
    
    # Check setup
    is_in_blender = check_blender_setup()
    
    if is_in_blender:
        print("\n🎉 You're running in Blender! Ready to test!")
        print("Use F6-F9 keys during Game Engine mode")
    else:
        # Show instructions for Blender testing
        show_blender_testing_instructions()
        show_expected_results()
        troubleshooting_guide()
        create_quick_test_file()
        
        print("\n" + "🎯" * 20)
        print("   SUMMARY: Run the code above in Blender!")
        print("🎯" * 20)

if __name__ == "__main__":
    main()
