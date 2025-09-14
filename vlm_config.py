"""
VLM Training System Configuration
================================

Configuration parameters for the VLM tool selection training system.
"""

# Training Configuration
TRAINING_CONFIG = {
    "model": {
        "base_model": "microsoft/DialoGPT-medium",
        "max_length": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True
    },
    
    "training": {
        "learning_rate": 5e-5,
        "batch_size": 8,
        "num_epochs": 3,
        "warmup_steps": 100,
        "weight_decay": 0.01,
        "gradient_accumulation_steps": 2
    },
    
    "dataset": {
        "train_split": 0.8,
        "validation_split": 0.2,
        "max_examples": 1000,
        "min_examples_per_tool": 10
    },
    
    "evaluation": {
        "eval_steps": 100,
        "save_steps": 500,
        "logging_steps": 50,
        "eval_strategy": "steps"
    }
}

# VESPER Microservices Configuration
VESPER_SERVICES = {
    "orchestration": {
        "url": "http://localhost:8000",
        "timeout": 30,
        "max_retries": 3
    },
    
    "navigation": {
        "url": "http://localhost:8001",
        "timeout": 15,
        "max_retries": 2
    },
    
    "vision": {
        "url": "http://localhost:8002",
        "timeout": 20,
        "max_retries": 2
    },
    
    "smart_home": {
        "url": "http://localhost:8003",
        "timeout": 10,
        "max_retries": 3
    },
    
    "task_planning": {
        "url": "http://localhost:8004",
        "timeout": 25,
        "max_retries": 2
    }
}

# Tool Metadata Configuration
TOOL_DEFINITIONS = {
    "navigate_to_location": {
        "description": "Navigate to a specific location in the environment",
        "parameters": ["target_location", "navigation_mode"],
        "context_requirements": ["current_position", "environment_map"],
        "success_criteria": ["reached_target", "path_efficiency"],
        "typical_duration": 10.0,
        "complexity": "medium"
    },
    
    "analyze_room": {
        "description": "Analyze visual features and objects in the current room",
        "parameters": ["analysis_type", "focus_areas"],
        "context_requirements": ["current_view", "lighting_conditions"],
        "success_criteria": ["objects_detected", "analysis_completeness"],
        "typical_duration": 5.0,
        "complexity": "low"
    },
    
    "control_device": {
        "description": "Control smart home devices like lights, thermostats, etc.",
        "parameters": ["device_id", "action", "parameters"],
        "context_requirements": ["device_status", "user_preferences"],
        "success_criteria": ["device_response", "state_change"],
        "typical_duration": 3.0,
        "complexity": "low"
    },
    
    "plan_task_sequence": {
        "description": "Plan a sequence of actions to accomplish a complex task",
        "parameters": ["task_description", "constraints", "preferences"],
        "context_requirements": ["environment_state", "available_tools"],
        "success_criteria": ["plan_feasibility", "step_clarity"],
        "typical_duration": 15.0,
        "complexity": "high"
    },
    
    "capture_image": {
        "description": "Capture and analyze images from the environment",
        "parameters": ["capture_mode", "analysis_focus"],
        "context_requirements": ["camera_position", "lighting"],
        "success_criteria": ["image_quality", "relevant_content"],
        "typical_duration": 2.0,
        "complexity": "low"
    },
    
    "wait_for_condition": {
        "description": "Wait for a specific condition to be met before proceeding",
        "parameters": ["condition_type", "timeout", "check_interval"],
        "context_requirements": ["current_state", "expected_change"],
        "success_criteria": ["condition_met", "timeout_respected"],
        "typical_duration": 8.0,
        "complexity": "low"
    }
}

