"""
VESPER Smart Home Integration - Blender Addon
Integrates Blender 3D environment with Docker-hosted virtual smart devices
"""

bl_info = {
    "name": "VESPER Smart Home Integration",
    "author": "VESPER Team",
    "version": (3, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > VESPER Smart Home",
    "description": "Complete smart home device management: sensors + virtual devices from Blender",
    "category": "System",
    "support": "COMMUNITY"
}

import bpy
import bpy.props
import bmesh
import time
import sys
import os 
import math
import socket
import subprocess
import re
import traceback
from mathutils import Vector

# Try to import requests, handle gracefully if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests module not available. Install with: pip install requests")

# Motion detection functionality now built-in - no external module needed
MOTION_DETECTION_AVAILABLE = True
print("✅ Built-in motion detection system ready")

# =============================================================================
# BGE MOTION DETECTION SYSTEM
# =============================================================================

# Global motion detection state
_motion_detection_state = {
    "sensors": {},
    "actor_position": None,
    "last_update": 0,
    "initialized": False
}

def initialize_motion_detection():
    """Initialize BGE motion detection system with room-based detection areas"""
    global _motion_detection_state
    
    try:
        import bge
        scene = bge.logic.getCurrentScene()
        
        # Define room detection areas based on motion sensor positions
        # These coordinates should match your house layout
        room_definitions = {
            "motion1": {
                "room_name": "living_room",
                "detection_area": {
                    "x_min": -2.0, "x_max": 4.0,  # Living room X boundaries
                    "y_min": -1.0, "y_max": 5.0,  # Living room Y boundaries
                    "z_min": -0.5, "z_max": 3.0   # Floor to ceiling
                }
            },
            "motion2": {
                "room_name": "bedroom",
                "detection_area": {
                    "x_min": 5.0, "x_max": 10.0,  # Bedroom X boundaries
                    "y_min": -1.0, "y_max": 4.0,  # Bedroom Y boundaries
                    "z_min": -0.5, "z_max": 3.0   # Floor to ceiling
                }
            }
        }
        
        # Find motion sensor objects in the scene
        motion_sensors = {}
        detected_sensors = []
        all_objects = []
        
        # Debug: List all objects in the scene to see what's available
        print("🔍 BGE: Scanning all objects in scene...")
        for obj in scene.objects:
            try:
                obj_name = obj.name
                all_objects.append(obj_name)
                # Look for motion sensors (case insensitive)
                if "motion" in obj_name.lower():
                    pos = obj.worldPosition.copy()
                    detected_sensors.append({
                        "name": obj_name,
                        "position": pos,
                        "x": pos.x,
                        "y": pos.y, 
                        "z": pos.z
                    })
            except Exception as e:
                # Skip objects that can't be processed
                continue
        
        # Print all objects for debugging
        print(f"🔍 BGE: Found {len(all_objects)} total objects in scene:")
        for i, obj_name in enumerate(all_objects[:20]):  # Show first 20 objects
            print(f"    {i+1}: {obj_name}")
        if len(all_objects) > 20:
            print(f"    ... and {len(all_objects) - 20} more objects")
                
        # Print detected sensor coordinates for easy copying
        print(f"🔍 BGE: Found {len(detected_sensors)} motion sensors:")
        for sensor in detected_sensors:
            print(f"    {sensor['name']}: X={sensor['x']:.2f}, Y={sensor['y']:.2f}, Z={sensor['z']:.2f}")
        
        # Find detection area objects in the scene and extract their actual coordinates
        detection_areas = {}
        for obj in scene.objects:
            try:
                obj_name = obj.name
                # Look for detection area objects (case insensitive)
                if "detectionarea" in obj_name.lower():
                    # Extract the coordinates from the mesh vertices
                    if hasattr(obj, 'data') and hasattr(obj.data, 'vertices'):
                        mesh = obj.data
                        world_vertices = []
                        
                        # Get world coordinates of all vertices
                        for vertex in mesh.vertices:
                            world_pos = obj.matrix_world @ vertex.co
                            world_vertices.append([world_pos.x, world_pos.y, world_pos.z])
                        
                        if len(world_vertices) >= 3:
                            # For triangular detection areas, we expect exactly 3 vertices
                            triangle_points = world_vertices[:3]  # Take first 3 vertices
                            
                            # Calculate bounding box from triangle vertices
                            x_coords = [v[0] for v in world_vertices]
                            y_coords = [v[1] for v in world_vertices]
                            z_coords = [v[2] for v in world_vertices]
                            
                            detection_areas[obj_name] = {
                                "vertices": world_vertices,
                                "triangle_points": triangle_points,  # Store the 3 main points
                                "bounding_box": {
                                    "x_min": min(x_coords),
                                    "x_max": max(x_coords),
                                    "y_min": min(y_coords),
                                    "y_max": max(y_coords),
                                    "z_min": min(z_coords),
                                    "z_max": max(z_coords)
                                }
                            }
                            
                            print(f"🔺 Found detection area: {obj_name}")
                            print(f"   📐 Total vertices: {len(world_vertices)}")
                            print(f"   🎯 Triangle points (first 3):")
                            for i, point in enumerate(triangle_points):
                                print(f"      Point {i+1}: [{point[0]:.3f}, {point[1]:.3f}, {point[2]:.3f}]")
                            print(f"   📦 Bounding box: X[{min(x_coords):.1f} to {max(x_coords):.1f}] "
                                  f"Y[{min(y_coords):.1f} to {max(y_coords):.1f}] "
                                  f"Z[{min(z_coords):.1f} to {max(z_coords):.1f}]")
            except Exception as e:
                continue
        
        # Define room detection areas based on ACTUAL detection area objects in Blender
        # Map detection area objects to motion sensors
        room_definitions = {}
        
        # Map motion sensors to their detection areas (flexible matching)
        sensor_to_area_mapping = {
            "motion1": "DetectionArea_motion1",
            "motion2": "DetectionArea_motion2"
        }
        
        for sensor_id, area_obj_name in sensor_to_area_mapping.items():
            # Find the detection area object with flexible matching
            area_data = None
            matched_area_name = None
            for area_name, area_info in detection_areas.items():
                # Check if the area name starts with the expected name (handles .001 suffixes)
                if area_name.startswith(area_obj_name) or area_obj_name in area_name:
                    area_data = area_info
                    matched_area_name = area_name
                    print(f"✅ {sensor_id} → Matched detection area: {matched_area_name}")
                    break
                    break
            
            if area_data:
                # Use the actual bounding box from the Blender detection area
                room_definitions[sensor_id] = {
                    "room_name": "living_room" if sensor_id == "motion1" else "bedroom",
                    "detection_area": area_data["bounding_box"],
                    "triangle_vertices": area_data["triangle_points"]  # Use the clean 3-point triangle
                }
                print(f"✅ {sensor_id} → Using actual Blender detection area coordinates")
                print(f"   📍 Triangle points:")
                for i, point in enumerate(area_data["triangle_points"]):
                    print(f"      {i+1}: [{point[0]:.3f}, {point[1]:.3f}, {point[2]:.3f}]")
            else:
                # Fallback to manual coordinates if detection area not found
                if sensor_id == "motion1":
                    room_definitions[sensor_id] = {
                        "room_name": "living_room",
                        "detection_area": {
                            "x_min": -4.0, "x_max": 1.0,
                            "y_min": -2.0, "y_max": 2.0,
                            "z_min": -2.0, "z_max": 3.0
                        }
                    }
                else:
                    room_definitions[sensor_id] = {
                        "room_name": "bedroom", 
                        "detection_area": {
                            "x_min": -6.0, "x_max": -2.0,
                            "y_min": 3.0, "y_max": 6.0,
                            "z_min": -2.0, "z_max": 3.0
                        }
                    }
                print(f"⚠️ {sensor_id} → Using fallback coordinates (detection area not found)")
        
        # Second pass: Create sensor data with room definitions
        for sensor_info in detected_sensors:
            obj_name = sensor_info["name"]
            # Find the object again by name
            sensor_obj = None
            for obj in scene.objects:
                if obj.name == obj_name:
                    sensor_obj = obj
                    break
            
            if sensor_obj is None:
                continue
                
            sensor_id = obj_name.lower()
            sensor_pos = sensor_info["position"]
            
            # Get room definition for this sensor
            room_def = room_definitions.get(sensor_id, {})
            room_name = room_def.get("room_name", "unknown_room")
            detection_area = room_def.get("detection_area")
            
            # If no predefined area, create one based on sensor position
            if not detection_area:
                detection_area = {
                    "x_min": sensor_pos.x - 3.0, "x_max": sensor_pos.x + 3.0,
                    "y_min": sensor_pos.y - 3.0, "y_max": sensor_pos.y + 3.0,
                    "z_min": sensor_pos.z - 1.0, "z_max": sensor_pos.z + 3.0
                }
                print(f"    ⚠️ No room definition for {sensor_id}, using auto-generated area around sensor")
            
            motion_sensors[sensor_id] = {
                "object": sensor_obj,
                "position": sensor_pos,
                "room_name": room_name,
                "detection_area": detection_area,
                "detecting": False,
                "last_detection": 0
            }
            
            print(f"� {obj_name} → {room_name}")
            print(f"    Sensor at: [{sensor_pos.x:.2f}, {sensor_pos.y:.2f}, {sensor_pos.z:.2f}]")
            print(f"    Detection area: X[{detection_area['x_min']:.1f} to {detection_area['x_max']:.1f}] "
                  f"Y[{detection_area['y_min']:.1f} to {detection_area['y_max']:.1f}] "
                  f"Z[{detection_area['z_min']:.1f} to {detection_area['z_max']:.1f}]")
        
        _motion_detection_state["sensors"] = motion_sensors
        _motion_detection_state["initialized"] = True
        
        # Initialize BGE global variables for debug counter
        if hasattr(bge.logic, 'globalDict'):
            print("[BGE INIT] Setting up global variables...")
            bge.logic.globalDict['motionState'] = {'motion1': False, 'motion2': False}
            bge.logic.globalDict['last_actor_pos'] = None
            bge.logic.globalDict['debug_counter'] = 0  # For periodic debug logging
            print(f"[BGE INIT] Motion state initialized: {bge.logic.globalDict['motionState']}")
        
        print(f"🎮 BGE: Motion detection initialized with {len(motion_sensors)} sensors")
        return True
        
    except ImportError:
        # Not in BGE, return mock detector
        print("⚠️ Not in BGE - creating mock motion detector")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize motion detection: {e}")
        return None

def point_in_triangle(point, triangle_vertices):
    """Check if a 2D point is inside a triangle using barycentric coordinates
    
    Args:
        point: [x, y] coordinates of the point to test
        triangle_vertices: List of 3 vertices [[x1,y1,z1], [x2,y2,z2], [x3,y3,z3]]
    
    Returns:
        bool: True if point is inside triangle
    """
    if len(triangle_vertices) < 3:
        return False
    
    # Extract 2D coordinates (ignore Z)
    p = [point[0], point[1]]
    a = [triangle_vertices[0][0], triangle_vertices[0][1]]
    b = [triangle_vertices[1][0], triangle_vertices[1][1]]
    c = [triangle_vertices[2][0], triangle_vertices[2][1]]
    
    # Calculate barycentric coordinates
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    
    d1 = sign(p, a, b)
    d2 = sign(p, b, c) 
    d3 = sign(p, c, a)
    
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    
    return not (has_neg and has_pos)

def get_detection_area_coordinates(object_name=None):
    """Get the 3 triangle coordinates of a detection area object in Blender
    
    Args:
        object_name: Name of the detection area object (optional)
        
    Returns:
        dict: Dictionary containing triangle coordinates for all or specific detection areas
    """
    try:
        import bge
        scene = bge.logic.getCurrentScene()
        
        detection_coordinates = {}
        
        for obj in scene.objects:
            try:
                obj_name = obj.name
                
                # Look for detection area objects or specific object
                if ("detectionarea" in obj_name.lower()) or (object_name and object_name.lower() in obj_name.lower()):
                    
                    if hasattr(obj, 'data') and hasattr(obj.data, 'vertices'):
                        mesh = obj.data
                        world_vertices = []
                        
                        # Get world coordinates of all vertices
                        for vertex in mesh.vertices:
                            world_pos = obj.matrix_world @ vertex.co
                            world_vertices.append([world_pos.x, world_pos.y, world_pos.z])
                        
                        if len(world_vertices) >= 3:
                            # Get the 3 main triangle points
                            triangle_points = world_vertices[:3]
                            
                            detection_coordinates[obj_name] = {
                                "triangle_points": triangle_points,
                                "total_vertices": len(world_vertices),
                                "object_name": obj_name
                            }
                            
                            print(f"📐 Detection Area: {obj_name}")
                            print(f"   Triangle coordinates:")
                            for i, point in enumerate(triangle_points):
                                print(f"   Point {i+1}: X={point[0]:.3f}, Y={point[1]:.3f}, Z={point[2]:.3f}")
                            print()
                            
            except Exception as e:
                continue
        
        return detection_coordinates
        
    except ImportError:
        print("⚠️ This function only works in Blender Game Engine")
        return {}
    except Exception as e:
        print(f"❌ Error getting detection area coordinates: {e}")
        return {}

def update_motion_detection():
    """Update motion detection - check if actor is in sensor detection areas"""
    global _motion_detection_state
    
    try:
        import bge
        from mathutils import Vector
        import time
        
        scene = bge.logic.getCurrentScene()
        current_time = time.time()
        
        # Skip if not initialized or too frequent updates
        if not _motion_detection_state["initialized"]:
            initialize_motion_detection()
            return
            
        if current_time - _motion_detection_state.get("last_update", 0) < 0.1:
            return  # Update at most 10 times per second
        
        _motion_detection_state["last_update"] = current_time
        
        # Debug: Print actor position every 5 seconds
        if "last_debug_time" not in _motion_detection_state:
            _motion_detection_state["last_debug_time"] = 0
        
        try:
            if current_time - _motion_detection_state["last_debug_time"] > 5.0:
                print(f"🔍 MOTION DEBUG: Actor at [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
                _motion_detection_state["last_debug_time"] = current_time
        except Exception as debug_error:
            print(f"⚠️ Debug print error: {debug_error}")
            _motion_detection_state["last_debug_time"] = current_time
        
        # Find the Actor object - BGE scene.objects is a list, not a dictionary
        actor = None
        for obj in scene.objects:
            if obj.name == "Actor":
                actor = obj
                break
        
        if not actor:
            print("⚠️ Actor object not found in scene")
            return
            
        actor_pos = actor.worldPosition
        _motion_detection_state["actor_position"] = actor_pos.copy()
        
        # Debug: Print actor position every 5 seconds
        if not hasattr(_motion_detection_state, "last_debug_time"):
            _motion_detection_state["last_debug_time"] = 0
        
        if current_time - _motion_detection_state["last_debug_time"] > 5.0:
            print(f"🔍 MOTION DEBUG: Actor at [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
            _motion_detection_state["last_debug_time"] = current_time
        
        # Check each motion sensor's detection area
        for sensor_id, sensor_data in _motion_detection_state["sensors"].items():
            try:
                sensor_obj = sensor_data["object"]
                room_name = sensor_data["room_name"]
                detection_area = sensor_data["detection_area"]
                
                # Check if actor is within the detection area boundaries
                # First check bounding box for quick elimination
                in_bounding_box = (
                    detection_area["x_min"] <= actor_pos.x <= detection_area["x_max"] and
                    detection_area["y_min"] <= actor_pos.y <= detection_area["y_max"] and
                    detection_area["z_min"] <= actor_pos.z <= detection_area["z_max"]
                )
                
                # If we have triangle vertices, do precise triangle detection
                is_in_area = in_bounding_box
                if in_bounding_box and "triangle_vertices" in sensor_data:
                    triangle_vertices = sensor_data["triangle_vertices"]
                    actor_2d = [actor_pos.x, actor_pos.y]
                    is_in_area = point_in_triangle(actor_2d, triangle_vertices)
                    
                    print(f"🔍 AREA CHECK: {sensor_id}")
                    print(f"    Actor: [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
                    print(f"    Bounding box: X[{detection_area['x_min']:.1f} to {detection_area['x_max']:.1f}] "
                          f"Y[{detection_area['y_min']:.1f} to {detection_area['y_max']:.1f}]")
                    print(f"    Triangle vertices: {triangle_vertices}")
                    print(f"    In bounding box: {in_bounding_box}")
                    print(f"    In triangle: {is_in_area}")
                else:
                    print(f"🔍 AREA CHECK: {sensor_id}")
                    print(f"    Actor: [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
                    print(f"    Bounding box: X[{detection_area['x_min']:.1f} to {detection_area['x_max']:.1f}] "
                          f"Y[{detection_area['y_min']:.1f} to {detection_area['y_max']:.1f}]")
                    print(f"    In area: {is_in_area} (bounding box only)")
                
                
            except Exception as e:
                print(f"⚠️ Motion sensor {sensor_id} check failed: {e}")
                continue
            
            # Check for state change
            was_detecting = sensor_data["detecting"]
            if is_in_area != was_detecting:
                sensor_data["detecting"] = is_in_area
                sensor_data["last_detection"] = current_time
                
                if is_in_area:
                    print(f"🔴 {sensor_obj.name} DETECTED - Actor entered {room_name}")
                    print(f"    📍 Actor position: [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
                    
                    # Send CASAS event for room entry
                    try:
                        # Import device manager and generate CASAS event
                        import sys
                        import os
                        addon_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "UPBGE", "Blender", "4.4", "scripts", "addons", "vesper_smart_home")
                        if addon_path not in sys.path:
                            sys.path.append(addon_path)
                        
                        # Get device manager from scene
                        if hasattr(scene, 'vesper_device_manager'):
                            device_manager = scene.vesper_device_manager
                            # Generate CASAS event with proper sensor mapping
                            sensor_mapping = {"motion1": "M01", "motion2": "M02"}
                            casas_id = sensor_mapping.get(sensor_id, sensor_id.upper())
                            event_msg = f"{casas_id} ON (Motion in {room_name})"
                            print(f"📊 CASAS Event (Real): {event_msg}")
                    except Exception as e:
                        print(f"⚠️ CASAS event generation failed: {e}")
                        
                else:
                    print(f"⚪ {sensor_obj.name} CLEAR - Actor left {room_name}")
                    print(f"    📍 Actor position: [{actor_pos.x:.2f}, {actor_pos.y:.2f}, {actor_pos.z:.2f}]")
                    
                    # Send CASAS event for room exit
                    try:
                        if hasattr(scene, 'vesper_device_manager'):
                            sensor_mapping = {"motion1": "M01", "motion2": "M02"}
                            casas_id = sensor_mapping.get(sensor_id, sensor_id.upper())
                            event_msg = f"{casas_id} OFF (Motion left {room_name})"
                            print(f"📊 CASAS Event (Real): {event_msg}")
                    except Exception as e:
                        print(f"⚠️ CASAS event generation failed: {e}")
        
        _motion_detection_state["last_update"] = current_time
        
    except ImportError:
        # Not in BGE
        pass
    except Exception as e:
        print(f"⚠️ Motion detection update error: {e}")

def get_motion_detection_status():
    """Get current motion detection status with room information"""
    global _motion_detection_state
    
    if not _motion_detection_state["initialized"]:
        return {
            "error": "Motion detection not initialized",
            "total_sensors": 0,
            "sensors_detecting": 0,
            "sensors": {}
        }
    
    sensors_status = {}
    detecting_count = 0
    current_room = "unknown"
    
    for sensor_id, sensor_data in _motion_detection_state["sensors"].items():
        is_detecting = sensor_data["detecting"]
        if is_detecting:
            detecting_count += 1
            current_room = sensor_data["room_name"]
            
        sensors_status[sensor_id] = {
            "detecting": is_detecting,
            "room_name": sensor_data["room_name"],
            "position": sensor_data["position"],
            "detection_area": sensor_data["detection_area"],
            "last_detection": sensor_data.get("last_detection", 0)
        }
    
    return {
        "total_sensors": len(_motion_detection_state["sensors"]),
        "sensors_detecting": detecting_count,
        "current_room": current_room,
        "sensors": sensors_status,
        "actor_position": _motion_detection_state.get("actor_position")
    }

# =============================================================================
# DEVICE MANAGEMENT CLASSES
# =============================================================================

class DeviceManager:
    """Manages communication with Docker-hosted virtual devices AND backend console virtual devices"""
    
    def __init__(self):
        # Sensor service URLs (existing functionality)
        self.base_urls = {
            "motion": "http://localhost:8001",
            "item": "http://localhost:8002", 
            "appliance": "http://localhost:8003",
            "dataset": "http://localhost:8004"
        }
        
        # Backend console URLs (new virtual device functionality)
        self.backend_api = "http://localhost:8088"
        self.cloud_api = "http://localhost:8081"
        
        # Port ranges for different device types
        self.device_port_ranges = {
            "motion-sensor": {"start": 9000, "end": 9199},      # 200 ports for motion sensors
            "item-sensor": {"start": 9200, "end": 9299},        # 100 ports for item sensors
            "appliance": {"start": 9300, "end": 9399},          # 100 ports for appliances
            "light": {"start": 9400, "end": 9499},              # 100 ports for lights
            "smart-plug": {"start": 9500, "end": 9599},         # 100 ports for smart plugs
            "camera": {"start": 9600, "end": 9699},             # 100 ports for cameras
            "thermostat": {"start": 9700, "end": 9799},         # 100 ports for thermostats
            "smart-lock": {"start": 9800, "end": 9899},         # 100 ports for smart locks
            "default": {"start": 9900, "end": 9999}             # 100 ports for other devices
        }
        
        # Virtual device configurations (same as web UI)
        self.virtual_configs = {
            "small_apartment_efficient": "small_apartment_efficient.yaml",
            "small_apartment_inefficient": "small_apartment_inefficient.yaml", 
            "medium_house_efficient": "medium_house_efficient.yaml"
        }
        
        # Port tracking to prevent race conditions
        self.allocated_ports = set()
        
        self.device_registry = {}
        self.virtual_devices = {}
        
        # Initialize motion sensor detection system
        if MOTION_DETECTION_AVAILABLE:
            try:
                self.motion_detector = initialize_motion_detection()
                print("🔍 Motion sensor detection system initialized in DeviceManager")
            except Exception as e:
                print(f"⚠️ Failed to initialize motion detection: {e}")
                self.motion_detector = None
        else:
            self.motion_detector = None
    
    # =============================================================================
    # VIRTUAL DEVICE MANAGEMENT (Backend Console API)
    # =============================================================================
    
    def map_device_type(self, device_type):
        """Map extended device types to supported backend types"""
        device_mapping = {
            # Core supported types (no mapping needed)
            "thermostat": "thermostat",
            "motion-sensor": "motion-sensor", 
            "item-sensor": "item-sensor",
            "appliance-controller": "appliance-controller",
            "casas-dataset-manager": "casas-dataset-manager",
            
            # Map new device types to existing ones
            "door-sensor": "motion-sensor",  # Door sensors work like motion sensors
            "temperature-sensor": "thermostat",  # Temperature sensors use thermostat base
            "humidity-sensor": "thermostat",
            "light-sensor": "motion-sensor",
            "smoke-detector": "motion-sensor", 
            "water-leak-sensor": "motion-sensor",
            "smart-switch": "appliance-controller",
            "smart-dimmer": "appliance-controller", 
            "smart-lock": "appliance-controller",
            "garage-door": "appliance-controller",
            "air-quality-sensor": "thermostat",
            "weather-station": "thermostat",
            "uv-sensor": "thermostat",
            "security-camera": "motion-sensor",
            "glass-break-sensor": "motion-sensor",
            "vibration-sensor": "motion-sensor", 
            "panic-button": "appliance-controller",
            "smart-tv": "appliance-controller",
            "coffee-maker": "appliance-controller",
            "robot-vacuum": "appliance-controller",
            "air-purifier": "appliance-controller",
            "energy-monitor": "thermostat",
            "occupancy-counter": "motion-sensor",
        }
        return device_mapping.get(device_type, "motion-sensor")  # Default to motion sensor
    
    def create_docker_container(self, device_type, serial_number, device_name=None):
        """Create individual Docker container for virtual device
        
        Args:
            device_type: Type of device to create
            serial_number: Unique serial number for the device
            device_name: Optional custom name for the device (used in container name)
        """
        import subprocess
        import os
        import re
        
        # Map device type to Docker image
        image_mapping = {
            "thermostat": "virtual-interaction-thermostat",
            "motion-sensor": "virtual-interaction-motion-sensor",
            "item-sensor": "virtual-interaction-item-sensor", 
            "appliance-controller": "virtual-interaction-appliance-controller",
            "casas-dataset-manager": "virtual-interaction-casas-dataset-manager"
        }
        
        backend_type = self.map_device_type(device_type)
        image_name = image_mapping.get(backend_type, "virtual-interaction-motion-sensor")
        
        # Create container name with optional custom device name
        if device_name and device_name.strip():
            # Sanitize device name for Docker container naming
            sanitized_name = re.sub(r'[^a-zA-Z0-9\-_]', '-', device_name.strip().lower().replace(' ', '-'))
            sanitized_name = re.sub(r'-+', '-', sanitized_name).strip('-')
            container_name = f"{sanitized_name}-{device_type}-{serial_number}"
        else:
            container_name = f"{device_type}-{serial_number}"
        
        # Find available port in device-specific range
        port_range = self.device_port_ranges.get(device_type, self.device_port_ranges["default"])
        port = self.find_available_port_in_range(port_range["start"], port_range["end"])
        
        if port is None:
            print(f"❌ No available ports in range {port_range['start']}-{port_range['end']} for {device_type}")
            return None
        
        # Reserve the port immediately to prevent race conditions
        self.allocated_ports.add(port)
        
        print(f"🔌 Assigned port {port} to {device_type} (range: {port_range['start']}-{port_range['end']})")
        
        try:
            # Ensure virtual-interaction_testbed-network exists
            network_check_cmd = ["docker", "network", "ls", "--filter", "name=^virtual-interaction_testbed-network$", "--format", "{{.Name}}"]
            network_result = subprocess.run(network_check_cmd, capture_output=True, text=True)
            
            if "virtual-interaction_testbed-network" not in network_result.stdout:
                print("🌐 Creating virtual-interaction_testbed-network...")
                create_network_cmd = ["docker", "network", "create", "virtual-interaction_testbed-network"]
                subprocess.run(create_network_cmd, capture_output=True, text=True)
                print("✅ virtual-interaction_testbed-network created")
            
            # Check if container with this name already exists and remove it
            check_cmd = ["docker", "ps", "-a", "--filter", f"name=^{container_name}$", "--format", "{{.Names}}"]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if check_result.returncode == 0 and container_name in check_result.stdout:
                print(f"⚠️ Container {container_name} already exists, removing it...")
                # Stop and remove existing container
                subprocess.run(["docker", "stop", container_name], capture_output=True, text=True)
                subprocess.run(["docker", "rm", container_name], capture_output=True, text=True)
                print(f"✅ Removed existing container {container_name}")
            
            # Create Docker container
            cmd = [
                "docker", "run", "-d",
                "--name", container_name,
                "--network", "virtual-interaction_testbed-network",
                "-p", f"{port}:8000",
                "-e", f"DEVICE_SERIAL={serial_number}",
                "-e", f"DEVICE_TYPE={device_type}",
                "-e", "REDIS_HOST=redis",
                "-e", "REDIS_PORT=6379",
                "-e", "CLOUD_SERVER_URL=http://cloud-server:8080",
                "-e", "API_PORT=8000"
            ]
            
            # Add device-specific environment variables
            if backend_type == "motion-sensor":
                cmd.extend(["-e", "SENSOR_ZONES=M01,M02,M03,M04,M05,M06,M07,M08,M09,M10,M11,M12,M13,M14,M15,M16,M17,M18,M19,M20,M21,M22,M23,M24,M25,M26"])
            
            cmd.append(image_name)
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="c:\\Users\\hbui11\\Desktop\\vesper_llm\\virtual-interaction")
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                print(f"✅ Created Docker container: {container_name} on port {port}")
                return {
                    "container_name": container_name,
                    "container_id": container_id,
                    "port": port,
                    "image": image_name
                }
            else:
                print(f"❌ Failed to create container: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating Docker container: {e}")
            return None
    
    def find_available_port_in_range(self, start_port, end_port):
        """Find an available port within a specific range"""
        import socket
        import subprocess
        
        port = start_port
        while port <= end_port:
            # Skip ports that are already allocated by this session
            if port in self.allocated_ports:
                port += 1
                continue
                
            try:
                # Check if port is available by trying to bind to all interfaces (0.0.0.0)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    
                    # Double-check by looking for existing Docker containers using this port
                    check_cmd = ["docker", "ps", "--format", "{{.Ports}}", "--filter", f"publish={port}"]
                    result = subprocess.run(check_cmd, capture_output=True, text=True)
                    
                    # If no containers are using this port, it's available
                    if result.returncode == 0 and not result.stdout.strip():
                        return port
                    else:
                        # Port is being used by Docker, try next one
                        port += 1
                        continue
                        
            except OSError:
                # Port is not available, try next one
                port += 1
                continue
        return None
    
    def find_available_port(self, start_port=9000):
        """Find an available port starting from start_port (legacy method)"""
        import socket
        port = start_port
        while port < 65535:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                port += 1
        return None
    
    def delete_docker_container(self, container_name):
        """Delete individual Docker container"""
        import subprocess
        
        try:
            # Stop and remove container
            stop_cmd = ["docker", "stop", container_name]
            remove_cmd = ["docker", "rm", container_name]
            
            subprocess.run(stop_cmd, capture_output=True, text=True)
            result = subprocess.run(remove_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Deleted Docker container: {container_name}")
                return True
            else:
                print(f"❌ Failed to delete container: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting Docker container: {e}")
            return False
    
    def spawn_virtual_device(self, device_type="thermostat", username="admin", config_type="medium_house_efficient", device_name=None):
        """Spawn virtual device with individual Docker container
        
        Args:
            device_type: Any device type from the expanded list
            username: User creating the device
            config_type: Configuration type for the device
            device_name: Custom name for the device (used in container name)
        """
        if not REQUESTS_AVAILABLE:
            return None
        
        if config_type not in self.virtual_configs:
            print(f"❌ Invalid config: {config_type}")
            return None
        
        # Map device type to supported backend type
        backend_device_type = self.map_device_type(device_type)
        original_type = device_type  # Keep original for display
        
        # Step 1: Create device via backend console API to get serial number
        payload = {
            "device_type": backend_device_type,
            "username": username,
            "environment_config": self.virtual_configs[config_type]
        }
        
        try:
            response = requests.post(f"{self.backend_api}/api/console/spawn", json=payload, timeout=30)
            if response.status_code == 200:
                device_info = response.json()
                serial = device_info.get("serial_number")
                
                # Step 2: Create individual Docker container for this device
                container_info = self.create_docker_container(original_type, serial, device_name=device_name)
                
                if container_info:
                    # Add container info to device
                    device_info["container_info"] = container_info
                    device_info["original_device_type"] = original_type
                    device_info["backend_device_type"] = backend_device_type
                    
                    self.virtual_devices[serial] = device_info
                    
                    container_name = container_info["container_name"]
                    port = container_info["port"]
                    
                    if original_type != backend_device_type:
                        print(f"✅ Spawned {original_type} (as {backend_device_type}): {serial}")
                    else:
                        print(f"✅ Spawned {original_type}: {serial}")
                    print(f"🐳 Created Docker container: {container_name} on port {port}")
                    
                    # 🎯 AUTO-CREATE DETECTION AREA FOR MOTION SENSORS
                    if original_type == "motion-sensor" or backend_device_type == "motion-sensor":
                        try:
                            # Use cursor location or default position (0, 0, 0)
                            import bpy
                            cursor_pos = bpy.context.scene.cursor.location.copy()
                            # Default orientation (0 degrees = facing North/+Y)
                            orientation = 0.0
                            
                            print(f"🎯 Creating visual sensor and detection area for virtual motion sensor {serial}")
                            
                            # Step 1: Create visual sensor object in Blender scene
                            bpy.ops.mesh.primitive_ico_sphere_add(radius=0.15, location=cursor_pos)
                            sensor_obj = bpy.context.active_object
                            sensor_obj.name = f"Motion_{serial}"
                            
                            # Create gray material for virtual motion sensors (different from red regular sensors)
                            mat = bpy.data.materials.new(name=f"VirtualMotion_Material_{serial}")
                            mat.use_nodes = True
                            if mat.node_tree and mat.node_tree.nodes.get("Principled BSDF"):
                                mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.7, 0.7, 0.7, 1)  # Gray
                            sensor_obj.data.materials.append(mat)
                            
                            # Add custom properties for virtual device tracking
                            sensor_obj["vesper_device_id"] = serial
                            sensor_obj["vesper_device_type"] = "virtual_motion"
                            sensor_obj["vesper_serial_number"] = serial
                            sensor_obj["vesper_container_name"] = container_name
                            sensor_obj["vesper_container_port"] = port
                            
                            print(f"✅ Created visual sensor: {sensor_obj.name}")
                            
                            # Step 2: Create detection area
                            detection_created = self.create_automatic_detection_area(serial, cursor_pos, orientation)
                            
                            if detection_created:
                                print(f"✅ Virtual motion sensor {serial} now has detection area!")
                                # Update device info to track detection area
                                device_info["detection_area_created"] = True
                                device_info["visual_sensor_created"] = True
                            else:
                                print(f"⚠️ Failed to create detection area for virtual motion sensor {serial}")
                                device_info["detection_area_created"] = False
                                device_info["visual_sensor_created"] = True
                                
                        except Exception as e:
                            print(f"⚠️ Error creating visual sensor/detection area for virtual motion sensor {serial}: {e}")
                            device_info["detection_area_created"] = False
                            device_info["visual_sensor_created"] = False
                    
                    return device_info
                else:
                    # If container creation failed, clean up the backend device
                    self.delete_virtual_device_backend_only(serial)
                    print(f"❌ Failed to create Docker container for {serial}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error spawning device: {e}")
        return None
    
    def delete_virtual_device_backend_only(self, serial_number):
        """Delete virtual device from backend only (helper method)"""
        try:
            response = requests.delete(f"{self.backend_api}/api/console/device/{serial_number}", timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error deleting backend device: {e}")
            return False

    def delete_virtual_device(self, serial_number):
        """Delete virtual device and its Docker container"""
        if not REQUESTS_AVAILABLE:
            return False
        
        # Get device info to find container name
        device_info = self.virtual_devices.get(serial_number)
        container_name = None
        
        if device_info and "container_info" in device_info:
            container_name = device_info["container_info"]["container_name"]
        
        try:
            # Step 1: Delete from backend console
            response = requests.delete(f"{self.backend_api}/api/console/device/{serial_number}", timeout=30)
            backend_deleted = response.status_code == 200
            
            # Step 2: Delete Docker container if it exists
            container_deleted = True
            if container_name:
                container_deleted = self.delete_docker_container(container_name)
            
            # Clean up local registry
            if serial_number in self.virtual_devices:
                del self.virtual_devices[serial_number]
            
            if backend_deleted and container_deleted:
                print(f"✅ Deleted virtual device and container: {serial_number}")
                return True
            else:
                print(f"⚠️ Partial deletion for {serial_number}: backend={backend_deleted}, container={container_deleted}")
                return backend_deleted  # At least backend was deleted
                
        except Exception as e:
            print(f"❌ Error deleting device: {e}")
            return False
    
    def get_virtual_devices(self):
        """Get list of active virtual devices"""
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            response = requests.get(f"{self.backend_api}/api/console/devices", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Error getting devices: {e}")
        return []
    
    def control_virtual_device(self, serial_number, command_type, value):
        """Control virtual device (setpoint, mode, etc.)"""
        if not REQUESTS_AVAILABLE:
            return False
        
        endpoints = {
            "setpoint": f"/api/console/device/{serial_number}/setpoint",
            "mode": f"/api/console/device/{serial_number}/mode",
            "weather": f"/api/console/device/{serial_number}/weather-override",
            "current_temp": f"/api/console/device/{serial_number}/current-temp"
        }
        
        payloads = {
            "setpoint": {"target_temp": value},
            "mode": {"mode": value},
            "weather": {"temperature": value},
            "current_temp": {"temperature": value}
        }
        
        if command_type not in endpoints:
            return False
        
        try:
            response = requests.post(
                f"{self.backend_api}{endpoints[command_type]}",
                json=payloads[command_type],
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error controlling device: {e}")
        return False
    
    # =============================================================================
    # SENSOR MANAGEMENT (Existing functionality)
    # =============================================================================
    
    def check_services_health(self):
        """Check if all Docker services are running"""
        if not REQUESTS_AVAILABLE:
            return {"error": "requests module not available"}
            
        health_status = {}
        for service, url in self.base_urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                health_status[service] = response.status_code == 200
            except Exception as e:
                health_status[service] = False
                print(f"Service {service} check failed: {e}")
        return health_status
    
    def add_motion_sensor(self, sensor_id: str, room: str, position: Vector, orientation: float = 0.0) -> bool:
        """Add a motion sensor to the virtual environment with automatic detection area creation
        
        Args:
            sensor_id: Unique identifier for the sensor
            room: Room where sensor is located
            position: 3D position of the sensor
            orientation: Sensor facing direction in degrees (0 = +Y axis)
        """
        if not REQUESTS_AVAILABLE:
            print("⚠️ requests module required for Docker communication")
            return False
            
        print(f"🎯 Creating motion sensor {sensor_id}")
        print(f"   📍 Position: [{position.x:.1f}, {position.y:.1f}, {position.z:.1f}]")
        print(f"   🧭 Orientation: {orientation}°")
        print(f"   🏠 Room: {room}")
        print(f"   🐳 Connecting to Docker backend...")
        
        try:
            # Configure Docker-hosted sensor service (required for persistence)
            data = {
                "detection_zone": {
                    "x": position.x,
                    "y": position.y,
                    "radius": 5.0  # Updated to 5m for Aeotec specs
                },
                "room_location": room,
                "sensitivity": 1.0,
                "cooldown_period": 3.0  # Updated to 3s for realistic behavior
            }
            response = requests.post(f"{self.base_urls['motion']}/configure", json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Docker sensor backend configured successfully")
                
                # Add to device registry
                self.device_registry[sensor_id] = {
                    "type": "motion",
                    "room": room,
                    "position": position,
                    "orientation": orientation,
                    "state": "inactive",
                    "detection_area_created": False
                }
                
                # Create visual sensor object in Blender
                try:
                    import bpy
                    
                    # Create sensor as small red sphere
                    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, location=position)
                    sensor_obj = bpy.context.active_object
                    sensor_obj.name = f"Motion_{sensor_id}"
                    
                    # Create red material for sensor
                    mat = bpy.data.materials.new(name=f"Motion_Material_{sensor_id}")
                    mat.use_nodes = True
                    if mat.node_tree and mat.node_tree.nodes.get("Principled BSDF"):
                        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red
                    sensor_obj.data.materials.append(mat)
                    
                    # Add custom properties
                    sensor_obj["vesper_device_id"] = sensor_id
                    sensor_obj["vesper_device_type"] = "motion"
                    sensor_obj["vesper_room"] = room
                    
                    print(f"✅ Created sensor visual: {sensor_obj.name}")
                    
                except Exception as e:
                    print(f"⚠️ Failed to create sensor visual: {e}")
                
                # Register with realistic motion detection system
                if MOTION_DETECTION_AVAILABLE and self.motion_detector is not None:
                    try:
                        register_motion_sensor_detection(sensor_id, position, room, orientation)
                        print(f"✅ Registered with motion detection system")
                    except Exception as e:
                        print(f"⚠️ Failed to register realistic detection for {sensor_id}: {e}")
                
                # Automatically create visual detection area in Blender
                detection_created = self.create_automatic_detection_area(sensor_id, position, orientation)
                
                if detection_created:
                    self.device_registry[sensor_id]["detection_area_created"] = True
                    print(f"✅ Created automatic detection area")
                else:
                    print(f"⚠️ Failed to create detection area")
                
                print(f"🎉 Motion sensor {sensor_id} created successfully!")
                print(f"   🐳 Docker backend: ✅")
                print(f"   🎯 Visual sensor: ✅") 
                print(f"   📐 Detection area: {'✅' if detection_created else '❌'}")
                print(f"   🔍 Motion detection: {'✅' if MOTION_DETECTION_AVAILABLE else '❌'}")
                
                return True
            else:
                print(f"❌ Docker sensor configuration failed (status: {response.status_code})")
                print(f"   🐳 Make sure Docker containers are running")
                print(f"   💡 Run: docker-compose -f docker-compose.casas.yml up -d")
                return False
                
        except Exception as e:
            print(f"❌ Failed to add motion sensor: {e}")
            print(f"   🐳 Docker backend communication error")
            print(f"   � Check if motion sensor container is running on {self.base_urls['motion']}")
            return False
    
    def add_item_sensor(self, sensor_id: str, item_name: str, position: Vector) -> bool:
        """Add an item sensor to track objects"""
        if not REQUESTS_AVAILABLE:
            print(" requests module required for Docker communication")
            return False
            
        try:
            data = {
                "sensor_id": sensor_id,
                "item_name": item_name,
                "position": [position.x, position.y, position.z],
                "state": "present"
            }
            response = requests.post(f"{self.base_urls['item']}/items", json=data, timeout=10)
            if response.status_code == 200:
                self.device_registry[sensor_id] = {
                    "type": "item",
                    "item_name": item_name,
                    "position": position,
                    "state": "present"
                }
                print(f" Added item sensor {sensor_id} for {item_name}")
                return True
        except Exception as e:
            print(f" Failed to add item sensor: {e}")
        return False
    
    def trigger_motion_sensor(self, sensor_id: str, state: str = "active") -> bool:
        """Trigger a motion sensor"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            data = {"motion": state}
            response = requests.post(f"{self.base_urls['motion']}/manual_trigger", json=data, timeout=10)
            if response.status_code == 200:
                if sensor_id in self.device_registry:
                    self.device_registry[sensor_id]["state"] = state
                return True
        except Exception as e:
            print(f" Failed to trigger motion sensor: {e}")
        return False
    
    def interact_with_item(self, sensor_id: str, state: str = "absent") -> bool:
        """Interact with an item (take/use)"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            data = {"sensor_id": sensor_id, "state": state}
            response = requests.post(f"{self.base_urls['item']}/interact", json=data, timeout=10)
            if response.status_code == 200:
                if sensor_id in self.device_registry:
                    self.device_registry[sensor_id]["state"] = state
                return True
        except Exception as e:
            print(f" Failed to interact with item: {e}")
        return False
    
    def update_motion_detection(self):
        """Update motion sensor detection system (call every frame) with enhanced status reporting"""
        if self.motion_detector is not None and MOTION_DETECTION_AVAILABLE:
            try:
                # Store previous detection states for comparison
                previous_states = {}
                for sensor_id in self.device_registry:
                    if self.device_registry[sensor_id].get("type") == "motion":
                        previous_states[sensor_id] = self.device_registry[sensor_id].get("detecting_actor", False)
                
                # Update the motion detection system
                update_motion_detection()
                
                # Get current detection status
                status = self.get_motion_detection_status()
                
                # Check for state changes and update device registry + visuals
                if "sensors" in status:
                    for sensor_id, sensor_status in status["sensors"].items():
                        is_detecting = sensor_status.get("detecting", False)
                        was_detecting = previous_states.get(sensor_id, False)
                        
                        # Update device registry
                        if sensor_id in self.device_registry:
                            self.device_registry[sensor_id]["detecting_actor"] = is_detecting
                            self.device_registry[sensor_id]["last_detection_update"] = time.time()
                            
                            # If state changed, update visuals and send notifications
                            if is_detecting != was_detecting:
                                # Update visual feedback
                                self.update_detection_area_visualization(sensor_id, is_detecting)
                                
                                # Send SmartThings update if this is a virtual sensor
                                if sensor_id in self.virtual_devices:
                                    actor_pos = sensor_status.get("position", [0, 0, 0])
                                    room = sensor_status.get("room", "unknown")
                                    
                                    self.update_smartthings_device(sensor_id, {
                                        "motion": is_detecting,
                                        "actor_position": actor_pos,
                                        "room": room,
                                        "timestamp": time.time(),
                                        "state_change": "motion_detected" if is_detecting else "motion_cleared"
                                    })
                                
                                # Enhanced status reporting
                                if is_detecting:
                                    print(f"🚨 MOTION DETECTED: Sensor {sensor_id}")
                                    print(f"   📍 Actor in detection zone")
                                    print(f"   🏠 Room: {sensor_status.get('room', 'unknown')}")
                                    print(f"   📊 Total detections: {sensor_status.get('detection_count', 0)}")
                                else:
                                    print(f"✅ MOTION CLEARED: Sensor {sensor_id}")
                                    print(f"   📍 Actor left detection zone")
                
            except Exception as e:
                print(f"⚠️ Motion detection update error: {e}")
    
    def get_motion_detection_status(self):
        """Get current motion detection status for all sensors"""
        if self.motion_detector is not None and MOTION_DETECTION_AVAILABLE:
            try:
                return get_motion_detection_status()
            except Exception as e:
                print(f"⚠️ Failed to get motion detection status: {e}")
                return {"error": str(e)}
        return {"error": "Motion detection system not available"}
    
    def update_smartthings_device(self, device_id: str, data: dict):
        """Update SmartThings device state (for motion sensor integration)
        
        Args:
            device_id: Device identifier
            data: State data to send to SmartThings
        """
        try:
            # Enhanced SmartThings integration for virtual motion sensors
            print(f"📱 SmartThings Update: {device_id}")
            for key, value in data.items():
                print(f"   {key}: {value}")
            
            # For virtual motion sensors, also update the Docker container
            if device_id in self.virtual_devices:
                device_info = self.virtual_devices[device_id]
                container_info = device_info.get("container_info")
                
                if container_info and "motion" in device_info.get("original_device_type", "").lower():
                    # Send motion status to virtual motion sensor container
                    container_port = container_info.get("port")
                    if container_port and REQUESTS_AVAILABLE:
                        try:
                            motion_state = data.get("motion", False)
                            actor_pos = data.get("actor_position", [0, 0, 0])
                            room = data.get("room", "unknown")
                            
                            payload = {
                                "motion": motion_state,
                                "actor_position": {
                                    "x": actor_pos[0] if isinstance(actor_pos, (list, tuple)) else actor_pos.x,
                                    "y": actor_pos[1] if isinstance(actor_pos, (list, tuple)) else actor_pos.y,
                                    "z": actor_pos[2] if isinstance(actor_pos, (list, tuple)) else actor_pos.z
                                },
                                "room": room,
                                "timestamp": data.get("timestamp", time.time()),
                                "trigger_source": "blender_addon"
                            }
                            
                            # Update virtual motion sensor container
                            print(f"🐳 Attempting container communication:")
                            print(f"   📡 Target URL: http://localhost:{container_port}/motion/trigger")
                            print(f"   📦 Payload: {payload}")
                            
                            response = requests.post(
                                f"http://localhost:{container_port}/motion/trigger",
                                json=payload,
                                timeout=5
                            )
                            
                            if response.status_code == 200:
                                print(f"✅ Virtual motion sensor {device_id} updated successfully")
                                print(f"   🐳 Container port: {container_port}")
                                print(f"   🚨 Motion: {'DETECTED' if motion_state else 'CLEAR'}")
                                print(f"   📍 Actor: [{actor_pos[0]:.1f}, {actor_pos[1]:.1f}, {actor_pos[2]:.1f}]")
                                print(f"   🏠 Room: {room}")
                                
                                # Try to get response details
                                try:
                                    response_data = response.json()
                                    print(f"   📱 SmartThings status: {response_data.get('smartthings_status', 'unknown')}")
                                    if 'device_id' in response_data:
                                        print(f"   🔗 SmartThings Device ID: {response_data['device_id']}")
                                    if 'error' in response_data:
                                        print(f"   ⚠️ Container error: {response_data['error']}")
                                except:
                                    print(f"   📄 Response: {response.text}")
                            else:
                                print(f"⚠️ Virtual sensor update failed: HTTP {response.status_code}")
                                print(f"   📄 Response: {response.text}")
                                print(f"   💡 Check container logs: docker logs virtual_motion_{device_id}")
                        
                        except requests.exceptions.ConnectionError:
                            print(f"❌ Container connection failed on port {container_port}")
                            print(f"   💡 Check if container is running: docker ps | grep {device_id}")
                            print(f"   💡 Try restarting: docker restart virtual_motion_{device_id}")
                        except requests.exceptions.Timeout:
                            print(f"⏱️ Container communication timeout on port {container_port}")
                            print(f"   💡 Container may be overloaded")
                        except Exception as e:
                            print(f"⚠️ Failed to update virtual motion sensor container: {e}")
                            print(f"   🐳 Port: {container_port}")
                            print(f"   💡 Debug: docker logs virtual_motion_{device_id}")
                    else:
                        if not container_port:
                            print(f"⚠️ No container port found for {device_id}")
                        if not REQUESTS_AVAILABLE:
                            print(f"⚠️ Requests library not available")
            
            # Handle fixed VESPER containers with direct port mapping
            if device_id == "VSM-15E8-AE80-15D9" and REQUESTS_AVAILABLE:
                try:
                    motion_state = data.get("motion", False)
                    actor_pos = data.get("actor_position", [0, 0, 0])
                    room = data.get("room", "unknown")
                    
                    payload = {
                        "motion": motion_state,
                        "actor_position": {
                            "x": actor_pos[0] if isinstance(actor_pos, (list, tuple)) else actor_pos.x,
                            "y": actor_pos[1] if isinstance(actor_pos, (list, tuple)) else actor_pos.y,
                            "z": actor_pos[2] if isinstance(actor_pos, (list, tuple)) else actor_pos.z
                        },
                        "room": room,
                        "timestamp": data.get("timestamp", time.time()),
                        "trigger_source": "vesper_addon_fixed"
                    }
                    
                    print(f"🐳 Attempting fixed VESPER container communication:")
                    print(f"   📡 Target URL: http://localhost:8001/motion/trigger")
                    print(f"   📦 Payload: {payload}")
                    
                    response = requests.post(
                        f"http://localhost:8001/motion/trigger",
                        json=payload,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        print(f"✅ Fixed VESPER motion sensor {device_id} updated successfully")
                        print(f"   🐳 Container port: 8001")
                        print(f"   🚨 Motion: {'DETECTED' if motion_state else 'CLEAR'}")
                        print(f"   📍 Actor: [{actor_pos[0]:.1f}, {actor_pos[1]:.1f}, {actor_pos[2]:.1f}]")
                        print(f"   🏠 Room: {room}")
                        
                        # Try to get response details
                        try:
                            response_data = response.json()
                            print(f"   📱 Response: {response_data}")
                        except:
                            print(f"   📄 Response: {response.text}")
                    else:
                        print(f"⚠️ Fixed VESPER sensor update failed: HTTP {response.status_code}")
                        print(f"   📄 Response: {response.text}")
                        print(f"   💡 Check container logs: docker logs vesper_motion_{device_id}")
                
                except requests.exceptions.ConnectionError:
                    print(f"❌ Fixed VESPER container connection failed on port 8001")
                    print(f"   💡 Check if container is running: docker ps | grep vesper_motion_{device_id}")
                    print(f"   💡 Try restarting: docker restart vesper_motion_{device_id}")
                except requests.exceptions.Timeout:
                    print(f"⏱️ Fixed VESPER container communication timeout on port 8001")
                    print(f"   💡 Container may be overloaded")
                except Exception as e:
                    print(f"⚠️ Failed to update fixed VESPER motion sensor container: {e}")
                    print(f"   🐳 Port: 8001")
                    print(f"   💡 Debug: docker logs vesper_motion_{device_id}")
            
            # TODO: Implement actual SmartThings Cloud API call for real devices
            # Example for future SmartThings integration:
            # if hasattr(self, 'smartthings_token') and self.smartthings_token:
            #     headers = {"Authorization": f"Bearer {self.smartthings_token}"}
            #     smartthings_data = {
            #         "commands": [{
            #             "component": "main",
            #             "capability": "motionSensor", 
            #             "command": "motion" if data.get("motion") else "inactive"
            #         }]
            #     }
            #     response = requests.post(
            #         f"https://api.smartthings.com/v1/devices/{device_id}/commands",
            #         json=smartthings_data, headers=headers, timeout=10
            #     )
                
        except Exception as e:
            print(f"❌ SmartThings update failed: {e}")
    
    def create_automatic_detection_area(self, sensor_id: str, position: Vector, orientation: float):
        """Create triangular detection area for motion sensor (exactly as requested)
        
        Args:
            sensor_id: Motion sensor identifier
            position: Sensor position
            orientation: Sensor orientation in degrees (0=North, 90=East, 180=South, 270=West)
        """
        try:
            import bpy
            import bmesh
            import math
            
            # Detection area specifications (more reasonable size)
            detection_range = 2.5  # 2.5 meters (reduced from 5m)
            fov_angle = 90.0      # 90 degrees field of view (reduced from 120°)
            
            print(f"🎯 Creating triangular detection area for {sensor_id}")
            print(f"   📍 Position: [{position.x:.1f}, {position.y:.1f}, {position.z:.1f}]")
            print(f"   🧭 Orientation: {orientation}°")
            print(f"   📏 Range: {detection_range}m")
            print(f"   📐 FOV: {fov_angle}°")
            
            # Create mesh data
            mesh = bpy.data.meshes.new(f"{sensor_id}_detection_area")
            bm = bmesh.new()
            
            # Convert orientation to radians
            orientation_rad = math.radians(orientation)
            half_fov_rad = math.radians(fov_angle / 2)
            
            # Create triangular detection area vertices
            # Center point (sensor position) - this is the apex of the triangle
            center = (0, 0, 0)
            
            # Left edge of detection cone (5m away)
            left_x = detection_range * math.sin(orientation_rad - half_fov_rad)
            left_y = detection_range * math.cos(orientation_rad - half_fov_rad)
            left_point = (left_x, left_y, 0)
            
            # Right edge of detection cone (5m away)
            right_x = detection_range * math.sin(orientation_rad + half_fov_rad)
            right_y = detection_range * math.cos(orientation_rad + half_fov_rad)
            right_point = (right_x, right_y, 0)
            
            print(f"   📐 Triangle vertices:")
            print(f"      Apex (sensor): {center}")
            print(f"      Left edge: ({left_x:.1f}, {left_y:.1f}, 0)")
            print(f"      Right edge: ({right_x:.1f}, {right_y:.1f}, 0)")
            
            # Add vertices to bmesh
            v_center = bm.verts.new(center)
            v_left = bm.verts.new(left_point)
            v_right = bm.verts.new(right_point)
            
            # Create triangle face (this automatically creates the edges)
            bm.faces.new([v_center, v_left, v_right])
            
            # Update mesh
            bm.to_mesh(mesh)
            bm.free()
            
            # Create object
            detection_obj = bpy.data.objects.new(f"DetectionArea_{sensor_id}", mesh)
            detection_obj.location = position
            
            # Add to scene
            bpy.context.collection.objects.link(detection_obj)
            
            # Create bright blue wireframe material for visibility
            material = bpy.data.materials.new(f"DetectionMaterial_{sensor_id}")
            material.use_nodes = True
            material.blend_method = 'ALPHA'
            
            # Set material properties for bright blue wireframe
            bsdf = material.node_tree.nodes["Principled BSDF"]
            bsdf.inputs["Base Color"].default_value = (0.2, 0.6, 1.0, 1.0)  # Bright blue
            bsdf.inputs["Alpha"].default_value = 0.8  # More visible
            
            # Apply material
            detection_obj.data.materials.append(material)
            
            # Set display properties for maximum visibility in EDITOR but invisible in BGE
            detection_obj.display_type = 'WIRE'  # Wireframe display
            detection_obj.hide_render = True     # Hide from renders
            detection_obj.show_in_front = True   # Show through other objects
            detection_obj.color = (0.2, 0.6, 1.0, 1.0)  # Blue color in viewport
            
            # BGE-specific properties: Make detection area invisible in game engine
            detection_obj.game.use_collision_bounds = False  # No collision in BGE
            detection_obj.game.physics_type = 'NO_COLLISION'  # No physics
            detection_obj.visible = False  # Invisible in BGE (this is the key!)
            
            # Alternative: Make it semi-transparent for BGE debugging
            # detection_obj.visible = True
            # detection_obj.color[3] = 0.1  # Very transparent
            
            # 🔗 PARENT DETECTION AREA TO SENSOR FOR SYNCHRONIZED MOVEMENT
            # Find the sensor object to parent the detection area to
            sensor_obj_name = f"Motion_{sensor_id}"
            sensor_obj = bpy.data.objects.get(sensor_obj_name)
            
            if sensor_obj:
                # Set detection area's parent to the sensor object
                detection_obj.parent = sensor_obj
                detection_obj.parent_type = 'OBJECT'
                
                # Make detection area position relative to sensor (local coordinates)
                # This ensures the triangle moves with the sensor
                detection_obj.location = (0, 0, 0)  # Reset to sensor's local origin
                
                print(f"🔗 Detection area parented to sensor: {sensor_obj_name}")
                print(f"   📍 Detection area will move with sensor automatically")
                print(f"   🎯 Triangle positioned relative to sensor's local coordinates")
            else:
                # If no sensor object found, create one or warn user
                print(f"⚠️ Sensor object '{sensor_obj_name}' not found")
                print(f"   📍 Detection area created at world coordinates")
                print(f"   💡 Create sensor visual first for automatic movement sync")
            
            # Add custom properties for tracking
            detection_obj["vesper_detection_area"] = True
            detection_obj["sensor_id"] = sensor_id
            detection_obj["detection_state"] = "idle"
            detection_obj["detection_range"] = detection_range
            detection_obj["fov_angle"] = fov_angle
            detection_obj["is_parented"] = sensor_obj is not None
            
            # Select the object so it's highlighted
            bpy.context.view_layer.objects.active = detection_obj
            detection_obj.select_set(True)
            
            # Update device registry
            if sensor_id in self.device_registry:
                self.device_registry[sensor_id]["detection_area_created"] = True
                self.device_registry[sensor_id]["detection_area_object"] = detection_obj.name
            
            print(f"✅ Triangular detection area created successfully!")
            print(f"   � Object name: {detection_obj.name}")
            print(f"   🎨 Material: Bright blue wireframe")
            print(f"   👁️ Display: Wireframe, show-through enabled")
            print(f"   🔍 Look for BLUE TRIANGLE extending from sensor position!")
            
            return True
            
        except ImportError:
            print(f"⚠️ Blender not available - skipping visual detection area for {sensor_id}")
            return False
        except Exception as e:
            print(f"❌ Failed to create detection area for {sensor_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_detection_area_visualization(self, sensor_id: str, detecting: bool):
        """Update visual detection area when sensor state changes
        
        Args:
            sensor_id: Motion sensor identifier  
            detecting: Whether sensor is currently detecting motion
        """
        try:
            import bpy
            
            detection_area_name = f"DetectionArea_{sensor_id}"
            detection_area = bpy.data.objects.get(detection_area_name)
            
            if detection_area and detection_area.data.materials:
                mat = detection_area.data.materials[0]
                if mat.use_nodes:
                    principled = mat.node_tree.nodes.get("Principled BSDF")
                    if principled:
                        if detecting:
                            # Bright red color when detecting motion
                            principled.inputs[0].default_value = (1.0, 0.1, 0.1, 1.0)  # Bright red
                            principled.inputs["Alpha"].default_value = 0.9  # More opaque
                            print(f"🔴 Detection area {sensor_id} - MOTION DETECTED")
                        else:
                            # Blue color when idle
                            principled.inputs[0].default_value = (0.2, 0.6, 1.0, 1.0)  # Blue
                            principled.inputs["Alpha"].default_value = 0.7  # Semi-transparent
                            print(f"🔵 Detection area {sensor_id} - Idle")
                        
                        # Force viewport update
                        for area in bpy.context.screen.areas:
                            if area.type == 'VIEW_3D':
                                area.tag_redraw()
            
            # Also update the sensor object itself
            sensor_obj_name = f"Motion_{sensor_id}"
            sensor_obj = bpy.data.objects.get(sensor_obj_name)
            
            if sensor_obj and sensor_obj.data.materials:
                sensor_mat = sensor_obj.data.materials[0]
                if sensor_mat.use_nodes:
                    sensor_principled = sensor_mat.node_tree.nodes.get("Principled BSDF")
                    if sensor_principled:
                        if detecting:
                            # Bright yellow sensor when detecting
                            sensor_principled.inputs[0].default_value = (1.0, 1.0, 0.0, 1.0)  # Yellow
                            # Add emission for glow effect
                            sensor_principled.inputs["Emission"].default_value = (1.0, 1.0, 0.0, 1.0)
                            sensor_principled.inputs["Emission Strength"].default_value = 0.5
                        else:
                            # Red or gray sensor when idle
                            is_virtual = sensor_obj.get("vesper_device_type") == "virtual_motion"
                            if is_virtual:
                                sensor_principled.inputs[0].default_value = (0.7, 0.7, 0.7, 1.0)  # Gray for virtual
                            else:
                                sensor_principled.inputs[0].default_value = (1.0, 0.0, 0.0, 1.0)  # Red for regular
                            # Remove emission
                            sensor_principled.inputs["Emission"].default_value = (0.0, 0.0, 0.0, 1.0)
                            sensor_principled.inputs["Emission Strength"].default_value = 0.0
            
        except ImportError:
            pass  # Blender not available
        except Exception as e:
            print(f"⚠️ Failed to update detection area visualization: {e}")
    
    def parent_detection_areas_to_sensors(self):
        """Parent all existing detection areas to their corresponding sensors for synchronized movement"""
        try:
            import bpy
            
            parented_count = 0
            detection_areas = [obj for obj in bpy.data.objects if obj.name.startswith("DetectionArea_")]
            
            if not detection_areas:
                print("ℹ️ No detection areas found to parent")
                return 0
            
            print(f"🔗 Parenting {len(detection_areas)} detection areas to sensors...")
            
            for detection_obj in detection_areas:
                # Extract sensor ID from detection area name
                if "DetectionArea_" in detection_obj.name:
                    sensor_id = detection_obj.name.replace("DetectionArea_", "")
                    sensor_obj_name = f"Motion_{sensor_id}"
                    sensor_obj = bpy.data.objects.get(sensor_obj_name)
                    
                    if sensor_obj and detection_obj.parent != sensor_obj:
                        # Store current world position
                        world_pos = detection_obj.matrix_world.translation.copy()
                        
                        # Set parent
                        detection_obj.parent = sensor_obj
                        detection_obj.parent_type = 'OBJECT'
                        
                        # Reset local position so triangle is centered on sensor
                        detection_obj.location = (0, 0, 0)
                        
                        # Mark as parented
                        detection_obj["is_parented"] = True
                        
                        parented_count += 1
                        print(f"   ✅ {detection_obj.name} → {sensor_obj_name}")
                    elif not sensor_obj:
                        print(f"   ⚠️ {detection_obj.name} - sensor not found: {sensor_obj_name}")
                    else:
                        print(f"   ℹ️ {detection_obj.name} - already parented")
            
            print(f"🎉 Parented {parented_count} detection areas to sensors")
            print(f"   💡 Detection areas will now move with their sensors automatically")
            return parented_count
            
        except ImportError:
            print("⚠️ Blender not available - cannot parent detection areas")
            return 0
        except Exception as e:
            print(f"❌ Failed to parent detection areas: {e}")
            return 0

# Global device manager instance
device_manager = DeviceManager()

# =============================================================================
# BGE MOTION DETECTION SYSTEM
# =============================================================================

class BGEMotionDetectionController:
    """BGE-compatible motion detection controller for game engine"""
    
    def __init__(self):
        self.enabled = True
        self.frame_count = 0
        self.last_update_time = 0
        self.update_interval = 0.1  # Update every 0.1 seconds
        self.debug_interval = 300   # Debug output every 5 seconds (300 frames at 60fps)
        
    def update(self):
        """Called every frame from BGE Always sensor"""
        if not self.enabled:
            return
            
        current_time = time.time()
        self.frame_count += 1
        
        # Throttle updates to reasonable frequency
        if current_time - self.last_update_time >= self.update_interval:
            try:
                # Import BGE modules (only available in game engine)
                import bge
                scene = bge.logic.getCurrentScene()
                
                # Get device manager from scene if available
                if hasattr(scene, 'vesper_device_manager'):
                    device_manager = scene.vesper_device_manager
                else:
                    # Initialize device manager in BGE scene
                    from . import device_manager as addon_device_manager
                    scene.vesper_device_manager = addon_device_manager
                    device_manager = addon_device_manager
                
                # Update motion detection system
                device_manager.update_motion_detection()
                self.last_update_time = current_time
                
                # Debug output occasionally
                if self.frame_count % self.debug_interval == 0:
                    status = device_manager.get_motion_detection_status()
                    detecting_count = status.get("sensors_detecting", 0)
                    if detecting_count > 0:
                        print(f"🎮 BGE Motion Detection: {detecting_count} sensors detecting motion")
                        
            except ImportError:
                # BGE not available (running in Blender editor)
                pass
            except Exception as e:
                print(f"⚠️ BGE motion detection error: {e}")

# Global BGE motion detection controller
bge_motion_controller = BGEMotionDetectionController()

def bge_motion_detection_update():
    """Main function to call from BGE Always sensor"""
    bge_motion_controller.update()

# =============================================================================
# BGE INTEGRATION SCRIPT
# =============================================================================

BGE_MOTION_SCRIPT = '''
"""
BGE Motion Detection Script
Attach this to an Always sensor (Pulse mode, Frequency = 0) in your BGE scene
Logic: Always Sensor → Python Controller → This Module
"""

def main():
    """Main BGE motion detection function - call from Always sensor"""
    try:
        import bge
        from mathutils import Vector
        import time
        
        # Get current scene and controller
        scene = bge.logic.getCurrentScene()
        controller = bge.logic.getCurrentController()
        owner = controller.owner
        
        # Initialize device manager if not already done
        if not hasattr(scene, 'vesper_device_manager'):
            try:
                # Try to import the device manager from the addon
                import sys
                import os
                
                # Add addon path to system path
                addon_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "UPBGE", "Blender", "4.4", "scripts", "addons", "vesper_smart_home")
                if addon_path not in sys.path:
                    sys.path.append(addon_path)
                
                # Import and initialize device manager
                from __init__ import device_manager
                scene.vesper_device_manager = device_manager
                
                # Initialize motion detection if available
                if hasattr(device_manager, 'motion_detector') and device_manager.motion_detector is None:
                    try:
                        from __init__ import initialize_motion_detection
                        device_manager.motion_detector = initialize_motion_detection()
                        print("🎮 BGE: Motion detection system initialized")
                    except Exception as e:
                        print(f"⚠️ BGE: Failed to initialize motion detection: {e}")
                
                print("🎮 BGE: VESPER device manager initialized in game engine")
                
            except Exception as e:
                print(f"⚠️ BGE: Failed to initialize device manager: {e}")
                return
        
        device_manager = scene.vesper_device_manager
        
        # Update motion detection system
        if hasattr(device_manager, 'update_motion_detection'):
            device_manager.update_motion_detection()
        
        # Optional: Update frame counter for debug output
        if not hasattr(scene, 'motion_frame_counter'):
            scene.motion_frame_counter = 0
        
        scene.motion_frame_counter += 1
        
        # Debug output every 5 seconds (300 frames at 60fps)
        if scene.motion_frame_counter % 300 == 0:
            try:
                status = device_manager.get_motion_detection_status()
                detecting_count = status.get("sensors_detecting", 0)
                total_sensors = status.get("total_sensors", 0)
                
                if total_sensors > 0:
                    print(f"🎮 BGE Motion Status: {detecting_count}/{total_sensors} sensors detecting")
                    
                    # Get Actor position for debug - BGE scene.objects is a list
                    actor = None
                    for obj in scene.objects:
                        if obj.name == "Actor":
                            actor = obj
                            break
                    if actor:
                        pos = actor.worldPosition
                        print(f"🎭 BGE Actor position: [{pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f}]")
                    
            except Exception as e:
                print(f"⚠️ BGE: Status check error: {e}")
    
    except Exception as e:
        print(f"❌ BGE: Motion detection script error: {e}")

# Call main function
if __name__ == "__main__":
    main()
'''

# =============================================================================
# MOTION DETECTION FRAME HANDLER (for Blender editor mode)
# =============================================================================

class MotionDetectionHandler:
    """Frame handler for continuous motion detection in BGE/UPBGE"""
    
    def __init__(self):
        self.enabled = True
        self.frame_count = 0
        self.last_update_time = 0
        self.update_interval = 0.1  # Update every 0.1 seconds (10 FPS for detection)
        self.debug_interval = 60   # Debug output every 60 frames
        
    def frame_update(self):
        """Called every frame to update motion detection"""
        if not self.enabled:
            return
            
        current_time = time.time()
        self.frame_count += 1
        
        # Throttle updates to reasonable frequency
        if current_time - self.last_update_time >= self.update_interval:
            try:
                # Update motion detection system
                device_manager.update_motion_detection()
                self.last_update_time = current_time
                
                # Debug output occasionally
                if self.frame_count % self.debug_interval == 0:
                    status = device_manager.get_motion_detection_status()
                    detecting_count = status.get("sensors_detecting", 0)
                    if detecting_count > 0:
                        print(f"🔍 Motion Detection Status: {detecting_count} sensors detecting motion")
                        
            except Exception as e:
                print(f"⚠️ Motion detection frame handler error: {e}")
    
    def enable(self):
        """Enable motion detection updates"""
        self.enabled = True
        print("✅ Motion detection frame handler enabled")
    
    def disable(self):
        """Disable motion detection updates"""
        self.enabled = False
        print("⏸️ Motion detection frame handler disabled")

# Global motion detection handler
motion_handler = MotionDetectionHandler()

def motion_detection_frame_handler(scene, depsgraph):
    """Blender frame handler for motion detection"""
    motion_handler.frame_update()

# =============================================================================
# BLENDER INTEGRATION FUNCTIONS  
# =============================================================================

def create_device_visual(device_id: str, device_type: str, position: Vector, room: str = "") -> bpy.types.Object:
    """Create visual representation of device in Blender scene"""
    
    # Create different shapes for different device types
    if device_type == "motion":
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, location=position)
        obj = bpy.context.active_object
        obj.name = f"Motion_{device_id}"
        
        # Create red material for motion sensors
        mat = bpy.data.materials.new(name=f"Motion_Material_{device_id}")
        if mat.use_nodes:
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 0, 0, 1)  # Red
        obj.data.materials.append(mat)
        
    elif device_type == "item":
        bpy.ops.mesh.primitive_cube_add(size=0.2, location=position)
        obj = bpy.context.active_object
        obj.name = f"Item_{device_id}"
        
        # Create blue material for item sensors
        mat = bpy.data.materials.new(name=f"Item_Material_{device_id}")
        if mat.use_nodes:
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, 0, 1, 1)  # Blue
        obj.data.materials.append(mat)
        
    elif device_type == "appliance":
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=position)
        obj = bpy.context.active_object
        obj.name = f"Appliance_{device_id}"
        
        # Create green material for appliances
        mat = bpy.data.materials.new(name=f"Appliance_Material_{device_id}")
        if mat.use_nodes:
            mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0, 1, 0, 1)  # Green
        obj.data.materials.append(mat)
    
    # Add custom properties to track device info
    obj["vesper_device_id"] = device_id
    obj["vesper_device_type"] = device_type
    obj["vesper_room"] = room
    
    return obj

def create_virtual_device_visual(device_info: dict, position: Vector) -> bpy.types.Object:
    """Create visual representation of virtual device from backend console"""
    serial = device_info.get("serial_number", "unknown")
    config = device_info.get("config_file", "unknown")
    original_type = device_info.get("original_device_type", "unknown")
    container_info = device_info.get("container_info", {})
    
    # Create a distinctive shape for virtual devices
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=position)
    obj = bpy.context.active_object
    obj.name = f"VirtualDevice_{serial}"
    
    # Create distinctive material for virtual devices
    mat = bpy.data.materials.new(name=f"Virtual_Material_{serial}")
    if mat.use_nodes:
        # Purple/magenta for virtual devices
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.2, 0.8, 1)
        if "Emission" in mat.node_tree.nodes["Principled BSDF"].inputs:
            mat.node_tree.nodes["Principled BSDF"].inputs["Emission"].default_value = (0.3, 0.1, 0.3, 1)
            mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0
    obj.data.materials.append(mat)
    
    # Add custom properties for virtual devices
    obj["vesper_device_type"] = "virtual"
    obj["vesper_serial_number"] = serial
    obj["vesper_config"] = config
    obj["vesper_username"] = device_info.get("username", "admin")
    obj["vesper_original_type"] = original_type
    
    # Add container information if available
    if container_info:
        obj["vesper_container_name"] = container_info.get("container_name", "unknown")
        obj["vesper_container_port"] = container_info.get("port", 0)
        obj["vesper_container_id"] = container_info.get("container_id", "unknown")
    
    return obj

def update_device_visual_state(device_id: str, state: str):
    """Update visual representation based on device state"""
    for obj in bpy.data.objects:
        if obj.get("vesper_device_id") == device_id:
            # Change material emission based on state
            if obj.data.materials:
                mat = obj.data.materials[0]
                if mat.use_nodes:
                    principled = mat.node_tree.nodes.get("Principled BSDF")
                    if principled:
                        if state in ["active", "ON", "absent"]:
                            principled.inputs["Emission"].default_value = (1, 1, 1, 1)  # Bright when active
                            principled.inputs["Emission Strength"].default_value = 2.0
                        else:
                            principled.inputs["Emission"].default_value = (0, 0, 0, 1)  # Dark when inactive
                            principled.inputs["Emission Strength"].default_value = 0.0
            break

def auto_detect_room(position: Vector) -> str:
    """Auto-detect room based on position"""
    if position.x < 0 and position.y > 0:
        return "kitchen"
    elif position.x > 0 and position.y > 0:
        return "living_room"
    elif position.x < 0 and position.y < 0:
        return "bathroom"
    elif position.x > 0 and position.y < 0:
        return "bedroom"
    else:
        return "hallway"

# =============================================================================
# BLENDER OPERATORS
# =============================================================================

class VESPER_OT_CheckServices(bpy.types.Operator):
    """Check Docker services health"""
    bl_idname = "vesper_smart.check_services"
    bl_label = "Check Services"
    bl_description = "Check Docker services status"
    
    def execute(self, context):
        if not REQUESTS_AVAILABLE:
            self.report({'ERROR'}, "requests module not available")
            return {'CANCELLED'}
        
        health = device_manager.check_services_health()
        all_healthy = all(health.values())
        
        if all_healthy:
            self.report({'INFO'}, "All Docker services running!")
        else:
            failed = [k for k, v in health.items() if not v]
            self.report({'WARNING'}, f"Services down: {', '.join(failed)}")
        
        # Print detailed status
        print(" Docker Services Status:")
        for service, status in health.items():
            icon = "" if status else ""
            print(f"  {icon} {service}: {'Running' if status else 'Down'}")
        
        return {'FINISHED'}

class VESPER_OT_AddMotionSensor(bpy.types.Operator):
    """Add motion sensor at cursor location"""
    bl_idname = "vesper_smart.add_motion_sensor"
    bl_label = "Add Motion Sensor"
    bl_description = "Add motion sensor at 3D cursor"
    
    sensor_id: bpy.props.StringProperty(name="Sensor ID", default="M")
    room: bpy.props.StringProperty(name="Room", default="")
    
    def execute(self, context):
        cursor_location = context.scene.cursor.location.copy()
        room = self.room if self.room else auto_detect_room(cursor_location)
        
        # Generate ID
        existing = [obj for obj in bpy.data.objects if obj.name.startswith("Motion_")]
        sensor_id = f"M{len(existing) + 1:02d}" if self.sensor_id == "M" else self.sensor_id
        
        # Create visual device
        create_device_visual(sensor_id, "motion", cursor_location, room)
        
        # Add to Docker if available
        if REQUESTS_AVAILABLE:
            if device_manager.add_motion_sensor(sensor_id, room, cursor_location):
                self.report({'INFO'}, f"Added motion sensor {sensor_id} in {room}")
            else:
                self.report({'WARNING'}, f"Added visual sensor {sensor_id} (Docker failed)")
        else:
            self.report({'INFO'}, f"Added visual sensor {sensor_id} (Docker not available)")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class VESPER_OT_AddItemSensor(bpy.types.Operator):
    """Add item sensor at cursor location"""
    bl_idname = "vesper_smart.add_item_sensor"
    bl_label = "Add Item Sensor"
    bl_description = "Add item sensor at 3D cursor"
    
    sensor_id: bpy.props.StringProperty(name="Sensor ID", default="I")
    item_name: bpy.props.StringProperty(name="Item Name", default="item")
    
    def execute(self, context):
        cursor_location = context.scene.cursor.location.copy()
        
        # Generate ID
        existing = [obj for obj in bpy.data.objects if obj.name.startswith("Item_")]
        sensor_id = f"I{len(existing) + 1:02d}" if self.sensor_id == "I" else self.sensor_id
        
        # Create visual device
        create_device_visual(sensor_id, "item", cursor_location, self.item_name)
        
        # Add to Docker if available
        if REQUESTS_AVAILABLE:
            if device_manager.add_item_sensor(sensor_id, self.item_name, cursor_location):
                self.report({'INFO'}, f"Added item sensor {sensor_id} for {self.item_name}")
            else:
                self.report({'WARNING'}, f"Added visual item {sensor_id} (Docker failed)")
        else:
            self.report({'INFO'}, f"Added visual item {sensor_id} (Docker not available)")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class VESPER_OT_TriggerDevice(bpy.types.Operator):
    """Trigger selected device"""
    bl_idname = "vesper_smart.trigger_device"
    bl_label = "Trigger Device"
    bl_description = "Trigger selected device"
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or "vesper_device_id" not in obj:
            self.report({'ERROR'}, "No VESPER device selected")
            return {'CANCELLED'}
        
        device_id = obj["vesper_device_id"]
        device_type = obj["vesper_device_type"]
        
        success = False
        
        # Trigger based on device type
        if device_type == "motion" and REQUESTS_AVAILABLE:
            success = device_manager.trigger_motion_sensor(device_id, "active")
        elif device_type == "item" and REQUESTS_AVAILABLE:
            success = device_manager.interact_with_item(device_id, "absent")
        
        # Visual feedback
        if device_type == "motion":
            update_device_visual_state(device_id, "active")
        elif device_type == "item":
            update_device_visual_state(device_id, "absent")
        
        if success:
            self.report({'INFO'}, f"Triggered device {device_id}")
        else:
            self.report({'INFO'}, f"Visual trigger {device_id} (Docker not available)")
        
        return {'FINISHED'}

class VESPER_OT_RemoveDevice(bpy.types.Operator):
    """Remove selected device"""
    bl_idname = "vesper_smart.remove_device"
    bl_label = "Remove Device"
    bl_description = "Remove selected device"
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or "vesper_device_id" not in obj:
            self.report({'ERROR'}, "No VESPER device selected")
            return {'CANCELLED'}
        
        device_id = obj["vesper_device_id"]
        bpy.data.objects.remove(obj, do_unlink=True)
        
        self.report({'INFO'}, f"Removed device {device_id}")
        return {'FINISHED'}

class VESPER_OT_StartDockerServices(bpy.types.Operator):
    """Start Docker services helper"""
    bl_idname = "vesper_smart.start_docker"
    bl_label = "Docker Help"
    bl_description = "Instructions to start Docker services"
    
    def execute(self, context):
        message = """To start Docker services:
1. Open PowerShell/Terminal
2. Navigate to: C:\\Users\\hbui11\\Desktop\\vesper_llm\\virtual-interaction
3. Run: docker-compose -f docker-compose.casas.yml up -d
4. Wait 30-60 seconds
5. Click 'Check Services' to verify"""
        
        self.report({'INFO'}, "Check console for Docker instructions")
        print(" DOCKER SETUP INSTRUCTIONS:")
        print(message)
        return {'FINISHED'}

# =============================================================================
# VIRTUAL DEVICE OPERATORS
# =============================================================================

class VESPER_OT_SpawnVirtualDevice(bpy.types.Operator):
    """Spawn virtual device using backend console API"""
    bl_idname = "vesper_smart.spawn_virtual_device"
    bl_label = "Spawn Virtual Device"
    bl_description = "Spawn virtual smart home device (like web UI)"
    
    device_type: bpy.props.EnumProperty(
        name="Device Type",
        description="Type of virtual device to spawn",
        items=[
            # Core Smart Home Devices
            ("thermostat", "🌡️ Thermostat", "Smart thermostat with temperature control and scheduling"),
            ("motion-sensor", "🚶 Motion Sensor", "PIR motion detection sensor for room occupancy"),
            ("item-sensor", "📦 Item Sensor", "RFID/NFC item tracking and inventory sensor"),
            ("appliance-controller", "🔌 Appliance Controller", "Smart plug/outlet for appliance control"),
            
            # Advanced Sensors
            ("door-sensor", "🚪 Door/Window Sensor", "Magnetic door/window open/close sensor"),
            ("temperature-sensor", "🌡️ Temperature Sensor", "Standalone temperature monitoring"),
            ("humidity-sensor", "💧 Humidity Sensor", "Environmental humidity monitoring"),
            ("light-sensor", "💡 Light/Luminosity Sensor", "Ambient light level detection"),
            ("smoke-detector", "🔥 Smoke Detector", "Fire/smoke detection and alarm"),
            ("water-leak-sensor", "💧 Water Leak Sensor", "Water leak detection and flood prevention"),
            
            # Smart Controls
            ("smart-switch", "💡 Smart Light Switch", "WiFi-enabled light switch control"),
            ("smart-dimmer", "🔅 Smart Dimmer", "Dimmable light control with scheduling"),
            ("smart-lock", "🔐 Smart Door Lock", "Electronic door lock with keypad/app control"),
            ("garage-door", "🏠 Garage Door Controller", "Smart garage door opener/closer"),
            
            # Environmental Controls
            ("air-quality-sensor", "🌬️ Air Quality Monitor", "CO2, VOC, and air quality monitoring"),
            ("weather-station", "⛅ Weather Station", "Indoor/outdoor weather monitoring"),
            ("uv-sensor", "☀️ UV Index Sensor", "UV radiation level monitoring"),
            
            # Security & Safety
            ("security-camera", "📷 Security Camera", "WiFi security camera with motion detection"),
            ("glass-break-sensor", "🔨 Glass Break Sensor", "Glass breakage detection for windows"),
            ("vibration-sensor", "📳 Vibration Sensor", "Vibration and impact detection"),
            ("panic-button", "🚨 Panic/Emergency Button", "Emergency alert button"),
            
            # Smart Appliances  
            ("smart-tv", "📺 Smart TV Controller", "TV power and input control"),
            ("coffee-maker", "☕ Smart Coffee Maker", "Programmable coffee brewing"),
            ("robot-vacuum", "🤖 Robot Vacuum", "Automated vacuum cleaner control"),
            ("air-purifier", "🌬️ Air Purifier", "Smart air filtration control"),
            
            # Research & Data
            ("casas-dataset-manager", "📊 CASAS Dataset Manager", "Research data collection and management"),
            ("energy-monitor", "⚡ Energy Monitor", "Power consumption tracking"),
            ("occupancy-counter", "👥 Occupancy Counter", "People counting and tracking"),
        ],
        default="motion-sensor"
    )
    username: bpy.props.StringProperty(name="Username", default="admin")
    device_location: bpy.props.EnumProperty(
        name="Room/Location",
        description="Where to place the device in the smart home",
        items=[
            ("living_room", "🛋️ Living Room", "Main living area"),
            ("kitchen", "🍳 Kitchen", "Cooking and dining area"),
            ("bedroom", "🛏️ Bedroom", "Master bedroom"),
            ("bedroom2", "🛏️ Bedroom 2", "Guest/secondary bedroom"),
            ("bathroom", "🚿 Bathroom", "Main bathroom"),
            ("bathroom2", "🚿 Bathroom 2", "Guest bathroom"),
            ("office", "💻 Home Office", "Work/study room"),
            ("garage", "🏠 Garage", "Vehicle storage area"),
            ("basement", "🏠 Basement", "Lower level/storage"),
            ("attic", "🏠 Attic", "Upper level/storage"),
            ("hallway", "🚪 Hallway", "Corridor/passage"),
            ("entryway", "🚪 Entryway", "Front door/foyer"),
            ("patio", "🌿 Patio/Deck", "Outdoor living space"),
            ("laundry", "👕 Laundry Room", "Washing/drying area"),
            ("pantry", "🥫 Pantry", "Food storage"),
            ("closet", "👔 Closet", "Storage closet"),
        ],
        default="living_room"
    )
    config_type: bpy.props.EnumProperty(
        name="Configuration",
        description="Device configuration type",
        items=[
            ("small_apartment_efficient", "🏠 Small Apartment (Efficient)", "Energy-efficient small space setup"),
            ("small_apartment_inefficient", "🏠 Small Apartment (Standard)", "Standard small space setup"),
            ("medium_house_efficient", "🏡 Medium House (Efficient)", "Energy-efficient medium home setup"),
            ("medium_house_standard", "🏡 Medium House (Standard)", "Standard medium home setup"),
            ("large_house_smart", "🏰 Large House (Smart)", "Fully automated large home setup"),
            ("custom", "⚙️ Custom Configuration", "Custom device configuration")
        ],
        default="medium_house_efficient"
    )
    
    device_name: bpy.props.StringProperty(
        name="Device Name",
        description="Custom name for the device (used in Docker container name for easier tracking)",
        default="",
        maxlen=32
    )
    
    def execute(self, context):
        if not REQUESTS_AVAILABLE:
            self.report({'ERROR'}, "requests module required")
            return {'CANCELLED'}
        
        # Spawn virtual device
        device_info = device_manager.spawn_virtual_device(self.device_type, self.username, self.config_type, device_name=self.device_name)
        
        if device_info:
            # Add location info to device
            device_info["location"] = self.device_location
            
            # Create visual representation at cursor
            cursor_location = context.scene.cursor.location.copy()
            create_virtual_device_visual(device_info, cursor_location)
            
            serial = device_info.get("serial_number")
            location = self.device_location.replace("_", " ").title()
            self.report({'INFO'}, f"✅ Spawned {self.device_type} '{serial}' in {location}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"❌ Failed to spawn {self.device_type}")
            return {'CANCELLED'}
    
    def get_docker_container_name(self, device_type):
        """Get the Docker container name for testing purposes"""
        mapped_type = device_manager.map_device_type(device_type)
        container_mapping = {
            "thermostat": "testbed-thermostat",
            "motion-sensor": "testbed-motion-sensor", 
            "item-sensor": "testbed-item-sensor",
            "appliance-controller": "testbed-appliance-controller",
            "casas-dataset-manager": "testbed-casas-dataset-manager"
        }
        return container_mapping.get(mapped_type, "testbed-motion-sensor")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)
    
    def draw(self, context):
        layout = self.layout
        
        # Main device configuration
        layout.prop(self, "device_type")
        layout.prop(self, "device_location")
        layout.prop(self, "username")
        layout.prop(self, "device_name")
        
        # Show Docker mapping for testing
        layout.separator()
        box = layout.box()
        box.label(text="🐳 Docker Container Mapping (for Testing):", icon='INFO')
        
        mapped_type = device_manager.map_device_type(self.device_type)
        container_name = self.get_docker_container_name(self.device_type)
        
        col = box.column(align=True)
        col.label(text=f"Device Type: {self.device_type}")
        col.label(text=f"Backend Type: {mapped_type}")
        col.label(text=f"Container: {container_name}")
        
        if mapped_type != self.device_type:
            col.label(text="ℹ️ This device type maps to an existing backend", icon='INFO')

class VESPER_OT_DeleteVirtualDevice(bpy.types.Operator):
    """Delete selected virtual device"""
    bl_idname = "vesper_smart.delete_virtual_device"
    bl_label = "Delete Virtual Device"
    bl_description = "Delete selected virtual device"
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.get("vesper_device_type") != "virtual":
            self.report({'ERROR'}, "No virtual device selected")
            return {'CANCELLED'}
        
        serial = obj.get("vesper_serial_number")
        if not serial:
            self.report({'ERROR'}, "Invalid device selected")
            return {'CANCELLED'}
        
        # Get container information from the Blender object
        container_name = obj.get("vesper_container_name")
        
        # Delete from backend and Docker container
        backend_deleted = device_manager.delete_virtual_device(serial)
        
        # Also try to delete container using info from Blender object if backend deletion missed it
        container_deleted = True
        if container_name and container_name != "unknown":
            container_deleted = device_manager.delete_docker_container(container_name)
        
        if backend_deleted or container_deleted:
            # Remove visual
            bpy.data.objects.remove(obj, do_unlink=True)
            if backend_deleted and container_deleted:
                self.report({'INFO'}, f"✅ Deleted virtual device and container: {serial}")
            elif backend_deleted:
                self.report({'INFO'}, f"✅ Deleted virtual device: {serial} (container may need manual cleanup)")
            else:
                self.report({'INFO'}, f"✅ Deleted container: {container_name} (backend may need manual cleanup)")
        else:
            self.report({'ERROR'}, f"❌ Failed to delete device: {serial}")
        
        return {'FINISHED'}

class VESPER_OT_ListVirtualDevices(bpy.types.Operator):
    """List all virtual devices"""
    bl_idname = "vesper_smart.list_virtual_devices"
    bl_label = "List Virtual Devices"
    bl_description = "Show all active virtual devices"
    
    def execute(self, context):
        devices = device_manager.get_virtual_devices()
        
        if not devices:
            self.report({'INFO'}, "No virtual devices found")
        else:
            print(f"\\n📱 Active Virtual Devices ({len(devices)}):")
            for device in devices:
                serial = device.get("serial_number", "unknown")
                config = device.get("config_file", "unknown") 
                status = "running" if device.get("current_state", {}).get("is_running") else "idle"
                temp = device.get("current_state", {}).get("temperature", "unknown")
                print(f"  • {serial}: {config} - {status} - {temp}°F")
            
            self.report({'INFO'}, f"Found {len(devices)} virtual devices (check console)")
        
        return {'FINISHED'}

class VESPER_OT_ListDockerContainers(bpy.types.Operator):
    """List all individual Docker containers for virtual devices"""
    bl_idname = "vesper_smart.list_docker_containers"
    bl_label = "List Docker Containers"
    bl_description = "Show all individual Docker containers for virtual devices"
    
    def execute(self, context):
        import subprocess
        
        try:
            # Get all containers with names containing device types
            cmd = ["docker", "ps", "--format", "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                device_containers = []
                
                # Filter for individual device containers (not testbed- containers)
                for line in lines[1:]:  # Skip header
                    if any(device_type in line for device_type in [
                        "motion-sensor-", "item-sensor-", "appliance-controller-",
                        "thermostat-", "casas-dataset-manager-", "temperature-sensor-",
                        "door-sensor-", "smart-switch-", "coffee-maker-"
                    ]):
                        device_containers.append(line)
                
                print(f"\\n🐳 Individual Device Containers ({len(device_containers)}):")
                if device_containers:
                    print("  " + lines[0])  # Header
                    for container in device_containers:
                        print("  " + container)
                    self.report({'INFO'}, f"Found {len(device_containers)} device containers (check console)")
                else:
                    print("  No individual device containers found")
                    self.report({'INFO'}, "No individual device containers found")
            else:
                self.report({'ERROR'}, f"Failed to list containers: {result.stderr}")
                
        except Exception as e:
            self.report({'ERROR'}, f"Error listing containers: {e}")
        
        return {'FINISHED'}

class VESPER_OT_ControlVirtualDevice(bpy.types.Operator):
    """Control selected virtual device"""
    bl_idname = "vesper_smart.control_virtual_device"
    bl_label = "Control Virtual Device"
    bl_description = "Control selected virtual device"
    
    command_type: bpy.props.EnumProperty(
        name="Command",
        items=[
            ("setpoint", "Set Temperature", ""),
            ("mode", "Set Mode", ""),
            ("weather", "Override Weather", ""),
            ("current_temp", "Set Current Temperature", "")
        ],
        default="setpoint"
    )
    
    temperature: bpy.props.FloatProperty(name="Temperature", default=72.0, min=50.0, max=90.0)
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[("auto", "Auto", ""), ("heat", "Heat", ""), ("cool", "Cool", ""), ("off", "Off", "")],
        default="auto"
    )
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.get("vesper_device_type") != "virtual":
            self.report({'ERROR'}, "No virtual device selected")
            return {'CANCELLED'}
        
        serial = obj.get("vesper_serial_number")
        value = self.mode if self.command_type == "mode" else self.temperature
        
        if device_manager.control_virtual_device(serial, self.command_type, value):
            self.report({'INFO'}, f"Sent {self.command_type} command to {serial}")
        else:
            self.report({'ERROR'}, f"Failed to control device {serial}")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class VESPER_OT_CleanupAllDevices(bpy.types.Operator):
    """Delete all virtual devices and their Docker containers"""
    bl_idname = "vesper_smart.cleanup_all_devices"
    bl_label = "Cleanup All Virtual Devices"
    bl_description = "Delete all virtual devices and Docker containers (DANGEROUS)"
    
    def execute(self, context):
        devices = device_manager.get_virtual_devices()
        deleted_count = 0
        container_count = 0
        
        # Also remove all virtual device visuals in Blender
        visual_objects = [obj for obj in bpy.data.objects if obj.get("vesper_device_type") == "virtual"]
        
        for device in devices:
            serial = device.get("serial_number")
            if serial and device_manager.delete_virtual_device(serial):
                deleted_count += 1
                
                # Remove visual if it exists
                for obj in visual_objects:
                    if obj.get("vesper_serial_number") == serial:
                        bpy.data.objects.remove(obj, do_unlink=True)
                        visual_objects.remove(obj)
                        break
        
        # Remove any remaining visual objects (in case backend deletion failed)
        for obj in visual_objects:
            container_name = obj.get("vesper_container_name")
            if container_name and container_name != "unknown":
                if device_manager.delete_docker_container(container_name):
                    container_count += 1
            bpy.data.objects.remove(obj, do_unlink=True)
        
        if container_count > 0:
            self.report({'INFO'}, f"✅ Cleaned up {deleted_count} devices + {container_count} containers")
        else:
            self.report({'INFO'}, f"✅ Cleaned up {deleted_count} virtual devices")
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="⚠️ This will delete ALL virtual devices!", icon='ERROR')
        layout.label(text="🐳 This will also remove all Docker containers!")
        layout.label(text="Are you sure you want to continue?")
        
        # Count devices for confirmation
        devices = device_manager.get_virtual_devices() if REQUESTS_AVAILABLE else []
        visual_objects = [obj for obj in bpy.data.objects if obj.get("vesper_device_type") == "virtual"]
        
        box = layout.box()
        box.label(text=f"📱 Backend devices to delete: {len(devices)}")
        box.label(text=f"👁️ Visual objects to remove: {len(visual_objects)}")
        
        if len(visual_objects) > len(devices):
            box.label(text="⚠️ Some visual objects may have orphaned containers")

class VESPER_OT_SetupBGEMotionDetection(bpy.types.Operator):
    """Setup BGE motion detection system"""
    bl_idname = "vesper_smart.setup_bge_motion"
    bl_label = "Setup BGE"
    bl_description = "Setup motion detection for Blender Game Engine (press P)"
    
    def execute(self, context):
        try:
            # Create BGE motion detection script file in workspace
            workspace_script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vesper_llm", "blender", "bge_motion_detection.py")
            
            # Also create in addon directory for easy access
            script_dir = os.path.join(os.path.dirname(__file__), "bge_scripts")
            os.makedirs(script_dir, exist_ok=True)
            script_path = os.path.join(script_dir, "bge_motion_detection.py")
            
            with open(script_path, 'w') as f:
                f.write(BGE_MOTION_SCRIPT)
            
            print(f"✅ Created BGE motion detection script: {script_path}")
            
            # Check if we have an Actor object
            actor = bpy.data.objects.get("Actor")
            if not actor:
                # Create a simple Actor cube
                bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
                actor = bpy.context.active_object
                actor.name = "Actor"
                
                # Make it slightly blue to distinguish it
                mat = bpy.data.materials.new(name="Actor_Material")
                mat.use_nodes = True
                if mat.node_tree and mat.node_tree.nodes.get("Principled BSDF"):
                    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.3, 1.0, 1.0)  # Blue
                actor.data.materials.append(mat)
                
                print("✅ Created Actor object (blue cube)")
            
            # Check for motion sensors
            motion_sensors = [obj for obj in bpy.data.objects if obj.name.startswith("Motion_")]
            
            # Create a text block with the BGE script for easy access
            if "bge_motion_detection.py" not in bpy.data.texts:
                bge_text = bpy.data.texts.new("bge_motion_detection.py")
                bge_text.write(BGE_MOTION_SCRIPT)
                print("✅ Created BGE script text block in Blender")
            
            instructions = [
                "🎮 BGE Motion Detection Setup Complete!",
                "",
                "📋 Quick Setup Method:",
                "1. Click 'Create Controller' button below",
                "2. Select the VESPER_MotionController object",
                "3. Go to Logic Properties panel (🎮 icon)",
                "4. Add Always Sensor (Pulse: OFF, Frequency: 0)",
                "5. Add Python Controller → Text: bge_motion_detection.py → main",
                "6. Press P to start the game engine!",
                "",
                "📋 Manual Setup Method:",
                "1. Add Empty object to scene",
                "2. Select it and go to Logic Properties",
                "3. Add Always Sensor (Pulse: OFF)",
                "4. Add Python Controller → Text: bge_motion_detection.py → main",
                "5. Press P to start game engine",
                "",
                f"📊 Current Setup:",
                f"   • Actor object: {'✅ Found' if actor else '❌ Missing'}",
                f"   • Motion sensors: {len(motion_sensors)} found",
                f"   • BGE script: ✅ Created in Text Editor",
                "",
                "💡 In BGE, manually move the Actor to test motion detection!",
                "🎯 Detection areas will turn RED when Actor is in range!"
            ]
            
            for line in instructions:
                print(line)
            
            self.report({'INFO'}, f"BGE setup complete! {len(motion_sensors)} sensors ready")
            
        except Exception as e:
            print(f"❌ Failed to setup BGE motion detection: {e}")
            self.report({'ERROR'}, f"Setup failed: {e}")
            
        return {'FINISHED'}

