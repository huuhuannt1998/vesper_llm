"""
VESPER Enhanced VLM Extensions
==============================

Extensions to the existing VLM navigation system to support:
1. First-person view integration
2. Virtual device interactions (switches, lights, sensors)
3. CASAS subtask management with checkpoints
4. Duration-based task validation

This module extends the existing llm_bge_navigation.py without conflicts.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Virtual Device System
class DeviceType(Enum):
    VIRTUAL_SWITCH = "virtual_switch"
    VIRTUAL_LIGHT = "virtual_light"
    WATER_CONTROL = "water_control"
    BURNER_CONTROL = "burner_control"
    PHONE_DEVICE = "phone_device"

@dataclass
class VirtualDevice:
    device_id: str
    device_type: DeviceType
    name: str
    location: str
    casas_sensor_id: str
    current_state: str
    interaction_methods: List[str]
    device_properties: Dict[str, Any]

class EnhancedVLMManager:
    """Enhanced VLM system that extends existing navigation with device interactions"""
    
    def __init__(self):
        self.devices: Dict[str, VirtualDevice] = {}
        self.interaction_history: List[Dict[str, Any]] = []
        self.casas_events: List[Dict[str, str]] = []
        self.current_subtask: Optional[Dict[str, Any]] = None
        self.subtask_start_time: Optional[float] = None
        
        # Initialize standard virtual devices
        self._initialize_devices()
        
    def _initialize_devices(self):
        """Initialize virtual devices for CASAS tasks"""
        
        # Kitchen devices
        self.devices["kitchen_light_switch"] = VirtualDevice(
            device_id="kitchen_light_switch",
            device_type=DeviceType.VIRTUAL_SWITCH,
            name="Kitchen Light Switch",
            location="Kitchen",
            casas_sensor_id="L01",
            current_state="OFF",
            interaction_methods=["toggle", "turn_on", "turn_off"],
            device_properties={"power_rating": 60}
        )
        
        self.devices["kitchen_light"] = VirtualDevice(
            device_id="kitchen_light",
            device_type=DeviceType.VIRTUAL_LIGHT,
            name="Kitchen Light",
            location="Kitchen", 
            casas_sensor_id="L01",
            current_state="OFF",
            interaction_methods=["illuminate", "dim"],
            device_properties={"brightness": 0, "max_brightness": 100}
        )
        
        self.devices["water_control"] = VirtualDevice(
            device_id="water_control",
            device_type=DeviceType.WATER_CONTROL,
            name="Kitchen Sink Water",
            location="Kitchen",
            casas_sensor_id="AD1-A",
            current_state="OFF",
            interaction_methods=["turn_on_hot", "turn_on_cold", "turn_off"],
            device_properties={"flow_rate": 0, "temperature": 20}
        )
        
        self.devices["stove_burner"] = VirtualDevice(
            device_id="stove_burner",
            device_type=DeviceType.BURNER_CONTROL,
            name="Stove Burner",
            location="Kitchen",
            casas_sensor_id="AD1-C",
            current_state="OFF",
            interaction_methods=["turn_on", "turn_off", "set_heat"],
            device_properties={"heat_level": 0, "max_heat": 100}
        )
        
        # Dining room devices
        self.devices["dining_light_switch"] = VirtualDevice(
            device_id="dining_light_switch",
            device_type=DeviceType.VIRTUAL_SWITCH,
            name="Dining Room Light Switch",
            location="DiningRoom",
            casas_sensor_id="L02",
            current_state="OFF",
            interaction_methods=["toggle", "turn_on", "turn_off"],
            device_properties={"power_rating": 75}
        )
        
        self.devices["phone"] = VirtualDevice(
            device_id="phone",
            device_type=DeviceType.PHONE_DEVICE,
            name="Dining Room Phone",
            location="DiningRoom",
            casas_sensor_id="*",
            current_state="INACTIVE",
            interaction_methods=["pickup", "hangup", "dial", "listen"],
            device_properties={"phone_type": "landline"}
        )
        
        print(f"🔧 Enhanced VLM: Initialized {len(self.devices)} virtual devices")
    
    def interact_with_device(self, device_id: str, interaction_type: str, 
                           actor_position: Tuple[float, float, float]) -> Dict[str, Any]:
        """Interact with a virtual device and generate CASAS events"""
        
        if device_id not in self.devices:
            return {"success": False, "error": f"Device {device_id} not found"}
        
        device = self.devices[device_id]
        timestamp = time.time()
        
        # Process interaction based on device type
        result = self._process_interaction(device, interaction_type)
        
        if result["success"]:
            # Generate CASAS event
            casas_event = self._generate_casas_event(device, interaction_type, result)
            
            # Record interaction
            interaction_record = {
                "device_id": device_id,
                "interaction_type": interaction_type,
                "actor_position": actor_position,
                "timestamp": timestamp,
                "result": result,
                "casas_event": casas_event
            }
            
            self.interaction_history.append(interaction_record)
            if casas_event:
                self.casas_events.append(casas_event)
            
            print(f"🎮 Device interaction: {device.name} - {interaction_type}")
            if casas_event:
                print(f"📊 CASAS event: {casas_event['sensor']},{casas_event['message']}")
        
        return result
    
    def _process_interaction(self, device: VirtualDevice, interaction_type: str) -> Dict[str, Any]:
        """Process device-specific interaction logic"""
        
        if device.device_type == DeviceType.VIRTUAL_SWITCH:
            if interaction_type == "toggle":
                new_state = "ON" if device.current_state == "OFF" else "OFF"
                device.current_state = new_state
                return {"success": True, "new_state": new_state, "action": "toggled"}
                
        elif device.device_type == DeviceType.VIRTUAL_LIGHT:
            if interaction_type == "illuminate":
                device.current_state = "ON"
                device.device_properties["brightness"] = 80
                return {"success": True, "new_state": "ON", "brightness": 80}
                
        elif device.device_type == DeviceType.WATER_CONTROL:
            if interaction_type in ["turn_on_hot", "turn_on_cold"]:
                device.current_state = "ON"
                flow_rate = 50
                temperature = 40 if "hot" in interaction_type else 15
                device.device_properties["flow_rate"] = flow_rate
                device.device_properties["temperature"] = temperature
                return {"success": True, "flow_rate": flow_rate, "temperature": temperature}
            elif interaction_type == "turn_off":
                device.current_state = "OFF"
                device.device_properties["flow_rate"] = 0
                return {"success": True, "new_state": "OFF", "flow_rate": 0}
                
        elif device.device_type == DeviceType.BURNER_CONTROL:
            if interaction_type == "turn_on":
                device.current_state = "ON"
                heat_level = 50
                device.device_properties["heat_level"] = heat_level
                return {"success": True, "new_state": "ON", "heat_level": heat_level}
            elif interaction_type == "turn_off":
                device.current_state = "OFF"
                device.device_properties["heat_level"] = 0
                return {"success": True, "new_state": "OFF", "heat_level": 0}
                
        elif device.device_type == DeviceType.PHONE_DEVICE:
            if interaction_type == "pickup":
                device.current_state = "ACTIVE"
                return {"success": True, "new_state": "ACTIVE", "action": "phone_pickup"}
            elif interaction_type == "hangup":
                device.current_state = "INACTIVE"
                return {"success": True, "new_state": "INACTIVE", "action": "phone_hangup"}
                
        return {"success": False, "error": f"Unknown interaction: {interaction_type}"}
    
    def _generate_casas_event(self, device: VirtualDevice, interaction_type: str, 
                            result: Dict[str, Any]) -> Dict[str, str]:
        """Generate CASAS sensor event from device interaction"""
        
        sensor_id = device.casas_sensor_id
        timestamp = time.strftime("%Y-%m-%d,%H:%M:%S.%f")[:-3]
        
        # Generate appropriate CASAS message
        if device.device_type == DeviceType.VIRTUAL_SWITCH:
            message = result.get("new_state", "OFF")
        elif device.device_type == DeviceType.VIRTUAL_LIGHT:
            message = "ON" if result.get("brightness", 0) > 0 else "OFF"
        elif device.device_type == DeviceType.WATER_CONTROL:
            message = str(result.get("flow_rate", 0))
        elif device.device_type == DeviceType.BURNER_CONTROL:
            message = str(result.get("heat_level", 0))
        elif device.device_type == DeviceType.PHONE_DEVICE:
            action = result.get("action", "")
            if action == "phone_pickup":
                message = "PHONE_PICKUP"
            elif action == "phone_hangup":
                message = "PHONE_HANGUP"
            else:
                message = "PHONE_INACTIVE"
        else:
            message = "UNKNOWN"
        
        return {
            "date": timestamp.split(",")[0],
            "time": timestamp.split(",")[1],
            "sensor": sensor_id,
            "message": message
        }
    
    def get_devices_in_room(self, room_name: str) -> List[VirtualDevice]:
        """Get all interactable devices in a specific room"""
        return [device for device in self.devices.values() if device.location == room_name]
    
    def get_interaction_prompts_for_room(self, room_name: str) -> str:
        """Get VLM prompt text for device interactions in a room"""
        devices = self.get_devices_in_room(room_name)
        
        if not devices:
            return "No interactive devices available in this room."
        
        prompt_parts = [f"\n🎮 INTERACTIVE DEVICES IN {room_name.upper()}:"]
        
        for device in devices:
            methods = ", ".join(device.interaction_methods)
            prompt_parts.append(f"   • {device.name}: {methods}")
            prompt_parts.append(f"     Current state: {device.current_state}")
        
        prompt_parts.append("\n💡 DEVICE INTERACTION INSTRUCTIONS:")
        prompt_parts.append("   - When near a device, VLM can suggest: 'interact_with_{device_id}'")
        prompt_parts.append("   - Example: 'interact_with_kitchen_light_switch' to toggle kitchen lights")
        prompt_parts.append("   - Device interactions create CASAS sensor events for evaluation")
        
        return "\n".join(prompt_parts)
    
    def get_casas_events(self, limit: int = 50) -> List[Dict[str, str]]:
        """Get generated CASAS events from device interactions"""
        return self.casas_events[-limit:]

# Enhanced CASAS subtask system
class CASASSubtaskManager:
    """Manages CASAS subtasks with duration and checkpoint validation"""
    
    def __init__(self):
        self.casas_tasks = {
            "phone_call": {
                "subtasks": [
                    {"id": "navigate_dining", "description": "Navigate to dining room", "expected_duration": 15, "checkpoints": []},
                    {"id": "pickup_phone_book", "description": "Pick up phone book", "expected_duration": 5, "checkpoints": ["interact_phone_book"]},
                    {"id": "use_phone", "description": "Use phone", "expected_duration": 30, "checkpoints": ["interact_with_phone"]},
                    {"id": "take_notes", "description": "Take notes", "expected_duration": 20, "checkpoints": ["interact_notepad"]},
                    {"id": "cleanup", "description": "Hang up and put away", "expected_duration": 10, "checkpoints": ["interact_with_phone"]}
                ],
                "total_duration": 80
            },
            "wash_hands": {
                "subtasks": [
                    {"id": "navigate_kitchen", "description": "Navigate to kitchen sink", "expected_duration": 10, "checkpoints": []},
                    {"id": "turn_on_water", "description": "Turn on water", "expected_duration": 5, "checkpoints": ["interact_with_water_control"]},
                    {"id": "wash_with_soap", "description": "Apply soap and wash", "expected_duration": 20, "checkpoints": ["interact_soap"]},
                    {"id": "rinse_hands", "description": "Rinse hands", "expected_duration": 10, "checkpoints": []},
                    {"id": "turn_off_water", "description": "Turn off water and dry", "expected_duration": 15, "checkpoints": ["interact_with_water_control"]}
                ],
                "total_duration": 60
            },
            "cook": {
                "subtasks": [
                    {"id": "gather_ingredients", "description": "Gather cooking ingredients", "expected_duration": 20, "checkpoints": []},
                    {"id": "prepare_water", "description": "Measure and add water", "expected_duration": 15, "checkpoints": ["interact_with_water_control"]},
                    {"id": "heat_stove", "description": "Turn on stove burner", "expected_duration": 10, "checkpoints": ["interact_with_stove_burner"]},
                    {"id": "wait_boil", "description": "Wait for water to boil", "expected_duration": 60, "checkpoints": []},
                    {"id": "add_oatmeal", "description": "Add oatmeal to pot", "expected_duration": 15, "checkpoints": []},
                    {"id": "cook_stir", "description": "Cook and stir", "expected_duration": 45, "checkpoints": []},
                    {"id": "serve", "description": "Turn off stove and serve", "expected_duration": 20, "checkpoints": ["interact_with_stove_burner"]}
                ],
                "total_duration": 185
            }
        }
        
        self.current_task: Optional[str] = None
        self.current_subtask_index: int = 0
        self.subtask_start_time: Optional[float] = None
        self.completed_checkpoints: List[str] = []
    
    def start_task(self, task_name: str) -> bool:
        """Start a CASAS task with subtask tracking"""
        task_key = self._normalize_task_name(task_name)
        if task_key in self.casas_tasks:
            self.current_task = task_key
            self.current_subtask_index = 0
            self.subtask_start_time = time.time()
            self.completed_checkpoints = []
            print(f"📋 Starting CASAS task: {task_name} ({task_key})")
            return True
        return False
    
    def _normalize_task_name(self, task_name: str) -> str:
        """Normalize task name to match CASAS keys"""
        task_lower = task_name.lower()
        if "phone" in task_lower or "call" in task_lower:
            return "phone_call"
        elif "wash" in task_lower or "hand" in task_lower:
            return "wash_hands"
        elif "cook" in task_lower or "oatmeal" in task_lower:
            return "cook"
        elif "eat" in task_lower:
            return "eat"
        elif "clean" in task_lower or "dish" in task_lower:
            return "clean"
        return "unknown"
    
    def get_current_subtask(self) -> Optional[Dict[str, Any]]:
        """Get current active subtask"""
        if not self.current_task or self.current_subtask_index >= len(self.casas_tasks[self.current_task]["subtasks"]):
            return None
        return self.casas_tasks[self.current_task]["subtasks"][self.current_subtask_index]
    
    def complete_checkpoint(self, checkpoint_id: str) -> bool:
        """Mark a checkpoint as completed"""
        if checkpoint_id not in self.completed_checkpoints:
            self.completed_checkpoints.append(checkpoint_id)
            print(f"✅ Checkpoint completed: {checkpoint_id}")
            return True
        return False
    
    def check_subtask_completion(self) -> bool:
        """Check if current subtask can be completed"""
        current_subtask = self.get_current_subtask()
        if not current_subtask:
            return False
        
        required_checkpoints = current_subtask.get("checkpoints", [])
        
        # Check if all required checkpoints are completed
        for checkpoint in required_checkpoints:
            if checkpoint not in self.completed_checkpoints:
                print(f"⏳ Waiting for checkpoint: {checkpoint}")
                return False
        
        # Check duration (allow some flexibility)
        if self.subtask_start_time:
            duration = time.time() - self.subtask_start_time
            expected_duration = current_subtask.get("expected_duration", 30)
            
            if duration < (expected_duration * 0.5):  # Too fast
                print(f"⏰ Subtask completed too quickly: {duration:.1f}s < {expected_duration * 0.5:.1f}s")
                return False
        
        return True
    
    def advance_subtask(self) -> bool:
        """Advance to next subtask"""
        if self.check_subtask_completion():
            self.current_subtask_index += 1
            self.subtask_start_time = time.time()
            self.completed_checkpoints = []  # Reset for next subtask
            
            current_subtask = self.get_current_subtask()
            if current_subtask:
                print(f"📋 Advancing to subtask: {current_subtask['description']}")
            else:
                print("🎉 All subtasks completed!")
            return True
        return False
    
    def get_task_progress(self) -> Dict[str, Any]:
        """Get current task progress"""
        if not self.current_task:
            return {"status": "no_active_task"}
        
        task_data = self.casas_tasks[self.current_task]
        current_subtask = self.get_current_subtask()
        
        return {
            "task": self.current_task,
            "subtask_index": self.current_subtask_index,
            "total_subtasks": len(task_data["subtasks"]),
            "current_subtask": current_subtask["description"] if current_subtask else "Complete",
            "required_checkpoints": current_subtask.get("checkpoints", []) if current_subtask else [],
            "completed_checkpoints": self.completed_checkpoints,
            "progress_percentage": (self.current_subtask_index / len(task_data["subtasks"])) * 100,
            "estimated_remaining_time": self._estimate_remaining_time()
        }
    
    def _estimate_remaining_time(self) -> int:
        """Estimate remaining time for current task"""
        if not self.current_task:
            return 0
        
        task_data = self.casas_tasks[self.current_task]
        remaining_subtasks = task_data["subtasks"][self.current_subtask_index:]
        
        return sum(subtask.get("expected_duration", 30) for subtask in remaining_subtasks)

# Global instances
enhanced_vlm_manager = EnhancedVLMManager()
casas_subtask_manager = CASASSubtaskManager()

def get_enhanced_vlm_manager():
    """Get the global enhanced VLM manager"""
    return enhanced_vlm_manager

def get_casas_subtask_manager():
    """Get the global CASAS subtask manager"""
    return casas_subtask_manager
