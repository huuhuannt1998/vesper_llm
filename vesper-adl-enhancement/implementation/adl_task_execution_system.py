#!/usr/bin/env python3
"""
VESPER ADL Enhancement - Phase 2: Task Execution System

Implements CASAS-compatible ADL task execution including:
- Multi-step task planning and execution
- Activity recognition and progression tracking
- Complex cooking, cleaning, and medication tasks
- Task success validation and error recovery

Build on Phase 1 object interaction foundation.
"""

import bge
import mathutils
from typing import Dict, List, Tuple, Optional, Any, Callable
import json
import time
from dataclasses import dataclass
from enum import Enum

# Import Phase 1 foundation
from object_interaction_system import CASASObjectManager, VLMObjectInteraction

class TaskStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ADLCategory(Enum):
    COOKING = "cooking"
    CLEANING = "cleaning"
    MEDICATION = "medication"
    COMMUNICATION = "communication"
    PERSONAL_CARE = "personal_care"
    MOBILITY = "mobility"

@dataclass
class TaskStep:
    """Individual step in an ADL task"""
    step_id: str
    description: str
    required_objects: List[str]  # CASAS sensor IDs
    required_location: str
    validation_criteria: Dict[str, Any]
    estimated_duration: float  # seconds
    
@dataclass
class ADLTask:
    """Complete ADL task definition"""
    task_id: str
    name: str
    category: ADLCategory
    description: str
    steps: List[TaskStep]
    total_estimated_duration: float
    success_criteria: Dict[str, Any]

