"""
CASAS Virtual Sensor Network
===========================

Simulates the CASAS smart home sensor network for VESPER navigation testing.
Maps VLM actions in Blender to sensor activations matching CASAS dataset format.
"""

import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class SensorType(Enum):
    MOTION = "motion"
    ITEM = "item" 
    DOOR = "door"
    WATER = "water"
    BURNER = "burner"
    PHONE = "phone"

@dataclass
class SensorReading:
    """Represents a single sensor reading in CASAS format"""
    date: str
    time: str
    sensor: str
    message: str
    
    def to_csv_row(self) -> str:
        """Convert to CASAS CSV format"""
        return f"{self.date},{self.time},{self.sensor},{self.message}"

class VirtualSensor:
    """Base class for all virtual sensors"""
    
    def __init__(self, sensor_id: str, sensor_type: SensorType, location: Tuple[float, float] = None):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.location = location  # (x, y) coordinates in Blender
        self.current_state = None
        self.last_activation = None
        
    def activate(self, message: str) -> SensorReading:
        """Generate a sensor reading"""
        now = datetime.now()
        self.last_activation = now
        self.current_state = message
        
        return SensorReading(
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S.%f")[:-3],  # CASAS format with milliseconds
            sensor=self.sensor_id,
            message=message
        )

class PIRMotionSensor(VirtualSensor):
    """PIR Motion Detector (M01-M026)"""
    
    def __init__(self, sensor_id: str, location: Tuple[float, float]):
        super().__init__(sensor_id, SensorType.MOTION, location)
        self.detection_radius = 2.0  # meters
        
    def detect_motion(self, actor_position: Tuple[float, float]) -> SensorReading:
        """Detect if actor is within sensor range"""
        if self.location:
            distance = ((actor_position[0] - self.location[0])**2 + 
                       (actor_position[1] - self.location[1])**2)**0.5
            
            if distance <= self.detection_radius:
                if self.current_state != "ON":
                    return self.activate("ON")
            else:
                if self.current_state == "ON":
                    return self.activate("OFF")
        return None

class ItemSensor(VirtualSensor):
    """Item Use Sensor (I01-I08)"""
    
    def __init__(self, sensor_id: str, item_name: str, location: Tuple[float, float]):
        super().__init__(sensor_id, SensorType.ITEM, location)
        self.item_name = item_name
        self.interaction_radius = 1.0  # meters
        
    def item_interaction(self, actor_position: Tuple[float, float], action: str) -> SensorReading:
        """Detect item pickup/putdown"""
        if self.location:
            distance = ((actor_position[0] - self.location[0])**2 + 
                       (actor_position[1] - self.location[1])**2)**0.5
            
            if distance <= self.interaction_radius:
                if action in ["pickup", "grab", "take"]:
                    return self.activate("ABSENT")
                elif action in ["putdown", "place", "drop"]:
                    return self.activate("PRESENT")
        return None

class DoorSensor(VirtualSensor):
    """Door/Cabinet Sensor (D01)"""
    
    def __init__(self, sensor_id: str, door_name: str, location: Tuple[float, float]):
        super().__init__(sensor_id, SensorType.DOOR, location)
        self.door_name = door_name
        
    def door_interaction(self, action: str) -> SensorReading:
        """Detect door open/close"""
        if action in ["open", "opening"]:
            return self.activate("OPEN")
        elif action in ["close", "closing"]:
            return self.activate("CLOSE")
        return None

class WaterSensor(VirtualSensor):
    """Water Level Sensor (AD1-A, AD1-B)"""
    
    def __init__(self, sensor_id: str, water_type: str, location: Tuple[float, float]):
        super().__init__(sensor_id, SensorType.WATER, location)
        self.water_type = water_type  # "hot" or "cold"
        
    def water_flow(self, flow_rate: float) -> SensorReading:
        """Detect water flow level"""
        level = min(100, max(0, int(flow_rate * 100)))  # 0-100 scale
        return self.activate(str(level))

class BurnerSensor(VirtualSensor):
    """Stove Burner Sensor (AD1-C)"""
    
    def __init__(self, sensor_id: str, location: Tuple[float, float]):
        super().__init__(sensor_id, SensorType.BURNER, location)
        
    def burner_heat(self, heat_level: float) -> SensorReading:
        """Detect burner heat level"""
        level = min(100, max(0, int(heat_level * 100)))  # 0-100 scale
        return self.activate(str(level))

class PhoneSensor(VirtualSensor):
    """Phone Use Sensor (*)"""
    
    def __init__(self, location: Tuple[float, float]):
        super().__init__("*", SensorType.PHONE, location)
        
    def phone_interaction(self, action: str) -> SensorReading:
        """Detect phone usage"""
        if action in ["pickup", "dial", "call"]:
            return self.activate("PICKUP")
        elif action in ["hangup", "end"]:
            return self.activate("HANGUP")
        return None

