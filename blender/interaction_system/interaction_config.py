"""
VESPER Interaction System - Configuration
Centralized configuration for sensors, devices, and time profiles
"""

# ============================================================================
# ITEM SENSOR CONFIGURATION
# ============================================================================

ITEM_SENSORS = {
    # Kitchen
    "I001": {"name": "Sink", "object": "KitchenSink", "room": "Kitchen", "category": "appliance"},
    "I002": {"name": "Stove", "object": "Stove", "room": "Kitchen", "category": "appliance"},
    "I003": {"name": "Fridge", "object": "Refrigerator", "room": "Kitchen", "category": "appliance"},
    "I004": {"name": "Microwave", "object": "Microwave", "room": "Kitchen", "category": "appliance"},
    "I005": {"name": "CoffeeMaker", "object": "CoffeeMaker", "room": "Kitchen", "category": "appliance"},
    "I006": {"name": "Kettle", "object": "Kettle", "room": "Kitchen", "category": "item"},
    "I007": {"name": "Dishes", "object": "Dishes", "room": "Kitchen", "category": "item"},
    
    # Dining Room
    "I008": {"name": "Phone", "object": "Phone", "room": "DiningRoom", "category": "item"},
    "I009": {"name": "DiningTable", "object": "DiningTable", "room": "DiningRoom", "category": "furniture"},
    
    # Bathroom
    "I010": {"name": "BathroomSink", "object": "BathroomSink", "room": "Bathroom", "category": "appliance"},
    "I011": {"name": "Shower", "object": "Shower", "room": "Bathroom", "category": "appliance"},
    "I012": {"name": "Toilet", "object": "Toilet", "room": "Bathroom", "category": "appliance"},
    "I013": {"name": "Medicine", "object": "MedicineCabinet", "room": "Bathroom", "category": "item"},
    
    # Bedroom
    "I014": {"name": "Bed", "object": "Bed", "room": "Bedroom", "category": "furniture"},
    "I015": {"name": "Closet", "object": "Closet", "room": "Bedroom", "category": "furniture"},
    "I016": {"name": "Lamp", "object": "BedroomLamp", "room": "Bedroom", "category": "item"},
    
    # Living Room
    "I017": {"name": "TV", "object": "Television", "room": "LivingRoom", "category": "appliance"},
    "I018": {"name": "Couch", "object": "Couch", "room": "LivingRoom", "category": "furniture"},
    "I019": {"name": "Book", "object": "Book", "room": "LivingRoom", "category": "item"},
}

# ============================================================================
# VIRTUAL DEVICE CONFIGURATION
# ============================================================================

VIRTUAL_DEVICES = {
    # Kitchen
    "D001": {"name": "Kitchen_Light", "type": "LIGHT", "room": "Kitchen", "initial_state": "OFF"},
    "D002": {"name": "Kitchen_Stove", "type": "APPLIANCE", "room": "Kitchen", "initial_state": "OFF"},
    "D003": {"name": "Kitchen_Fridge", "type": "APPLIANCE", "room": "Kitchen", "initial_state": "ON"},
    "D004": {"name": "Kitchen_Microwave", "type": "APPLIANCE", "room": "Kitchen", "initial_state": "OFF"},
    
    # Living Room
    "D005": {"name": "Living_Light", "type": "LIGHT", "room": "LivingRoom", "initial_state": "OFF"},
    "D006": {"name": "Living_TV", "type": "APPLIANCE", "room": "LivingRoom", "initial_state": "OFF"},
    "D007": {"name": "Living_Lamp", "type": "LIGHT", "room": "LivingRoom", "initial_state": "OFF"},
    
    # Bedroom
    "D008": {"name": "Bedroom_Light", "type": "LIGHT", "room": "Bedroom", "initial_state": "OFF"},
    "D009": {"name": "Bedroom_Lamp", "type": "LIGHT", "room": "Bedroom", "initial_state": "OFF"},
    
    # Bathroom
    "D010": {"name": "Bathroom_Light", "type": "LIGHT", "room": "Bathroom", "initial_state": "OFF"},
    
    # Dining Room
    "D011": {"name": "Dining_Light", "type": "LIGHT", "room": "DiningRoom", "initial_state": "OFF"},
}

# ============================================================================
# INTERACTION CONFIGURATION
# ============================================================================

