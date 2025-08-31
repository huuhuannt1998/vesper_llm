# VESPER-CASAS Testbed Design Document

## Overview
Create a comprehensive testbed that uses VESPER's VLM navigation system to replicate CASAS smart home activities, then compare VLM-generated sensor patterns against ground truth CASAS data for evaluation.

## Architecture

### 1. Virtual Environment Recreation
```
VESPER-CASAS/
├── environments/
│   ├── chinook_apartment.blend          # Recreated CASAS apartment
│   ├── sensor_placements.json          # Sensor location mapping
│   └── object_locations.json           # Interactive objects
├── simulation/
│   ├── virtual_sensors.py              # Simulated sensor system
│   ├── activity_executor.py            # Task execution engine
│   └── error_injector.py               # Error simulation
├── evaluation/
│   ├── casas_comparator.py             # Ground truth comparison
│   ├── activity_recognizer.py          # Pattern matching
│   └── metrics_calculator.py           # Performance metrics
└── data/
    ├── casas_ground_truth/             # Original CASAS data
    ├── vesper_generated/               # VLM-generated data
    └── comparison_results/             # Analysis results
```

### 2. Core Components

#### A. Environment Recreation (Blender/BGE)
- **Chinook Apartment Model:** Recreate the CASAS apartment layout based on provided floorplan
- **Interactive Objects:** Phone, sink, stove, cabinets, oatmeal, medicine, etc.
- **Sensor Zones:** Virtual sensor placement matching CASAS locations
- **Visual Fidelity:** Ensure VLM can identify objects and locations accurately

#### B. Virtual Sensor System
```python
class VirtualSensorNetwork:
    sensors = {
        # Motion sensors
        'M01-M026': PIRMotionSensor(),
        
        # Item sensors  
        'I01': ItemSensor('oatmeal'),
        'I02': ItemSensor('raisins'),
        'I03': ItemSensor('brown_sugar'),
        'I04': ItemSensor('bowl'),
        'I05': ItemSensor('measuring_spoon'),
        'I06': ItemSensor('medicine_container'),
        'I07': ItemSensor('pot'),
        'I08': ItemSensor('phone_book'),
        
        # Environmental sensors
        'D01': DoorSensor('kitchen_cabinet'),
        'AD1-A': WaterSensor('sink_hot'),
        'AD1-B': WaterSensor('sink_cold'),
        'AD1-C': BurnerSensor('stove'),
        '*': PhoneSensor()
    }
```

#### C. Activity Execution Engine
```python
class CASASActivityExecutor:
    def execute_task(self, task_id, participant_profile, error_mode=False):
        """Execute CASAS task using VLM navigation"""
        
        tasks = {
            1: self.make_phone_call,
            2: self.wash_hands, 
            3: self.cook_oatmeal,
            4: self.eat_meal,
            5: self.clean_dishes
        }
        
        # Record sensor data while VLM navigates
        sensor_log = []
        with SensorRecorder(sensor_log):
            success = tasks[task_id](error_mode)
            
        return sensor_log, success
```

#### D. Ground Truth Comparison
```python
class CASASComparator:
    def compare_execution(self, vesper_log, casas_ground_truth):
        """Compare VLM execution against CASAS data"""
        
        metrics = {
            'temporal_alignment': self.analyze_timing_patterns(),
            'sensor_activation_accuracy': self.compare_sensor_sequences(),
            'spatial_movement_correlation': self.analyze_motion_patterns(),
            'task_completion_fidelity': self.evaluate_task_success(),
            'error_detection_capability': self.assess_error_recognition()
        }
        
        return metrics
```

### 3. Evaluation Framework

#### Primary Research Questions:
1. **Spatial Navigation Accuracy:** Can VLM navigate to correct locations?
2. **Object Recognition Fidelity:** Does VLM identify and interact with correct objects?
3. **Task Sequence Understanding:** Does VLM follow logical task progression?
4. **Error Detection Capability:** Can VLM detect and respond to scripted errors?
5. **Temporal Pattern Matching:** Do VLM-generated sensor patterns match human timing?

#### Evaluation Metrics:
```python
metrics = {
    # Spatial Metrics
    'location_accuracy': location_errors / total_movements,
    'path_efficiency': optimal_path_length / actual_path_length,
    
    # Object Interaction Metrics  
    'object_recognition_rate': correct_objects / total_objects,
    'interaction_sequence_accuracy': correct_sequences / total_sequences,
    
    # Temporal Metrics
    'task_completion_time_correlation': correlation(vlm_times, human_times),
    'sensor_activation_timing_accuracy': timing_alignment_score,
    
    # Error Handling Metrics
    'error_detection_rate': detected_errors / total_errors,
    'error_recovery_success': successful_recoveries / detected_errors
}
```

### 4. Implementation Strategy

#### Phase 1: Environment Setup (Week 1-2)
- Download and analyze CASAS dataset structure
- Recreate Chinook apartment in Blender based on floorplan
- Implement virtual sensor network
- Set up basic VLM navigation integration

#### Phase 2: Activity Implementation (Week 3-4)  
- Implement 5 core CASAS tasks in VESPER
- Create task-specific prompts for VLM
- Develop sensor data recording system
- Test basic task execution

#### Phase 3: Evaluation Framework (Week 5-6)
- Implement CASAS data parser
- Create comparison algorithms
- Develop evaluation metrics
- Build automated testing pipeline

#### Phase 4: Analysis & Validation (Week 7-8)
- Run comprehensive evaluations
- Compare VLM performance against human data
- Analyze failure modes and improvement areas
- Generate research findings

### 5. Expected Outcomes

#### Immediate Capabilities:
- Quantitative assessment of VLM spatial navigation
- Objective measurement of object recognition accuracy
- Systematic evaluation of task understanding
- Benchmarking against established human activity data

#### Research Contributions:
- First comprehensive VLM evaluation using real-world ADL data
- Novel methodology for embodied AI assessment
- Insights into VLM limitations for assistive technology
- Validation framework for smart home AI systems

#### Technical Deliverables:
- VESPER-CASAS testbed codebase
- Automated evaluation pipeline
- Comprehensive performance metrics
- Research dataset for future work

### 6. Next Steps

1. **Download CASAS Data:** Obtain adl_noerror.zip and adl_error.zip
2. **Create Project Structure:** Set up VESPER-CASAS directories
3. **Analyze Ground Truth:** Parse CASAS CSV files to understand patterns
4. **Design Virtual Environment:** Plan Blender apartment recreation
5. **Implement Core Framework:** Build sensor system and activity executor

This testbed will provide unprecedented insight into VLM capabilities for real-world assistive tasks while creating a valuable evaluation framework for the embodied AI community.
