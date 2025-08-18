"""
Simple test to check BGE screenshot functionality
"""
import bge
import os
import time

def test_bge_screenshot():
    """Test basic BGE screenshot functionality"""
    try:
        # Get current scene
        scene = bge.logic.getCurrentScene()
        print(f"Current scene: {scene}")
        
        # Test basic screenshot
        test_path = "C:\\Users\\hbui11\\Desktop\\vesper_llm\\blender\\test_screenshot.png"
        print(f"Testing screenshot to: {test_path}")
        
        # Try screenshot
        result = bge.render.makeScreenshot(test_path)
        print(f"makeScreenshot result: {result}")
        
        # Wait and check
        time.sleep(2)
        if os.path.exists(test_path):
            size = os.path.getsize(test_path)
            print(f"SUCCESS: Screenshot created, size: {size} bytes")
        else:
            print("FAILED: Screenshot file not found")
            
        # Check what functions are available
        print(f"BGE render functions: {dir(bge.render)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bge_screenshot()
