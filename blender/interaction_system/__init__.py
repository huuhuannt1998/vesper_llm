"""
VESPER Interaction System
Item sensors and object interaction tracking
"""

from .item_sensor_manager import (
    ItemSensor,
    ItemSensorManager,
    get_item_sensor_manager,
    setup_default_item_sensors
)

from .object_interaction_handler import (
    InteractionZone,
    ObjectInteractionHandler,
    get_interaction_handler,
    setup_default_interactions
)

__all__ = [
    'ItemSensor',
    'ItemSensorManager',
    'get_item_sensor_manager',
    'setup_default_item_sensors',
    'InteractionZone',
    'ObjectInteractionHandler',
    'get_interaction_handler',
    'setup_default_interactions'
]
