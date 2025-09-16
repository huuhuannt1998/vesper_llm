#!/usr/bin/env python3
"""
Test script for BGE camera switching fix.
Run this in the Blender Game Engine to test camera functionality.
"""

import bge
import time
import os
import sys

def test_camera_switching():
    """Test camera switching functionality in BGE"""
    
    print("🧪 Testing BGE Camera Switching Fix")
    print("=" * 50)
    
    scene = bge.logic.getCurrentScene()
    
    # Find cameras
    bird_eye_camera = None
    first_person_camera = None
    
    for obj in scene.objects:
        if obj.name == "BirdEyeCamera":
            bird_eye_camera = obj
        elif obj.name == "Actor_FPCamera":
            first_person_camera = obj
    
    print(f"🔍 Found cameras:")
    print(f"   Bird-eye: {'✅' if bird_eye_camera else '❌'} {bird_eye_camera.name if bird_eye_camera else 'Not found'}")
    print(f"   First-person: {'✅' if first_person_camera else '❌'} {first_person_camera.name if first_person_camera else 'Not found'}")
    
    if not bird_eye_camera or not first_person_camera:
        print("❌ Required cameras not found!")
        return False
    
    original_camera = scene.active_camera
    print(f"🎬 Original active camera: {original_camera.name if original_camera else 'None'}")
    
    # Test 1: Switch to bird-eye camera
    print("\n📋 Test 1: Switch to Bird-eye Camera")
    scene.active_camera = bird_eye_camera
    time.sleep(0.1)
    
    if scene.active_camera == bird_eye_camera:
        print("✅ Bird-eye camera switch successful")
        
        # Test bird-eye screenshot
        bird_eye_path = os.path.join(os.getcwd(), "test_bird_eye.png")
        try:
            screenshot_result = bge.render.makeScreenshot(bird_eye_path)
            time.sleep(0.2)
            
            if os.path.exists(bird_eye_path) and os.path.getsize(bird_eye_path) > 0:
                file_size = os.path.getsize(bird_eye_path)
                print(f"✅ Bird-eye screenshot captured: {file_size} bytes")
            else:
                print(f"❌ Bird-eye screenshot failed (result: {screenshot_result})")
        except Exception as e:
            print(f"❌ Bird-eye screenshot error: {e}")
    else:
        print("❌ Bird-eye camera switch failed")
    
    # Test 2: Switch to first-person camera
    print("\n📋 Test 2: Switch to First-person Camera")
    scene.active_camera = first_person_camera
    time.sleep(0.1)
    
    if scene.active_camera == first_person_camera:
        print("✅ First-person camera switch successful")
        
        # Test first-person screenshot
        first_person_path = os.path.join(os.getcwd(), "test_first_person.png")
        try:
            screenshot_result = bge.render.makeScreenshot(first_person_path)
            time.sleep(0.2)
            
            if os.path.exists(first_person_path) and os.path.getsize(first_person_path) > 0:
                file_size = os.path.getsize(first_person_path)
                print(f"✅ First-person screenshot captured: {file_size} bytes")
            else:
                print(f"❌ First-person screenshot failed (result: {screenshot_result})")
        except Exception as e:
            print(f"❌ First-person screenshot error: {e}")
    else:
        print("❌ First-person camera switch failed")
    
    # Test 3: Multiple rapid switches
    print("\n📋 Test 3: Rapid Camera Switches")
    success_count = 0
    total_tests = 5
    
    for i in range(total_tests):
        # Switch to bird-eye
        scene.active_camera = bird_eye_camera
        time.sleep(0.05)
        
        if scene.active_camera == bird_eye_camera:
            # Switch to first-person
            scene.active_camera = first_person_camera
            time.sleep(0.05)
            
            if scene.active_camera == first_person_camera:
                success_count += 1
                print(f"✅ Rapid switch test {i+1}: Success")
            else:
                print(f"❌ Rapid switch test {i+1}: Failed at first-person")
        else:
            print(f"❌ Rapid switch test {i+1}: Failed at bird-eye")
    
    print(f"📊 Rapid switch success rate: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
    
    # Restore original camera
    if original_camera:
        scene.active_camera = original_camera
        print(f"🔄 Restored original camera: {original_camera.name}")
    
    print("\n" + "=" * 50)
    print("🧪 Camera switching test complete!")
    
    # Overall result
    all_cameras_found = bird_eye_camera and first_person_camera
    camera_switching_works = success_count > 0
    
    if all_cameras_found and camera_switching_works:
        print("✅ OVERALL: Camera system working!")
        return True
    else:
        print("❌ OVERALL: Camera system has issues!")
        return False

def test_bge_runtime_detection():
    """Test BGE runtime detection"""
    
    print("\n🔍 Testing BGE Runtime Detection")
    print("-" * 30)
    
    try:
        import bge
        scene = bge.logic.getCurrentScene()
        print("✅ BGE modules imported successfully")
        print(f"✅ Scene accessible: {scene}")
        print("✅ BGE runtime detected correctly")
        return True
    except Exception as e:
        print(f"❌ BGE runtime detection failed: {e}")
        return False

if __name__ == "__main__":
    print("🎮 BGE Camera Fix Test Suite")
    print("=" * 60)
    
    # Test BGE runtime detection
    bge_detected = test_bge_runtime_detection()
    
    if bge_detected:
        # Test camera switching
        camera_test_passed = test_camera_switching()
        
        if camera_test_passed:
            print("\n🎉 ALL TESTS PASSED! Camera system is working correctly.")
            sys.exit(0)
        else:
            print("\n⚠️ CAMERA TESTS FAILED! Check camera setup and BGE configuration.")
            sys.exit(1)
    else:
        print("\n❌ BGE DETECTION FAILED! This script must be run in Blender Game Engine.")
        sys.exit(1)
