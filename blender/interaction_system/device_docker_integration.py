"""
VESPER Device-Docker Integration
Links physical item sensors (Phone, Stove, etc.) with virtual Docker container devices
Tracks device state, usage, and container health
"""

import time
import json
import os

# Try to import requests for Docker container communication
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests module not available - Docker integration limited")


class DeviceDockerBridge:
    """
    Links item sensors (Phone, Stove, Sink, etc.) with Docker container virtual devices
    Tracks device state and container health
    """
    
    def __init__(self, backend_api_url="http://localhost:8088"):
        self.backend_api = backend_api_url
        
        # Map item sensor names to device types
        self.sensor_to_device_type = {
            "Phone": "smart_speaker",  # Telephone uses smart speaker device
            "BathroomSink": "smart_faucet",
            "KitchenSink": "smart_faucet",
            "Stove": "thermostat",  # Stove uses thermostat as proxy
            "DiningTable": "motion_sensor",  # Dining uses motion sensor
            "Microwave": "thermostat",
            "Refrigerator": "thermostat",
            "CoffeeMaker": "thermostat",
            "TV": "smart_speaker"
        }
        
        # Device state tracking
        self.device_states = {}  # {object_name: {status, container_port, serial, last_check}}
        
        # Container health tracking
        self.container_health = {}  # {serial_number: {healthy, last_check, port}}
        
        print("🐳 Device-Docker Bridge initialized")
    
    def map_object_to_device_type(self, object_name):
        """Get device type for an object"""
        return self.sensor_to_device_type.get(object_name, "motion_sensor")
    
    def check_container_health(self, serial_number, port):
        """
        Check if Docker container is healthy and responding
        
        Args:
            serial_number: Device serial number
            port: Container port
        
        Returns:
            bool: True if container is healthy
        """
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            # Health check endpoint
            response = requests.get(
                f"http://localhost:{port}/health",
                timeout=2
            )
            
            is_healthy = response.status_code == 200
            
            # Update health cache
            self.container_health[serial_number] = {
                "healthy": is_healthy,
                "last_check": time.time(),
                "port": port,
                "status_code": response.status_code
            }
            
            return is_healthy
            
        except requests.exceptions.RequestException as e:
            # Container not reachable
            self.container_health[serial_number] = {
                "healthy": False,
                "last_check": time.time(),
                "port": port,
                "error": str(e)
            }
            return False
    
    def get_active_devices_for_room(self, room_name):
        """
        Get active Docker devices for a specific room
        
        Args:
            room_name: Room name (Kitchen, Bathroom, DiningRoom, etc.)
        
        Returns:
            List of device information
        """
        if not REQUESTS_AVAILABLE:
            return []
        
        try:
            response = requests.get(
                f"{self.backend_api}/api/console/devices",
                timeout=5
            )
            
            if response.status_code == 200:
                all_devices = response.json()
                
                # Filter by room (based on device metadata)
                room_devices = []
                for device in all_devices:
                    device_room = device.get("room", "")
                    if device_room.lower() == room_name.lower():
                        room_devices.append(device)
                
                return room_devices
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error getting devices for room {room_name}: {e}")
            return []
    
    def flag_device_in_use(self, object_name, serial_number, port, in_use=True):
        """
        Flag a device as in use (actor is interacting)
        
        Args:
            object_name: Object being interacted with (Phone, Stove, etc.)
            serial_number: Device serial number
            port: Container port
            in_use: True if device is being used
        
        Returns:
            bool: True if successfully flagged
        """
        # Check container health first
        is_healthy = self.check_container_health(serial_number, port)
        
        if not is_healthy:
            print(f"⚠️ Cannot flag device {object_name} - container {serial_number} unhealthy")
            return False
        
        # Update device state
        self.device_states[object_name] = {
            "serial": serial_number,
            "port": port,
            "in_use": in_use,
            "last_update": time.time(),
            "healthy": is_healthy
        }
        
        if in_use:
            print(f"🔴 Device {object_name} FLAGGED as IN USE (container: {serial_number}:{port})")
        else:
            print(f"🟢 Device {object_name} FLAGGED as AVAILABLE (container: {serial_number}:{port})")
        
        return True
    
    def get_device_state(self, object_name):
        """
        Get current state of a device
        
        Args:
            object_name: Object name
        
        Returns:
            dict: Device state info
        """
        return self.device_states.get(object_name, {
            "in_use": False,
            "healthy": False,
            "serial": None,
            "port": None
        })
    
    def send_device_command(self, object_name, command_type, value):
        """
        Send command to device container
        
        Args:
            object_name: Object controlling the device
            command_type: Command type (turn_on, turn_off, set_value)
            value: Command value
        
        Returns:
            bool: True if command successful
        """
        device_state = self.device_states.get(object_name)
        
        if not device_state or not device_state.get("healthy"):
            print(f"⚠️ Cannot send command - device {object_name} not available")
            return False
        
        serial = device_state["serial"]
        port = device_state["port"]
        
        if not REQUESTS_AVAILABLE:
            print(f"⚠️ Cannot send command - requests module not available")
            return False
        
        try:
            # Map command type to endpoint
            endpoint_map = {
                "turn_on": f"/api/device/{serial}/on",
                "turn_off": f"/api/device/{serial}/off",
                "set_value": f"/api/device/{serial}/value"
            }
            
            if command_type not in endpoint_map:
                print(f"⚠️ Unknown command type: {command_type}")
                return False
            
            url = f"http://localhost:{port}{endpoint_map[command_type]}"
            payload = {"value": value} if command_type == "set_value" else {}
            
            response = requests.post(url, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Command sent to {object_name}: {command_type} = {value}")
                return True
            else:
                print(f"⚠️ Command failed for {object_name}: status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending command to {object_name}: {e}")
            return False
    
    def export_device_tracking_log(self, output_dir):
        """
        Export device state tracking log
        
        Args:
            output_dir: Directory to save log
        """
        log_path = os.path.join(output_dir, "device_docker_tracking.json")
        
        log_data = {
            "device_states": self.device_states,
            "container_health": self.container_health,
            "timestamp": time.time()
        }
        
        try:
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            print(f"💾 Device-Docker tracking log saved: {log_path}")
            
        except Exception as e:
            print(f"❌ Error saving device tracking log: {e}")
    
    def print_status_summary(self):
        """Print summary of device states and container health"""
        print("\n" + "="*70)
        print("DEVICE-DOCKER STATUS SUMMARY")
        print("="*70)
        
        print(f"\n📱 Device States ({len(self.device_states)} tracked):")
        for obj_name, state in self.device_states.items():
            status = "🔴 IN USE" if state.get("in_use") else "🟢 AVAILABLE"
            health = "✅ HEALTHY" if state.get("healthy") else "❌ UNHEALTHY"
            serial = state.get("serial", "N/A")
            print(f"   {obj_name}: {status} | {health} | Container: {serial}")
        
        print(f"\n🐳 Container Health ({len(self.container_health)} checked):")
        for serial, health in self.container_health.items():
            status = "✅ HEALTHY" if health.get("healthy") else "❌ UNHEALTHY"
            port = health.get("port", "N/A")
            last_check = time.time() - health.get("last_check", 0)
            print(f"   {serial}:{port} - {status} (checked {last_check:.1f}s ago)")
        
        print("="*70 + "\n")


# Global bridge instance
device_docker_bridge = DeviceDockerBridge()


def get_device_docker_bridge():
    """Get global device-docker bridge instance"""
    return device_docker_bridge
