"""
VESPER BGE Motion Detection Script
=================================

This script enables motion detection in the Blender Game Engine (BGE/UPBGE).

SETUP INSTRUCTIONS:
1. Copy this entire script
2. In Blender, go to Text Editor 
3. Create a new text block and paste this script
4. Name the text block "bge_motion_detection.py"
5. Add an Empty object to your scene
6. Add Logic Bricks to the Empty:
   - Always Sensor (Pulse: OFF, Frequency: 0)
   - Python Controller → Script: bge_motion_detection.py → main
7. Make sure you have motion sensors and an "Actor" object in your scene
8. Press P to start the game engine

The system will automatically detect when the Actor moves within range of motion sensors
and update the visual detection areas in real-time.
"""

def main():
    """Main BGE motion detection function - call from Always sensor"""
    try:
        import bge
        from mathutils import Vector
        import time
        import sys
        import os
        
        # Get current scene and controller
        scene = bge.logic.getCurrentScene()
        controller = bge.logic.getCurrentController()
        owner = controller.owner
        
        # Initialize device manager if not already done
        if not hasattr(scene, 'vesper_device_manager'):
            try:
                # Try to import the device manager from the addon
                addon_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "UPBGE", "Blender", "4.4", "scripts", "addons", "vesper_smart_home")
                if addon_path not in sys.path:
                    sys.path.append(addon_path)
                
                # Import and initialize device manager
                try:
                    from __init__ import device_manager
                    scene.vesper_device_manager = device_manager
                    print("🎮 BGE: VESPER device manager imported successfully")
                except ImportError:
                    print("⚠️ BGE: Could not import VESPER device manager - using basic detection")
                    scene.vesper_device_manager = None
                
            except Exception as e:
                print(f"⚠️ BGE: Failed to initialize device manager: {e}")
                scene.vesper_device_manager = None
        
        # Simple motion detection if device manager not available
        if scene.vesper_device_manager is None:
            simple_motion_detection(scene)
        else:
            # Use full VESPER motion detection system
            device_manager = scene.vesper_device_manager
            if hasattr(device_manager, 'update_motion_detection'):
                device_manager.update_motion_detection()
        
        # Update frame counter for debug output
        if not hasattr(scene, 'motion_frame_counter'):
            scene.motion_frame_counter = 0
        
        scene.motion_frame_counter += 1
        
        # Debug output every 5 seconds (300 frames at 60fps)
        if scene.motion_frame_counter % 300 == 0:
            try:
                actor = scene.objects.get("Actor")
                if actor:
                    pos = actor.worldPosition
                    print(f"🎭 BGE Actor position: [{pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f}]")
                
                # Count motion sensors
                motion_sensors = [obj for obj in scene.objects if obj.name.startswith("Motion_")]
                print(f"🎮 BGE Motion Detection: {len(motion_sensors)} sensors active")
                
            except Exception as e:
                print(f"⚠️ BGE: Status check error: {e}")
    
    except Exception as e:
        print(f"❌ BGE: Motion detection script error: {e}")

