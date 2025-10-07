# VESPER Production Workflow

## 🎯 **Clean, Production-Ready Pipeline**

This document describes the streamlined production workflow for generating and comparing VESPER datasets.

---

## 📁 **File Structure**

```
vesper_llm/
├── blender/
│   ├── llm_bge_navigation.py           ← Main BGE navigation system
│   └── casas_motion_logger.py          ← Motion sensor tracking
│
├── casas_testbed/
│   ├── vesper_datasets/                ← PRODUCTION OUTPUT (all datasets here)
│   │   ├── vesper_casas_p01_YYYYMMDD_HHMMSS.txt    ← Motion sensor data
│   │   └── vesper_metrics_p01_YYYYMMDD_HHMMSS.json ← VLM metrics
│   │
│   └── data/
│       ├── casas_ground_truth/         ← Ground truth datasets
│       │   ├── adl_noerror/            (120 CSV files)
│       │   └── adl_error/              (100 CSV files)
│       │
│       └── comparison_results/         ← Analysis outputs
│           ├── vesper_comparison_report_*.md
│           └── pipeline_results_*.json
│
└── evaluation/
    └── vesper_dataset_pipeline.py      ← Comparison pipeline
```

---

## 🔄 **Production Workflow**

### **Step 1: Generate VESPER Dataset**

Run Blender Game Engine navigation:

```bash
python blender/llm_bge_navigation.py
```

**What happens:**
1. BGE initializes with CASAS motion sensor logger
2. Actor navigates through environment
3. Real-time motion sensor tracking
4. Datasets exported to `casas_testbed/vesper_datasets/`

**Expected output:**
```
🎯 CASAS motion sensor logger initialized
🎮 Starting continuous task execution...

📡 Motion Sensor: motion1 (M001) Living_Room ON
📡 Motion Sensor: motion3 (M003) Kitchen ON

🎉 ALL TASKS COMPLETED!
✅ CASAS: vesper_casas_p01_20251006_143022.txt
✅ Metrics: vesper_metrics_p01_20251006_143022.json
📁 Location: C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\vesper_datasets
```

---

### **Step 2: Analyze and Compare**

Run evaluation pipeline:

```bash
python evaluation/vesper_dataset_pipeline.py
```

**What happens:**
1. Detects datasets in `casas_testbed/vesper_datasets/`
2. Validates CASAS format
3. Compares with ground truth (220 CSV files)
4. Generates comparison report
5. Saves results to `casas_testbed/data/comparison_results/`

**Expected output:**
```
================================================================================
DETECTING VESPER DATASETS
================================================================================

📊 Found 1 CASAS sensor files
   - vesper_casas_p01_20251006_143022.txt

📊 Found 1 VLM metrics files
   - vesper_metrics_p01_20251006_143022.json

================================================================================
VALIDATING CASAS FORMAT
================================================================================

✅ vesper_casas_p01_20251006_143022.txt
   Events: 45
   Sensors: M001, M003, M002

================================================================================
COMPARING: vesper_casas_p01_20251006_143022.txt
================================================================================

📊 VESPER dataset: 45 sensor events
   Sensor activations:
     M001: 12 events
     M003: 18 events
     M002: 15 events

🔍 Scanning ground truth datasets...
   Found 220 ground truth files

📈 Comparing with ground truth samples...
   p01.t1.csv: 75.0% match
   p01.t2.csv: 82.3% match
   p01.t3.csv: 68.5% match

================================================================================
PIPELINE COMPLETED SUCCESSFULLY
================================================================================
```

---

## 📊 **Output Files**

### **After BGE Navigation:**

#### `vesper_casas_p01_YYYYMMDD_HHMMSS.txt`
CASAS-format motion sensor events:
```
2024-10-06 14:30:22.446 M001 Living_Room ON
2024-10-06 14:30:25.831 M001 Living_Room OFF
2024-10-06 14:30:26.123 M003 Kitchen ON
```

