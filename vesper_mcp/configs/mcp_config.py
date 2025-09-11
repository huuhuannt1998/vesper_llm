"""
VESPER FastMCP Configuration
===========================

Configuration settings for FastMCP tools integration.
"""

# Server configuration
MCP_SERVER_CONFIG = {
    "name": "VESPER Navigation Tools",
    "version": "1.0.0",
    "description": "Enhanced VLM navigation system using FastMCP tools",
    "host": "localhost",
    "port": 8080
}

# Tool configuration
TOOL_CONFIG = {
    "image_analysis": {
        "enabled": True,
        "screenshot_resolution": {"width": 1024, "height": 768},
        "bird_eye_resolution": {"width": 800, "height": 800},
        "capture_height": 15.0,
        "ortho_scale": 12.0,
        "first_person_lens": 35,
        "temp_dir_cleanup": True
    },
    
    "spatial_awareness": {
        "enabled": True,
        "room_detection_radius": 3.0,
        "cluster_radius": 3.0,
        "boundary_limits": {"x": [-5.0, 5.0], "y": [-5.0, 5.0]},
        "cache_room_layout": True,
        "recalculate_interval": 100  # frames
    },
    
    "action_control": {
        "enabled": True,
        "default_step_size": 0.5,
        "interaction_radius": 2.0,
        "max_history_length": 50,
        "collision_detection": "simple",  # "simple" or "advanced"
        "boundary_checking": True
    }
}

# Blender integration settings
BLENDER_CONFIG = {
    "actor_name": "Actor",
    "first_person_camera_name": "FirstPersonCamera",
    "bird_eye_camera_name": "BirdEyeCamera",
    "ceiling_collection_name": "Ceilings",
    "auto_create_cameras": True,
    "preserve_original_camera": True
}

# VLM integration settings
VLM_CONFIG = {
    "models": {
        "vision": "llava:7b",
        "reasoning": "gemma3:4b"
    },
    "backend_url": "http://127.0.0.1:11434",
    "timeout": 30,
    "max_retries": 3,
    "context_window": 4096
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "file_logging": True,
    "log_file": "vesper_mcp.log",
    "console_logging": True,
    "debug_mode": False
}

# Performance settings
PERFORMANCE_CONFIG = {
    "max_concurrent_captures": 2,
    "image_cache_size": 10,
    "spatial_cache_timeout": 300,  # seconds
    "action_history_cleanup": True
}