class CASASTaskLibrary:
    """Library of CASAS-compatible ADL tasks"""
    
    def __init__(self):
        self.tasks = self._initialize_task_library()
    
    def _initialize_task_library(self) -> Dict[str, ADLTask]:
        """Initialize comprehensive CASAS task library"""
        
        tasks = {}
        
        # COOKING: Make Oatmeal (from CASAS dataset)
        tasks["cook_oatmeal"] = ADLTask(
            task_id="cook_oatmeal",
            name="Make Oatmeal",
            category=ADLCategory.COOKING,
            description="Prepare oatmeal with raisins and brown sugar",
            steps=[
                TaskStep(
                    step_id="gather_ingredients",
                    description="Collect oatmeal, raisins, brown sugar, and bowl",
                    required_objects=["I01", "I02", "I03", "I04"],  # oatmeal, raisins, brown_sugar, bowl
                    required_location="kitchen",
                    validation_criteria={"objects_in_inventory": ["I01", "I02", "I03", "I04"]},
                    estimated_duration=45.0
                ),
                TaskStep(
                    step_id="get_pot",
                    description="Get pot for cooking",
                    required_objects=["I07"],  # pot
                    required_location="kitchen",
                    validation_criteria={"objects_in_inventory": ["I07"]},
                    estimated_duration=15.0
                ),
                TaskStep(
                    step_id="cook_oatmeal",
                    description="Cook oatmeal in pot",
                    required_objects=["I01", "I07"],  # oatmeal, pot
                    required_location="stove",
                    validation_criteria={"stove_used": True, "cooking_time": 120.0},
                    estimated_duration=120.0
                ),
                TaskStep(
                    step_id="add_ingredients",
                    description="Add raisins and brown sugar to cooked oatmeal",
                    required_objects=["I02", "I03", "I04"],  # raisins, brown_sugar, bowl
                    required_location="counter",
                    validation_criteria={"ingredients_mixed": True},
                    estimated_duration=30.0
                ),
                TaskStep(
                    step_id="serve_meal",
                    description="Serve oatmeal in bowl",
                    required_objects=["I04"],  # bowl
                    required_location="dining_area",
                    validation_criteria={"meal_served": True},
                    estimated_duration=20.0
                )
            ],
            total_estimated_duration=230.0,
            success_criteria={
                "all_steps_completed": True,
                "meal_prepared": True,
                "kitchen_cleaned": True
            }
        )
        
        # MEDICATION: Take Medicine
        tasks["take_medication"] = ADLTask(
            task_id="take_medication",
            name="Take Medication",
            category=ADLCategory.MEDICATION,
            description="Retrieve and take prescribed medication",
            steps=[
                TaskStep(
                    step_id="get_medicine",
                    description="Retrieve medicine from cabinet",
                    required_objects=["I06"],  # medicine
                    required_location="bathroom",
                    validation_criteria={"medicine_retrieved": True},
                    estimated_duration=30.0
                ),
                TaskStep(
                    step_id="check_dosage",
                    description="Check medication dosage and instructions",
                    required_objects=["I06"],  # medicine
                    required_location="bathroom",
                    validation_criteria={"dosage_verified": True},
                    estimated_duration=15.0
                ),
                TaskStep(
                    step_id="take_medicine",
                    description="Take the prescribed medication",
                    required_objects=["I06"],  # medicine
                    required_location="bathroom",
                    validation_criteria={"medication_consumed": True},
                    estimated_duration=10.0
                ),
                TaskStep(
                    step_id="return_medicine",
                    description="Return medicine to storage location",
                    required_objects=["I06"],  # medicine
                    required_location="bathroom_cabinet",
                    validation_criteria={"medicine_stored": True},
                    estimated_duration=15.0
                )
            ],
            total_estimated_duration=70.0,
            success_criteria={
                "medication_taken": True,
                "proper_dosage": True,
                "medicine_returned": True
            }
        )
        
        # COMMUNICATION: Phone Call
        tasks["make_phone_call"] = ADLTask(
            task_id="make_phone_call",
            name="Make Phone Call",
            category=ADLCategory.COMMUNICATION,
            description="Use phone book to look up and make a phone call",
            steps=[
                TaskStep(
                    step_id="get_phone_book",
                    description="Retrieve phone book",
                    required_objects=["I08"],  # phone_book
                    required_location="dining_room",
                    validation_criteria={"phone_book_retrieved": True},
                    estimated_duration=20.0
                ),
                TaskStep(
                    step_id="lookup_number",
                    description="Look up phone number in phone book",
                    required_objects=["I08"],  # phone_book
                    required_location="dining_room_table",
                    validation_criteria={"number_found": True},
                    estimated_duration=45.0
                ),
                TaskStep(
                    step_id="dial_number",
                    description="Dial the phone number",
                    required_objects=[],
                    required_location="living_room",
                    validation_criteria={"number_dialed": True},
                    estimated_duration=15.0
                ),
                TaskStep(
                    step_id="make_call",
                    description="Conduct phone conversation",
                    required_objects=[],
                    required_location="living_room",
                    validation_criteria={"call_completed": True},
                    estimated_duration=120.0
                )
            ],
            total_estimated_duration=200.0,
            success_criteria={
                "call_successful": True,
                "phone_book_used": True,
                "conversation_completed": True
            }
        )
        
        return tasks
    
    def get_task(self, task_id: str) -> Optional[ADLTask]:
        """Get task definition by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_category(self, category: ADLCategory) -> List[ADLTask]:
        """Get all tasks in a specific category"""
        return [task for task in self.tasks.values() if task.category == category]
    
    def list_all_tasks(self) -> List[str]:
        """List all available task IDs"""
        return list(self.tasks.keys())

class ADLTaskExecutor:
    """Executes ADL tasks using VLM guidance and object interaction"""
    
    def __init__(self):
        self.task_library = CASASTaskLibrary()
        self.object_manager = CASASObjectManager()
        self.vlm_interaction = VLMObjectInteraction()
        
        # Task execution state
        self.current_task: Optional[ADLTask] = None
        self.current_step_index: int = 0
        self.task_status: TaskStatus = TaskStatus.NOT_STARTED
        self.step_completion_times: List[float] = []
        self.task_start_time: Optional[float] = None
        
        # Performance tracking
        self.execution_log: List[Dict[str, Any]] = []
        self.error_recovery_attempts: int = 0
        
    def start_task(self, task_id: str) -> bool:
        """Start executing an ADL task"""
        task = self.task_library.get_task(task_id)
        if not task:
            print(f"❌ Unknown task: {task_id}")
            return False
            
        self.current_task = task
        self.current_step_index = 0
        self.task_status = TaskStatus.IN_PROGRESS
        self.task_start_time = time.time()
        self.step_completion_times = []
        self.error_recovery_attempts = 0
        
        print(f"🎯 Starting task: {task.name}")
        print(f"📋 Description: {task.description}")
        print(f"⏱️  Estimated duration: {task.total_estimated_duration}s")
        
        # Log task start
        self.log_task_event("task_started", {
            "task_id": task_id,
            "task_name": task.name,
            "category": task.category.value,
            "total_steps": len(task.steps)
        })
        
        return True
    
    def execute_current_step(self, actor_position: Tuple[float, float, float]) -> bool:
        """Execute the current step of the active task"""
        if not self.current_task or self.task_status != TaskStatus.IN_PROGRESS:
            print("❌ No active task in progress")
            return False
            
        if self.current_step_index >= len(self.current_task.steps):
            print("✅ All task steps completed!")
            self.complete_task()
            return True
            
        current_step = self.current_task.steps[self.current_step_index]
        step_start_time = time.time()
        
        print(f"🔄 Executing step {self.current_step_index + 1}/{len(self.current_task.steps)}: {current_step.description}")
        
        # Check if actor is in required location
        if not self.verify_location(actor_position, current_step.required_location):
            print(f"⚠️  Actor not in required location: {current_step.required_location}")
            return False
            
        # Execute step based on required objects
        success = self.execute_step_actions(current_step, actor_position)
        
        if success:
            step_duration = time.time() - step_start_time
            self.step_completion_times.append(step_duration)
            
            print(f"✅ Step completed in {step_duration:.1f}s (estimated: {current_step.estimated_duration}s)")
            
            # Log step completion
            self.log_task_event("step_completed", {
                "step_id": current_step.step_id,
                "step_index": self.current_step_index,
                "duration": step_duration,
                "estimated_duration": current_step.estimated_duration
            })
            
            self.current_step_index += 1
            return True
        else:
            print(f"❌ Step failed: {current_step.description}")
            self.handle_step_failure(current_step)
            return False
    
    def execute_step_actions(self, step: TaskStep, actor_position: Tuple[float, float, float]) -> bool:
        """Execute the specific actions required for a task step"""
        
        # For each required object, attempt to interact with it
        for object_sensor_id in step.required_objects:
            obj_data = self.object_manager.casas_objects.get(object_sensor_id)
            if not obj_data:
                print(f"❌ Unknown object sensor: {object_sensor_id}")
                return False
                
            # Check if object is already in inventory
            if object_sensor_id in self.object_manager.actor_inventory:
                print(f"✅ {obj_data['name']} already in inventory")
                continue
                
            # Attempt to pick up the object
            success = self.object_manager.pick_up_object(object_sensor_id, actor_position)
            if not success:
                print(f"❌ Failed to pick up {obj_data['name']}")
                return False
        
        # Validate step completion criteria
        return self.validate_step_completion(step)
    
    def validate_step_completion(self, step: TaskStep) -> bool:
        """Validate that step completion criteria are met"""
        criteria = step.validation_criteria
        
        # Check inventory requirements
        if "objects_in_inventory" in criteria:
            required_objects = criteria["objects_in_inventory"]
            for obj_id in required_objects:
                if obj_id not in self.object_manager.actor_inventory:
                    print(f"❌ Validation failed: {obj_id} not in inventory")
                    return False
        
        # Additional validation logic would go here based on criteria
        # For now, basic inventory check is sufficient
        
        return True
    
    def verify_location(self, actor_position: Tuple[float, float, float], required_location: str) -> bool:
        """Verify actor is in the required location for the task step"""
        # This would integrate with your room detection system
        # For now, return True as placeholder
        return True
    
    def handle_step_failure(self, step: TaskStep):
        """Handle step execution failure with error recovery"""
        self.error_recovery_attempts += 1
        
        if self.error_recovery_attempts > 3:
            print("❌ Too many failures, aborting task")
            self.task_status = TaskStatus.FAILED
            self.log_task_event("task_failed", {
                "reason": "too_many_step_failures",
                "failed_step": step.step_id
            })
            return
        
        print(f"🔄 Attempting error recovery (attempt {self.error_recovery_attempts})")
        
        # Log failure for analysis
        self.log_task_event("step_failed", {
            "step_id": step.step_id,
            "failure_reason": "execution_error",
            "recovery_attempt": self.error_recovery_attempts
        })
    
    def complete_task(self):
        """Mark task as completed and calculate performance metrics"""
        if not self.current_task or not self.task_start_time:
            return
            
        total_duration = time.time() - self.task_start_time
        
        self.task_status = TaskStatus.COMPLETED
        
        # Calculate performance metrics
        estimated_duration = self.current_task.total_estimated_duration
        efficiency = estimated_duration / total_duration if total_duration > 0 else 0
        
        print(f"🎉 Task '{self.current_task.name}' completed!")
        print(f"⏱️  Total time: {total_duration:.1f}s (estimated: {estimated_duration}s)")
        print(f"📊 Efficiency: {efficiency:.2f}")
        
        # Log task completion
        self.log_task_event("task_completed", {
            "task_id": self.current_task.task_id,
            "total_duration": total_duration,
            "estimated_duration": estimated_duration,
            "efficiency": efficiency,
            "steps_completed": len(self.step_completion_times)
        })
    
    def log_task_event(self, event_type: str, data: Dict[str, Any]):
        """Log task execution events for analysis"""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "task_id": self.current_task.task_id if self.current_task else None,
            "data": data
        }
        
        self.execution_log.append(event)
        
        # Also log to BGE evaluation system if available
        if hasattr(bge.logic, 'evaluation_log'):
            if 'task_events' not in bge.logic.evaluation_log:
                bge.logic.evaluation_log['task_events'] = []
            bge.logic.evaluation_log['task_events'].append(event)
    
    def get_task_progress(self) -> Dict[str, Any]:
        """Get current task execution progress"""
        if not self.current_task:
            return {"status": "no_active_task"}
            
        progress = {
            "task_name": self.current_task.name,
            "task_id": self.current_task.task_id,
            "status": self.task_status.value,
            "current_step": self.current_step_index,
            "total_steps": len(self.current_task.steps),
            "progress_percentage": (self.current_step_index / len(self.current_task.steps)) * 100,
            "elapsed_time": time.time() - self.task_start_time if self.task_start_time else 0,
            "estimated_remaining": self.current_task.total_estimated_duration - sum(self.step_completion_times)
        }
        
        if self.current_step_index < len(self.current_task.steps):
            current_step = self.current_task.steps[self.current_step_index]
            progress["current_step_description"] = current_step.description
            progress["current_step_objects"] = current_step.required_objects
            
        return progress

# Integration function for main VLM navigation system
def integrate_task_execution_with_navigation():
    """Integration point with existing navigation system"""
    
    # Initialize task executor
    if not hasattr(bge.logic, 'task_executor'):
        bge.logic.task_executor = ADLTaskExecutor()
    
    # Get current actor position
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    
    if not actor:
        return
        
    actor_pos = tuple(actor.worldPosition)
    
    # Execute current task step if task is active
    executor = bge.logic.task_executor
    if executor.task_status == TaskStatus.IN_PROGRESS:
        executor.execute_current_step(actor_pos)

# Test function for Phase 2 development
def test_task_execution_system():
    """Test the ADL task execution system"""
    print("🧪 Testing VESPER ADL Task Execution System...")
    
    # Initialize system
    executor = ADLTaskExecutor()
    
    # List available tasks
    print("📋 Available tasks:")
    for task_id in executor.task_library.list_all_tasks():
        task = executor.task_library.get_task(task_id)
        print(f"  - {task_id}: {task.name} ({task.category.value})")
    
    # Test starting a task
    success = executor.start_task("cook_oatmeal")
    if success:
        print("✅ Task started successfully")
        
        # Get progress
        progress = executor.get_task_progress()
        print(f"📊 Progress: {progress}")
        
        # Simulate step execution
        actor_pos = (2.0, 1.0, 0.0)  # Kitchen position
        
        # Execute a few steps
        for i in range(3):
            print(f"\n--- Executing step {i+1} ---")
            step_success = executor.execute_current_step(actor_pos)
            
            progress = executor.get_task_progress()
            print(f"📊 Progress: {progress['progress_percentage']:.1f}%")
            
            if not step_success:
                break
    
    print("🧪 Task execution system test complete!")

if __name__ == "__main__":
    # Run tests when executed directly
    test_task_execution_system()
