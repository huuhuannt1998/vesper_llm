# VESPER Interaction System Documentation

## Overview
The VESPER Interaction System extends the navigation capabilities with object interaction, virtual sensors, device control, and time management features compatible with CASAS dataset format.

## System Architecture

```
vesper_llm/blender/
├── interaction_system/
│   ├── item_sensor_manager.py       # CASAS-compatible item sensors
│   └── object_interaction_handler.py # Object interaction logic
├── time_system/
│   └── virtual_time_manager.py      # Time acceleration & tracking
├── virtual_sensors/
│   └── virtual_device_manager.py    # SmartThings-style devices
└── vesper_interaction_integration.py # Main integration module
```

## Features

### 1. Item Sensor Manager
Tracks object interactions similar to CASAS dataset item sensors.

**Features:**
- Track interaction start/end times
- Calculate interaction durations
- CASAS-compatible event logging
- Detailed JSON export

**Supported Sensors:**
- Kitchen: Sink, Stove, Fridge, Microwave, etc.
- Dining: Phone, Table
- Bathroom: Sink, Shower, Toilet
- Bedroom: Bed, Closet, Lamp
- Living Room: TV, Couch, Books

**Usage:**
```python
from item_sensor_manager import get_item_sensor_manager

manager = get_item_sensor_manager()

# Start interaction
manager.interact_with_object("Phone")

# End interaction (automatically calculates duration)
manager.end_interaction("Phone")

# Export CASAS format
manager.export_casas_format()
```

### 2. Object Interaction Handler
Manages actor-object interactions in BGE with VLM guidance.

**Interaction Types:**
- **Manual**: Requires explicit action (e.g., stove, sink)
- **Auto**: Proximity-based (e.g., phone, bed)

**Features:**
- Proximity detection
- Interaction zones
- VLM-guided interaction decisions
- Task-relevant object filtering

**Usage:**
```python
from object_interaction_handler import get_interaction_handler

handler = get_interaction_handler()

# Check nearby objects
nearby = handler.check_nearby_objects(actor_position)

# Start interaction
handler.start_interaction("Stove", task_context="Cook oatmeal")

# End interaction
handler.end_interaction()
```

### 3. Virtual Time Manager
Manages virtual time with acceleration for long-duration tasks.

**Features:**
- Time acceleration (e.g., 8-hour sleep in 5 seconds)
- Virtual timestamps for CASAS compatibility
- Task-based time profiles
- Scheduled events

**Task Time Profiles:**
- Sleep: 8 hours
- Cooking (simple): 15 minutes
- Cooking (complex): 45 minutes
- Eating: 20 minutes
- Phone call: 5 minutes
- Shower: 10 minutes

**Usage:**
```python
from virtual_time_manager import get_virtual_time_manager

time_mgr = get_virtual_time_manager()

# Normal operation (1x speed)
current_time = time_mgr.get_current_time()

# Accelerate for sleeping (8 hours in 5 seconds)
time_mgr.accelerate_for_task("sleeping", 8*3600, max_real_seconds=5.0)

# Fast forward
time_mgr.fast_forward(virtual_seconds=1800, real_seconds=2.0)
```

### 4. Virtual Device Manager
SmartThings-style virtual device control and monitoring.

**Device Types:**
- Lights
- Switches
- Appliances
- Sensors
- Locks
- Thermostats

**Features:**
- Device state tracking
- Automatic task-based control
- Room-based device management
- Usage statistics

**Usage:**
```python
from virtual_device_manager import get_device_manager

device_mgr = get_device_manager()

# Control individual device
device_mgr.control_device("D001", "on")

# Control all devices in room
device_mgr.control_room_devices("Kitchen", "on")

# Auto-control for task
device_mgr.auto_control_for_task("Cook oatmeal", "Kitchen")
```

## Integration with BGE Navigation

### Initialize System
```python
from vesper_interaction_integration import initialize_interaction_system_for_bge

# Initialize all subsystems
initialize_interaction_system_for_bge()
```

