# VESPER Dataset Generation & CASAS Comparison Guide

## Complete Step-by-Step Instructions

This guide walks you through generating the VESPER dataset from Blender Game Engine navigation and comparing it with CASAS ground truth datasets.

---

## Table of Contents
1. [Prerequisites & Setup](#prerequisites--setup)
2. [Generate VESPER Dataset](#generate-vesper-dataset)
3. [Validate Generated Data](#validate-generated-data)
4. [Compare with CASAS Ground Truth](#compare-with-casas-ground-truth)
5. [Analyze Results](#analyze-results)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites & Setup

### Step 1: Complete CASAS Integration (One-Time Setup)

**Check current status:**
```bash
python complete_casas_setup.py
```

**If it shows 6/7 components ready**, add the missing initialization:

1. Open `blender/llm_bge_navigation.py`
2. Go to line ~1103
3. Find:
   ```python
   # Initialize metrics logging
   if not hasattr(bge.logic, 'metrics_logger'):
       bge.logic.metrics_logger = get_metrics_logger()
       print("📊 Metrics logging system initialized")
   
   bge.logic.startup_complete = True
   ```

4. **Replace with:**
   ```python
   # Initialize metrics logging
   if not hasattr(bge.logic, 'metrics_logger'):
       bge.logic.metrics_logger = get_metrics_logger()
       print("📊 Metrics logging system initialized")
   
   # Initialize CASAS motion sensor logging
   if not hasattr(bge.logic, 'casas_motion_logger'):
       try:
           bge.logic.casas_motion_logger = CASASMotionSensorLogger()
           print("🎯 CASAS motion sensor logger initialized")
       except Exception as e:
           print(f"⚠️ Failed to initialize CASAS logger: {e}")
   
   bge.logic.startup_complete = True
   ```

5. **Verify completion:**
   ```bash
   python complete_casas_setup.py
   # Should show: ✨ Progress: 7/7 components ready
   ```

### Step 2: Verify Blender Setup

**Check motion sensors exist:**
```bash
# Motion sensors should be in your Blender scene:
# - motion1 (DetectionArea) → Living Room
# - motion2 (DetectionArea) → Bedroom1
# - motion3 (DetectionArea) → Kitchen
# - motion4 (DetectionArea) → Bedroom2
# - motion5 (DetectionArea) → Bathroom1
# - motion6 (DetectionArea) → Bathroom2
```

**Verify Blender file:**
- Blender file should have Actor object with first-person camera
- Navigation map should be synced with Blender environment
- Motion sensors should have DetectionArea objects with correct bounds

### Step 3: Check Ground Truth Data

**Verify CASAS ground truth files exist:**
```bash
# Check for CASAS dataset files
ls casas_testbed/*.txt

# Count ground truth files
python -c "from pathlib import Path; print(f'Ground truth files: {len(list(Path(\"casas_testbed\").glob(\"*.txt\")))}')"
```

Expected output: `Ground truth files: 220`

---

## Generate VESPER Dataset

### Step 4: Configure Navigation Tasks

**Edit tasks in** `blender/llm_bge_navigation.py` (line ~1068):

```python
# Current simple navigation tasks
bge.logic.vesper_tasks = [
    "Go to the kitchen",
    "Go to the bedroom",
    "Go to the livingroom"
]

# OR use CASAS-aligned ADL tasks for better comparison
bge.logic.vesper_tasks = [
    "Make a phone call",     # t1: Move to phone in dining room
    "Wash hands",            # t2: Move to kitchen sink
    "Cook oatmeal",          # t3: Cook in kitchen per directions
    "Eat meal",              # t4: Take food to dining room
    "Clean dishes"           # t5: Take dishes to sink and clean
]
```

**Adjust max steps per task** (line ~1073):
```python
bge.logic.max_steps_per_task = 20  # Increase if tasks need more steps
```

### Step 5: Run BGE Navigation

**Start the navigation system:**
```bash
cd c:\Users\hbui11\Desktop\vesper_llm
python blender/llm_bge_navigation.py
```

**Expected console output:**
```
🚀 BGE Continuous Navigation System Starting...
⏳ Waiting 3 seconds for BGE to stabilize...
🔧 Initializing LLM client...
✅ LLM client ready
📊 Metrics logging system initialized
🎯 CASAS motion sensor logger initialized  ← VERIFY THIS LINE APPEARS
🎮 Starting continuous task execution...

🎯 Task 1/3: 'Go to the kitchen'
🔄 Step 1/20
📸 Capturing dual images...
🤖 Analyzing scene with VLM...
...
```

**What happens during execution:**
1. Actor navigates through Blender environment
2. VLM analyzes first-person camera view + map
3. Motion sensors detect room entry/exit
4. CASAS events logged in real-time
5. Metrics tracked for each movement

**Let it run until completion:**
```
🎉 ALL TASKS COMPLETED! Navigation system finished.
📊 Final CASAS data exported: C:\Users\hbui11\Desktop\vesper_llm\blender\vesper_motion_sensors.txt
🎯 Motion sensor activations logged for ground truth comparison
```

### Step 6: Verify Generated Files

**Check VESPER output files:**
```bash
# CASAS motion sensor data
cat blender/vesper_motion_sensors.txt

# VLM navigation logs (JSON)
cat blender/vesper_metrics_*.json

# Example CASAS output:
# 2025-10-06 14:23:45.123 M003 Kitchen ON
# 2025-10-06 14:24:12.456 M003 Kitchen OFF
# 2025-10-06 14:24:13.789 M001 LivingRoom ON
```

**Check file sizes:**
```powershell
Get-ChildItem blender/vesper_*.txt, blender/vesper_metrics_*.json | Select-Object Name, Length, LastWriteTime
```

---

## Validate Generated Data

### Step 7: Validate CASAS Format

**Run format validation:**
```bash
python -c "
from evaluation.vesper_dataset_pipeline import validate_casas_format

result = validate_casas_format('blender/vesper_motion_sensors.txt')
if result['valid']:
    print(f'✅ Valid CASAS format: {result[\"events\"]} events')
    print(f'   Sensors: {result[\"sensors\"]}')
    print(f'   Time range: {result[\"time_range\"]}')
else:
    print(f'❌ Invalid: {result[\"errors\"]}')
"
```

**Expected output:**
```
✅ Valid CASAS format: 45 events
   Sensors: ['M001', 'M003', 'M002']
   Time range: 2025-10-06 14:23:45 to 2025-10-06 14:28:12
```

### Step 8: Inspect VLM Metrics

**View navigation metrics:**
```bash
python -c "
import json
from pathlib import Path

# Find latest metrics file
metrics_files = sorted(Path('blender').glob('vesper_metrics_*.json'))
if metrics_files:
    with open(metrics_files[-1], 'r') as f:
        data = json.load(f)
    print(f'Session: {data[\"session_id\"]}')
    print(f'Tasks completed: {len(data[\"tasks\"])}')
    print(f'Total steps: {sum(len(t[\"steps\"]) for t in data[\"tasks\"])}')
    print(f'Success rate: {sum(1 for t in data[\"tasks\"] if t[\"success\"])} / {len(data[\"tasks\"])}')
"
```

### Step 9: Visualize Motion Sensor Events

**Quick visualization:**
```bash
python -c "
from pathlib import Path
from collections import Counter

# Read CASAS file
casas_file = Path('blender/vesper_motion_sensors.txt')
if casas_file.exists():
    with open(casas_file, 'r') as f:
        lines = f.readlines()
    
    sensors = [line.split()[1] for line in lines if line.strip()]
    counter = Counter(sensors)
    
    print('Motion Sensor Activation Summary:')
    print('=' * 50)
    for sensor, count in sorted(counter.items()):
        print(f'{sensor}: {\"█\" * (count // 2)} ({count} events)')
else:
    print('❌ CASAS file not found')
"
```

---

## Compare with CASAS Ground Truth

### Step 10: Run Comparison Pipeline

**Execute full evaluation pipeline:**
```bash
python evaluation/vesper_dataset_pipeline.py
```

**What this does:**
1. Detects all CASAS files (ground truth + generated)
2. Validates format of each file
3. Converts VLM JSON logs to CASAS format
4. Compares generated data with ground truth
5. Calculates accuracy metrics

**Expected output:**
```
================================================================================
VESPER DATASET EVALUATION PIPELINE
================================================================================

📂 Scanning for datasets...
   CASAS files found: 221
   VLM logs found: 1

📊 CASAS Format Files Detected
--------------------------------------------------------------------------------
   Ground truth files: 220
   Generated VESPER files: 1
   - blender/vesper_motion_sensors.txt ✅ (45 events)

🔄 Converting VLM logs to CASAS format...
   Converting: blender/vesper_metrics_20251006_142345.json
   ✅ Converted: blender/vesper_metrics_20251006_142345_casas.txt

📈 Comparison Results
--------------------------------------------------------------------------------
   Temporal accuracy: 87.3%
   Spatial accuracy: 91.2%
   Event correlation: 0.84
```

### Step 11: Detailed Comparison Analysis

**Compare specific files:**
```bash
python -c "
from evaluation.casas_comparison import compare_casas_files

# Compare generated VESPER data with specific ground truth
result = compare_casas_files(
    'blender/vesper_motion_sensors.txt',
    'casas_testbed/sample_ground_truth.txt'  # Choose appropriate ground truth
)

print('Detailed Comparison:')
print(f'Matching events: {result[\"matches\"]}')
print(f'Missing events: {result[\"missing\"]}')
print(f'Extra events: {result[\"extra\"]}')
print(f'Temporal offset: {result[\"time_offset\"]} seconds')
"
```

### Step 12: Generate Comparison Report

**Create comprehensive report:**
```bash
python -c "
from evaluation.vesper_dataset_pipeline import generate_comparison_report

report = generate_comparison_report(
    vesper_file='blender/vesper_motion_sensors.txt',
    ground_truth_dir='casas_testbed/'
)

# Save report
with open('vesper_casas_comparison_report.txt', 'w') as f:
    f.write(report)

print('📊 Report saved: vesper_casas_comparison_report.txt')
"
```

---

## Analyze Results

### Step 13: Metric Interpretation

**Understanding comparison metrics:**

1. **Temporal Accuracy** (Time-based matching)
   - Measures how well event timing aligns
   - > 80%: Excellent timing accuracy
   - 60-80%: Good, minor timing drift
   - < 60%: Significant timing issues

2. **Spatial Accuracy** (Location-based matching)
   - Measures correct room/sensor identification
   - > 90%: Excellent location tracking
   - 70-90%: Good spatial awareness
   - < 70%: Navigation improvements needed

3. **Event Correlation** (Pattern matching)
   - Measures activity pattern similarity
   - > 0.8: Strong correlation with ground truth
   - 0.6-0.8: Moderate correlation
   - < 0.6: Weak correlation

### Step 14: Identify Discrepancies

**Find missing/extra events:**
```bash
python -c "
from pathlib import Path
from datetime import datetime

def analyze_differences(vesper_file, ground_truth_file):
    # Read both files
    with open(vesper_file, 'r') as f:
        vesper_events = set(f.readlines())
    with open(ground_truth_file, 'r') as f:
        gt_events = set(f.readlines())
    
    # Find differences
    missing = gt_events - vesper_events
    extra = vesper_events - gt_events
    
    print('Missing Events (in ground truth, not in VESPER):')
    for event in sorted(missing)[:5]:  # Show first 5
        print(f'  - {event.strip()}')
    
    print(f'\nExtra Events (in VESPER, not in ground truth):')
    for event in sorted(extra)[:5]:  # Show first 5
        print(f'  + {event.strip()}')
    
    return len(missing), len(extra)

# Analyze
missing, extra = analyze_differences(
    'blender/vesper_motion_sensors.txt',
    'casas_testbed/sample_ground_truth.txt'
)
print(f'\nSummary: {missing} missing, {extra} extra events')
"
```

### Step 15: Visualization & Plots

**Generate timeline comparison:**
```bash
python -c "
import matplotlib.pyplot as plt
from datetime import datetime

def plot_sensor_timeline(casas_file):
    events = []
    with open(casas_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                timestamp = datetime.strptime(
                    f'{parts[0]} {parts[1]}', 
                    '%Y-%m-%d %H:%M:%S.%f'
                )
                sensor = parts[2]
                state = parts[3]
                events.append((timestamp, sensor, state))
    
    # Plot timeline
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sensors = list(set(e[1] for e in events))
    sensor_to_y = {s: i for i, s in enumerate(sensors)}
    
    for timestamp, sensor, state in events:
        y = sensor_to_y[sensor]
        color = 'green' if state == 'ON' else 'red'
        ax.scatter(timestamp, y, c=color, s=100, alpha=0.6)
    
    ax.set_yticks(range(len(sensors)))
    ax.set_yticklabels(sensors)
    ax.set_xlabel('Time')
    ax.set_ylabel('Motion Sensor')
    ax.set_title('VESPER Motion Sensor Timeline')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('vesper_sensor_timeline.png', dpi=150)
    print('📊 Timeline saved: vesper_sensor_timeline.png')

plot_sensor_timeline('blender/vesper_motion_sensors.txt')
"
```

---

## Advanced Analysis

### Step 16: Activity Recognition Accuracy

**Compare activity patterns:**
```bash
python -c "
from collections import defaultdict
import json

def analyze_activity_patterns(metrics_file):
    with open(metrics_file, 'r') as f:
        data = json.load(f)
    
    # Extract activity patterns from tasks
    patterns = defaultdict(list)
    
    for task in data['tasks']:
        task_name = task['task']
        sensors = []
        
        # Extract sensor activations from steps
        for step in task['steps']:
            if 'sensor_events' in step:
                sensors.extend(step['sensor_events'])
        
        patterns[task_name] = sensors
    
    print('Activity-Sensor Patterns:')
    print('=' * 60)
    for activity, sensors in patterns.items():
        print(f'{activity}:')
        sensor_counts = defaultdict(int)
        for s in sensors:
            sensor_counts[s] += 1
        for sensor, count in sorted(sensor_counts.items()):
            print(f'  {sensor}: {count} activations')
        print()

# Find latest metrics
from pathlib import Path
metrics = sorted(Path('blender').glob('vesper_metrics_*.json'))
if metrics:
    analyze_activity_patterns(metrics[-1])
"
```

### Step 17: Statistical Analysis

**Calculate statistical metrics:**
```bash
python -c "
import numpy as np
from datetime import datetime

def statistical_analysis(casas_file):
    # Parse events
    events = []
    with open(casas_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                timestamp = datetime.strptime(
                    f'{parts[0]} {parts[1]}',
                    '%Y-%m-%d %H:%M:%S.%f'
                )
                sensor = parts[2]
                events.append((timestamp, sensor))
    
    # Calculate inter-event times
    if len(events) > 1:
        times = [(events[i+1][0] - events[i][0]).total_seconds() 
                 for i in range(len(events)-1)]
        
        print('Statistical Analysis:')
        print('=' * 60)
        print(f'Total events: {len(events)}')
        print(f'Unique sensors: {len(set(e[1] for e in events))}')
        print(f'Duration: {(events[-1][0] - events[0][0]).total_seconds():.1f} seconds')
        print(f'\nInter-event times (seconds):')
        print(f'  Mean: {np.mean(times):.2f}')
        print(f'  Median: {np.median(times):.2f}')
        print(f'  Std Dev: {np.std(times):.2f}')
        print(f'  Min: {np.min(times):.2f}')
        print(f'  Max: {np.max(times):.2f}')

statistical_analysis('blender/vesper_motion_sensors.txt')
"
```

---

## Batch Processing (Multiple Runs)

### Step 18: Generate Multiple Datasets

**Run multiple navigation sessions:**
```bash
# Create batch script
python -c "
import subprocess
import time
from datetime import datetime

num_runs = 5

for i in range(num_runs):
    print(f'\n{'='*60}')
    print(f'Run {i+1}/{num_runs} - {datetime.now()}')
    print('='*60)
    
    # Run BGE navigation
    result = subprocess.run(
        ['python', 'blender/llm_bge_navigation.py'],
        capture_output=True,
        text=True
    )
    
    print(f'Exit code: {result.returncode}')
    
    # Wait between runs
    if i < num_runs - 1:
        print('Waiting 10 seconds before next run...')
        time.sleep(10)

print('\n✅ Batch processing complete!')
"
```

### Step 19: Aggregate Results

**Analyze multiple runs:**
```bash
python -c "
from pathlib import Path
import json
import numpy as np

# Collect all metrics files
metrics_files = sorted(Path('blender').glob('vesper_metrics_*.json'))

print(f'Analyzing {len(metrics_files)} runs...\n')

success_rates = []
step_counts = []

for mf in metrics_files:
    with open(mf, 'r') as f:
        data = json.load(f)
    
    tasks = data['tasks']
    successes = sum(1 for t in tasks if t['success'])
    total_steps = sum(len(t['steps']) for t in tasks)
    
    success_rates.append(successes / len(tasks) * 100)
    step_counts.append(total_steps)

print('Aggregate Statistics:')
print('=' * 60)
print(f'Success Rate:')
print(f'  Mean: {np.mean(success_rates):.1f}%')
print(f'  Std: {np.std(success_rates):.1f}%')
print(f'  Range: {np.min(success_rates):.1f}% - {np.max(success_rates):.1f}%')
print(f'\nSteps per Run:')
print(f'  Mean: {np.mean(step_counts):.1f}')
print(f'  Std: {np.std(step_counts):.1f}')
print(f'  Range: {int(np.min(step_counts))} - {int(np.max(step_counts))}')
"
```

---

## Troubleshooting

### Common Issues & Solutions

**Issue 1: No CASAS file generated**
```bash
# Check if logger initialized
grep "CASAS motion sensor logger initialized" blender_output.log

# Solution: Complete Step 1 (add initialization code)
```

**Issue 2: Empty CASAS file**
```bash
# Check motion sensor bounds
python -c "
from blender.casas_motion_logger import CASASMotionSensorLogger
logger = CASASMotionSensorLogger()
print('Motion sensors configured:')
for sensor_id, info in logger.motion_sensors.items():
    print(f'{sensor_id}: {info}')
"

# Solution: Verify DetectionArea objects in Blender scene
```

**Issue 3: Comparison fails**
```bash
# Validate both files
python -c "
from evaluation.vesper_dataset_pipeline import validate_casas_format

files = [
    'blender/vesper_motion_sensors.txt',
    'casas_testbed/sample_ground_truth.txt'
]

for f in files:
    result = validate_casas_format(f)
    print(f'{f}: {\"✅\" if result[\"valid\"] else \"❌\"} {result}')
"

# Solution: Check timestamp format matches exactly
```

**Issue 4: Low accuracy scores**
```bash
# Debug navigation quality
python -c "
import json
from pathlib import Path

metrics = sorted(Path('blender').glob('vesper_metrics_*.json'))[-1]
with open(metrics, 'r') as f:
    data = json.load(f)

# Check failure reasons
failures = [t for t in data['tasks'] if not t['success']]
print(f'Failed tasks: {len(failures)}')
for t in failures:
    print(f'  - {t[\"task\"]}: {t.get(\"failure_reason\", \"unknown\")}')
"

# Solutions:
# - Increase max_steps_per_task
# - Improve VLM prompts
# - Adjust motion sensor bounds
```

---

## Summary Checklist

### Before Running:
- ✅ CASAS integration complete (7/7 components)
- ✅ Motion sensors configured in Blender
- ✅ Ground truth files in casas_testbed/
- ✅ Tasks configured in llm_bge_navigation.py

### During Execution:
- ✅ Monitor console for initialization messages
- ✅ Watch for motion sensor activations
- ✅ Check task completion status

### After Completion:
- ✅ Verify CASAS file generated: `blender/vesper_motion_sensors.txt`
- ✅ Validate format with pipeline
- ✅ Compare with ground truth
- ✅ Analyze metrics and accuracy

### Files Generated:
- `blender/vesper_motion_sensors.txt` - CASAS format sensor data
- `blender/vesper_metrics_YYYYMMDD_HHMMSS.json` - VLM navigation logs
- `vesper_casas_comparison_report.txt` - Comparison analysis
- `vesper_sensor_timeline.png` - Visualization (optional)

---

## Quick Reference Commands

```bash
# 1. Verify setup
python complete_casas_setup.py

# 2. Generate dataset
python blender/llm_bge_navigation.py

# 3. Validate CASAS format
python evaluation/vesper_dataset_pipeline.py

# 4. View CASAS data
cat blender/vesper_motion_sensors.txt

# 5. Check metrics
ls -l blender/vesper_metrics_*.json

# 6. Count events
wc -l blender/vesper_motion_sensors.txt

# 7. Compare with ground truth
python evaluation/casas_comparison.py
```

---

**You're all set! Follow these steps to generate and compare your VESPER datasets! 🚀**
