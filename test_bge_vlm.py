#!/usr/bin/env python3
"""
Test BGE Navigation VLM functionality with extended timeouts
"""
import os
import sys
from pathlib import Path

# Setup path like BGE script does
def setup_bge_path():
    current_dir = Path(__file__).parent
    backend_path = current_dir / "backend"
    
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    # Load .env if available
    env_path = current_dir / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            print(f"✅ Loaded .env from {env_path}")
        except ImportError:
            print("⚠️ dotenv not available, parsing manually")
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    return True

def test_bge_vlm_navigation():
    """Test VLM navigation like BGE would do"""
    if not setup_bge_path():
        return False
    
    try:
        from app.llm.client import chat_completion_with_vision
        
        # Find latest screenshot
        captures_dir = Path("blender/captures")
        if not captures_dir.exists():
            print("❌ No captures folder")
            return False
        
        png_files = list(captures_dir.glob("*.png"))
        if not png_files:
            print("❌ No screenshots")
            return False
        
        latest = max(png_files, key=lambda f: f.stat().st_mtime)
        print(f"📸 Using: {latest.name}")
        
        # BGE-style navigation prompt
        prompt = """You are helping navigate through a house. Based on this bird's eye view, 
        what direction should I move to get to the kitchen? 
        Reply with only: FORWARD, BACKWARD, LEFT, or RIGHT."""
        
        print("🔄 Testing VLM navigation (with 180s timeout)...")
        
        response = chat_completion_with_vision(prompt, image_path=str(latest))
        
        print(f"✅ VLM Navigation Response: {response}")
        
        # Validate response
        valid_directions = ['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT']
        if any(direction in response.upper() for direction in valid_directions):
            print("✅ Valid navigation direction received")
            return True
        else:
            print("⚠️ Response doesn't contain clear direction")
            return False
            
    except Exception as e:
        print(f"❌ BGE VLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== BGE VLM Navigation Test ===")
    test_bge_vlm_navigation()
