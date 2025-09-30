# VESPER Motion Detection Integration Patch
# ==========================================
# 
# This patch integrates real-time motion detection into the existing VLM navigation system.
# Apply by copying the code sections into blender/llm_bge_navigation.py


# =============================================================================
# MOTION SENSOR DETECTION INTEGRATION FOR CASAS DATASET GENERATION
# =============================================================================

class MotionSensorIntegration:
    """Real-time motion detection integration for VLM navigation"""
    
    def __init__(self):
        """Initialize motion sensor integration"""
        self.motion_sensors = {
            "motion1": {
                "casas_id": "M01",
                "room": "living_room", 
                "detection_area": {
                    "x_min": -2.0, "x_max": 4.0,
                    "y_min": -1.0, "y_max": 5.0,
                    "z_min": -0.5, "z_max": 3.0
                },
                "state": "OFF",
                "last_triggered": 0
            },
            "motion2": {
                "casas_id": "M02",
                "room": "bedroom",
                "detection_area": {
                    "x_min": 5.0, "x_max": 10.0,
                    "y_min": -1.0, "y_max": 4.0, 
                    "z_min": -0.5, "z_max": 3.0
                },
                "state": "OFF",
                "last_triggered": 0
            }
        }
        self.motion_events = []
        self.cooldown_period = 3.0
        
    def is_actor_in_detection_area(self, position, sensor_id):
        """Check if actor is in sensor detection area"""
        if not position or len(position) < 2:
            return False
            
        x, y = position[0], position[1]
        z = position[2] if len(position) > 2 else 1.0
        
        area = self.motion_sensors[sensor_id]["detection_area"]
        
        return (area["x_min"] <= x <= area["x_max"] and
                area["y_min"] <= y <= area["y_max"] and
                area["z_min"] <= z <= area["z_max"])
    
    def update_motion_detection(self, actor_position, timestamp):
        """Update motion detection and generate events"""
        events_generated = []
        
        for sensor_id, sensor_data in self.motion_sensors.items():
            casas_id = sensor_data["casas_id"]
            room = sensor_data["room"]
            
            in_area = self.is_actor_in_detection_area(actor_position, sensor_id)
            current_state = sensor_data["state"] 
            
            time_since_last = timestamp - sensor_data.get("last_triggered", 0)
            
            if in_area and current_state == "OFF" and time_since_last > self.cooldown_period:
                # Motion detected
                sensor_data["state"] = "ON"
                sensor_data["last_triggered"] = timestamp
                
                event = {
                    "sensor_id": casas_id,
                    "sensor_name": sensor_id,
                    "room": room,
                    "state": "ON",
                    "timestamp": timestamp,
                    "actor_position": actor_position.copy() if hasattr(actor_position, 'copy') else list(actor_position),
                    "event_type": "motion_detected"
                }
                events_generated.append(event)
                self.motion_events.append(event)
                
                print(f"🔴 MOTION: {casas_id} ON in {room} at [{actor_position[0]:.2f}, {actor_position[1]:.2f}]")
                
            elif not in_area and current_state == "ON" and time_since_last > self.cooldown_period:
                # Motion cleared
                sensor_data["state"] = "OFF"
                sensor_data["last_triggered"] = timestamp
                
                event = {
                    "sensor_id": casas_id,
                    "sensor_name": sensor_id,
                    "room": room,
                    "state": "OFF",
                    "timestamp": timestamp,
                    "actor_position": actor_position.copy() if hasattr(actor_position, 'copy') else list(actor_position),
                    "event_type": "motion_cleared"
                }
                events_generated.append(event)
                self.motion_events.append(event)
                
                print(f"⚪ MOTION: {casas_id} OFF in {room}")
                
        return events_generated

# Initialize motion sensor integration
motion_sensor_integration = MotionSensorIntegration()

# =============================================================================
# ENHANCED MOVEMENT TRACKING WITH MOTION DETECTION
# =============================================================================

