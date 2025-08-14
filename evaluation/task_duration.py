"""
Task Duration System for VESPER LLM
==================================

Provides realistic duration times for different daily activities 
to make the actor stay in rooms for appropriate amounts of time.

Usage:
    from task_duration import get_task_duration, simulate_task_activity
    
    duration = get_task_duration("Make coffee")  # Returns duration in seconds
    simulate_task_activity("Make coffee", actor, room)  # Animated activity simulation
"""

import time
import random
from typing import Dict, List, Tuple, Optional, Any

# =============================================================================
# TASK DURATION MAPPINGS
# =============================================================================

# Duration ranges in seconds (min, max) for realistic variety
TASK_DURATIONS = {
    # Kitchen Activities
    "make coffee": (90, 180),      # 1.5-3 minutes
    "brew tea": (120, 240),        # 2-4 minutes
    "get water": (10, 30),         # 10-30 seconds
    "make breakfast": (300, 900),  # 5-15 minutes
    "cook dinner": (900, 2700),    # 15-45 minutes
    "prepare lunch": (600, 1200),  # 10-20 minutes
    "heat up food": (60, 180),     # 1-3 minutes
    "get a snack": (30, 90),       # 30 seconds - 1.5 minutes
    "wash dishes": (300, 600),     # 5-10 minutes
    "clean the counter": (180, 300), # 3-5 minutes
    "check the refrigerator": (15, 60), # 15 seconds - 1 minute
    "make toast": (120, 180),      # 2-3 minutes
    "boil water": (180, 300),      # 3-5 minutes
    "use the microwave": (60, 300), # 1-5 minutes
    "get cooking utensils": (30, 90), # 30 seconds - 1.5 minutes
    "prepare ingredients": (300, 900), # 5-15 minutes
    "put away groceries": (300, 600), # 5-10 minutes
    "make smoothie": (180, 300),   # 3-5 minutes
    "bake something": (1800, 3600), # 30-60 minutes
    "make salad": (300, 600),      # 5-10 minutes
    "get plates and cups": (30, 90), # 30 seconds - 1.5 minutes
    
    # Living Room Activities  
    "watch tv": (900, 3600),       # 15-60 minutes
    "turn on television": (10, 30), # 10-30 seconds
    "change tv channel": (5, 15),  # 5-15 seconds
    "turn off tv": (5, 10),        # 5-10 seconds
    "dim living room lights": (10, 30), # 10-30 seconds
    "turn on lights": (5, 15),     # 5-15 seconds
    "turn off lights": (5, 15),    # 5-15 seconds
    "sit on sofa": (300, 1800),    # 5-30 minutes
    "read a book": (900, 3600),    # 15-60 minutes
    "listen to music": (600, 2400), # 10-40 minutes
    "check the news": (300, 900),  # 5-15 minutes
    "relax on couch": (600, 2400), # 10-40 minutes
    "adjust thermostat": (30, 90), # 30 seconds - 1.5 minutes
    "close the curtains": (30, 90), # 30 seconds - 1.5 minutes
    "open the curtains": (30, 90), # 30 seconds - 1.5 minutes
    "clean living room": (900, 1800), # 15-30 minutes
    "vacuum the carpet": (600, 1200), # 10-20 minutes
    "dust furniture": (300, 600),  # 5-10 minutes
    "arrange pillows": (60, 180),  # 1-3 minutes
    "get remote control": (10, 30), # 10-30 seconds
    "turn on stereo": (30, 90),    # 30 seconds - 1.5 minutes
    "watch a movie": (5400, 9000), # 90-150 minutes
    "play video games": (1800, 7200), # 30-120 minutes
    "tidy up living area": (300, 600), # 5-10 minutes
    
    # Bedroom Activities
    "go to bed": (600, 1800),      # 10-30 minutes (getting ready + settling)
    "go to sleep": (300, 900),     # 5-15 minutes (actually falling asleep)
    "wake up": (180, 600),         # 3-10 minutes (getting oriented)
    "get dressed": (300, 600),     # 5-10 minutes
    "change clothes": (180, 360),  # 3-6 minutes
    "put on pajamas": (180, 300),  # 3-5 minutes
    "make the bed": (180, 300),    # 3-5 minutes
    "get out of bed": (60, 300),   # 1-5 minutes
    "open bedroom window": (15, 60), # 15 seconds - 1 minute
    "close bedroom window": (15, 60), # 15 seconds - 1 minute
    "turn on bedroom lights": (5, 15), # 5-15 seconds
    "turn off bedroom lights": (5, 15), # 5-15 seconds
    "get clothes from closet": (120, 300), # 2-5 minutes
    "put clothes away": (180, 360), # 3-6 minutes
    "set alarm clock": (30, 90),   # 30 seconds - 1.5 minutes
    "check the time": (5, 15),     # 5-15 seconds
    "get shoes": (60, 120),        # 1-2 minutes
    "put on shoes": (60, 180),     # 1-3 minutes
    "take off shoes": (30, 60),    # 30 seconds - 1 minute
    "organize closet": (900, 2700), # 15-45 minutes
    "take a nap": (1800, 5400),    # 30-90 minutes
    "rest for a while": (600, 1800), # 10-30 minutes
    
    # Bathroom Activities
    "brush teeth": (120, 180),     # 2-3 minutes
    "take a shower": (600, 1200),  # 10-20 minutes
    "wash hands": (30, 60),        # 30 seconds - 1 minute
    "use the toilet": (120, 300),  # 2-5 minutes
    "wash face": (60, 120),        # 1-2 minutes
    "comb hair": (60, 180),        # 1-3 minutes
    "brush hair": (60, 180),       # 1-3 minutes
    "apply makeup": (600, 1200),   # 10-20 minutes
    "remove makeup": (300, 600),   # 5-10 minutes
    "shave": (300, 600),           # 5-10 minutes
    "use mouthwash": (30, 60),     # 30 seconds - 1 minute
    "take medicine": (30, 120),    # 30 seconds - 2 minutes
    "get ready for work": (1200, 2700), # 20-45 minutes
    "get ready for bed": (600, 1200), # 10-20 minutes
    "clean the mirror": (180, 300), # 3-5 minutes
    "get clean towel": (30, 90),   # 30 seconds - 1.5 minutes
    "apply lotion": (120, 300),    # 2-5 minutes
    "check appearance": (60, 180), # 1-3 minutes
    "use deodorant": (30, 60),     # 30 seconds - 1 minute
    "floss teeth": (60, 180),      # 1-3 minutes
    "take a bath": (1200, 2700),   # 20-45 minutes
    "dry hair": (180, 600),        # 3-10 minutes
    "clean bathroom": (600, 1200), # 10-20 minutes
    
    # Office Activities
    "work on computer": (1800, 7200), # 30-120 minutes
    "check emails": (300, 900),    # 5-15 minutes
    "make phone calls": (300, 1800), # 5-30 minutes
    "do paperwork": (900, 2700),   # 15-45 minutes
    "study": (1800, 5400),         # 30-90 minutes
    "read documents": (600, 1800), # 10-30 minutes
    "write reports": (1800, 5400), # 30-90 minutes
    "use the printer": (60, 300),  # 1-5 minutes
    "video conference": (900, 3600), # 15-60 minutes
    "take work break": (300, 900), # 5-15 minutes
    "organize desk": (300, 600),   # 5-10 minutes
    "get office supplies": (60, 180), # 1-3 minutes
    "file documents": (300, 600),  # 5-10 minutes
    "review schedules": (180, 600), # 3-10 minutes
    "plan meetings": (600, 1800),  # 10-30 minutes
    "research online": (900, 3600), # 15-60 minutes
    "update calendar": (180, 300), # 3-5 minutes
    "backup files": (300, 900),    # 5-15 minutes
    "clean workspace": (300, 600), # 5-10 minutes
    "charge devices": (60, 180),   # 1-3 minutes (plugging in)
    "return to work": (60, 180),   # 1-3 minutes (settling back in)
    "focus on tasks": (1800, 5400), # 30-90 minutes
    "finish project": (900, 3600), # 15-60 minutes
    
    # Dining Room Activities
    "eat breakfast": (600, 1200),  # 10-20 minutes
    "eat lunch": (900, 1800),      # 15-30 minutes
    "eat dinner": (1200, 2700),    # 20-45 minutes
    "have a meal": (900, 2400),    # 15-40 minutes
    "set dining table": (300, 600), # 5-10 minutes
    "clear the table": (180, 300), # 3-5 minutes
    "serve food": (180, 600),      # 3-10 minutes
    "have family dinner": (1800, 3600), # 30-60 minutes
    "entertain guests": (3600, 10800), # 60-180 minutes
    "have coffee with friends": (1800, 5400), # 30-90 minutes
    "celebrate occasion": (3600, 14400), # 60-240 minutes
    "clean dining table": (180, 300), # 3-5 minutes
    "arrange chairs": (120, 300),  # 2-5 minutes
    "get dining utensils": (60, 180), # 1-3 minutes
    "put away dishes": (300, 600), # 5-10 minutes
    "light candles": (60, 120),    # 1-2 minutes
    "set placemats": (120, 300),   # 2-5 minutes
    "serve drinks": (120, 300),    # 2-5 minutes
    "have formal meal": (2700, 5400), # 45-90 minutes
    "host dinner party": (7200, 18000), # 120-300 minutes
    "family gathering": (5400, 14400), # 90-240 minutes
}

