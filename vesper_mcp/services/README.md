# VESPER Microservices Architecture

## Overview

This directory contains the microservices implementation of the VESPER VLM navigation system. The monolithic `vesper_mcp_server.py` has been decomposed into specialized services for improved maintainability, scalability, and modularity.

## Architecture

### Service Decomposition

The original 901-line monolithic FastMCP server has been split into 11 specialized microservices:

1. **Camera Service** (`camera_service.py`) - Port 8001
   - First-person camera setup and management
   - Image capture and screenshot functionality
   - Camera configuration and status

2. **Image Analysis Service** (`image_analysis_service.py`) - Port 8002
   - Room classification from images
   - Object detection and furniture identification
   - Visual analysis and metadata extraction

3. **Spatial Awareness Service** (`spatial_service.py`) - Port 8003
   - Position tracking and room detection
   - Navigation context and path planning
   - Spatial relationship calculations

4. **Movement Control Service** (`movement_service.py`) - Port 8004
   - Actor movement and positioning
   - Path execution and collision detection
   - Movement constraints and capabilities

5. **Interaction Control Service** (`interaction_service.py`) - Port 8005
   - Object interactions and device control
   - Smart home device management
   - Interaction history and feedback

6. **Task Analysis Service** (`task_analysis_service.py`) - Port 8006
   - Task interpretation and guidance
   - CASAS task management
   - Progress tracking and completion

7. **Navigation History Service** (`history_service.py`) - Port 8007
   - Navigation pattern analysis
   - Performance metrics and efficiency
   - Historical data management

8. **Sensor Simulation Service** (`sensor_simulation_service.py`) - Port 8008
   - Smart home sensor simulation
   - IoT device emulation
   - Environmental state management

9. **Virtual Device Manager Service** (`device_service.py`) - Port 8009
   - Virtual device management
   - CASAS event handling
   - Device state synchronization

10. **CASAS Task Manager Service** (`task_manager_service.py`) - Port 8010
    - CASAS dataset integration
    - Task definitions and subtasks
    - Activity recognition support

11. **VLM Orchestration Service** (`orchestration_service.py`) - Port 8000
    - Central coordination and VLM prompt building
    - Inter-service communication
    - Unified API and guidance generation

### Service Communication

Services communicate via HTTP/REST APIs using the FastMCP framework. The orchestration service acts as the central coordinator, aggregating data from specialized services to build comprehensive VLM prompts.

## Deployment

### Prerequisites

- Python 3.8+
- FastMCP framework
- Blender with BGE (for 3D environment)
- aiohttp for inter-service communication

### Quick Start

1. **Deploy All Services**:
   ```bash
   python deployment_manager.py deploy
   ```

2. **Check Service Status**:
   ```bash
   python deployment_manager.py status
   ```

3. **Health Check**:
   ```bash
   python deployment_manager.py health
   ```

4. **Stop All Services**:
   ```bash
   python deployment_manager.py stop
   ```

### Individual Service Management

Deploy specific service:
```bash
python deployment_manager.py deploy --service camera
```

Stop specific service:
```bash
python deployment_manager.py stop --service camera
```

## Service Details

### Camera Service (Port 8001)

**Tools:**
- `setup_first_person_camera()` - Initialize actor camera
- `capture_first_person_view()` - Take screenshots
- `get_camera_info()` - Camera status and configuration
- `list_camera_captures()` - List captured images

**Dependencies:** Blender BGE

### Image Analysis Service (Port 8002)

**Tools:**
- `analyze_room_from_image()` - Room classification
- `identify_furniture_objects()` - Object detection
- `get_image_metadata()` - Image file information
- `batch_analyze_images()` - Multiple image processing

**Dependencies:** None (uses rule-based analysis)

### Spatial Awareness Service (Port 8003)

**Tools:**
- `get_current_position()` - Actor position and orientation
- `detect_room()` - Room boundary detection
- `get_navigation_context()` - Navigation options
- `get_room_layout()` - Complete spatial map
- `calculate_distance_between_points()` - Distance calculations

**Dependencies:** Blender BGE

### Movement Control Service (Port 8004)

**Tools:**
- `move_actor_to_position()` - Absolute positioning
- `move_actor_relative()` - Relative movement
- `rotate_actor()` - Rotation control
- `move_to_room()` - Room-based navigation
- `execute_movement_path()` - Multi-waypoint paths

**Dependencies:** Blender BGE, Spatial Service

### VLM Orchestration Service (Port 8000)

**Tools:**
- `vlm_navigation_guidance()` - Complete VLM guidance
- `execute_coordinated_action()` - Multi-service actions
- `get_comprehensive_status()` - System-wide status
- `initialize_services()` - Service startup coordination

**Dependencies:** All other services

## Migration from Monolithic Server

The original `vesper_mcp_server.py` contained all functionality in a single file. Key migration points:

### Original Structure
```python
# Single file with all tools
class VesperMCPServer:
    def setup_first_person_camera()  # → Camera Service
    def dual_view_screenshot()       # → Camera Service  
    def analyze_room_content()       # → Image Analysis Service
    def get_spatial_context()       # → Spatial Service
    def move_actor()                 # → Movement Service
    def interact_with_object()       # → Interaction Service
    # ... 9 total tools
```

### New Structure
```python
# Distributed across specialized services
CameraService().setup_first_person_camera()
ImageAnalysisService().analyze_room_from_image()
SpatialService().get_current_position()
MovementService().move_actor_to_position()
OrchestrationService().vlm_navigation_guidance()
```

## Benefits of Microservices Architecture

1. **Modularity**: Each service has a single responsibility
2. **Scalability**: Services can be scaled independently
3. **Maintainability**: Easier to update and debug individual components
4. **Fault Isolation**: Service failures don't bring down the entire system
5. **Development**: Teams can work on services independently
6. **Testing**: Easier to unit test individual services

## Configuration

Service configuration is centralized in `__init__.py`:

```python
SERVICES = {
    "camera": {
        "name": "Camera & Visual Input Service",
        "port": 8001,
        "module": "camera_service"
    },
    # ... other services
}
```

## Monitoring and Health Checks

Each service implements a health check endpoint that reports:
- Service status
- Available capabilities
- Resource usage
- Dependencies

The deployment manager provides comprehensive monitoring across all services.

## Future Enhancements

1. **Service Discovery**: Automatic service registration and discovery
2. **Load Balancing**: Multiple instances of high-demand services
3. **Circuit Breakers**: Fault tolerance patterns
4. **Distributed Tracing**: Request tracking across services
5. **Metrics Collection**: Performance monitoring and alerting
6. **Configuration Management**: Centralized configuration service

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 8000-8010 are available
2. **Service Dependencies**: Start services in dependency order
3. **Blender Integration**: Ensure Blender BGE is available for spatial services
4. **Network Connectivity**: Check inter-service communication

### Debug Mode

Set environment variable for detailed logging:
```bash
export VESPER_DEBUG=1
python deployment_manager.py deploy
```

### Log Analysis

Service logs are available via the deployment manager:
```bash
python deployment_manager.py status --verbose
```
