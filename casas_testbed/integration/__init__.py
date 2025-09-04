"""
VESPER-CASAS Integration Package
===============================

Production-ready integration between VESPER VLM navigation and CASAS dataset generation.

Main Components:
- VESPERCASASIntegration: Complete integration system
- VESPERDeviceBridge: Low-level device management  
- run_task_evaluation: Quick evaluation entry point
"""

# Production integration system
from .vesper_casas_integration import (
    VESPERCASASIntegration,
    VESPERDevice,
    CASASEvent,
    ComparisonMetrics,
    run_task_evaluation,
    run_phone_call_evaluation
)

# Low-level device bridge (for advanced use)
from .vesper_device_bridge import (
    VESPERDeviceBridge,
    VirtualDeviceInfo,
    create_vesper_bridge
)

__all__ = [
    # Main integration system
    'VESPERCASASIntegration',
    'run_task_evaluation', 
    'run_phone_call_evaluation',
    
    # Data structures
    'VESPERDevice',
    'CASASEvent', 
    'ComparisonMetrics',
    
    # Low-level components
    'VESPERDeviceBridge',
    'VirtualDeviceInfo',
    'create_vesper_bridge'
]