# =============================================================================
# CONTEXTUAL DURATION MODIFIERS
# =============================================================================

# Time of day affects activity duration
TIME_MODIFIERS = {
    "morning": {
        "breakfast_activities": 1.2,    # Rushed mornings
        "preparation_activities": 0.8,  # Quick preparation
        "relaxation_activities": 0.5    # Less time to relax
    },
    "afternoon": {
        "work_activities": 1.0,         # Normal work pace
        "meal_activities": 0.9,         # Quick lunch
        "break_activities": 1.1         # Longer breaks
    },
    "evening": {
        "cooking_activities": 1.3,      # More elaborate cooking
        "relaxation_activities": 1.5,   # More time to unwind
        "entertainment_activities": 1.2  # Longer entertainment
    },
    "night": {
        "preparation_activities": 1.1,   # Slower bedtime prep
        "relaxation_activities": 0.8,    # Tired, less active relaxation
        "sleep_activities": 1.0         # Normal sleep prep
    }
}

# Mood affects activity duration
MOOD_MODIFIERS = {
    "tired": 1.3,        # Everything takes longer when tired
    "energetic": 0.8,    # Faster when energetic
    "stressed": 1.2,     # Stressed activities take longer
    "relaxed": 0.9,      # More efficient when relaxed
    "focused": 0.85,     # Very efficient when focused
    "distracted": 1.4    # Much slower when distracted
}

