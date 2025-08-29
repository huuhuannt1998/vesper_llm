#!/usr/bin/env python3
"""
Minimal BGE Test Script - Step-by-step diagnostics
This script tests each component individually to isolate the failure point
"""

import bge
import time
import sys
import os

def test_basic_bge():
    """Test basic BGE functionality"""
    print("=" * 60)
    print("🚀 MINIMAL BGE TEST STARTED")
    print(f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Test 1: BGE scene access
        print("\n🧪 TEST 1: BGE Scene Access")
        scene = bge.logic.getCurrentScene()
        print(f"   ✅ Scene name: {scene.name}")
        print(f"   ✅ Scene objects count: {len(scene.objects)}")
        
        # Test 2: List all objects
        print("\n🧪 TEST 2: Scene Objects")
        for i, obj in enumerate(scene.objects):
            print(f"   {i+1:2d}. {obj.name} at {obj.worldPosition}")
        
        # Test 3: Find Actor
        print("\n🧪 TEST 3: Actor Object Search")
        actor = scene.objects.get("Actor")
        if actor:
            print(f"   ✅ Actor found at position: {actor.worldPosition}")
            print(f"   ✅ Actor type: {type(actor)}")
        else:
            print("   ❌ Actor object NOT FOUND!")
            print("   🔍 Searching for similar names:")
            for obj in scene.objects:
                if 'actor' in obj.name.lower() or 'player' in obj.name.lower():
                    print(f"      • {obj.name} (possible actor)")
        
        # Test 4: Python path and imports
        print("\n🧪 TEST 4: Python Environment")
        print(f"   Python version: {sys.version}")
        print(f"   Python path entries:")
        for i, path in enumerate(sys.path[:5]):  # Show first 5 paths
            print(f"      {i+1}. {path}")
        
        # Test 5: Try importing navigation modules
        print("\n🧪 TEST 5: Module Import Test")
        try:
            # Test basic imports
            import json
            print("   ✅ json module")
            
            import base64
            print("   ✅ base64 module")
            
            import threading
            print("   ✅ threading module")
            
            import queue
            print("   ✅ queue module")
            
        except Exception as e:
            print(f"   ❌ Basic imports failed: {e}")
        
        # Test 6: Try importing backend modules (expected to fail in BGE)
        print("\n🧪 TEST 6: Backend Module Test")
        try:
            from backend.app.llm.client import client
            print("   ✅ backend.app.llm.client imported (unexpected success)")
        except ImportError as e:
            print(f"   ⚠️ backend.app.llm.client import failed (expected): {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error importing backend: {e}")
        
        # Test 7: File system access
        print("\n🧪 TEST 7: File System Access")
        vesper_path = "C:\\Users\\hbui11\\Desktop\\vesper_llm"
        if os.path.exists(vesper_path):
            print(f"   ✅ VESPER directory found: {vesper_path}")
            
            # Check for key files
            key_files = [
                "blender/llm_bge_navigation.py",
                "blender/evaluation_logs",
                "backend/app/main.py"
            ]
            
            for file_path in key_files:
                full_path = os.path.join(vesper_path, file_path)
                if os.path.exists(full_path):
                    print(f"   ✅ {file_path}")
                else:
                    print(f"   ❌ {file_path} - NOT FOUND")
        else:
            print(f"   ❌ VESPER directory not found: {vesper_path}")
        
        # Test 8: Try creating a log file
        print("\n🧪 TEST 8: Log File Creation Test")
        try:
            log_dir = os.path.join(vesper_path, "blender", "evaluation_logs")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                print(f"   ✅ Created log directory: {log_dir}")
            
            test_log = os.path.join(log_dir, "bge_test_log.txt")
            with open(test_log, 'w') as f:
                f.write(f"BGE Test Log - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("This is a test from minimal BGE script\n")
            print(f"   ✅ Test log created: {os.path.basename(test_log)}")
            
        except Exception as e:
            print(f"   ❌ Log file creation failed: {e}")
        
        print("\n" + "=" * 60)
        print("🎯 MINIMAL TEST COMPLETED")
        print("If you can see this message, basic BGE functionality works!")
        print("Check the console output above for any ❌ failures")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR in minimal test: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

def main():
    """Main function called by BGE"""
    test_basic_bge()

# BGE will call this
if __name__ == "__main__":
    main()
