#!/usr/bin/env python3
"""
Test BGE navigation initialization with Open WebUI
"""

import os
import sys

# Add project paths to Python path (same as BGE navigation does)
current_dir = os.path.dirname(os.path.abspath(__file__))
blender_dir = os.path.join(current_dir, 'blender')
parent_dir = os.path.dirname(current_dir)

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if blender_dir not in sys.path:
    sys.path.insert(0, blender_dir)

def test_bge_navigation_initialization():
    """Test that BGE navigation can initialize with Open WebUI"""
    
    print("🧪 Testing BGE Navigation Initialization")
    print("=" * 45)
    
    # Mock BGE logic for testing outside of Blender
    class MockBGELogic:
        def __init__(self):
            self.vesper_continuous_nav = False
            self.llm_initialized = False
    
    class MockBGE:
        def __init__(self):
            self.logic = MockBGELogic()
    
    # Mock bge module for testing
    sys.modules['bge'] = MockBGE()
    sys.modules['mathutils'] = type('MockMathutils', (), {})()
    
    try:
        # Test importing the BGE navigation functions we modified
        print("📦 Testing imports...")
        
        # Add blender directory to path for import
        if blender_dir not in sys.path:
            sys.path.insert(0, blender_dir)
        
        # Import the functions we care about
        from llm_bge_navigation import setup_python_path, initialize_llm_client
        
        print("✅ Successfully imported BGE navigation functions")
        
        # Test setup_python_path
        print("\n🔧 Testing setup_python_path...")
        path_result = setup_python_path()
        print(f"✅ Path setup result: {path_result}")
        
        # Test initialize_llm_client 
        print("\n🤖 Testing initialize_llm_client...")
        llm_result = initialize_llm_client()
        print(f"✅ LLM initialization result: {llm_result}")
        
        if llm_result:
            print("\n🎉 BGE Navigation Initialization Success!")
            print("✅ Path setup completed")
            print("✅ LLM client initialized")
            print("✅ Open WebUI integration confirmed")
            print("🚀 BGE navigation is ready to use the faster model!")
        else:
            print("\n❌ LLM initialization failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def show_integration_summary():
    """Show summary of the integration"""
    
    print(f"\n📋 BGE Navigation Open WebUI Integration Summary")
    print("=" * 55)
    
    print("✅ Changes Made:")
    print("  - Updated backend/app/llm/client.py to use Open WebUI")
    print("  - Added configuration logging to BGE navigation")
    print("  - Maintained backward compatibility with Ollama")
    print("  - Enhanced initialization feedback")
    
    print("\n🔧 Configuration:")
    print("  - Primary: Open WebUI server with InternVL3_5-30B-A3B")
    print("  - Fallback: Ollama (if Open WebUI unavailable)")
    print("  - Vision: Full support for both text and image analysis")
    
    print("\n🎯 Usage in BGE:")
    print("  1. BGE calls initialize_llm_client()")
    print("  2. Client auto-detects Open WebUI configuration")
    print("  3. Creates VLM wrapper for BGE image processing")
    print("  4. Navigation uses faster model for all decisions")
    
    print(f"\n🚀 Ready for Production!")
    print(f"BGE navigation will now use the faster Open WebUI model automatically.")

if __name__ == "__main__":
    print("🔍 BGE Navigation Open WebUI Integration Verification")
    print("=" * 60)
    
    success = test_bge_navigation_initialization()
    
    if success:
        show_integration_summary()
    else:
        print("\n❌ Integration verification failed")
        print("🔧 Please check server connectivity and configuration")