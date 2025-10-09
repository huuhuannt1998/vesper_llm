# Add this method to VESPERMetricsLogger class after log_llm_call method

def log_sensor_event(self, sensor_name, sensor_id, room, event_type, position, timestamp):
    """Log virtual motion sensor activation/deactivation for VESPER dataset"""
    event = {
        "timestamp": timestamp,
        "sensor_name": sensor_name,
        "sensor_id": sensor_id,
        "room": room,
        "event": event_type,  # "ON" or "OFF"
        "position": [round(position[0], 2), round(position[1], 2)]
    }
    
    self.session_data["virtual_sensor_events"].append(event)
    
    # Also add to current task if active
    if self.current_task_data:
        if "sensor_events" not in self.current_task_data:
            self.current_task_data["sensor_events"] = []
        self.current_task_data["sensor_events"].append(event)
    
    print(f"📡 VESPER Sensor: {sensor_name} ({sensor_id}) {room} {event_type} at [{position[0]:.2f}, {position[1]:.2f}]")
    
    # Save to file immediately
    self._log_to_file()
