"""
VESPER Virtual Device Manager
Manages virtual smart home devices that can be controlled and monitored
Integrates with SmartThings-style virtual sensors
"""

import time
import json
import os
from datetime import datetime
from enum import Enum


class DeviceState(Enum):
    """Device states"""
    OFF = "off"
    ON = "on"
    IDLE = "idle"
    ACTIVE = "active"
    UNAVAILABLE = "unavailable"


class DeviceType(Enum):
    """Types of smart home devices"""
    LIGHT = "light"
    SWITCH = "switch"
    APPLIANCE = "appliance"
    SENSOR = "sensor"
    LOCK = "lock"
    THERMOSTAT = "thermostat"
    CONTACT = "contact"
    MOTION = "motion"


class VirtualDevice:
    """Represents a single virtual smart home device"""
    
    def __init__(self, device_id, device_name, device_type, room, 
                 initial_state=DeviceState.OFF):
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        self.room = room
        self.state = initial_state
        
        # State history
        self.state_changes = []
        self.last_state_change = time.time()
        
        # Device properties (customizable per device type)
        self.properties = {}
        
        # Statistics
        self.total_on_time = 0.0
        self.activation_count = 0
    
    def set_state(self, new_state, timestamp=None):
        """Change device state"""
        if timestamp is None:
            timestamp = time.time()
        
        if self.state == new_state:
            return False
        
        old_state = self.state
        self.state = new_state
        
        # Track ON time
        if old_state == DeviceState.ON:
            self.total_on_time += timestamp - self.last_state_change
        
        if new_state == DeviceState.ON:
            self.activation_count += 1
        
        # Record state change
        change_record = {
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "old_state": old_state.value,
            "new_state": new_state.value
        }
        self.state_changes.append(change_record)
        self.last_state_change = timestamp
        
        print(f"💡 Device {self.device_name} ({self.device_id}): {old_state.value} → {new_state.value}")
        
        return True
    
    def turn_on(self, timestamp=None):
        """Turn device on"""
        return self.set_state(DeviceState.ON, timestamp)
    
    def turn_off(self, timestamp=None):
        """Turn device off"""
        return self.set_state(DeviceState.OFF, timestamp)
    
    def toggle(self, timestamp=None):
        """Toggle device state"""
        if self.state == DeviceState.ON:
            return self.turn_off(timestamp)
        else:
            return self.turn_on(timestamp)
    
    def set_property(self, property_name, value):
        """Set a device property (e.g., brightness, temperature)"""
        old_value = self.properties.get(property_name)
        self.properties[property_name] = value
        
        print(f"🔧 {self.device_name}.{property_name}: {old_value} → {value}")
        return True
    
    def get_state_summary(self):
        """Get device state summary"""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type.value,
            "room": self.room,
            "current_state": self.state.value,
            "properties": self.properties,
            "activation_count": self.activation_count,
            "total_on_time": self.total_on_time,
            "state_changes": len(self.state_changes)
        }


