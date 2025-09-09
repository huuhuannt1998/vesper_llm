# Proper Motion Sensor Test with Docker Backend
# This test ensures Docker is running and creates motion sensors correctly

import bpy
from mathutils import Vector

def check_docker_services():
    """Check if required Docker services are running"""
    print("🐳 Checking Docker services...")
    
    try:
        from vesper_smart_home import device_manager
        
        # Check service health
        health = device_manager.check_services_health()
        
        print("📊 Docker Services Status:")
        all_healthy = True
        for service, status in health.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {service}: {'Running' if status else 'Down'}")
            if not status:
                all_healthy = False
        
        if all_healthy:
            print("🎉 All Docker services are running!")
            return True
        else:
            print("⚠️ Some Docker services are down")
            print("\n💡 To start Docker services:")
            print("   1. Open PowerShell/Terminal")
            print("   2. Navigate to: C:\\Users\\hbui11\\Desktop\\vesper_llm\\virtual-interaction")
            print("   3. Run: docker-compose -f docker-compose.casas.yml up -d")
            print("   4. Wait 30-60 seconds for containers to start")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Docker services: {e}")
        return False

def test_motion_sensor_with_docker():
    """Test motion sensor creation with proper Docker backend"""
    
    print("\n🎯 Testing Motion Sensor with Docker Backend")
    print("=" * 60)
    
    # Clear existing test objects
    for obj in bpy.data.objects:
        if ("docker_test" in obj.name.lower() or 
            "motion_docker_test" in obj.name.lower() or
            "detectionarea_docker_test" in obj.name.lower()):
            bpy.data.objects.remove(obj, do_unlink=True)
    
    try:
        from vesper_smart_home import device_manager
        
        # Test parameters
        sensor_id = "DOCKER_TEST_01"
        position = Vector((2, 2, 2.0))
        room = "living_room"
        orientation = 0.0  # North facing
        
        print(f"📋 Test Parameters:")
        print(f"   🆔 Sensor ID: {sensor_id}")
        print(f"   📍 Position: {position}")
        print(f"   🏠 Room: {room}")
        print(f"   🧭 Orientation: {orientation}°")
        
        print(f"\n🚀 Creating motion sensor with Docker backend...")
        
        # This will create the Docker container AND the visual elements
        success = device_manager.add_motion_sensor(sensor_id, room, position, orientation)
        
        if success:
            print(f"\n🎉 Motion sensor created successfully!")
            
            # Verify what was created
            sensor_obj_name = f"Motion_{sensor_id}"
            detection_obj_name = f"DetectionArea_{sensor_id}"
            
            sensor_obj = bpy.data.objects.get(sensor_obj_name)
            detection_obj = bpy.data.objects.get(detection_obj_name)
            
            print(f"\n📦 Created Objects:")
            
            if sensor_obj:
                print(f"   ✅ Sensor object: {sensor_obj.name}")
                print(f"      📍 Location: {sensor_obj.location}")
                print(f"      🎨 Materials: {len(sensor_obj.data.materials)}")
                print(f"      🏷️ Device ID: {sensor_obj.get('vesper_device_id', 'Not set')}")
            else:
                print(f"   ❌ Sensor object not found: {sensor_obj_name}")
            
            if detection_obj:
                print(f"   ✅ Detection area: {detection_obj.name}")
                print(f"      📍 Location: {detection_obj.location}")
                print(f"      🔗 Parented: {detection_obj.parent is not None}")
                if detection_obj.parent:
                    print(f"      👨‍👧 Parent: {detection_obj.parent.name}")
                print(f"      🎨 Materials: {len(detection_obj.data.materials)}")
                print(f"      👁️ Display type: {detection_obj.display_type}")
                
                # Make it selected and visible
                bpy.context.view_layer.objects.active = detection_obj
                detection_obj.select_set(True)
                sensor_obj.select_set(True) if sensor_obj else None
                
                # Check visibility settings
                detection_obj.hide_viewport = False
                detection_obj.hide_set(False)
                
            else:
                print(f"   ❌ Detection area not found: {detection_obj_name}")
            
            # Check device registry
            if sensor_id in device_manager.device_registry:
                registry_entry = device_manager.device_registry[sensor_id]
                print(f"\n📊 Device Registry Entry:")
                for key, value in registry_entry.items():
                    print(f"      {key}: {value}")
            
            return sensor_obj, detection_obj
            
        else:
            print(f"❌ Motion sensor creation failed")
            print(f"   💡 This is expected if Docker containers are not running")
            return None, None
            
    except Exception as e:
        print(f"❌ Error during motion sensor test: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_detection_area_visibility():
    """Test detection area visibility settings"""
    print(f"\n👁️ Testing Detection Area Visibility")
    print("=" * 50)
    
    # Find all detection areas
    detection_areas = [obj for obj in bpy.data.objects if obj.name.startswith("DetectionArea_")]
    
    if not detection_areas:
        print("❌ No detection areas found to test")
        return
    
    print(f"🔍 Found {len(detection_areas)} detection areas")
    
    for detection_obj in detection_areas:
        print(f"\n📐 Testing: {detection_obj.name}")
        
        # Check basic properties
        print(f"   📍 Location: {detection_obj.location}")
        print(f"   👁️ Hidden in viewport: {detection_obj.hide_viewport}")
        print(f"   🙈 Hidden generally: {detection_obj.hide_get()}")
        print(f"   🎭 Display type: {detection_obj.display_type}")
        print(f"   🎨 Material count: {len(detection_obj.data.materials)}")
        print(f"   🔗 Has parent: {detection_obj.parent is not None}")
        
        # Make sure it's visible
        detection_obj.hide_viewport = False
        detection_obj.hide_set(False)
        detection_obj.select_set(True)
        
        # Check material
        if detection_obj.data.materials:
            mat = detection_obj.data.materials[0]
            print(f"   🎨 Material: {mat.name}")
            if mat.use_nodes and mat.node_tree:
                nodes = mat.node_tree.nodes
                bsdf = nodes.get("Principled BSDF")
                if bsdf:
                    base_color = bsdf.inputs[0].default_value
                    print(f"   🎨 Base color: {base_color[:3]}")

def run_complete_test():
    """Run complete test sequence"""
    print("🧪 COMPLETE MOTION SENSOR TEST")
    print("=" * 70)
    
    # Step 1: Check Docker
    docker_ok = check_docker_services()
    
    if not docker_ok:
        print("\n⚠️ Docker services not running - motion sensor creation will fail")
        print("   Start Docker services first, then run this test again")
        return False
    
    # Step 2: Test motion sensor creation
    sensor_obj, detection_obj = test_motion_sensor_with_docker()
    
    # Step 3: Test visibility
    test_detection_area_visibility()
    
    # Step 4: Final instructions
    if detection_obj:
        print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print(f"\n🔍 You should now see:")
        print(f"   • Red sphere (sensor) at {sensor_obj.location if sensor_obj else 'position'}")
        print(f"   • Blue triangle (detection area) extending north")
        print(f"   • Triangle: 5 meters long, 120° wide")
        print(f"   • Both objects selected in viewport")
        
        print(f"\n🎮 Test movement synchronization:")
        print(f"   1. Select the red sensor sphere")
        print(f"   2. Press 'G' to grab/move")
        print(f"   3. Blue triangle should move with sensor")
        print(f"   4. Press 'R' + 'Z' to rotate sensor")
        print(f"   5. Triangle should rotate with sensor")
        
        return True
    else:
        print(f"\n❌ TEST FAILED - No detection area created")
        return False

# Run the complete test
if __name__ == "__main__":
    run_complete_test()

print(f"\n💡 Individual test functions:")
print(f"   check_docker_services()           # Check Docker status")
print(f"   test_motion_sensor_with_docker()  # Test sensor creation")
print(f"   test_detection_area_visibility()  # Check visibility")
print(f"   run_complete_test()               # Run all tests")
