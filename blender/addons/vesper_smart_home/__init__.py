"""
VESPER Smart Home Integration - Blender Addon
Integrates Blender 3D environment with Docker-hosted virtual smart devices
"""

bl_info = {
    "name": "VESPER Smart Home Integration",
    "author": "VESPER Team",
    "version": (3, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > VESPER Smart Home",
    "description": "Complete smart home device management: sensors + virtual devices from Blender",
    "category": "System",
    "support": "COMMUNITY"
}

import bpy
import bpy.props
from mathutils import Vector

# Try to import requests, handle gracefully if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print(" requests module not available. Install with: pip install requests")

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
        
        # Virtual device configurations (same as web UI)
        self.virtual_configs = {
            "small_apartment_efficient": "small_apartment_efficient.yaml",
            "small_apartment_inefficient": "small_apartment_inefficient.yaml", 
            "medium_house_efficient": "medium_house_efficient.yaml"
        }
        
        self.device_registry = {}
        self.virtual_devices = {}
    
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
        
        # Find available port (starting from 9000)
        port = self.find_available_port(9000)
        
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
            ]
            
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
    
    def find_available_port(self, start_port=9000):
        """Find an available port starting from start_port"""
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
    
    def add_motion_sensor(self, sensor_id: str, room: str, position: Vector) -> bool:
        """Add a motion sensor to the virtual environment"""
        if not REQUESTS_AVAILABLE:
            print(" requests module required for Docker communication")
            return False
            
        try:
            data = {
                "detection_zone": {
                    "x": position.x,
                    "y": position.y,
                    "radius": 2.0
                },
                "room_location": room,
                "sensitivity": 1.0,
                "cooldown_period": 2.0
            }
            response = requests.post(f"{self.base_urls['motion']}/configure", json=data, timeout=10)
            if response.status_code == 200:
                self.device_registry[sensor_id] = {
                    "type": "motion",
                    "room": room,
                    "position": position,
                    "state": "inactive"
                }
                print(f" Added motion sensor {sensor_id} in {room}")
                return True
        except Exception as e:
            print(f" Failed to add motion sensor: {e}")
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

# Global device manager instance
device_manager = DeviceManager()

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
    # UI Panel
    VESPER_PT_SmartHomePanel,
    VESPER_PT_DockerReferencePanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    print("✅ VESPER Enhanced Smart Home Integration registered")
    print("   - Virtual device management with individual Docker containers")
    print("   - 27 device types with automatic container creation")
    print("   - Backend console API integration")
    print("   - Docker container lifecycle management")

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("❌ VESPER Smart Home Integration unregistered")
    print("   - All virtual devices and Docker containers should be cleaned up manually")

if __name__ == "__main__":
    register()
