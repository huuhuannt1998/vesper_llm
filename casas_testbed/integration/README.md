# VESPER-CASAS Integration Usage Guide

## Overview

The VESPER-CASAS integration provides a clean, production-ready system for connecting Blender VLM navigation with CASAS dataset generation and evaluation.

## File Structure (Cleaned)

```
casas_testbed/integration/
├── vesper_casas_integration.py    # 🎯 Main production system
├── vesper_device_bridge.py        # 🔧 Low-level device management
├── __init__.py                     # 📦 Package exports
└── backup_*.py                     # 📁 Old test files (archived)
```

## Quick Start

### 1. Simple Task Evaluation

```python
from casas_testbed.integration import run_phone_call_evaluation

# Run complete phone call evaluation
results = run_phone_call_evaluation()

if results["success"]:
    print(f"Similarity: {results['metrics'].overall_similarity:.1%}")
    print(f"Dataset: {results['dataset_file']}")
    print(f"Report: {results['report_file']}")
```

### 2. Custom Task Evaluation

```python
from casas_testbed.integration import run_task_evaluation

# Evaluate any task type
results = run_task_evaluation(
    task_type="wash_hands",
    participant_id=2, 
    task_id="t2"
)
```

### 3. Full Integration System

```python
from casas_testbed.integration import VESPERCASASIntegration

# Create integration system
integration = VESPERCASASIntegration(output_dir="my_results")

# Discover devices
devices = integration.discover_devices()

# Run complete evaluation workflow  
results = integration.run_complete_evaluation(
    task_type="cook",
    participant_id=1,
    task_id="t3"
)
```

## Integration with Blender

The system is designed to integrate with actual Blender VLM navigation:

```python
# In production, this connects to real Blender navigation
events = integration.execute_blender_task("phone_call", duration=120)

# Currently falls back to realistic simulation
# TODO: Connect to blender/llm_bge_navigation.py
```

## Output Files

Each evaluation generates:

1. **CASAS Dataset** (`session_id.csv`)
   ```
   date,time,sensor,message
   2025-09-02,14:00:08.899,M13,ON
   2025-09-02,14:00:23.900,A01,PHONE_PICKUP
   ```

2. **Evaluation Report** (`session_id_report.md`)
   - Similarity metrics
   - Sensor coverage analysis
   - Event comparison details

## Task Types Supported

- `phone_call` - Phone call activity (Task 1)
- `wash_hands` - Hand washing activity (Task 2) 
- `cook` - Cooking activity (Task 3)
- `eat` - Eating activity (Task 4)
- `clean` - Cleaning activity (Task 5)

## Evaluation Metrics

- **Overall Similarity**: Combined score (0.0-1.0)
- **Sensor Coverage**: % of ground truth sensors detected
- **Event Ratio**: Proportion of events generated vs ground truth
- **Common Sensors**: Sensors found in both VESPER and ground truth

## Next Steps for Production

1. **Connect to Real Blender Navigation**
   - Integrate with `blender/llm_bge_navigation.py`
   - Monitor actor position and generate events from movement
   - Replace simulation with actual VLM task execution

2. **Enhance Sensor Mapping**
   - Map Blender room positions to more CASAS sensor IDs
   - Increase event density for better similarity scores

3. **Real-time Device Integration**
   - Connect simulated events to actual virtual device state changes
   - Use position-based triggers for realistic sensor activation

## API Reference

See docstrings in `vesper_casas_integration.py` for complete API documentation.
