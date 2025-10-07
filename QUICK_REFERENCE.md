# 🚀 VESPER Quick Reference Card

## Production Workflow (2 Steps)

### **Step 1: Generate**
```bash
python blender/llm_bge_navigation.py
```
→ Outputs to `casas_testbed/vesper_datasets/`

### **Step 2: Analyze**
```bash
python evaluation/vesper_dataset_pipeline.py
```
→ Results in `casas_testbed/data/comparison_results/`

---

## 📁 File Locations

| Type | Location |
|------|----------|
| **VESPER Datasets** | `casas_testbed/vesper_datasets/` |
| **Ground Truth** | `casas_testbed/data/casas_ground_truth/` |
| **Comparison Results** | `casas_testbed/data/comparison_results/` |

---

## 📊 Output Files

After BGE run:
- `vesper_casas_p01_YYYYMMDD_HHMMSS.txt` ← Motion sensors
- `vesper_metrics_p01_YYYYMMDD_HHMMSS.json` ← VLM metrics

After pipeline:
- `vesper_comparison_report_YYYYMMDD_HHMMSS.md` ← Analysis report
- `pipeline_results_YYYYMMDD_HHMMSS.json` ← Full results

---

## ✅ Verification

```bash
python complete_casas_setup.py
```
Should show: `7/7 components ready` + `220 ground truth files`

---

## 🔍 Quick Checks

```bash
# View generated datasets
ls casas_testbed/vesper_datasets/

# View comparison results
ls casas_testbed/data/comparison_results/

# View ground truth
ls casas_testbed/data/casas_ground_truth/adl_noerror/
```

---

## 📚 Documentation

- `PRODUCTION_WORKFLOW.md` ← Start here!
- `PRODUCTION_UPDATE_SUMMARY.md` ← What changed
- `VESPER_DATASET_GENERATION_GUIDE.md` ← Detailed guide
- `CASAS_GROUND_TRUTH_INFO.md` ← Ground truth info

---

## ⚡ Common Commands

```bash
# Full workflow
python complete_casas_setup.py              # Verify
python blender/llm_bge_navigation.py        # Generate
python evaluation/vesper_dataset_pipeline.py # Compare

# Check outputs
cat casas_testbed/vesper_datasets/vesper_casas_*.txt
cat casas_testbed/data/comparison_results/vesper_comparison_report_*.md
```

---

**That's it! Two commands, one production folder. Simple. Clean. Ready.** 🎯
