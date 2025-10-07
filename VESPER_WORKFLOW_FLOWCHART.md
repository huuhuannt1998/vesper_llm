# VESPER Dataset Generation Flowchart

## Complete Process from Setup to Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     VESPER DATASET WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║                         PHASE 1: SETUP (One-Time)                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────┐
    │  Verify Setup       │
    │  Status             │──────┐
    └─────────────────────┘      │
                                  ▼
    ┌──────────────────────────────────────────┐
    │ Run: python complete_casas_setup.py      │
    └──────────────────────────────────────────┘
                    │
                    ▼
    ┌─────────────────────────────────────────────┐
    │ Status: 6/7 or 7/7 components?              │
    └─────────────────────────────────────────────┘
           │                              │
           │ 6/7                          │ 7/7
           ▼                              ▼
    ┌─────────────────────┐      ┌──────────────────┐
    │ Add Manual Setup    │      │ Setup Complete!  │
    │ (1 initialization)  │      │ Ready to Run     │
    └─────────────────────┘      └──────────────────┘
           │                              │
           └──────────────┬───────────────┘
                          ▼
    ┌────────────────────────────────────────────┐
    │ Components Ready:                          │
    │ ✅ casas_motion_logger.py                 │
    │ ✅ llm_bge_navigation.py (with imports)   │
    │ ✅ Motion sensor tracking                 │
    │ ✅ CASAS logger initialization            │
    │ ✅ Export on task completion              │
    │ ✅ Evaluation pipeline                    │
    └────────────────────────────────────────────┘
                          │
                          ▼

╔═══════════════════════════════════════════════════════════════════════════╗
║                      PHASE 2: DATASET GENERATION                          ║
╚═══════════════════════════════════════════════════════════════════════════╝

    ┌────────────────────────────────────────────┐
    │ Configure Tasks (Optional)                 │
    │ Edit: blender/llm_bge_navigation.py        │
    │ Line ~1068: bge.logic.vesper_tasks         │
    └────────────────────────────────────────────┘
                          │
                          ▼
    ┌────────────────────────────────────────────┐
    │ START NAVIGATION                           │
    │ python blender/llm_bge_navigation.py       │
    └────────────────────────────────────────────┘
                          │
                          ▼
    ┌────────────────────────────────────────────┐
    │ BGE Initialization                         │
    │ • Load Blender scene                       │
    │ • Initialize LLM client                    │
    │ • Setup metrics logger                     │
    │ • Initialize CASAS logger ← VERIFY THIS    │
    └────────────────────────────────────────────┘
                          │
                          ▼
    ┌────────────────────────────────────────────┐
    │ Task Execution Loop                        │
    │ For each task in vesper_tasks:             │
    └────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────┐
    │ Navigation Step                         │
    │ 1. Capture FP camera + map              │
    │ 2. VLM analyzes scene                   │
    │ 3. Generate movement command            │
    │ 4. Execute movement                     │
    │ 5. Check motion sensors ← TRACKING      │
    │ 6. Log to CASAS file                    │
    └─────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────┐
    │ Task Complete?                          │
    └─────────────────────────────────────────┘
           │                    │
           │ No                 │ Yes
           │ (More steps)       ▼
           │            ┌──────────────────────┐
           │            │ Export CASAS Data    │
           │            │ Task metrics saved   │
           │            └──────────────────────┘
           │                    │
           └────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────┐
    │ All Tasks Complete?                     │
    └─────────────────────────────────────────┘
           │                    │
           │ No                 │ Yes
           │ (Next task)        ▼
           │            ┌──────────────────────────┐
           │            │ Final CASAS Export       │
           │            │ Session complete         │
           │            └──────────────────────────┘
           │                    │
           └────────────────────┘
                          │
                          ▼
    ┌────────────────────────────────────────────┐
    │ OUTPUT FILES GENERATED:                    │
    │ 📄 vesper_motion_sensors.txt              │
    │    (CASAS format motion sensor logs)       │
    │ 📄 vesper_metrics_YYYYMMDD.json           │
    │    (VLM navigation metrics)                │
    └────────────────────────────────────────────┘
                          │
                          ▼