INTERACTIVE_OBJECTS = {
    # Kitchen - Manual interactions
    "KitchenSink": {"distance": 1.5, "type": "manual", "duration": None},
    "Stove": {"distance": 1.5, "type": "manual", "duration": None},
    "Refrigerator": {"distance": 1.5, "type": "manual", "duration": None},
    "Microwave": {"distance": 1.2, "type": "manual", "duration": None},
    
    # Items - Auto interactions
    "Phone": {"distance": 1.0, "type": "auto", "duration": 10.0},
    "Dishes": {"distance": 1.0, "type": "auto", "duration": 5.0},
    
    # Furniture - Auto interactions for specific tasks
    "Bed": {"distance": 1.5, "type": "auto", "duration": 60.0},
    "Couch": {"distance": 1.5, "type": "auto", "duration": 30.0},
    "DiningTable": {"distance": 1.5, "type": "auto", "duration": 15.0},
}

# ============================================================================
# TIME PROFILE CONFIGURATION (virtual seconds)
# ============================================================================

TIME_PROFILES = {
    # Sleep/Rest
    "sleep": 28800,          # 8 hours
    "nap": 1800,             # 30 minutes
    "rest": 600,             # 10 minutes
    
    # Personal Care
    "shower": 600,           # 10 minutes
    "wash_hands": 60,        # 1 minute
    "brush_teeth": 120,      # 2 minutes
    "bathe": 1200,           # 20 minutes
    
    # Cooking
    "cook_simple": 900,      # 15 minutes (toast, cereal, etc.)
    "cook_complex": 2700,    # 45 minutes (full meal)
    "cook_oatmeal": 600,     # 10 minutes
    "microwave": 180,        # 3 minutes
    "boil_water": 300,       # 5 minutes
    
    # Eating
    "eat": 1200,             # 20 minutes
    "snack": 300,            # 5 minutes
    "drink": 60,             # 1 minute
    
    # Communication
    "phone_call": 300,       # 5 minutes
    "phone_call_long": 1800, # 30 minutes
    
    # Entertainment
    "watch_tv": 3600,        # 1 hour
    "read": 1800,            # 30 minutes
    "read_short": 600,       # 10 minutes
    
    # Cleaning
    "clean_dishes": 300,     # 5 minutes
    "clean_room": 900,       # 15 minutes
    "laundry": 2700,         # 45 minutes
    
    # Work/Study
    "work": 7200,            # 2 hours
    "study": 3600,           # 1 hour
}

# ============================================================================
# TIME ACCELERATION SETTINGS
# ============================================================================

TIME_ACCELERATION = {
    # Maximum real-world time to spend on any task (seconds)
    "max_real_duration": 10.0,
    
    # Minimum virtual duration to trigger acceleration (seconds)
    "min_virtual_for_acceleration": 300,  # 5 minutes
    
    # Tasks that should always use acceleration
    "always_accelerate": [
        "sleep", "nap", "cook_complex", "watch_tv", 
        "work", "study", "laundry"
    ],
    
    # Tasks that should run in real-time
    "never_accelerate": [
        "wash_hands", "drink", "microwave"
    ],
}

# ============================================================================
# TASK-ROOM MAPPING
# ============================================================================

TASK_ROOM_MAPPING = {
    # Kitchen tasks
    "Kitchen": [
        "cook", "eat", "kitchen", "oatmeal", "dish", 
        "sink", "stove", "microwave", "fridge"
    ],
    
    # Bedroom tasks
    "Bedroom": [
        "sleep", "bed", "bedroom", "nap", "rest",
        "closet", "dress", "change"
    ],
    
    # Living Room tasks
    "LivingRoom": [
        "tv", "watch", "living", "couch", "relax",
        "read", "book"
    ],
    
    # Dining Room tasks
    "DiningRoom": [
        "phone", "dining", "call", "table"
    ],
    
    # Bathroom tasks
    "Bathroom": [
        "shower", "wash", "bathroom", "bath", "toilet",
        "brush", "medicine"
    ],
}

# ============================================================================
# TASK-OBJECT RELEVANCE MAPPING
# ============================================================================

TASK_OBJECT_RELEVANCE = {
    "phone": ["phone", "call"],
    "sink": ["wash", "clean", "dish", "hands"],
    "stove": ["cook"],
    "bed": ["sleep", "nap", "rest"],
    "couch": ["sit", "rest", "tv", "watch", "relax"],
    "tv": ["watch", "tv"],
    "television": ["watch", "tv"],
    "microwave": ["cook", "heat", "warm"],
    "fridge": ["cook", "eat", "get", "food"],
    "refrigerator": ["cook", "eat", "get", "food"],
    "shower": ["shower", "bathe", "wash"],
    "toilet": ["toilet", "bathroom"],
    "table": ["eat", "meal", "phone", "call"],
    "dishes": ["clean", "wash", "dish"],
}

