#!/usr/bin/env python3
"""
VESPER ADL Enhancement - Phase 1: Object Interaction Foundation

Implementation starter for object detection and interaction system in Blender.
This is the foundation for all ADL task capabilities.

Phase 1 Goals:
- Detect 8 CASAS objects (oatmeal, raisins, brown_sugar, bowl, measuring_spoon, medicine, pot, phone_book)
- Implement pick/place mechanics
- Integrate with item sensors (I01-I08)
- Track object states and locations
"""

import bge
import mathutils
from typing import Dict, List, Tuple, Optional, Any
import json
import time

class CASASObjectManager:
    """Manages CASAS-compatible objects in Blender environment"""
    
    def __init__(self):
        self.casas_objects = {
            "I01": {"name": "oatmeal", "location": "kitchen_cabinet", "state": "PRESENT"},
            "I02": {"name": "raisins", "location": "kitchen_cabinet", "state": "PRESENT"}, 
            "I03": {"name": "brown_sugar", "location": "kitchen_cabinet", "state": "PRESENT"},
            "I04": {"name": "bowl", "location": "kitchen_cabinet", "state": "PRESENT"},
            "I05": {"name": "measuring_spoon", "location": "kitchen_drawer", "state": "PRESENT"},
            "I06": {"name": "medicine", "location": "bathroom_cabinet", "state": "PRESENT"},
            "I07": {"name": "pot", "location": "kitchen_cabinet", "state": "PRESENT"},
            "I08": {"name": "phone_book", "location": "dining_room_table", "state": "PRESENT"}
        }
        
        self.object_positions = {}
        self.actor_inventory = []
        self.interaction_range = 2.0  # meters
        
    def detect_nearby_objects(self, actor_position: Tuple[float, float, float]) -> List[Dict[str, Any]]:
        """Detect CASAS objects within interaction range of actor"""
        nearby_objects = []
        
        scene = bge.logic.getCurrentScene()
        
        for sensor_id, obj_data in self.casas_objects.items():
            # Find object in scene
            obj_name = obj_data["name"]
            
            try:
                blender_obj = scene.objects[obj_name]
                obj_position = blender_obj.worldPosition
                
                # Calculate distance to actor
                distance = mathutils.Vector(actor_position).distance(mathutils.Vector(obj_position))
                
                if distance <= self.interaction_range and obj_data["state"] == "PRESENT":
                    nearby_objects.append({
                        "sensor_id": sensor_id,
                        "name": obj_name,
                        "position": list(obj_position),
                        "distance": distance,
                        "blender_object": blender_obj
                    })
                    
            except KeyError:
                print(f"⚠️  Object '{obj_name}' not found in Blender scene")
                
        return sorted(nearby_objects, key=lambda x: x["distance"])
    
    def pick_up_object(self, sensor_id: str, actor_position: Tuple[float, float, float]) -> bool:
        """Pick up a CASAS object and trigger item sensor"""
        if sensor_id not in self.casas_objects:
            print(f"❌ Unknown object sensor: {sensor_id}")
            return False
            
        obj_data = self.casas_objects[sensor_id]
        
        if obj_data["state"] != "PRESENT":
            print(f"❌ Object {obj_data['name']} is not available")
            return False
            
        nearby_objects = self.detect_nearby_objects(actor_position)
        target_object = None
        
        for obj in nearby_objects:
            if obj["sensor_id"] == sensor_id:
                target_object = obj
                break
                
        if not target_object:
            print(f"❌ Object {obj_data['name']} is not within range")
            return False
            
        # Update object state
        self.casas_objects[sensor_id]["state"] = "ABSENT"
        self.actor_inventory.append(sensor_id)
        
        # Trigger item sensor event
        self.trigger_item_sensor(sensor_id, "ABSENT")
        
        # Hide object in Blender (simulate picking up)
        target_object["blender_object"].setVisible(False)
        
        print(f"✅ Picked up {obj_data['name']} (sensor {sensor_id})")
        return True
    
    def place_object(self, sensor_id: str, location: str) -> bool:
        """Place an object from inventory at specified location"""
        if sensor_id not in self.actor_inventory:
            print(f"❌ Object {sensor_id} not in inventory")
            return False
            
        obj_data = self.casas_objects[sensor_id]
        
        # Update object state
        self.casas_objects[sensor_id]["state"] = "PRESENT"
        self.casas_objects[sensor_id]["location"] = location
        self.actor_inventory.remove(sensor_id)
        
        # Trigger item sensor event
        self.trigger_item_sensor(sensor_id, "PRESENT")
        
        # Show object in Blender (simulate placing)
        scene = bge.logic.getCurrentScene()
        try:
            blender_obj = scene.objects[obj_data["name"]]
            blender_obj.setVisible(True)
        except KeyError:
            pass
            
        print(f"✅ Placed {obj_data['name']} at {location} (sensor {sensor_id})")
        return True
    
    def trigger_item_sensor(self, sensor_id: str, state: str):
        """Trigger CASAS item sensor event"""
        timestamp = time.time()
        
        # Log sensor event in CASAS format
        sensor_event = {
            "timestamp": timestamp,
            "sensor": sensor_id,
            "message": state,
            "object_name": self.casas_objects[sensor_id]["name"]
        }
        
        # Send to sensor logging system
        self.log_sensor_event(sensor_event)
        
        # Trigger virtual smart home sensor if available
        try:
            self.trigger_virtual_sensor(sensor_id, state)
        except Exception as e:
            print(f"⚠️  Virtual sensor trigger failed: {e}")
    
    def log_sensor_event(self, event: Dict[str, Any]):
        """Log sensor event for CASAS dataset generation"""
        # This would integrate with your existing sensor logging system
        print(f"📊 SENSOR EVENT: {event['sensor']} = {event['message']} ({event['object_name']})")
        
        # Append to evaluation log
        if hasattr(bge.logic, 'evaluation_log'):
            if 'sensor_events' not in bge.logic.evaluation_log:
                bge.logic.evaluation_log['sensor_events'] = []
            bge.logic.evaluation_log['sensor_events'].append(event)
    
    def trigger_virtual_sensor(self, sensor_id: str, state: str):
        """Trigger virtual smart home item sensor"""
        # Integration with your existing virtual sensor system
        import requests
        
        # Map sensor ID to port (item sensors use ports 9200-9299)
        base_port = 9200
        sensor_number = int(sensor_id[1:])  # Extract number from I01, I02, etc.
        port = base_port + sensor_number
        
        try:
            requests.post(f"http://localhost:{port}/trigger", json={
                "sensor_id": sensor_id,
                "state": state,
                "timestamp": time.time()
            }, timeout=1)
        except requests.RequestException:
            pass  # Virtual sensor not available
    
    def get_inventory_status(self) -> List[Dict[str, Any]]:
        """Get current actor inventory status"""
        inventory = []
        for sensor_id in self.actor_inventory:
            obj_data = self.casas_objects[sensor_id]
            inventory.append({
                "sensor_id": sensor_id,
                "name": obj_data["name"],
                "picked_up_from": obj_data["location"]
            })
        return inventory


