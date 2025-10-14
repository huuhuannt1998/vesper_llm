"""
VESPER Interaction Integration
Integrates object interaction, virtual devices, and time management with BGE navigation
"""

import sys
import os

# Add parent directory to path to find sibling modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from interaction_system.item_sensor_manager import get_item_sensor_manager, setup_default_item_sensors
from interaction_system.object_interaction_handler import get_interaction_handler, setup_default_interactions
from time_system.virtual_time_manager import get_virtual_time_manager, get_task_timer, TASK_TIME_PROFILES
from virtual_sensors.virtual_device_manager import get_device_manager, setup_default_devices

import time


class VESPERInteractionSystem:
    """
    Central integration point for all interaction systems
    Coordinates object interactions, sensors, devices, and time management
    """
    
    def __init__(self):
        # Initialize all subsystems
        self.item_sensor_manager = get_item_sensor_manager()
        self.interaction_handler = get_interaction_handler()
        self.time_manager = get_virtual_time_manager()
        self.task_timer = get_task_timer()
        self.device_manager = get_device_manager()
        
        # Integration state
        self.current_task = None
        self.task_start_time = None
        self.active_interactions = []
        
        print("✅ VESPER Interaction System initialized")
    
    def setup_all_systems(self):
        """Initialize all subsystems with default configurations"""
        print("\n🔧 Setting up VESPER interaction systems...")
        
        # Setup item sensors
        setup_default_item_sensors()
        
        # Setup interactive objects
        setup_default_interactions()
        
        # Setup virtual devices
        setup_default_devices()
        
        print("✅ All systems configured\n")
    
    def start_task_with_interactions(self, task_name, actor_position):
        """
        Start a task with full interaction support
        
        Args:
            task_name: Name of the task
            actor_position: Current actor position [x, y]
        
        Returns:
            Task context with recommended interactions
        """
        self.current_task = task_name
        self.task_start_time = self.time_manager.get_current_time()
        
        # Start task timer
        expected_duration = self._estimate_task_duration(task_name)
        self.task_timer.start_task_timer(task_name, expected_duration)
        
        # Auto-control devices for task
        task_room = self._infer_task_room(task_name)
        if task_room:
            self.device_manager.auto_control_for_task(task_name, task_room)
        
        # Get nearby interactive objects
        nearby_objects = self.interaction_handler.check_nearby_objects(actor_position)
        
        # Determine if time acceleration is needed
        time_acceleration = self._should_accelerate_time(task_name)
        
        task_context = {
            "task_name": task_name,
            "start_time": self.task_start_time,
            "expected_duration": expected_duration,
            "nearby_objects": nearby_objects,
            "task_room": task_room,
            "time_acceleration": time_acceleration
        }
        
        print(f"\n🎯 Started task: {task_name}")
        print(f"   Room: {task_room}")
        print(f"   Expected duration: {expected_duration}s ({expected_duration/60:.1f} min)")
        if nearby_objects:
            print(f"   Nearby objects: {[obj['object_name'] for obj in nearby_objects]}")
        
        return task_context
    
    def update_interaction_state(self, actor_position, current_task=None):
        """
        Update interaction state based on actor position
        Handles automatic interactions and proximity-based events
        
        Args:
            actor_position: Current actor position [x, y]
            current_task: Current task being performed
        
        Returns:
            List of interaction events
        """
        events = []
        
        # Check for nearby interactive objects
        nearby_objects = self.interaction_handler.check_nearby_objects(actor_position)
        
        # Auto-interact with nearby objects if appropriate
        for obj in nearby_objects:
            if obj["interaction_type"] == "auto" and obj["available"]:
                # Check if this object is relevant to current task
                if self._is_object_relevant_to_task(obj["object_name"], current_task):
                    # Start interaction
                    if self.interaction_handler.start_interaction(
                        obj["object_name"], 
                        current_task
                    ):
                        events.append({
                            "type": "interaction_start",
                            "object": obj["object_name"],
                            "task": current_task
                        })
        
        return events
    
    def complete_task(self, task_name, success=True):
        """
        Complete a task and finalize all interactions
        
        Args:
            task_name: Name of task being completed
            success: Whether task was successful
        """
        # End task timer
        task_duration = self.task_timer.end_task_timer(task_name)
        
        # End any active interactions
        if self.interaction_handler.active_interaction:
            self.interaction_handler.end_interaction()
        
        # Reset time scale to normal
        if self.time_manager.time_scale != 1.0:
            self.time_manager.set_time_scale(1.0, reason="Task completed")
        
        # Turn off devices if appropriate
        # (Could be made more sophisticated)
        
        print(f"\n✅ Task completed: {task_name}")
        if task_duration:
            print(f"   Duration: {task_duration['virtual_duration']:.1f}s ({task_duration['virtual_duration']/60:.1f} min)")
        
        self.current_task = None
    
    def handle_long_duration_task(self, task_name, virtual_duration, max_real_duration=10.0):
        """
        Handle a long-duration task with time acceleration
        
        Args:
            task_name: Name of task
            virtual_duration: How long task takes in virtual time (seconds)
            max_real_duration: Max real-world time to spend (seconds)
        """
        print(f"\n⏩ Starting long-duration task: {task_name}")
        print(f"   Virtual duration: {virtual_duration}s ({virtual_duration/60:.1f} min)")
        print(f"   Real duration: {max_real_duration}s")
        
        # Accelerate time
        self.time_manager.accelerate_for_task(
            task_name,
            virtual_duration,
            max_real_duration
        )
        
        # Wait for task to complete
        print(f"   ⏱️  Task in progress (accelerated time)...")
        time.sleep(max_real_duration)
        
        # Time scale automatically resets
        print(f"   ✅ Task completed!")
    
    def _estimate_task_duration(self, task_name):
        """Estimate task duration based on task name"""
        task_lower = task_name.lower()
        
        # Check known task profiles
        for task_key, duration in TASK_TIME_PROFILES.items():
            if task_key in task_lower:
                return duration
        
        # Default estimates based on keywords
        if "cook" in task_lower:
            return TASK_TIME_PROFILES["cook_simple"]
        elif "eat" in task_lower:
            return TASK_TIME_PROFILES["eat"]
        elif "sleep" in task_lower:
            return TASK_TIME_PROFILES["sleep"]
        elif "wash" in task_lower or "clean" in task_lower:
            return 300  # 5 minutes
        elif "phone" in task_lower or "call" in task_lower:
            return TASK_TIME_PROFILES["phone_call"]
        
        # Default
        return 300  # 5 minutes
    
    def _infer_task_room(self, task_name):
        """Infer which room a task should be performed in"""
        task_lower = task_name.lower()
        
        if any(word in task_lower for word in ["cook", "eat", "kitchen", "oatmeal", "dish"]):
            return "Kitchen"
        elif any(word in task_lower for word in ["sleep", "bed", "bedroom"]):
            return "Bedroom"
        elif any(word in task_lower for word in ["tv", "watch", "living"]):
            return "LivingRoom"
        elif any(word in task_lower for word in ["phone", "dining"]):
            return "DiningRoom"
        elif any(word in task_lower for word in ["shower", "wash", "bathroom"]):
            return "Bathroom"
        
        return None
    
    def _should_accelerate_time(self, task_name):
        """Determine if time acceleration is needed for task"""
        task_lower = task_name.lower()
        
        # Long-duration tasks need acceleration
        long_duration_keywords = ["sleep", "nap", "cook", "watch", "read"]
        
        return any(keyword in task_lower for keyword in long_duration_keywords)
    
    def _is_object_relevant_to_task(self, object_name, task_name):
        """Check if an object is relevant to current task"""
        if not task_name:
            return True  # Allow interaction if no specific task
        
        task_lower = task_name.lower()
        object_lower = object_name.lower()
        
        # Task-object relevance rules
        relevance_map = {
            "phone": ["phone", "call"],
            "sink": ["wash", "clean", "dish"],
            "stove": ["cook"],
            "bed": ["sleep", "nap"],
            "couch": ["sit", "rest", "tv", "watch"],
            "tv": ["watch", "tv"],
            "microwave": ["cook", "heat"],
            "fridge": ["cook", "eat", "get"],
        }
        
        # Check if object keywords appear in task
        for obj_keyword, task_keywords in relevance_map.items():
            if obj_keyword in object_lower:
                if any(task_keyword in task_lower for task_keyword in task_keywords):
                    return True
        
        # Default: allow interaction
        return True
    
    def export_all_data(self):
        """Export data from all subsystems"""
        print("\n💾 Exporting all interaction data...")
        
        # Export item sensor data
        self.item_sensor_manager.export_casas_format()
        self.item_sensor_manager.export_detailed_json()
        
        # Export device log
        self.device_manager.export_device_log()
        
        # Export time log
        self.time_manager.export_time_log(self.item_sensor_manager.dataset_dir)
        
        print("✅ All data exported\n")
    
    def print_session_summary(self):
        """Print comprehensive session summary"""
        print("\n" + "="*70)
        print("VESPER INTERACTION SESSION SUMMARY")
        print("="*70)
        
        # Time summary
        self.time_manager.print_summary()
        
        # Interaction summary
        self.item_sensor_manager.print_summary()
        
        # Device summary
        self.device_manager.print_summary()
        
        print("="*70 + "\n")


