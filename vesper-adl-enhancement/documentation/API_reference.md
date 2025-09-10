# VESPER ADL Enhancement - API Reference

## Core Classes and Methods

### Object Interaction System (`object_interaction_system.py`)

#### CASASObjectManager

Manages CASAS-compatible objects in Blender environment.

```python
class CASASObjectManager:
    def __init__(self):
        """Initialize CASAS object manager with 8 predefined objects (I01-I08)"""
        
    def detect_nearby_objects(self, actor_position: Tuple[float, float, float]) -> List[Dict[str, Any]]:
        """
        Detect CASAS objects within interaction range of actor.
        
        Args:
            actor_position: (x, y, z) coordinates of actor
            
        Returns:
            List of nearby objects with distance and position data
        """
        
    def pick_up_object(self, sensor_id: str, actor_position: Tuple[float, float, float]) -> bool:
        """
        Pick up a CASAS object and trigger item sensor.
        
        Args:
            sensor_id: CASAS sensor ID (I01-I08)
            actor_position: Current actor position
            
        Returns:
            True if successful, False otherwise
        """
        
    def place_object(self, sensor_id: str, location: str) -> bool:
        """
        Place an object from inventory at specified location.
        
        Args:
            sensor_id: CASAS sensor ID
            location: Target location name
            
        Returns:
            True if successful, False otherwise
        """
        
    def get_inventory_status(self) -> List[Dict[str, Any]]:
        """
        Get current actor inventory status.
        
        Returns:
            List of objects in inventory with metadata
        """
```

#### CASAS Objects Reference

| Sensor ID | Object Name | Default Location | Description |
|-----------|-------------|------------------|-------------|
| I01 | oatmeal | kitchen_cabinet | Breakfast ingredient |
| I02 | raisins | kitchen_cabinet | Cooking ingredient |
| I03 | brown_sugar | kitchen_cabinet | Sweetener |
| I04 | bowl | kitchen_cabinet | Serving container |
| I05 | measuring_spoon | kitchen_drawer | Cooking utensil |
| I06 | medicine | bathroom_cabinet | Medication |
| I07 | pot | kitchen_cabinet | Cooking vessel |
| I08 | phone_book | dining_room_table | Communication aid |

#### VLMObjectInteraction

VLM-driven object interaction system.

```python
class VLMObjectInteraction:
    def __init__(self):
        """Initialize VLM object interaction system"""
        
    def analyze_scene_for_objects(self, screenshot_path: str, actor_position: Tuple[float, float, float]) -> Dict[str, Any]:
        """
        Use VLM to analyze scene and identify interactable objects.
        
        Args:
            screenshot_path: Path to environment screenshot
            actor_position: Current actor position
            
        Returns:
            Object analysis with VLM recommendations
        """
        
    def execute_vlm_object_action(self, vlm_response: Dict[str, Any], actor_position: Tuple[float, float, float]) -> bool:
        """
        Execute object interaction based on VLM recommendation.
        
        Args:
            vlm_response: VLM analysis response
            actor_position: Current actor position
            
        Returns:
            True if action executed successfully
        """
```

### Task Execution System (`adl_task_execution_system.py`)

#### ADLTaskExecutor

Executes ADL tasks using VLM guidance and object interaction.

```python
class ADLTaskExecutor:
    def __init__(self):
        """Initialize ADL task executor"""
        
    def start_task(self, task_id: str) -> bool:
        """
        Start executing an ADL task.
        
        Args:
            task_id: Task identifier from CASASTaskLibrary
            
        Returns:
            True if task started successfully
        """
        
    def execute_current_step(self, actor_position: Tuple[float, float, float]) -> bool:
        """
        Execute the current step of the active task.
        
        Args:
            actor_position: Current actor position
            
        Returns:
            True if step completed successfully
        """
        
    def get_task_progress(self) -> Dict[str, Any]:
        """
        Get current task execution progress.
        
        Returns:
            Progress information including completion percentage
        """
```

#### CASASTaskLibrary

Library of CASAS-compatible ADL tasks.

```python
class CASASTaskLibrary:
    def get_task(self, task_id: str) -> Optional[ADLTask]:
        """Get task definition by ID"""
        
    def get_tasks_by_category(self, category: ADLCategory) -> List[ADLTask]:
        """Get all tasks in a specific category"""
        
    def list_all_tasks(self) -> List[str]:
        """List all available task IDs"""
```

#### Available Tasks

