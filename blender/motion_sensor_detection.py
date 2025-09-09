"""
VESPER Motion Sensor Detection System
====================================

Implements realistic motion sensor detection based on Aeotec SmartThings Motion Sensor specifications:
- 120° field of view 
- Up to 5 meters (16 feet) detection distance
- PIR (Passive Infrared) motion detection
- SmartThings integration for real-time notifications

This system continuously monitors Actor position and triggers motion sensors when:
1. Actor enters the detection zone (5m radius, 120° cone)
2. Motion is detected after cooldown period expires
3. Sensor state changes are communicated to SmartThings app
"""

import bge
import mathutils
import math
import time
import json
from mathutils import Vector

class MotionSensorDetector:
    """Real-time motion sensor detection system for VESPER virtual environment"""
    
    def __init__(self):
        """Initialize motion sensor detection system"""
        self.sensors = {}  # Registry of all motion sensors
        self.detection_states = {}  # Current detection states
        self.cooldown_timers = {}  # Cooldown tracking
        self.last_positions = {}  # Position tracking for motion detection
        
        # Aeotec SmartThings Motion Sensor specifications
        self.DETECTION_RANGE = 5.0  # meters (16 feet)
        self.FIELD_OF_VIEW = 120.0  # degrees
        self.COOLDOWN_PERIOD = 3.0  # seconds between detections
        self.MOTION_THRESHOLD = 0.1  # minimum movement distance to trigger
        
        print("🔍 Motion Sensor Detection System initialized")
        print(f"   📏 Detection Range: {self.DETECTION_RANGE}m (16ft)")
        print(f"   👁️ Field of View: {self.FIELD_OF_VIEW}°")
        print(f"   ⏱️ Cooldown Period: {self.COOLDOWN_PERIOD}s")
    
    def register_motion_sensor(self, sensor_id: str, position: Vector, room: str, orientation: float = 0.0):
        """Register a motion sensor with the detection system
        
        Args:
            sensor_id: Unique identifier for the sensor
            position: 3D position of the sensor in Blender coordinates
            room: Room name where sensor is located
            orientation: Sensor facing direction in degrees (0 = +Y axis)
        """
        self.sensors[sensor_id] = {
            "position": Vector(position),
            "room": room, 
            "orientation": math.radians(orientation),  # Convert to radians
            "active": True,
            "last_triggered": 0.0,
            "detection_count": 0,
            "actor_detected": False
        }
        
        self.detection_states[sensor_id] = "idle"
        self.cooldown_timers[sensor_id] = 0.0
        
        print(f"✅ Motion sensor {sensor_id} registered:")
        print(f"   📍 Position: [{position.x:.1f}, {position.y:.1f}, {position.z:.1f}]")
        print(f"   🏠 Room: {room}")
        print(f"   🧭 Orientation: {orientation}°")
    
    def unregister_motion_sensor(self, sensor_id: str):
        """Remove a motion sensor from the detection system"""
        if sensor_id in self.sensors:
            del self.sensors[sensor_id]
            del self.detection_states[sensor_id]
            del self.cooldown_timers[sensor_id]
            print(f"🗑️ Motion sensor {sensor_id} unregistered")
    
    def get_actor_position(self):
        """Get current Actor position from BGE scene"""
        try:
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            if actor:
                return Vector((actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z))
        except Exception as e:
            print(f"⚠️ Error getting Actor position: {e}")
        return None
    
    def is_within_detection_cone(self, sensor_pos: Vector, sensor_orientation: float, actor_pos: Vector):
        """Check if actor is within the sensor's 120° detection cone
        
        Args:
            sensor_pos: Motion sensor position
            sensor_orientation: Sensor facing direction (radians)
            actor_pos: Actor position
            
        Returns:
            bool: True if actor is within detection cone
        """
        # Vector from sensor to actor
        to_actor = actor_pos - sensor_pos
        distance = to_actor.length
        
        # Check distance first (quick rejection)
        if distance > self.DETECTION_RANGE:
            return False
            
        # Check if within field of view cone
        if distance > 0.01:  # Avoid division by zero
            # Normalize the vector to actor
            to_actor_normalized = to_actor.normalized()
            
            # Sensor forward direction (based on orientation)
            sensor_forward = Vector((math.sin(sensor_orientation), math.cos(sensor_orientation), 0))
            
            # Calculate angle between sensor forward and actor direction
            dot_product = sensor_forward.dot(to_actor_normalized)
            angle_to_actor = math.acos(max(-1, min(1, dot_product)))  # Clamp to avoid numerical errors
            
            # Check if within half the field of view (120° total = ±60°)
            half_fov = math.radians(self.FIELD_OF_VIEW / 2)
            
            return angle_to_actor <= half_fov
        
        return distance <= self.DETECTION_RANGE  # Very close, always detect
    
    def detect_motion(self, sensor_id: str, actor_pos: Vector):
        """Detect if actor has moved enough to trigger motion sensor
        
        Args:
            sensor_id: Motion sensor identifier
            actor_pos: Current actor position
            
        Returns:
            bool: True if motion detected
        """
        if sensor_id not in self.last_positions:
            self.last_positions[sensor_id] = actor_pos.copy()
            return False
        
        # Calculate distance moved since last check
        last_pos = self.last_positions[sensor_id]
        movement_distance = (actor_pos - last_pos).length
        
        # Update position tracking
        self.last_positions[sensor_id] = actor_pos.copy()
        
        # Check if movement exceeds threshold
        return movement_distance >= self.MOTION_THRESHOLD
    
    def trigger_motion_sensor(self, sensor_id: str, trigger_type: str = "motion_detected"):
        """Trigger motion sensor and send to SmartThings
        
        Args:
            sensor_id: Motion sensor identifier
            trigger_type: Type of trigger (motion_detected, no_motion, etc.)
        """
        current_time = time.time()
        
        # Update sensor state
        if sensor_id in self.sensors:
            self.sensors[sensor_id]["last_triggered"] = current_time
            self.sensors[sensor_id]["detection_count"] += 1
            self.sensors[sensor_id]["actor_detected"] = (trigger_type == "motion_detected")
        
        # Update detection state
        self.detection_states[sensor_id] = trigger_type
        self.cooldown_timers[sensor_id] = current_time + self.COOLDOWN_PERIOD
        
        # Get sensor info for logging
        sensor_info = self.sensors.get(sensor_id, {})
        room = sensor_info.get("room", "Unknown")
        position = sensor_info.get("position", Vector((0, 0, 0)))
        
        print(f"🚨 Motion Sensor {sensor_id} triggered:")
        print(f"   🏠 Room: {room}")
        print(f"   📍 Position: [{position.x:.1f}, {position.y:.1f}]")
        print(f"   🔍 Event: {trigger_type}")
        print(f"   📊 Detection Count: {sensor_info.get('detection_count', 0)}")
        
        # Send to SmartThings (via DeviceManager)
        try:
            self.send_to_smartthings(sensor_id, trigger_type, room)
        except Exception as e:
            print(f"⚠️ Failed to send to SmartThings: {e}")
    
    def send_to_smartthings(self, sensor_id: str, event_type: str, room: str):
        """Send motion sensor event to SmartThings app
        
        Args:
            sensor_id: Motion sensor identifier
            event_type: Type of motion event
            room: Room where motion was detected
        """
        try:
            # Get the VESPER device manager
            scene = bge.logic.getCurrentScene()
            if hasattr(scene, 'vesper_device_manager'):
                device_manager = scene.vesper_device_manager
                
                # Trigger motion sensor in the virtual testbed
                success = device_manager.trigger_motion_sensor(sensor_id, "active" if event_type == "motion_detected" else "inactive")
                
                if success:
                    print(f"✅ SmartThings notified: {sensor_id} - {event_type} in {room}")
                    
                    # Also update any connected SmartThings devices
                    if hasattr(device_manager, 'update_smartthings_device'):
                        device_manager.update_smartthings_device(sensor_id, {
                            "motion": event_type == "motion_detected",
                            "room": room,
                            "timestamp": time.time()
                        })
                else:
                    print(f"❌ Failed to notify SmartThings for {sensor_id}")
            else:
                print(f"⚠️ VESPER device manager not available")
                
        except Exception as e:
            print(f"❌ SmartThings communication error: {e}")
    
    def update_detection(self):
        """Main detection loop - call this every frame from BGE"""
        current_time = time.time()
        actor_pos = self.get_actor_position()
        
        if not actor_pos:
            return  # No actor found, skip detection
        
        for sensor_id, sensor_info in self.sensors.items():
            if not sensor_info["active"]:
                continue
                
            # Check if sensor is in cooldown
            if current_time < self.cooldown_timers.get(sensor_id, 0):
                continue
                
            sensor_pos = sensor_info["position"]
            sensor_orientation = sensor_info["orientation"]
            
            # Check if actor is within detection cone
            in_detection_zone = self.is_within_detection_cone(sensor_pos, sensor_orientation, actor_pos)
            
            if in_detection_zone:
                # Check for actual motion
                motion_detected = self.detect_motion(sensor_id, actor_pos)
                
                if motion_detected:
                    # Only trigger if not currently detecting
                    if not sensor_info.get("actor_detected", False):
                        self.trigger_motion_sensor(sensor_id, "motion_detected")
                        
            else:
                # Actor left detection zone
                if sensor_info.get("actor_detected", False):
                    self.trigger_motion_sensor(sensor_id, "no_motion")
    
    def get_detection_status(self):
        """Get current detection status for all sensors
        
        Returns:
            dict: Status information for all sensors
        """
        status = {
            "total_sensors": len(self.sensors),
            "active_sensors": sum(1 for s in self.sensors.values() if s["active"]),
            "sensors_detecting": sum(1 for s in self.sensors.values() if s.get("actor_detected", False)),
            "sensors": {}
        }
        
        for sensor_id, sensor_info in self.sensors.items():
            status["sensors"][sensor_id] = {
                "room": sensor_info["room"],
                "position": [sensor_info["position"].x, sensor_info["position"].y, sensor_info["position"].z],
                "active": sensor_info["active"],
                "detecting": sensor_info.get("actor_detected", False),
                "detection_count": sensor_info.get("detection_count", 0),
                "last_triggered": sensor_info.get("last_triggered", 0),
                "state": self.detection_states.get(sensor_id, "idle")
            }
        
        return status
    
    def debug_visualization(self):
        """Draw debug visualization of detection zones (for development)"""
        try:
            import bgl
            import gpu
            from gpu_extras.batch import batch_for_shader
            
            # This would draw detection cones in the 3D viewport
            # Implementation depends on Blender's GPU module availability in BGE
            pass
        except ImportError:
            pass  # GPU module not available in BGE

