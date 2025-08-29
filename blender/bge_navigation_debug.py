#!/usr/bin/env python3
"""
BGE Navigation with Robust Import Handling
This version handles import failures gracefully and provides detailed error reporting
"""

import bge
import time
import sys
import os

def setup_python_path():
    """Add VESPER project to Python path for imports"""
    vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
    if vesper_root not in sys.path:
        sys.path.insert(0, vesper_root)
        print(f"🔧 Added to Python path: {vesper_root}")
    
    return vesper_root

def test_imports():
    """Test all required imports and report status"""
    print("🔍 Testing imports...")
    
    import_results = {}
    
    # Test basic Python modules
    basic_modules = ['json', 'base64', 'threading', 'queue', 'traceback']
    for module in basic_modules:
        try:
            __import__(module)
            import_results[module] = "✅"
            print(f"   ✅ {module}")
        except Exception as e:
            import_results[module] = f"❌ {e}"
            print(f"   ❌ {module}: {e}")
    
    # Test backend imports
    backend_modules = [
        'backend.app.llm.client',
        'backend.app.llm.few_shot_navigation'
    ]
    
    for module in backend_modules:
        try:
            __import__(module)
            import_results[module] = "✅"
            print(f"   ✅ {module}")
        except Exception as e:
            import_results[module] = f"❌ {e}"
            print(f"   ❌ {module}: {e}")
    
    return import_results

def create_debug_log(results, vesper_root):
    """Create a debug log with all test results"""
    try:
        log_dir = os.path.join(vesper_root, "blender", "evaluation_logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        debug_log_path = os.path.join(log_dir, f"bge_debug_{int(time.time())}.txt")
        
        with open(debug_log_path, 'w') as f:
            f.write(f"BGE Navigation Debug Log - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("PYTHON ENVIRONMENT:\n")
            f.write(f"Python version: {sys.version}\n")
            f.write(f"Python executable: {sys.executable}\n")
            f.write("\nPython path:\n")
            for i, path in enumerate(sys.path):
                f.write(f"  {i+1}. {path}\n")
            
            f.write("\nIMPORT TEST RESULTS:\n")
            for module, result in results.items():
                f.write(f"  {module}: {result}\n")
            
            f.write("\nBGE SCENE INFO:\n")
            try:
                scene = bge.logic.getCurrentScene()
                f.write(f"Scene name: {scene.name}\n")
                f.write(f"Objects count: {len(scene.objects)}\n")
                f.write("Objects list:\n")
                for obj in scene.objects:
                    f.write(f"  - {obj.name}\n")
                
                actor = scene.objects.get("Actor")
                if actor:
                    f.write(f"Actor found at: {actor.worldPosition}\n")
                else:
                    f.write("Actor object NOT FOUND\n")
                    
            except Exception as e:
                f.write(f"Error getting scene info: {e}\n")
        
        print(f"✅ Debug log created: {os.path.basename(debug_log_path)}")
        return debug_log_path
        
    except Exception as e:
        print(f"❌ Failed to create debug log: {e}")
        return None

def main():
    """Main BGE function with comprehensive diagnostics"""
    print("=" * 60)
    print("🚀 BGE NAVIGATION DIAGNOSTIC VERSION")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Step 1: Setup Python path
        vesper_root = setup_python_path()
        
        # Step 2: Test BGE scene
        print("\n🎬 Testing BGE scene...")
        scene = bge.logic.getCurrentScene()
        print(f"   Scene: {scene.name}")
        print(f"   Objects: {len(scene.objects)}")
        
        # Step 3: Check for Actor
        print("\n🎯 Checking for Actor object...")
        actor = scene.objects.get("Actor")
        if actor:
            print(f"   ✅ Actor found at: {actor.worldPosition}")
        else:
            print("   ❌ Actor object NOT FOUND!")
            print("   Available objects:")
            for obj in scene.objects:
                print(f"      • {obj.name}")
        
        # Step 4: Test imports
        print("\n📦 Testing imports...")
        import_results = test_imports()
        
        # Step 5: Create debug log
        print("\n📝 Creating debug log...")
        log_path = create_debug_log(import_results, vesper_root)
        
        # Step 6: Attempt to initialize metrics logger if imports work
        print("\n📊 Testing metrics logger...")
        backend_imports_ok = all("✅" in str(result) for module, result in import_results.items() if module.startswith('backend'))
        
        if backend_imports_ok:
            print("   Backend imports successful, attempting metrics initialization...")
            try:
                # Try to import and initialize the real metrics logger
                from blender.llm_bge_navigation import VESPERMetricsLogger
                metrics = VESPERMetricsLogger()
                print("   ✅ VESPERMetricsLogger initialized successfully!")
                
                # Test logging a simple entry
                metrics.log_session_start("test_task")
                print("   ✅ Test log entry created")
                
            except Exception as e:
                print(f"   ❌ Metrics logger failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   ⚠️ Backend imports failed, skipping metrics test")
        
        print("\n" + "=" * 60)
        print("🎯 DIAGNOSTIC COMPLETED")
        if log_path:
            print(f"📄 Debug log saved: {os.path.basename(log_path)}")
        print("Check console output above for detailed results")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

# Entry point for BGE
if __name__ == "__main__":
    main()
