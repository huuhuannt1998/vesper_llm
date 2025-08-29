#!/usr/bin/env python3
"""
Test BGE Navigation System after Syntax Fixes
Quick validation script for Windows compatibility
"""

import os
import sys
import subprocess
import time

def test_syntax_validation():
    """Test Python syntax in BGE navigation file"""
    print("🔍 Testing BGE Navigation Syntax...")
    
    bge_file = r"C:\Users\hbui11\Desktop\vesper_llm\blender\llm_bge_navigation.py"
    
    if not os.path.exists(bge_file):
        print(f"❌ BGE navigation file not found: {bge_file}")
        return False
    
    try:
        # Test Python syntax compilation
        with open(bge_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, bge_file, 'exec')
        print("✅ BGE Navigation syntax validation PASSED")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error in BGE Navigation:")
        print(f"   Line {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Compilation Error: {e}")
        return False

def test_timeout_import():
    """Test Windows-compatible timeout imports"""
    print("🔍 Testing Windows Threading Timeout...")
    
    try:
        import threading
        import queue
        import time
        
        # Test timeout mechanism
        result_queue = queue.Queue()
        
        def test_worker():
            time.sleep(0.1)  # Quick test
            result_queue.put(('success', 'test_result'))
        
        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()
        
        # Test timeout with short window
        try:
            result_type, result_data = result_queue.get(timeout=1.0)
            if result_type == 'success':
                print("✅ Windows threading timeout mechanism WORKING")
                return True
        except queue.Empty:
            print("❌ Timeout mechanism failed")
            return False
            
    except Exception as e:
        print(f"❌ Threading import error: {e}")
        return False

def check_evaluation_system():
    """Check if evaluation system is ready"""
    print("🔍 Checking Evaluation System...")
    
    eval_files = [
        r"C:\Users\hbui11\Desktop\vesper_llm\evaluation\log_analyzer.py",
        r"C:\Users\hbui11\Desktop\vesper_llm\evaluation\run_evaluation.py",
        r"C:\Users\hbui11\Desktop\vesper_llm\evaluation\test_metrics.py"
    ]
    
    all_exist = True
    for file_path in eval_files:
        if os.path.exists(file_path):
            print(f"✅ {os.path.basename(file_path)} - Found")
        else:
            print(f"❌ {os.path.basename(file_path)} - Missing")
            all_exist = False
    
    return all_exist

def check_backend_status():
    """Check if backend server is accessible"""
    print("🔍 Checking Backend Server...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"⚠️ Backend server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("⚠️ Backend server not running (this is okay for BGE testing)")
        return False
    except Exception as e:
        print(f"⚠️ Backend check failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 VESPER BGE Navigation Validation")
    print("=" * 50)
    
    tests = [
        ("Syntax Validation", test_syntax_validation),
        ("Threading Timeout", test_timeout_import),
        ("Evaluation System", check_evaluation_system),
        ("Backend Status", check_backend_status)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("🎯 VALIDATION SUMMARY:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed >= 3:  # Backend optional
        print("\n🎉 BGE Navigation System READY for testing!")
        print("\n📋 Next Steps:")
        print("1. Open Blender with house.blend")
        print("2. Press P to run BGE navigation")
        print("3. Run evaluation monitoring:")
        print("   python evaluation/run_evaluation.py")
        print("4. Monitor real-time metrics capture")
    else:
        print("\n⚠️ Some issues found - check failed tests above")

if __name__ == "__main__":
    main()