╔═══════════════════════════════════════════════════════════════════════════╗
║                        PHASE 3: DATA VALIDATION                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

    ┌────────────────────────────────────────────┐
    │ Verify Files Exist                         │
    └────────────────────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────────────┐
    │ Check CASAS Format                         │
    │ • Timestamp format: YYYY-MM-DD HH:MM:SS.mmm│
    │ • Sensor IDs: M001-M006                    │
    │ • States: ON/OFF                           │
    └────────────────────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────────────┐
    │ Quick Validation                           │
    │ python -c "validate_casas_format(...)"     │
    └────────────────────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────────────┐
    │ Validation Results                         │
    │ ✅ Valid: Events, sensors, time range     │
    │ ❌ Invalid: Error messages                │
    └────────────────────────────────────────────┘
           │
           ▼

╔═══════════════════════════════════════════════════════════════════════════╗
║                    PHASE 4: COMPARISON WITH GROUND TRUTH                  ║
╚═══════════════════════════════════════════════════════════════════════════╝

    ┌────────────────────────────────────────────┐
    │ Run Evaluation Pipeline                    │
    │ python evaluation/vesper_dataset_pipeline.py│
    └────────────────────────────────────────────┘
           │
           ▼
    ┌────────────────────────────────────────────┐
    │ Pipeline Steps:                            │
    └────────────────────────────────────────────┘
           │
           ├─► ┌──────────────────────────────┐
           │   │ 1. Scan for Files           │
           │   │ • Ground truth (casas_testbed/)│
           │   │ • Generated (blender/)      │
           │   └──────────────────────────────┘
           │
           ├─► ┌──────────────────────────────┐
           │   │ 2. Validate Formats         │
           │   │ • Check each file           │
           │   │ • Report errors             │
           │   └──────────────────────────────┘
           │
           ├─► ┌──────────────────────────────┐
           │   │ 3. Convert VLM to CASAS     │
           │   │ • JSON → CASAS format       │
           │   │ • Align timestamps          │
           │   └──────────────────────────────┘
           │
           ├─► ┌──────────────────────────────┐
           │   │ 4. Compare Datasets         │
           │   │ • Event matching            │
           │   │ • Timing analysis           │
           │   │ • Location correlation      │
           │   └──────────────────────────────┘
           │
           └─► ┌──────────────────────────────┐
               │ 5. Generate Metrics         │
               │ • Temporal accuracy         │
               │ • Spatial accuracy          │
               │ • Event correlation         │
               └──────────────────────────────┘
                          │
                          ▼
    ┌────────────────────────────────────────────┐
    │ COMPARISON RESULTS:                        │
    │ 📊 Temporal Accuracy: XX%                 │
    │ 📊 Spatial Accuracy: XX%                  │
    │ 📊 Event Correlation: X.XX                │
    │ 📊 Missing Events: XX                     │
    │ 📊 Extra Events: XX                       │
    └────────────────────────────────────────────┘
                          │
                          ▼

╔═══════════════════════════════════════════════════════════════════════════╗
║                        PHASE 5: ANALYSIS & ITERATION                      ║
╚═══════════════════════════════════════════════════════════════════════════╝

    ┌────────────────────────────────────────────┐
    │ Analyze Results                            │
    └────────────────────────────────────────────┘
           │
           ├─► ┌──────────────────────────────┐
           │   │ Statistical Analysis        │
           │   │ • Event frequency           │
           │   │ • Sensor patterns           │
           │   │ • Timing distributions      │
           │   └──────────────────────────────┘
           │
           ├─► ┌──────────────────────────────┐
           │   │ Visualizations              │
           │   │ • Timeline plots            │
           │   │ • Sensor heatmaps           │
           │   │ • Activity patterns         │
           │   └──────────────────────────────┘
           │
           └─► ┌──────────────────────────────┐
               │ Identify Issues             │
               │ • Low accuracy areas        │
               │ • Timing drifts             │
               │ • Missing sensors           │
               └──────────────────────────────┘
                          │
                          ▼
    ┌────────────────────────────────────────────┐
    │ Improvement Actions                        │
    └────────────────────────────────────────────┘
           │
           ├─► Adjust motion sensor bounds
           ├─► Increase max_steps_per_task
           ├─► Refine VLM prompts
           ├─► Fine-tune navigation logic
           │
           └─► ┌──────────────────────────────┐
               │ Re-run Generation            │
               │ (Return to Phase 2)          │
               └──────────────────────────────┘

```

## Key Files & Their Roles

### Generation Phase
```
blender/llm_bge_navigation.py
    ↓ (imports)
blender/casas_motion_logger.py
    ↓ (tracks sensors)
blender/vesper_motion_sensors.txt          ← OUTPUT: CASAS format
blender/vesper_metrics_YYYYMMDD.json       ← OUTPUT: VLM logs
```

### Comparison Phase
```
evaluation/vesper_dataset_pipeline.py
    ↓ (orchestrates)