# =============================================================================
# DURATION CALCULATION FUNCTIONS
# =============================================================================

def get_task_duration(task_name: str, context: Dict[str, Any] = None) -> int:
    """
    Get realistic duration for a task in seconds
    
    Args:
        task_name: Name of the task
        context: Optional context with time_of_day, mood, etc.
    
    Returns:
        Duration in seconds
    """
    task_lower = task_name.lower().strip()
    
    # Try exact match first
    if task_lower in TASK_DURATIONS:
        min_duration, max_duration = TASK_DURATIONS[task_lower]
    else:
        # Try partial matching
        duration_found = None
        for task_key in TASK_DURATIONS:
            if task_key in task_lower or any(word in task_key for word in task_lower.split()):
                duration_found = TASK_DURATIONS[task_key]
                break
        
        if duration_found:
            min_duration, max_duration = duration_found
        else:
            # Default duration for unknown tasks
            min_duration, max_duration = (300, 900)  # 5-15 minutes default
    
    # Get base duration
    base_duration = random.randint(min_duration, max_duration)
    
    # Apply context modifiers if provided
    if context:
        base_duration = apply_context_modifiers(base_duration, task_lower, context)
    
    return max(5, base_duration)  # Minimum 5 seconds

def apply_context_modifiers(duration: int, task: str, context: Dict[str, Any]) -> int:
    """Apply contextual modifiers to duration"""
    modified_duration = duration
    
    # Time of day modifier
    time_of_day = context.get("time_of_day", "").lower()
    if time_of_day in TIME_MODIFIERS:
        task_category = categorize_task(task)
        modifier = TIME_MODIFIERS[time_of_day].get(task_category, 1.0)
        modified_duration *= modifier
    
    # Mood modifier
    mood = context.get("mood", "").lower()
    if mood in MOOD_MODIFIERS:
        modified_duration *= MOOD_MODIFIERS[mood]
    
    # Day type modifier
    day_type = context.get("day_type", "").lower()
    if day_type == "weekend":
        modified_duration *= 1.2  # More relaxed on weekends
    elif day_type == "holiday":
        modified_duration *= 1.5  # Much more relaxed on holidays
    
    return int(modified_duration)