class VirtualDeviceManager:
    """
    Manages all virtual smart home devices
    Provides SmartThings-style device control interface
    """
    
    def __init__(self, dataset_dir=None):
        self.devices = {}  # device_id -> VirtualDevice
        self.room_devices = {}  # room -> [device_ids]
        self.type_devices = {}  # device_type -> [device_ids]
        
        # Output directory
        if dataset_dir is None:
            dataset_dir = os.path.join(
                r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed",
                "vesper_datasets"
            )
        self.dataset_dir = dataset_dir
        os.makedirs(self.dataset_dir, exist_ok=True)
        
        # Session tracking
        self.session_start = time.time()
        self.session_id = time.strftime("%Y%m%d_%H%M%S")
        
        # Event log
        self.event_log = []
        
        print("✅ Virtual Device Manager initialized")
    
    def register_device(self, device_id, device_name, device_type, room, 
                       initial_state=DeviceState.OFF, properties=None):
        """Register a new virtual device"""
        
        # Convert string to enum if needed
        if isinstance(device_type, str):
            device_type = DeviceType[device_type.upper()]
        if isinstance(initial_state, str):
            initial_state = DeviceState[initial_state.upper()]
        
        device = VirtualDevice(device_id, device_name, device_type, room, initial_state)
        
        if properties:
            device.properties = properties
        
        self.devices[device_id] = device
        
        # Index by room
        if room not in self.room_devices:
            self.room_devices[room] = []
        self.room_devices[room].append(device_id)
        
        # Index by type
        type_key = device_type.value
        if type_key not in self.type_devices:
            self.type_devices[type_key] = []
        self.type_devices[type_key].append(device_id)
        
        print(f"📱 Registered device: {device_name} ({device_id}) - {device_type.value} in {room}")
        
        return device
    
    def get_device(self, device_id):
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_devices_in_room(self, room):
        """Get all devices in a room"""
        device_ids = self.room_devices.get(room, [])
        return [self.devices[did] for did in device_ids]
    
    def get_devices_by_type(self, device_type):
        """Get all devices of a type"""
        if isinstance(device_type, DeviceType):
            device_type = device_type.value
        device_ids = self.type_devices.get(device_type, [])
        return [self.devices[did] for did in device_ids]
    
    def control_device(self, device_id, action, timestamp=None, **kwargs):
        """
        Control a device
        
        Args:
            device_id: Device to control
            action: "on", "off", "toggle", "set_property"
            timestamp: Event timestamp
            **kwargs: Additional parameters (e.g., property_name, value)
        """
        if device_id not in self.devices:
            print(f"⚠️ Device not found: {device_id}")
            return False
        
        device = self.devices[device_id]
        
        if timestamp is None:
            timestamp = time.time()
        
        result = False
        
        if action == "on":
            result = device.turn_on(timestamp)
        elif action == "off":
            result = device.turn_off(timestamp)
        elif action == "toggle":
            result = device.toggle(timestamp)
        elif action == "set_property":
            prop_name = kwargs.get("property_name")
            value = kwargs.get("value")
            if prop_name and value is not None:
                result = device.set_property(prop_name, value)
        
        if result:
            # Log event
            event = {
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "device_id": device_id,
                "device_name": device.device_name,
                "room": device.room,
                "action": action,
                "state": device.state.value
            }
            self.event_log.append(event)
        
        return result
    
    def control_room_devices(self, room, action, device_type_filter=None):
        """Control all devices in a room"""
        devices = self.get_devices_in_room(room)
        
        if device_type_filter:
            devices = [d for d in devices if d.device_type == device_type_filter]
        
        results = []
        for device in devices:
            result = self.control_device(device.device_id, action)
            results.append((device.device_id, result))
        
        return results
    
    def auto_control_for_task(self, task_name, room):
        """
        Automatically control devices based on task
        
        Examples:
            - "Cook" -> Turn on kitchen lights and stove
            - "Sleep" -> Turn off bedroom lights
            - "Watch TV" -> Turn on living room TV and lights
        """
        task_lower = task_name.lower()
        
        # Task-based automation rules
        if "cook" in task_lower:
            self.control_room_devices(room, "on", DeviceType.LIGHT)
            # Could turn on stove, etc.
        
        elif "sleep" in task_lower:
            self.control_room_devices(room, "off", DeviceType.LIGHT)
        
        elif "tv" in task_lower or "watch" in task_lower:
            self.control_room_devices(room, "on", DeviceType.LIGHT)
            # Turn on TV
            tv_devices = [d for d in self.get_devices_in_room(room) 
                         if "tv" in d.device_name.lower()]
            for tv in tv_devices:
                self.control_device(tv.device_id, "on")
        
        elif "phone" in task_lower or "call" in task_lower:
            # Turn on lights in room
            self.control_room_devices(room, "on", DeviceType.LIGHT)
        
        print(f"🤖 Auto-controlled devices for task: {task_name} in {room}")
    
    def get_all_device_states(self):
        """Get current state of all devices"""
        return {
            device_id: device.get_state_summary()
            for device_id, device in self.devices.items()
        }
    
    def export_device_log(self):
        """Export device control log"""
        try:
            output_file = os.path.join(
                self.dataset_dir,
                f"device_log_{self.session_id}.json"
            )
            
            data = {
                "session_id": self.session_id,
                "session_start": self.session_start,
                "devices": self.get_all_device_states(),
                "event_log": self.event_log,
                "summary": self._generate_summary()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Device log exported: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def _generate_summary(self):
        """Generate device usage summary"""
        total_activations = sum(d.activation_count for d in self.devices.values())
        total_on_time = sum(d.total_on_time for d in self.devices.values())
        
        most_used = max(
            self.devices.values(),
            key=lambda d: d.activation_count,
            default=None
        )
        
        return {
            "total_devices": len(self.devices),
            "total_activations": total_activations,
            "total_on_time": total_on_time,
            "most_used_device": most_used.device_name if most_used else None,
            "most_used_count": most_used.activation_count if most_used else 0,
            "devices_by_room": {
                room: len(devices) for room, devices in self.room_devices.items()
            }
        }
    
    def print_summary(self):
        """Print device usage summary"""
        summary = self._generate_summary()
        
        print("\n" + "="*60)
        print("VIRTUAL DEVICE SUMMARY")
        print("="*60)
        print(f"📱 Total Devices: {summary['total_devices']}")
        print(f"⚡ Total Activations: {summary['total_activations']}")
        print(f"⏱️  Total ON Time: {summary['total_on_time']:.1f}s")
        print(f"🏆 Most Used: {summary['most_used_device']} ({summary['most_used_count']} times)")
        print(f"\nDevices by Room:")
        for room, count in summary['devices_by_room'].items():
            print(f"  - {room}: {count} devices")
        print("="*60 + "\n")


# Global instance
_device_manager = None

def get_device_manager():
    """Get or create global device manager"""
    global _device_manager
    if _device_manager is None:
        _device_manager = VirtualDeviceManager()
    return _device_manager


def setup_default_devices():
    """Setup virtual devices for ONLY objects available in Blender scene"""
    manager = get_device_manager()
    
    # ========================================
    # AVAILABLE OBJECTS IN BLENDER SCENE:
    # Phone, Stove, DiningTable, KitchenSink, BathroomSink1, BathroomSink2
    # ========================================
    
    # Kitchen devices
    manager.register_device("D001", "Stove", DeviceType.APPLIANCE, "Kitchen")
    manager.register_device("D002", "KitchenSink", DeviceType.APPLIANCE, "Kitchen")
    
    # Dining room devices
    manager.register_device("D003", "Phone", DeviceType.APPLIANCE, "DiningRoom")
    manager.register_device("D004", "DiningTable", DeviceType.APPLIANCE, "DiningRoom")
    
    # Bathroom devices
    manager.register_device("D005", "BathroomSink1", DeviceType.APPLIANCE, "Bathroom1")
    manager.register_device("D006", "BathroomSink2", DeviceType.APPLIANCE, "Bathroom2")
    
    print("✅ Default devices configured (6 objects: Phone, Stove, DiningTable, KitchenSink, BathroomSink1, BathroomSink2)")
    return manager


if __name__ == "__main__":
    print("🧪 Testing Virtual Device Manager\n")
    
    manager = setup_default_devices()
    
    # Simulate device control
    print("\n🎮 Simulating device control...")
    
    manager.control_device("D001", "on")
    time.sleep(1)
    manager.control_device("D001", "off")
    
    manager.control_device("D006", "on")
    time.sleep(2)
    
    # Auto-control for task
    manager.auto_control_for_task("Cook oatmeal", "Kitchen")
    
    # Print summary
    manager.print_summary()
    
    # Export log
    manager.export_device_log()
