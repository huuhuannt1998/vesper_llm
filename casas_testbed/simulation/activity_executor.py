"""
CASAS Activity Executor
======================

Executes the 5 core CASAS ADL tasks using VESPER VLM navigation.
Integrates with virtual sensor network to generate comparable data.
"""

import time
import sys
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Add VESPER paths
sys.path.insert(0, r"C:\Users\hbui11\Desktop\vesper_llm")
from casas_testbed.simulation.virtual_sensors import VirtualSensorNetwork, SensorReading

class TaskType(Enum):
    PHONE_CALL = 1
    WASH_HANDS = 2  
    COOK = 3
    EAT = 4
    CLEAN = 5

class ErrorType(Enum):
    NONE = "none"
    WRONG_NUMBER = "wrong_number"  # Task 1
    WATER_LEFT_ON = "water_left_on"  # Task 2
    BURNER_LEFT_ON = "burner_left_on"  # Task 3
    NO_MEDICINE = "no_medicine"  # Task 4
    NO_WATER_CLEANING = "no_water_cleaning"  # Task 5

@dataclass
class TaskExecution:
    """Results of a single task execution"""
    task_id: int
    task_name: str
    participant_id: str
    error_type: ErrorType
    success: bool
    duration: float
    sensor_readings: List[SensorReading]
    vlm_actions: List[Dict[str, Any]]
    final_position: Tuple[float, float]
    error_detected: bool = False
    error_corrected: bool = False