class VESPER_OT_CreateBGEController(bpy.types.Operator):
    """Create BGE motion detection controller object"""
    bl_idname = "vesper_smart.create_bge_controller"
    bl_label = "Create Controller"
    bl_description = "Create Empty object with BGE motion detection logic"
    
    def execute(self, context):
        try:
            # Create Empty object for BGE controller
            bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
            controller = bpy.context.active_object
            controller.name = "VESPER_MotionController"
            
            # Add game properties for configuration
            bpy.ops.object.game_property_new()
            controller.game.properties[-1].name = "motion_detection_enabled"
            controller.game.properties[-1].type = 'BOOL'
            controller.game.properties[-1].value = True
            
            print("✅ Created VESPER Motion Controller object")
            print("📋 Next steps:")
            print("   1. Select the VESPER_MotionController object")
            print("   2. Go to Logic Properties panel")
            print("   3. Add Always Sensor (Pulse: OFF)")
            print("   4. Add Python Controller → Script: bge_motion_detection.py → main")
            print("   5. Press P to test in game engine!")
            
            self.report({'INFO'}, "BGE controller created! Add logic bricks manually.")
            
        except Exception as e:
            print(f"❌ Failed to create BGE controller: {e}")
            self.report({'ERROR'}, f"Controller creation failed: {e}")
            
        return {'FINISHED'}

