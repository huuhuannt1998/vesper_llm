#!/usr/bin/env python
"""
CASAS Motion Sensor Logger for VESPER Navigation System
Tracks motion sensor activations in CASAS-compatible format
"""

import time
from datetime import datetime
from pathlib import Path

try:
    import bge
except ImportError:
    bge = None


class CASASMotionSensorLogger:
    """CASAS-compatible motion sensor logging system"""
    
    def __init__(self):
        self.sensor_events = []
        self.active_sensors = set()
        
        # Map Blender motion sensors to CASAS format
        self.sensor_mapping = {
            'motion1': 'M001',  # Living Room
            'motion2': 'M002',  # Bedroom 1  
            'motion3': 'M003',  # Kitchen
            'motion4': 'M004',  # Bedroom 2
            'motion5': 'M005',  # Bathroom 1
            'motion6': 'M006',  # Bathroom 2
        }
        
        self.location_mapping = {
            'motion1': 'Living_Room',
            'motion2': 'Bedroom1', 
            'motion3': 'Kitchen',
            'motion4': 'Bedroom2',
            'motion5': 'Bathroom1',
            'motion6': 'Bathroom2',
        }
        
        print("📡 CASAS motion sensor logger initialized")
        
    def check_motion_sensors(self, actor_position, timestamp):
        """Check which motion sensors should be activated based on actor position"""
        try:
            if not bge:
                return
                
            scene = bge.logic.getCurrentScene()
            currently_active = set()
            
            # Check each motion sensor detection area
            for sensor_name in self.sensor_mapping.keys():
                detection_area = scene.objects.get(f'DetectionArea_{sensor_name}')
                if detection_area:
                    if self.is_actor_in_detection_area(actor_position, detection_area):
                        currently_active.add(sensor_name)
            
            # Log activations (ON events)
            for sensor in currently_active - self.active_sensors:
                self.log_sensor_activation(sensor, timestamp, 'ON')
                
            # Log deactivations (OFF events) 
            for sensor in self.active_sensors - currently_active:
                self.log_sensor_activation(sensor, timestamp, 'OFF')
                
            self.active_sensors = currently_active
            
        except Exception as e:
            print(f"⚠️ Motion sensor check failed: {e}")
            
    def is_actor_in_detection_area(self, actor_pos, detection_area):
        """Check if actor is within detection area bounds"""
        try:
            # Get detection area bounds
            area_pos = detection_area.worldPosition
            area_scale = detection_area.worldScale
            
            # Simple bounding box check
            dx = abs(actor_pos[0] - area_pos[0])
            dy = abs(actor_pos[1] - area_pos[1])
            
            # Check if within scaled bounds (1.5x scale for coverage)
            return dx <= area_scale[0] * 1.5 and dy <= area_scale[1] * 1.5
            
        except Exception as e:
            print(f"⚠️ Detection area check failed: {e}")
            return False
        
    def log_sensor_activation(self, sensor_name, timestamp, state):
        """Log sensor event in CASAS format: YYYY-MM-DD HH:MM:SS.mmm SENSOR LOCATION STATE"""
        try:
            casas_id = self.sensor_mapping[sensor_name]
            location = self.location_mapping[sensor_name]
            
            # Format timestamp for CASAS (millisecond precision)
            dt = datetime.fromtimestamp(timestamp)
            casas_timestamp = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            # Create CASAS format entry
            casas_entry = f"{casas_timestamp} {casas_id} {location} {state}"
            self.sensor_events.append(casas_entry)
            
            print(f"📡 Motion Sensor: {sensor_name} ({casas_id}) {location} {state}")
            
        except Exception as e:
            print(f"⚠️ Sensor logging failed: {e}")
        
    def export_casas_sensor_data(self, session_id):
        """Export sensor data in CASAS format to vesper_datasets directory"""
        try:
            # Create CASAS-compatible dataset directory
            casas_dir = Path(r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\vesper_datasets")
            casas_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"vesper_casas_p01_{session_id}.txt"
            filepath = casas_dir / filename
            
            with open(filepath, 'w') as f:
                for event in self.sensor_events:
                    f.write(event + '\n')
                    
            print(f"✅ CASAS sensor data exported: {filepath}")
            print(f"   Total sensor events: {len(self.sensor_events)}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ CASAS export failed: {e}")
            return None
    
    def get_sensor_statistics(self):
        """Get statistics about sensor activations"""
        stats = {
            'total_events': len(self.sensor_events),
            'currently_active': list(self.active_sensors),
            'sensor_counts': {}
        }
        
        for event in self.sensor_events:
            parts = event.split()
            if len(parts) >= 3:
                sensor_id = parts[2]
                stats['sensor_counts'][sensor_id] = stats['sensor_counts'].get(sensor_id, 0) + 1
        
        return stats