### During Navigation
```python
import bge

# Access interaction system
system = bge.logic.interaction_system

# Start task with interactions
task_context = system.start_task_with_interactions(
    "Cook oatmeal",
    actor_position=[5.0, 3.0]
)

# Update during navigation loop
events = system.update_interaction_state(
    actor_position=current_position,
    current_task="Cook oatmeal"
)

# Complete task
system.complete_task("Cook oatmeal", success=True)
```

### Long-Duration Tasks
```python
# Handle 8-hour sleep in 10 real seconds
system.handle_long_duration_task(
    "Go to sleep",
    virtual_duration=8*3600,  # 8 hours
    max_real_duration=10.0    # 10 seconds
)
```

## Data Export

All systems export CASAS-compatible and detailed JSON logs:

### Export Formats
1. **Item Sensor Log** (CASAS format):
   ```
   2024-01-15 10:30:45.123 I001 Phone ON
   2024-01-15 10:31:00.456 I001 Phone OFF
   ```

2. **Detailed JSON**:
   - Full interaction history
   - Duration statistics
   - Task context

3. **Device Log**:
   - Device state changes
   - Activation counts
   - Usage patterns

4. **Time Log**:
   - Virtual time events
   - Time scale changes
   - Task durations

### Export All Data
```python
system = bge.logic.interaction_system

# Export all logs
system.export_all_data()

# Print summary
system.print_session_summary()
```

## Example: Complete Task Flow

```python
# 1. Initialize system
from vesper_interaction_integration import get_interaction_system
system = get_interaction_system()
system.setup_all_systems()

# 2. Start task
actor_pos = [5.0, 3.0]
task_context = system.start_task_with_interactions("Cook oatmeal", actor_pos)

# 3. Navigate to kitchen (existing navigation system)
# ... navigation steps ...

# 4. Interact with objects
system.interaction_handler.start_interaction("Stove", "Cook oatmeal")

# 5. Time-accelerated cooking
system.handle_long_duration_task("Cooking oatmeal", 900, 5.0)  # 15 min → 5 sec

# 6. End interaction
system.interaction_handler.end_interaction()

# 7. Complete task
system.complete_task("Cook oatmeal", success=True)

# 8. Export all data
system.export_all_data()
```

## File Outputs

All data is saved to: `C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\vesper_datasets\`

**Files Generated:**
- `item_sensor_log_YYYYMMDD_HHMMSS.txt` - CASAS format
- `item_interactions_YYYYMMDD_HHMMSS.json` - Detailed JSON
- `device_log_YYYYMMDD_HHMMSS.json` - Device states
- `virtual_time_log.json` - Time events

## CASAS Dataset Compatibility

The interaction system is designed for compatibility with CASAS dataset format:

1. **Timestamps**: CASAS-compatible format with millisecond precision
2. **Sensor IDs**: Standard format (M001-M050 for motion, I001-I050 for items, D001-D050 for devices)
3. **Event format**: Standard ON/OFF events
4. **Room labels**: Consistent room naming

## Task-Object Mapping

The system automatically determines relevant objects for tasks:

| Task | Relevant Objects | Room |
|------|-----------------|------|
| Make phone call | Phone | Dining Room |
| Wash hands | Sink | Kitchen/Bathroom |
| Cook oatmeal | Stove, Sink, Microwave | Kitchen |
| Eat meal | Dining Table | Dining Room |
| Clean dishes | Sink, Dishes | Kitchen |
| Sleep | Bed | Bedroom |
| Watch TV | TV, Couch | Living Room |

## Testing

Each module includes standalone testing:

```bash
# Test item sensors
python interaction_system/item_sensor_manager.py

# Test time system
python time_system/virtual_time_manager.py

# Test devices
python virtual_sensors/virtual_device_manager.py

# Test integration
python vesper_interaction_integration.py
```

## Notes

- Virtual time allows realistic task durations without real-time waiting
- Item sensors automatically track when objects are being used
- Devices can be auto-controlled based on tasks
- All data is CASAS-compatible for evaluation against real datasets
- System integrates seamlessly with existing VLM navigation