| Task ID | Name | Category | Steps | Duration | Description |
|---------|------|----------|-------|----------|-------------|
| cook_oatmeal | Make Oatmeal | COOKING | 5 | 230s | Prepare oatmeal with raisins and brown sugar |
| take_medication | Take Medication | MEDICATION | 4 | 70s | Retrieve and take prescribed medication |
| make_phone_call | Make Phone Call | COMMUNICATION | 4 | 200s | Use phone book to make a call |

#### TaskStep Structure

```python
@dataclass
class TaskStep:
    step_id: str                    # Unique step identifier
    description: str                # Human-readable description
    required_objects: List[str]     # CASAS sensor IDs needed
    required_location: str          # Location requirement
    validation_criteria: Dict       # Success criteria
    estimated_duration: float      # Expected time in seconds
```

### VLM Intelligence Enhancement (`vlm_intelligence_enhancement.py`)

#### AdvancedVLMProcessor

Enhanced VLM processing for complex ADL reasoning.

```python
class AdvancedVLMProcessor:
    def __init__(self):
        """Initialize advanced VLM processor"""
        
    def process_vlm_request(self, template_id: str, context_data: Dict[str, Any], 
                           screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a VLM request using structured templates.
        
        Args:
            template_id: Template identifier
            context_data: Context information for prompt
            screenshot_path: Optional environment screenshot
            
        Returns:
            Processed VLM response with validation
        """
        
    def get_reasoning_analytics(self) -> Dict[str, Any]:
        """
        Get analytics on VLM reasoning performance.
        
        Returns:
            Performance metrics and error patterns
        """
```

#### Available VLM Templates

| Template ID | Context | Complexity | Purpose |
|-------------|---------|------------|---------|
| adl_task_planning | TASK_PLANNING | COMPLEX | Generate multi-step task plans |
| error_recovery | ERROR_RECOVERY | EXPERT | Diagnose failures and create recovery strategies |
| safety_assessment | SAFETY_ASSESSMENT | MODERATE | Evaluate action safety and risks |

#### IntelligentTaskPlanner

Advanced task planning using enhanced VLM reasoning.

```python
class IntelligentTaskPlanner:
    def plan_adaptive_task(self, task_goal: str, environment_context: Dict[str, Any], 
                          screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Plan a task with adaptive reasoning based on environment.
        
        Args:
            task_goal: High-level task description
            environment_context: Current environment state
            screenshot_path: Optional environment screenshot
            
        Returns:
            Adaptive task plan with VLM reasoning
        """
        
    def handle_task_failure_intelligently(self, failed_action: str, error_context: Dict[str, Any], 
                                        screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Use VLM reasoning for intelligent error recovery.
        
        Args:
            failed_action: Description of failed action
            error_context: Error information and context
            screenshot_path: Optional environment screenshot
            
        Returns:
            Recovery strategy with success probability
        """
        
    def assess_action_safety(self, planned_action: str, environment_context: Dict[str, Any],
                           screenshot_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Use VLM for intelligent safety assessment.
        
        Args:
            planned_action: Description of planned action
            environment_context: Current environment state
            screenshot_path: Optional environment screenshot
            
        Returns:
            Safety assessment with risk analysis
        """
```

### Integrated System (`vesper_adl_integrated_system.py`)

#### VESPERADLIntegratedSystem

Main integrated system orchestrating all ADL enhancement components.

```python
class VESPERADLIntegratedSystem:
    def __init__(self, config: SystemConfiguration):
        """Initialize complete VESPER ADL Enhancement system"""
        
    def initialize_system(self) -> bool:
        """
        Initialize the complete system.
        
        Returns:
            True if initialization successful
        """
        
    def execute_adl_session(self, session_tasks: List[str], 
                           evaluation_mode: bool = False) -> Dict[str, Any]:
        """
        Execute a complete ADL session with multiple tasks.
        
        Args:
            session_tasks: List of task descriptions
            evaluation_mode: Enable detailed evaluation metrics
            
        Returns:
            Complete session results with performance metrics
        """
        
    def get_system_status_report(self) -> Dict[str, Any]:
        """
        Get comprehensive system status report.
        
        Returns:
            System status with performance metrics
        """
```

#### SystemConfiguration

