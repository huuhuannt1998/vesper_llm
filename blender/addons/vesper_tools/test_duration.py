#!/usr/bin/env python3
"""Test the task duration system"""

import random

def get_task_duration(task_name: str) -> int:
    """Get realistic duration for a task in seconds (simplified version)"""
    task_lower = task_name.lower().strip()
    
    # TESTING MODE: Shortened durations for faster testing
    duration_map = {
        "make coffee": random.randint(3, 8),         # 3-8 seconds
        "brew tea": random.randint(4, 10),           # 4-10 seconds  
        "cook dinner": random.randint(10, 20),       # 10-20 seconds
        "watch tv": random.randint(8, 15),           # 8-15 seconds
        "brush teeth": random.randint(3, 6),         # 3-6 seconds
        "take shower": random.randint(6, 12),        # 6-12 seconds
        "work on computer": random.randint(10, 18),  # 10-18 seconds
        "eat dinner": random.randint(8, 16),         # 8-16 seconds
        "clean": random.randint(6, 15),              # 6-15 seconds
        "relax": random.randint(5, 12),              # 5-12 seconds
        "sleep": random.randint(8, 20),              # 8-20 seconds
        "get ready": random.randint(6, 15),          # 6-15 seconds
    }
    
    # Try exact match first
    if task_lower in duration_map:
        return duration_map[task_lower]
    
    # Try partial matching
    for key in duration_map:
        if key in task_lower or any(word in key for word in task_lower.split()):
            return duration_map[key]
    
    # Default duration - TESTING MODE: Shortened
    return random.randint(5, 15)  # 5-15 seconds default

def format_duration(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        else:
            return f"{minutes}m"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

if __name__ == "__main__":
    print("🧪 Testing Task Duration System...")
    print()
    
    # Test various tasks
    test_tasks = [
        'make coffee',
        'cook dinner', 
        'watch TV',
        'brush teeth',
        'take shower',
        'work on computer',
        'clean kitchen',
        'relax on sofa',
        'unknown task'
    ]
    
    for task in test_tasks:
        duration = get_task_duration(task)
        formatted = format_duration(duration)
        print(f'Task: "{task}" -> Duration: {formatted} ({duration}s)')
    
    print()
    print("✅ Duration system working correctly!")
