#!/usr/bin/env python3
"""
Test the LLM client directly to debug the connection issue
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from backend.app.llm.client import chat_completion, BASE_URL, API_KEY, MODEL
    
    print("✅ Successfully imported LLM client")
    print(f"📍 Base URL: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:10]}...")
    print(f"🤖 Model: {MODEL}")
    
    print("\n🧪 Testing LLM connection...")
    response = chat_completion("You are a test AI.", "Say OK", 5)
    print(f"✅ LLM Response: {response}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
