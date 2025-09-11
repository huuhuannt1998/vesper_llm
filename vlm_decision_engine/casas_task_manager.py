"""
CASAS Task Manager
==================

Manages CASAS ADL tasks with detailed subtask breakdown and device interaction requirements.
Maps tasks to specific rooms, required objects, and expected durations.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

class CASASTaskType(Enum):
    """CASAS ADL task types from the dataset"""
    PHONE_CALL = "t1"      # Make a phone call
    WASH_HANDS = "t2"      # Wash hands  
    COOK = "t3"            # Cook oatmeal
    EAT = "t4"             # Eat meal
    CLEAN = "t5"           # Clean dishes

@dataclass
class SubTask:
    """Individual subtask within a CASAS task"""
    id: str
    description: str
    target_room: str
    required_objects: List[str]
    required_devices: List[str]  # Virtual switches, lights, sensors
    expected_duration: int  # seconds
    sensor_triggers: List[str]  # Expected CASAS sensor activations
    interaction_checkpoints: List[str]  # Device interactions that validate completion
    completion_criteria: str

@dataclass
class CASASTask:
    """Complete CASAS ADL task definition"""
    task_type: CASASTaskType
    name: str
    description: str
    subtasks: List[SubTask]
    total_expected_duration: int
    primary_rooms: List[str]
    required_objects: List[str]
    success_criteria: List[str]
    error_scenarios: List[str]  # Common failure modes for this task

class CASASTaskManager:
    """Manages CASAS ADL tasks and subtask progression"""
    
    def __init__(self):
        self.task_definitions = self._initialize_casas_tasks()
        self.current_task: Optional[CASASTask] = None
        self.current_subtask_index: int = 0
        self.task_start_time: Optional[float] = None
        self.subtask_completion_log: List[Dict[str, Any]] = []
        
    def _initialize_casas_tasks(self) -> Dict[CASASTaskType, CASASTask]:
        """Initialize all CASAS task definitions with detailed subtasks"""
        
        tasks = {}
        
        # Task 1: Make a phone call
        tasks[CASASTaskType.PHONE_CALL] = CASASTask(
            task_type=CASASTaskType.PHONE_CALL,
            name="Make a phone call",
            description="Move to phone in dining room, look up number in phone book, dial and listen to cooking directions, summarize on notepad",
            subtasks=[
                SubTask(
                    id="t1_s1",
                    description="Navigate to dining room",
                    target_room="DiningRoom",
                    required_objects=[],
                    required_devices=[],
                    expected_duration=15,
                    sensor_triggers=["M03_ON", "M04_ON"],
                    interaction_checkpoints=[],
                    completion_criteria="Actor position in dining room"
                ),
                SubTask(
                    id="t1_s2", 
                    description="Pick up phone book",
                    target_room="DiningRoom",
                    required_objects=["phone_book"],
                    required_devices=[],
                    expected_duration=5,
                    sensor_triggers=["I08_PRESENT"],
                    interaction_checkpoints=["interact_phone_book"],
                    completion_criteria="Phone book interaction detected"
                ),
                SubTask(
                    id="t1_s3",
                    description="Use phone to make call",
                    target_room="DiningRoom", 
                    required_objects=["phone"],
                    required_devices=["virtual_phone"],
                    expected_duration=30,
                    sensor_triggers=["*_PHONE_PICKUP", "*_PHONE_ACTIVE"],
                    interaction_checkpoints=["activate_phone", "listen_message"],
                    completion_criteria="Phone conversation completed"
                ),
                SubTask(
                    id="t1_s4",
                    description="Take notes from phone message",
                    target_room="DiningRoom",
                    required_objects=["notepad", "pen"],
                    required_devices=[],
                    expected_duration=20,
                    sensor_triggers=[],
                    interaction_checkpoints=["interact_notepad"],
                    completion_criteria="Notes taken successfully"
                ),
                SubTask(
                    id="t1_s5",
                    description="Hang up phone and put away phone book",
                    target_room="DiningRoom",
                    required_objects=["phone", "phone_book"],
                    required_devices=["virtual_phone"],
                    expected_duration=10,
                    sensor_triggers=["*_PHONE_HANGUP", "I08_ABSENT"],
                    interaction_checkpoints=["deactivate_phone", "put_away_phone_book"],
                    completion_criteria="Phone call ended, items stored"
                )
            ],
            total_expected_duration=80,
            primary_rooms=["DiningRoom"],
            required_objects=["phone", "phone_book", "notepad", "pen"],
            success_criteria=["All subtasks completed", "Notes taken", "Phone returned to original state"],
            error_scenarios=["Phone book missing", "Phone not working", "Unable to hear message"]
        )
        
        # Task 2: Wash hands
        tasks[CASASTaskType.WASH_HANDS] = CASASTask(
            task_type=CASASTaskType.WASH_HANDS,
            name="Wash hands",
            description="Move to kitchen sink, wash hands with soap, dry with paper towel",
            subtasks=[
                SubTask(
                    id="t2_s1",
                    description="Navigate to kitchen sink",
                    target_room="Kitchen",
                    required_objects=[],
                    required_devices=[],
                    expected_duration=10,
                    sensor_triggers=["M13_ON", "M14_ON"],
                    interaction_checkpoints=[],
                    completion_criteria="Actor at kitchen sink area"
                ),
                SubTask(
                    id="t2_s2",
                    description="Turn on water faucet",
                    target_room="Kitchen",
                    required_objects=["faucet"],
                    required_devices=["virtual_water_control"],
                    expected_duration=5,
                    sensor_triggers=["AD1-A_50"],  # Water level 50%
                    interaction_checkpoints=["activate_water_hot", "activate_water_cold"],
                    completion_criteria="Water running at appropriate temperature"
                ),
                SubTask(
                    id="t2_s3",
                    description="Apply soap and wash hands",
                    target_room="Kitchen",
                    required_objects=["soap"],
                    required_devices=[],
                    expected_duration=20,
                    sensor_triggers=[],
                    interaction_checkpoints=["interact_soap", "scrub_hands"],
                    completion_criteria="Hands washed thoroughly with soap"
                ),
                SubTask(
                    id="t2_s4",
                    description="Rinse hands under water",
                    target_room="Kitchen",
                    required_objects=["faucet"],
                    required_devices=["virtual_water_control"],
                    expected_duration=10,
                    sensor_triggers=["AD1-A_75"],  # Increased water usage
                    interaction_checkpoints=["rinse_hands"],
                    completion_criteria="Soap rinsed off hands"
                ),
                SubTask(
                    id="t2_s5",
                    description="Turn off water and dry hands",
                    target_room="Kitchen",
                    required_objects=["paper_towel"],
                    required_devices=["virtual_water_control"],
                    expected_duration=15,
                    sensor_triggers=["AD1-A_0"],  # Water off
                    interaction_checkpoints=["deactivate_water", "interact_paper_towel"],
                    completion_criteria="Water off, hands dried"
                )
            ],
            total_expected_duration=60,
            primary_rooms=["Kitchen"],
            required_objects=["soap", "paper_towel", "faucet"],
            success_criteria=["Hands clean and dry", "Water turned off", "No water waste"],
            error_scenarios=["No soap available", "Water too hot/cold", "No paper towels"]
        )
        
        # Task 3: Cook oatmeal
        tasks[CASASTaskType.COOK] = CASASTask(
            task_type=CASASTaskType.COOK,
            name="Cook oatmeal",
            description="Cook oatmeal per phone directions - measure water, boil in pot, add oats, serve with raisins and brown sugar",
            subtasks=[
                SubTask(
                    id="t3_s1",
                    description="Navigate to kitchen and gather ingredients",
                    target_room="Kitchen", 
                    required_objects=["pot", "measuring_cup"],
                    required_devices=[],
                    expected_duration=20,
                    sensor_triggers=["M13_ON", "M14_ON", "I07_PRESENT", "I05_PRESENT"],
                    interaction_checkpoints=["get_pot", "get_measuring_cup"],
                    completion_criteria="Cooking utensils gathered"
                ),
                SubTask(
                    id="t3_s2",
                    description="Measure and add water to pot",
                    target_room="Kitchen",
                    required_objects=["pot", "measuring_cup", "water"],
                    required_devices=["virtual_water_control"],
                    expected_duration=15,
                    sensor_triggers=["AD1-A_100"],  # Water filling
                    interaction_checkpoints=["measure_water", "fill_pot"],
                    completion_criteria="Correct amount of water in pot"
                ),
                SubTask(
                    id="t3_s3",
                    description="Place pot on stove and turn on burner",
                    target_room="Kitchen",
                    required_objects=["pot", "stove"],
                    required_devices=["virtual_burner_control"],
                    expected_duration=10,
                    sensor_triggers=["AD1-C_80"],  # Burner on high
                    interaction_checkpoints=["place_pot_on_stove", "activate_burner"],
                    completion_criteria="Burner on, pot heating"
                ),
                SubTask(
                    id="t3_s4",
                    description="Wait for water to boil",
                    target_room="Kitchen",
                    required_objects=["pot"],
                    required_devices=["virtual_burner_control"],
                    expected_duration=60,
                    sensor_triggers=["AD1-C_80"],  # Sustained heating
                    interaction_checkpoints=["monitor_boiling"],
                    completion_criteria="Water at rolling boil"
                ),
                SubTask(
                    id="t3_s5",
                    description="Add oatmeal to boiling water",
                    target_room="Kitchen",
                    required_objects=["oatmeal", "measuring_spoon"],
                    required_devices=[],
                    expected_duration=15,
                    sensor_triggers=["I01_PRESENT", "I05_PRESENT"],
                    interaction_checkpoints=["measure_oatmeal", "add_to_pot"],
                    completion_criteria="Oatmeal added to pot"
                ),
                SubTask(
                    id="t3_s6", 
                    description="Cook oatmeal and stir",
                    target_room="Kitchen",
                    required_objects=["spoon"],
                    required_devices=["virtual_burner_control"],
                    expected_duration=45,
                    sensor_triggers=["AD1-C_40"],  # Reduced heat
                    interaction_checkpoints=["reduce_heat", "stir_oatmeal"],
                    completion_criteria="Oatmeal cooked to proper consistency"
                ),
                SubTask(
                    id="t3_s7",
                    description="Turn off burner and serve with toppings",
                    target_room="Kitchen",
                    required_objects=["bowl", "raisins", "brown_sugar"],
                    required_devices=["virtual_burner_control"],
                    expected_duration=20,
                    sensor_triggers=["AD1-C_0", "I02_PRESENT", "I03_PRESENT", "I04_PRESENT"],
                    interaction_checkpoints=["deactivate_burner", "serve_oatmeal", "add_toppings"],
                    completion_criteria="Oatmeal served with raisins and brown sugar"
                )
            ],
            total_expected_duration=185,
            primary_rooms=["Kitchen"],
            required_objects=["pot", "measuring_cup", "oatmeal", "raisins", "brown_sugar", "bowl", "spoon"],
            success_criteria=["Oatmeal cooked properly", "Burner turned off", "Toppings added"],
            error_scenarios=["Water boils over", "Oatmeal burns", "Missing ingredients"]
        )
        
        # Task 4: Eat meal
        tasks[CASASTaskType.EAT] = CASASTask(
            task_type=CASASTaskType.EAT,
            name="Eat meal",
            description="Take oatmeal and medicine to dining room and eat",
            subtasks=[
                SubTask(
                    id="t4_s1",
                    description="Get oatmeal bowl and medicine",
                    target_room="Kitchen",
                    required_objects=["oatmeal_bowl", "medicine_container"],
                    required_devices=[],
                    expected_duration=10,
                    sensor_triggers=["I04_PRESENT", "I06_PRESENT"],
                    interaction_checkpoints=["get_oatmeal", "get_medicine"],
                    completion_criteria="Food and medicine gathered"
                ),
                SubTask(
                    id="t4_s2",
                    description="Navigate to dining room",
                    target_room="DiningRoom",
                    required_objects=["oatmeal_bowl", "medicine_container"],
                    required_devices=[],
                    expected_duration=15,
                    sensor_triggers=["M13_OFF", "M03_ON", "M04_ON"],
                    interaction_checkpoints=[],
                    completion_criteria="Arrived at dining table with food"
                ),
                SubTask(
                    id="t4_s3",
                    description="Sit down and take medicine",
                    target_room="DiningRoom",
                    required_objects=["medicine_container"],
                    required_devices=[],
                    expected_duration=10,
                    sensor_triggers=["I06_ABSENT"],  # Medicine taken
                    interaction_checkpoints=["sit_at_table", "take_medicine"],
                    completion_criteria="Medicine consumed"
                ),
                SubTask(
                    id="t4_s4",
                    description="Eat the oatmeal meal",
                    target_room="DiningRoom",
                    required_objects=["oatmeal_bowl", "spoon"],
                    required_devices=[],
                    expected_duration=120,  # 2 minutes eating
                    sensor_triggers=["M03_ON", "M04_ON"],  # Sustained presence
                    interaction_checkpoints=["eat_meal"],
                    completion_criteria="Meal consumed"
                ),
                SubTask(
                    id="t4_s5",
                    description="Finish eating and prepare to clean up",
                    target_room="DiningRoom",
                    required_objects=["empty_bowl"],
                    required_devices=[],
                    expected_duration=10,
                    sensor_triggers=["I04_ABSENT"],  # Bowl empty
                    interaction_checkpoints=["finish_meal"],
                    completion_criteria="Meal completed"
                )
            ],
            total_expected_duration=165,
            primary_rooms=["Kitchen", "DiningRoom"],
            required_objects=["oatmeal_bowl", "medicine_container", "spoon"],
            success_criteria=["Medicine taken", "Meal consumed completely", "Ready for cleanup"],
            error_scenarios=["Forgot medicine", "Food too hot", "Spilled food"]
        )
        
        # Task 5: Clean dishes
        tasks[CASASTaskType.CLEAN] = CASASTask(
            task_type=CASASTaskType.CLEAN,
            name="Clean dishes", 
            description="Take dishes to sink, clean with water and dish soap",
            subtasks=[
                SubTask(
                    id="t5_s1",
                    description="Collect dirty dishes",
                    target_room="DiningRoom",
                    required_objects=["dirty_bowl", "dirty_spoon"],
                    required_devices=[],
                    expected_duration=15,
                    sensor_triggers=["I04_PRESENT", "I07_PRESENT"],
                    interaction_checkpoints=["collect_dishes"],
                    completion_criteria="All dirty dishes gathered"
                ),
                SubTask(
                    id="t5_s2",
                    description="Transport dishes to kitchen sink",
                    target_room="Kitchen",
                    required_objects=["dirty_bowl", "dirty_spoon"],
                    required_devices=[],
                    expected_duration=15,
                    sensor_triggers=["M03_OFF", "M13_ON"],
                    interaction_checkpoints=[],
                    completion_criteria="Dishes at kitchen sink"
                ),
                SubTask(
                    id="t5_s3",
                    description="Turn on water and get dish soap",
                    target_room="Kitchen",
                    required_objects=["dish_soap"],
                    required_devices=["virtual_water_control"],
                    expected_duration=10,
                    sensor_triggers=["AD1-A_60"],  # Water on
                    interaction_checkpoints=["activate_water", "get_dish_soap"],
                    completion_criteria="Water running, soap ready"
                ),
                SubTask(
                    id="t5_s4",
                    description="Wash dishes with soap and water",
                    target_room="Kitchen",
                    required_objects=["dish_soap", "sponge"],
                    required_devices=["virtual_water_control"],
                    expected_duration=45,
                    sensor_triggers=["AD1-A_75"],  # High water usage
                    interaction_checkpoints=["wash_bowl", "wash_spoon", "scrub_dishes"],
                    completion_criteria="Dishes clean and rinsed"
                ),
                SubTask(
                    id="t5_s5",
                    description="Turn off water and put dishes away",
                    target_room="Kitchen",
                    required_objects=["clean_dishes"],
                    required_devices=["virtual_water_control"],
                    expected_duration=20,
                    sensor_triggers=["AD1-A_0", "I04_ABSENT", "I07_ABSENT"],
                    interaction_checkpoints=["deactivate_water", "dry_dishes", "put_away_dishes"],
                    completion_criteria="Water off, dishes stored clean"
                )
            ],
            total_expected_duration=105,
            primary_rooms=["DiningRoom", "Kitchen"],
            required_objects=["dirty_bowl", "dirty_spoon", "dish_soap", "sponge"],
            success_criteria=["All dishes clean", "Water turned off", "Dishes properly stored"],
            error_scenarios=["Soap dispenser empty", "Water too hot", "Dishes still dirty"]
        )
        
        return tasks
    
    def get_task(self, task_type: CASASTaskType) -> CASASTask:
        """Get a specific CASAS task definition"""
        return self.task_definitions.get(task_type)
    
    def start_task(self, task_type: CASASTaskType) -> bool:
        """Start a new CASAS task"""
        task = self.get_task(task_type)
        if task:
            self.current_task = task
            self.current_subtask_index = 0
            self.task_start_time = None  # Will be set when first subtask starts
            self.subtask_completion_log = []
            return True
        return False
    
    def get_current_subtask(self) -> Optional[SubTask]:
        """Get the current active subtask"""
        if self.current_task and self.current_subtask_index < len(self.current_task.subtasks):
            return self.current_task.subtasks[self.current_subtask_index]
        return None
    
    def complete_current_subtask(self, completion_data: Dict[str, Any]) -> bool:
        """Mark current subtask as completed and advance to next"""
        if not self.current_task:
            return False
            
        current_subtask = self.get_current_subtask()
        if not current_subtask:
            return False
        
        # Log completion
        self.subtask_completion_log.append({
            "subtask_id": current_subtask.id,
            "completion_time": completion_data.get("timestamp"),
            "duration": completion_data.get("duration"),
            "checkpoints_completed": completion_data.get("checkpoints", []),
            "sensor_activations": completion_data.get("sensors", []),
            "success": True
        })
        
        # Advance to next subtask
        self.current_subtask_index += 1
        
        return True
    
    def is_task_complete(self) -> bool:
        """Check if current task is completely finished"""
        if not self.current_task:
            return False
        return self.current_subtask_index >= len(self.current_task.subtasks)
    
    def get_task_progress(self) -> Dict[str, Any]:
        """Get current task progress information"""
        if not self.current_task:
            return {"status": "no_active_task"}
        
        current_subtask = self.get_current_subtask()
        
        return {
            "task_type": self.current_task.task_type.value,
            "task_name": self.current_task.name,
            "total_subtasks": len(self.current_task.subtasks),
            "completed_subtasks": self.current_subtask_index,
            "current_subtask": current_subtask.description if current_subtask else None,
            "current_subtask_id": current_subtask.id if current_subtask else None,
            "target_room": current_subtask.target_room if current_subtask else None,
            "required_objects": current_subtask.required_objects if current_subtask else [],
            "required_devices": current_subtask.required_devices if current_subtask else [],
            "interaction_checkpoints": current_subtask.interaction_checkpoints if current_subtask else [],
            "expected_duration": current_subtask.expected_duration if current_subtask else 0,
            "completion_percentage": (self.current_subtask_index / len(self.current_task.subtasks)) * 100,
            "is_complete": self.is_task_complete()
        }
    
    def get_all_task_types(self) -> List[str]:
        """Get list of all available CASAS task types"""
        return [task_type.value for task_type in CASASTaskType]
    
    def validate_subtask_completion(self, subtask: SubTask, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that a subtask has been properly completed"""
        validation_result = {
            "valid": True,
            "missing_checkpoints": [],
            "missing_sensors": [],
            "errors": []
        }
        
        # Check interaction checkpoints
        completed_checkpoints = completion_data.get("checkpoints", [])
        for required_checkpoint in subtask.interaction_checkpoints:
            if required_checkpoint not in completed_checkpoints:
                validation_result["missing_checkpoints"].append(required_checkpoint)
                validation_result["valid"] = False
        
        # Check sensor activations
        triggered_sensors = completion_data.get("sensors", [])
        for required_sensor in subtask.sensor_triggers:
            if required_sensor not in triggered_sensors:
                validation_result["missing_sensors"].append(required_sensor)
                validation_result["valid"] = False
        
        # Check duration constraints
        actual_duration = completion_data.get("duration", 0)
        expected_duration = subtask.expected_duration
        if actual_duration > expected_duration * 2:  # Allow 100% over expected time
            validation_result["errors"].append(f"Task took too long: {actual_duration}s vs expected {expected_duration}s")
            validation_result["valid"] = False
        
        return validation_result
