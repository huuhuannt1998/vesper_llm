# Blender-CASAS Integration Guide

## Overview

This guide shows how to integrate real CASAS event generation into the Blender VLM navigation system.

## Current Status

**BEFORE**: We were generating simulated CASAS events without running Blender
**NOW**: We have a proper CASAS generator that can be integrated into Blender navigation
**NEXT**: Connect the generator to actual Blender actor movement and tasks

## Integration Steps

### Step 1: Add CASAS Import to Blender Navigation

Add this to the top of `blender/llm_bge_navigation.py`:

```python
# Add after existing imports
try:
    # Import CASAS generator for real event generation
    vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
    if vesper_root not in sys.path:
        sys.path.insert(0, vesper_root)
    
    from casas_testbed.blender_casas_generator import (
        init_blender_casas, blender_room_entered, blender_room_left,
        blender_task_started, blender_task_completed, finalize_blender_casas,
        get_casas_status
    )
    CASAS_AVAILABLE = True
    print("🏠 CASAS: Generator connected to Blender")
except ImportError as e:
    CASAS_AVAILABLE = False
    print(f"⚠️ CASAS: Generator not available - {e}")
```

### Step 2: Initialize CASAS in Blender Main Function

In the `main()` function initialization block:

```python
# Add after bge.logic.vesper_nav_init = True
if CASAS_AVAILABLE:
    # Initialize CASAS generation for this session
    casas_session = init_blender_casas("p01")
    bge.logic.casas_session_id = casas_session
    bge.logic.casas_last_room = None
    print(f"🏠 CASAS: Session started - {casas_session}")
```

### Step 3: Track Room Transitions

Add room detection logic to track when actor moves between rooms:

```python
def detect_current_room(actor_position):
    """Detect which room the actor is currently in based on position"""
    x, y, z = actor_position
    
    # Room boundaries (adjust based on your Blender layout)
    if -2 <= x <= 2 and -2 <= y <= 2:
        return "living_room"
    elif 3 <= x <= 7 and -2 <= y <= 2:
        return "kitchen"
    elif -2 <= x <= 2 and 3 <= y <= 7:
        return "bedroom"
    elif 3 <= x <= 7 and 3 <= y <= 7:
        return "bathroom"
    # Add more room mappings based on your layout
    else:
        return "hallway"

# Add to main navigation loop
if CASAS_AVAILABLE and actor:
    current_room = detect_current_room(actor.worldPosition)
    last_room = getattr(bge.logic, 'casas_last_room', None)
    
    if current_room != last_room:
        if last_room:
            blender_room_left(last_room)
        blender_room_entered(current_room, actor.worldPosition)
        bge.logic.casas_last_room = current_room
```

### Step 4: Track Task Events

Add task tracking to the existing task system:

```python
# When starting a task (in start_task method)
if CASAS_AVAILABLE:
    blender_task_started(task_name)

# When completing a task (in task validation logic)
if CASAS_AVAILABLE and task_completed:
    blender_task_completed(current_task)
```

### Step 5: Save CASAS Dataset on Exit

Add cleanup when Blender session ends:

```python
# Add exit handler or manual save
def save_casas_dataset():
    if CASAS_AVAILABLE:
        dataset_file = finalize_blender_casas()
        if dataset_file:
            print(f"💾 CASAS: Dataset saved - {dataset_file}")
        return dataset_file
    return None
```

## Testing the Integration

### Test 1: Standalone CASAS Generator

```bash
cd C:\Users\hbui11\Desktop\vesper_llm
python casas_testbed\blender_casas_generator.py
```

This should create a test CASAS dataset file.

### Test 2: Blender with CASAS Integration

1. Open Blender with one of the house layouts
2. Run the modified `llm_bge_navigation.py`
3. Execute VLM navigation tasks
4. Check `casas_testbed/blender_datasets/` for generated CSV files

### Test 3: Compare with Ground Truth

Use the existing comparison system:

```python
from casas_testbed.integration import VESPERCASASIntegration

integration = VESPERCASASIntegration()

# Load real Blender-generated dataset
real_dataset = "casas_testbed/blender_datasets/blender_p01_vlm_navigation_*.csv"

# Compare with ground truth
metrics = integration.compare_with_ground_truth(real_dataset, "phone_call")
print(f"Real navigation similarity: {metrics.overall_similarity:.1%}")
```

## Expected Results

With real Blender integration, you should see:

1. **Higher Similarity Scores**: Real navigation should match ground truth better than simulation
2. **Realistic Timing**: Events generated based on actual actor movement timing
3. **Accurate Room Mapping**: CASAS events triggered by actual room entry/exit
4. **Task-Based Events**: Device interactions triggered by completed VLM tasks

## File Locations

- **CASAS Generator**: `casas_testbed/blender_casas_generator.py`
- **Blender Navigation**: `blender/llm_bge_navigation.py` (to be modified)
- **Generated Datasets**: `casas_testbed/blender_datasets/`
- **Integration System**: `casas_testbed/integration/vesper_casas_integration.py`

## Next Steps

1. Modify `blender/llm_bge_navigation.py` with the integration code above
2. Test the CASAS generator standalone
3. Run Blender navigation with CASAS integration
4. Compare real datasets with ground truth
5. Tune room boundaries and sensor mappings for better accuracy
