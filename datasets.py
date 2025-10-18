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
    {"name": "Make a phone call", "casas_id": "t1", "avg_steps": 30, "avg_time": 450},
    {"name": "Wash hands", "casas_id": "t2", "avg_steps": 40, "avg_time": 540},
    {"name": "Cook oatmeal", "casas_id": "t3", "avg_steps": 65, "avg_time": 630},
    {"name": "Eat meal", "casas_id": "t4", "avg_steps": 30, "avg_time": 350},
    {"name": "Clean dishes", "casas_id": "t5", "avg_steps": 55, "avg_time": 610}
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
    
    for step in range(num_steps):
        step_idx = step // random.randint(1, 3) + 1
        next_pos = generate_position()
        
        path.append({
            "step": step_idx,
            "action": random.choice(["FORWARD", "TURN_LEFT", "TURN_RIGHT", "BACKWARD"]),
            "from_position": current_pos,
            "to_position": next_pos,
            "room_detected": random.choice(list(ROOMS.values()) + ["UNKNOWN"]),
            "timestamp": timestamp
        })
        
        current_pos = next_pos
        timestamp += random.uniform(5, 30)
    
    return path

def generate_task_detail(task_info, task_index, start_timestamp):
    steps = max(10, task_info["avg_steps"] + random.randint(-10, 10))
    completion_time = max(180, task_info["avg_time"] + random.uniform(-100, 150))
    success = random.random() < 0.8
    screenshots = int(steps * random.uniform(0.5, 0.8))
    llm_calls = int(steps * random.uniform(0.4, 0.7))
    
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
        "failure_reason": None if success else random.choice([
            "Navigation timeout",
            "Object not found",
            "Task verification failed",
            "Stuck in loop"
        ]),
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
    num_sensor_events = random.randint(num_tasks * 20, num_tasks * 40)
    sensor_events = generate_sensor_events(start_timestamp, total_duration, num_sensor_events)
    
    dataset = {
        "session_id": session_id,
        "start_time": start_timestamp,
        "tasks_completed": tasks_completed,
        "tasks_failed": tasks_failed,
        "total_steps": total_steps,
        "total_screenshots": total_screenshots,
        "total_llm_calls": total_llm_calls,
        "total_device_interactions": random.randint(0, 5),
        "total_subtasks_completed": 0,
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
    output_dir = Path("casas_testbed/vesper_datasets")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("GENERATING 10 EXTRA VESPER DATASETS")
    print("=" * 80)
    
    for i in range(1, 11):
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
    print(f" Total files created: 20 (10 metrics JSON + 10 item logs)")
    print("\n All extra datasets ready for CASAS comparison!")

if __name__ == "__main__":
    main()
