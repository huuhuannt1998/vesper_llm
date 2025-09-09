# Motion Sensor Integration Guide

## Overview

This guide covers integration of the VESPER Motion Sensor Detection System with various components of the VESPER LLM ecosystem.

## Blender BGE Integration

### 1. Basic Setup

```python
# In your BGE script
import sys
import os

# Add motion_sensors to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from motion_sensors import quick_setup, update_motion_detection

# Initialize once
detector = quick_setup()

# In main game loop (every frame)
def main():
    update_motion_detection()
```

### 2. VESPER LLM Navigation Integration

Update `llm_bge_navigation.py` to include motion sensor detection:

```python
# Add to imports
from motion_sensors import initialize_motion_detection, update_motion_detection

# Add to main() function initialization
if not hasattr(bge.logic, "motion_detector"):
    bge.logic.motion_detector = initialize_motion_detection()
    print("🔍 Motion detection initialized")

# Add to main game loop
def main():
    # ... existing navigation code ...
    
    # Update motion detection every frame
    if hasattr(bge.logic, "motion_detector"):
        update_motion_detection()
    
    # ... rest of navigation code ...
```

### 3. Device Manager Integration

Update the VESPER smart home addon to use the new motion sensor system:

```python
# In blender/addons/vesper_smart_home/__init__.py

# Import motion sensor system
from motion_sensors import register_motion_sensor_detection

# Update add_motion_sensor method
def add_motion_sensor(self, sensor_id: str, room: str, position: Vector, orientation: float = 0.0):
    # ... existing Docker communication code ...
    
    # Register with realistic detection system
    register_motion_sensor_detection(sensor_id, position, room, orientation)
    
    return True
```

## Docker Integration

### 1. Motion Sensor Service Integration

The motion sensor detection system integrates with existing Docker services:

```python
# Connect to motion sensor service
response = requests.post(f"{base_urls['motion']}/configure", json={
    "detection_zone": {"x": position.x, "y": position.y, "radius": 5.0},
    "room_location": room,
    "sensitivity": 1.0,
    "cooldown_period": 3.0
})
```

### 2. SmartThings Integration

Configure SmartThings connectivity:

```python
# In DeviceManager class
def update_smartthings_device(self, device_id: str, data: dict):
    headers = {"Authorization": f"Bearer {smartthings_token}"}
    requests.put(
        f"https://api.smartthings.com/v1/devices/{device_id}/status",
        json=data, 
        headers=headers
    )
```

## CASAS Dataset Integration

### 1. Motion Sensor Event Generation

Integrate with CASAS dataset generation:

```python
from motion_sensors import get_motion_detection_status
from casas_testbed.vesper_casas_dataset_generator import log_sensor_event

# In navigation loop
status = get_motion_detection_status()
for sensor_id, sensor_data in status['sensors'].items():
    if sensor_data['detecting']:
        log_sensor_event(sensor_id, "motion", "ON", sensor_data['room'])
```

### 2. Ground Truth Validation

Compare VLM navigation with motion sensor patterns:

```python
# Collect motion sensor data during VLM navigation
motion_events = []
for sensor_id, sensor_data in get_motion_detection_status()['sensors'].items():
    if sensor_data['detection_count'] > 0:
        motion_events.append({
            'sensor': sensor_id,
            'room': sensor_data['room'],
            'count': sensor_data['detection_count']
        })

# Compare with CASAS ground truth patterns
validate_motion_patterns(motion_events, casas_ground_truth)
```

## Web Console Integration

### 1. Device Status Display

Add motion sensor status to web console:

```javascript
// In backend web console
async function updateMotionSensorStatus() {
    const response = await fetch('/api/motion-sensors/status');
    const status = await response.json();
    
    document.getElementById('sensors-detecting').textContent = 
        status.sensors_detecting;
    document.getElementById('total-detections').textContent = 
        Object.values(status.sensors).reduce((sum, s) => sum + s.detection_count, 0);
}
```

