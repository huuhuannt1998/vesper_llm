# 🏠 VESPER Smart Home Device Name Mapping Reference

## Overview
This document shows how device names in the Blender addon map to Docker container names for testing purposes.

## Core Docker Containers (Backend Services)

| Device Type | Container Name | Port | Purpose |
|-------------|----------------|------|---------|
| motion-sensor | testbed-motion-sensor | :8001 | Motion detection devices |
| item-sensor | testbed-item-sensor | :8002 | Item tracking sensors |
| appliance-controller | testbed-appliance-controller | :8003 | Smart device control |
| casas-dataset-manager | testbed-casas-dataset-manager | :8004 | Data collection |
| thermostat | testbed-thermostat | :8005 | Temperature control |

## Device Type Mappings

### Blender Addon → Backend Container
The Blender addon offers 27 device types that map to the 5 core backend containers:

#### Core Sensors (Direct Mapping)
- `thermostat` → `testbed-thermostat` (:8005)
- `motion-sensor` → `testbed-motion-sensor` (:8001)
- `item-sensor` → `testbed-item-sensor` (:8002)
- `appliance-controller` → `testbed-appliance-controller` (:8003)
- `casas-dataset-manager` → `testbed-casas-dataset-manager` (:8004)

#### Advanced Sensors → Motion Sensor Backend
- `door-sensor` → `testbed-motion-sensor` (:8001)
- `light-sensor` → `testbed-motion-sensor` (:8001)
- `smoke-detector` → `testbed-motion-sensor` (:8001)
- `water-leak-sensor` → `testbed-motion-sensor` (:8001)
- `security-camera` → `testbed-motion-sensor` (:8001)
- `glass-break-sensor` → `testbed-motion-sensor` (:8001)
- `vibration-sensor` → `testbed-motion-sensor` (:8001)
- `occupancy-counter` → `testbed-motion-sensor` (:8001)

#### Environmental Sensors → Thermostat Backend
- `temperature-sensor` → `testbed-thermostat` (:8005)
- `humidity-sensor` → `testbed-thermostat` (:8005)
- `air-quality-sensor` → `testbed-thermostat` (:8005)
- `weather-station` → `testbed-thermostat` (:8005)
- `uv-sensor` → `testbed-thermostat` (:8005)
- `energy-monitor` → `testbed-thermostat` (:8005)

#### Smart Controls → Appliance Controller Backend
- `smart-switch` → `testbed-appliance-controller` (:8003)
- `smart-dimmer` → `testbed-appliance-controller` (:8003)
- `smart-lock` → `testbed-appliance-controller` (:8003)
- `garage-door` → `testbed-appliance-controller` (:8003)
- `panic-button` → `testbed-appliance-controller` (:8003)
- `smart-tv` → `testbed-appliance-controller` (:8003)
- `coffee-maker` → `testbed-appliance-controller` (:8003)
- `robot-vacuum` → `testbed-appliance-controller` (:8003)
- `air-purifier` → `testbed-appliance-controller` (:8003)

## Testing Guide

### 1. Device Creation Testing
When you create a device in Blender:
1. Select device type from the 27 available options
2. Choose location/room
3. The addon will show you which Docker container it maps to
4. Test communication with the mapped container

### 2. Container Status Check
```powershell
# Check all running containers
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"

# Check specific device container
docker logs testbed-motion-sensor
docker logs testbed-thermostat
# etc.
```

### 3. API Testing
```powershell
# Test device creation (example for motion sensor)
Invoke-RestMethod -Uri "http://localhost:8088/spawn_device" -Method POST -ContentType "application/json" -Body '{"device_type": "motion-sensor", "username": "admin", "config_type": "medium_house_efficient"}'

# Check device container directly
Invoke-RestMethod -Uri "http://localhost:8001/status"
```

## Blender Addon Features

### Enhanced Device Spawning Dialog
- 27 device types with emoji categorization
- Location/room selection dropdown
- Docker container mapping display
- Real-time backend type mapping info

### Docker Reference Panel
- Collapsed panel in VESPER category
- Shows all active container mappings
- Device type mapping examples
- Port information for testing

## Device Serial Number Patterns

Each backend type has a unique serial prefix:
- `VST-` - Thermostat devices
- `VSM-` - Motion sensor devices  
- `VSI-` - Item sensor devices
- `VSA-` - Appliance controller devices
- `VSD-` - Dataset manager devices

Example: `VSM-05CB-2BD2-3F1E` (Motion sensor device)

## Notes for Testing

1. **Container Dependencies**: Ensure all 5 core containers are running before testing
2. **Network Configuration**: All containers share the `testbed-network` 
3. **Backend API**: The backend console (`testbed-backend-console`) orchestrates device creation
4. **SmartThings Integration**: Uses ngrok tunnel for external connectivity
5. **Device Mapping**: Advanced device types inherit behavior from core backend types

## Troubleshooting

- **Connection Errors**: Check if static services are running with `docker ps`
- **Device Creation Fails**: Verify backend console is accessible at `localhost:8088`
- **SmartThings Issues**: Check ngrok tunnel status at `localhost:4040`
- **Missing Containers**: Run `docker-compose up -d` to start all services

---
*Last updated: Enhanced addon with comprehensive device type support and Docker container mapping*