class VESPER_OT_CreateBGEDemo(bpy.types.Operator):
    """Create complete BGE motion detection demo scene"""
    bl_idname = "vesper_smart.create_bge_demo"
    bl_label = "Demo Scene"
    bl_description = "Create a complete demo scene for BGE motion detection testing"
    
    def execute(self, context):
        try:
            # Create Actor
            if not bpy.data.objects.get("Actor"):
                bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
                actor = bpy.context.active_object
                actor.name = "Actor"
                
                # Blue material for Actor
                mat = bpy.data.materials.new(name="Actor_Material")
                mat.use_nodes = True
                if mat.node_tree and mat.node_tree.nodes.get("Principled BSDF"):
                    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.3, 1.0, 1.0)
                actor.data.materials.append(mat)
                print("✅ Created Actor (blue cube)")
            
            # Create a few motion sensors strategically placed
            sensor_positions = [
                (-3, 3, 2, "living_room"),
                (3, -3, 2, "bedroom"), 
                (0, 4, 2, "kitchen"),
                (-4, -2, 2, "bathroom")
            ]
            
            sensors_created = 0
            for i, (x, y, z, room) in enumerate(sensor_positions):
                sensor_id = f"M{i+1:02d}"
                existing_sensor = bpy.data.objects.get(f"Motion_{sensor_id}")
                
                if not existing_sensor:
                    # Position cursor and add sensor
                    bpy.context.scene.cursor.location = (x, y, z)
                    
                    # Use the addon's motion sensor creation
                    success = device_manager.add_motion_sensor(sensor_id, room, Vector((x, y, z)), orientation=0)
                    
                    if success:
                        sensors_created += 1
                        print(f"✅ Created motion sensor {sensor_id} in {room}")
            
            # Create ground plane
            if not bpy.data.objects.get("Ground"):
                bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
                ground = bpy.context.active_object
                ground.name = "Ground"
                
                # Gray material for ground
                mat = bpy.data.materials.new(name="Ground_Material")
                mat.use_nodes = True
                if mat.node_tree and mat.node_tree.nodes.get("Principled BSDF"):
                    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.5, 0.5, 0.5, 1.0)
                ground.data.materials.append(mat)
                print("✅ Created ground plane")
            
            # Set up BGE motion detection
            bpy.ops.vesper_smart.setup_bge_motion()
            bpy.ops.vesper_smart.create_bge_controller()
            
            print("\n🎮 BGE Motion Detection Demo Scene Created!")
            print(f"   📊 {sensors_created} motion sensors placed")
            print("   🎭 Actor ready for testing")
            print("   🎮 BGE controller configured")
            print("\n📋 Final Steps:")
            print("   1. Select VESPER_MotionController")
            print("   2. Logic Properties → Add Always Sensor (Pulse OFF)")
            print("   3. Add Python Controller → Text: bge_motion_detection.py → main")
            print("   4. Press P to start game engine")
            print("   5. Move Actor around to trigger sensors!")
            
            self.report({'INFO'}, f"Demo scene created! {sensors_created} sensors ready")
            
        except Exception as e:
            print(f"❌ Failed to create BGE demo: {e}")
            self.report({'ERROR'}, f"Demo creation failed: {e}")
            
        return {'FINISHED'}

