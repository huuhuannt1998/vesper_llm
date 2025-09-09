"""
Motion Sensor Setup and Configuration Module
============================================

This module contains setup scripts and configuration tools for motion sensor deployment.
"""

from .setup_motion_sensors import (
    setup_smart_home_motion_sensors,
    calculate_optimal_sensor_positions,
    validate_sensor_coverage,
    export_sensor_configuration,
    deploy_sensors_to_blender
)

__all__ = [
    'setup_smart_home_motion_sensors',
    'calculate_optimal_sensor_positions',
    'validate_sensor_coverage',
    'export_sensor_configuration',
    'deploy_sensors_to_blender'
]