#### `vesper_metrics_p01_YYYYMMDD_HHMMSS.json`
VLM navigation metrics:
```json
{
  "session_id": "20251006_143022",
  "tasks_completed": 3,
  "total_steps": 15,
  "task_details": [...]
}
```

### **After Pipeline Analysis:**

#### `vesper_comparison_report_YYYYMMDD_HHMMSS.md`
Markdown report with:
- Dataset overview
- Sensor distribution
- Ground truth comparison results
- Recommendations

#### `pipeline_results_YYYYMMDD_HHMMSS.json`
JSON with complete pipeline results

---

## 🎯 **Key Features**

### **Removed (Old System)**
- ❌ `blender/evaluation_logs/` - No longer used
- ❌ Manual CASAS conversion scripts
- ❌ Separate conversion step
- ❌ Multiple output locations

### **Added (Production)**
- ✅ Direct export to `casas_testbed/vesper_datasets/`
- ✅ Real-time CASAS logging during navigation
- ✅ Automatic dataset export on completion
- ✅ Single production folder for all outputs
- ✅ Streamlined 2-step workflow

---

## 🔧 **Verification**

Check setup status:

```bash
python complete_casas_setup.py
```

Expected output:
```
✨ Progress: 7/7 components ready

📁 PRODUCTION DATASET OUTPUT
Found 2 dataset files in: casas_testbed\vesper_datasets
   - vesper_casas_p01_20251006_143022.txt (CASAS sensors)
   - vesper_metrics_p01_20251006_143022.json (VLM metrics)

✅ Found 220 CASAS ground truth files
   Location: casas_testbed\data\casas_ground_truth
```

---

## 📈 **Quick Commands**

```bash
# 1. Verify setup
python complete_casas_setup.py

# 2. Generate dataset
python blender/llm_bge_navigation.py

# 3. Check generated files
ls casas_testbed/vesper_datasets/

# 4. Run comparison
python evaluation/vesper_dataset_pipeline.py

# 5. View results
ls casas_testbed/data/comparison_results/
```

---

## 🎓 **Research Workflow**

### **Single Run:**
1. Configure tasks in `llm_bge_navigation.py`
2. Run BGE navigation
3. Run pipeline analysis
4. Review comparison report

### **Multiple Runs:**
```bash
# Run navigation multiple times
for i in {1..5}; do
    python blender/llm_bge_navigation.py
    sleep 10
done

# Analyze all generated datasets
python evaluation/vesper_dataset_pipeline.py
```

### **Batch Analysis:**
- Pipeline automatically detects all files in `vesper_datasets/`
- Compares each with ground truth
- Generates aggregate statistics

---

## 📂 **Data Management**

### **Dataset Naming Convention:**
- CASAS sensors: `vesper_casas_p01_YYYYMMDD_HHMMSS.txt`
- VLM metrics: `vesper_metrics_p01_YYYYMMDD_HHMMSS.json`
- `p01` = participant ID (can be changed for multi-user studies)
- Timestamp = Session identifier

### **Archiving:**
```bash
# Archive old datasets
mkdir casas_testbed/vesper_datasets/archive
mv casas_testbed/vesper_datasets/vesper_*.txt casas_testbed/vesper_datasets/archive/
mv casas_testbed/vesper_datasets/vesper_*.json casas_testbed/vesper_datasets/archive/
```

### **Cleanup:**
```bash
# Remove old comparison results
rm casas_testbed/data/comparison_results/*.md
rm casas_testbed/data/comparison_results/*.json
```

---

## ✅ **Summary**

**Production Workflow = 2 Simple Steps:**

1. **Generate**: `python blender/llm_bge_navigation.py`
   - Outputs to `casas_testbed/vesper_datasets/`

2. **Analyze**: `python evaluation/vesper_dataset_pipeline.py`
   - Reads from `casas_testbed/vesper_datasets/`
   - Compares with `casas_testbed/data/casas_ground_truth/`
   - Saves results to `casas_testbed/data/comparison_results/`

**Clean. Simple. Production-ready.** 🚀