def categorize_task(task: str) -> str:
    """Categorize task for time modifier application"""
    task_lower = task.lower()
    
    if any(word in task_lower for word in ["breakfast", "eat", "meal"]):
        return "meal_activities"
    elif any(word in task_lower for word in ["work", "email", "computer", "office"]):
        return "work_activities"
    elif any(word in task_lower for word in ["cook", "prepare", "make", "bake"]):
        return "cooking_activities"
    elif any(word in task_lower for word in ["ready", "dress", "prepare", "shower"]):
        return "preparation_activities"
    elif any(word in task_lower for word in ["watch", "relax", "read", "music", "tv"]):
        return "entertainment_activities"
    elif any(word in task_lower for word in ["rest", "sit", "relax", "break"]):
        return "relaxation_activities"
    elif any(word in task_lower for word in ["sleep", "bed", "nap"]):
        return "sleep_activities"
    else:
        return "general_activities"

# =============================================================================
# ACTIVITY SIMULATION FUNCTIONS  
# =============================================================================

def simulate_task_activity(task_name: str, actor_obj=None, room_name: str = "", 
                          context: Dict[str, Any] = None, callback=None) -> Dict[str, Any]:
    """
    Simulate realistic task activity with duration and optional animations
    
    Args:
        task_name: Name of the task to simulate
        actor_obj: Blender actor object (optional)
        room_name: Name of the room where task is performed
        context: Context dictionary with time_of_day, mood, etc.
        callback: Optional callback function for progress updates
    
    Returns:
        Dictionary with simulation results
    """
    duration = get_task_duration(task_name, context)
    
    print(f"🎭 Starting activity: '{task_name}' in {room_name}")
    print(f"⏱️ Estimated duration: {duration//60}m {duration%60}s")
    
    simulation_result = {
        "task": task_name,
        "room": room_name,
        "duration": duration,
        "start_time": time.time(),
        "progress": 0,
        "completed": False,
        "activity_phases": []
    }
    
    # Get activity phases for this task
    phases = get_activity_phases(task_name, duration)
    simulation_result["activity_phases"] = phases
    
    # Simulate activity with phases
    for i, phase in enumerate(phases):
        phase_name = phase["name"]
        phase_duration = phase["duration"]
        
        print(f"  📍 Phase {i+1}: {phase_name} ({phase_duration}s)")
        
        # Update progress
        simulation_result["progress"] = (i + 1) / len(phases) * 100
        
        # Call callback if provided
        if callback:
            callback(simulation_result.copy())
        
        # Optional: Add actor animations/movements here
        if actor_obj:
            simulate_phase_animation(actor_obj, phase_name, phase_duration)
        
        # Wait for phase duration (or shorter intervals for responsiveness)
        phase_intervals = max(1, phase_duration // 10)  # 10 updates per phase
        for interval in range(phase_intervals):
            time.sleep(phase_duration / phase_intervals)
            if callback:
                callback(simulation_result.copy())
    
    simulation_result["completed"] = True
    simulation_result["end_time"] = time.time()
    simulation_result["actual_duration"] = simulation_result["end_time"] - simulation_result["start_time"]
    
    print(f"✅ Activity '{task_name}' completed in {simulation_result['actual_duration']:.1f}s")
    
    return simulation_result

def get_activity_phases(task_name: str, total_duration: int) -> List[Dict[str, Any]]:
    """Break down task into realistic phases"""
    task_lower = task_name.lower()
    
    # Define phase templates for different task types
    phase_templates = {
        "make coffee": [
            ("Prepare coffee maker", 0.15),
            ("Add coffee grounds", 0.1), 
            ("Add water", 0.1),
            ("Start brewing", 0.05),
            ("Wait for brewing", 0.5),
            ("Pour coffee", 0.1)
        ],
        "cook dinner": [
            ("Gather ingredients", 0.15),
            ("Prepare ingredients", 0.25),
            ("Start cooking", 0.1),
            ("Cook food", 0.4),
            ("Final preparations", 0.1)
        ],
        "take shower": [
            ("Prepare bathroom", 0.1),
            ("Undress", 0.1),
            ("Turn on water", 0.05),
            ("Shower", 0.65),
            ("Dry off", 0.1)
        ],
        "watch tv": [
            ("Find remote", 0.05),
            ("Turn on TV", 0.05),
            ("Choose program", 0.1),
            ("Watch content", 0.8)
        ],
        "work on computer": [
            ("Boot up computer", 0.1),
            ("Open applications", 0.1),
            ("Work session 1", 0.4),
            ("Short break", 0.1),
            ("Work session 2", 0.3)
        ],
        "eat meal": [
            ("Sit down", 0.05),
            ("Start eating", 0.1),
            ("Main eating", 0.7),
            ("Finish meal", 0.15)
        ]
    }
    
    # Try to find matching template
    template = None
    for template_key in phase_templates:
        if template_key in task_lower or any(word in template_key for word in task_lower.split()):
            template = phase_templates[template_key]
            break
    
    # Default generic template
    if not template:
        if total_duration <= 60:  # Short tasks
            template = [("Setup", 0.2), ("Main activity", 0.6), ("Finish", 0.2)]
        elif total_duration <= 300:  # Medium tasks
            template = [("Preparation", 0.15), ("Main activity", 0.7), ("Cleanup", 0.15)]
        else:  # Long tasks
            template = [
                ("Setup", 0.1), ("Phase 1", 0.3), ("Phase 2", 0.3), 
                ("Phase 3", 0.2), ("Finish", 0.1)
            ]
    
    # Calculate actual phase durations
    phases = []
    for phase_name, proportion in template:
        phase_duration = int(total_duration * proportion)
        phases.append({
            "name": phase_name,
            "duration": max(1, phase_duration),  # Minimum 1 second
            "proportion": proportion
        })
    
    return phases

def simulate_phase_animation(actor_obj, phase_name: str, duration: int):
    """Simulate subtle animations during activity phases"""
    # This is a placeholder for potential actor animations
    # Could include small movements, rotations, or pose changes
    try:
        import bpy
        if actor_obj and hasattr(actor_obj, 'location'):
            # Add very subtle random movements to simulate activity
            original_pos = actor_obj.location.copy()
            
            # Small random movements within activity area
            for _ in range(max(1, duration // 5)):
                offset_x = random.uniform(-0.1, 0.1)
                offset_y = random.uniform(-0.1, 0.1)
                
                actor_obj.location.x = original_pos.x + offset_x
                actor_obj.location.y = original_pos.y + offset_y
                
                bpy.context.view_layer.update()
                time.sleep(min(2, duration // 5))
                
                # Return to original position
                actor_obj.location = original_pos
                bpy.context.view_layer.update()
                
    except Exception as e:
        print(f"⚠️ Animation simulation failed: {e}")

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_duration_statistics() -> Dict[str, Any]:
    """Get statistics about task durations"""
    total_tasks = len(TASK_DURATIONS)
    
    # Calculate average durations by category
    categories = {}
    for task, (min_dur, max_dur) in TASK_DURATIONS.items():
        avg_dur = (min_dur + max_dur) / 2
        
        # Categorize task
        if any(word in task for word in ["kitchen", "cook", "make", "eat", "food"]):
            category = "kitchen"
        elif any(word in task for word in ["living", "tv", "watch", "relax"]):
            category = "living_room"
        elif any(word in task for word in ["bed", "sleep", "dress", "clothes"]):
            category = "bedroom"
        elif any(word in task for word in ["bathroom", "shower", "brush", "wash"]):
            category = "bathroom"
        elif any(word in task for word in ["work", "computer", "office", "email"]):
            category = "office"
        elif any(word in task for word in ["dining", "dinner", "meal", "table"]):
            category = "dining_room"
        else:
            category = "general"
        
        if category not in categories:
            categories[category] = []
        categories[category].append(avg_dur)
    
    # Calculate category averages
    category_stats = {}
    for category, durations in categories.items():
        category_stats[category] = {
            "count": len(durations),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations)
        }
    
    return {
        "total_tasks": total_tasks,
        "category_statistics": category_stats,
        "overall_min": min(min_dur for min_dur, max_dur in TASK_DURATIONS.values()),
        "overall_max": max(max_dur for min_dur, max_dur in TASK_DURATIONS.values())
    }

def format_duration(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

def create_activity_schedule(tasks: List[str], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Create a scheduled list of activities with durations"""
    schedule = []
    current_time = context.get("start_time", time.time()) if context else time.time()
    
    for i, task in enumerate(tasks):
        duration = get_task_duration(task, context)
        
        activity = {
            "task": task,
            "order": i + 1,
            "start_time": current_time,
            "duration": duration,
            "end_time": current_time + duration,
            "formatted_duration": format_duration(duration)
        }
        
        schedule.append(activity)
        current_time += duration
    
    return schedule

# =============================================================================
# DEMONSTRATION AND TESTING
# =============================================================================

def demo_task_durations():
    """Demonstrate task duration system"""
    print("🎭 VESPER TASK DURATION SYSTEM DEMO")
    print("=" * 50)
    
    # Show statistics
    stats = get_duration_statistics()
    print(f"📊 Total tasks with duration data: {stats['total_tasks']}")
    print(f"📊 Duration range: {format_duration(stats['overall_min'])} - {format_duration(stats['overall_max'])}")
    
    print(f"\n📊 Category Statistics:")
    for category, data in stats['category_statistics'].items():
        print(f"  🎯 {category}: {data['count']} tasks, avg {format_duration(int(data['avg_duration']))}")
    
    # Demo specific tasks
    demo_tasks = [
        "Make coffee",
        "Cook dinner", 
        "Watch TV",
        "Take shower",
        "Work on computer",
        "Eat breakfast",
        "Clean living room",
        "Go to sleep"
    ]
    
    print(f"\n🎯 Sample Task Durations:")
    for task in demo_tasks:
        duration = get_task_duration(task)
        print(f"  • {task}: {format_duration(duration)}")
    
    # Demo with context
    print(f"\n🌅 Morning Context Example:")
    morning_context = {"time_of_day": "morning", "mood": "energetic", "day_type": "weekday"}
    for task in ["Make coffee", "Take shower", "Get dressed"]:
        duration = get_task_duration(task, morning_context)
        print(f"  • {task}: {format_duration(duration)} (morning, energetic)")
    
    # Demo schedule
    print(f"\n📅 Sample Daily Schedule:")
    daily_tasks = ["Wake up", "Take shower", "Make coffee", "Work on computer", "Eat lunch", "Watch TV"]
    schedule = create_activity_schedule(daily_tasks, morning_context)
    
    for activity in schedule:
        start_time = time.strftime("%H:%M", time.localtime(activity["start_time"]))
        end_time = time.strftime("%H:%M", time.localtime(activity["end_time"]))
        print(f"  📍 {start_time}-{end_time}: {activity['task']} ({activity['formatted_duration']})")

if __name__ == "__main__":
    demo_task_durations()
