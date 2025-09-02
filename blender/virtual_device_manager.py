"""
VESPER Virtual Device Manager for Blender
Integrates with backend-console API to spawn/delete virtual smart home devices
Equivalent to the web UI functionality but accessible from Blender
"""

import bge
import mathutils
import json
import time
import os

# Try to import requests for HTTP communication
try:
    import requests
    REQUESTS_AVAILABLE = True
    print("✅ BGE: requests module available")
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ BGE: requests module not available - install with: pip install requests")

class VirtualDeviceManager:
    """
    Manages virtual smart home devices through backend-console API
    Equivalent to the web UI device management functionality
    """
    
    def __init__(self):
        # Backend console API endpoints
        self.api_base = "http://localhost:8088"  # Backend console API
        self.cloud_base = "http://localhost:8081"  # Cloud server
        
        # Device configurations (same as web UI)
        self.device_configs = {
            "small_apartment_efficient": "small_apartment_efficient.yaml",
            "small_apartment_inefficient": "small_apartment_inefficient.yaml", 
            "medium_house_efficient": "medium_house_efficient.yaml"
        }
        
        # Track spawned devices
        self.active_devices = {}
        
        print("🏠 BGE: Virtual Device Manager initialized")
    
    def check_backend_health(self):
        """Check if backend console is available"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_active_devices(self):
        """Get list of active devices from backend"""
        if not REQUESTS_AVAILABLE:
            print("❌ BGE: Cannot get devices - requests not available")
            return []
        
        try:
            response = requests.get(f"{self.api_base}/api/console/devices", timeout=10)
            if response.status_code == 200:
                devices = response.json()
                print(f"📱 BGE: Found {len(devices)} active devices")
                return devices
            else:
                print(f"❌ BGE: Failed to get devices - status {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ BGE: Error getting devices: {e}")
            return []
    
    def spawn_device(self, username="admin", config_type="medium_house_efficient"):
        """
        Spawn a new virtual device (equivalent to clicking spawn button in web UI)
        
        Args:
            username: User to assign device to
            config_type: Device configuration type
        """
        if not REQUESTS_AVAILABLE:
            print("❌ BGE: Cannot spawn device - requests not available")
            return None
        
        if config_type not in self.device_configs:
            print(f"❌ BGE: Invalid config type: {config_type}")
            return None
        
        config_file = self.device_configs[config_type]
        
        payload = {
            "username": username,
            "environment_config": config_file
        }
        
        try:
            print(f"🔄 BGE: Spawning device with config {config_type} for user {username}")
            response = requests.post(
                f"{self.api_base}/api/console/spawn",
                json=payload,
                timeout=30  # Spawning can take time
            )
            
            if response.status_code == 200:
                device_info = response.json()
                serial = device_info.get("serial_number")
                
                # Store device info
                self.active_devices[serial] = {
                    "serial": serial,
                    "config": config_type,
                    "username": username,
                    "spawned_at": time.time()
                }
                
                print(f"✅ BGE: Successfully spawned device {serial}")
                return device_info
            else:
                print(f"❌ BGE: Failed to spawn device - status {response.status_code}")
                print(f"    Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ BGE: Error spawning device: {e}")
            return None
    
    def delete_device(self, serial_number):
        """
        Delete a virtual device (equivalent to clicking delete button in web UI)
        
        Args:
            serial_number: Device serial number to delete
        """
        if not REQUESTS_AVAILABLE:
            print("❌ BGE: Cannot delete device - requests not available")
            return False
        
        try:
            print(f"🗑️ BGE: Deleting device {serial_number}")
            response = requests.delete(
                f"{self.api_base}/api/console/device/{serial_number}",
                timeout=30  # Deletion can take time
            )
            
            if response.status_code == 200:
                # Remove from our tracking
                if serial_number in self.active_devices:
                    del self.active_devices[serial_number]
                
                print(f"✅ BGE: Successfully deleted device {serial_number}")
                return True
            else:
                print(f"❌ BGE: Failed to delete device - status {response.status_code}")
                print(f"    Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ BGE: Error deleting device: {e}")
            return False
    
    def control_device(self, serial_number, command_type, value):
        """
        Send control commands to a device
        
        Args:
            serial_number: Device to control
            command_type: Type of command (setpoint, mode, weather, current_temp)
            value: Command value
        """
        if not REQUESTS_AVAILABLE:
            print("❌ BGE: Cannot control device - requests not available")
            return False
        
        endpoint_map = {
            "setpoint": f"/api/console/device/{serial_number}/setpoint",
            "mode": f"/api/console/device/{serial_number}/mode", 
            "weather": f"/api/console/device/{serial_number}/weather-override",
            "current_temp": f"/api/console/device/{serial_number}/current-temp"
        }
        
        payload_map = {
            "setpoint": {"target_temp": value},
            "mode": {"mode": value},
            "weather": {"temperature": value},
            "current_temp": {"temperature": value}
        }
        
        if command_type not in endpoint_map:
            print(f"❌ BGE: Invalid command type: {command_type}")
            return False
        
        try:
            print(f"🎛️ BGE: Sending {command_type} command to {serial_number}: {value}")
            response = requests.post(
                f"{self.api_base}{endpoint_map[command_type]}",
                json=payload_map[command_type],
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ BGE: Successfully sent {command_type} command")
                return True
            else:
                print(f"❌ BGE: Failed to send command - status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ BGE: Error sending command: {e}")
            return False
    
    def list_available_configs(self):
        """List available device configurations"""
        print("📋 BGE: Available device configurations:")
        for i, (key, file) in enumerate(self.device_configs.items(), 1):
            print(f"  {i}. {key} -> {file}")
        return list(self.device_configs.keys())
    
    def get_device_status(self, serial_number):
        """Get detailed status of a specific device"""
        devices = self.get_active_devices()
        for device in devices:
            if device.get("serial_number") == serial_number:
                return device
        return None
    
    def cleanup_all_devices(self):
        """Delete all active devices"""
        devices = self.get_active_devices()
        deleted_count = 0
        
        for device in devices:
            serial = device.get("serial_number")
            if serial:
                if self.delete_device(serial):
                    deleted_count += 1
        
        print(f"🧹 BGE: Cleaned up {deleted_count} devices")
        return deleted_count

# Global device manager instance
virtual_device_manager = VirtualDeviceManager()

# =============================================================================
# BGE INTEGRATION FUNCTIONS
# =============================================================================

def create_device_visual_in_scene(device_info, position=None):
    """Create visual representation of spawned device in BGE scene"""
    scene = bge.logic.getCurrentScene()
    
    if position is None:
        # Default position near origin
        position = mathutils.Vector((0, 0, 1))
    
    try:
        # Try to add a simple cube to represent the device
        # In a real implementation, you might want different shapes for different device types
        serial = device_info.get("serial_number", "unknown")
        config = device_info.get("config_file", "unknown")
        
        # In BGE, we'd need existing objects to instantiate
        # For now, just log the device creation
        print(f"🎨 BGE: Would create visual for device {serial} with config {config} at {position}")
        
        # Store device info in scene for later reference
        if not hasattr(bge.logic, "spawned_devices"):
            bge.logic.spawned_devices = {}
        
        bge.logic.spawned_devices[serial] = {
            "info": device_info,
            "position": position,
            "created_at": time.time()
        }
        
        return True
        
    except Exception as e:
        print(f"❌ BGE: Error creating device visual: {e}")
        return False

def remove_device_visual_from_scene(serial_number):
    """Remove visual representation of device from BGE scene"""
    try:
        if hasattr(bge.logic, "spawned_devices") and serial_number in bge.logic.spawned_devices:
            del bge.logic.spawned_devices[serial_number]
            print(f"🗑️ BGE: Removed visual for device {serial_number}")
            return True
    except Exception as e:
        print(f"❌ BGE: Error removing device visual: {e}")
    return False

# =============================================================================
# CONVENIENCE FUNCTIONS FOR BGE SCRIPTS
# =============================================================================

def spawn_apartment_device(username="admin"):
    """Quick function to spawn a small apartment device"""
    return virtual_device_manager.spawn_device(username, "small_apartment_efficient")

def spawn_house_device(username="admin"):
    """Quick function to spawn a medium house device"""
    return virtual_device_manager.spawn_device(username, "medium_house_efficient")

def quick_device_status():
    """Quick status check of all devices"""
    devices = virtual_device_manager.get_active_devices()
    print(f"\n📊 BGE: Device Status Summary")
    print(f"    Active devices: {len(devices)}")
    
    for device in devices:
        serial = device.get("serial_number", "unknown")
        config = device.get("config_file", "unknown")
        status = "running" if device.get("current_state", {}).get("is_running") else "idle"
        temp = device.get("current_state", {}).get("temperature", "unknown")
        print(f"    • {serial}: {config} - {status} - {temp}°F")
    
    return devices

def cleanup_all():
    """Quick cleanup of all devices"""
    return virtual_device_manager.cleanup_all_devices()

# =============================================================================
# BGE GAME LOGIC INTEGRATION
# =============================================================================

def main():
    """Main BGE logic function - call this from Logic Bricks"""
    controller = bge.logic.getCurrentController()
    owner = controller.owner
    
    # Example: Spawn device when 'S' key is pressed
    keyboard = bge.logic.keyboard
    
    if keyboard.events[bge.events.SKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: S key pressed - spawning device")
        device = spawn_house_device()
        if device:
            create_device_visual_in_scene(device)
    
    # Example: Delete all devices when 'D' key is pressed
    if keyboard.events[bge.events.DKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: D key pressed - cleaning up devices")
        cleanup_all()
    
    # Example: Check status when 'Q' key is pressed
    if keyboard.events[bge.events.QKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: Q key pressed - checking device status")
        quick_device_status()

if __name__ == "__main__":
    # Test the module
    print("🧪 BGE: Testing Virtual Device Manager")
    
    # Check if backend is available
    if virtual_device_manager.check_backend_health():
        print("✅ BGE: Backend console is available")
        
        # Show available configs
        virtual_device_manager.list_available_configs()
        
        # Show current devices
        quick_device_status()
        
    else:
        print("❌ BGE: Backend console is not available")
        print("    Make sure docker-compose is running:")
        print("    cd C:\\Users\\hbui11\\Desktop\\vesper_llm\\virtual-interaction")
        print("    docker-compose up -d")
