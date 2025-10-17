# Device Reaching & Docker Tracking Flow Diagram

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        START SIMULATION                              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Link Sensors to Docker  │
                    │ Containers (one-time)   │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │ Task Assigned to Actor  │
                    │ "Make a phone call"     │
                    └─────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 1: DEVICE DETECTION                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │ Check nearby objects      │
                    │ within detection range    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │ Found: Phone (3.5m away)  │
                    │ Is this relevant to task? │
                    └─────────────┬─────────────┘
                                  │
                                  ├─── YES ───┐
                                  │           │
                    ┌─────────────▼───────────▼───┐
                    │ Is distance ≤ 2.0m?         │
                    └─────────────┬───────────────┘
                                  │
                    NO            │            YES
                    │             │             │
                    ▼             │             ▼
        ┌───────────────────┐    │    ┌─────────────────┐
        │ 🎯 TARGET SET:    │    │    │ ✅ DEVICE        │
        │ Phone (3.5m away) │    │    │ REACHED (1.8m)  │
        │ NEED TO GET CLOSER│    │    └────────┬────────┘
        └────────┬──────────┘    │             │
                 │                │             │
                 └───────┬────────┘             │
                         │                      │
                         ▼                      │
        ┌────────────────────────────┐          │
        │ Actor navigates closer...  │          │
        │ (VLM guides movement)      │          │
        └────────────┬───────────────┘          │
                     │                           │
                     └───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PHASE 2: CONTAINER HEALTH CHECK                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │ Check Docker container    │
                    │ health for Phone          │
                    │ Serial: ABC123            │
                    │ Port: 8001                │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │ GET http://localhost:8001 │
                    │            /health         │
                    └─────────────┬─────────────┘
                                  │
                                  ├─── Healthy (200 OK) ─┐
                                  │                       │
                    Unhealthy     │                       │
                    │             │                       ▼
                    ▼             │         ┌────────────────────────┐
        ┌───────────────────┐    │         │ ✅ Container healthy   │
        │ ⚠️  Cannot        │    │         │ Proceed to interaction │
        │ interact - Docker │    │         └────────┬───────────────┘
        │ container         │    │                  │
        │ unhealthy         │    │                  │
        └────────┬──────────┘    │                  │
                 │                │                  │
                 ▼                │                  │
        ┌────────────────┐       │                  │
        │ Skip interaction│       │                  │
        │ Wait or retry   │       │                  │
        └─────────────────┘       │                  │
                                  └──────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 3: START INTERACTION                        │
└─────────────────────────────────────────────────────────────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Start interaction with    │
                              │ Phone                     │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ 🔴 FLAG DEVICE IN USE     │
                              │ POST to container         │
                              │ Status: IN_USE            │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Start time tracking       │
                              │ Start: 14:23:15.123       │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Log item sensor ON        │
                              │ "I008 Phone ON"           │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Accelerate virtual time   │
                              │ 1.0x → 30.0x (5 min task) │
                              └─────────────┬─────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 4: INTERACTION ACTIVE                       │
└─────────────────────────────────────────────────────────────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Actor using Phone         │
                              │ Time passing (accelerated)│
                              │ Real: 10.5s               │
                              │ Virtual: 5.5 min          │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Continuously monitor:     │
                              │ - Actor position          │
                              │ - Container health        │
                              │ - Time elapsed            │
                              └─────────────┬─────────────┘
                                            │
                                            ├─── Actor moves away? ─┐
                                            │                        │
                                            │                    ▼ YES
                                            │        ┌────────────────────┐
                                            │        │ End interaction    │
                                            │        │ (distance-based)   │
                                            │        └────────┬───────────┘
                                            │                 │
                                            │                 │
                              NO (staying)  │                 │
                                            └─────────────────┘
                                            │
                                            ▼
                              ┌─────────────────────────┐
                              │ Task complete?          │
                              └─────────────┬───────────┘
                                            │
                                            ▼ YES
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE 5: END INTERACTION                         │
└─────────────────────────────────────────────────────────────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ End interaction with Phone│
                              │ End: 14:28:45.456         │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ 🟢 UNFLAG DEVICE          │
                              │ POST to container         │
                              │ Status: AVAILABLE         │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Stop time tracking        │
                              │ Duration: 10.5s real      │
                              │          330s virtual     │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Log item sensor OFF       │
                              │ "I008 Phone OFF"          │
                              └─────────────┬─────────────┘
                                            │
                              ┌─────────────▼─────────────┐
                              │ Reset time acceleration   │
                              │ 30.0x → 1.0x              │
                              └─────────────┬─────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PHASE 6: LOGGING & EXPORT                       │
