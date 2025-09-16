#!/usr/bin/env python3
"""
Test BGE First-Person Camera Compatibility
=========================================

This test checks that the first-person camera system works properly in BGE
without trying to access non-existent scene attributes.
"""

import bge
import time
import os

def test_bge_scene_compatibility():
    """Test BGE scene object compatibility"""
    
    print("🧪 Testing BGE Scene Compatibility")
    print("=" * 40)
    
    try:
        scene = bge.logic.getCurrentScene()
        print(f"✅ BGE scene accessed: {type(scene)}")
        
        # Test what attributes the scene actually has
        print(f"📋 Scene attributes: {[attr for attr in dir(scene) if not attr.startswith('_')][:10]}...")
        
        # Check if render attribute exists (should NOT exist in BGE)
        if hasattr(scene, 'render'):
            print(f"⚠️ Scene has render attribute: {scene.render}")
        else:
            print("✅ Scene correctly has NO render attribute (BGE compatible)")
        
        # Test logic tic rate access (BGE compatible way to trigger updates)
        try:
            tic_rate = bge.logic.getLogicTicRate()
            print(f"✅ Logic tic rate accessed: {tic_rate}")
        except Exception as e:
            print(f"❌ Logic tic rate error: {e}")
        
        # Test screenshot capability
        try:
            test_path = os.path.join(os.path.dirname(__file__), "test_compatibility.png")
            result = bge.render.makeScreenshot(test_path)
            print(f"✅ makeScreenshot test: {result}")
            
            # Check if file was created
            time.sleep(0.2)
            if os.path.exists(test_path):
                size = os.path.getsize(test_path)
                print(f"✅ Screenshot file created: {size} bytes")
                os.remove(test_path)  # Cleanup
            else:
                print("⚠️ Screenshot file not created")
                
        except Exception as e:
            print(f"❌ Screenshot test error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ BGE compatibility test failed: {e}")
        return False

def test_first_person_camera_fix():
    """Test the fixed first-person camera system"""
    
    print("\n🎥 Testing Fixed First-Person Camera")
    print("=" * 40)
    
    try:
        # Import the fixed system
        from first_person_camera import get_first_person_camera
        
        fp_camera = get_first_person_camera()
        print("✅ First-person camera system imported")
        
        # Test camera setup
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        
        if actor:
            print(f"✅ Actor found at: {[actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]}")
            
            # Test screenshot request (should not fail with render attribute error)
            actor_pos = (actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z)
            shot_path = fp_camera.request_first_person_screenshot(actor_pos, (0, 0, 0))
            
            if shot_path:
                print(f"✅ Screenshot request successful: {os.path.basename(shot_path)}")
                print("💡 No 'render' attribute errors - BGE compatibility fixed!")
                return True
            else:
                print("❌ Screenshot request failed")
                return False
        else:
            print("❌ No Actor found")
            return False
            
    except Exception as e:
        print(f"❌ First-person camera test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("🔧 BGE COMPATIBILITY TEST SUITE")
    print("=" * 50)
    
    # Test 1: BGE Scene Compatibility
    scene_ok = test_bge_scene_compatibility()
    
    # Test 2: First-Person Camera Fix
    camera_ok = test_first_person_camera_fix()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"🔧 BGE Scene Compatibility: {'✅ PASS' if scene_ok else '❌ FAIL'}")
    print(f"🎥 First-Person Camera Fix: {'✅ PASS' if camera_ok else '❌ FAIL'}")
    
    if scene_ok and camera_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 BGE compatibility issues resolved")
        print("💡 First-person camera should work without 'render' errors")
    else:
        print("\n❌ SOME TESTS FAILED")
        print("💡 Check BGE compatibility issues")

if __name__ == "__main__":
    main()
