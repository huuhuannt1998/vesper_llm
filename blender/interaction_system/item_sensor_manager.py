"""
VESPER Item Sensor Manager
Tracks object interactions similar to CASAS dataset item sensors
Logs interaction start/end times and durations
"""

import time
import json
import os
from datetime import datetime
from pathlib import Path


class ItemSensor:
    """Represents a single item sensor attached to an object"""
    
    def __init__(self, sensor_id, sensor_name, object_name, room, category="item"):
        self.sensor_id = sensor_id  # e.g., "I001", "I002"
        self.sensor_name = sensor_name  # e.g., "Phone", "Sink", "Stove"
        self.object_name = object_name  # Blender object name
        self.room = room  # Room where item is located
        self.category = category  # item, appliance, furniture, etc.
        
        # Interaction state
        self.is_active = False
        self.activation_time = None
        self.last_deactivation_time = None
        self.total_interaction_time = 0.0
        self.interaction_count = 0
        
        # Interaction history
        self.interaction_history = []
    
    def activate(self, timestamp):
        """Mark item as being interacted with"""
        if not self.is_active:
            self.is_active = True
            self.activation_time = timestamp
            self.interaction_count += 1
            print(f"🔵 Item Sensor ON: {self.sensor_name} ({self.sensor_id}) - {self.room}")
            return True
        return False
    
    def deactivate(self, timestamp):
        """Mark item interaction as ended"""
        if self.is_active:
            self.is_active = False
            duration = timestamp - self.activation_time
            self.total_interaction_time += duration
            self.last_deactivation_time = timestamp
            
            # Record interaction
            interaction_record = {
                "start_time": self.activation_time,
                "end_time": timestamp,
                "duration": duration,
                "interaction_number": self.interaction_count
            }
            self.interaction_history.append(interaction_record)
            
            print(f"⚪ Item Sensor OFF: {self.sensor_name} ({self.sensor_id}) - Duration: {duration:.2f}s")
            return interaction_record
        return None
    
    def get_state(self):
        """Get current sensor state"""
        return {
            "sensor_id": self.sensor_id,
            "sensor_name": self.sensor_name,
            "object_name": self.object_name,
            "room": self.room,
            "category": self.category,
            "is_active": self.is_active,
            "interaction_count": self.interaction_count,
            "total_interaction_time": self.total_interaction_time
        }