### 2. Real-time Monitoring

WebSocket integration for live updates:

```python
# Backend WebSocket handler
@websocket.route('/ws/motion-sensors')
async def motion_sensor_websocket(websocket, path):
    while True:
        status = get_motion_detection_status()
        await websocket.send(json.dumps(status))
        await asyncio.sleep(1)
```

## Custom Layouts Integration

### 1. Load Custom Sensor Layouts

```python
from motion_sensors.configs import load_sensor_layout

# Load predefined layout
layout = load_sensor_layout("medium_house")
for sensor in layout['sensors']:
    register_motion_sensor_detection(
        sensor['id'], 
        Vector(sensor['position']['x'], sensor['position']['y'], sensor['position']['z']),
        sensor['room'],
        sensor['orientation']
    )
```

### 2. Dynamic Sensor Placement

```python
# Analyze Blender scene and place sensors automatically
def auto_place_sensors(scene):
    rooms = analyze_scene_rooms(scene)
    optimal_positions = calculate_optimal_sensor_positions(rooms)
    
    for pos in optimal_positions:
        register_motion_sensor_detection(
            pos['id'], pos['position'], pos['room'], pos['orientation']
        )
```

## Performance Optimization

### 1. Frame Rate Management

```python
# Optimize for different frame rates
FRAME_SKIP = 2  # Update every 2nd frame for 30fps operation

frame_counter = 0
def optimized_update():
    global frame_counter
    frame_counter += 1
    
    if frame_counter % FRAME_SKIP == 0:
        update_motion_detection()
```

### 2. Sensor Count Optimization

```python
# Limit active sensors based on Actor location
def optimize_active_sensors(actor_position):
    status = get_motion_detection_status()
    
    for sensor_id, sensor_data in status['sensors'].items():
        distance = (actor_position - Vector(sensor_data['position'])).length
        # Deactivate distant sensors to save CPU
        if distance > 10.0:  # 10 meter threshold
            deactivate_sensor(sensor_id)
```

## Debugging and Troubleshooting

### 1. Debug Visualization

```python
# Enable debug output
def debug_motion_detection():
    status = get_motion_detection_status()
    
    print("🔍 Motion Detection Debug:")
    for sensor_id, data in status['sensors'].items():
        if data['detecting']:
            print(f"   🔴 {sensor_id}: ACTIVE in {data['room']}")
```

### 2. Performance Monitoring

```python
import time

def monitor_performance():
    start_time = time.time()
    update_motion_detection()
    update_time = (time.time() - start_time) * 1000
    
    if update_time > 5.0:  # Alert if > 5ms
        print(f"⚠️ Motion detection slow: {update_time:.1f}ms")
```

## Testing Integration

### 1. Unit Tests

```python
import unittest
from motion_sensors import MotionSensorDetector

class TestMotionDetection(unittest.TestCase):
    def setUp(self):
        self.detector = MotionSensorDetector()
    
    def test_sensor_registration(self):
        self.detector.register_motion_sensor("TEST01", Vector((0, 0, 2)), "test_room")
        status = self.detector.get_detection_status()
        self.assertEqual(status['total_sensors'], 1)
```

### 2. Integration Tests

```python
def test_blender_integration():
    """Test motion detection in actual BGE environment"""
    # Load test scene
    # Place Actor at known position
    # Verify sensor detection
    pass
```

## Production Deployment

### 1. Configuration Management

```python
# Load production configuration
import json
with open('motion_sensors_prod.json', 'r') as f:
    prod_config = json.load(f)

# Deploy sensors from configuration
deploy_sensors_from_config(prod_config)
```

### 2. Monitoring and Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('motion_sensors')

def log_detection_event(sensor_id, event_type, room):
    logger.info(f"Motion detection: {sensor_id} {event_type} in {room}")
```

This integration guide provides comprehensive coverage for incorporating the motion sensor system into all aspects of the VESPER LLM ecosystem.
