"""
FINAL MANUAL STEP - CASAS Logger Initialization
================================================

Copy the code block below and paste it into:
blender/llm_bge_navigation.py at line ~1103

FIND THIS SECTION (around line 1100):
-----------------------------------
        # Initialize metrics logging
        if not hasattr(bge.logic, 'metrics_logger'):
            bge.logic.metrics_logger = get_metrics_logger()
            print("📊 Metrics logging system initialized")
        
        bge.logic.startup_complete = True
        print("🎮 Starting continuous task execution...")


REPLACE WITH:
-----------------------------------
        # Initialize metrics logging
        if not hasattr(bge.logic, 'metrics_logger'):
            bge.logic.metrics_logger = get_metrics_logger()
            print("📊 Metrics logging system initialized")
        
        # Initialize CASAS motion sensor logging
        if not hasattr(bge.logic, 'casas_motion_logger'):
            try:
                bge.logic.casas_motion_logger = CASASMotionSensorLogger()
                print("🎯 CASAS motion sensor logger initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize CASAS logger: {e}")
        
        bge.logic.startup_complete = True
        print("🎮 Starting continuous task execution...")


THAT'S IT! 
==========
After adding this:
✅ All 7/7 components will be complete
✅ CASAS motion sensor logging fully integrated
✅ Ready for ground truth comparison

Then run:
  python blender/llm_bge_navigation.py

Your system will automatically:
  • Track motion sensors (motion1-6) as actor moves
  • Log CASAS format data to: blender/vesper_motion_sensors.txt
  • Export data on task completion for comparison
"""

# Quick check if you've added it
import sys
from pathlib import Path

nav_file = Path(__file__).parent / "blender" / "llm_bge_navigation.py"
if nav_file.exists():
    with open(nav_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "bge.logic.casas_motion_logger = CASASMotionSensorLogger()" in content:
            print("✅ CASAS logger initialization FOUND! All components ready!")
            print("🚀 Run: python blender/llm_bge_navigation.py")
        else:
            print("⚠️  Please add the initialization code above to complete setup")
            print(f"   Edit: {nav_file}")
            print("   Line: ~1103 (after metrics logger initialization)")
