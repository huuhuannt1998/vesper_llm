# VESPER Motion Sensor Auto-Setup Guide

## 🎯 Automatic Detection Area Creation

Every motion sensor you create will automatically have its own visual detection area with realistic Aeotec SmartThings specifications:

- **120° field of view cone** (blue wireframe visualization)
- **5-meter detection range** (industry standard)
- **Real-time color changes** (blue = idle, red = detecting motion)
- **Semi-transparent display** (non-interfering with navigation)
- **Automatic integration** with VESPER detection system

## 🚀 Quick Setup Methods

### Method 1: Full Automatic Setup (Recommended)

```python
# In Blender, load and run this script:
exec(open(r"C:\Users\hbui11\Desktop\vesper_llm\auto_setup_motion_sensors.py").read())

# This creates 5 optimally placed sensors with automatic detection areas:
# ✅ M01_LivingRoom - Main living area coverage
# ✅ M02_Kitchen - Kitchen prep and cooking area  
# ✅ M03_Hallway - Main traffic monitoring
# ✅ M04_Bedroom - Bedroom occupancy detection
# ✅ M05_Entry - Security entrance monitoring
```

### Method 2: Using Motion Sensor Launcher

```bash
# From command line:
cd C:\Users\hbui11\Desktop\vesper_llm
python motion_sensor_launcher.py setup --layout medium_house

# This deploys 10 sensors with automatic detection areas
```

### Method 3: Manual Individual Sensors

```python
# In Blender BGE, create individual sensors:
from addons.vesper_smart_home import device_manager
from mathutils import Vector

# Create a motion sensor - detection area is automatic!
device_manager.add_motion_sensor(
    sensor_id="M01_Kitchen",
    room="kitchen", 
    position=Vector((-2.0, 5.0, 2.3)),
    orientation=270.0  # Facing towards stove/counter
)

# The sensor automatically gets:
# 🎯 Visual 120° detection cone (blue wireframe)
# 📏 5-meter detection range
# 🔴 Real-time color changes when detecting
# 📱 SmartThings integration
```

## 🔧 Step-by-Step Setup in Blender

### 1. Prepare Blender Scene

```python
# 1. Open Blender with your house layout
# 2. Ensure you have an "Actor" object in the scene
# 3. Switch to "Scripting" workspace
# 4. Create new text file in Text Editor
```

### 2. Load VESPER Motion Sensor System

```python
# Paste this code in Blender Text Editor:
import bpy
import sys
import os
from mathutils import Vector

# Add VESPER paths
vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
sys.path.append(os.path.join(vesper_root, "motion_sensors"))
sys.path.append(os.path.join(vesper_root, "blender", "addons"))

# Import device manager
from vesper_smart_home import device_manager

print("✅ VESPER Motion Sensor System loaded")
```

### 3. Create Motion Sensors with Automatic Detection Areas

```python
# Create sensors - each automatically gets visual detection area
sensors_to_create = [
    ("M01_LivingRoom", Vector((3.0, 4.0, 2.2)), "living_room", 225.0),
    ("M02_Kitchen", Vector((-1.5, 5.0, 2.3)), "kitchen", 270.0),
    ("M03_Hallway", Vector((0.0, 0.0, 2.4)), "hallway", 0.0),
]

for sensor_id, position, room, orientation in sensors_to_create:
    success = device_manager.add_motion_sensor(sensor_id, room, position, orientation)
    if success:
        print(f"✅ {sensor_id} created with automatic detection area")

print("🎉 All sensors created with automatic 120° detection cones!")
```

### 4. Test in Game Engine

```python
# 1. Switch to "Layout" workspace
# 2. Press P to start Blender Game Engine
# 3. Move the Actor around using arrow keys
# 4. Watch detection cones change from blue to red when Actor enters
# 5. Check console for detection events
```

## 🎨 Visual Detection Areas Explained

When you create a motion sensor, it automatically creates:

### Visual Cone Properties
- **Shape**: 120° cone extending 5 meters from sensor
- **Color**: Blue (idle) → Red (detecting motion)
- **Display**: Semi-transparent wireframe
- **Collision**: Non-collidable (won't interfere with Actor movement)
- **Rendering**: Hidden from final renders

### Automatic Features
```python
# Each detection area automatically includes:
{
    "detection_range": 5.0,      # meters (Aeotec SmartThings spec)
    "field_of_view": 120.0,      # degrees
    "visualization": "wireframe", # Semi-transparent cone
    "color_idle": "blue",        # (0.2, 0.6, 1.0, 0.3)
    "color_detecting": "red",    # (1.0, 0.2, 0.2, 0.5)
    "non_collidable": True,      # Won't block Actor movement
    "hide_render": True          # Won't appear in renders
}
```

## 🔍 Real-Time Detection Features

### Automatic State Changes
- **Idle State**: Blue wireframe cone, semi-transparent
- **Detecting State**: Red cone, more opaque
- **Cooldown Period**: 3 seconds between detections
- **Motion Threshold**: 0.1 meters minimum movement

### Console Output
```
🚨 Motion Sensor M01_LivingRoom triggered:
   🏠 Room: living_room
   📍 Position: [3.0, 4.0]
   🔍 Event: motion_detected
   📊 Detection Count: 5
   🎯 Visual detection area updated (blue → red)
```

## 📱 SmartThings Integration

Each sensor automatically connects to SmartThings simulation:

```python
# Automatic SmartThings events:
{
    "device_id": "M01_LivingRoom",
    "event_type": "motion_detected",
    "room": "living_room", 
    "timestamp": "2025-09-08T15:30:00Z",
    "detection_count": 5
}
```

## 🛠️ Customization Options

### Custom Sensor Placement
```python
# Create sensor at specific location with automatic detection area
device_manager.add_motion_sensor(
    sensor_id="M_Custom",
    room="office",
    position=Vector((5.0, 1.0, 2.2)),  # Your desired position
    orientation=180.0                   # Facing direction
)
# Detection area is created automatically!
```

### Bulk Sensor Creation
```python
# Create multiple sensors from layout
from motion_sensors.configs import load_sensor_layout

layout = load_sensor_layout("medium_house")
for sensor in layout['sensors']:
    device_manager.add_motion_sensor(
        sensor['id'],
        sensor['room'],
        Vector(sensor['position']['x'], sensor['position']['y'], sensor['position']['z']),
        sensor['orientation']
    )
    # Each gets automatic detection area!
```

## 🎮 Testing Your Setup

### 1. Visual Verification
- Look for blue wireframe cones in 3D viewport
- Each sensor should have a 120° cone extending 5 meters
- Cones should be oriented correctly based on sensor direction

### 2. Runtime Testing
- Start BGE (Press P)
- Move Actor through detection zones
- Watch cones change from blue to red
- Check console for detection events

### 3. Coverage Analysis
```python
# Check sensor coverage
from motion_sensors import get_motion_detection_status

status = get_motion_detection_status()
print(f"Active sensors: {status['active_sensors']}")
print(f"Currently detecting: {status['sensors_detecting']}")
```

## 🚨 Troubleshooting

### Common Issues

**Detection areas not visible:**
- Check 3D viewport shading mode (Wireframe or Solid)
- Ensure objects aren't hidden in outliner
- Verify material transparency is enabled

**Sensors not detecting:**
- Confirm Actor object exists and is named "Actor"
- Check BGE is running (Press P)
- Verify sensor orientations are correct

**Import errors:**
- Ensure VESPER paths are correct in sys.path
- Check motion_sensors folder exists
- Verify Blender addon is installed

### Debug Commands
```python
# Check if detection system is working
from motion_sensors import get_motion_detection_status
status = get_motion_detection_status()
print(status)

# Verify device manager
from vesper_smart_home import device_manager
print(f"Registered sensors: {len(device_manager.device_registry)}")
```

## 🎉 Result

After setup, you'll have:
- ✅ Motion sensors with automatic 120° detection cones
- ✅ Real-time visual feedback (blue → red when detecting)
- ✅ Professional Aeotec SmartThings specifications
- ✅ SmartThings app integration
- ✅ Complete coverage analysis and statistics

**Every motion sensor you create will automatically have its own realistic detection area!** 🎯