def simple_motion_detection(scene):
    """Enhanced motion detection when full VESPER system is not available"""
    try:
        # Get Actor object
        actor = scene.objects.get("Actor")
        if not actor:
            return
        
        actor_pos = Vector((actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z))
        
        # Find all motion sensors in scene
        motion_sensors = [obj for obj in scene.objects if obj.name.startswith("Motion_")]
        
        for sensor_obj in motion_sensors:
            sensor_pos = Vector((sensor_obj.worldPosition.x, sensor_obj.worldPosition.y, sensor_obj.worldPosition.z))
            distance = (actor_pos - sensor_pos).length
            
            # Simple distance-based detection (2.5m range)
            in_range = distance <= 2.5
            
            # Find corresponding detection area
            sensor_id = sensor_obj.name.replace("Motion_", "")
            detection_area_name = f"DetectionArea_{sensor_id}"
            detection_area = scene.objects.get(detection_area_name)
            
            # Update detection area material (if visible)
            if detection_area and detection_area.visible:
                # Get material and update color
                meshes = detection_area.meshes
                if meshes:
                    for mesh in meshes:
                        for material in mesh.materials:
                            if in_range:
                                # Bright red when detecting
                                material.diffuse = [1.0, 0.0, 0.0]  # Bright red
                                material.emit = 0.3  # Add glow effect
                            else:
                                # Blue when idle
                                material.diffuse = [0.2, 0.6, 1.0]  # Blue
                                material.emit = 0.0  # No glow
            
            # Update sensor material with enhanced visual feedback
            sensor_meshes = sensor_obj.meshes
            if sensor_meshes:
                for mesh in sensor_meshes:
                    for material in mesh.materials:
                        if in_range:
                            # Bright yellow with strong emission when detecting
                            material.diffuse = [1.0, 1.0, 0.0]  # Yellow
                            material.emit = 0.5  # Strong glow
                            material.specular = [1.0, 1.0, 1.0]  # White specular
                        else:
                            # Normal color when idle
                            is_virtual = sensor_obj.get("vesper_device_type") == "virtual_motion"
                            if is_virtual:
                                material.diffuse = [0.7, 0.7, 0.7]  # Gray for virtual
                            else:
                                material.diffuse = [1.0, 0.0, 0.0]  # Red for regular
                            material.emit = 0.0  # No glow
                            material.specular = [0.0, 0.0, 0.0]  # No specular
            
            # Store detection state for tracking
            if not hasattr(sensor_obj, 'was_detecting'):
                sensor_obj['was_detecting'] = False
            
            # Print status changes and trigger SmartThings updates
            if in_range and not sensor_obj['was_detecting']:
                room = sensor_obj.get("vesper_room", "unknown")
                print(f"🚨 BGE MOTION DETECTED: {sensor_id} in {room}")
                print(f"   📍 Actor distance: {distance:.1f}m")
                print(f"   📍 Actor position: [{actor_pos.x:.1f}, {actor_pos.y:.1f}, {actor_pos.z:.1f}]")
                print(f"   📍 Sensor position: [{sensor_pos.x:.1f}, {sensor_pos.y:.1f}, {sensor_pos.z:.1f}]")
                
                # Try to trigger SmartThings update for virtual sensors
                trigger_smartthings_update(sensor_obj, True, actor_pos, room)
                
                sensor_obj['was_detecting'] = True
            elif not in_range and sensor_obj['was_detecting']:
                print(f"✅ BGE MOTION CLEARED: {sensor_id}")
                
                # Try to trigger SmartThings update for virtual sensors
                room = sensor_obj.get("vesper_room", "unknown")
                trigger_smartthings_update(sensor_obj, False, actor_pos, room)
                
                sensor_obj['was_detecting'] = False
                
    except Exception as e:
        print(f"⚠️ BGE Simple motion detection error: {e}")

def trigger_smartthings_update(sensor_obj, motion_detected, actor_pos, room):
    """Trigger SmartThings update for virtual motion sensors via cloud server architecture"""
    try:
        # Check if this is a virtual motion sensor
        serial_number = sensor_obj.get("vesper_serial_number")
        container_port = sensor_obj.get("vesper_container_port")
        device_type = sensor_obj.get("vesper_device_type")
        
        if serial_number and device_type == "virtual_motion":
            print(f"🐳 BGE → Container Communication for {serial_number}")
            
            # First, try to trigger the sensor directly if we have a port
            if container_port:
                success = trigger_direct_container_motion(serial_number, container_port, motion_detected, actor_pos, room)
                if success:
                    return
            
            # Fallback: Try the fixed VESPER container on port 8001
            if serial_number == "VSM-15E8-AE80-15D9":
                success = trigger_direct_container_motion(serial_number, 8001, motion_detected, actor_pos, room)
                if success:
                    return
            
            # Final fallback: Try cloud server API
            trigger_cloud_server_motion(serial_number, motion_detected, actor_pos, room)
                
    except Exception as e:
        print(f"⚠️ BGE SmartThings trigger error: {e}")