# Global instance
_interaction_system = None

def get_interaction_system():
    """Get or create global interaction system"""
    global _interaction_system
    if _interaction_system is None:
        _interaction_system = VESPERInteractionSystem()
        _interaction_system.setup_all_systems()
    return _interaction_system


# BGE Integration helpers
def initialize_interaction_system_for_bge():
    """Initialize interaction system for BGE navigation"""
    try:
        import bge
        
        # Initialize system
        system = get_interaction_system()
        
        # Store in BGE logic for access
        bge.logic.interaction_system = system
        
        print("✅ VESPER Interaction System ready for BGE")
        return True
        
    except Exception as e:
        print(f"⚠️ BGE interaction initialization failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing VESPER Interaction Integration\n")
    
    # Create system
    system = VESPERInteractionSystem()
    system.setup_all_systems()
    
    # Simulate a task
    print("\n📝 Simulating 'Cook oatmeal' task...\n")
    
    actor_pos = [5.0, 3.0]
    task_context = system.start_task_with_interactions("Cook oatmeal", actor_pos)
    
    # Simulate some time passing
    print("\n⏸️  Simulating cooking process...")
    time.sleep(2)
    
    # Simulate interaction with stove
    system.interaction_handler.start_interaction("Stove", "Cook oatmeal")
    time.sleep(3)
    system.interaction_handler.end_interaction("Stove")
    
    # Complete task
    system.complete_task("Cook oatmeal", success=True)
    
    # Print summary
    system.print_session_summary()
    
    # Export data
    system.export_all_data()