class VLMObjectInteraction:
    """VLM-driven object interaction system"""
    
    def __init__(self):
        self.object_manager = CASASObjectManager()
        self.interaction_history = []
        
    def analyze_scene_for_objects(self, screenshot_path: str, actor_position: Tuple[float, float, float]) -> Dict[str, Any]:
        """Use VLM to analyze scene and identify interactable objects"""
        nearby_objects = self.object_manager.detect_nearby_objects(actor_position)
        
        if not nearby_objects:
            return {"objects_detected": [], "recommendations": []}
            
        # Prepare object information for VLM
        object_descriptions = []
        for obj in nearby_objects:
            object_descriptions.append(f"{obj['name']} (sensor {obj['sensor_id']}) at distance {obj['distance']:.1f}m")
        
        # This would integrate with your existing VLM system
        vlm_prompt = f"""
        You are controlling an actor in a smart home environment. 
        
        Current task: Complete ADL activities using available objects.
        Actor position: {actor_position}
        
        Available objects nearby:
        {chr(10).join(object_descriptions)}
        
        Based on the screenshot and available objects, what should the actor do next?
        Consider ADL tasks: cooking, cleaning, medication, communication.
        
        Respond with:
        1. Target object to interact with (if any)
        2. Action to take (pick_up, examine, ignore)
        3. Reasoning for decision
        """
        
        # Placeholder for VLM integration
        return {
            "objects_detected": nearby_objects,
            "vlm_recommendation": "pick_up oatmeal for cooking task",
            "target_object": nearby_objects[0] if nearby_objects else None
        }
    
    def execute_vlm_object_action(self, vlm_response: Dict[str, Any], actor_position: Tuple[float, float, float]) -> bool:
        """Execute object interaction based on VLM recommendation"""
        if not vlm_response.get("target_object"):
            return False
            
        target_obj = vlm_response["target_object"]
        sensor_id = target_obj["sensor_id"]
        
        # Execute the recommended action
        if "pick_up" in vlm_response.get("vlm_recommendation", "").lower():
            success = self.object_manager.pick_up_object(sensor_id, actor_position)
            
            if success:
                self.interaction_history.append({
                    "action": "pick_up",
                    "object": target_obj["name"],
                    "sensor_id": sensor_id,
                    "timestamp": time.time(),
                    "position": actor_position
                })
                
            return success
            
        return False


# Integration with existing VLM navigation system
def integrate_object_interaction_with_navigation():
    """Integration point with existing llm_bge_navigation.py"""
    
    # Initialize object interaction system
    if not hasattr(bge.logic, 'object_interaction'):
        bge.logic.object_interaction = VLMObjectInteraction()
    
    # Get current actor position
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    
    if not actor:
        return
        
    actor_pos = tuple(actor.worldPosition)
    
    # Analyze scene for objects (integrate with existing screenshot system)
    screenshot_path = getattr(bge.logic, 'latest_screenshot', None)
    
    if screenshot_path:
        object_analysis = bge.logic.object_interaction.analyze_scene_for_objects(
            screenshot_path, actor_pos
        )
        
        # Execute object interaction if VLM recommends it
        if object_analysis.get("target_object"):
            bge.logic.object_interaction.execute_vlm_object_action(object_analysis, actor_pos)


# Test function for Phase 1 development
def test_object_interaction_system():
    """Test the object interaction system"""
    print("🧪 Testing CASAS Object Interaction System...")
    
    # Initialize system
    obj_manager = CASASObjectManager()
    
    # Simulate actor position in kitchen
    actor_pos = (2.0, 1.0, 0.0)
    
    # Test object detection
    nearby = obj_manager.detect_nearby_objects(actor_pos)
    print(f"📍 Found {len(nearby)} nearby objects")
    
    # Test object pickup
    if nearby:
        sensor_id = nearby[0]["sensor_id"]
        success = obj_manager.pick_up_object(sensor_id, actor_pos)
        if success:
            print(f"✅ Successfully picked up object")
            
            # Test inventory
            inventory = obj_manager.get_inventory_status()
            print(f"🎒 Inventory: {inventory}")
            
            # Test placing object
            obj_manager.place_object(sensor_id, "counter")
            print(f"✅ Successfully placed object")
    
    print("🧪 Object interaction system test complete!")


if __name__ == "__main__":
    # Run tests when executed directly
    test_object_interaction_system()
