# CASAS Ground Truth Dataset Information

## ✅ Status: 220 Ground Truth Files Available!

### 📍 **Location**
```
casas_testbed/data/casas_ground_truth/
├── adl_error/      (100 files)
└── adl_noerror/    (120 files)
```

---

## 📊 Dataset Structure

### **Total Files: 220 CSV files**

#### **ADL No Error** (120 files)
- **Location**: `casas_testbed/data/casas_ground_truth/adl_noerror/`
- **Format**: `pXX.tY.csv`
  - `XX` = Participant number (01-51)
  - `Y` = Task number (1-5)
- **Purpose**: Clean ADL task executions without errors

**Participants**: 24 total
- p01-p16 (16 participants)
- p32, p40-p43 (5 participants)
- p49-p51 (3 participants)

**Tasks per participant**: 5 tasks (t1-t5)
- t1: Make a phone call
- t2: Wash hands
- t3: Cook oatmeal
- t4: Eat meal
- t5: Clean dishes

**Examples**:
```
p01.t1.csv  → Participant 01, Task 1 (Make a phone call)
p01.t2.csv  → Participant 01, Task 2 (Wash hands)
...
p16.t5.csv  → Participant 16, Task 5 (Clean dishes)
```

#### **ADL Error** (100 files)
- **Location**: `casas_testbed/data/casas_ground_truth/adl_error/`
- **Format**: Same as adl_noerror
- **Purpose**: ADL task executions with common errors/deviations
- **Participants**: 20 participants (fewer than noerror)
- **Tasks**: Same 5 tasks per participant

---

## 🎯 Ground Truth Tasks (CASAS ADL Dataset)

These are the standard CASAS ADL (Activities of Daily Living) tasks:

### **Task 1 (t1): Make a Phone Call**
- Navigate to phone location (typically dining room)
- Pick up phone
- Complete call action

### **Task 2 (t2): Wash Hands**
- Navigate to kitchen sink
- Perform hand washing

### **Task 3 (t3): Cook Oatmeal**
- Navigate to kitchen
- Follow cooking directions
- Use stove/microwave

### **Task 4 (t4): Eat Meal**
- Take food to dining room
- Complete eating activity

### **Task 5 (t5): Clean Dishes**
- Take dishes to sink
- Clean dishes

---

## 📄 CSV File Format

Each CSV file contains CASAS-format sensor events:

```csv
2016-03-01 08:00:00.000000,M001,Living Room,ON
2016-03-01 08:00:05.123456,M001,Living Room,OFF
2016-03-01 08:00:06.234567,M003,Kitchen,ON
...
```

**Columns**:
1. **Timestamp**: YYYY-MM-DD HH:MM:SS.mmmmmm
2. **Sensor ID**: M001-M006 (motion sensors)
3. **Location**: Room name
4. **State**: ON/OFF

---

## 🔗 Mapping to Your VESPER System

### **Motion Sensors**
Your Blender scene should align with CASAS sensor layout:

| Sensor ID | VESPER Object | Location | Ground Truth |
|-----------|---------------|----------|--------------|
| M001 | motion1 | Living Room | M001 |
| M002 | motion2 | Bedroom1 | M002 |
| M003 | motion3 | Kitchen | M003 |
| M004 | motion4 | Bedroom2 | M004 |
| M005 | motion5 | Bathroom1 | M005 |
| M006 | motion6 | Bathroom2 | M006 |

### **Task Alignment**
Configure your navigation tasks to match CASAS tasks:

**Current VESPER tasks** (in `llm_bge_navigation.py`):
```python
bge.logic.vesper_tasks = [
    "Go to the kitchen",
    "Go to the bedroom",
    "Go to the livingroom"
]
```

**Recommended CASAS-aligned tasks**:
```python
bge.logic.vesper_tasks = [
    "Make a phone call",     # t1: CASAS task 1
    "Wash hands",            # t2: CASAS task 2
    "Cook oatmeal",          # t3: CASAS task 3
    "Eat meal",              # t4: CASAS task 4
    "Clean dishes"           # t5: CASAS task 5
]
```

---

## 📈 How Ground Truth Comparison Works

### **1. Generate VESPER Data**
```bash
python blender/llm_bge_navigation.py
```
**Output**: `blender/vesper_motion_sensors.txt`

### **2. Compare with Ground Truth**
```bash
python evaluation/vesper_dataset_pipeline.py
```

### **3. Comparison Process**

The evaluation pipeline will:

