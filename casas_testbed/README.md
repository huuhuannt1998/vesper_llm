# VESPER-CASAS Testbed Setup Instructions

## Quick Start

1. **Download CASAS Ground Truth Data:**
   ```bash
   # Download from https://zenodo.org/records/15712834
   # Extract adl_noerror.zip and adl_error.zip to:
   # casas_testbed/data/casas_ground_truth/
   ```

2. **Install Dependencies:**
   ```bash
   pip install pandas numpy matplotlib seaborn
   ```

3. **Run Single Task Test:**
   ```python
   from casas_testbed.vesper_casas_runner import VESPERCASASTestbed
   from casas_testbed.simulation.activity_executor import TaskType, ErrorType
   
   testbed = VESPERCASASTestbed(
       casas_ground_truth_dir="casas_testbed/data/casas_ground_truth",
       output_dir="casas_testbed/data"
   )
   
   # Test phone call task
   result = testbed.run_single_task(TaskType.PHONE_CALL, ErrorType.NONE)
   print(result)
   ```

4. **Run Full Evaluation:**
   ```python
   python casas_testbed/vesper_casas_runner.py
   ```

## Integration with VESPER

To integrate with your existing VESPER system, update these files:

### 1. Activity Executor Integration
Edit `casas_testbed/simulation/activity_executor.py`:

```python
def _navigate_to_location(self, location: str) -> bool:
    """Navigate using VESPER VLM system"""
    # Replace this section with actual VESPER calls
    # Example:
    # return self.vesper.navigate_to(location)
```

### 2. VESPER System Initialization
Edit `casas_testbed/vesper_casas_runner.py`:

```python
def __init__(self, casas_ground_truth_dir: str, output_dir: str):
    # Initialize with actual VESPER system
    from blender.llm_bge_navigation import VESPERNavigationSystem
    self.vesper_system = VESPERNavigationSystem()
    self.executor = CASASActivityExecutor(self.vesper_system)
```

## Expected Outputs

### 1. Sensor Data (CASAS Format)
```
2025-08-31,14:30:15.123,M001,ON
2025-08-31,14:30:16.456,I08,ABSENT
2025-08-31,14:30:18.789,*,PICKUP
```

### 2. Comparison Metrics
```json
{
  "temporal": {
    "task_duration_correlation": 0.85,
    "sensor_timing_accuracy": 0.72,
    "sequence_alignment_score": 0.68
  },
  "spatial": {
    "motion_pattern_similarity": 0.79,
    "location_visitation_accuracy": 0.91,
    "path_efficiency_ratio": 0.83
  },
  "behavioral": {
    "object_interaction_accuracy": 0.76,
    "task_completion_fidelity": 0.88,
    "error_detection_capability": 0.65
  },
  "overall": {
    "similarity_score": 0.78
  }
}
```

### 3. Evaluation Summary
```
📊 VESPER-CASAS EVALUATION SUMMARY
================================
📋 Total Tasks: 10
✅ Successful Comparisons: 9
⏱️ Total Duration: 1247.3s

🎯 Task Success Rates:
   Normal Tasks: 90.0%
   Error Tasks: 70.0%
   Overall: 80.0%

🔍 Error Handling:
   Detection Rate: 70.0%
   Correction Rate: 50.0%

📈 Performance Distribution:
   Excellent (≥80%): 3 tasks
   Good (60-80%): 4 tasks
   Fair (40-60%): 2 tasks
   Poor (<40%): 0 tasks
```

## Research Applications

### 1. VLM Spatial Navigation Assessment
- Quantify VLM accuracy in apartment navigation
- Compare path efficiency vs. human behavior
- Analyze failure modes in complex environments

### 2. Object Recognition Evaluation
- Measure VLM ability to identify and interact with objects
- Test recognition under different lighting/angles
- Assess performance with occluded or partially visible items

### 3. Task Understanding Analysis
- Evaluate VLM comprehension of multi-step tasks
- Test ability to maintain task context over time
- Analyze performance degradation with task complexity

### 4. Error Detection Capabilities
- Assess VLM ability to detect procedural errors
- Test error correction and recovery behaviors
- Compare error handling across different error types

### 5. Temporal Pattern Analysis
- Compare VLM timing patterns against human baselines
- Analyze decision-making speed vs. accuracy trade-offs
- Study learning effects across repeated tasks

## Next Steps

1. **Environment Setup:** Download CASAS data and set up ground truth directory
2. **VESPER Integration:** Connect the testbed with your existing VESPER navigation system
3. **Baseline Testing:** Run initial evaluations to establish baseline performance
4. **Iterative Improvement:** Use metrics to identify and improve VLM weaknesses
5. **Research Publication:** Document findings for academic contribution

This testbed provides a comprehensive framework for evaluating VLM performance against established human activity patterns, enabling systematic improvement and validation of embodied AI systems.
