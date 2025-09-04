# Running VESPER-CASAS Testbed with Blender Game Engine + VLM

## Overview

This guide shows how to run the complete testbed with:
- ✅ **Exact CASAS task alignment** (5 ADL tasks)
- ✅ **Exact CASAS sensor mapping** (M01-M026, I01-I08, etc.)
- ✅ **Blender Game Engine** with VLM navigation
- ✅ **Real-time CASAS dataset generation** from navigation
- ✅ **Automatic evaluation** against CASAS ground truth

## Prerequisites

### ✅ Already Completed:
1. **CASAS Dataset Generator**: `casas_testbed/vesper_casas_dataset_generator.py`
2. **CASAS Task Definitions**: `blender/vesper_casas_tasks.txt`
3. **Blender Integration**: Modified `blender/llm_bge_navigation.py`
4. **Evaluation System**: `casas_testbed/integration/`

### 🔧 What You Need:
1. **Blender/UPBGE** with house layout (`house_2.blend` or `house_3.blend`)
2. **LLM Backend** running (for VLM navigation)
3. **CASAS Ground Truth** data (already in `casas_testbed/data/`)

## Step-by-Step Testbed Execution

### Step 1: Verify CASAS Integration

```bash
# Test CASAS generator standalone
cd C:\Users\hbui11\Desktop\vesper_llm
python casas_testbed\vesper_casas_dataset_generator.py

# Expected output: 5 CASAS datasets generated
# Location: casas_testbed\data\vesper_generated\vesper_p01.t1.csv through vesper_p01.t5.csv
```

### Step 2: Start LLM Backend

```bash
# Start the VLM backend (in separate terminal)
cd C:\Users\hbui11\Desktop\vesper_llm
python -m backend.app.main

# Verify LLM is accessible at http://localhost:8000
```

### Step 3: Open Blender with Smart Home Layout

1. **Open UPBGE/Blender**
2. **Load house layout**: `blender/house_2.blend` or `house_3.blend`
3. **Verify objects**:
   - ✅ "Actor" object (navigation agent)
   - ✅ "BirdEyeCamera" (for screenshots)
   - ✅ Room boundaries and furniture

### Step 4: Configure CASAS Tasks

The integration will automatically load CASAS-aligned tasks:

```python
# Tasks loaded from blender/vesper_casas_tasks.txt:
# 1. Make phone call
# 2. Wash hands  
# 3. Cook oatmeal
# 4. Eat meal
# 5. Clean dishes
```

### Step 5: Run Blender Game Engine with VLM+CASAS

1. **Switch to Game Engine mode** in Blender
2. **Run the script**: Execute `llm_bge_navigation.py` 
3. **Monitor output**:
   ```
   🔗 LLM: Connected
   🏠 CASAS: Dataset generator connected
   🧠 BGE: VESPER Navigation initialized!
   📋 BGE: Tasks: ['Make phone call', 'Wash hands', 'Cook oatmeal', 'Eat meal', 'Clean dishes']
   🏠 BGE: CASAS session started - vesper_p01_t1_20250902_HHMMSS
   ```

### Step 6: Monitor VLM Navigation + CASAS Generation

**Expected sequence for each task**:

1. **VLM Navigation**: Actor moves to appropriate room using vision-language model
2. **Task Completion**: VLM confirms task completion (e.g., phone call made)
3. **CASAS Generation**: Realistic sensor events generated automatically
4. **Dataset Saved**: CASAS-format CSV file created
5. **Next Task**: System advances to next CASAS task

**Console Output Example**:
```
🎯 BGE: Executing task: Make phone call
📸 BGE: Screenshot captured for VLM analysis
🧠 VLM: Moving actor to dining room for phone task
✅ BGE: Task 'Make phone call' VALIDATED - Actor confirmed in correct room!
🏠 BGE: Generating CASAS events for 'Make phone call'
📊 CASAS: 14:30:15.123 M03 ON (move_to_dining_room)
📊 CASAS: 14:30:15.234 I08 PRESENT (pick_up_phone_book)
📊 CASAS: 14:30:15.345 * PHONE_PICKUP (use_phone)
💾 BGE: CASAS dataset saved - vesper_p01.t1.csv
🏠 BGE: Started CASAS session for next task: t2
```

