"""
VESPER Time System
Virtual time management with acceleration
"""

from .virtual_time_manager import (
    VirtualTimeManager,
    TaskTimer,
    get_virtual_time_manager,
    get_task_timer,
    TASK_TIME_PROFILES
)

__all__ = [
    'VirtualTimeManager',
    'TaskTimer',
    'get_virtual_time_manager',
    'get_task_timer',
    'TASK_TIME_PROFILES'
]