class ItemSensorManager:
    """
    Manages all item sensors in the virtual smart home
    Compatible with CASAS dataset format for item interactions
    """
    
    def __init__(self, dataset_dir=None):
        self.sensors = {}  # sensor_id -> ItemSensor
        self.object_to_sensor = {}  # object_name -> sensor_id
        
        # Output directory for logs
        if dataset_dir is None:
            dataset_dir = os.path.join(
                r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed",
                "vesper_datasets"
            )
        self.dataset_dir = dataset_dir
        os.makedirs(self.dataset_dir, exist_ok=True)
        
        # Session tracking
        self.session_start_time = time.time()
        self.session_id = time.strftime("%Y%m%d_%H%M%S")
        
        # Event log (CASAS format compatible)
        self.event_log = []
        
        print("✅ Item Sensor Manager initialized")
    
    def register_item_sensor(self, sensor_id, sensor_name, object_name, room, category="item"):
        """Register a new item sensor"""
        sensor = ItemSensor(sensor_id, sensor_name, object_name, room, category)
        self.sensors[sensor_id] = sensor
        self.object_to_sensor[object_name] = sensor_id
        
        print(f"📍 Registered item sensor: {sensor_name} ({sensor_id}) in {room}")
        return sensor
    
    def interact_with_object(self, object_name, timestamp=None):
        """Start interaction with an object"""
        if timestamp is None:
            timestamp = time.time()
        
        if object_name not in self.object_to_sensor:
            print(f"⚠️ No sensor registered for object: {object_name}")
            return None
        
        sensor_id = self.object_to_sensor[object_name]
        sensor = self.sensors[sensor_id]
        
        if sensor.activate(timestamp):
            # Log CASAS-style event
            event = {
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "sensor_id": sensor_id,
                "sensor_name": sensor.sensor_name,
                "room": sensor.room,
                "event": "ON",
                "category": sensor.category
            }
            self.event_log.append(event)
            return event
        return None
    
    def end_interaction(self, object_name, timestamp=None):
        """End interaction with an object"""
        if timestamp is None:
            timestamp = time.time()
        
        if object_name not in self.object_to_sensor:
            return None
        
        sensor_id = self.object_to_sensor[object_name]
        sensor = self.sensors[sensor_id]
        
        interaction_record = sensor.deactivate(timestamp)
        if interaction_record:
            # Log CASAS-style event
            event = {
                "timestamp": timestamp,
                "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "sensor_id": sensor_id,
                "sensor_name": sensor.sensor_name,
                "room": sensor.room,
                "event": "OFF",
                "category": sensor.category,
                "duration": interaction_record["duration"]
            }
            self.event_log.append(event)
            return event
        return None
    
    def check_proximity_interaction(self, actor_position, interaction_distance=1.5):
        """
        Check if actor is close enough to any objects to auto-trigger interaction
        Returns list of nearby interactive objects
        """
        try:
            import bge
            scene = bge.logic.getCurrentScene()
            nearby_objects = []
            
            for sensor_id, sensor in self.sensors.items():
                # Get object from scene
                if sensor.object_name in scene.objects:
                    obj = scene.objects[sensor.object_name]
                    obj_pos = obj.worldPosition
                    
                    # Calculate distance
                    distance = ((actor_position[0] - obj_pos[0])**2 + 
                              (actor_position[1] - obj_pos[1])**2)**0.5
                    
                    if distance <= interaction_distance:
                        nearby_objects.append({
                            "object_name": sensor.object_name,
                            "sensor_name": sensor.sensor_name,
                            "sensor_id": sensor_id,
                            "distance": distance,
                            "is_active": sensor.is_active
                        })
            
            return nearby_objects
            
        except Exception as e:
            print(f"⚠️ Proximity check failed: {e}")
            return []
    
    def get_all_active_sensors(self):
        """Get list of all currently active sensors"""
        return [
            sensor.get_state() 
            for sensor in self.sensors.values() 
            if sensor.is_active
        ]
    
    def export_casas_format(self):
        """Export interaction log in CASAS dataset format"""
        try:
            # CASAS format: timestamp sensor_id sensor_name event
            output_file = os.path.join(
                self.dataset_dir,
                f"item_sensor_log_{self.session_id}.txt"
            )
            
            with open(output_file, 'w') as f:
                for event in self.event_log:
                    # Format: 2024-01-15 10:30:45.123 I001 Phone ON
                    line = f"{event['datetime']} {event['sensor_id']} {event['sensor_name']} {event['event']}\n"
                    f.write(line)
            
            print(f"💾 CASAS item sensor log exported: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def export_detailed_json(self):
        """Export detailed interaction data as JSON"""
        try:
            output_file = os.path.join(
                self.dataset_dir,
                f"item_interactions_{self.session_id}.json"
            )
            
            data = {
                "session_id": self.session_id,
                "session_start": self.session_start_time,
                "sensors": {
                    sensor_id: sensor.get_state()
                    for sensor_id, sensor in self.sensors.items()
                },
                "event_log": self.event_log,
                "interaction_summary": self._generate_summary()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Detailed interaction log exported: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None
    
    def _generate_summary(self):
        """Generate interaction summary statistics"""
        total_interactions = sum(s.interaction_count for s in self.sensors.values())
        total_time = sum(s.total_interaction_time for s in self.sensors.values())
        
        most_used = max(
            self.sensors.values(),
            key=lambda s: s.interaction_count,
            default=None
        )
        
        return {
            "total_interactions": total_interactions,
            "total_interaction_time": total_time,
            "unique_items_used": len([s for s in self.sensors.values() if s.interaction_count > 0]),
            "most_used_item": most_used.sensor_name if most_used else None,
            "most_used_count": most_used.interaction_count if most_used else 0
        }
    
    def print_summary(self):
        """Print interaction summary to console"""
        summary = self._generate_summary()
        
        print("\n" + "="*60)
        print("ITEM SENSOR INTERACTION SUMMARY")
        print("="*60)
        print(f"📊 Total Interactions: {summary['total_interactions']}")
        print(f"⏱️  Total Time: {summary['total_interaction_time']:.1f}s")
        print(f"🎯 Unique Items Used: {summary['unique_items_used']}")
        print(f"🏆 Most Used: {summary['most_used_item']} ({summary['most_used_count']} times)")
        print("="*60)
        
        # Show per-item breakdown
        print("\nPer-Item Breakdown:")
        for sensor_id, sensor in sorted(self.sensors.items()):
            if sensor.interaction_count > 0:
                print(f"  {sensor.sensor_name} ({sensor_id}):")
                print(f"    - Uses: {sensor.interaction_count}")
                print(f"    - Total time: {sensor.total_interaction_time:.1f}s")
                if sensor.interaction_count > 0:
                    avg_time = sensor.total_interaction_time / sensor.interaction_count
                    print(f"    - Avg time: {avg_time:.1f}s")
        print()


# Global instance
_item_sensor_manager = None

def get_item_sensor_manager():
    """Get or create global item sensor manager"""
    global _item_sensor_manager
    if _item_sensor_manager is None:
        _item_sensor_manager = ItemSensorManager()
    return _item_sensor_manager


def setup_default_item_sensors():
    """Setup item sensors for ONLY objects available in Blender scene"""
    manager = get_item_sensor_manager()
    
    # ========================================
    # AVAILABLE OBJECTS IN BLENDER SCENE:
    # Phone, Stove, DiningTable, KitchenSink, BathroomSink1, BathroomSink2
    # ========================================
    
    # Kitchen items
    manager.register_item_sensor("I001", "Phone", "Phone", "Kitchen", "item")
    manager.register_item_sensor("I002", "Stove", "Stove", "Kitchen", "appliance")
    manager.register_item_sensor("I003", "DiningTable", "DiningTable", "DiningRoom", "furniture")
    manager.register_item_sensor("I004", "KitchenSink", "KitchenSink", "Kitchen", "appliance")
    
    # Bathroom items
    manager.register_item_sensor("I005", "BathroomSink1", "BathroomSink1", "Bathroom1", "appliance")
    manager.register_item_sensor("I006", "BathroomSink2", "BathroomSink2", "Bathroom2", "appliance")
    
    print("✅ Default item sensors configured (6 objects: Phone, Stove, DiningTable, KitchenSink, BathroomSink1, BathroomSink2)")
    return manager


if __name__ == "__main__":
    # Test the system
    print("🧪 Testing Item Sensor Manager\n")
    
    manager = setup_default_item_sensors()
    
    # Simulate some interactions
    print("\n📝 Simulating interactions...")
    manager.interact_with_object("Phone")
    time.sleep(2)
    manager.end_interaction("Phone")
    
    manager.interact_with_object("KitchenSink")
    time.sleep(5)
    manager.end_interaction("KitchenSink")
    
    manager.interact_with_object("Stove")
    time.sleep(3)
    manager.end_interaction("Stove")
    
    # Print summary
    manager.print_summary()
    
    # Export data
    manager.export_casas_format()
    manager.export_detailed_json()
