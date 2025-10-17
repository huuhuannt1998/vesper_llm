# 🎯 Device Tracking with Docker Container Integration

## Overview

This system ensures that:
1. **Agent reaches devices** before interaction (minimum 2.0 meters proximity)
2. **Time tracking** records exact usage duration for each device
3. **Docker containers** are checked for health and flagged during device use

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VESPER Interaction System                     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Item Sensors │    │  Time System │    │ Docker Bridge│
│              │    │              │    │              │
│ - Phone      │    │ - Duration   │    │ - Container  │
│ - Stove      │    │ - Timestamps │    │   Health     │
│ - Sinks      │    │ - Virtual    │    │ - Device     │
│ - Table      │    │   Time       │    │   Flagging   │
└──────────────┘    └──────────────┘    └──────────────┘
```

## How It Works

### 1. Device Detection and Targeting

When the agent approaches a device:

```
Distance > 2.0m:
🎯 TARGET SET: Phone (3.5m away - NEED TO GET CLOSER)
↓
Agent navigates closer...
↓
Distance ≤ 2.0m:
✅ DEVICE REACHED: Phone (1.8m away)
```

### 2. Container Health Check

Before interaction starts:

```python
# Check if Docker container is healthy
container_ok = bridge.check_container_health(serial_number, port)

if not container_ok:
    ⚠️ Cannot interact with Phone - Docker container unhealthy
    # Interaction blocked
```

### 3. Device Flagging During Use

When interaction starts:

```
🔴 Device Phone FLAGGED as IN USE (container: ABC123:8001)
↓
Time tracking starts...
↓
Interaction happens (agent uses device)
↓
Time tracking records duration
↓
🟢 Device Phone FLAGGED as AVAILABLE (container: ABC123:8001)
```

### 4. Time Tracking

Time system records:
- **Real time**: Actual seconds elapsed
- **Virtual time**: Accelerated time (e.g., 5 min task in 10s real time)
- **Start/End timestamps**: Precise event timing

## Setup Instructions

### Step 1: Create Item Sensors in Blender

Create objects with these **exact names** (case-sensitive):

```
✅ Phone          (for "Make a phone call")
✅ BathroomSink   (for "Wash Hand")
✅ Stove          (for "cook oatmeal")
✅ DiningTable    (for "eat Meal")
✅ KitchenSink    (for "clean dishes")
```

### Step 2: Ensure Docker Containers are Running

Make sure backend-console is running and has spawned virtual devices:

```bash
# Check backend health
curl http://localhost:8088/health

# Check active devices
curl http://localhost:8088/api/console/devices
```

### Step 3: Link Item Sensors to Docker Containers

Run the linking script:

```bash
cd blender/interaction_system
python link_sensors_to_docker.py
```

This will:
- Query backend for active Docker containers
- Match item sensors to appropriate device types
- Check container health
- Create bidirectional links

Expected output:
```
✅ LINKED: Phone → ABC123:8001 (smart_speaker) ✅ HEALTHY
✅ LINKED: BathroomSink → DEF456:8002 (smart_faucet) ✅ HEALTHY
✅ LINKED: KitchenSink → GHI789:8003 (smart_faucet) ✅ HEALTHY
✅ LINKED: Stove → JKL012:8004 (thermostat) ✅ HEALTHY
✅ LINKED: DiningTable → MNO345:8005 (motion_sensor) ✅ HEALTHY

