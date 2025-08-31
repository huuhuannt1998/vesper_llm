# VESPER-CASAS Integration Guide

This document provides instructions for integrating the VESPER-CASAS virtual smart home testbed with the VESPER BGE navigation system for comprehensive VLM evaluation.

## Overview

The VESPER-CASAS testbed provides a complete virtual smart home environment that mirrors real CASAS sensor data, enabling researchers to evaluate VLM performance against ground truth human activity patterns.

## Architecture Components

### Virtual Sensor Network
- **Motion Sensors (M01-M26)**: Zone-based presence detection
- **Item Sensors (I01-I08)**: Object tracking for kitchen items
- **Appliance Controller**: Water, burner, door, and phone control
- **Dataset Manager**: Ground truth comparison and research analytics

### Integration Points

#### 1. VESPER BGE Navigation Interface
```python
# Example integration with VESPER BGE navigation
import requests
import json

class VESPERCASASBridge:
    def __init__(self, casas_base_url="http://localhost:8001"):
        self.motion_url = f"{casas_base_url}"
        self.item_url = "http://localhost:8002" 
        self.appliance_url = "http://localhost:8003"
        self.dataset_url = "http://localhost:8004"
    
    async def process_vlm_action(self, action_data):
        """Process VLM action and trigger appropriate sensors"""
        
        action_type = action_data.get("type")
        location = action_data.get("location")
        object_id = action_data.get("object")
        
        if action_type == "move_to":
            # Trigger motion sensors based on navigation path
            await self.trigger_motion_sequence(location)
        
        elif action_type == "interact_with":
            # Trigger item sensors for object interaction
            await self.trigger_item_interaction(object_id)
        
        elif action_type == "use_appliance":
            # Control appliances (water, burner, etc.)
            await self.control_appliance(object_id, action_data.get("state"))
    
    async def trigger_motion_sequence(self, target_location):
        """Trigger motion sensors along navigation path"""
        # Map location to motion sensor zones
        zone_mapping = {
            "kitchen": ["M01", "M02", "M03"],
            "living_room": ["M04", "M05"], 
            "bathroom": ["M06", "M07"],
            # Add more zones based on apartment layout
        }
        
        zones = zone_mapping.get(target_location, [])
        
        for zone in zones:
            response = requests.post(f"{self.motion_url}/trigger", json={
                "sensor_id": zone,
                "state": "ON"
            })
```

#### 2. CASAS Event Generation
```python
# Events are automatically generated in CASAS format
# Example: 2024-08-14 10:30:15.123 M01 ON
# This mirrors real CASAS dataset format for direct comparison
```

#### 3. Research Data Collection
```python
# Start task execution tracking
task_data = {
    "participant_id": "vesper_vlm_001",
    "task_id": 3,  # Cook oatmeal
    "task_name": "Cook oatmeal", 
    "error_type": "none",
    "start_time": "2024-08-14T10:30:00Z"
}

# Log task execution
requests.post("http://localhost:8004/task_execution", json=task_data)

# Request comparison with ground truth
comparison_request = {
    "vesper_session_id": "session_12345",
    "casas_reference_file": "cook_oatmeal_normal.csv",
    "task_id": 3,
    "participant_id": "vesper_vlm_001"
}

requests.post("http://localhost:8004/compare", json=comparison_request)
```

## Deployment Instructions

### 1. Setup CASAS Ground Truth Data
```bash
# Create directory for CASAS ground truth files
mkdir -p ./data/casas_ground_truth

# Place CASAS CSV files in this directory:
# - cook_oatmeal_normal.csv
# - cook_oatmeal_error.csv
# - wash_hands_normal.csv
# - phone_call_normal.csv
# - eat_meal_normal.csv
# - clean_dishes_normal.csv
```

### 2. Deploy CASAS Virtual Environment
```bash
# Deploy all CASAS services
docker-compose -f docker-compose.casas.yml up -d

# Verify all services are running
docker-compose -f docker-compose.casas.yml ps

# Check service health
curl http://localhost:8001/health  # Motion sensors
curl http://localhost:8002/health  # Item sensors  
curl http://localhost:8003/health  # Appliance controller
curl http://localhost:8004/health  # Dataset manager
```

### 3. Integration with VESPER BGE

