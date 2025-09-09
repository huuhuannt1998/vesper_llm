"""
VESPER Motion Sensor Detection System
====================================

This module provides realistic motion sensor detection capabilities for VESPER LLM
based on Aeotec SmartThings Motion Sensor specifications.

Directory Structure:
├── motion_sensors/
│   ├── __init__.py              # Main module exports
│   ├── README.md                # Documentation and usage guide
│   ├── core/                    # Core detection system
│   │   ├── __init__.py
│   │   └── motion_sensor_detection.py   # Main detection engine
│   ├── setup/                   # Setup and configuration
│   │   ├── __init__.py
│   │   └── setup_motion_sensors.py      # Sensor placement setup
│   ├── demos/                   # Demo and test scripts
│   │   ├── __init__.py
│   │   ├── test_motion_sensors.py       # Testing framework
│   │   └── demo_motion_sensors.py       # Interactive demo
│   ├── configs/                 # Configuration files
│   │   ├── __init__.py
│   │   ├── sensor_layouts.json          # Predefined layouts
│   │   └── device_specs.json            # Device specifications
│   └── documentation/           # Documentation
│       ├── API_REFERENCE.md             # API documentation
│       ├── INTEGRATION_GUIDE.md         # Integration instructions
│       └── PLACEMENT_GUIDE.md           # Sensor placement guide

Features:
- Realistic Aeotec SmartThings Motion Sensor behavior
- 120° field of view with 5-meter detection range
- Real-time Actor tracking in Blender BGE
- SmartThings app integration
- Professional sensor placement optimization
- Production-ready performance and reliability
"""

# Core detection system exports
from .core.motion_sensor_detection import (
    MotionSensorDetector,
    initialize_motion_detection,
    register_motion_sensor_detection,
    update_motion_detection,
    get_motion_detection_status
)

# Setup and configuration exports
from .setup.setup_motion_sensors import (
    setup_smart_home_motion_sensors,
    calculate_optimal_sensor_positions,
    validate_sensor_coverage,
    export_sensor_configuration,
    deploy_sensors_to_blender
)

# Demo and testing exports
from .demos.test_motion_sensors import (
    run_motion_sensor_test,
    monitor_motion_detection,
    get_test_statistics
)

from .demos.demo_motion_sensors import (
    run_comprehensive_demo,
    show_detection_zones,
    demo_sensor_placement_guide
)

# Version and metadata
__version__ = "1.0.0"
__author__ = "VESPER Team"
__description__ = "Realistic motion sensor detection system for VESPER LLM"

# Sensor specifications (Aeotec SmartThings)
SENSOR_SPECS = {
    "model": "Aeotec SmartThings Motion Sensor",
    "field_of_view": 120,  # degrees
    "detection_range": 5.0,  # meters
    "cooldown_period": 3.0,  # seconds
    "motion_threshold": 0.1,  # meters
    "battery_type": "CR2_3V_lithium",
    "connectivity": "Z-Wave_Plus"
}

# Quick access functions
def quick_setup():
    """Quick setup for motion sensor detection system"""
    try:
        detector = initialize_motion_detection()
        print("✅ Motion sensor detection system initialized")
        return detector
    except Exception as e:
        print(f"❌ Quick setup failed: {e}")
        return None

def get_sensor_specs():
    """Get current sensor specifications"""
    return SENSOR_SPECS.copy()

# Module initialization
print("🔍 VESPER Motion Sensor Detection System loaded")
print(f"   📊 Version: {__version__}")
print(f"   🎯 Sensor Model: {SENSOR_SPECS['model']}")
print(f"   📐 FOV: {SENSOR_SPECS['field_of_view']}° | Range: {SENSOR_SPECS['detection_range']}m")