class VESPER_OT_FixDetectionAreas(bpy.types.Operator):
    """Fix detection area parenting to sensors"""
    bl_idname = "vesper_smart.fix_detection_areas"
    bl_label = "Fix Detection Areas"
    bl_description = "Parent detection areas to their sensors so they move together"
    
    def execute(self, context):
        parented_count = device_manager.parent_detection_areas_to_sensors()
        
        if parented_count > 0:
            self.report({'INFO'}, f"✅ Fixed {parented_count} detection areas")
        else:
            self.report({'WARNING'}, "⚠️ No detection areas needed fixing")
        
        return {'FINISHED'}

# =============================================================================
# UI PANEL
# =============================================================================

class VESPER_PT_SmartHomePanel(bpy.types.Panel):
    """VESPER Smart Home control panel"""
    bl_label = "Smart Home"
    bl_idname = "VESPER_PT_smart_home_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VESPER'
    
    def draw(self, context):
        layout = self.layout
        
        # Header
        row = layout.row()
        row.label(text="🏠 VESPER Smart Home", icon='HOME')
        
        # Status section
        if not REQUESTS_AVAILABLE:
            box = layout.box()
            box.alert = True
            box.label(text="⚠️ Limited Mode", icon='ERROR')
            box.label(text="Missing: requests module")
            box.label(text="Install: pip install requests")
        
        # Virtual Device Management Section
        box = layout.box()
        box.label(text="Virtual Device Management", icon='NETWORK_DRIVE')
        
        if not REQUESTS_AVAILABLE:
            box.label(text="requests module required", icon='ERROR')
        else:
            row = box.row()
            row.operator("vesper_smart.spawn_virtual_device", icon='ADD')
            
            row = box.row()
            row.operator("vesper_smart.delete_virtual_device", icon='REMOVE')
            row.operator("vesper_smart.control_virtual_device", icon='SETTINGS')
            
            row = box.row()
            row.operator("vesper_smart.list_virtual_devices", icon='PRESET')
            row.operator("vesper_smart.list_docker_containers", icon='PREFERENCES', text="Containers")
            
            box.separator()
            row = box.row()
            row.operator("vesper_smart.cleanup_all_devices", icon='TRASH', text="Cleanup All")
            row.operator("vesper_smart.fix_detection_areas", icon='LINKED', text="Fix Areas")
        
        # Motion Detection System section
        layout.separator()
        box = layout.box()
        box.label(text="VLM Motion Detection (BGE)", icon='PLAY')
        
        # BGE mode setup only
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("vesper_smart.setup_bge_motion", icon='SCRIPT', text="Setup BGE")
        row.operator("vesper_smart.create_bge_controller", icon='EMPTY_AXIS', text="Controller")
        
        row = col.row()
        row.operator("vesper_smart.create_bge_demo", icon='SCENE_DATA', text="Create Demo Scene")
        
        # Instructions
        col = box.column()
        col.scale_y = 0.8
        col.label(text="💡 Setup BGE, then press P for VLM testing!", icon='INFO')
        col.label(text="🎯 Motion sensors will detect actor automatically", icon='INFO')
        
        # Docker services section
        layout.separator()
        box = layout.box()
        box.label(text="Docker Services", icon='PREFERENCES')
        
        row = box.row(align=True)
        row.operator("vesper_smart.check_services", icon='CHECKMARK')
        row.operator("vesper_smart.start_docker", icon='CONSOLE', text="Help")
        
        # Status Section
        layout.separator()
        box = layout.box()
        box.label(text="Selected Device", icon='INFO')
        
        obj = context.active_object
        if obj and "vesper_device_type" in obj:
            device_type = obj["vesper_device_type"]
            if device_type == "virtual":
                serial = obj.get("vesper_serial_number", "unknown")
                config = obj.get("vesper_config", "unknown")
                username = obj.get("vesper_username", "unknown")
                original_type = obj.get("vesper_original_type", "unknown")
                container_name = obj.get("vesper_container_name", "none")
                container_port = obj.get("vesper_container_port", 0)
                
                box.label(text=f"Virtual: {serial}")
                box.label(text=f"Type: {original_type}")
                box.label(text=f"Config: {config}")
                box.label(text=f"User: {username}")
                
                # Container information
                if container_name != "none":
                    box.separator()
                    container_box = box.box()
                    container_box.label(text="🐳 Docker Container:", icon='INFO')
                    container_box.label(text=f"Name: {container_name}")
                    container_box.label(text=f"Port: {container_port}")
                else:
                    box.label(text="⚠️ No container created")
                    
            else:
                device_id = obj.get("vesper_device_id", "unknown")
                room = obj.get("vesper_room", "unknown")
                box.label(text=f"Sensor: {device_id}")
                box.label(text=f"Type: {device_type}")
                box.label(text=f"Room: {room}")
        else:
            box.label(text="No VESPER device selected")