def enhanced_move_actor_and_detect_motion(direction, distance=0.5):
    """Enhanced actor movement with real-time motion detection"""
    global motion_sensor_integration
    
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    
    if not actor:
        print("⚠️ Actor object not found")
        return False
        
    # Get current position before movement
    old_position = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
    
    # Execute movement (existing movement code)
    movement_success = move_actor(direction, distance)  # Your existing move function
    
    if movement_success:
        # Get new position after movement
        new_position = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
        current_time = time.time()
        
        # Update motion detection
        motion_events = motion_sensor_integration.update_motion_detection(new_position, current_time)
        
        # Add motion events to movement log entry
        if hasattr(bge.logic, 'current_movement_log'):
            bge.logic.current_movement_log["motion_sensor_events"] = motion_events
            bge.logic.current_movement_log["motion_events_count"] = len(motion_events)
        
        return True
    
    return False

# =============================================================================
# NAVIGATION LOG ENHANCEMENT FOR CASAS COMPATIBILITY
# =============================================================================

def save_enhanced_navigation_log_with_motion_detection(log_data, session_id):
    """Save navigation log with integrated motion sensor data"""
    global motion_sensor_integration
    
    # Add motion sensor summary to log
    log_data["motion_sensor_integration"] = {
        "enabled": True,
        "sensors_configured": ["motion1", "motion2"],
        "casas_sensor_mapping": {"motion1": "M01", "motion2": "M02"},
        "total_motion_events": len(motion_sensor_integration.motion_events),
        "motion1_activations": len([e for e in motion_sensor_integration.motion_events if e["sensor_name"] == "motion1" and e["state"] == "ON"]),
        "motion2_activations": len([e for e in motion_sensor_integration.motion_events if e["sensor_name"] == "motion2" and e["state"] == "ON"]),
        "rooms_visited": list(set([e["room"] for e in motion_sensor_integration.motion_events]))
    }
    
    # Generate CASAS format events
    casas_events = []
    for event in motion_sensor_integration.motion_events:
        dt = datetime.fromtimestamp(event["timestamp"])
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]
        casas_line = f"{date_str},{time_str},{event['sensor_id']},{event['state']}"
        casas_events.append(casas_line)
    
    log_data["motion_sensor_integration"]["casas_events_generated"] = casas_events
    
    # Save enhanced navigation log
    log_filename = f"blender/evaluation_logs/vesper_navigation_log_{session_id}_with_motion.json"
    
    try:
        with open(log_filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"✅ Enhanced navigation log saved: {log_filename}")
        
        # Save CASAS events separately
        if casas_events:
            casas_filename = f"blender/evaluation_logs/vesper_navigation_casas_{session_id}.csv"
            with open(casas_filename, 'w') as f:
                f.write("Date,Time,Sensor,State\n")
                for event in casas_events:
                    f.write(event + "\n")
            
            print(f"✅ CASAS events saved: {casas_filename}")
            print(f"📊 Motion sensor summary:")
            print(f"    🏠 M01 (living room) activations: {log_data['motion_sensor_integration']['motion1_activations']}")
            print(f"    🛏️ M02 (bedroom) activations: {log_data['motion_sensor_integration']['motion2_activations']}")
            print(f"    📋 Total motion events: {len(casas_events)}")
            
    except Exception as e:
        print(f"❌ Error saving enhanced log: {e}")

# =============================================================================
# INTEGRATION INSTRUCTIONS FOR EXISTING VLM NAVIGATION CODE
# =============================================================================

"""
INTEGRATION STEPS:

1. Add the MotionSensorIntegration class to your blender/llm_bge_navigation.py file

2. Replace your existing move_actor() calls with enhanced_move_actor_and_detect_motion()

3. In your main navigation loop, add motion detection updates:
   
   # Before making VLM decisions
   current_pos = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]
   motion_events = motion_sensor_integration.update_motion_detection(current_pos, time.time())

4. Replace your save_navigation_log() call with save_enhanced_navigation_log_with_motion_detection()

5. The system will automatically:
   - Track actor movement through living room and bedroom
   - Generate M01/M02 sensor events in CASAS format
   - Include motion data in navigation logs
   - Save separate CASAS CSV files for dataset comparison

6. Test by running VLM navigation and checking for:
   - M01 ON/OFF events when moving through living room
   - M02 ON/OFF events when moving through bedroom  
   - CASAS CSV files generated in evaluation_logs/
"""