# Expert System Rules Configuration
EXPERT_RULES = {
    "navigation_rules": [
        {
            "condition": "task_involves_movement",
            "tools": ["navigate_to_location"],
            "priority": 0.9
        },
        {
            "condition": "need_path_planning",
            "tools": ["plan_task_sequence", "navigate_to_location"],
            "priority": 0.8
        }
    ],
    
    "analysis_rules": [
        {
            "condition": "need_visual_information",
            "tools": ["capture_image", "analyze_room"],
            "priority": 0.8
        },
        {
            "condition": "room_exploration_task",
            "tools": ["analyze_room"],
            "priority": 0.9
        }
    ],
    
    "control_rules": [
        {
            "condition": "device_interaction_needed",
            "tools": ["control_device"],
            "priority": 0.9
        },
        {
            "condition": "smart_home_automation",
            "tools": ["control_device", "wait_for_condition"],
            "priority": 0.7
        }
    ],
    
    "planning_rules": [
        {
            "condition": "complex_multi_step_task",
            "tools": ["plan_task_sequence"],
            "priority": 0.9
        },
        {
            "condition": "need_coordination",
            "tools": ["plan_task_sequence", "wait_for_condition"],
            "priority": 0.7
        }
    ]
}

# Reward Function Configuration
REWARD_CONFIG = {
    "success_rewards": {
        "task_completion": 10.0,
        "efficient_tool_selection": 5.0,
        "quick_execution": 3.0,
        "context_appropriateness": 4.0
    },
    
    "penalty_weights": {
        "tool_failure": -5.0,
        "inefficient_selection": -2.0,
        "context_mismatch": -3.0,
        "timeout": -4.0
    },
    
    "bonus_conditions": {
        "optimal_sequence": 2.0,
        "creative_solution": 3.0,
        "resource_efficiency": 1.5,
        "user_satisfaction": 4.0
    }
}

# File Paths Configuration
PATHS = {
    "training_data": "vlm_training_data",
    "model_output": "vlm_tool_model",
    "logs": "vlm_training_logs",
    "checkpoints": "vlm_checkpoints",
    "evaluation_results": "vlm_evaluation_results"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "handlers": {
        "file": {
            "filename": "vlm_training.log",
            "max_bytes": 10485760,  # 10MB
            "backup_count": 5
        },
        "console": {
            "level": "INFO"
        }
    }
}

# Development and Testing Configuration
DEV_CONFIG = {
    "demo_mode": True,
    "mock_services": True,
    "quick_training": True,
    "reduced_dataset": True,
    "debug_logging": True
}

# Production Configuration
PROD_CONFIG = {
    "demo_mode": False,
    "mock_services": False,
    "quick_training": False,
    "reduced_dataset": False,
    "debug_logging": False,
    "model_validation": True,
    "performance_monitoring": True
}

# Environment-specific configurations
ENVIRONMENTS = {
    "development": DEV_CONFIG,
    "production": PROD_CONFIG
}

def get_config(environment="development"):
    """Get configuration for specific environment"""
    base_config = {
        "training": TRAINING_CONFIG,
        "services": VESPER_SERVICES,
        "tools": TOOL_DEFINITIONS,
        "expert_rules": EXPERT_RULES,
        "rewards": REWARD_CONFIG,
        "paths": PATHS,
        "logging": LOGGING_CONFIG
    }
    
    # Apply environment-specific overrides
    env_config = ENVIRONMENTS.get(environment, DEV_CONFIG)
    base_config.update(env_config)
    
    return base_config

def validate_config(config):
    """Validate configuration parameters"""
    required_sections = ["training", "services", "tools", "expert_rules", "rewards", "paths"]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate training parameters
    training = config["training"]["training"]
    if training["learning_rate"] <= 0:
        raise ValueError("Learning rate must be positive")
    
    if training["batch_size"] <= 0:
        raise ValueError("Batch size must be positive")
    
    # Validate service URLs
    for service_name, service_config in config["services"].items():
        if not service_config["url"].startswith(("http://", "https://")):
            raise ValueError(f"Invalid URL for service {service_name}")
    
    return True

# Export commonly used configurations
DEFAULT_CONFIG = get_config("development")
PRODUCTION_CONFIG = get_config("production")