class VESPER_PT_DockerReferencePanel(bpy.types.Panel):
    """Docker container mapping reference panel"""
    bl_label = "Docker Container Reference"
    bl_idname = "VESPER_PT_docker_reference"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'VESPER'
    bl_parent_id = "VESPER_PT_smart_home_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        
        # Container mapping info
        box = layout.box()
        box.label(text="🐳 Active Docker Containers:", icon='INFO')
        
        container_info = [
            ("motion-sensor", "testbed-motion-sensor", ":8001"),
            ("item-sensor", "testbed-item-sensor", ":8002"),
            ("appliance-controller", "testbed-appliance-controller", ":8003"),
            ("casas-dataset-manager", "testbed-casas-dataset-manager", ":8004"),
            ("thermostat", "testbed-thermostat", ":8005"),
        ]
        
        for device_type, container, port in container_info:
            row = box.row()
            row.label(text=f"{device_type}")
            row.label(text=f"→ {container}{port}")
        
        # Device type mapping
        layout.separator()
        box = layout.box()
        box.label(text="📱 Device Type Mapping:", icon='INFO')
        box.label(text="Advanced device types map to core backends:")
        
        mapping_examples = [
            ("🚪 door-sensor", "→ motion-sensor"),
            ("🌡️ temperature-sensor", "→ thermostat"),
            ("💡 smart-switch", "→ appliance-controller"),
            ("📷 security-camera", "→ motion-sensor"),
            ("☕ coffee-maker", "→ appliance-controller"),
        ]
        
        for device, mapping in mapping_examples:
            row = box.row()
            row.label(text=device)
            row.label(text=mapping)