# Global instance for use in BGE
motion_detector = None

def initialize_motion_detection():
    """Initialize the global motion detection system"""
    global motion_detector
    if motion_detector is None:
        motion_detector = MotionSensorDetector()
        print("🔍 Global motion detection system initialized")
    return motion_detector

def register_motion_sensor_detection(sensor_id: str, position: Vector, room: str, orientation: float = 0.0):
    """Register a motion sensor for detection (convenience function)"""
    global motion_detector
    if motion_detector is None:
        motion_detector = initialize_motion_detection()
    
    motion_detector.register_motion_sensor(sensor_id, position, room, orientation)

def update_motion_detection():
    """Update motion detection system (call every frame)"""
    global motion_detector
    if motion_detector is not None:
        motion_detector.update_detection()

def get_motion_detection_status():
    """Get current motion detection status"""
    global motion_detector
    if motion_detector is not None:
        return motion_detector.get_detection_status()
    return {"error": "Motion detection system not initialized"}

# Example usage in BGE:
"""
# In your BGE main loop or init script:
from blender.motion_sensor_detection import initialize_motion_detection, register_motion_sensor_detection, update_motion_detection

# Initialize system
detector = initialize_motion_detection()

# Register sensors (typically done when placing sensors in scene)
register_motion_sensor_detection("M01", Vector((2.5, 3.0, 2.0)), "living_room", 45.0)
register_motion_sensor_detection("M02", Vector((-1.0, 5.0, 2.0)), "kitchen", 180.0)

# In your main game loop:
def main_loop():
    update_motion_detection()  # Call every frame
"""
