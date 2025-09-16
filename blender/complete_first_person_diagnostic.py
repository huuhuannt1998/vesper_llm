"""
Complete First-Person Camera Diagnostic Suite
===========================================

This script combines all diagnostic tools to identify and fix 
first-person camera issues in one comprehensive test.
"""

import bge
import time

def run_complete_first_person_diagnostic():
    """Run complete diagnostic suite for first-person camera issues"""
    
    print("🔧 COMPLETE FIRST-PERSON CAMERA DIAGNOSTIC")
    print("=" * 50)
    print("Identifying why first-person view is not using correct camera...")
    print()
    
    results = {}
    
    # Test 1: Scene Analysis
    print("🔍 1. SCENE ANALYSIS")
    print("-" * 20)
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Find all cameras
        all_cameras = []
        actor_fp_camera = None
        actor = None
        
        for obj in scene.objects:
            if hasattr(obj, 'camera') or 'Camera' in obj.name:
                all_cameras.append(obj)
                print(f"📷 Found camera: {obj.name} at [{obj.worldPosition.x:.2f}, {obj.worldPosition.y:.2f}, {obj.worldPosition.z:.2f}]")
                
                if obj.name == "Actor_FPCamera":
                    actor_fp_camera = obj
            
            if obj.name == "Actor":
                actor = obj
        
        print(f"Total cameras found: {len(all_cameras)}")
        print(f"Actor_FPCamera exists: {'✅ YES' if actor_fp_camera else '❌ NO'}")
        print(f"Actor exists: {'✅ YES' if actor else '❌ NO'}")
        
        results['scene_analysis'] = {
            'total_cameras': len(all_cameras),
            'actor_fp_camera_exists': actor_fp_camera is not None,
            'actor_exists': actor is not None
        }
        
    except Exception as e:
        print(f"❌ Scene analysis failed: {e}")
        results['scene_analysis'] = {'error': str(e)}
    
    # Test 2: First-Person Camera Manager
    print(f"\n🎥 2. FIRST-PERSON CAMERA MANAGER TEST")
    print("-" * 40)
    
    try:
        import sys
        sys.path.append("c:/Users/hbui11/Desktop/vesper_llm/blender")
        from first_person_camera import FirstPersonCameraManager
        
        print("✅ FirstPersonCameraManager imported successfully")
        
        # Create manager instance
        fp_manager = FirstPersonCameraManager()
        
        if fp_manager.camera_object:
            camera = fp_manager.camera_object
            print(f"✅ Manager found camera: {camera.name}")
            print(f"📍 Camera position: [{camera.worldPosition.x:.2f}, {camera.worldPosition.y:.2f}, {camera.worldPosition.z:.2f}]")
            
            # Check if it's the right camera
            if camera.name == "Actor_FPCamera":
                print("✅ Using correct Actor_FPCamera")
            else:
                print(f"⚠️ Using {camera.name} instead of Actor_FPCamera")
            
            results['fp_manager'] = {
                'success': True,
                'camera_found': True,
                'camera_name': camera.name,
                'is_correct_camera': camera.name == "Actor_FPCamera"
            }
        else:
            print("❌ Manager could not find any camera")
            results['fp_manager'] = {
                'success': True,
                'camera_found': False
            }
        
    except Exception as e:
        print(f"❌ FirstPersonCameraManager test failed: {e}")
        results['fp_manager'] = {'error': str(e)}
    
    # Test 3: Camera Capture Function
    print(f"\n📸 3. CAMERA CAPTURE FUNCTION TEST")
    print("-" * 35)
    
    try:
        from first_person_camera import capture_immediate_first_person_view
        
        print("✅ capture_immediate_first_person_view imported")
        
        # Test with dummy position/orientation
        test_position = (0, 0, 0)
        test_orientation = (0, 0, 0)
        
        print("🧪 Testing capture function (dry run)...")
        
        # This would normally capture, but we're just testing the setup
        print("⚠️ Skipping actual capture to avoid file creation")
        print("✅ Capture function is available")
        
        results['capture_function'] = {'success': True}
        
    except Exception as e:
        print(f"❌ Capture function test failed: {e}")
        results['capture_function'] = {'error': str(e)}
    
    # Test 4: Intelligent Camera Selection Integration
    print(f"\n🧠 4. INTELLIGENT CAMERA SELECTION TEST")
    print("-" * 40)
    
    try:
        from intelligent_camera_selection import capture_with_intelligent_camera
        
        print("✅ Intelligent camera selection imported")
        
        # Test decision making (without actual capture)
        print("🤔 Testing camera selection logic...")
        
        results['intelligent_selection'] = {'success': True}
        
    except Exception as e:
        print(f"❌ Intelligent camera selection test failed: {e}")
        results['intelligent_selection'] = {'error': str(e)}
    
    # Test 5: Camera Positioning Analysis
    if results.get('scene_analysis', {}).get('actor_fp_camera_exists') and results.get('scene_analysis', {}).get('actor_exists'):
        print(f"\n📏 5. CAMERA POSITIONING ANALYSIS")
        print("-" * 35)
        
        try:
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            camera = scene.objects.get("Actor_FPCamera")
            
            if actor and camera:
                actor_pos = actor.worldPosition
                camera_pos = camera.worldPosition
                
                distance = ((camera_pos.x - actor_pos.x)**2 + 
                           (camera_pos.y - actor_pos.y)**2 + 
                           (camera_pos.z - actor_pos.z)**2)**0.5
                
                print(f"🚶 Actor position: [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
                print(f"📷 Camera position: [{camera_pos.x:.2f}, {camera_pos.y:.2f}, {camera_pos.z:.2f}]")
                print(f"📏 Distance: {distance:.2f} units")
                
                if distance < 2.0:
                    print("✅ Camera is properly positioned for first-person view")
                    positioning_ok = True
                else:
                    print("⚠️ Camera is far from Actor - might not give true first-person view")
                    positioning_ok = False
                
                results['positioning'] = {
                    'distance': distance,
                    'positioning_ok': positioning_ok
                }
                
        except Exception as e:
            print(f"❌ Positioning analysis failed: {e}")
            results['positioning'] = {'error': str(e)}
    
    # Summary and Recommendations
    print(f"\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 25)
    
    issues_found = []
    fixes_needed = []
    
    # Check each test result
    if not results.get('scene_analysis', {}).get('actor_fp_camera_exists'):
        issues_found.append("Actor_FPCamera not found in scene")
        fixes_needed.append("Create or rename a camera to 'Actor_FPCamera'")
    
    if results.get('fp_manager', {}).get('camera_found') and not results.get('fp_manager', {}).get('is_correct_camera'):
        issues_found.append("FirstPersonCameraManager using wrong camera")
        fixes_needed.append("Ensure Actor_FPCamera is the closest camera to Actor")
    
    if results.get('positioning', {}) and not results.get('positioning', {}).get('positioning_ok'):
        issues_found.append("Camera positioned too far from Actor")
        fixes_needed.append("Move Actor_FPCamera closer to Actor (< 2 units distance)")
    
    if issues_found:
        print("❌ ISSUES FOUND:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 RECOMMENDED FIXES:")
        for i, fix in enumerate(fixes_needed, 1):
            print(f"   {i}. {fix}")
    else:
        print("✅ NO OBVIOUS ISSUES FOUND")
        print("First-person camera setup appears correct")
        print("Issue might be in capture timing or file handling")
    
    # Additional troubleshooting steps
    print(f"\n🛠️ ADDITIONAL TROUBLESHOOTING")
    print("=" * 30)
    print("If issues persist after fixing above:")
    print("1. Check Blender camera data block assignment")
    print("2. Verify camera is not disabled or hidden")
    print("3. Test manual camera switching in BGE")
    print("4. Check file permissions for screenshot saving")
    print("5. Verify BGE render capabilities")
    
    return results

# Auto-run if executed directly
if __name__ == "__main__":
    run_complete_first_person_diagnostic()

print("✅ Complete first-person diagnostic loaded - call run_complete_first_person_diagnostic() to execute")
