# VESPER Interaction System - Quick Reference

## 🎯 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    VESPER Interaction System                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Item Sensors │  │   Devices    │  │     Time     │          │
│  │   (I001-50)  │  │  (D001-50)   │  │ Acceleration │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         └─────────────────┴──────────────────┘                   │
│                           │                                      │
│                  ┌────────▼────────┐                            │
│                  │   Integration   │                            │
│                  │     System      │                            │
│                  └────────┬────────┘                            │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│    ┌────▼────┐      ┌────▼────┐      ┌────▼────┐              │
│    │   BGE   │      │   VLM   │      │  CASAS  │              │
│    │   Nav   │      │ Decision│      │ Dataset │              │
│    └─────────┘      └─────────┘      └─────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📂 File Organization

```
blender/
│
├── interaction_system/          🎯 Object Interaction
│   ├── item_sensor_manager.py      → Track item usage (CASAS format)
│   └── object_interaction_handler.py → Manage object interactions
│
├── time_system/                 ⏱️ Time Management
│   └── virtual_time_manager.py     → Time acceleration & tracking
│
├── virtual_sensors/             💡 Smart Devices
│   └── virtual_device_manager.py   → SmartThings-style control
│
├── vesper_interaction_integration.py  🔗 Main Integration
├── demo_interaction_system.py         🧪 Complete Demo
├── interaction_config.py              ⚙️ Configuration
│
└── Documentation/
    ├── INTERACTION_SYSTEM_README.md   📖 Full docs
    ├── INTEGRATION_QUICK_START.py     🚀 Integration guide
    └── PROJECT_SUMMARY.md             📋 Summary
```

## 🔄 Data Flow

```
┌─────────────┐
│  Actor      │
│  Navigates  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Check Proximity to Objects │
└──────┬──────────────────────┘
       │
       ▼
   ┌───────┐ No
   │ Near? ├─────→ Continue Navigation
   └───┬───┘
       │ Yes
       ▼
┌─────────────────────┐
│ Start Interaction   │
│ • Item Sensor ON    │
│ • Device Control    │
│ • Time Acceleration │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Perform Task        │
│ (Accelerated Time)  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ End Interaction     │
│ • Item Sensor OFF   │
│ • Log Duration      │
│ • Reset Time        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Export CASAS Data   │
└─────────────────────┘
```

## 💾 Output Files

```
vesper_datasets/
├── item_sensor_log_20241014_120000.txt      ← CASAS format
├── item_interactions_20241014_120000.json   ← Detailed JSON
├── device_log_20241014_120000.json          ← Device states
└── virtual_time_log.json                    ← Time events
```

## 📊 CASAS Format Example

```
TIMESTAMP                SENSOR  NAME         EVENT
─────────────────────────────────────────────────────
2024-10-14 12:00:00.123  I001    Phone        ON
2024-10-14 12:05:15.456  I001    Phone        OFF
2024-10-14 12:05:30.789  I002    Stove        ON
2024-10-14 12:20:45.012  I002    Stove        OFF
2024-10-14 12:21:00.345  I009    DiningTable  ON
2024-10-14 12:41:15.678  I009    DiningTable  OFF
```

## 🎮 Usage Examples

### Example 1: Simple Task
```python
system.start_task_with_interactions("Make a phone call", actor_pos)
# → Auto-turns on Dining Room light
# → Detects phone nearby
# → Starts item sensor I001
# → Accelerates 5 min → 3 sec
system.complete_task("Make a phone call")
# → Logs all interactions
```

### Example 2: Complex Task
```python
system.start_task_with_interactions("Cook oatmeal", actor_pos)
# → Turns on Kitchen light
# → Navigate to stove
# → Interact with stove (I002 ON)
# → Cook: 15 min → 4 sec
# → End interaction (I002 OFF)
system.complete_task("Cook oatmeal")
```

### Example 3: Long Duration
```python
system.start_task_with_interactions("Go to sleep", actor_pos)
# → Turns off Bedroom lights
# → Interact with bed (I014 ON)
# → Sleep: 8 hours → 5 sec
# → Wake up (I014 OFF)
system.complete_task("Go to sleep")
```

## ⚙️ Configuration Quick Reference

### Sensor IDs
- **I001-I019**: Item sensors (19 configured)
- **D001-D011**: Devices (11 configured)
- **M001-M050**: Motion sensors (existing)

### Time Scales
```python
Real Time → Virtual Time
─────────────────────────
1 sec     →  1 sec        (Normal)
1 sec     →  10 sec       (10x acceleration)
5 sec     →  8 hours      (5760x acceleration for sleep)
```

### Interaction Distances
- **Manual objects**: 1.5 Blender units (stove, sink)
- **Auto objects**: 1.0 units (phone, items)
- **Furniture**: 1.5 units (bed, table)

## 🧪 Testing Commands

```bash
# Test each system
python interaction_system/item_sensor_manager.py
python time_system/virtual_time_manager.py
python virtual_sensors/virtual_device_manager.py

# Run complete demo
python demo_interaction_system.py

# Test integration
python vesper_interaction_integration.py

# Export configuration
python interaction_config.py
```

## 🚀 Integration Checklist

- [ ] Review `INTERACTION_SYSTEM_README.md`
- [ ] Run `demo_interaction_system.py`
- [ ] Check output files in `vesper_datasets/`
- [ ] Review `INTEGRATION_QUICK_START.py`
- [ ] Add imports to `llm_bge_navigation.py`
- [ ] Initialize in `main()` function
- [ ] Test with existing navigation
- [ ] Verify CASAS format output
- [ ] Customize `interaction_config.py` if needed

## 🎯 Key Benefits

| Feature | Benefit |
|---------|---------|
| **Item Sensors** | Track every object interaction with CASAS format |
| **Time Acceleration** | Complete 8-hour tasks in seconds |
| **Virtual Devices** | SmartThings-style automation |
| **Clean Organization** | Separate folders for each system |
| **Easy Integration** | Minimal changes to existing code |
| **CASAS Compatible** | Direct comparison with real datasets |

## 📞 Quick API Reference

```python
# Get systems
system = get_interaction_system()
item_mgr = get_item_sensor_manager()
time_mgr = get_virtual_time_manager()
device_mgr = get_device_manager()

# Start task
system.start_task_with_interactions(task_name, actor_pos)

# Interact
system.interaction_handler.start_interaction(object_name, task)
system.interaction_handler.end_interaction()

# Time
time_mgr.accelerate_for_task(task, virtual_duration, real_duration)

# Devices
device_mgr.control_device(device_id, "on")
device_mgr.auto_control_for_task(task_name, room)

# Complete
system.complete_task(task_name, success=True)
system.export_all_data()
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| No sensors detected | Check Blender object names match config |
| Time not accelerating | Verify task duration > 5 minutes |
| Devices not controlling | Check device IDs in config |
| No CASAS output | Call `export_all_data()` at end |
| Import errors | Ensure all `__init__.py` files exist |

---

**Quick Start**: Run `python demo_interaction_system.py` to see everything in action!