1. **Load Ground Truth**: Read CSV files from `adl_noerror/` or `adl_error/`
2. **Load VESPER Data**: Read your generated `vesper_motion_sensors.txt`
3. **Align Timestamps**: Match events based on timing
4. **Compare Sensors**: Check if same sensors activated
5. **Calculate Metrics**:
   - **Temporal Accuracy**: Did sensors fire at similar times?
   - **Spatial Accuracy**: Did the same sensors activate?
   - **Event Correlation**: Do sensor patterns match activity?

### **4. Expected Results**

**Good Performance**:
- Temporal Accuracy: > 70%
- Spatial Accuracy: > 80%
- Event Correlation: > 0.7

**What affects accuracy**:
- Navigation path quality (VLM decisions)
- Motion sensor placement and bounds
- Task execution efficiency
- Environmental layout differences

---

## 🔍 Inspecting Ground Truth Data

### **View a sample file**:
```bash
# Windows PowerShell
Get-Content "casas_testbed\data\casas_ground_truth\adl_noerror\p01.t1.csv" -Head 20

# Linux/Mac
head -20 casas_testbed/data/casas_ground_truth/adl_noerror/p01.t1.csv
```

### **Count events in a file**:
```bash
# Windows
Get-Content "casas_testbed\data\casas_ground_truth\adl_noerror\p01.t1.csv" | Measure-Object -Line

# Linux/Mac
wc -l casas_testbed/data/casas_ground_truth/adl_noerror/p01.t1.csv
```

### **Analyze sensor distribution**:
```python
import csv
from collections import Counter

# Read a ground truth file
with open('casas_testbed/data/casas_ground_truth/adl_noerror/p01.t1.csv', 'r') as f:
    reader = csv.reader(f)
    sensors = [row[1] for row in reader if len(row) >= 2]

# Count sensor activations
sensor_counts = Counter(sensors)
print("Sensor activations in p01.t1 (Make a phone call):")
for sensor, count in sensor_counts.most_common():
    print(f"  {sensor}: {count} events")
```

---

## 🎓 Research Context

### **CASAS Dataset Background**
- **Source**: Washington State University CASAS Smart Home Project
- **Purpose**: Activity recognition in smart home environments
- **Data Type**: Real sensor data from physical smart home testbed
- **Participants**: Real human subjects performing ADL tasks
- **Quality**: Ground truth validated by human observation

### **Why Compare?**
1. **Validation**: Verify your VLM navigation generates realistic sensor patterns
2. **Benchmarking**: Compare simulated vs. real-world sensor activations
3. **Training Data**: Use comparison to improve VLM and navigation algorithms
4. **Research**: Publish results showing simulation-to-reality transfer

### **Expected Differences**
Your VESPER simulation may differ from ground truth because:
- **Simulated vs. Real**: Perfect sensor placement vs. real-world noise
- **AI Navigation**: VLM decisions vs. human movement
- **Environment**: Blender scene vs. physical testbed layout
- **Timing**: Simulated physics vs. real-world physics

**Goal**: Achieve similar sensor activation patterns, not exact matches

---

## 📊 Using Ground Truth for Evaluation

### **Compare Single Task**:
```python
from evaluation.casas_comparison import compare_casas_files

# Compare your generated data with ground truth task 1
result = compare_casas_files(
    'blender/vesper_motion_sensors.txt',  # Your data
    'casas_testbed/data/casas_ground_truth/adl_noerror/p01.t1.csv'  # Ground truth
)

print(f"Accuracy: {result['accuracy']}%")
print(f"Matching events: {result['matches']}")
```

### **Batch Comparison**:
```python
from pathlib import Path
from evaluation.vesper_dataset_pipeline import VESPERDatasetPipeline

# Compare with all ground truth files
pipeline = VESPERDatasetPipeline()
results = pipeline.run_full_pipeline()

print(f"Average accuracy across {len(results)} comparisons:")
print(f"  Temporal: {results['temporal_avg']}%")
print(f"  Spatial: {results['spatial_avg']}%")
```

---

## ✅ Summary

- **✅ 220 ground truth files available**
- **✅ Standard CASAS ADL format (CSV)**
- **✅ 5 tasks × 24-44 participants**
- **✅ Both error and no-error conditions**
- **✅ Ready for comparison with VESPER-generated data**

### **Next Steps**:

1. **Generate VESPER data**: Run your navigation
2. **Compare**: Use evaluation pipeline
3. **Analyze**: Review accuracy metrics
4. **Iterate**: Improve navigation based on results

**You have a comprehensive ground truth dataset to validate your VESPER system! 🎉**
