# How to Integrate VESPER Interaction System with llm_bge_navigation.py

## 🎯 Overview

The VESPER Interaction System is **already imported** into your `llm_bge_navigation.py` file, but needs a few code additions to be fully functional.

## ✅ What's Already Done

- Import statement is in place
- All interaction modules are created and ready
- System is available via `INTERACTION_SYSTEM_AVAILABLE` flag

## 📋 What You Need to Do

Add **6 code snippets** to specific locations in `llm_bge_navigation.py`. Each takes ~5 lines of code.

---

## 🚀 Quick Integration (Copy & Paste)

### 1️⃣ Initialize System (Line ~1234)

**Find**: `# Initialize CASAS motion sensor logging`  
**Add After**:
```python
# Initialize VESPER Interaction System
if INTERACTION_SYSTEM_AVAILABLE and not hasattr(bge.logic, 'interaction_system'):
    try:
        initialize_interaction_system_for_bge()
        print("✅ VESPER Interaction System integrated")
    except Exception as e:
        print(f"⚠️ Interaction init failed: {e}")
```

### 2️⃣ Start Task Tracking (Line ~1275)

**Find**: `bge.logic.current_task_logged = bge.logic.current_task_index`  
**Add After**:
```python
# Start interaction tracking
if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
    if not hasattr(bge.logic, 'task_interaction_started') or not bge.logic.task_interaction_started:
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        if actor:
            try:
                bge.logic.interaction_system.start_task_with_interactions(
                    current_task, [actor.worldPosition.x, actor.worldPosition.y]
                )
                bge.logic.task_interaction_started = True
            except: pass
```

### 3️⃣ Complete Task Successfully (Line ~1387)

**Find**: `if task_complete:`  
**Add After** (before metrics_logger code):
```python
# Complete with interaction system
if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
    try:
        bge.logic.interaction_system.complete_task(current_task, success=True)
        bge.logic.task_interaction_started = False
    except: pass
```

### 4️⃣ Handle Task Failure (Line ~1297)

**Find**: `if bge.logic.navigation_step >= bge.logic.max_steps_per_task:`  
**Add After** (before metrics_logger code):
```python
# Log interaction failure
if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
    try:
        bge.logic.interaction_system.complete_task(current_task, success=False)
        bge.logic.task_interaction_started = False
    except: pass
```

### 5️⃣ Export All Data (Line ~1256)

**Find**: `if bge.logic.current_task_index >= len(bge.logic.vesper_tasks):`  
**Add Before** `return`:
```python
# Export interaction data
if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
    try:
        print("\n💾 Exporting interaction data...")
        bge.logic.interaction_system.print_session_summary()
        bge.logic.interaction_system.export_all_data()
    except: pass
```

### 6️⃣ Update During Navigation (Line ~1430) - OPTIONAL

**Find**: `success = execute_movement(action)`  
**Add After**:
```python
# Update interactions
if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    if actor:
        try:
            events = bge.logic.interaction_system.update_interaction_state(
                [actor.worldPosition.x, actor.worldPosition.y], current_task
            )
        except: pass
```

---

## ✨ That's It!

After adding these 6 snippets, you'll have:

✅ **Item Sensors** - Automatic object interaction tracking  
✅ **Virtual Devices** - Smart home device control  
✅ **Time Acceleration** - Fast-forward long tasks  
✅ **CASAS Export** - Compatible dataset format  

---

## 📊 Output Files

After running, check: `casas_testbed/vesper_datasets/`

- `item_sensor_log_*.txt` - CASAS format events
- `item_interactions_*.json` - Detailed interaction data
- `device_log_*.json` - Device state changes
- `virtual_time_log.json` - Time acceleration events

---

## 🧪 Test It

1. Add the 6 code snippets above
2. Run your BGE navigation
3. Complete a few tasks
4. Check the output files

Console should show:
```
✅ VESPER Interaction System integrated
🎯 Interaction tracking started for: Make a phone call
💾 Exporting interaction data...
```

---

## 📚 Need Help?

- **Detailed Guide**: `INTEGRATION_STATUS.md`
- **All Code Snippets**: `INTEGRATION_PATCHES.py`  
- **Standalone Demo**: Run `python demo_interaction_system.py`
- **Documentation**: `INTERACTION_SYSTEM_README.md`

---

## 💡 Minimal Integration (3 lines)

If you just want basic functionality:

```python
# 1. In main() after CASAS logger
if INTERACTION_SYSTEM_AVAILABLE:
    initialize_interaction_system_for_bge()

# 2. When all tasks complete
if hasattr(bge.logic, 'interaction_system'):
    bge.logic.interaction_system.export_all_data()
```

This gives you automatic interaction logging with minimal code!

---

**Ready to integrate?** Just copy-paste the 6 snippets above! 🚀
