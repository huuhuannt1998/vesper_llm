#!/usr/bin/env python3
"""
Quick test for BGE first-person camera fix.
This will test the enhanced first-person camera capture without offscreen rendering.
"""

import bge
import time
import os

def test_first_person_capture():
    """Test the fixed first-person camera capture system"""
    
    print("🧪 Testing Fixed First-Person Camera Capture")
    print("=" * 50)
    
    try:
        # Import the fixed first-person camera system
        import sys
        
        # Add blender directory to path if not already there
        blender_dir = os.path.dirname(os.path.abspath(__file__))
        if blender_dir not in sys.path:
            sys.path.append(blender_dir)
        
        from first_person_camera import get_first_person_camera
        
        # Get the camera manager
        fp_camera = get_first_person_camera()
        
        print("✅ First-person camera system imported successfully")
        
        # Test camera setup
        scene = bge.logic.getCurrentScene()
        
        # Find Actor
        actor = scene.objects.get("Actor")
        if not actor:
            print("❌ No Actor found in scene")
            return False
        
        print(f"✅ Actor found at: {[actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]}")
        
        # Test screenshot capture (this should now work without offscreen errors)
        print("📸 Testing first-person screenshot capture...")
        
        actor_pos = (actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z)
        actor_orient = (0, 0, 0)  # Default orientation
        
        # Request screenshot
        shot_path = fp_camera.request_first_person_screenshot(actor_pos, actor_orient)
        
        if shot_path:
            print(f"✅ Screenshot request successful: {os.path.basename(shot_path)}")
            
            # Poll for completion
            start_time = time.time()
            timeout = 10.0
            
            while time.time() - start_time < timeout:
                result = fp_camera.poll_first_person_ready()
                
                if result == "TIMEOUT":
                    print("⏰ Screenshot timed out")
                    break
                elif result:
                    print(f"✅ Screenshot completed: {os.path.basename(result)}")
                    return True
                
                time.sleep(0.1)
            
            print("⚠️ Screenshot polling timed out")
            return False
        else:
            print("❌ Screenshot request failed")
            return False
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    if test_first_person_capture():
        print("\n🎉 First-person camera fix test PASSED!")
        print("💡 The 'bytes-like object is required' error should be resolved")
    else:
        print("\n❌ First-person camera fix test FAILED")
        print("💡 May need additional debugging")

if __name__ == "__main__":
    main()
