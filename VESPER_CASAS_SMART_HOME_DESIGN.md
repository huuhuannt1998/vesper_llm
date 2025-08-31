# VESPER-CASAS Virtual Smart Home Integration Design

## Overview

Extend the existing virtual-interaction system to support all CASAS sensor types, creating a comprehensive virtual smart home environment that:

1. **Virtual Devices in VESPER/Blender**: Simulated sensors and appliances that respond to VLM actions
2. **SmartThings Mirror**: Virtual devices automatically created and synchronized in SmartThings
3. **CASAS Ground Truth**: Use real CASAS dataset patterns as validation benchmarks
4. **Research Dataset Generation**: Create comprehensive datasets for VLM evaluation

## Architecture Extension

```
┌─────────────────────────────────────────────────────────────────┐
│                    SmartThings Cloud                             │
│        (Virtual CASAS Devices: Motion, Lights, Appliances)       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  ngrok  │
                    │ tunnel  │
                    └────┬────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  CASAS Cloud Server                              │
│           (Device Registry, State Sync, OAuth)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │ Docker Network
┌────────────────────────┼────────────────────────────────────────┐
│   VIRTUAL SMART HOME ECOSYSTEM                                   │
│                        │                                         │
│   ┌─────────────┐     │     ┌─────────────┐                     │
│   │   Motion    │◄────┼────►│ Environment │                     │
│   │  Sensors    │     │     │  Simulator  │                     │
│   │ (M01-M26)   │     │     │             │                     │
│   └─────────────┘     │     └─────────────┘                     │
│                       │                                         │
│   ┌─────────────┐     │     ┌─────────────┐                     │
│   │ Item/Object │◄────┼────►│ Appliance   │                     │
│   │  Sensors    │     │     │ Controllers │                     │
│   │ (I01-I08)   │     │     │ (Stove,Sink)│                     │
│   └─────────────┘     │     └─────────────┘                     │
│                       │                                         │
│   ┌─────────────┐     │     ┌─────────────┐                     │
│   │ Door/Water/ │◄────┼────►│ VESPER BGE  │                     │
│   │   Phone     │     │     │ Integration │                     │
│   │ (D01,AD1,*) │     │     │   Layer     │                     │
│   └─────────────┘     │     └─────────────┘                     │
└────────────────────────┼────────────────────────────────────────┘
                         │
                    ┌────▼────┐         ┌─────────┐
                    │  Redis  │         │CASAS    │
                    │Database │◄────────┤Dataset  │ ──► Research
                    └─────────┘         │Manager  │     Analysis
                                       └─────────┘
```

## CASAS Device Types to Implement

### 1. Motion Sensors (M01-M26)
- **Virtual Device**: PIR motion detectors in Blender zones
- **SmartThings**: Motion sensor capabilities
- **States**: motion/no-motion with timestamps
- **CASAS Mapping**: ON/OFF events

### 2. Item/Object Sensors (I01-I08)
- **Virtual Device**: Smart object trackers
- **SmartThings**: Contact sensor or custom capability
- **States**: PRESENT/ABSENT when objects moved
- **CASAS Mapping**: 
  - I01: oatmeal container
  - I02: raisins container  
  - I03: brown sugar container
  - I04: bowl
  - I05: measuring spoon
  - I06: medicine container
  - I07: pot
  - I08: phone book

### 3. Door Sensors (D01)
- **Virtual Device**: Smart door/cabinet sensors
- **SmartThings**: Contact sensor capability
- **States**: OPEN/CLOSE
- **CASAS Mapping**: Kitchen cabinet door

### 4. Water Sensors (AD1-A, AD1-B)
- **Virtual Device**: Smart water flow sensors
- **SmartThings**: Water sensor or custom capability
- **States**: Flow rate values (0-100)
- **CASAS Mapping**: Hot/cold water at kitchen sink

### 5. Burner Sensor (AD1-C)
- **Virtual Device**: Smart stove controller
- **SmartThings**: Switch or thermostat capability
- **States**: Heat level (0-100)
- **CASAS Mapping**: Stove burner intensity

### 6. Phone Sensor (*)
- **Virtual Device**: Smart phone base station
- **SmartThings**: Switch or custom capability
- **States**: PICKUP/HANGUP
- **CASAS Mapping**: Phone usage events

## Implementation Strategy

### Phase 1: Core Device Framework (Week 1)
1. **Extend cloud server** to support multiple device types
2. **Create base device classes** for each CASAS sensor type
3. **Implement SmartThings capabilities** for all device types
4. **Set up Docker containers** for device fleet management

### Phase 2: VESPER Integration (Week 2)
1. **BGE sensor integration** - Connect Blender collision/interaction events to virtual devices
2. **Real-time state sync** - Update SmartThings when VLM interacts with objects
3. **CASAS event logging** - Generate CASAS-format CSV files from device events
4. **Apartment layout mapping** - Position virtual devices according to Chinook floorplan