def trigger_direct_container_motion(serial_number, port, motion_detected, actor_pos, room):
    """Try to trigger motion via direct container communication"""
    try:
        import urllib.request
        import json
        
        # Check available endpoints first
        health_url = f"http://localhost:{port}/health"
        try:
            with urllib.request.urlopen(health_url, timeout=2) as response:
                if response.status != 200:
                    print(f"   ⚠️ Container {serial_number} health check failed on port {port}")
                    return False
        except Exception as e:
            print(f"   ❌ Container {serial_number} not reachable on port {port}: {e}")
            return False
        
        # Try motion state endpoint (based on testbed API pattern)
        motion_endpoints = [
            f"http://localhost:{port}/motion/state",
            f"http://localhost:{port}/api/motion/state", 
            f"http://localhost:{port}/state",
            f"http://localhost:{port}/motion/trigger"
        ]
        
        payload = {
            "motion": "active" if motion_detected else "inactive",
            "sensor_state": "active" if motion_detected else "inactive",
            "actor_position": {
                "x": float(actor_pos.x),
                "y": float(actor_pos.y), 
                "z": float(actor_pos.z)
            },
            "room": room,
            "timestamp": __import__('time').time(),
            "trigger_source": "bge_game_engine"
        }
        
        for endpoint in motion_endpoints:
            try:
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(endpoint, data=data)
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req, timeout=3) as response:
                    if response.status == 200:
                        response_data = json.loads(response.read().decode())
                        print(f"   ✅ Direct trigger successful via {endpoint}")
                        print(f"   📱 Response: {response_data}")
                        return True
                    else:
                        print(f"   ⚠️ Endpoint {endpoint}: HTTP {response.status}")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # Try next endpoint
                print(f"   ⚠️ Endpoint {endpoint}: HTTP {e.code}")
            except Exception as e:
                print(f"   ⚠️ Endpoint {endpoint}: {e}")
                continue
        
        print(f"   ❌ No working motion endpoints found for container on port {port}")
        return False
        
    except Exception as e:
        print(f"   ⚠️ Direct container communication failed: {e}")
        return False

def trigger_cloud_server_motion(serial_number, motion_detected, actor_pos, room):
    """Trigger motion via cloud server (testbed architecture pattern)"""
    try:
        import urllib.request
        import json
        
        # Try cloud server API endpoints (based on logs showing /api/devices/{id}/state)
        cloud_endpoints = [
            f"http://localhost:8081/api/devices/{serial_number}/state",
            f"http://localhost:8081/api/motion/{serial_number}/state",
            f"http://localhost:8081/devices/{serial_number}/motion"
        ]
        
        payload = {
            "motion": "active" if motion_detected else "inactive",
            "state": "active" if motion_detected else "inactive", 
            "sensor_data": {
                "motion_detected": motion_detected,
                "actor_position": {
                    "x": float(actor_pos.x),
                    "y": float(actor_pos.y),
                    "z": float(actor_pos.z)
                },
                "room": room,
                "timestamp": __import__('time').time()
            },
            "trigger_source": "bge_vesper_addon"
        }
        
        for endpoint in cloud_endpoints:
            try:
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(endpoint, data=data)
                req.add_header('Content-Type', 'application/json')
                
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        print(f"   ✅ Cloud server trigger successful via {endpoint}")
                        response_data = json.loads(response.read().decode())
                        print(f"   📱 Cloud response: {response_data}")
                        return True
                    else:
                        print(f"   ⚠️ Cloud endpoint {endpoint}: HTTP {response.status}")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # Try next endpoint
                print(f"   ⚠️ Cloud endpoint {endpoint}: HTTP {e.code}")
            except Exception as e:
                print(f"   ⚠️ Cloud endpoint {endpoint}: {e}")
                continue
        
        print(f"   ❌ No working cloud server endpoints found")
        return False
        
    except Exception as e:
        print(f"   ⚠️ Cloud server communication failed: {e}")
        return False

# Call main function
if __name__ == "__main__":
    main()