└─────────────────────────────────────────────────────────────────────┘
                                            │
                    ┌───────────────────────┼──────────────────────┐
                    │                       │                      │
                    ▼                       ▼                      ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │ item_sensor_log  │  │ time_tracking    │  │ device_docker    │
        │      .txt         │  │     _log.json    │  │  _tracking.json  │
        │                  │  │                  │  │                  │
        │ I008 Phone ON    │  │ "Make a phone    │  │ "Phone": {       │
        │ I008 Phone OFF   │  │  call": {        │  │   "in_use": false│
        │                  │  │   "real": 10.5s  │  │   "healthy": true│
        │ CASAS format     │  │   "virtual": 330s│  │   "serial": ...  │
        └──────────────────┘  └──────────────────┘  └──────────────────┘
                    │                       │                      │
                    └───────────────────────┼──────────────────────┘
                                            │
                                            ▼
                              ┌─────────────────────────┐
                              │ Print session summary   │
                              │ - Time stats            │
                              │ - Interaction stats     │
                              │ - Device stats          │
                              │ - Docker stats          │
                              └─────────────┬───────────┘
                                            │
                                            ▼
                              ┌─────────────────────────┐
                              │ ✅ Task complete!       │
                              │ Move to next task       │
                              └─────────────────────────┘
```

## Key Decision Points

### 1. Distance Check
```
Distance > 2.0m:  Set as target, wait for actor to approach
Distance ≤ 2.0m:  Device reached, proceed to health check
```

### 2. Container Health Check
```
HTTP 200 OK:      Container healthy, allow interaction
HTTP error:       Container unhealthy, block interaction
Timeout/Error:    Container unreachable, block interaction
```

### 3. Interaction End Triggers
```
1. Task completed successfully
2. Task failed (max steps exceeded)
3. Actor moved away (distance-based)
4. Manual end (edge case)
```

## State Transitions

```
IDLE → TARGETING → REACHED → HEALTH_CHECK → INTERACTING → ENDING → LOGGED
```

### IDLE
- No active task
- Waiting for task assignment

### TARGETING
- Device detected beyond interaction range
- Actor navigating closer
- Console: "🎯 TARGET SET: Phone (3.5m away - NEED TO GET CLOSER)"

### REACHED
- Actor within 2.0m of device
- Ready for health check
- Console: "✅ DEVICE REACHED: Phone (1.8m away)"

### HEALTH_CHECK
- Querying Docker container status
- Checking if device is available

### INTERACTING
- Active interaction in progress
- Time tracking active
- Device flagged as IN USE in Docker
- Console: "🔴 Device Phone FLAGGED as IN USE"

### ENDING
- Interaction stopping
- Time tracking stopping
- Device being unflagged
- Console: "🟢 Device Phone FLAGGED as AVAILABLE"

### LOGGED
- All data exported to log files
- System ready for next task

## Error Handling Paths

```
Container Unhealthy:
  ├─→ Skip interaction
  ├─→ Log warning
  └─→ Move to next task

Actor Moves Away:
  ├─→ End interaction immediately
  ├─→ Mark task as incomplete
  └─→ Log duration achieved

Max Steps Exceeded:
  ├─→ Force end interaction
  ├─→ Mark task as failed
  └─→ Export partial logs
```

## Time Tracking Details

```
Start Time (real):     14:23:15.123
Start Time (virtual):  14:23:15.123

Time Scale:            30.0x

Real Duration:         10.5 seconds
Virtual Duration:      315 seconds (5.25 minutes)

End Time (real):       14:23:25.623
End Time (virtual):    14:28:30.123
```

## Docker Communication

```
Health Check:
  GET http://localhost:8001/health
  Response: 200 OK

Flag IN USE:
  POST http://localhost:8001/api/device/ABC123/state
  Body: {"state": "in_use"}

Flag AVAILABLE:
  POST http://localhost:8001/api/device/ABC123/state
  Body: {"state": "available"}
```

## Log File Generation

```
During Interaction:
  - Real-time item sensor events (ON/OFF)
  - Time tracking updates
  - Docker state changes

After Interaction:
  - Final duration calculation
  - Export all data to JSON
  - Print summary statistics
```

## Success Metrics

✅ Agent reaches device (distance ≤ 2.0m)  
✅ Container health verified before interaction  
✅ Device flagged IN USE during interaction  
✅ Time tracking accurate (real + virtual)  
✅ Device unflagged AVAILABLE after interaction  
✅ All 3 log files generated correctly  
