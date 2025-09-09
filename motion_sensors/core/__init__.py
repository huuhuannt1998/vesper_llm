"""
Core Motion Sensor Detection Module
==================================

This module contains the core motion sensor detection system implementation.
"""

from .motion_sensor_detection import (
    MotionSensorDetector,
    initialize_motion_detection,
    register_motion_sensor_detection,
    update_motion_detection,
    get_motion_detection_status
)

__all__ = [
    'MotionSensorDetector',
    'initialize_motion_detection',
    'register_motion_sensor_detection',
    'update_motion_detection',
    'get_motion_detection_status'
]