#### Update VESPER BGE Navigation Script
```python
# In your VESPER BGE navigation script, add CASAS integration:

import sys
sys.path.append('/path/to/vesper_llm/virtual-interaction')

from vesper_casas_bridge import VESPERCASASBridge

class EnhancedVESPERNavigation:
    def __init__(self):
        self.casas_bridge = VESPERCASASBridge()
        # Existing VESPER initialization...
    
    async def execute_vlm_instruction(self, instruction):
        """Execute VLM instruction with CASAS sensor tracking"""
        
        # Parse VLM instruction
        action = self.parse_instruction(instruction)
        
        # Execute in BGE
        await self.execute_bge_action(action)
        
        # Trigger CASAS sensors
        await self.casas_bridge.process_vlm_action(action)
        
        return action
```

## Research Evaluation Workflow

### 1. Task Dataset Preparation
```python
# CASAS task definitions
casas_tasks = {
    1: {"name": "Make phone call", "sensors": ["*", "M01", "M02"]},
    2: {"name": "Wash hands", "sensors": ["AD1-A", "AD1-B", "M06", "M07"]},
    3: {"name": "Cook oatmeal", "sensors": ["I01", "I02", "I03", "AD1-C", "M01"]},
    4: {"name": "Eat meal", "sensors": ["I03", "I04", "I07", "M04", "M05"]}, 
    5: {"name": "Clean dishes", "sensors": ["AD1-A", "AD1-B", "I07", "I08"]}
}
```

### 2. VLM Evaluation Loop
```python
async def evaluate_vlm_on_casas():
    """Run VLM evaluation against CASAS tasks"""
    
    results = []
    
    for task_id, task_info in casas_tasks.items():
        # Present task to VLM
        instruction = f"Please {task_info['name']}"
        
        # Start CASAS session tracking
        session_id = f"vlm_eval_{task_id}_{int(time.time())}"
        
        # Execute with VLM
        start_time = time.time()
        success = await execute_vlm_task(instruction, session_id)
        duration = time.time() - start_time
        
        # Request comparison with ground truth
        comparison = await request_casas_comparison(
            session_id, 
            f"{task_info['name'].lower().replace(' ', '_')}_normal.csv",
            task_id
        )
        
        results.append({
            "task_id": task_id,
            "success": success,
            "duration": duration,
            "comparison": comparison
        })
    
    return results
```

### 3. Results Analysis
```python
# Get comparison results
comparison = requests.get(f"http://localhost:8004/comparison/{session_id}").json()

print(f"Overall Score: {comparison['overall_score']:.2f}")
print(f"Sequence Similarity: {comparison['sequence_similarity']['similarity_score']:.2f}")
print(f"Sensor Coverage: {comparison['sensor_coverage']['coverage_score']:.2f}")
print(f"Timing Score: {comparison['timing_analysis']['timing_score']:.2f}")

# Export dataset for further analysis
export_request = {
    "session_ids": [session_id],
    "format": "casas_csv",
    "include_comparison": True
}

response = requests.post("http://localhost:8004/export", json=export_request)
print(f"Dataset exported: {response.json()['filename']}")
```

## Key Features

### Automated Ground Truth Comparison
- Real-time comparison with CASAS reference data
- Sequence similarity analysis using edit distance
- Sensor coverage and timing pattern analysis
- Comprehensive scoring for VLM performance

### Research Data Export
- CASAS CSV format for compatibility with existing research
- JSON format for detailed analysis
- SmartThings format for cloud platform integration
- Automated timestamping and session management

### Scalable Evaluation
- Parallel VLM testing across multiple tasks
- Automated dataset generation for large-scale studies
- Statistical analysis of VLM vs human performance
- Error condition testing with modified scenarios

## SmartThings Integration

The virtual sensors automatically register with SmartThings cloud, enabling:
- Real-time monitoring via SmartThings app
- Integration with existing smart home automations
- Third-party platform connectivity
- Mobile device notifications for research tracking

## Troubleshooting

### Common Issues
1. **Services not starting**: Check Docker logs with `docker-compose logs [service]`
2. **Redis connection errors**: Ensure Redis is running first
3. **Missing ground truth data**: Verify CASAS CSV files are in correct directory
4. **BGE integration issues**: Check VESPER path configuration

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Check service status
curl http://localhost:8004/health

# View active sessions
curl http://localhost:8004/sessions

# List ground truth files  
curl http://localhost:8004/ground_truth
```

This integration enables comprehensive VLM evaluation against real human activity patterns, providing quantitative metrics for smart home navigation and interaction capabilities.
