#!/usr/bin/env python3
"""
Test the backend LLM client to see if it works.
"""
import sys
import os

# Add the backend path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.llm.client import chat_completion
    
    print("🧪 Testing Backend LLM Client")
    print("=" * 40)
    
    # Enable debug mode
    os.environ['LLM_DEBUG'] = '1'
    
    result = chat_completion(
        system="You are a helpful assistant.",
        user="Say 'Hello from backend!' in one short sentence.",
        max_tokens=20
    )
    
    print(f"✅ SUCCESS: {result}")
    
except Exception as e:
    print(f"❌ Backend LLM client failed: {e}")
    import traceback
    traceback.print_exc()
