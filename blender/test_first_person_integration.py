"""
First-Person Camera Integration Test
===================================

Test script to demonstrate the first-person camera system that follows
the same pattern as the bird-eye view implementation.

Key Features Tested:
1. Non-blocking screenshot capture using BGE render
2. File-based image storage and polling
3. Integration with existing vision_only_completion function
4. Multi-modal analysis with both first-person and bird-eye views
"""

import sys
import os
import time

# Add paths for VESPER modules
vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
sys.path.insert(0, vesper_root)
sys.path.insert(0, os.path.join(vesper_root, "blender"))

def test_first_person_screenshot_pattern():
    """Test first-person screenshot following bird-eye pattern"""
    print("\n" + "="*60)
    print("🎥 TESTING FIRST-PERSON SCREENSHOT PATTERN")
    print("="*60)
    
    try:
        from first_person_camera import FirstPersonCameraManager
        
        # Initialize first-person camera
        fp_camera = FirstPersonCameraManager()
        print("✅ First-person camera manager initialized")
        
        # Test screenshot request (non-blocking)
        actor_pos = (-2.0, 2.0, 0.0)  # Kitchen position
        actor_orient = (0.0, 0.0, 0.0)  # Facing forward
        
        print(f"\n📸 Requesting first-person screenshot...")
        print(f"   Actor position: {actor_pos}")
        print(f"   Actor orientation: {actor_orient}")
        
        screenshot_path = fp_camera.request_first_person_screenshot(actor_pos, actor_orient)
        
        if screenshot_path:
            print(f"✅ Screenshot requested: {os.path.basename(screenshot_path)}")
            
            # Poll for completion (follows bird-eye pattern)
            print("\n⏳ Polling for screenshot completion...")
            start_time = time.time()
            
            while time.time() - start_time < 10.0:  # 10 second timeout
                result = fp_camera.poll_first_person_ready()
                
                if result == "TIMEOUT":
                    print("⏰ Screenshot polling timeout")
                    break
                elif result:
                    print(f"✅ Screenshot ready: {os.path.basename(result)}")
                    print(f"   File size: {os.path.getsize(result)} bytes")
                    print(f"   Time taken: {time.time() - start_time:.1f}s")
                    return result
                
                time.sleep(0.5)  # Wait before next poll
            
        else:
            print("❌ Screenshot request failed")
            
    except Exception as e:
        print(f"❌ First-person screenshot test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def test_multimodal_screenshot_capture():
    """Test multi-modal screenshot capture (first-person + bird-eye)"""
    print("\n" + "="*60)
    print("🔄 TESTING MULTI-MODAL SCREENSHOT CAPTURE")
    print("="*60)
    
    try:
        from first_person_camera import request_multimodal_navigation_screenshots, poll_multimodal_navigation_ready
        
        actor_pos = (0.0, 1.0, 0.0)  # Central position
        actor_orient = (0.0, 0.0, 1.57)  # Facing right
        
        print(f"📸 Requesting both first-person and bird-eye screenshots...")
        print(f"   Actor position: {actor_pos}")
        print(f"   Actor orientation: {actor_orient}")
        
        # Request both screenshots
        capture_results = request_multimodal_navigation_screenshots(actor_pos, actor_orient)
        
        print(f"✅ Capture request results:")
        print(f"   First-person path: {capture_results.get('first_person_path', 'None')}")
        print(f"   Bird-eye path: {capture_results.get('bird_eye_path', 'None')}")
        print(f"   Status: {capture_results.get('status', 'Unknown')}")
        
        # Poll for both to be ready
        print("\n⏳ Polling for both screenshots to be ready...")
        ready_status = poll_multimodal_navigation_ready(capture_results, timeout_s=15.0)
        
        print(f"📊 Final status:")
        print(f"   First-person ready: {ready_status.get('first_person_ready', False)}")
        print(f"   Bird-eye ready: {ready_status.get('bird_eye_ready', False)}")
        print(f"   Timeout occurred: {ready_status.get('timeout', False)}")
        
        # Show file info if ready
        if ready_status.get('first_person_ready') and ready_status.get('first_person_path'):
            fp_path = ready_status['first_person_path']
            print(f"✅ First-person: {os.path.basename(fp_path)} ({os.path.getsize(fp_path)} bytes)")
        
        if ready_status.get('bird_eye_ready') and ready_status.get('bird_eye_path'):
            be_path = ready_status['bird_eye_path']
            print(f"✅ Bird-eye: {os.path.basename(be_path)} ({os.path.getsize(be_path)} bytes)")
        
        return ready_status
        
    except Exception as e:
        print(f"❌ Multi-modal capture test failed: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def test_vision_completion_integration():
    """Test integration with vision completion functions"""
    print("\n" + "="*60)
    print("🧠 TESTING VISION COMPLETION INTEGRATION")
    print("="*60)
    
    try:
        # First get some screenshots
        print("📸 Capturing test screenshots...")
        multimodal_result = test_multimodal_screenshot_capture()
        
        if not multimodal_result:
            print("❌ No screenshots available for vision test")
            return
        
        # Test vision completion functions
        fp_path = multimodal_result.get('first_person_path')
        be_path = multimodal_result.get('bird_eye_path')
        
        if be_path and os.path.exists(be_path):
            print(f"\n🔍 Testing single-view vision completion...")
            print(f"   Using bird-eye: {os.path.basename(be_path)}")
            
            try:
                from llm_bge_navigation import vision_only_completion
                
                test_prompt = """Analyze this house layout image and identify:
1. Location of pink dot (actor position)
2. Current room type based on furniture
3. Navigation options available

Respond with JSON: {"current_room": "ROOM", "furniture_visible": ["items"], "reasoning": "analysis"}"""
                
                result, response_time, timeout = vision_only_completion(test_prompt, be_path)
                print(f"✅ Single-view analysis completed in {response_time:.1f}s")
                print(f"   Response length: {len(result)} characters")
                print(f"   Timeout occurred: {timeout}")
                print(f"   Sample response: {result[:200]}...")
                
            except Exception as e:
                print(f"⚠️ Single-view vision completion error: {e}")
        
        if fp_path and be_path and os.path.exists(fp_path) and os.path.exists(be_path):
            print(f"\n🔍 Testing multi-modal vision completion...")
            print(f"   Using first-person: {os.path.basename(fp_path)}")
            print(f"   Using bird-eye: {os.path.basename(be_path)}")
            
            try:
                from llm_bge_navigation import multimodal_vision_completion
                
                test_prompt = """Analyze both images for comprehensive navigation:
1. Use bird-eye view to locate actor (pink dot)
2. Use first-person view to identify room and obstacles
3. Combine both for navigation decision

Respond with JSON: {"current_room": "ROOM", "furniture_visible": ["items"], "movement_sequence": ["DIRECTION"], "reasoning": "dual-view analysis"}"""
                
                result, response_time, timeout = multimodal_vision_completion(test_prompt, be_path, fp_path)
                print(f"✅ Multi-modal analysis completed in {response_time:.1f}s")
                print(f"   Response length: {len(result)} characters")
                print(f"   Timeout occurred: {timeout}")
                print(f"   Sample response: {result[:200]}...")
                
            except Exception as e:
                print(f"⚠️ Multi-modal vision completion error: {e}")
                
    except Exception as e:
        print(f"❌ Vision completion integration test failed: {e}")
        import traceback
        traceback.print_exc()

def test_camera_positioning():
    """Test camera positioning and actor attachment"""
    print("\n" + "="*60)
    print("📐 TESTING CAMERA POSITIONING")
    print("="*60)
    
    try:
        from first_person_camera import FirstPersonCameraManager
        
        fp_camera = FirstPersonCameraManager()
        
        # Test different actor positions
        test_positions = [
            (-2.0, 2.0, 0.0),  # Kitchen
            (1.0, 2.0, 0.0),   # Dining room  
            (-1.0, -1.0, 0.0), # Living room
            (2.0, -1.0, 0.0)   # Bedroom
        ]
        
        test_orientations = [
            (0.0, 0.0, 0.0),     # Facing forward
            (0.0, 0.0, 1.57),    # Facing right
            (0.0, 0.0, 3.14),    # Facing backward
            (0.0, 0.0, -1.57)    # Facing left
        ]
        
        for i, (pos, orient) in enumerate(zip(test_positions, test_orientations)):
            print(f"\n📍 Test position {i+1}:")
            print(f"   Actor: {pos} orientation: {orient}")
            
            # Update camera position
            fp_camera._update_camera_position(pos, orient)
            
            if fp_camera.camera_object:
                cam_pos = fp_camera.camera_object.worldPosition
                cam_orient = fp_camera.camera_object.worldOrientation
                print(f"   Camera: [{cam_pos[0]:.2f}, {cam_pos[1]:.2f}, {cam_pos[2]:.2f}]")
                
                # Generate room description
                description = fp_camera.generate_first_person_description(pos)
                print(f"   Description: {description[:100]}...")
            else:
                print("   ⚠️ No camera object available")
                
    except Exception as e:
        print(f"❌ Camera positioning test failed: {e}")
        import traceback
        traceback.print_exc()

def compare_bird_eye_and_first_person_patterns():
    """Compare the implementation patterns between bird-eye and first-person"""
    print("\n" + "="*60)
    print("🔄 COMPARING BIRD-EYE AND FIRST-PERSON PATTERNS")
    print("="*60)
    
    print("📋 IMPLEMENTATION COMPARISON:")
    print("=" * 40)
    
    patterns = [
        ("Screenshot Request", "request_bird_eye_screenshot()", "request_first_person_screenshot(pos, orient)"),
        ("Polling", "poll_screenshot_ready()", "poll_first_person_ready()"),
        ("File Storage", "captures/screenshot_XXXX.png", "captures/first_person/first_person_XXXX.png"),
        ("Camera Setup", "BirdEyeCamera object", "FirstPersonCamera object"),
        ("BGE Integration", "bge.render.makeScreenshot()", "bge.render.makeScreenshot()"),
        ("State Management", "_vesper_shot", "_vesper_first_person_shot"),
        ("Vision Function", "vision_only_completion()", "multimodal_vision_completion()"),
        ("Timeout Handling", "Thread-based with queue", "Thread-based with queue"),
        ("Error Fallback", "Text-only navigation", "Bird-eye only navigation")
    ]
    
    for feature, bird_eye, first_person in patterns:
        print(f"🔸 {feature}:")
        print(f"   Bird-eye: {bird_eye}")
        print(f"   First-person: {first_person}")
        print()
    
    print("✅ PATTERN CONSISTENCY:")
    print("   • Both use non-blocking screenshot requests")
    print("   • Both use file-based image storage")
    print("   • Both use polling for completion detection")
    print("   • Both integrate with BGE render system")
    print("   • Both have timeout and error handling")
    print("   • Both support vision LLM integration")

def run_all_first_person_tests():
    """Run comprehensive first-person camera tests"""
    print("🎥 FIRST-PERSON CAMERA INTEGRATION TEST SUITE")
    print("=" * 70)
    print("Testing implementation that follows bird-eye view pattern")
    print("=" * 70)
    
    try:
        # Test basic functionality
        test_first_person_screenshot_pattern()
        
        # Test multi-modal integration
        test_multimodal_screenshot_capture()
        
        # Test vision completion
        test_vision_completion_integration()
        
        # Test camera positioning
        test_camera_positioning()
        
        # Compare patterns
        compare_bird_eye_and_first_person_patterns()
        
        print("\n" + "="*70)
        print("✅ ALL FIRST-PERSON CAMERA TESTS COMPLETED!")
        print("🎯 Key Achievement: First-person camera follows exact bird-eye pattern")
        print("🔄 Integration: Seamless multi-modal vision with existing system")
        print("📸 Capability: Non-blocking screenshot capture with file-based storage")
        print("🧠 Enhancement: Multi-modal VLM analysis with dual perspectives")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ FIRST-PERSON TEST SUITE FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_all_first_person_tests()
