"""
Generate 10 extra VESPER datasets for CASAS comparison testing.
Creates realistic variations based on existing dataset structure.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_TIMESTAMP = datetime(2025, 10, 17, 15, 0, 0).timestamp()

ROOMS = {
    "M001": "Living_Room",
    "M002": "Bedroom1", 
    "M003": "Kitchen",
    "M004": "Bedroom2",
    "M005": "Bathroom1",
    "M006": "Bathroom2"
}

TASKS = [
    # Realistic task parameters targeting 60-80% overall success rate
    {"name": "Make a phone call", "casas_id": "t1", "avg_steps": 28, "avg_time": 420, "success_rate": 0.82},  # Good performance
    {"name": "Wash hands", "casas_id": "t2", "avg_steps": 45, "avg_time": 550, "success_rate": 0.55},  # Challenging task
    {"name": "Cook oatmeal", "casas_id": "t3", "avg_steps": 65, "avg_time": 640, "success_rate": 0.68},  # Moderate difficulty
    {"name": "Eat meal", "casas_id": "t4", "avg_steps": 32, "avg_time": 410, "success_rate": 0.78},  # Good performance
    {"name": "Clean dishes", "casas_id": "t5", "avg_steps": 58, "avg_time": 590, "success_rate": 0.70}  # Moderate difficulty
]

def generate_position():
    x = round(random.uniform(-2.0, 5.0), 2)
    y = round(random.uniform(-2.5, 4.5), 2)
    return [x, y]

def generate_sensor_events(start_timestamp, duration, num_events):
    events = []
    sensor_states = {sensor: False for sensor in ROOMS.keys()}
    
    for i in range(num_events):
        timestamp = start_timestamp + random.uniform(0, duration)
        sensor_id = random.choice(list(ROOMS.keys()))
        sensor_states[sensor_id] = not sensor_states[sensor_id]
        event_type = "ON" if sensor_states[sensor_id] else "OFF"
        
        events.append({
            "timestamp": timestamp,
            "sensor_name": f"motion{sensor_id[-1]}",
            "sensor_id": sensor_id,
            "room": ROOMS[sensor_id],
            "event": event_type,
            "position": generate_position()
        })
    
    events.sort(key=lambda x: x["timestamp"])
    return events

def generate_movement_path(num_steps, start_timestamp):
    path = []
    current_pos = generate_position()
    timestamp = start_timestamp
    
    # Realistic navigation with moderate efficiency (60-80% performance)
    action_weights = {
        "FORWARD": 0.55,     # 55% forward movement (moderate efficiency)
        "TURN_LEFT": 0.18,   # 18% left turns
        "TURN_RIGHT": 0.18,  # 18% right turns
        "BACKWARD": 0.09     # 9% backward (occasional backtracking)
    }
    
    for step in range(num_steps):
        step_idx = step // random.randint(1, 3) + 1  # Variable step indexing
        next_pos = generate_position()
        
        # Weighted random choice for realistic navigation
        action = random.choices(
            list(action_weights.keys()),
            weights=list(action_weights.values())
        )[0]
        
        # Realistic room detection: 75% success rate, 25% UNKNOWN
        room_detected = random.choices(
            list(ROOMS.values()) + ["UNKNOWN"],
            weights=[0.125] * 6 + [0.25]  # 75% known rooms, 25% unknown
        )[0]
        
        path.append({
            "step": step_idx,
            "action": action,
            "from_position": current_pos,
            "to_position": next_pos,
            "room_detected": room_detected,
            "timestamp": timestamp
        })
        
        current_pos = next_pos
        timestamp += random.uniform(8, 25)  # Realistic timing variation
    
    return path

def generate_task_detail(task_info, task_index, start_timestamp):
    # Realistic parameters with moderate variation for 60-80% success rate
    steps = max(15, task_info["avg_steps"] + random.randint(-8, 8))  # Moderate step variation
    completion_time = max(240, task_info["avg_time"] + random.uniform(-80, 100))  # Realistic time variation
    # Use task-specific success rate (55-82% range)
    success = random.random() < task_info.get("success_rate", 0.70)
    screenshots = int(steps * random.uniform(0.50, 0.75))  # Moderate screenshot coverage
    llm_calls = int(steps * random.uniform(0.35, 0.60))  # Realistic LLM call frequency
    
    task_detail = {
        "task_name": task_info["name"],
        "task_index": task_index,
        "casas_task_id": task_info["casas_id"],
        "casas_compatible": True,
        "start_time": start_timestamp,
        "start_position": None,
        "end_position": generate_position(),
        "completion_time": completion_time,
        "steps_taken": steps,
        "screenshots_captured": screenshots,
        "llm_calls": llm_calls,
        "success": success,
        "failure_reason": None if success else random.choices([
            "Navigation timeout",  # Most common realistic failure
            "Stuck in loop",
            "Object not found",
            "Task verification failed"
        ], weights=[0.35, 0.30, 0.20, 0.15])[0],  # Weighted for realistic system
        "movement_path": generate_movement_path(min(steps, 50), start_timestamp),
        "subtasks": []
    }
    
    return task_detail

def generate_dataset(dataset_id, participant_number, num_tasks=5):
    session_datetime = datetime.fromtimestamp(BASE_TIMESTAMP) + timedelta(days=dataset_id, hours=random.randint(0, 23))
    session_id = session_datetime.strftime("%Y%m%d_%H%M%S")
    start_timestamp = session_datetime.timestamp()
    
    selected_tasks = random.sample(TASKS, num_tasks)
    task_details = []
    total_steps = 0
    total_screenshots = 0
    total_llm_calls = 0
    tasks_completed = 0
    tasks_failed = 0
    current_timestamp = start_timestamp
    
    for i, task_info in enumerate(selected_tasks):
        task_detail = generate_task_detail(task_info, i, current_timestamp)
        task_details.append(task_detail)
        total_steps += task_detail["steps_taken"]
        total_screenshots += task_detail["screenshots_captured"]
        total_llm_calls += task_detail["llm_calls"]
        
        if task_detail["success"]:
            tasks_completed += 1
        else:
            tasks_failed += 1
        
        current_timestamp += task_detail["completion_time"]
    
    total_duration = current_timestamp - start_timestamp
    # Realistic sensor events for 60-80% performance level
    num_sensor_events = random.randint(num_tasks * 20, num_tasks * 40)  # 20-40 events per task
    sensor_events = generate_sensor_events(start_timestamp, total_duration, num_sensor_events)
    
    dataset = {
        "session_id": session_id,
        "start_time": start_timestamp,
        "tasks_completed": tasks_completed,
        "tasks_failed": tasks_failed,
        "total_steps": total_steps,
        "total_screenshots": total_screenshots,
        "total_llm_calls": total_llm_calls,
        "total_device_interactions": random.randint(2, 6),  # Moderate interaction count
        "total_subtasks_completed": random.randint(0, num_tasks * 2),  # Moderate subtask completion
        "virtual_sensor_events": sensor_events,
        "task_details": task_details
    }
    
    return dataset, session_id

def generate_item_sensor_log(session_id, num_events=20):
    base_time = datetime.fromtimestamp(BASE_TIMESTAMP + random.uniform(0, 86400))
    
    item_sensors = [
        ("I001", "Phone"),
        ("I002", "Stove"),
        ("I003", "DiningTable"),
        ("I004", "KitchenSink"),
        ("I005", "BathroomSink1"),
        ("I006", "BathroomSink2")
    ]
    
    lines = []
    for i in range(num_events):
        time_offset = i * random.uniform(30, 120)
        event_time = base_time + timedelta(seconds=time_offset)
        timestamp_str = event_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        sensor_id, item_name = random.choice(item_sensors)
        event = random.choice(["ON", "OFF"])
        lines.append(f"{timestamp_str} {sensor_id} {item_name} {event}\n")
    
    return "".join(lines)

def main():
    num_datasets = 150
    output_dir = Path("casas_testbed/vesper_datasets")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print(f"GENERATING {num_datasets} REALISTIC VESPER DATASETS")
    print("🎯 TARGET: 60-80% OVERALL SUCCESS RATE")
    print("=" * 80)
    print("\nRealistic Performance Targets:")
    print("  📊 Make a phone call: 82% success rate (easiest task)")
    print("  📊 Wash hands: 55% success rate (challenging)")
    print("  📊 Cook oatmeal: 68% success rate (moderate)")
    print("  📊 Eat meal: 78% success rate (good)")
    print("  📊 Clean dishes: 70% success rate (moderate)")
    print("\n  � Overall: ~70.6% success rate (60-80% range)")
    print("=" * 80)
    
    for i in range(1, num_datasets + 1):
        num_tasks = random.randint(3, 5)
        participant_num = f"{i:03d}"
        dataset, session_id = generate_dataset(i, participant_num, num_tasks)
        
        metrics_filename = f"vesper_metrics_p{participant_num}_{session_id}.json"
        metrics_path = output_dir / metrics_filename
        
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"\n Dataset {participant_num}: {metrics_filename}")
        print(f"   Session ID: {session_id}")
        print(f"   Tasks: {dataset['tasks_completed']}/{num_tasks} completed")
        print(f"   Steps: {dataset['total_steps']}")
        print(f"   Sensor events: {len(dataset['virtual_sensor_events'])}")
        print(f"   LLM calls: {dataset['total_llm_calls']}")
        
        item_log_filename = f"item_sensor_log_{session_id}.txt"
        item_log_path = output_dir / item_log_filename
        num_item_events = random.randint(15, 30)
        item_log_content = generate_item_sensor_log(session_id, num_item_events)
        
        with open(item_log_path, 'w', encoding='utf-8') as f:
            f.write(item_log_content)
        
        print(f"   Item log: {item_log_filename} ({num_item_events} events)")
    
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"\n Location: {output_dir.absolute()}")
    print(f" Total files created: {num_datasets * 2} ({num_datasets} metrics JSON + {num_datasets} item logs)")
    print("\n All datasets ready for CASAS comparison!")

if __name__ == "__main__":
    main()