class VirtualSensorNetwork:
    """Manages the complete CASAS sensor network"""
    
    def __init__(self):
        self.sensors: Dict[str, VirtualSensor] = {}
        self.sensor_log: List[SensorReading] = []
        self.setup_casas_sensors()
        
    def setup_casas_sensors(self):
        """Initialize all CASAS sensors based on apartment layout"""
        
        # Motion sensors (M01-M026) - distributed throughout apartment
        motion_locations = [
            # Kitchen area
            (-2.0, 1.0), (-1.0, 1.0), (0.0, 1.0), (1.0, 1.0),
            # Dining area  
            (2.0, 1.0), (3.0, 1.0), (2.0, 0.0), (3.0, 0.0),
            # Living area
            (-2.0, -1.0), (-1.0, -1.0), (0.0, -1.0), (1.0, -1.0),
            # Bedroom area
            (2.0, -1.0), (3.0, -1.0), (4.0, 0.0), (4.0, 1.0),
            # Bathroom area
            (-3.0, 0.0), (-3.0, 1.0), (-3.0, -1.0),
            # Hallway/transitions
            (0.0, 0.0), (1.0, 0.0), (-1.0, 0.0),
            # Entry area
            (-2.0, 2.0), (-1.0, 2.0), (0.0, 2.0)
        ]
        
        for i, location in enumerate(motion_locations, 1):
            sensor_id = f"M{i:03d}"
            self.sensors[sensor_id] = PIRMotionSensor(sensor_id, location)
            
        # Item sensors (I01-I08)
        item_sensors = [
            ("I01", "oatmeal", (-1.0, 1.5)),
            ("I02", "raisins", (-1.2, 1.5)),  
            ("I03", "brown_sugar", (-0.8, 1.5)),
            ("I04", "bowl", (-1.0, 1.7)),
            ("I05", "measuring_spoon", (-1.5, 1.5)),
            ("I06", "medicine_container", (2.5, 0.5)),
            ("I07", "pot", (-0.5, 1.5)),
            ("I08", "phone_book", (2.8, 1.0))
        ]
        
        for sensor_id, item_name, location in item_sensors:
            self.sensors[sensor_id] = ItemSensor(sensor_id, item_name, location)
            
        # Door sensor (D01)
        self.sensors["D01"] = DoorSensor("D01", "kitchen_cabinet", (-1.0, 2.0))
        
        # Water sensors (AD1-A, AD1-B)
        self.sensors["AD1-A"] = WaterSensor("AD1-A", "hot", (-2.0, 1.5))
        self.sensors["AD1-B"] = WaterSensor("AD1-B", "cold", (-2.0, 1.5))
        
        # Burner sensor (AD1-C)
        self.sensors["AD1-C"] = BurnerSensor("AD1-C", (0.0, 1.5))
        
        # Phone sensor (*)
        self.sensors["*"] = PhoneSensor((2.8, 1.0))
        
    def update_sensors(self, actor_position: Tuple[float, float], action: str = None, 
                      context: Dict[str, Any] = None) -> List[SensorReading]:
        """Update all sensors based on actor state and return new readings"""
        new_readings = []
        
        # Update motion sensors
        for sensor_id, sensor in self.sensors.items():
            if isinstance(sensor, PIRMotionSensor):
                reading = sensor.detect_motion(actor_position)
                if reading:
                    new_readings.append(reading)
                    
        # Handle specific actions
        if action and context:
            action_readings = self._process_action(actor_position, action, context)
            new_readings.extend(action_readings)
            
        # Add to log
        self.sensor_log.extend(new_readings)
        return new_readings
        
    def _process_action(self, actor_position: Tuple[float, float], action: str, 
                       context: Dict[str, Any]) -> List[SensorReading]:
        """Process specific actions into sensor readings"""
        readings = []
        
        # Item interactions
        if "item" in context:
            item_name = context["item"]
            for sensor_id, sensor in self.sensors.items():
                if isinstance(sensor, ItemSensor) and sensor.item_name == item_name:
                    reading = sensor.item_interaction(actor_position, action)
                    if reading:
                        readings.append(reading)
                        
        # Door interactions
        if "door" in context:
            door_name = context["door"]
            for sensor_id, sensor in self.sensors.items():
                if isinstance(sensor, DoorSensor) and sensor.door_name == door_name:
                    reading = sensor.door_interaction(action)
                    if reading:
                        readings.append(reading)
                        
        # Water interactions
        if "water" in context:
            water_flow = context.get("flow_rate", 0.5)
            for sensor_id in ["AD1-A", "AD1-B"]:
                reading = self.sensors[sensor_id].water_flow(water_flow)
                if reading:
                    readings.append(reading)
                    
        # Burner interactions
        if "burner" in context:
            heat_level = context.get("heat_level", 0.7)
            reading = self.sensors["AD1-C"].burner_heat(heat_level)
            if reading:
                readings.append(reading)
                
        # Phone interactions
        if "phone" in context:
            reading = self.sensors["*"].phone_interaction(action)
            if reading:
                readings.append(reading)
                
        return readings
        
    def export_to_casas_format(self, filename: str):
        """Export sensor log to CASAS CSV format"""
        with open(filename, 'w') as f:
            for reading in self.sensor_log:
                f.write(reading.to_csv_row() + "\n")
                
    def clear_log(self):
        """Clear the sensor log"""
        self.sensor_log.clear()
        
    def get_sensor_summary(self) -> Dict[str, int]:
        """Get summary of sensor activations"""
        summary = {}
        for reading in self.sensor_log:
            if reading.sensor not in summary:
                summary[reading.sensor] = 0
            summary[reading.sensor] += 1
        return summary
