#!/usr/bin/env python3
"""
BGE Navigation Diagnostic Tool
Identifies why navigation didn't run and provides troubleshooting steps
"""

import os
import json
from datetime import datetime

def analyze_empty_log():
    """Analyze the empty log file and provide diagnostic information"""
    print("🔍 BGE Navigation Diagnostic Analysis")
    print("=" * 50)
    
    log_file = r"c:\Users\hbui11\Desktop\vesper_llm\blender\evaluation_logs\vesper_navigation_log_20250828_134413.json"
    
    print(f"📄 Log File: {os.path.basename(log_file)}")
    print(f"📅 Session ID: 20250828_134413")
    print(f"⏰ Timestamp: {datetime.fromtimestamp(1756403053.4642522)}")
    
    print("\n🚨 ISSUE IDENTIFIED: Empty Navigation Log")
    print("All counters at 0 indicates BGE navigation didn't execute properly")
    
    print("\n🔍 POSSIBLE CAUSES:")
    causes = [
        "1. BGE Game Engine didn't start (Press P not working)",
        "2. Python script not loaded in Blender Logic Bricks",
        "3. LLM backend server not running",
        "4. Import errors in BGE navigation script",
        "5. Screenshot capture failing",
        "6. Actor object missing from scene",
        "7. Logic brick connections not properly set up"
    ]
    
    for cause in causes:
        print(f"   {cause}")
    
    return True

def check_bge_setup():
    """Check BGE navigation file and dependencies"""
    print("\n🔧 SETUP VERIFICATION:")
    
    # Check BGE navigation file
    bge_file = r"c:\Users\hbui11\Desktop\vesper_llm\blender\llm_bge_navigation.py"
    if os.path.exists(bge_file):
        print("   ✅ BGE navigation script exists")
        
        # Check file size (should be substantial)
        file_size = os.path.getsize(bge_file)
        if file_size > 50000:  # Should be ~50KB+
            print(f"   ✅ Script file size: {file_size:,} bytes (good)")
        else:
            print(f"   ⚠️ Script file size: {file_size:,} bytes (seems small)")
    else:
        print("   ❌ BGE navigation script missing!")
        return False
    
    # Check Blender files
    blender_files = [
        r"c:\Users\hbui11\Desktop\vesper_llm\blender\house.blend",
        r"c:\Users\hbui11\Desktop\vesper_llm\blender\house_2.blend",
        r"c:\Users\hbui11\Desktop\vesper_llm\blender\house_3.blend"
    ]
    
    found_blend = False
    for blend_file in blender_files:
        if os.path.exists(blend_file):
            print(f"   ✅ {os.path.basename(blend_file)} exists")
            found_blend = True
        else:
            print(f"   ❌ {os.path.basename(blend_file)} missing")
    
    if not found_blend:
        print("   🚨 No Blender scene files found!")
        return False
    
    # Check evaluation logs directory
    log_dir = r"c:\Users\hbui11\Desktop\vesper_llm\blender\evaluation_logs"
    if os.path.exists(log_dir):
        print("   ✅ Evaluation logs directory exists")
        
        # List recent log files
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
        print(f"   📊 Found {len(log_files)} log files")
        
        if log_files:
            latest_log = max(log_files)
            print(f"   📄 Latest log: {latest_log}")
    else:
        print("   ❌ Evaluation logs directory missing!")
    
    return True

def provide_troubleshooting_steps():
    """Provide step-by-step troubleshooting guide"""
    print("\n🛠️ TROUBLESHOOTING STEPS:")
    
    steps = [
        {
            "step": "1. Verify Blender Setup",
            "actions": [
                "Open Blender",
                "Load house.blend from vesper_llm/blender/",
                "Check if 'Actor' object exists in scene",
                "Verify Logic Bricks are connected to Actor"
            ]
        },
        {
            "step": "2. Check Logic Bricks Configuration",
            "actions": [
                "Select Actor object in Blender",
                "Go to Logic Editor",
                "Verify Python script controller exists",
                "Ensure script points to llm_bge_navigation.py",
                "Check sensor connections (Always sensor recommended)"
            ]
        },
        {
            "step": "3. Test BGE Startup",
            "actions": [
                "In Blender, press P to start Game Engine",
                "Check Blender console for Python errors",
                "Look for initial startup messages",
                "Watch for 'BGE: Starting VLM navigation' message"
            ]
        },
        {
            "step": "4. Backend Server Check",
            "actions": [
                "Start backend server: python backend/app/main.py",
                "Verify server runs on http://localhost:8000",
                "Test with: curl http://localhost:8000/health",
                "Check LLM model availability"
            ]
        },
        {
            "step": "5. Debug Mode Testing",
            "actions": [
                "Add print statements at start of main() function",
                "Test individual components separately",
                "Check screenshot capture works",
                "Verify metrics logger initialization"
            ]
        }
    ]
    
    for step_info in steps:
        print(f"\n   {step_info['step']}:")
        for action in step_info['actions']:
            print(f"      • {action}")

def create_debug_version():
    """Create a minimal debug version of BGE script"""
    print("\n🐛 CREATING DEBUG VERSION:")
    
    debug_script = '''import bge
import time

def main():
    print("🚀 DEBUG: BGE Navigation Debug Version Started!")
    print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    scene = bge.logic.getCurrentScene()
    print(f"🎬 Scene: {scene.name}")
    
    # Check for Actor
    actor = scene.objects.get("Actor")
    if actor:
        print(f"🎯 Actor found at: {actor.worldPosition}")
    else:
        print("❌ Actor object not found!")
        # List all objects
        print("📋 Scene objects:")
        for obj in scene.objects:
            print(f"   - {obj.name}")
    
    # Test metrics logger
    try:
        from blender.llm_bge_navigation import VESPERMetricsLogger
        metrics = VESPERMetricsLogger()
        print("✅ VESPERMetricsLogger initialized successfully")
    except Exception as e:
        print(f"❌ VESPERMetricsLogger failed: {e}")
    
    print("🔚 DEBUG: Script completed")

if __name__ == "__main__":
    main()
'''
    
    debug_file = r"c:\Users\hbui11\Desktop\vesper_llm\blender\debug_bge_test.py"
    
    try:
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(debug_script)
        print(f"   ✅ Created debug script: {os.path.basename(debug_file)}")
        print("   📋 To use:")
        print("      1. In Blender Logic Editor, change script to debug_bge_test.py")
        print("      2. Press P to run BGE")
        print("      3. Check console for debug output")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create debug script: {e}")
        return False

def main():
    """Run complete diagnostic analysis"""
    analyze_empty_log()
    check_bge_setup()
    provide_troubleshooting_steps()
    create_debug_version()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDED NEXT ACTIONS:")
    print("1. Use the debug script to test basic BGE functionality")
    print("2. Check Blender console for any Python errors")
    print("3. Verify backend server is running")
    print("4. Ensure Logic Bricks are properly configured")
    print("5. Test with the debug version first, then full navigation")
    
    print(f"\n📊 For real-time monitoring, run:")
    print("   python evaluation/run_evaluation.py")
    
    print(f"\n🔍 To analyze logs after successful run:")
    print("   python evaluation/log_analyzer.py")

if __name__ == "__main__":
    main()
'''
