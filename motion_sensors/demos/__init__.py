"""
Motion Sensor Demos and Testing Module
======================================

This module contains demo scripts and testing frameworks for motion sensor validation.
"""

from .test_motion_sensors import (
    run_motion_sensor_test,
    monitor_motion_detection,
    get_test_statistics
)

from .demo_motion_sensors import (
    run_comprehensive_demo,
    show_detection_zones,
    demo_sensor_placement_guide
)

__all__ = [
    'run_motion_sensor_test',
    'monitor_motion_detection',
    'get_test_statistics',
    'run_comprehensive_demo',
    'show_detection_zones',
    'demo_sensor_placement_guide'
]
