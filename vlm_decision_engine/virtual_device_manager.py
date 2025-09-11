"""
Virtual Device Interaction Manager
==================================

Manages virtual switches, lights, and other interactive devices in the VESPER environment.
Creates templates for device interactions and tracks state changes for CASAS sensor generation.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import requests
import json

class DeviceType(Enum):
    """Types of virtual devices"""
    MOTION_SENSOR = "motion_sensor"
    VIRTUAL_SWITCH = "virtual_switch"
    VIRTUAL_LIGHT = "virtual_light"
    WATER_CONTROL = "water_control"
    BURNER_CONTROL = "burner_control"
    PHONE_DEVICE = "phone_device"
    ITEM_SENSOR = "item_sensor"

class DeviceState(Enum):
    """Device states"""
    ON = "ON"
    OFF = "OFF"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"

@dataclass
class VirtualDevice:
    """Virtual device definition"""
    device_id: str
    device_type: DeviceType
    name: str
    location: str  # Room where device is located
    casas_sensor_id: str  # Corresponding CASAS sensor ID
    current_state: DeviceState
    interaction_methods: List[str]  # Available interaction types
    device_properties: Dict[str, Any]  # Device-specific properties
    api_endpoint: Optional[str] = None  # API endpoint if managed externally
    last_interaction: Optional[float] = None

@dataclass
class DeviceInteraction:
    """Device interaction event"""
    device_id: str
    interaction_type: str
    actor_position: Tuple[float, float, float]
    timestamp: float
    interaction_data: Dict[str, Any]
    casas_event: Optional[Dict[str, str]] = None  # Generated CASAS event

class VirtualDeviceInteractionManager:
    """Manages all virtual device interactions and state tracking"""
    
    def __init__(self):
        self.devices: Dict[str, VirtualDevice] = {}
        self.interaction_history: List[DeviceInteraction] = []
        self.device_manager_url = "http://localhost:9000"  # Backend device manager
        self.casas_events: List[Dict[str, str]] = []
        
        # Initialize standard virtual devices
        self._initialize_standard_devices()
    
    def _initialize_standard_devices(self):
        """Initialize standard virtual devices for CASAS tasks"""
        
        # Virtual switches for lights and appliances
        self.register_device(VirtualDevice(
            device_id="switch_kitchen_light",
            device_type=DeviceType.VIRTUAL_SWITCH,
            name="Kitchen Light Switch",
            location="Kitchen",
            casas_sensor_id="L01",  # Custom light sensor ID
            current_state=DeviceState.OFF,
            interaction_methods=["toggle", "turn_on", "turn_off"],
            device_properties={"power_rating": 60, "switch_type": "toggle"}
        ))
        
        self.register_device(VirtualDevice(
            device_id="switch_dining_light",
            device_type=DeviceType.VIRTUAL_SWITCH,
            name="Dining Room Light Switch",
            location="DiningRoom", 
            casas_sensor_id="L02",
            current_state=DeviceState.OFF,
            interaction_methods=["toggle", "turn_on", "turn_off"],
            device_properties={"power_rating": 75, "switch_type": "toggle"}
        ))
        
        self.register_device(VirtualDevice(
            device_id="switch_living_light",
            device_type=DeviceType.VIRTUAL_SWITCH,
            name="Living Room Light Switch",
            location="LivingRoom",
            casas_sensor_id="L03",
            current_state=DeviceState.OFF,
            interaction_methods=["toggle", "turn_on", "turn_off"],
            device_properties={"power_rating": 100, "switch_type": "dimmer"}
        ))
        
        # Virtual lights (controlled by switches)
        self.register_device(VirtualDevice(
            device_id="light_kitchen_main",
            device_type=DeviceType.VIRTUAL_LIGHT,
            name="Kitchen Main Light",
            location="Kitchen",
            casas_sensor_id="L01",  # Same as switch
            current_state=DeviceState.OFF,
            interaction_methods=["illuminate", "dim", "brighten"],
            device_properties={"brightness": 0, "color_temp": 3000, "max_brightness": 100}
        ))
        
        self.register_device(VirtualDevice(
            device_id="light_dining_main",
            device_type=DeviceType.VIRTUAL_LIGHT,
            name="Dining Room Main Light",
            location="DiningRoom",
            casas_sensor_id="L02",
            current_state=DeviceState.OFF,
            interaction_methods=["illuminate", "dim", "brighten"],
            device_properties={"brightness": 0, "color_temp": 2700, "max_brightness": 100}
        ))
        
        self.register_device(VirtualDevice(
            device_id="light_living_main",
            device_type=DeviceType.VIRTUAL_LIGHT,
            name="Living Room Main Light", 
            location="LivingRoom",
            casas_sensor_id="L03",
            current_state=DeviceState.OFF,
            interaction_methods=["illuminate", "dim", "brighten"],
            device_properties={"brightness": 0, "color_temp": 2700, "max_brightness": 100}
        ))
        
        # Water control devices
        self.register_device(VirtualDevice(
            device_id="water_control_kitchen",
            device_type=DeviceType.WATER_CONTROL,
            name="Kitchen Sink Water Control",
            location="Kitchen",
            casas_sensor_id="AD1-A",  # Hot water sensor
            current_state=DeviceState.OFF,
            interaction_methods=["turn_on_hot", "turn_on_cold", "turn_off", "adjust_temperature"],
            device_properties={"flow_rate": 0, "temperature": 20, "max_flow": 100}
        ))
        
        self.register_device(VirtualDevice(
            device_id="water_control_cold",
            device_type=DeviceType.WATER_CONTROL,
            name="Kitchen Sink Cold Water",
            location="Kitchen", 
            casas_sensor_id="AD1-B",  # Cold water sensor
            current_state=DeviceState.OFF,
            interaction_methods=["turn_on_cold", "turn_off", "adjust_flow"],
            device_properties={"flow_rate": 0, "temperature": 15, "max_flow": 100}
        ))
        
        # Burner control device
        self.register_device(VirtualDevice(
            device_id="burner_control_stove",
            device_type=DeviceType.BURNER_CONTROL,
            name="Kitchen Stove Burner Control",
            location="Kitchen",
            casas_sensor_id="AD1-C",  # Burner sensor
            current_state=DeviceState.OFF,
            interaction_methods=["turn_on", "turn_off", "set_heat_level", "adjust_temperature"],
            device_properties={"heat_level": 0, "max_heat": 100, "burner_type": "gas"}
        ))
        
        # Phone device
        self.register_device(VirtualDevice(
            device_id="phone_dining_room",
            device_type=DeviceType.PHONE_DEVICE,
            name="Dining Room Phone",
            location="DiningRoom",
            casas_sensor_id="*",  # Phone sensor
            current_state=DeviceState.INACTIVE,
            interaction_methods=["pickup", "hangup", "dial", "listen"],
            device_properties={"phone_type": "landline", "has_voicemail": True}
        ))
        
    def register_device(self, device: VirtualDevice):
        """Register a new virtual device"""
        self.devices[device.device_id] = device
        print(f"✅ Registered virtual device: {device.name} ({device.device_id})")
    
    def interact_with_device(self, device_id: str, interaction_type: str, 
                           actor_position: Tuple[float, float, float],
                           interaction_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Interact with a virtual device and generate CASAS events"""
        
        if device_id not in self.devices:
            return {"success": False, "error": f"Device {device_id} not found"}
        
        device = self.devices[device_id]
        timestamp = time.time()
        
        # Validate interaction type
        if interaction_type not in device.interaction_methods:
            return {
                "success": False, 
                "error": f"Interaction '{interaction_type}' not supported for {device.name}"
            }
        
        # Process device-specific interaction
        result = self._process_device_interaction(device, interaction_type, interaction_data or {})
        
        if result["success"]:
            # Generate CASAS event
            casas_event = self._generate_casas_event(device, interaction_type, result)
            
            # Record interaction
            interaction = DeviceInteraction(
                device_id=device_id,
                interaction_type=interaction_type,
                actor_position=actor_position,
                timestamp=timestamp,
                interaction_data=interaction_data or {},
                casas_event=casas_event
            )
            
            self.interaction_history.append(interaction)
            if casas_event:
                self.casas_events.append(casas_event)
            
            # Update device state
            device.last_interaction = timestamp
            
            print(f"🎮 Device interaction: {device.name} - {interaction_type}")
            if casas_event:
                print(f"📊 CASAS event: {casas_event['sensor']},{casas_event['message']}")
        
        return result
    
    def _process_device_interaction(self, device: VirtualDevice, interaction_type: str, 
                                  interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process device-specific interaction logic"""
        
        if device.device_type == DeviceType.VIRTUAL_SWITCH:
            return self._process_switch_interaction(device, interaction_type, interaction_data)
        elif device.device_type == DeviceType.VIRTUAL_LIGHT:
            return self._process_light_interaction(device, interaction_type, interaction_data)
        elif device.device_type == DeviceType.WATER_CONTROL:
            return self._process_water_interaction(device, interaction_type, interaction_data)
        elif device.device_type == DeviceType.BURNER_CONTROL:
            return self._process_burner_interaction(device, interaction_type, interaction_data)
        elif device.device_type == DeviceType.PHONE_DEVICE:
            return self._process_phone_interaction(device, interaction_type, interaction_data)
        else:
            return {"success": False, "error": f"Unknown device type: {device.device_type}"}
    
    def _process_switch_interaction(self, device: VirtualDevice, interaction_type: str, 
                                  interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process virtual switch interactions"""
        
        if interaction_type == "toggle":
            new_state = DeviceState.ON if device.current_state == DeviceState.OFF else DeviceState.OFF
            device.current_state = new_state
            
            # Also update corresponding light
            light_id = device.device_id.replace("switch_", "light_").replace("_light", "_main")
            if light_id in self.devices:
                light_device = self.devices[light_id]
                light_device.current_state = new_state
                if new_state == DeviceState.ON:
                    light_device.device_properties["brightness"] = 80  # Default brightness
                else:
                    light_device.device_properties["brightness"] = 0
            
            return {
                "success": True,
                "new_state": new_state.value,
                "action": "toggled",
                "affected_devices": [light_id] if light_id in self.devices else []
            }
        
        elif interaction_type in ["turn_on", "turn_off"]:
            new_state = DeviceState.ON if interaction_type == "turn_on" else DeviceState.OFF
            device.current_state = new_state
            
            return {
                "success": True,
                "new_state": new_state.value,
                "action": interaction_type
            }
        
        return {"success": False, "error": f"Unknown switch interaction: {interaction_type}"}
    
    def _process_light_interaction(self, device: VirtualDevice, interaction_type: str, 
                                 interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process virtual light interactions"""
        
        if interaction_type == "illuminate":
            device.current_state = DeviceState.ON
            brightness = interaction_data.get("brightness", 80)
            device.device_properties["brightness"] = min(100, max(0, brightness))
            
            return {
                "success": True,
                "new_state": "ON",
                "brightness": device.device_properties["brightness"],
                "action": "illuminated"
            }
        
        elif interaction_type in ["dim", "brighten"]:
            current_brightness = device.device_properties.get("brightness", 0)
            adjustment = interaction_data.get("amount", 20)
            
            if interaction_type == "dim":
                new_brightness = max(0, current_brightness - adjustment)
            else:  # brighten
                new_brightness = min(100, current_brightness + adjustment)
            
            device.device_properties["brightness"] = new_brightness
            device.current_state = DeviceState.ON if new_brightness > 0 else DeviceState.OFF
            
            return {
                "success": True,
                "new_state": device.current_state.value,
                "brightness": new_brightness,
                "action": interaction_type
            }
        
        return {"success": False, "error": f"Unknown light interaction: {interaction_type}"}
    
    def _process_water_interaction(self, device: VirtualDevice, interaction_type: str, 
                                 interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process water control interactions"""
        
        if interaction_type in ["turn_on_hot", "turn_on_cold"]:
            device.current_state = DeviceState.ON
            flow_rate = interaction_data.get("flow_rate", 50)
            temperature = 40 if "hot" in interaction_type else 15
            
            device.device_properties["flow_rate"] = flow_rate
            device.device_properties["temperature"] = temperature
            
            return {
                "success": True,
                "new_state": "ON",
                "flow_rate": flow_rate,
                "temperature": temperature,
                "water_type": "hot" if "hot" in interaction_type else "cold"
            }
        
        elif interaction_type == "turn_off":
            device.current_state = DeviceState.OFF
            device.device_properties["flow_rate"] = 0
            
            return {
                "success": True,
                "new_state": "OFF",
                "flow_rate": 0,
                "action": "water_stopped"
            }
        
        elif interaction_type == "adjust_temperature":
            if device.current_state == DeviceState.ON:
                new_temp = interaction_data.get("temperature", 30)
                device.device_properties["temperature"] = new_temp
                
                return {
                    "success": True,
                    "temperature": new_temp,
                    "action": "temperature_adjusted"
                }
        
        return {"success": False, "error": f"Unknown water interaction: {interaction_type}"}
    
    def _process_burner_interaction(self, device: VirtualDevice, interaction_type: str, 
                                  interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process burner control interactions"""
        
        if interaction_type == "turn_on":
            device.current_state = DeviceState.ON
            heat_level = interaction_data.get("heat_level", 50)
            device.device_properties["heat_level"] = min(100, max(0, heat_level))
            
            return {
                "success": True,
                "new_state": "ON",
                "heat_level": device.device_properties["heat_level"],
                "action": "burner_ignited"
            }
        
        elif interaction_type == "turn_off":
            device.current_state = DeviceState.OFF
            device.device_properties["heat_level"] = 0
            
            return {
                "success": True,
                "new_state": "OFF",
                "heat_level": 0,
                "action": "burner_extinguished"
            }
        
        elif interaction_type in ["set_heat_level", "adjust_temperature"]:
            if device.current_state == DeviceState.ON:
                new_heat = interaction_data.get("heat_level", 50)
                device.device_properties["heat_level"] = min(100, max(0, new_heat))
                
                return {
                    "success": True,
                    "heat_level": device.device_properties["heat_level"],
                    "action": "heat_adjusted"
                }
        
        return {"success": False, "error": f"Unknown burner interaction: {interaction_type}"}
    
    def _process_phone_interaction(self, device: VirtualDevice, interaction_type: str, 
                                 interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process phone device interactions"""
        
        if interaction_type == "pickup":
            device.current_state = DeviceState.ACTIVE
            
            return {
                "success": True,
                "new_state": "ACTIVE",
                "action": "phone_pickup",
                "phone_status": "call_active"
            }
        
        elif interaction_type == "hangup":
            device.current_state = DeviceState.INACTIVE
            
            return {
                "success": True,
                "new_state": "INACTIVE",
                "action": "phone_hangup",
                "phone_status": "call_ended"
            }
        
        elif interaction_type == "dial":
            if device.current_state == DeviceState.ACTIVE:
                number = interaction_data.get("number", "555-0123")
                
                return {
                    "success": True,
                    "action": "phone_dial",
                    "number_dialed": number,
                    "phone_status": "dialing"
                }
        
        elif interaction_type == "listen":
            if device.current_state == DeviceState.ACTIVE:
                message = interaction_data.get("message", "cooking_instructions")
                
                return {
                    "success": True,
                    "action": "phone_listen",
                    "message_received": message,
                    "phone_status": "listening"
                }
        
        return {"success": False, "error": f"Unknown phone interaction: {interaction_type}"}
    
    def _generate_casas_event(self, device: VirtualDevice, interaction_type: str, 
                            interaction_result: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Generate CASAS sensor event from device interaction"""
        
        sensor_id = device.casas_sensor_id
        timestamp = time.strftime("%Y-%m-%d,%H:%M:%S.%f")[:-3]  # CASAS format timestamp
        
        # Generate appropriate CASAS message based on device type and interaction
        if device.device_type == DeviceType.VIRTUAL_SWITCH:
            message = interaction_result.get("new_state", "OFF")
            
        elif device.device_type == DeviceType.VIRTUAL_LIGHT:
            brightness = interaction_result.get("brightness", 0)
            if brightness > 0:
                message = "ON"
            else:
                message = "OFF"
                
        elif device.device_type == DeviceType.WATER_CONTROL:
            flow_rate = interaction_result.get("flow_rate", 0)
            message = str(flow_rate)  # Water sensors use numeric values
            
        elif device.device_type == DeviceType.BURNER_CONTROL:
            heat_level = interaction_result.get("heat_level", 0)
            message = str(heat_level)  # Burner sensors use numeric values
            
        elif device.device_type == DeviceType.PHONE_DEVICE:
            action = interaction_result.get("action", "")
            if action == "phone_pickup":
                message = "PHONE_PICKUP"
            elif action == "phone_hangup":
                message = "PHONE_HANGUP"
            elif action in ["phone_dial", "phone_listen"]:
                message = "PHONE_ACTIVE"
            else:
                message = "PHONE_INACTIVE"
        
        else:
            return None  # Unknown device type
        
        return {
            "date": timestamp.split(",")[0],
            "time": timestamp.split(",")[1],
            "sensor": sensor_id,
            "message": message
        }
    
    def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a device"""
        if device_id in self.devices:
            device = self.devices[device_id]
            return {
                "device_id": device_id,
                "name": device.name,
                "type": device.device_type.value,
                "location": device.location,
                "current_state": device.current_state.value,
                "properties": device.device_properties,
                "last_interaction": device.last_interaction
            }
        return None
    
    def get_devices_in_room(self, room_name: str) -> List[VirtualDevice]:
        """Get all devices in a specific room"""
        return [device for device in self.devices.values() if device.location == room_name]
    
    def get_interactable_devices_near_position(self, position: Tuple[float, float, float], 
                                             max_distance: float = 2.0) -> List[VirtualDevice]:
        """Get devices that can be interacted with from current position"""
        # For now, return all devices in the same room
        # In a full implementation, this would use actual distance calculations
        
        interactable = []
        for device in self.devices.values():
            # Simple room-based proximity for now
            # Could be enhanced with actual 3D distance calculations
            interactable.append(device)
        
        return interactable
    
    def get_interaction_history(self, device_id: Optional[str] = None, 
                              limit: int = 50) -> List[DeviceInteraction]:
        """Get device interaction history"""
        history = self.interaction_history
        
        if device_id:
            history = [interaction for interaction in history if interaction.device_id == device_id]
        
        return history[-limit:]  # Return most recent interactions
    
    def get_casas_events(self, limit: int = 100) -> List[Dict[str, str]]:
        """Get generated CASAS events from device interactions"""
        return self.casas_events[-limit:]
    
    def reset_all_devices(self):
        """Reset all devices to their default states"""
        for device in self.devices.values():
            if device.device_type in [DeviceType.VIRTUAL_SWITCH, DeviceType.VIRTUAL_LIGHT]:
                device.current_state = DeviceState.OFF
                if "brightness" in device.device_properties:
                    device.device_properties["brightness"] = 0
            elif device.device_type == DeviceType.WATER_CONTROL:
                device.current_state = DeviceState.OFF
                device.device_properties["flow_rate"] = 0
            elif device.device_type == DeviceType.BURNER_CONTROL:
                device.current_state = DeviceState.OFF
                device.device_properties["heat_level"] = 0
            elif device.device_type == DeviceType.PHONE_DEVICE:
                device.current_state = DeviceState.INACTIVE
            
            device.last_interaction = None
        
        self.interaction_history.clear()
        self.casas_events.clear()
        print("🔄 All virtual devices reset to default states")
    
    def validate_device_interaction_sequence(self, expected_sequence: List[str]) -> Dict[str, Any]:
        """Validate that device interactions followed expected sequence"""
        actual_sequence = [interaction.interaction_type for interaction in self.interaction_history]
        
        validation_result = {
            "valid": True,
            "expected": expected_sequence,
            "actual": actual_sequence,
            "missing_interactions": [],
            "unexpected_interactions": [],
            "sequence_score": 0.0
        }
        
        # Check for missing interactions
        for expected in expected_sequence:
            if expected not in actual_sequence:
                validation_result["missing_interactions"].append(expected)
                validation_result["valid"] = False
        
        # Check for unexpected interactions
        for actual in actual_sequence:
            if actual not in expected_sequence:
                validation_result["unexpected_interactions"].append(actual)
        
        # Calculate sequence similarity score
        if expected_sequence and actual_sequence:
            # Simple similarity: ratio of matching interactions
            matches = len(set(expected_sequence) & set(actual_sequence))
            validation_result["sequence_score"] = matches / max(len(expected_sequence), len(actual_sequence))
        
        return validation_result
