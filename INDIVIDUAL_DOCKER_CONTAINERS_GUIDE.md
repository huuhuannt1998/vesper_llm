# 🐳 Individual Docker Container Management for Virtual Devices

## Overview
The enhanced VESPER Smart Home addon now creates **individual Docker containers** for each virtual device spawned from Blender. Each device gets its own dedicated container with a unique name based on the device type and serial number.

## How It Works

### 🎯 **Individual Container Creation**
When you spawn a virtual device in Blender:

1. **Backend Registration**: Device registered with backend console API
2. **Serial Number Generation**: Unique serial (e.g., `VSM-05CB-2BD2-3F1E`)
3. **Container Creation**: Individual Docker container created
4. **Port Assignment**: Dynamic port allocation starting from 9000
5. **Visual Representation**: Device appears in Blender with container info

### 📦 **Container Naming Convention**
```
{device-type}-{serial-number}
```

**Examples:**
- `motion-sensor-VSM-05CB-2BD2-3F1E`
- `coffee-maker-VSA-F7F2-6AC9-820F`
- `temperature-sensor-VST-4E4D-D0E3-8A40`

## Device Type Mapping

### 🏠 **Core Device Types → Docker Images**
| Device Type | Docker Image | Port Range |
|-------------|--------------|------------|
| `thermostat` | `virtual-interaction-thermostat` | 9000+ |
| `motion-sensor` | `virtual-interaction-motion-sensor` | 9000+ |
| `item-sensor` | `virtual-interaction-item-sensor` | 9000+ |
| `appliance-controller` | `virtual-interaction-appliance-controller` | 9000+ |
| `casas-dataset-manager` | `virtual-interaction-casas-dataset-manager` | 9000+ |

### 🔄 **Advanced Device Mapping**
Advanced device types are mapped to core backend containers:

| Advanced Type | Maps To | Container Example |
|---------------|---------|-------------------|
| `coffee-maker` | `appliance-controller` | `coffee-maker-VSA-1234-5678-9ABC` |
| `door-sensor` | `motion-sensor` | `door-sensor-VSM-ABCD-EFGH-1234` |
| `temperature-sensor` | `thermostat` | `temperature-sensor-VST-9876-5432-DCBA` |
| `smart-switch` | `appliance-controller` | `smart-switch-VSA-4321-8765-FEDC` |

## Usage Guide

### 1. **Spawning Virtual Devices**
1. Open Blender with VESPER addon enabled
2. Go to VESPER panel → "Spawn Virtual Device"
3. Select device type (27 options available)
4. Choose location/room
5. **Result**: 
   - Device registered in backend
   - Individual Docker container created
   - Visual device appears in Blender
   - Container info shown in UI

### 2. **Container Information Display**
When you select a virtual device in Blender, the VESPER panel shows:
```
Virtual: VSM-05CB-2BD2-3F1E
Type: motion-sensor
Config: medium_house_efficient
User: admin

🐳 Docker Container:
Name: motion-sensor-VSM-05CB-2BD2-3F1E
Port: 9001
```

### 3. **Managing Containers**

#### **List All Individual Containers**
- Click "Containers" button in VESPER panel
- Shows only individual device containers (not testbed- containers)
- Displays container name, image, ports, and status

#### **Delete Virtual Device**
- Select virtual device in Blender
- Click "Delete Virtual Device"
- **Both** backend device and Docker container are removed

#### **Cleanup All**
- Click "Cleanup All" to remove all virtual devices
- Removes all individual containers and backend registrations

## Docker Commands

### 🔍 **Manual Container Management**

#### **List Individual Device Containers**
```powershell
docker ps --filter "name=motion-sensor-" --filter "name=coffee-maker-" --filter "name=door-sensor-"
```

#### **Check Specific Container**
```powershell
# Check logs for specific device
docker logs motion-sensor-VSM-05CB-2BD2-3F1E

# Check container status
docker inspect coffee-maker-VSA-F7F2-6AC9-820F
```