# ============================================================================
# AUTOMATIC DEVICE CONTROL RULES
# ============================================================================

AUTO_DEVICE_RULES = {
    # When entering kitchen for cooking
    "cook": {
        "room": "Kitchen",
        "turn_on": ["D001"],  # Kitchen light
        "turn_off": []
    },
    
    # When going to sleep
    "sleep": {
        "room": "Bedroom",
        "turn_on": [],
        "turn_off": ["D008", "D009"]  # Bedroom lights
    },
    
    # When watching TV
    "watch": {
        "room": "LivingRoom",
        "turn_on": ["D005", "D006"],  # Living light and TV
        "turn_off": []
    },
    
    # When using phone
    "phone": {
        "room": "DiningRoom",
        "turn_on": ["D011"],  # Dining light
        "turn_off": []
    },
}

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

OUTPUT_CONFIG = {
    # Base directory for all outputs
    "base_dir": r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\vesper_datasets",
    
    # File naming patterns
    "item_sensor_log": "item_sensor_log_{session_id}.txt",
    "item_interactions": "item_interactions_{session_id}.json",
    "device_log": "device_log_{session_id}.json",
    "time_log": "virtual_time_log.json",
    
    # CASAS format settings
    "timestamp_format": "%Y-%m-%d %H:%M:%S.%f",  # Trim to milliseconds
    "event_format": "{datetime} {sensor_id} {sensor_name} {event}\n",
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_task_room(task_name):
    """Infer room from task name"""
    task_lower = task_name.lower()
    
    for room, keywords in TASK_ROOM_MAPPING.items():
        if any(keyword in task_lower for keyword in keywords):
            return room
    
    return None


def get_task_duration(task_name):
    """Get estimated duration for a task"""
    task_lower = task_name.lower()
    
    # Check exact matches first
    for task_key, duration in TIME_PROFILES.items():
        if task_key in task_lower:
            return duration
    
    # Default fallback
    return 300  # 5 minutes


def should_accelerate_time(task_name, virtual_duration):
    """Determine if time acceleration is needed"""
    task_lower = task_name.lower()
    
    # Never accelerate these tasks
    if any(keyword in task_lower for keyword in TIME_ACCELERATION["never_accelerate"]):
        return False
    
    # Always accelerate these tasks
    if any(keyword in task_lower for keyword in TIME_ACCELERATION["always_accelerate"]):
        return True
    
    # Accelerate if duration is long enough
    return virtual_duration >= TIME_ACCELERATION["min_virtual_for_acceleration"]


def is_object_relevant(object_name, task_name):
    """Check if object is relevant to task"""
    if not task_name:
        return True
    
    task_lower = task_name.lower()
    object_lower = object_name.lower()
    
    for obj_keyword, task_keywords in TASK_OBJECT_RELEVANCE.items():
        if obj_keyword in object_lower:
            if any(task_keyword in task_lower for task_keyword in task_keywords):
                return True
    
    return True  # Default: allow interaction


# ============================================================================
# CONFIGURATION EXPORT
# ============================================================================

def export_config(filename="interaction_config.json"):
    """Export configuration as JSON for reference"""
    import json
    
    config = {
        "item_sensors": ITEM_SENSORS,
        "virtual_devices": VIRTUAL_DEVICES,
        "interactive_objects": INTERACTIVE_OBJECTS,
        "time_profiles": TIME_PROFILES,
        "time_acceleration": TIME_ACCELERATION,
        "task_room_mapping": TASK_ROOM_MAPPING,
        "task_object_relevance": TASK_OBJECT_RELEVANCE,
        "auto_device_rules": AUTO_DEVICE_RULES,
        "output_config": OUTPUT_CONFIG,
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuration exported to: {filename}")


if __name__ == "__main__":
    print("📋 VESPER Interaction System Configuration")
    print(f"   Item Sensors: {len(ITEM_SENSORS)}")
    print(f"   Virtual Devices: {len(VIRTUAL_DEVICES)}")
    print(f"   Interactive Objects: {len(INTERACTIVE_OBJECTS)}")
    print(f"   Time Profiles: {len(TIME_PROFILES)}")
    print()
    
    # Export config
    export_config()
