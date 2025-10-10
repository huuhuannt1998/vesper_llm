"""
Smart Pathfinding System for BGE Navigation
Provides spatial memory, stuck detection, and intelligent pathfinding
"""

import time
import random
from collections import deque

# ============================================================================
# SPATIAL MEMORY & SMART PATHFINDING SYSTEM
# ============================================================================

# Spatial memory for anti-stuck navigation
SPATIAL_MEMORY = {
    'visited_positions': [],  # [(x, y, timestamp), ...]
    'stuck_positions': [],    # Positions where agent got stuck
    'room_centers': {},       # Known room center positions
    'successful_paths': {},   # Task -> successful position sequence
    'last_positions': []      # Last 10 positions for loop detection
}

# Task-specific goal locations
TASK_GOAL_ROOMS = {
    "Make a phone call": ["LIVING_ROOM", "DINING_ROOM"],
    "Wash hands": ["BATHROOM_1", "BATHROOM_2"],
    "Cook oatmeal": ["KITCHEN"],
    "Eat meal": ["DINING_ROOM", "KITCHEN"],
    "Clean dishes": ["KITCHEN"]
}

# Room adjacency graph (based on house layout)
ROOM_ADJACENCY = {
    'LIVING_ROOM': ['HALLWAY', 'KITCHEN', 'BEDROOM_2'],
    'KITCHEN': ['LIVING_ROOM', 'HALLWAY', 'BATHROOM_1'],
    'HALLWAY': ['LIVING_ROOM', 'KITCHEN', 'BEDROOM_1', 'STORAGE_1', 'BATHROOM_1'],
    'BEDROOM_1': ['HALLWAY'],
    'BEDROOM_2': ['LIVING_ROOM', 'BATHROOM_2'],
    'BATHROOM_1': ['HALLWAY', 'KITCHEN'],
    'BATHROOM_2': ['BEDROOM_2'],
    'STORAGE_1': ['HALLWAY'],
    'STORAGE_2': ['BEDROOM_2']
}

def update_spatial_memory(position, room):
    """Track visited positions and detect loops"""
    current_time = time.time()
    
    # Add to visited positions
    SPATIAL_MEMORY['visited_positions'].append((position[0], position[1], current_time))
    
    # Keep only last 100 positions
    if len(SPATIAL_MEMORY['visited_positions']) > 100:
        SPATIAL_MEMORY['visited_positions'] = SPATIAL_MEMORY['visited_positions'][-100:]
    
    # Update last positions for loop detection
    pos_tuple = (round(position[0], 1), round(position[1], 1))  # Round to avoid float comparison issues
    SPATIAL_MEMORY['last_positions'].append(pos_tuple)
    if len(SPATIAL_MEMORY['last_positions']) > 10:
        SPATIAL_MEMORY['last_positions'].pop(0)
    
    # Update room centers (running average)
    if room and room != 'UNKNOWN':
        if room not in SPATIAL_MEMORY['room_centers']:
            SPATIAL_MEMORY['room_centers'][room] = list(position)
        else:
            # Running average of room center
            center = SPATIAL_MEMORY['room_centers'][room]
            SPATIAL_MEMORY['room_centers'][room] = [
                (center[0] * 0.9 + position[0] * 0.1),
                (center[1] * 0.9 + position[1] * 0.1)
            ]

def detect_stuck_loop():
    """Detect if agent is stuck in a loop"""
    if len(SPATIAL_MEMORY['last_positions']) < 6:
        return False, None
    
    recent = SPATIAL_MEMORY['last_positions'][-6:]
    
    # Pattern: A-B-A-B-A-B (oscillating between 2 positions)
    if (recent[0] == recent[2] == recent[4] and 
        recent[1] == recent[3] == recent[5] and
        recent[0] != recent[1]):
        return True, "OSCILLATING"
    
    # Pattern: A-A-A-A-A-A (stuck in same spot)
    if all(pos == recent[0] for pos in recent):
        return True, "STUCK"
    
    # Pattern: A-B-C-A-B-C (loop of 3)
    if (len(set(recent)) == 3 and
        recent[0] == recent[3] and
        recent[1] == recent[4] and
        recent[2] == recent[5]):
        return True, "LOOP3"
    
    return False, None

def get_escape_action(stuck_type):
    """Get action to escape from stuck situation"""
    if stuck_type == "OSCILLATING":
        # If oscillating, turn to break the pattern
        return random.choice(["LEFT", "LEFT", "RIGHT"])
    
    elif stuck_type == "STUCK":
        # If completely stuck, turn significantly
        return random.choice(["LEFT", "LEFT", "RIGHT", "RIGHT"])
    
    elif stuck_type == "LOOP3":
        # If in 3-position loop, try different approach
        return random.choice(["LEFT", "FORWARD", "RIGHT", "FORWARD"])
    
    return "LEFT"  # Default

def get_target_room_for_task(task_name):
    """Get the target room(s) for a given task"""
    if not task_name:
        return None
    
    task_lower = task_name.lower()
    for task_key, rooms in TASK_GOAL_ROOMS.items():
        if task_key.lower() in task_lower:
            return rooms
    return None

def calculate_room_distance(current_room, target_rooms):
    """Calculate shortest distance to any target room using BFS"""
    if not current_room or current_room == 'UNKNOWN' or not target_rooms:
        return float('inf')
    
    # Normalize room names
    current_room = current_room.upper().replace(' ', '_')
    target_rooms = [r.upper().replace(' ', '_') for r in target_rooms]
    
    # BFS to find shortest path
    queue_list = deque([(current_room, 0)])
    visited = {current_room}
    
    while queue_list:
        room, distance = queue_list.popleft()
        
        if room in target_rooms:
            return distance
        
        if room in ROOM_ADJACENCY:
            for neighbor in ROOM_ADJACENCY[room]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue_list.append((neighbor, distance + 1))
    
    return float('inf')

def record_successful_path(task_name, position_history, room_history):
    """Record successful navigation path for future reference"""
    if not task_name or not position_history:
        return
    
    SPATIAL_MEMORY['successful_paths'][task_name] = {
        'positions': position_history[-20:],
        'rooms': room_history[-10:] if room_history else [],
        'final_position': position_history[-1] if position_history else None
    }
    
    print(f"✅ Learned successful path for '{task_name}'")
    if position_history:
        print(f"   Final position: ({position_history[-1][0]:.1f}, {position_history[-1][1]:.1f})")
    if room_history:
        print(f"   Room sequence: {' → '.join(room_history[-5:])}")

def clear_spatial_memory():
    """Clear spatial memory at start of new task"""
    SPATIAL_MEMORY['last_positions'] = []
    print("🔄 Spatial memory cleared for new task")

def get_navigation_context(current_room, current_task):
    """Get navigation context for VLM prompt enhancement"""
    target_rooms = get_target_room_for_task(current_task)
    room_distance = calculate_room_distance(current_room, target_rooms) if target_rooms else float('inf')
    
    is_stuck, stuck_type = detect_stuck_loop()
    
    context = {
        'target_rooms': target_rooms,
        'room_distance': room_distance,
        'is_stuck': is_stuck,
        'stuck_type': stuck_type,
        'visited_count': len(SPATIAL_MEMORY['visited_positions']),
        'current_room': current_room
    }
    
    return context
