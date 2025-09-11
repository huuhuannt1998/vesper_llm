"""
VESPER VLM Decision Engine
==========================

Comprehensive VLM decision-making system for CASAS ADL tasks with virtual device interactions.

Architecture Components:
1. CASASTaskManager - Manages CASAS ADL tasks and subtasks
2. VirtualDeviceInteractionManager - Handles virtual switches, lights, sensors
3. MultiModalVLMProcessor - Processes house layout, bird-eye, and first-person views
4. DecisionEngine - Makes navigation and interaction decisions
5. TaskProgressTracker - Tracks task completion and subtask checkpoints

Key Features:
- CASAS dataset-compatible task definitions
- Virtual device interaction templates
- Multi-modal visual input processing
- Subtask checkpoint validation
- Duration-based task completion
- Real-time sensor feedback integration
"""

from .casas_task_manager import CASASTaskManager
from .virtual_device_manager import VirtualDeviceInteractionManager  
from .multimodal_vlm_processor import MultiModalVLMProcessor
from .decision_engine import VLMDecisionEngine
from .task_progress_tracker import TaskProgressTracker

__all__ = [
    'CASASTaskManager',
    'VirtualDeviceInteractionManager', 
    'MultiModalVLMProcessor',
    'VLMDecisionEngine',
    'TaskProgressTracker'
]

__version__ = "1.0.0"
