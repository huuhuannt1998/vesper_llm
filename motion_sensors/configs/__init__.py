"""
Motion Sensor Configuration Module
==================================

This module contains configuration files and settings for motion sensor deployment.
"""

import json
import os

def load_sensor_layout(layout_name):
    """Load a predefined sensor layout configuration"""
    config_path = os.path.join(os.path.dirname(__file__), f"{layout_name}.json")
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return None

def save_sensor_layout(layout_name, layout_data):
    """Save a sensor layout configuration"""
    config_path = os.path.join(os.path.dirname(__file__), f"{layout_name}.json")
    with open(config_path, 'w') as f:
        json.dump(layout_data, f, indent=2)

__all__ = ['load_sensor_layout', 'save_sensor_layout']
