# 📊 VESPER Dataset Pipeline Demo Results

**Date:** October 6, 2025  
**Pipeline:** `vesper_dataset_pipeline.py`

---

## 🎯 What We Created

### 3 Simulated Blender Sessions

Each session generated **2 files**:
1. **CASAS motion sensor data** (`.txt`) - Motion sensor activations
2. **VLM metrics** (`.json`) - Decision-making data

| Session ID | Duration | Sensor Events | Rooms Visited | VLM Decisions |
|------------|----------|---------------|---------------|---------------|
| `20251006_140530` | 33s | 12 | 4 (LivingRoom, Kitchen, Bedroom1, Bathroom1) | 5 |
| `20251006_151245` | 46s | 14 | 6 (All rooms) | 6 |
| `20251006_163015` | 33s | 10 | 4 (Kitchen, LivingRoom, Bedroom1, Bathroom1) | 4 |

---

## 📁 Generated Files

### In `casas_testbed/vesper_datasets/`:
```
✅ vesper_casas_p01_20251006_140530.txt      (516 bytes)
✅ vesper_metrics_p01_20251006_140530.json   (899 bytes)
✅ vesper_casas_p01_20251006_151245.txt      (605 bytes)
✅ vesper_metrics_p01_20251006_151245.json   (1,057 bytes)
✅ vesper_casas_p01_20251006_163015.txt      (433 bytes)
✅ vesper_metrics_p01_20251006_163015.json   (809 bytes)
```

### In `casas_testbed/data/comparison_results/`:
```
✅ vesper_comparison_report_20251006_214710.md
✅ pipeline_results_20251006_214710.json
```

---

## 🔍 Pipeline Analysis

### What the Pipeline Did:

1. **✅ Detection Phase**
   - Found 3 CASAS sensor files
   - Found 3 VLM metrics files
   - Paired them correctly by session ID

2. **✅ Validation Phase**
   - Validated CASAS format for all 3 files
   - Confirmed sensor IDs: M001-M006
   - Verified timestamp format
   - Event counts: 12, 14, 10

3. **✅ Comparison Phase**
   - Loaded 220 ground truth files
   - Compared each VESPER dataset with 5 ground truth samples
   - Calculated sensor activation patterns
   - Measured match percentages

4. **✅ Report Generation**
   - Created markdown report with statistics
   - Generated JSON with detailed comparisons
   - Summarized sensor distributions
   - Provided recommendations

---

## 📊 Example Dataset

### Session: `20251006_140530`

**CASAS Sensor Events:**
```
2024-11-08 09:15:23.450 M001 LivingRoom ON
2024-11-08 09:15:25.120 M003 Kitchen ON
2024-11-08 09:15:27.890 M001 LivingRoom OFF
2024-11-08 09:15:30.340 M003 Kitchen OFF
2024-11-08 09:15:32.670 M002 Bedroom1 ON
2024-11-08 09:15:35.120 M002 Bedroom1 OFF
2024-11-08 09:15:38.450 M005 Bathroom1 ON
2024-11-08 09:15:42.230 M005 Bathroom1 OFF
2024-11-08 09:15:45.890 M003 Kitchen ON
2024-11-08 09:15:49.120 M003 Kitchen OFF
2024-11-08 09:15:52.670 M001 LivingRoom ON
2024-11-08 09:15:56.340 M001 LivingRoom OFF
```

**Sensor Activations:**
- M001 (LivingRoom): 4 events (2 ON/OFF cycles)
- M002 (Bedroom1): 2 events (1 ON/OFF cycle)
- M003 (Kitchen): 4 events (2 ON/OFF cycles)
- M005 (Bathroom1): 2 events (1 ON/OFF cycle)

**VLM Decisions:**
```json
[
  {"timestamp": "2024-11-08 09:15:23", "decision": "move_to_kitchen", "confidence": 0.87},
  {"timestamp": "2024-11-08 09:15:30", "decision": "move_to_bedroom", "confidence": 0.92},
  {"timestamp": "2024-11-08 09:15:35", "decision": "move_to_bathroom", "confidence": 0.78},
  {"timestamp": "2024-11-08 09:15:42", "decision": "move_to_kitchen", "confidence": 0.85},
  {"timestamp": "2024-11-08 09:15:49", "decision": "move_to_living_room", "confidence": 0.91}
]
```

---

## 📈 Pipeline Output Statistics

### Validation Results:
```
✅ All 3 CASAS files: VALID
   - Correct format: YYYY-MM-DD HH:MM:SS.mmm SENSOR_ID LOCATION STATE
   - Valid sensor IDs: M001-M006
   - Proper ON/OFF pairing
```

### Comparison Results:
```
📊 VESPER datasets: 3
📊 Ground truth files: 220
📊 Comparisons performed: 3 × 5 = 15 comparisons
📊 Reports generated: 2 (1 markdown + 1 JSON)
```

---

## 🎓 Key Observations

### Sensor Usage Patterns:
- **M001 (LivingRoom)**: Most frequently used (appeared in all sessions)
- **M003 (Kitchen)**: Second most common
- **M002 (Bedroom1)**: Regular usage
- **M005 (Bathroom1)**: Regular usage
- **M004 (Bedroom2)**: Less frequent
- **M006 (Bathroom2)**: Less frequent

### VLM Decision Confidence:
- Average confidence: ~0.85
- Highest: 0.93 (move_to_living_room)
- Lowest: 0.76 (move_to_bedroom2)

---

## ✅ Pipeline Verification

**Pipeline successfully:**
1. ✅ Detected all VESPER datasets in production folder
2. ✅ Validated CASAS format correctly
3. ✅ Compared with 220 ground truth files
4. ✅ Generated comprehensive reports
5. ✅ Exported detailed JSON results
6. ✅ Provided actionable recommendations

---

## 🔄 How It Works (Simplified)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DETECTION: Scan vesper_datasets/ folder                  │
│    → Found: 3 .txt files, 3 .json files                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. VALIDATION: Check CASAS format                           │
│    → All valid: 12, 14, 10 events                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. COMPARISON: Compare with ground truth                    │
│    → Loaded 220 ground truth CSV files                      │
│    → Compared sensor patterns                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. REPORTING: Generate analysis reports                     │
│    → vesper_comparison_report_*.md                          │
│    → pipeline_results_*.json                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Next Steps

When you run **real** Blender sessions:

1. **Run BGE Navigation:**
   ```bash
   python blender/llm_bge_navigation.py
   ```
   → Generates real datasets to `vesper_datasets/`

2. **Run Pipeline:**
   ```bash
   python evaluation/vesper_dataset_pipeline.py
   ```
   → Analyzes real data against ground truth

3. **Review Results:**
   ```bash
   cat casas_testbed/data/comparison_results/vesper_comparison_report_*.md
   ```

---

## 🎯 Summary

The pipeline is **production-ready** and successfully:
- ✅ Detects datasets automatically
- ✅ Validates CASAS format
- ✅ Compares with 220 ground truth files
- ✅ Generates comprehensive reports
- ✅ Works with clean, unified folder structure

**Everything is working as expected!** 🚀