### Step 7: Generated Datasets

After all 5 tasks complete, check:

```bash
# Generated CASAS datasets
ls casas_testbed\data\vesper_generated\
# vesper_p01.t1.csv  (Phone call - ~9 events)
# vesper_p01.t2.csv  (Wash hands - ~8 events)  
# vesper_p01.t3.csv  (Cook oatmeal - ~13 events)
# vesper_p01.t4.csv  (Eat meal - ~8 events)
# vesper_p01.t5.csv  (Clean dishes - ~10 events)

# Comparison results
ls casas_testbed\data\comparison_results\
# Contains evaluation reports and metrics
```

### Step 8: Evaluate Against CASAS Ground Truth

```python
# Automatic evaluation of generated datasets
from casas_testbed.integration import VESPERCASASIntegration

integration = VESPERCASASIntegration()

# Evaluate each task
for task_id in ['t1', 't2', 't3', 't4', 't5']:
    vesper_dataset = f"casas_testbed/data/vesper_generated/vesper_p01.{task_id}.csv"
    metrics = integration.compare_with_ground_truth(vesper_dataset, f"task_{task_id}")
    
    print(f"Task {task_id}: {metrics.overall_similarity:.1%} similarity")
    print(f"  Sensor Coverage: {metrics.sensor_coverage:.1%}")
    print(f"  Common Sensors: {metrics.common_sensors}")
    
# Results saved to: casas_testbed/data/comparison_results/
```

## Expected Results

### 🎯 **Real vs Simulated Comparison**:

**BEFORE (Simulated)**:
- Fixed timing patterns
- No actual navigation
- Lower similarity to CASAS (~11%)

**NOW (Real VLM Navigation)**:
- Realistic timing from actual movement
- Position-based sensor activation  
- Higher similarity to CASAS (expected 25-40%+)

### 📊 **Sample Real Dataset** (t1 - Phone Call):
```csv
date,time,sensor,message
2025-09-02,14:30:15.123,M03,ON         # Actor enters dining room
2025-09-02,14:30:15.234,I08,PRESENT    # Phone book picked up
2025-09-02,14:30:15.345,*,PHONE_PICKUP # Phone call starts
2025-09-02,14:30:45.567,*,PHONE_HANGUP # Phone call ends
2025-09-02,14:30:46.678,I08,ABSENT     # Phone book put down
2025-09-02,14:30:47.789,M03,OFF        # Actor leaves dining room
```

### 🏆 **Validation Metrics**:
- **Format Compatibility**: ✅ Exact CASAS CSV structure
- **Sensor Accuracy**: ✅ Real sensor IDs (M03, I08, *, etc.)
- **Task Sequences**: ✅ Realistic ADL patterns
- **Timing**: ✅ Millisecond precision from actual navigation
- **Evaluation**: ✅ Direct comparison with CASAS ground truth

## Troubleshooting

### Issue: "CASAS: Dataset generator not available"
**Solution**: Ensure `casas_testbed/vesper_casas_dataset_generator.py` exists and is importable

### Issue: "LLM: Import failed"
**Solution**: Start the LLM backend server and verify connectivity

### Issue: No datasets generated
**Solution**: Check that tasks complete successfully (STAY command validation)

### Issue: Low similarity scores
**Solution**: Adjust room boundaries and sensor mappings in generator

## Summary

This testbed provides:

1. **Real VLM Navigation**: Actor navigates using vision-language model
2. **Exact CASAS Alignment**: Same tasks, sensors, and format as CASAS dataset
3. **Automatic Dataset Generation**: Real-time CASAS events during navigation
4. **Scientific Validation**: Direct comparison with established CASAS ground truth
5. **Research Ready**: Complete pipeline for ADL recognition research

**The testbed bridges the gap between simulated smart home environments and real ADL datasets, enabling rigorous evaluation of VLM navigation systems against established benchmarks.**
