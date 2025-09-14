"""
VESPER MCP Services Package
===========================

Microservices architecture for VESPER VLM navigation system.
Each service handles a specific domain of functionality.
"""

__version__ = "1.0.0"

# Service registry for orchestration
SERVICES = {
    "camera": {
        "name": "Camera & Visual Input Service",
        "description": "Manages first-person camera and image capture",
        "port": 8001,
        "module": "camera_service"
    },
    "image_analysis": {
        "name": "Image Analysis Service", 
        "description": "Analyzes captured images for room classification",
        "port": 8002,
        "module": "image_analysis_service"
    },
    "spatial": {
        "name": "Spatial Awareness Service",
        "description": "Provides position, room detection, and navigation planning",
        "port": 8003,
        "module": "spatial_service"
    },
    "movement": {
        "name": "Movement Control Service",
        "description": "Executes movement actions and path planning",
        "port": 8004,
        "module": "movement_service"
    },
    "interaction": {
        "name": "Interaction Control Service",
        "description": "Handles object interactions and sensor activations",
        "port": 8005,
        "module": "interaction_service"
    },
    "task_analysis": {
        "name": "Task Context Analysis Service",
        "description": "Interprets task descriptions and provides guidance",
        "port": 8006,
        "module": "task_analysis_service"
    },
    "history": {
        "name": "Navigation History Analysis Service",
        "description": "Analyzes navigation patterns and efficiency",
        "port": 8007,
        "module": "history_service"
    },
    "sensor_simulation": {
        "name": "Sensor Simulation Service",
        "description": "Simulates smart home sensors and IoT devices",
        "port": 8008,
        "module": "sensor_simulation_service"
    },
    "device": {
        "name": "Virtual Device Manager Service",
        "description": "Manages virtual devices and CASAS events",
        "port": 8009,
        "module": "device_service"
    },
    "task_manager": {
        "name": "CASAS Task Manager Service",
        "description": "Manages CASAS task definitions and progress",
        "port": 8010,
        "module": "task_manager_service"
    },
    "orchestration": {
        "name": "VLM Orchestration Service",
        "description": "Coordinates services and builds VLM prompts",
        "port": 8000,
        "module": "orchestration_service"
    }
}

def get_service_info(service_name: str) -> dict:
    """Get information about a specific service"""
    return SERVICES.get(service_name, {})

def get_all_services() -> dict:
    """Get information about all services"""
    return SERVICES

def get_service_url(service_name: str) -> str:
    """Get the URL for a specific service"""
    service = SERVICES.get(service_name)
    if service:
        return f"http://localhost:{service['port']}"
    return ""
