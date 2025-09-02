"""
CASAS Event Generator for Blender Integration
Generates real CASAS events during Blender VLM navigation tasks
"""

import os
import csv
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class BlenderCASASGenerator:
    """Generates CASAS events during actual Blender navigation"""
    
    def __init__(self, output_dir: str = None):
        """Initialize CASAS event generator for Blender integration"""
        if output_dir is None:
            # Default to casas_testbed folder in the vesper_llm project
            vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
            output_dir = os.path.join(vesper_root, "casas_testbed", "blender_datasets")
        
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Track current session
        self.session_id = None
        self.events = []
        self.start_time = None
        self.current_room = None
        self.active_sensors = set()
        
        # Room to CASAS sensor mapping (based on CASAS ground truth analysis)
        self.room_sensor_map = {
            'kitchen': ['M13', 'D07', 'T01', 'I06', 'I08'],
            'bedroom': ['M02', 'M15', 'D03', 'T03'],
            'bathroom': ['M08', 'T02', 'D08'],
            'living_room': ['M01', 'D01', 'I02', 'I01'],
            'living room': ['M01', 'D01', 'I02', 'I01'],
            'dining_room': ['M05', 'D02', 'T04'],
            'dining room': ['M05', 'D02', 'T04'],
            'hallway': ['M11', 'M14'],
            'entrance': ['D01', 'M01'],
            'office': ['M06', 'D04', 'I03'],
            'laundry': ['M09', 'I05', 'T05']
        }
        
        # Task to device interaction mapping
        self.task_device_map = {
            'phone_call': ['A01'],  # Phone
            'cook': ['I06', 'I08', 'T01'],  # Stove, microwave, temp
            'eat': ['I02', 'T04'],  # Item sensors, dining temp
            'wash_hands': ['T02'],  # Bathroom temp
            'clean': ['I05'],  # Cleaning items
            'watch_tv': ['I02'],  # Living room items
            'sleep': ['M02', 'M15'],  # Bedroom motion
            'use_computer': ['I03']  # Office items
        }
        
        print(f"🏠 CASAS: Generator initialized - output: {output_dir}")
    
    def start_session(self, participant_id: str = "p01", task_description: str = "navigation"):
        """Start a new CASAS session for Blender navigation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"blender_{participant_id}_{task_description}_{timestamp}"
        self.events = []
        self.start_time = time.time()
        self.active_sensors = set()
        
        print(f"📋 CASAS: Session started - {self.session_id}")
        return self.session_id
    
    def actor_entered_room(self, room_name: str, position: Tuple[float, float, float] = None):
        """Generate CASAS events when actor enters a room"""
        if not self.session_id:
            print("⚠️ CASAS: No active session - call start_session() first")
            return
        
        room_name = room_name.lower().strip()
        
        # Turn off sensors from previous room
        if self.current_room and self.current_room != room_name:
            self._deactivate_room_sensors(self.current_room)
        
        # Turn on sensors for new room
        if room_name in self.room_sensor_map:
            sensors = self.room_sensor_map[room_name]
            
            for sensor in sensors:
                if sensor.startswith('M'):  # Motion sensor
                    self._add_event(sensor, "ON")
                    self.active_sensors.add(sensor)
                elif sensor.startswith('D'):  # Door sensor (if entering)
                    self._add_event(sensor, "OPEN")
            
            self.current_room = room_name
            print(f"🚶 CASAS: Actor entered {room_name} - activated {len(sensors)} sensors")
        else:
            print(f"⚠️ CASAS: Unknown room '{room_name}' - no sensor mapping")
    
    def actor_left_room(self, room_name: str):
        """Generate CASAS events when actor leaves a room"""
        if not self.session_id:
            return
        
        room_name = room_name.lower().strip()
        self._deactivate_room_sensors(room_name)
        
        if self.current_room == room_name:
            self.current_room = None
    
    def task_started(self, task_name: str):
        """Generate CASAS events when a task starts"""
        if not self.session_id:
            return
        
        task_name = task_name.lower().strip()
        
        if task_name in self.task_device_map:
            devices = self.task_device_map[task_name]
            
            for device in devices:
                if device.startswith('A'):  # Appliance
                    if task_name == 'phone_call':
                        self._add_event(device, "PHONE_PICKUP")
                    else:
                        self._add_event(device, "ON")
                elif device.startswith('I'):  # Item sensor
                    self._add_event(device, "PRESENT")
                elif device.startswith('T'):  # Temperature
                    # Temperature changes during tasks
                    pass
            
            print(f"🎯 CASAS: Task '{task_name}' started - activated {len(devices)} devices")
    
    def task_completed(self, task_name: str):
        """Generate CASAS events when a task completes"""
        if not self.session_id:
            return
        
        task_name = task_name.lower().strip()
        
        if task_name in self.task_device_map:
            devices = self.task_device_map[task_name]
            
            for device in devices:
                if device.startswith('A'):  # Appliance
                    if task_name == 'phone_call':
                        self._add_event(device, "PHONE_HANGUP")
                    else:
                        self._add_event(device, "OFF")
                elif device.startswith('I'):  # Item sensor
                    self._add_event(device, "ABSENT")
            
            print(f"✅ CASAS: Task '{task_name}' completed")
    
    def end_session(self):
        """End the current session and save CASAS dataset"""
        if not self.session_id:
            print("⚠️ CASAS: No active session to end")
            return None
        
        # Deactivate all remaining sensors
        if self.current_room:
            self._deactivate_room_sensors(self.current_room)
        
        # Save CASAS dataset
        dataset_file = self._save_dataset()
        
        # Reset session
        session_id = self.session_id
        self.session_id = None
        self.events = []
        self.active_sensors = set()
        self.current_room = None
        
        print(f"💾 CASAS: Session ended - saved {dataset_file}")
        return dataset_file
    
    def _add_event(self, sensor: str, message: str):
        """Add a CASAS event with proper timestamp"""
        now = datetime.now()
        event = {
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S.%f')[:-3],  # milliseconds
            'sensor': sensor,
            'message': message
        }
        self.events.append(event)
        print(f"📊 CASAS: {event['time']} {sensor} {message}")
    
    def _deactivate_room_sensors(self, room_name: str):
        """Turn off sensors when leaving a room"""
        if room_name in self.room_sensor_map:
            sensors = self.room_sensor_map[room_name]
            
            for sensor in sensors:
                if sensor in self.active_sensors:
                    if sensor.startswith('M'):  # Motion sensor
                        self._add_event(sensor, "OFF")
                        self.active_sensors.remove(sensor)
                    elif sensor.startswith('D'):  # Door sensor
                        self._add_event(sensor, "CLOSE")
    
    def _save_dataset(self) -> str:
        """Save events to CASAS CSV format"""
        if not self.events:
            print("⚠️ CASAS: No events to save")
            return None
        
        filename = f"{self.session_id}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'time', 'sensor', 'message'])
            
            for event in self.events:
                writer.writerow([event['date'], event['time'], event['sensor'], event['message']])
        
        print(f"💾 CASAS: Saved {len(self.events)} events to {filepath}")
        return filepath


# ==========================================
# Blender Integration Functions
# ==========================================

# Global CASAS generator instance for Blender
_blender_casas_generator = None

def init_blender_casas(participant_id: str = "p01"):
    """Initialize CASAS generation for Blender session"""
    global _blender_casas_generator
    _blender_casas_generator = BlenderCASASGenerator()
    
    # Start session with current task info
    task_description = "vlm_navigation"
    session_id = _blender_casas_generator.start_session(participant_id, task_description)
    return session_id

def blender_room_entered(room_name: str, actor_position: Tuple[float, float, float] = None):
    """Called when actor enters a room in Blender"""
    if _blender_casas_generator:
        _blender_casas_generator.actor_entered_room(room_name, actor_position)

def blender_room_left(room_name: str):
    """Called when actor leaves a room in Blender"""
    if _blender_casas_generator:
        _blender_casas_generator.actor_left_room(room_name)

def blender_task_started(task_name: str):
    """Called when a VLM task starts in Blender"""
    if _blender_casas_generator:
        _blender_casas_generator.task_started(task_name)

def blender_task_completed(task_name: str):
    """Called when a VLM task completes in Blender"""
    if _blender_casas_generator:
        _blender_casas_generator.task_completed(task_name)

def finalize_blender_casas():
    """End CASAS session and save dataset"""
    global _blender_casas_generator
    if _blender_casas_generator:
        dataset_file = _blender_casas_generator.end_session()
        _blender_casas_generator = None
        return dataset_file
    return None

def get_casas_status():
    """Get current CASAS generation status"""
    if _blender_casas_generator:
        return {
            'active': True,
            'session_id': _blender_casas_generator.session_id,
            'current_room': _blender_casas_generator.current_room,
            'event_count': len(_blender_casas_generator.events),
            'active_sensors': list(_blender_casas_generator.active_sensors)
        }
    return {'active': False}


# ==========================================
# Test Integration (Standalone)
# ==========================================

if __name__ == "__main__":
    # Test the CASAS generator
    print("🧪 Testing CASAS Generator...")
    
    generator = BlenderCASASGenerator()
    
    # Simulate a phone call task
    generator.start_session("p01", "phone_call_test")
    
    # Actor moves to living room
    generator.actor_entered_room("living_room", (1.0, 2.0, 0.0))
    time.sleep(0.1)
    
    # Start phone call task
    generator.task_started("phone_call")
    time.sleep(0.1)
    
    # Complete phone call
    generator.task_completed("phone_call")
    time.sleep(0.1)
    
    # Leave living room
    generator.actor_left_room("living_room")
    
    # End session
    dataset_file = generator.end_session()
    
    print(f"✅ Test completed - dataset saved: {dataset_file}")
