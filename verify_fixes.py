#!/usr/bin/env python3
"""
Test the fixed path resolution for Game Engine LLM integration
"""
import os
import sys

def test_fixed_imports():
    """Test that all the fixed import paths work correctly"""
    print("🧪 Testing Fixed Path Resolution")
    print("=" * 50)
    
    # Test 1: Backend LLM client with planner
    try:
        from backend.app.llm.client import chat_completion, BASE_URL, MODEL
        from backend.app.llm.planner import ROOMS, DEVICES
        print("✅ Backend LLM client and planner import successfully")
        print(f"   Base URL: {BASE_URL}")
        print(f"   Model: {MODEL}")
        print(f"   Rooms loaded: {list(ROOMS.keys())}")
    except Exception as e:
        print(f"❌ Backend import failed: {e}")
        return False
    
    # Test 2: Scripts with fixed paths
    try:
        from scripts.visual_navigation import ROOMS as nav_rooms
        from scripts.llm_planner import ROOMS as planner_rooms
        print("✅ Scripts import successfully with fixed paths")
        print(f"   Navigation rooms: {list(nav_rooms.keys())}")
        print(f"   Planner rooms: {list(planner_rooms.keys())}")
    except Exception as e:
        print(f"❌ Scripts import failed: {e}")
        return False
    
    # Test 3: Dynamic path finding function
    def find_vesper_root():
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        
        while current_dir and current_dir != os.path.dirname(current_dir):
            if os.path.basename(current_dir) == 'vesper_llm':
                return current_dir
            if os.path.exists(os.path.join(current_dir, 'backend', 'app', 'llm', 'client.py')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        
        return None
    
    detected_root = find_vesper_root()
    if detected_root:
        print(f"✅ Dynamic path detection works: {detected_root}")
    else:
        print("❌ Dynamic path detection failed")
        return False
    
    print(f"\n🎉 All path fixes are working correctly!")
    print(f"The Game Engine should now be able to find and import the LLM client.")
    
    return True

if __name__ == "__main__":
    success = test_fixed_imports()
    exit_code = 0 if success else 1
    print(f"\nTest completed with exit code: {exit_code}")
    sys.exit(exit_code)