#### **Connect to Container**
```powershell
# Access container shell
docker exec -it motion-sensor-VSM-05CB-2BD2-3F1E /bin/bash

# Test device API directly
Invoke-RestMethod -Uri "http://localhost:9001/health"
```

#### **Manual Container Cleanup**
```powershell
# Stop and remove specific container
docker stop motion-sensor-VSM-05CB-2BD2-3F1E
docker rm motion-sensor-VSM-05CB-2BD2-3F1E

# Remove all individual device containers
docker ps -a --filter "name=-VS" --format "{{.Names}}" | ForEach-Object { docker stop $_; docker rm $_ }
```

## Network Configuration

### 🌐 **Container Networking**
- **Network**: All containers join `testbed-network`
- **Port Mapping**: Dynamic allocation starting from 9000
- **Host Access**: Each container accessible via `localhost:{port}`
- **Inter-Container**: Containers can communicate via container names

### 📡 **Port Management**
- **Static Services**: Ports 8001-8005 (testbed- containers)
- **Backend Console**: Port 8088
- **Cloud Server**: Port 8081
- **Individual Devices**: Ports 9000+ (auto-assigned)

## Environment Variables

Each individual container receives:
```bash
DEVICE_SERIAL={serial_number}    # e.g., VSM-05CB-2BD2-3F1E
DEVICE_TYPE={original_type}      # e.g., motion-sensor, coffee-maker
```

## Testing & Debugging

### 🧪 **Device Testing Workflow**

1. **Create Device in Blender**
   ```
   Spawn → motion-sensor → living_room
   Result: motion-sensor-VSM-05CB-2BD2-3F1E on port 9001
   ```

2. **Test Container Direct Access**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:9001/health"
   ```

3. **Test Device Functionality**
   ```powershell
   # Trigger motion
   Invoke-RestMethod -Uri "http://localhost:9001/manual_trigger" -Method POST -ContentType "application/json" -Body '{"motion": "active"}'
   ```

4. **Monitor Container Logs**
   ```powershell
   docker logs motion-sensor-VSM-05CB-2BD2-3F1E -f
   ```

### 🐛 **Troubleshooting**

#### **Container Creation Fails**
- Check Docker is running
- Verify images exist (`docker images | grep virtual-interaction`)
- Check port availability
- Review container logs

#### **Port Conflicts**
- Use different starting port in `find_available_port()`
- Check `docker ps` for port usage
- Manually assign specific ports if needed

#### **Network Issues**
- Verify `testbed-network` exists: `docker network ls`
- Check container network: `docker inspect {container_name}`

## Advanced Features

### 🔧 **Container Lifecycle Management**
- **Auto-cleanup**: Failed container creation triggers backend cleanup
- **Graceful shutdown**: Containers stopped before removal
- **Error handling**: Partial failures logged with specific error details

### 📊 **Resource Monitoring**
```powershell
# Monitor resource usage
docker stats motion-sensor-VSM-05CB-2BD2-3F1E

# Check container health
docker exec motion-sensor-VSM-05CB-2BD2-3F1E curl localhost:8000/health
```

### 🔄 **Integration Points**
- **Backend Console**: Manages device logic and state
- **SmartThings**: Devices discoverable via ngrok tunnel
- **Blender UI**: Real-time container status display
- **CASAS Dataset**: Individual containers can contribute to research data

## Benefits

### ✅ **Advantages of Individual Containers**
1. **Isolation**: Each device runs independently
2. **Scalability**: Add unlimited devices without conflicts
3. **Testing**: Direct access to each device API
4. **Debugging**: Individual container logs and monitoring
5. **Realistic Simulation**: Mirrors real IoT device deployment
6. **Custom Configuration**: Each device can have unique settings

### 🎯 **Use Cases**
- **Smart Home Simulation**: Create entire house layouts
- **IoT Testing**: Test device interactions and failures
- **Research**: Generate CASAS datasets with multiple devices
- **Development**: Debug individual device behaviors
- **Education**: Learn container orchestration and IoT concepts

---

**🚀 Ready to Use!** 
Restart Blender, spawn virtual devices, and watch individual Docker containers come to life for each device you create!