class CASASActivityExecutor:
    """Executes CASAS ADL tasks using VESPER VLM navigation"""
    
    def __init__(self, vesper_navigation_system):
        self.vesper = vesper_navigation_system
        self.sensor_network = VirtualSensorNetwork()
        self.current_execution: Optional[TaskExecution] = None
        
        # Task definitions matching CASAS protocol
        self.tasks = {
            TaskType.PHONE_CALL: {
                "name": "Make a phone call",
                "description": "Move to phone in dining room, look up number in phone book, dial number, listen to message, summarize on notepad",
                "target_location": "dining_room",
                "required_objects": ["phone", "phone_book", "notepad"],
                "expected_duration": 180  # 3 minutes
            },
            TaskType.WASH_HANDS: {
                "name": "Wash hands", 
                "description": "Move to kitchen sink, wash hands with soap, dry with paper towel",
                "target_location": "kitchen_sink",
                "required_objects": ["soap", "paper_towel"],
                "expected_duration": 120  # 2 minutes
            },
            TaskType.COOK: {
                "name": "Cook",
                "description": "Cook oatmeal according to phone message - measure water, boil water, add oats, serve with raisins and brown sugar",
                "target_location": "kitchen_stove",
                "required_objects": ["pot", "water", "oatmeal", "raisins", "brown_sugar", "bowl"],
                "expected_duration": 300  # 5 minutes
            },
            TaskType.EAT: {
                "name": "Eat",
                "description": "Take oatmeal and medicine container to dining room and eat",
                "target_location": "dining_room",
                "required_objects": ["oatmeal_bowl", "medicine_container"],
                "expected_duration": 240  # 4 minutes
            },
            TaskType.CLEAN: {
                "name": "Clean",
                "description": "Take dishes to sink and clean with water and dish soap",
                "target_location": "kitchen_sink", 
                "required_objects": ["dishes", "dish_soap", "water"],
                "expected_duration": 180  # 3 minutes
            }
        }
        
    def execute_task(self, task_type: TaskType, participant_id: str, 
                    error_type: ErrorType = ErrorType.NONE) -> TaskExecution:
        """Execute a single CASAS task"""
        
        task_info = self.tasks[task_type]
        start_time = time.time()
        
        # Initialize execution tracking
        self.current_execution = TaskExecution(
            task_id=task_type.value,
            task_name=task_info["name"],
            participant_id=participant_id,
            error_type=error_type,
            success=False,
            duration=0.0,
            sensor_readings=[],
            vlm_actions=[],
            final_position=(0.0, 0.0)
        )
        
        # Clear sensor log for this task
        self.sensor_network.clear_log()
        
        try:
            # Execute task-specific logic
            if task_type == TaskType.PHONE_CALL:
                success = self._execute_phone_call(error_type)
            elif task_type == TaskType.WASH_HANDS:
                success = self._execute_wash_hands(error_type)
            elif task_type == TaskType.COOK:
                success = self._execute_cook(error_type)
            elif task_type == TaskType.EAT:
                success = self._execute_eat(error_type)
            elif task_type == TaskType.CLEAN:
                success = self._execute_clean(error_type)
            else:
                success = False
                
            self.current_execution.success = success
            
        except Exception as e:
            print(f"❌ Task execution failed: {e}")
            self.current_execution.success = False
            
        finally:
            # Finalize execution data
            self.current_execution.duration = time.time() - start_time
            self.current_execution.sensor_readings = self.sensor_network.sensor_log.copy()
            self.current_execution.final_position = self._get_current_position()
            
        return self.current_execution
        
    def _execute_phone_call(self, error_type: ErrorType) -> bool:
        """Execute phone call task with optional error injection"""
        
        try:
            # Navigate to dining room
            success = self._navigate_to_location("dining_room")
            if not success:
                return False
                
            # Look up number in phone book
            self._interact_with_object("phone_book", "pickup")
            time.sleep(2)  # Simulate reading time
            
            # Pick up phone
            self._interact_with_object("phone", "pickup")
            
            # Inject error if specified
            if error_type == ErrorType.WRONG_NUMBER:
                # Dial wrong number first
                self._phone_action("dial_wrong")
                time.sleep(3)  # Listen to wrong number
                self._phone_action("hangup")
                
                # Then dial correct number
                self._phone_action("dial_correct")
            else:
                # Dial correct number directly
                self._phone_action("dial_correct")
                
            # Listen to message
            time.sleep(10)  # Simulate listening time
            
            # Hang up phone
            self._phone_action("hangup")
            
            # Write summary on notepad
            self._interact_with_object("notepad", "write")
            time.sleep(5)  # Simulate writing time
            
            return True
            
        except Exception as e:
            print(f"❌ Phone call task failed: {e}")
            return False
            
    def _execute_wash_hands(self, error_type: ErrorType) -> bool:
        """Execute hand washing task with optional error injection"""
        
        try:
            # Navigate to kitchen sink
            success = self._navigate_to_location("kitchen_sink")
            if not success:
                return False
                
            # Turn on water
            self._water_control("turn_on", flow_rate=0.6)
            
            # Use soap
            self._interact_with_object("soap", "use")
            
            # Wash hands (simulate scrubbing)
            time.sleep(15)  # 15 seconds hand washing
            
            # Inject error if specified  
            if error_type != ErrorType.WATER_LEFT_ON:
                # Turn off water (normal behavior)
                self._water_control("turn_off")
            # else: leave water on (error)
            
            # Dry hands with paper towel
            self._interact_with_object("paper_towel", "use")
            time.sleep(3)  # Simulate drying
            
            # Check if error was corrected
            if error_type == ErrorType.WATER_LEFT_ON:
                # Simulate VLM potentially noticing and correcting
                if self._vlm_detect_error("water still running"):
                    self._water_control("turn_off")
                    self.current_execution.error_detected = True
                    self.current_execution.error_corrected = True
                    
            return True
            
        except Exception as e:
            print(f"❌ Hand washing task failed: {e}")
            return False
            
    def _execute_cook(self, error_type: ErrorType) -> bool:
        """Execute cooking task with optional error injection"""
        
        try:
            # Navigate to kitchen stove area
            success = self._navigate_to_location("kitchen_stove")
            if not success:
                return False
                
            # Get pot and measure water
            self._interact_with_object("pot", "pickup")
            self._interact_with_object("measuring_cup", "use")
            
            # Fill pot with water at sink
            self._navigate_to_location("kitchen_sink")
            self._water_control("turn_on", flow_rate=0.8)
            time.sleep(5)  # Fill pot
            self._water_control("turn_off")
            
            # Return to stove
            self._navigate_to_location("kitchen_stove")
            
            # Turn on burner and boil water
            self._burner_control("turn_on", heat_level=0.8)
            time.sleep(30)  # Wait for water to boil
            
            # Add oats
            self._interact_with_object("oatmeal", "add_to_pot")
            time.sleep(10)  # Cook oatmeal
            
            # Inject error if specified
            if error_type != ErrorType.BURNER_LEFT_ON:
                # Turn off burner (normal behavior)
                self._burner_control("turn_off")
            # else: leave burner on (error)
            
            # Serve oatmeal
            self._interact_with_object("bowl", "pickup")
            self._serve_food("oatmeal", "bowl")
            
            # Add toppings
            self._interact_with_object("raisins", "add_to_bowl")
            self._interact_with_object("brown_sugar", "add_to_bowl")
            
            # Check if error was corrected
            if error_type == ErrorType.BURNER_LEFT_ON:
                if self._vlm_detect_error("burner still on"):
                    self._burner_control("turn_off")
                    self.current_execution.error_detected = True
                    self.current_execution.error_corrected = True
                    
            return True
            
        except Exception as e:
            print(f"❌ Cooking task failed: {e}")
            return False
            
    def _execute_eat(self, error_type: ErrorType) -> bool:
        """Execute eating task with optional error injection"""
        
        try:
            # Get oatmeal bowl
            self._interact_with_object("oatmeal_bowl", "pickup")
            
            # Get medicine container (or forget it if error)
            if error_type != ErrorType.NO_MEDICINE:
                self._interact_with_object("medicine_container", "pickup")
            # else: forget medicine (error)
            
            # Navigate to dining room
            success = self._navigate_to_location("dining_room")
            if not success:
                return False
                
            # Check if error was detected
            if error_type == ErrorType.NO_MEDICINE:
                if self._vlm_detect_error("forgot medicine"):
                    # Go back for medicine
                    self._navigate_to_location("kitchen")
                    self._interact_with_object("medicine_container", "pickup")
                    self._navigate_to_location("dining_room")
                    self.current_execution.error_detected = True
                    self.current_execution.error_corrected = True
                    
            # Eat meal
            time.sleep(60)  # Simulate eating time
            
            # Take medicine
            if "medicine_container" in [action.get("object") for action in self.current_execution.vlm_actions]:
                self._interact_with_object("medicine_container", "take_medicine")
                
            return True
            
        except Exception as e:
            print(f"❌ Eating task failed: {e}")
            return False
            
    def _execute_clean(self, error_type: ErrorType) -> bool:
        """Execute cleaning task with optional error injection"""
        
        try:
            # Collect dishes
            self._interact_with_object("dishes", "collect")
            
            # Navigate to kitchen sink
            success = self._navigate_to_location("kitchen_sink")
            if not success:
                return False
                
            # Get dish soap
            self._interact_with_object("dish_soap", "pickup")
            
            # Clean dishes
            if error_type != ErrorType.NO_WATER_CLEANING:
                # Use water normally
                self._water_control("turn_on", flow_rate=0.7)
                time.sleep(20)  # Simulate washing
                self._water_control("turn_off")
            else:
                # Skip water (error) - just use soap
                time.sleep(20)  # Simulate "washing" without water
                
            # Check if error was detected
            if error_type == ErrorType.NO_WATER_CLEANING:
                if self._vlm_detect_error("dishes not properly cleaned"):
                    # Rewash with water
                    self._water_control("turn_on", flow_rate=0.7)
                    time.sleep(15)  # Rewash
                    self._water_control("turn_off")
                    self.current_execution.error_detected = True
                    self.current_execution.error_corrected = True
                    
            return True
            
        except Exception as e:
            print(f"❌ Cleaning task failed: {e}")
            return False
            
    # Helper methods for VESPER integration
    
    def _navigate_to_location(self, location: str) -> bool:
        """Navigate using VESPER VLM system"""
        try:
            # This would integrate with your existing VESPER navigation
            prompt = f"Navigate to the {location}. Move carefully and identify the target location."
            
            # Simulate VLM navigation (replace with actual VESPER call)
            success = True  # Replace with actual navigation result
            
            # Update sensors based on movement
            current_pos = self._get_current_position()
            self.sensor_network.update_sensors(current_pos)
            
            # Log action
            self.current_execution.vlm_actions.append({
                "action": "navigate",
                "target": location,
                "success": success,
                "timestamp": time.time()
            })
            
            return success
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
            
    def _interact_with_object(self, object_name: str, action: str):
        """Interact with objects and trigger sensors"""
        current_pos = self._get_current_position()
        
        # Update sensors based on interaction
        context = {"item": object_name}
        readings = self.sensor_network.update_sensors(current_pos, action, context)
        
        # Log action
        self.current_execution.vlm_actions.append({
            "action": action,
            "object": object_name,
            "position": current_pos,
            "sensor_readings": len(readings),
            "timestamp": time.time()
        })
        
    def _water_control(self, action: str, flow_rate: float = 0.5):
        """Control water and trigger water sensors"""
        current_pos = self._get_current_position()
        context = {"water": True, "flow_rate": flow_rate}
        
        if action == "turn_off":
            context["flow_rate"] = 0.0
            
        readings = self.sensor_network.update_sensors(current_pos, action, context)
        
        self.current_execution.vlm_actions.append({
            "action": f"water_{action}",
            "flow_rate": flow_rate,
            "timestamp": time.time()
        })
        
    def _burner_control(self, action: str, heat_level: float = 0.5):
        """Control stove burner and trigger sensors"""
        current_pos = self._get_current_position()
        context = {"burner": True, "heat_level": heat_level}
        
        if action == "turn_off":
            context["heat_level"] = 0.0
            
        readings = self.sensor_network.update_sensors(current_pos, action, context)
        
        self.current_execution.vlm_actions.append({
            "action": f"burner_{action}",
            "heat_level": heat_level,
            "timestamp": time.time()
        })
        
    def _phone_action(self, action: str):
        """Handle phone interactions"""
        current_pos = self._get_current_position()
        context = {"phone": True}
        readings = self.sensor_network.update_sensors(current_pos, action, context)
        
        self.current_execution.vlm_actions.append({
            "action": f"phone_{action}",
            "timestamp": time.time()
        })
        
    def _serve_food(self, food: str, container: str):
        """Handle food serving"""
        self.current_execution.vlm_actions.append({
            "action": "serve",
            "food": food,
            "container": container,
            "timestamp": time.time()
        })
        
    def _vlm_detect_error(self, error_description: str) -> bool:
        """Simulate VLM error detection capability"""
        # This would use actual VLM analysis
        # For now, simulate 70% detection rate
        import random
        detected = random.random() < 0.7
        
        if detected:
            print(f"🔍 VLM detected error: {error_description}")
            
        return detected
        
    def _get_current_position(self) -> Tuple[float, float]:
        """Get current actor position from VESPER"""
        # This would integrate with your VESPER system
        # For now, return a simulated position
        return (0.0, 0.0)  # Replace with actual position
        
    def export_execution(self, execution: TaskExecution, output_dir: str):
        """Export execution data in CASAS format"""
        filename = f"{output_dir}/p{execution.participant_id}.t{execution.task_id}.csv"
        self.sensor_network.export_to_casas_format(filename)
        
        # Also save detailed execution data
        import json
        detail_filename = f"{output_dir}/p{execution.participant_id}.t{execution.task_id}_details.json"
        with open(detail_filename, 'w') as f:
            json.dump({
                "task_id": execution.task_id,
                "task_name": execution.task_name,
                "participant_id": execution.participant_id,
                "error_type": execution.error_type.value,
                "success": execution.success,
                "duration": execution.duration,
                "vlm_actions": execution.vlm_actions,
                "final_position": execution.final_position,
                "error_detected": execution.error_detected,
                "error_corrected": execution.error_corrected,
                "sensor_summary": self.sensor_network.get_sensor_summary()
            }, f, indent=2)