LINKING COMPLETE: 5/5 sensors linked
```

### Step 4: Run Blender Simulation

The system will now:
1. Detect when agent approaches devices
2. Wait until agent is within 2.0m
3. Check Docker container health
4. Start interaction and flag device as in use
5. Track time usage
6. Unflag device when interaction ends

## Log Files Generated

After running, check these files:

### 1. **item_sensor_log.txt** (CASAS format)
```
2025-10-17 14:23:15.123 I008 Phone ON
2025-10-17 14:28:45.456 I008 Phone OFF
2025-10-17 14:30:00.789 I010 BathroomSink ON
2025-10-17 14:32:30.012 I010 BathroomSink OFF
```

### 2. **time_tracking_log.json**
```json
{
  "Make a phone call": {
    "real_duration": 10.5,
    "virtual_duration": 330.0,
    "time_scale": 30.0,
    "start_time": "2025-10-17T14:23:15.123",
    "end_time": "2025-10-17T14:28:45.456"
  }
}
```

### 3. **device_docker_tracking.json** (NEW)
```json
{
  "device_states": {
    "Phone": {
      "serial": "ABC123",
      "port": 8001,
      "in_use": false,
      "healthy": true,
      "device_type": "smart_speaker"
    }
  },
  "container_health": {
    "ABC123": {
      "healthy": true,
      "last_check": 1697557845.123,
      "port": 8001
    }
  }
}
```

## Verification Checklist

Use this checklist to verify everything is working:

- [ ] Item sensors created with correct names (Phone, BathroomSink, Stove, DiningTable, KitchenSink)
- [ ] Docker containers running (check `http://localhost:8088/api/console/devices`)
- [ ] Linking script executed successfully (5/5 sensors linked)
- [ ] Agent approaches devices and sees "TARGET SET" message
- [ ] Agent gets closer and sees "DEVICE REACHED" message
- [ ] Container health checked before interaction
- [ ] Device flagged as "IN USE" when interaction starts
- [ ] Time tracking shows duration in logs
- [ ] Device flagged as "AVAILABLE" when interaction ends
- [ ] All 3 log files generated with correct data

## Console Output Example

When working correctly, you should see:

```
🎯 TARGET SET: Phone (3.5m away - NEED TO GET CLOSER)
... (agent navigates) ...
✅ DEVICE REACHED: Phone (1.8m away)
🤝 Started interaction: Phone (task: Make a phone call)
🔴 Device Phone FLAGGED as IN USE (container: ABC123:8001)
⏱️  Virtual time accelerated: 1.0x → 30.0x (task duration: 5.0 min)
... (time passes) ...
✋ Ended interaction with: Phone (Duration: 10.5s)
🟢 Device Phone FLAGGED as AVAILABLE (container: ABC123:8001)

✅ Task completed: Make a phone call
   Duration: 330.0s (5.5 min)
   Real time: 10.5s
   Time acceleration: 30.0x
```

## Troubleshooting

### Problem: "Cannot interact - Docker container unhealthy"

**Solution**: Check container status
```bash
curl http://localhost:8001/health
```
If unhealthy, restart the container or respawn the device.

### Problem: "No sensors were linked"

**Solution**: Spawn devices first
```bash
# Use backend console web UI at http://localhost:8088
# Or use virtual_device_manager.py to spawn devices
```

### Problem: Agent never reaches device

**Solution**: 
1. Check if device object exists in Blender scene
2. Verify object name matches exactly (case-sensitive)
3. Ensure agent can navigate to device location
4. Check `min_interaction_distance` (default: 2.0m)

### Problem: Time tracking not showing in logs

**Solution**:
1. Verify interaction system is initialized
2. Check if `time_system` module is available
3. Ensure task names match expected format
4. Look for errors in console output

## API Reference

### Key Methods

#### `update_interaction_state(actor_position, current_task)`
Checks for nearby devices and manages interaction lifecycle.

#### `is_device_reached(object_name=None)`
Returns `True` if agent has reached the target device.

#### `get_target_device_status()`
Returns detailed status of current target device.

#### `flag_device_in_use(object_name, serial, port, in_use=True)`
Flags a device as in use or available in Docker container.

#### `check_container_health(serial_number, port)`
Checks if Docker container is responding and healthy.

## Integration with Existing Code

The Docker integration is **optional** and **non-breaking**:

- If `device_docker_integration.py` is not available, system works without it
- If backend is not reachable, interactions still work (just no Docker flagging)
- All existing functionality preserved

## Benefits

1. **Ensures realistic interaction**: Agent must physically reach device
2. **Accurate time tracking**: Records exact duration of device usage
3. **Docker awareness**: Checks container health before allowing interaction
4. **Device state tracking**: Knows which devices are in use at any time
5. **Complete audit trail**: All interactions logged with timestamps

## Next Steps

1. Test with actual Blender simulation
2. Verify all 5 devices can be reached and interacted with
3. Check log files for correct data
4. Validate Docker container flagging works
5. Confirm time tracking shows realistic durations
