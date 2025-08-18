#!/usr/bin/env python3
"""
Test the updated client.py with extended timeouts
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.llm.client import chat_completion, chat_completion_with_vision
    
    print("=== Testing Updated Client with Extended Timeouts ===")
    
    # Test 1: Text-only
    print("\n🔄 Testing text completion...")
    response = chat_completion("What is 2+2? Answer with just the number.")
    print(f"✅ Text response: {response}")
    
    # Test 2: Vision with latest screenshot
    print("\n🔄 Testing vision completion...")
    captures_dir = Path("blender/captures")
    if captures_dir.exists():
        png_files = list(captures_dir.glob("*.png"))
        if png_files:
            latest = max(png_files, key=lambda f: f.stat().st_mtime)
            print(f"📸 Using screenshot: {latest.name}")
            
            response = chat_completion_with_vision(
                "What do you see in this image? Describe it in one sentence.",
                image_path=str(latest)
            )
            print(f"✅ Vision response: {response}")
        else:
            print("❌ No screenshots found")
    else:
        print("❌ No captures folder found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