```python
@dataclass
class SystemConfiguration:
    mode: SystemMode                # EVALUATION, TRAINING, DEMONSTRATION, RESEARCH
    vlm_model: str                  # VLM model identifier
    evaluation_dataset: str         # Evaluation dataset name
    target_similarity: float        # Target CASAS similarity
    max_execution_time: float       # Maximum execution time
    safety_mode: bool              # Enable safety checks
    logging_level: str             # Logging verbosity
```

## Usage Examples

### Basic Object Interaction

```python
# Initialize object manager
obj_manager = CASASObjectManager()

# Get actor position
actor_pos = (2.0, 1.0, 0.0)

# Detect nearby objects
nearby = obj_manager.detect_nearby_objects(actor_pos)
print(f"Found {len(nearby)} nearby objects")

# Pick up an object
if nearby:
    sensor_id = nearby[0]["sensor_id"]
    success = obj_manager.pick_up_object(sensor_id, actor_pos)
    if success:
        print(f"Successfully picked up {nearby[0]['name']}")
```

### Task Execution

```python
# Initialize task executor
executor = ADLTaskExecutor()

# Start a task
success = executor.start_task("cook_oatmeal")
if success:
    # Execute steps
    while executor.task_status == TaskStatus.IN_PROGRESS:
        step_success = executor.execute_current_step(actor_pos)
        if not step_success:
            break
    
    # Check completion
    if executor.task_status == TaskStatus.COMPLETED:
        print("Task completed successfully!")
```

### Intelligent Planning

```python
# Initialize intelligent planner
planner = IntelligentTaskPlanner()

# Plan adaptive task
environment_context = {
    "actor_position": (2.0, 1.0, 0.0),
    "actor_capabilities": "standard"
}

task_plan = planner.plan_adaptive_task(
    "Make breakfast with available ingredients",
    environment_context,
    "screenshot.png"
)

if task_plan["success"]:
    print("VLM generated intelligent task plan")
    print(f"Strategy: {task_plan['task_plan'].description}")
```

### Complete System Integration

```python
# Create system configuration
config = SystemConfiguration(
    mode=SystemMode.EVALUATION,
    vlm_model="llava:7b",
    evaluation_dataset="casas_2024",
    target_similarity=0.70,
    max_execution_time=300.0,
    safety_mode=True,
    logging_level="INFO"
)

# Initialize system
vesper_system = VESPERADLIntegratedSystem(config)
vesper_system.initialize_system()

# Execute ADL session
tasks = [
    "Make oatmeal with raisins and brown sugar",
    "Take morning medication",
    "Make a phone call using phone book"
]

results = vesper_system.execute_adl_session(tasks, evaluation_mode=True)

# Check performance
performance = results["overall_performance"]
casas_compat = results["casas_compatibility"]

print(f"Task completion rate: {performance['task_completion_rate']:.1%}")
print(f"CASAS similarity: {casas_compat['overall_similarity']:.1%}")
```

## Integration Points

### Blender BGE Integration

```python
# BGE integration functions
def integrate_object_interaction_with_navigation():
    """Integration with existing llm_bge_navigation.py"""
    
def integrate_task_execution_with_navigation():
    """Integration with task execution system"""
    
def integrate_vlm_intelligence_with_system():
    """Integration with VLM intelligence layer"""
    
def initialize_vesper_adl_system():
    """Initialize complete system in BGE"""
```

### Virtual Sensor Integration

```python
# Virtual sensor mappings
ITEM_SENSOR_PORTS = {
    "I01": 9201,  # oatmeal
    "I02": 9202,  # raisins  
    "I03": 9203,  # brown_sugar
    "I04": 9204,  # bowl
    "I05": 9205,  # measuring_spoon
    "I06": 9206,  # medicine
    "I07": 9207,  # pot
    "I08": 9208   # phone_book
}
```

## Error Handling

### Common Error Patterns

| Error Type | Description | Recovery Strategy |
|------------|-------------|-------------------|
| ObjectNotFound | CASAS object not in scene | Check object naming and placement |
| VLMConnectionError | VLM endpoint unavailable | Fallback to default behaviors |
| TaskValidationError | Task step validation failed | Retry with error recovery |
| SafetyViolation | Unsafe action detected | Abort action, assess alternatives |

### Debug Information

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get system diagnostics
status = vesper_system.get_system_status_report()
print(f"System status: {status}")

# Check component health
analytics = vlm_processor.get_reasoning_analytics()
print(f"VLM success rate: {analytics['success_rate']:.1%}")
```

---

**Last Updated:** September 10, 2025  
**Version:** 1.0.0  
**API Stability:** Development Phase