# =============================================================================
# REGISTRATION
# =============================================================================

classes = [
    # Sensor operators (existing)
    VESPER_OT_CheckServices,
    VESPER_OT_AddMotionSensor,
    VESPER_OT_AddItemSensor,
    VESPER_OT_TriggerDevice,
    VESPER_OT_RemoveDevice,
    VESPER_OT_StartDockerServices,
    # Virtual device operators (new)
    VESPER_OT_SpawnVirtualDevice,
    VESPER_OT_DeleteVirtualDevice,
    VESPER_OT_ListVirtualDevices,
    VESPER_OT_ListDockerContainers,
    VESPER_OT_ControlVirtualDevice,
    VESPER_OT_CleanupAllDevices,
    VESPER_OT_FixDetectionAreas,
    # BGE Motion detection operators (Game Engine only)
    VESPER_OT_SetupBGEMotionDetection,
    VESPER_OT_CreateBGEController,
    VESPER_OT_CreateBGEDemo,
    # UI Panel
    VESPER_PT_SmartHomePanel,
    VESPER_PT_DockerReferencePanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Initialize motion detection system
    if MOTION_DETECTION_AVAILABLE:
        try:
            device_manager.motion_detector = initialize_motion_detection()
            print("🔍 Motion detection system initialized with addon")
        except Exception as e:
            print(f"⚠️ Failed to initialize motion detection system: {e}")
    
    print("✅ VESPER Enhanced Smart Home Integration v3.1.0 registered")
    print("   📋 New Features:")
    print("   - Real-time actor detection and SmartThings integration")
    print("   - Frame-based motion detection system")
    print("   - Enhanced virtual motion sensor status updates")
    print("   📋 Existing Features:")
    print("   - Virtual device management with individual Docker containers")
    print("   - 27 device types with automatic container creation")
    print("   - Backend console API integration")
    print("   - Docker container lifecycle management")

def unregister():
    # Clean up motion detection frame handler
    try:
        if motion_detection_frame_handler in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(motion_detection_frame_handler)
            print("🎬 Motion detection frame handler unregistered")
    except Exception as e:
        print(f"⚠️ Failed to unregister motion detection handler: {e}")
    
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("❌ VESPER Smart Home Integration unregistered")
    print("   - All virtual devices and Docker containers should be cleaned up manually")

if __name__ == "__main__":
    register()
