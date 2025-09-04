# CASAS Integration Status

## Current Problem

You are correct! We have been generating **simulated** CASAS events without actually running Blender. Here's what's happening:

### What We Have:
1. **Blender VLM Navigation** (`blender/llm_bge_navigation.py`)
   - Runs VLM-based navigation tasks in Blender
   - Actor moves through rooms following LLM instructions
   - NO CASAS event generation currently

2. **CASAS Simulation** (`casas_testbed/integration/vesper_casas_integration.py`)
   - Generates fake CASAS events based on task patterns
   - Never actually connects to Blender
   - Uses `time.sleep()` to simulate task duration

### What We Need:
- **Real Integration**: Connect Blender navigation to CASAS event generation
- **Position-Based Events**: Generate CASAS events when actor enters/exits rooms
- **Task-Based Events**: Generate device interaction events during specific tasks

## Solution: True Blender-CASAS Integration

### Step 1: Add CASAS Event Generation to Blender
Modify `blender/llm_bge_navigation.py` to:
- Track actor position and room transitions
- Generate CASAS events when entering rooms (motion sensors)
- Generate device events when completing tasks (appliances, phones, etc.)

### Step 2: Room-to-Sensor Mapping
Create mapping from Blender room names to CASAS sensor IDs:
```
Kitchen → M13, D07, T01
Bedroom → M02, M15, D03
Bathroom → M08, T02
Living Room → M01, D01, I02
```

### Step 3: Event Generation Logic
```python
# When actor enters kitchen
generate_casas_event("M13", "ON", timestamp)

# When task "phone_call" completes
generate_casas_event("A01", "PHONE_PICKUP", timestamp)
generate_casas_event("A01", "PHONE_HANGUP", timestamp + 30)

# When actor leaves kitchen  
generate_casas_event("M13", "OFF", timestamp)
```

## Files Organization

All CASAS-related files are now properly organized in `casas_testbed/`:

```
casas_testbed/
├── integration/           # Production CASAS integration
├── data/                 # CASAS ground truth datasets (220 files)
├── blender_casas_*.csv   # Generated event files (moved here)
├── vesper_casas_bridge.py # Device bridge (moved here)
└── simulation/           # Test environments
```

## Next Steps

1. **Integrate CASAS into Blender**: Add event generation to `llm_bge_navigation.py`
2. **Test Real Navigation**: Run actual Blender tasks with CASAS event output
3. **Validate Events**: Compare real navigation events with ground truth data

The current system is generating realistic-looking CASAS events, but they're simulated. We need to connect them to actual Blender navigation for real dataset generation.