evaluation/vlm_to_casas_converter.py
    ↓ (converts)
evaluation/casas_comparison.py
    ↓ (compares)
casas_testbed/*.txt                         ← INPUT: Ground truth
comparison_results/                         ← OUTPUT: Analysis
```

## Data Flow

```
┌─────────────┐
│   Blender   │
│   Scene     │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────┐
│   Actor     │─────>│ First-Person │
│   Movement  │      │   Camera     │
└──────┬──────┘      └──────┬───────┘
       │                    │
       ▼                    ▼
┌─────────────┐      ┌──────────────┐
│   Motion    │      │     VLM      │
│   Sensors   │      │   Analysis   │
└──────┬──────┘      └──────┬───────┘
       │                    │
       ├────────────────────┤
       │
       ▼
┌─────────────────────────────┐
│  CASAS Motion Sensor Logger │
│  • Detects room entry       │
│  • Timestamps events        │
│  • Formats CASAS output     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  vesper_motion_sensors.txt  │
│                             │
│  2025-10-06 14:23:45.123    │
│  M003 Kitchen ON            │
│  2025-10-06 14:24:12.456    │
│  M003 Kitchen OFF           │
│  2025-10-06 14:24:13.789    │
│  M001 LivingRoom ON         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Evaluation Pipeline        │
│  • Validate format          │
│  • Compare with GT          │
│  • Calculate metrics        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Comparison Results         │
│  • Accuracy scores          │
│  • Discrepancy analysis     │
│  • Recommendations          │
└─────────────────────────────┘
```

## Quick Command Reference

### Setup
```bash
# Verify setup status
python complete_casas_setup.py

# Quick start guide
python quick_start_vesper_dataset.py
```

### Generation
```bash
# Generate dataset
python blender/llm_bge_navigation.py

# Check output
cat blender/vesper_motion_sensors.txt
ls blender/vesper_metrics_*.json
```

### Validation
```bash
# Count events
wc -l blender/vesper_motion_sensors.txt          # Linux/Mac
Get-Content ... | Measure-Object -Line           # Windows

# View sample
head -20 blender/vesper_motion_sensors.txt       # Linux/Mac
Get-Content ... -TotalCount 20                   # Windows
```

### Comparison
```bash
# Run full pipeline
python evaluation/vesper_dataset_pipeline.py

# Quick sensor summary
python -c "
from collections import Counter
with open('blender/vesper_motion_sensors.txt', 'r') as f:
    sensors = [line.split()[2] for line in f if line.strip()]
print(Counter(sensors))
"
```

### Analysis
```bash
# View metrics
python -c "
import json
from pathlib import Path
metrics = sorted(Path('blender').glob('vesper_metrics_*.json'))[-1]
with open(metrics, 'r') as f:
    data = json.load(f)
print(f'Tasks: {len(data[\"tasks\"])}')
print(f'Success: {sum(1 for t in data[\"tasks\"] if t[\"success\"])}')
"
```

## Success Criteria

### ✅ Setup Complete When:
- [x] complete_casas_setup.py shows 7/7
- [x] Motion sensors configured
- [x] Ground truth data available

### ✅ Generation Successful When:
- [x] vesper_motion_sensors.txt created
- [x] File contains CASAS-format events
- [x] vesper_metrics_*.json exists
- [x] Console shows "CASAS motion sensor logger initialized"

### ✅ Validation Passed When:
- [x] All timestamps valid
- [x] Sensor IDs in M001-M006 range
- [x] States are ON/OFF
- [x] Events chronologically ordered

### ✅ Comparison Meaningful When:
- [x] Temporal accuracy > 70%
- [x] Spatial accuracy > 80%
- [x] Event correlation > 0.6
- [x] Similar event counts

## Troubleshooting Decision Tree

```
Generated CASAS file?
├─ No
│  ├─ Logger initialized? → Check Step 1 setup
│  ├─ Tasks completed? → Increase max_steps
│  └─ Errors in console? → Debug motion sensors
│
└─ Yes
   ├─ Valid format?
   │  ├─ No → Check timestamp/sensor format
   │  └─ Yes → Proceed to comparison
   │
   └─ Low accuracy?
      ├─ < 50% → Check sensor bounds
      ├─ 50-70% → Adjust navigation
      └─ > 70% → Fine-tune & iterate
```

---

**Follow this flowchart to successfully generate and compare VESPER datasets! 🚀**
