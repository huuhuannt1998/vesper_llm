"""
VESPER Virtual Sensors
SmartThings-style virtual device management
"""

from .virtual_device_manager import (
    DeviceState,
    DeviceType,
    VirtualDevice,
    VirtualDeviceManager,
    get_device_manager,
    setup_default_devices
)

__all__ = [
    'DeviceState',
    'DeviceType',
    'VirtualDevice',
    'VirtualDeviceManager',
    'get_device_manager',
    'setup_default_devices'
]
