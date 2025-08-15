#!/usr/bin/env python3
"""
Simulate the exact import and test that happens in the Blender addon
"""
import sys
import os

# Add the exact paths that the Blender addon would use
vesper_path = r"c:\Users\hbui11\Desktop\vesper_llm"
backend_path = os.path.join(vesper_path, "backend")

if vesper_path not in sys.path:
    sys.path.insert(0, vesper_path)

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Change to vesper path like the addon does
original_cwd = os.getcwd()
os.chdir(vesper_path)

try:
    print("🔍 DEBUG: Importing LLM client...")
    from backend.app.llm.client import chat_completion, BASE_URL
    from backend.app.llm.visual_decider import decide_with_vision
    print(f"🔍 DEBUG: Import successful, BASE_URL = {BASE_URL}")
    
    # Test LLM client functionality
    print("🔍 DEBUG: Testing LLM client functionality with 5 second timeout...")
    import time
    start_time = time.time()
    test_response = chat_completion("You are a test AI.", "Say OK", 5)
    end_time = time.time()
    print(f"✅ LLM Visual System: Connected to LLM client (took {end_time - start_time:.2f}s)")
    print(f"📝 Response: '{test_response}'")
    
except Exception as e:
    print(f"⚠️ LLM Visual System: LLM client unavailable - {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # Restore original working directory
    os.chdir(original_cwd)
