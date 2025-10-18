"""
VESPER Object Interaction Handler
Manages actor-object interactions in BGE with VLM-guided decision making
"""

import bge
import time
import json
import os
from datetime import datetime


class InteractionZone:
    """Defines an interaction zone around an object"""
    
    def __init__(self, object_name, interaction_distance=1.5, interaction_angle=45):
        self.object_name = object_name
        self.interaction_distance = interaction_distance  # Distance in Blender units
        self.interaction_angle = interaction_angle  # Degrees from forward direction
        self.is_in_range = False
        self.last_check_time = 0
    
    def check_actor_in_range(self, actor_pos, actor_orientation, object_pos):
        """Check if actor is in position to interact with object"""
        import math
        
        # Calculate distance
        distance = ((actor_pos[0] - object_pos[0])**2 + 
                   (actor_pos[1] - object_pos[1])**2)**0.5
        
        if distance > self.interaction_distance:
            self.is_in_range = False
            return False
        
        # Calculate angle to object (optional - for directional interaction)
        # For now, just use distance
        self.is_in_range = True
        return True


class ObjectInteractionHandler:
    """
    Handles all object interactions in VESPER
    Integrates with item sensors and VLM decision making
    """
    
    def __init__(self, item_sensor_manager=None):
        self.item_sensor_manager = item_sensor_manager
        
        # Interaction zones for all objects
        self.interaction_zones = {}
        
        # Current interaction state
        self.active_interaction = None
        self.interaction_start_time = None
        
        # Interaction history
        self.interaction_history = []
        
        # VLM interaction prompts
        self.interaction_prompts = {}
        
        print("✅ Object Interaction Handler initialized")
    
    def register_interactive_object(self, object_name, interaction_distance=1.5, 
                                   interaction_type="manual", interaction_duration=None):
        """
        Register an object as interactive
        
        Args:
            object_name: Blender object name
            interaction_distance: How close actor needs to be
            interaction_type: "manual" (requires action) or "auto" (proximity-based)
            interaction_duration: Fixed duration for auto-interactions (seconds)
        """
        zone = InteractionZone(object_name, interaction_distance)
        self.interaction_zones[object_name] = {
            "zone": zone,
            "type": interaction_type,
            "duration": interaction_duration,
            "available": True
        }
        
        print(f"🎯 Registered interactive object: {object_name} ({interaction_type})")
    
    def check_nearby_objects(self, actor_position, actor_orientation=None):
        """
        Check what objects are nearby and available for interaction
        Returns list of interactive objects in range
        """
        try:
            scene = bge.logic.getCurrentScene()
            nearby_objects = []
            
            for obj_name, obj_data in self.interaction_zones.items():
                if obj_name not in scene.objects:
                    continue
                
                obj = scene.objects[obj_name]
                zone = obj_data["zone"]
                
                if zone.check_actor_in_range(
                    actor_position, 
                    actor_orientation, 
                    obj.worldPosition
                ):
                    nearby_objects.append({
                        "object_name": obj_name,
                        "distance": ((actor_position[0] - obj.worldPosition[0])**2 + 
                                   (actor_position[1] - obj.worldPosition[1])**2)**0.5,
                        "interaction_type": obj_data["type"],
                        "available": obj_data["available"]
                    })
            
            return sorted(nearby_objects, key=lambda x: x["distance"])
            
        except Exception as e:
            print(f"⚠️ Nearby objects check failed: {e}")
            return []
    
    def start_interaction(self, object_name, task_context=None):
        """
        Start interacting with an object
        
        Args:
            object_name: Object to interact with
            task_context: Current task being performed (for logging)
        """
        if self.active_interaction:
            print(f"⚠️ Already interacting with {self.active_interaction}")
            return False
        
        if object_name not in self.interaction_zones:
            print(f"⚠️ Object not registered for interaction: {object_name}")
            return False
        
        # Start interaction
        self.active_interaction = object_name
        self.interaction_start_time = time.time()
        
        # Trigger item sensor if available
        if self.item_sensor_manager:
            self.item_sensor_manager.interact_with_object(
                object_name, 
                self.interaction_start_time
            )
        
        print(f"🤝 Started interaction with: {object_name}")
        if task_context:
            print(f"   Task context: {task_context}")
        
        return True
    
    def end_interaction(self, object_name=None):
        """
        End current interaction
        
        Args:
            object_name: Specific object to end interaction with (optional)
        """
        if not self.active_interaction:
            return False
        
        if object_name and object_name != self.active_interaction:
            print(f"⚠️ Not currently interacting with {object_name}")
            return False
        
        # Calculate duration
        end_time = time.time()
        duration = end_time - self.interaction_start_time
        
        # End item sensor tracking
        if self.item_sensor_manager:
            self.item_sensor_manager.end_interaction(
                self.active_interaction,
                end_time
            )
        
        # Record interaction
        interaction_record = {
            "object": self.active_interaction,
            "start_time": self.interaction_start_time,
            "end_time": end_time,
            "duration": duration
        }
        self.interaction_history.append(interaction_record)
        
        print(f"✋ Ended interaction with: {self.active_interaction} (Duration: {duration:.1f}s)")
        
        self.active_interaction = None
        self.interaction_start_time = None
        
        return True
    
    def auto_interact_with_nearby(self, actor_position, task_name=None):
        """
        Automatically interact with nearby objects based on task
        Returns object interacted with, or None
        """
        nearby = self.check_nearby_objects(actor_position)
        
        if not nearby:
            return None
        
        # For auto-interaction type objects, start interaction
        for obj in nearby:
            if obj["interaction_type"] == "auto" and obj["available"]:
                obj_data = self.interaction_zones[obj["object_name"]]
                
                # Start interaction
                if self.start_interaction(obj["object_name"], task_name):
                    
                    # If duration is specified, schedule auto-end
                    if obj_data["duration"]:
                        print(f"⏱️  Auto-interaction duration: {obj_data['duration']}s")
                        # Could use BGE timer here for auto-end
                    
                    return obj["object_name"]
        
        return None
    
    def get_interaction_prompt_for_vlm(self, nearby_objects, task_name):
        """
        Generate VLM prompt to decide which object to interact with
        
        Args:
            nearby_objects: List of nearby interactive objects
            task_name: Current task being performed
        
        Returns:
            Prompt string for VLM
        """
        if not nearby_objects:
            return None
        
        objects_list = "\n".join([
            f"- {obj['object_name']} (distance: {obj['distance']:.1f}m)"
            for obj in nearby_objects
        ])
        
        prompt = f"""TASK: {task_name}

NEARBY INTERACTIVE OBJECTS:
{objects_list}

Based on the task "{task_name}", which object should the actor interact with?

Respond with JSON:
{{
    "should_interact": true/false,
    "object_to_interact": "object_name",
    "interaction_duration": estimated_seconds,
    "reasoning": "why this object is needed for the task"
}}"""
        
        return prompt
    
    def vlm_guided_interaction(self, actor_position, task_name, vlm_func):
        """
        Use VLM to decide what to interact with
        
        Args:
            actor_position: Current actor position
            task_name: Current task
            vlm_func: VLM completion function
        
        Returns:
            Interaction decision from VLM
        """
        nearby = self.check_nearby_objects(actor_position)
        
        if not nearby:
            return None
        
        # Get VLM prompt
        prompt = self.get_interaction_prompt_for_vlm(nearby, task_name)
        
        try:
            # Call VLM (text-only for interaction decisions)
            response = vlm_func(prompt, images=None)
            
            # Parse response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group(0))
                
                if decision.get("should_interact"):
                    obj_name = decision.get("object_to_interact")
                    
                    if obj_name in [o["object_name"] for o in nearby]:
                        # Start interaction
                        self.start_interaction(obj_name, task_name)
                        
                        return {
                            "object": obj_name,
                            "duration": decision.get("interaction_duration", 5.0),
                            "reasoning": decision.get("reasoning", "")
                        }
            
        except Exception as e:
            print(f"⚠️ VLM interaction decision failed: {e}")
        
        return None
    
    def get_interaction_summary(self):
        """Get summary of all interactions"""
        total_interactions = len(self.interaction_history)
        total_time = sum(i["duration"] for i in self.interaction_history)
        
        if total_interactions == 0:
            return {
                "total_interactions": 0,
                "total_time": 0,
                "average_duration": 0,
                "objects_used": []
            }
        
        objects_used = {}
        for interaction in self.interaction_history:
            obj = interaction["object"]
            if obj not in objects_used:
                objects_used[obj] = {"count": 0, "total_time": 0}
            objects_used[obj]["count"] += 1
            objects_used[obj]["total_time"] += interaction["duration"]
        
        return {
            "total_interactions": total_interactions,
            "total_time": total_time,
            "average_duration": total_time / total_interactions,
            "objects_used": objects_used
        }


