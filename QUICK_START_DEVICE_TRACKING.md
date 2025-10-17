# 🚀 Quick Start: Device Reaching + Docker Tracking

**Get your Blender simulation working with device tracking in 5 steps!**

---

## Prerequisites

✅ Blender Game Engine setup complete  
✅ Backend console running (`http://localhost:8088`)  
✅ Docker containers with virtual devices spawned  

---

## Step 1: Create Item Sensors in Blender (5 minutes)

Open your Blender file and create these objects with **EXACT NAMES**:

```
Phone          ← for "Make a phone call" task
BathroomSink   ← for "Wash Hand" task
Stove          ← for "cook oatmeal" task
DiningTable    ← for "eat Meal" task
KitchenSink    ← for "clean dishes" task
```

**Important**: 
- Use PascalCase (no spaces, no underscores)
- Spelling must match exactly
- Place objects in appropriate rooms

---

## Step 2: Verify Docker Containers (2 minutes)

Open PowerShell and check:

```powershell
# Check if backend is running
curl http://localhost:8088/health

# Check active devices
curl http://localhost:8088/api/console/devices
```

**Expected**: You should see JSON with at least 5 devices (one for each sensor type)

**If no devices**: Go to `http://localhost:8088` in browser and spawn devices using the web UI.

---

## Step 3: Link Sensors to Containers (1 minute)

Run the linking script:

```powershell
cd C:\Users\hbui11\Desktop\vesper_llm\blender\interaction_system
python link_sensors_to_docker.py
```

**Expected output**:
```
✅ LINKED: Phone → ABC123:8001 (smart_speaker) ✅ HEALTHY
✅ LINKED: BathroomSink → DEF456:8002 (smart_faucet) ✅ HEALTHY
✅ LINKED: KitchenSink → GHI789:8003 (smart_faucet) ✅ HEALTHY
✅ LINKED: Stove → JKL012:8004 (thermostat) ✅ HEALTHY
✅ LINKED: DiningTable → MNO345:8005 (motion_sensor) ✅ HEALTHY

LINKING COMPLETE: 5/5 sensors linked
```

**If not all linked**: Spawn more devices matching the required types.

---

## Step 4: Run Blender Simulation (Test!)

1. Open Blender with your house scene
2. Start the game engine (press P)
3. Watch the console output

**What to look for**:

```
🎯 TARGET SET: Phone (3.5m away - NEED TO GET CLOSER)
   ↓
✅ DEVICE REACHED: Phone (1.8m away)
   ↓
🤝 Started interaction: Phone (task: Make a phone call)
   ↓
🔴 Device Phone FLAGGED as IN USE (container: ABC123:8001)
   ↓
⏱️  Virtual time accelerated: 1.0x → 30.0x
   ↓
✋ Ended interaction with: Phone (Duration: 10.5s)
   ↓
🟢 Device Phone FLAGGED as AVAILABLE (container: ABC123:8001)
   ↓
✅ Task completed: Make a phone call
   Duration: 330.0s (5.5 min)
   Real time: 10.5s
   Time acceleration: 30.0x
```

---

## Step 5: Verify Logs (1 minute)

Check these files in `vesper_logs/` or `datasets/`:

### ✅ item_sensor_log.txt
```
2025-10-17 14:23:15.123 I008 Phone ON
2025-10-17 14:28:45.456 I008 Phone OFF
2025-10-17 14:30:00.789 I010 BathroomSink ON
2025-10-17 14:32:30.012 I010 BathroomSink OFF
```

### ✅ time_tracking_log.json
```json
{
  "Make a phone call": {
    "real_duration": 10.5,
    "virtual_duration": 330.0,
    "time_scale": 30.0
  }
}
```

### ✅ device_docker_tracking.json (NEW!)
```json
{
  "device_states": {
    "Phone": {
      "serial": "ABC123",
      "port": 8001,
      "in_use": false,
      "healthy": true
    }
  }
}
```

---

## ✅ Success Checklist

Mark these off as you complete them:

- [ ] 5 item sensors created in Blender with correct names
- [ ] Backend console responding at localhost:8088
- [ ] At least 5 Docker containers spawned
- [ ] Linking script shows 5/5 sensors linked
- [ ] Console shows "TARGET SET" when approaching devices
- [ ] Console shows "DEVICE REACHED" when close enough
- [ ] Console shows "FLAGGED as IN USE" during interaction
- [ ] Time tracking shows duration in console
- [ ] All 3 log files generated
- [ ] CASAS format events in item_sensor_log.txt
- [ ] Duration data in time_tracking_log.json
- [ ] Docker states in device_docker_tracking.json

---

## 🔧 Troubleshooting

### Problem: "No sensors were linked"

**Fix**: Spawn more devices
```powershell
# Go to http://localhost:8088 and click "Spawn Device" multiple times
# Need: smart_speaker, smart_faucet (x2), thermostat, motion_sensor
```

### Problem: "Container unhealthy"

**Fix**: Check container health
```powershell
curl http://localhost:8001/health
# If fails, restart container or respawn device
```

### Problem: Agent never reaches device

**Fix**: 
1. Check if object exists in Blender scene
2. Verify object name is exactly correct (case-sensitive!)
3. Ensure agent can navigate to device location

### Problem: No time tracking in logs

**Fix**:
1. Make sure interaction system initialized (check console)
2. Verify task names match expected format
3. Look for errors in console output

---

## 📚 Full Documentation

For detailed information, see:
- `DEVICE_DOCKER_TRACKING_GUIDE.md` - Complete guide
- `DEVICE_REACHING_DOCKER_TRACKING_SUMMARY.md` - Implementation details

---

## 🎉 Expected Results

After completing all steps, your simulation will:

✅ Make agent reach devices before interaction  
✅ Check Docker container health automatically  
✅ Flag devices IN USE during interaction  
✅ Track exact time spent using each device  
✅ Generate CASAS-compatible logs  
✅ Export Docker tracking data  

**Total Setup Time**: ~10 minutes  
**Result**: Fully tracked, realistic device interactions!

---

## 🆘 Need Help?

If something doesn't work:
1. Check console output for error messages
2. Verify all prerequisites are met
3. Review the troubleshooting section
4. Check the full guide: `DEVICE_DOCKER_TRACKING_GUIDE.md`