### Phase 3: Dataset Generation (Week 3)
1. **CASAS pattern replay** - Use ground truth data to validate device responses
2. **VLM task execution** - Run ADL tasks and collect comprehensive device data
3. **Comparative analysis** - Generate metrics comparing VLM vs human patterns
4. **Error injection testing** - Test VLM error detection using CASAS error scenarios

### Phase 4: Research Framework (Week 4)
1. **Automated evaluation pipeline** - Batch processing of VLM task executions
2. **Statistical analysis tools** - Generate research-ready metrics and visualizations
3. **Dataset publishing** - Package results for academic use
4. **SmartThings app** - User interface for monitoring virtual smart home

## Technical Implementation Details

### Device Container Structure
```
virtual-interaction/
├── motion-sensor/           # M01-M26 motion detectors
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── item-sensor/            # I01-I08 object trackers  
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── door-sensor/            # D01 cabinet door
├── water-sensor/           # AD1-A/B sink water
├── burner-controller/      # AD1-C stove burner
├── phone-controller/       # * phone base
├── casas-environment/      # Environment simulator for all devices
└── casas-dataset-manager/  # CASAS data processing and comparison
```

### CASAS Event Bus
```python
class CASASEventBus:
    """Central event collection and SmartThings sync"""
    
    def __init__(self):
        self.redis_client = redis.Redis()
        self.smartthings_client = SmartThingsClient()
        
    async def publish_sensor_event(self, sensor_id: str, message: str):
        """Publish CASAS format event"""
        event = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "sensor": sensor_id,
            "message": message,
            "timestamp": time.time()
        }
        
        # Store in Redis
        await self.redis_client.lpush(f"casas:events", json.dumps(event))
        
        # Update SmartThings
        await self.smartthings_client.update_device(sensor_id, message)
        
        # Log to CSV for CASAS comparison
        await self.log_to_casas_csv(event)
```

### VLM Integration Points
```python
class VESPERCASASBridge:
    """Bridge between VESPER BGE and virtual devices"""
    
    def on_actor_movement(self, position: Tuple[float, float]):
        """Trigger motion sensors based on actor position"""
        for motion_sensor in self.motion_sensors:
            if motion_sensor.is_in_detection_zone(position):
                motion_sensor.trigger_motion()
                
    def on_object_interaction(self, object_name: str, action: str):
        """Handle object pickup/putdown events"""
        if object_name in self.item_sensors:
            sensor = self.item_sensors[object_name]
            if action in ["pickup", "grab"]:
                sensor.set_state("ABSENT")
            elif action in ["putdown", "place"]:
                sensor.set_state("PRESENT")
                
    def on_appliance_control(self, appliance: str, action: str, value: float = None):
        """Handle appliance interactions"""
        if appliance == "stove":
            self.burner_controller.set_heat_level(value or 0)
        elif appliance == "sink":
            self.water_sensors["hot"].set_flow_rate(value or 0)
            self.water_sensors["cold"].set_flow_rate(value or 0)
```

## Research Applications

### 1. VLM Spatial Intelligence
- **Question**: How accurately can VLM navigate apartment layouts?
- **Measurement**: Motion sensor activation patterns vs CASAS ground truth
- **Metrics**: Path efficiency, room transition accuracy, spatial memory

### 2. Object Recognition & Interaction  
- **Question**: Can VLM correctly identify and manipulate household objects?
- **Measurement**: Item sensor activation sequences during ADL tasks
- **Metrics**: Object identification accuracy, interaction sequence fidelity

### 3. Task Planning & Execution
- **Question**: How well does VLM understand multi-step household tasks?
- **Measurement**: Complete sensor event sequences vs CASAS task patterns
- **Metrics**: Task completion rate, step ordering accuracy, timing correlation

### 4. Error Detection & Recovery
- **Question**: Can VLM detect and correct procedural errors?
- **Measurement**: Response to CASAS error scenarios (water left on, etc.)
- **Metrics**: Error detection rate, correction success rate, recovery strategies

### 5. Smart Home Integration
- **Question**: How effectively can VLM control smart home ecosystems?
- **Measurement**: SmartThings device state changes during VLM tasks
- **Metrics**: Device control accuracy, automation trigger success, user intent understanding

## Expected Deliverables

### 1. Virtual Smart Home Platform
- Full CASAS sensor ecosystem in virtual environment
- Real-time SmartThings synchronization
- Scalable device management system

### 2. VESPER-CASAS Dataset
- VLM-generated ADL task executions
- Comprehensive sensor event logs
- SmartThings device interaction histories
- Comparative analysis against CASAS ground truth

### 3. Research Framework
- Automated VLM evaluation pipeline
- Statistical analysis and visualization tools
- Academic dataset for community use

### 4. Smart Home Application
- SmartThings app for monitoring virtual environment
- Real-time visualization of VLM actions
- Manual control interface for testing

This comprehensive approach creates a unique research platform that bridges embodied AI (VLM in virtual environment), IoT (SmartThings ecosystem), and established ADL research (CASAS dataset), enabling unprecedented evaluation of VLM capabilities in realistic smart home scenarios.