# Global instance
_interaction_handler = None

def get_interaction_handler():
    """Get or create global interaction handler"""
    global _interaction_handler
    if _interaction_handler is None:
        # Try to get item sensor manager
        try:
            from interaction_system.item_sensor_manager import get_item_sensor_manager
            sensor_manager = get_item_sensor_manager()
        except:
            sensor_manager = None
        
        _interaction_handler = ObjectInteractionHandler(sensor_manager)
    return _interaction_handler


def setup_default_interactions():
    """Setup common household interactions - ONLY objects available in Blender scene"""
    handler = get_interaction_handler()
    
    # ========================================
    # AVAILABLE OBJECTS IN BLENDER SCENE:
    # Phone, Stove, DiningTable, KitchenSink, BathroomSink1, BathroomSink2
    # ========================================
    
    # Kitchen interactions (auto-interact for task-based usage)
    handler.register_interactive_object("KitchenSink", 1.5, "auto", 20.0)  # 20 sec wash hands
    handler.register_interactive_object("Stove", 1.5, "auto", 30.0)  # 30 sec cook
    
    # Bathroom interactions (auto-interact for hygiene tasks)
    handler.register_interactive_object("BathroomSink1", 1.5, "auto", 20.0)  # 20 sec wash hands
    handler.register_interactive_object("BathroomSink2", 1.5, "auto", 20.0)  # 20 sec wash hands
    
    # Items (auto-interact when very close)
    handler.register_interactive_object("Phone", 1.0, "auto", 10.0)  # 10 sec phone call
    
    # Furniture (auto-interact for tasks like eating)
    handler.register_interactive_object("DiningTable", 1.5, "auto", 15.0)  # 15 sec eating/sitting
    
    print("✅ Default interactions configured (6 objects: Phone, Stove, DiningTable, KitchenSink, BathroomSink1, BathroomSink2)")
    return handler


if __name__ == "__main__":
    print("🧪 Testing Object Interaction Handler\n")
    
    # This would normally run in BGE context
    print("⚠️ This module requires BGE context to run")
    print("✅ Module loaded successfully")
