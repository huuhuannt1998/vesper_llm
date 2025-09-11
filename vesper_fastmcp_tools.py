"""
VESPER FastMCP Tools Architecture
=================================

Enhanced VLM navigation system using FastMCP to modularize capabilities
into specialized tools that VLMs can invoke based on context and need.
"""

from fastmcp import FastMCP
import asyncio
import json
import base64
import bpy
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from mathutils import Vector
import os
import tempfile

# Initialize FastMCP server
mcp = FastMCP("VESPER Navigation Tools")

# ============================================================================
# CORE TOOL 1: MULTI-VIEW IMAGE ANALYSIS
# ============================================================================

@mcp.tool()
def capture_dual_view_images(include_first_person: bool = True, 
                           include_bird_eye: bool = True,
                           include_reference: bool = False) -> Dict[str, Any]:
    """
    Capture multiple camera views for comprehensive scene analysis.
    
    Args:
        include_first_person: Capture first-person view from actor
        include_bird_eye: Capture bird's-eye view for navigation
        include_reference: Include static reference layout image
        
    Returns:
        Dictionary with base64-encoded images and metadata
    """
    try:
        results = {
            "views_captured": [],
            "actor_position": None,
            "timestamp": None
        }
        
        # Get actor reference
        actor = bpy.data.objects.get("Actor")
        if not actor:
            return {"error": "Actor not found in scene"}
            
        results["actor_position"] = {
            "x": actor.location.x,
            "y": actor.location.y, 
            "z": actor.location.z
        }
        
        scene = bpy.context.scene
        original_camera = scene.camera
        
        # 1. FIRST-PERSON VIEW
        if include_first_person:
            # Create/find first-person camera attached to actor
            fp_camera = bpy.data.objects.get("FirstPersonCamera")
            if not fp_camera:
                bpy.ops.object.camera_add()
                fp_camera = bpy.context.object
                fp_camera.name = "FirstPersonCamera"
                
                # Parent to actor for movement
                fp_camera.parent = actor
                fp_camera.parent_type = 'OBJECT'
            
            # Position at actor eye level, looking forward
            fp_camera.location = (actor.location.x, actor.location.y, actor.location.z + 1.6)
            fp_camera.rotation_euler = actor.rotation_euler
            
            # Configure for human-like view
            fp_camera.data.lens = 35  # Natural field of view
            fp_camera.data.sensor_width = 36
            
            # Capture first-person screenshot
            scene.camera = fp_camera
            scene.render.resolution_x = 1024
            scene.render.resolution_y = 768
            
            fp_path = os.path.join(tempfile.gettempdir(), "vesper_first_person.png")
            scene.render.filepath = fp_path
            bpy.ops.render.render(write_still=True)
            
            if os.path.exists(fp_path):
                with open(fp_path, "rb") as f:
                    fp_b64 = base64.b64encode(f.read()).decode('utf-8')
                results["first_person_view"] = fp_b64
                results["views_captured"].append("first_person")
                os.remove(fp_path)
        
        # 2. BIRD'S-EYE VIEW  
        if include_bird_eye:
            # Create/update bird's-eye camera
            be_camera = bpy.data.objects.get("BirdEyeCamera")
            if not be_camera:
                bpy.ops.object.camera_add()
                be_camera = bpy.context.object
                be_camera.name = "BirdEyeCamera"
            
            # Position above actor
            be_camera.location = (actor.location.x, actor.location.y, 15.0)
            be_camera.rotation_euler = (0, 0, 0)  # Point straight down
            be_camera.data.type = 'ORTHO'
            be_camera.data.ortho_scale = 12
            
            # Capture bird's-eye screenshot
            scene.camera = be_camera
            scene.render.resolution_x = 800
            scene.render.resolution_y = 800
            
            be_path = os.path.join(tempfile.gettempdir(), "vesper_bird_eye.png")
            scene.render.filepath = be_path
            bpy.ops.render.render(write_still=True)
            
            if os.path.exists(be_path):
                with open(be_path, "rb") as f:
                    be_b64 = base64.b64encode(f.read()).decode('utf-8')
                results["bird_eye_view"] = be_b64
                results["views_captured"].append("bird_eye")
                os.remove(be_path)
        
        # 3. REFERENCE LAYOUT
        if include_reference:
            ref_path = "/path/to/house_layout_reference.png"  # Update with actual path
            if os.path.exists(ref_path):
                with open(ref_path, "rb") as f:
                    ref_b64 = base64.b64encode(f.read()).decode('utf-8')
                results["reference_layout"] = ref_b64
                results["views_captured"].append("reference")
        
        # Restore original camera
        scene.camera = original_camera
        
        results["timestamp"] = bpy.context.scene.frame_current
        return results
        
    except Exception as e:
        return {"error": f"Image capture failed: {str(e)}"}


@mcp.tool()
def analyze_room_from_images(first_person_b64: str = None, 
                           bird_eye_b64: str = None) -> Dict[str, Any]:
    """
    Analyze room type and furniture from captured images.
    
    Args:
        first_person_b64: Base64 first-person view image
        bird_eye_b64: Base64 bird's-eye view image
        
    Returns:
        Room analysis with furniture detection and room classification
    """
    analysis = {
        "room_type": "UNKNOWN",
        "confidence": 0.0,
        "furniture_detected": [],
        "spatial_features": {},
        "recommendations": []
    }
    
    # Get actor for spatial context
    actor = bpy.data.objects.get("Actor")
    if actor:
        analysis["actor_position"] = {
            "x": round(actor.location.x, 2),
            "y": round(actor.location.y, 2),
            "room_boundaries": _get_room_boundaries(actor.location)
        }
    
    # Analyze visible objects near actor (Blender scene analysis)
    nearby_objects = _get_nearby_objects(actor.location if actor else Vector((0,0,0)), radius=3.0)
    
    # Room classification based on furniture
    room_indicators = {
        "KITCHEN": ["stove", "oven", "refrigerator", "sink", "counter", "cabinet"],
        "BEDROOM": ["bed", "dresser", "wardrobe", "nightstand", "pillow"],  
        "LIVING_ROOM": ["sofa", "couch", "tv", "coffee_table", "entertainment"],
        "BATHROOM": ["toilet", "bathtub", "shower", "sink", "mirror"],
        "OFFICE": ["desk", "computer", "chair", "bookshelf"],
        "GARAGE": ["car", "tools", "workbench"]
    }
    
    room_scores = {}
    for room_type, indicators in room_indicators.items():
        score = sum(1 for obj in nearby_objects if any(ind in obj.name.lower() for ind in indicators))
        room_scores[room_type] = score / len(indicators)
    
    if room_scores:
        best_room = max(room_scores, key=room_scores.get)
        analysis["room_type"] = best_room
        analysis["confidence"] = room_scores[best_room]
        analysis["furniture_detected"] = [obj.name for obj in nearby_objects]
    
    # Add spatial analysis
    if actor:
        analysis["spatial_features"] = {
            "near_walls": _check_wall_proximity(actor.location),
            "open_paths": _get_available_directions(actor.location),
            "room_center_distance": _distance_to_room_center(actor.location, analysis["room_type"])
        }
    
    return analysis


# ============================================================================
# CORE TOOL 2: SPATIAL AWARENESS & COORDINATES
# ============================================================================

@mcp.tool() 
def get_spatial_context() -> Dict[str, Any]:
    """
    Get comprehensive spatial context including actor position, room layout,
    and navigation possibilities.
    
    Returns:
        Complete spatial analysis for navigation planning
    """
    try:
        actor = bpy.data.objects.get("Actor")
        if not actor:
            return {"error": "Actor not found"}
            
        context = {
            "actor_position": {
                "x": round(actor.location.x, 2),
                "y": round(actor.location.y, 2), 
                "z": round(actor.location.z, 2),
                "rotation": [round(r, 2) for r in actor.rotation_euler]
            },
            "room_layout": {},
            "navigation_options": {},
            "obstacles": [],
            "targets": []
        }
        
        # Map all rooms and their boundaries
        rooms = _detect_all_rooms()
        context["room_layout"] = rooms
        
        # Current room identification
        current_room = _identify_current_room(actor.location)
        context["current_room"] = current_room
        
        # Available movement directions
        directions = _analyze_movement_options(actor.location)
        context["navigation_options"] = directions
        
        # Detect obstacles within movement range
        obstacles = _detect_obstacles(actor.location, radius=2.0)
        context["obstacles"] = obstacles
        
        # Find navigation targets (doors, furniture, exits)
        targets = _find_navigation_targets(actor.location, radius=5.0)
        context["targets"] = targets
        
        # Path suggestions to major rooms
        path_suggestions = {}
        for room_name, room_data in rooms.items():
            if room_name != current_room:
                path = _suggest_path(actor.location, room_data["center"])
                path_suggestions[room_name] = path
        context["path_suggestions"] = path_suggestions
        
        return context
        
    except Exception as e:
        return {"error": f"Spatial analysis failed: {str(e)}"}


@mcp.tool()
def get_room_connectivity_map() -> Dict[str, Any]:
    """
    Generate a connectivity map showing how rooms connect to each other.
    
    Returns:
        Room connectivity graph for navigation planning
    """
    try:
        connectivity = {
            "rooms": {},
            "connections": [],
            "navigation_graph": {}
        }
        
        # Get all rooms
        rooms = _detect_all_rooms()
        
        for room_name, room_data in rooms.items():
            connectivity["rooms"][room_name] = {
                "center": room_data["center"],
                "bounds": room_data["bounds"],
                "area": room_data["area"],
                "furniture_count": len(room_data.get("furniture", []))
            }
            
            # Find connections to other rooms
            connections = []
            for other_room, other_data in rooms.items():
                if other_room != room_name:
                    connection = _check_room_connection(room_data, other_data)
                    if connection:
                        connections.append({
                            "to_room": other_room,
                            "connection_type": connection["type"],  # door, opening, corridor
                            "distance": connection["distance"],
                            "direction": connection["direction"]
                        })
            
            connectivity["navigation_graph"][room_name] = connections
        
        return connectivity
        
    except Exception as e:
        return {"error": f"Connectivity mapping failed: {str(e)}"}


# ============================================================================
# CORE TOOL 3: ACTION EXECUTION & CONTROL
# ============================================================================

@mcp.tool()
def execute_movement_action(action_type: str, 
                          direction: str = None,
                          target_position: List[float] = None,
                          steps: int = 1) -> Dict[str, Any]:
    """
    Execute various movement actions for the actor.
    
    Args:
        action_type: "step", "turn", "goto", "explore", "stop"
        direction: "UP", "DOWN", "LEFT", "RIGHT", "FORWARD", "BACK"
        target_position: [x, y, z] coordinates for "goto" action
        steps: Number of steps for movement actions
        
    Returns:
        Movement execution result with new position and status
    """
    try:
        actor = bpy.data.objects.get("Actor")
        if not actor:
            return {"error": "Actor not found"}
            
        result = {
            "action_executed": action_type,
            "previous_position": [round(actor.location.x, 2), round(actor.location.y, 2), round(actor.location.z, 2)],
            "new_position": None,
            "movement_successful": False,
            "obstacles_encountered": [],
            "status": ""
        }
        
        step_size = 0.5  # meters per step
        
        if action_type == "step":
            # Single step movement
            offset = _direction_to_offset(direction, step_size * steps)
            new_pos = Vector(actor.location) + Vector(offset)
            
            # Check for obstacles
            obstacles = _check_path_obstacles(actor.location, new_pos)
            if not obstacles:
                actor.location = new_pos
                result["movement_successful"] = True
                result["status"] = f"Moved {steps} step(s) {direction}"
            else:
                result["obstacles_encountered"] = obstacles
                result["status"] = f"Movement blocked by obstacles: {obstacles}"
                
        elif action_type == "turn":
            # Rotation action
            rotation_amount = {"LEFT": -90, "RIGHT": 90, "AROUND": 180}.get(direction, 0)
            actor.rotation_euler.z += np.radians(rotation_amount)
            result["movement_successful"] = True
            result["status"] = f"Turned {direction} ({rotation_amount} degrees)"
            
        elif action_type == "goto":
            # Navigate to specific coordinates
            if target_position:
                path = _plan_path(actor.location, Vector(target_position))
                if path:
                    # Execute first step of path
                    next_pos = path[1] if len(path) > 1 else Vector(target_position)
                    actor.location = next_pos
                    result["movement_successful"] = True
                    result["status"] = f"Moving toward target {target_position}"
                    result["remaining_path"] = [[round(p.x, 2), round(p.y, 2), round(p.z, 2)] for p in path[1:]]
                else:
                    result["status"] = "No valid path to target"
                    
        elif action_type == "explore":
            # Exploratory movement toward interesting areas
            exploration_target = _find_exploration_target(actor.location)
            if exploration_target:
                direction_to_target = _get_direction_to_target(actor.location, exploration_target)
                offset = _direction_to_offset(direction_to_target, step_size)
                actor.location = Vector(actor.location) + Vector(offset)
                result["movement_successful"] = True
                result["status"] = f"Exploring toward {exploration_target}"
            else:
                result["status"] = "No exploration targets found"
                
        elif action_type == "stop":
            # Stop all movement
            result["movement_successful"] = True
            result["status"] = "Movement stopped"
        
        result["new_position"] = [round(actor.location.x, 2), round(actor.location.y, 2), round(actor.location.z, 2)]
        return result
        
    except Exception as e:
        return {"error": f"Movement execution failed: {str(e)}"}


@mcp.tool()
def execute_interaction_action(interaction_type: str, 
                             target_object: str = None) -> Dict[str, Any]:
    """
    Execute interaction with environment objects.
    
    Args:
        interaction_type: "open", "close", "use", "examine", "pickup"
        target_object: Name of object to interact with
        
    Returns:
        Interaction result with sensor activations and state changes
    """
    try:
        actor = bpy.data.objects.get("Actor")
        if not actor:
            return {"error": "Actor not found"}
            
        result = {
            "interaction_type": interaction_type,
            "target_object": target_object,
            "interaction_successful": False,
            "sensor_activations": [],
            "state_changes": [],
            "feedback": ""
        }
        
        # Find target object
        target = bpy.data.objects.get(target_object) if target_object else None
        if not target:
            # Find nearby interactable objects
            nearby_objects = _get_nearby_objects(actor.location, radius=2.0)
            interactable = [obj for obj in nearby_objects if _is_interactable(obj)]
            if interactable:
                target = interactable[0]
                result["target_object"] = target.name
                result["feedback"] = f"Auto-selected nearby object: {target.name}"
            else:
                return {"error": "No interactable objects found nearby"}
        
        # Execute interaction based on type and object
        if interaction_type == "open" and "door" in target.name.lower():
            # Door interaction
            result["sensor_activations"].append(f"Door_{target.name}_OPEN")
            result["state_changes"].append(f"{target.name} opened")
            result["interaction_successful"] = True
            
        elif interaction_type == "use" and any(x in target.name.lower() for x in ["stove", "sink", "toilet"]):
            # Appliance interaction
            result["sensor_activations"].extend([
                f"Motion_sensor_{_get_current_room()}_ON",
                f"{target.name}_ACTIVATED"
            ])
            result["state_changes"].append(f"{target.name} activated")
            result["interaction_successful"] = True
            
        elif interaction_type == "examine":
            # Examination interaction
            result["sensor_activations"].append(f"Motion_sensor_{_get_current_room()}_ON")
            result["feedback"] = f"Examined {target.name}: {_get_object_description(target)}"
            result["interaction_successful"] = True
        
        return result
        
    except Exception as e:
        return {"error": f"Interaction failed: {str(e)}"}


# ============================================================================
# ADDITIONAL TOOLS FOR ENHANCED CAPABILITIES  
# ============================================================================

@mcp.tool()
def get_task_context_analysis(current_task: str) -> Dict[str, Any]:
    """
    Analyze the current task to provide context-specific guidance.
    
    Args:
        current_task: Description of the task to perform
        
    Returns:
        Task analysis with recommended actions and target locations
    """
    try:
        analysis = {
            "task": current_task,
            "task_type": "unknown",
            "target_room": None,
            "required_objects": [],
            "action_sequence": [],
            "success_criteria": "",
            "estimated_duration": 0
        }
        
        task_lower = current_task.lower()
        
        # Task classification and planning
        if any(x in task_lower for x in ["cook", "kitchen", "meal", "food"]):
            analysis.update({
                "task_type": "cooking",
                "target_room": "KITCHEN", 
                "required_objects": ["stove", "sink", "refrigerator"],
                "action_sequence": [
                    "Navigate to kitchen",
                    "Examine cooking equipment", 
                    "Use stove/appliances",
                    "Complete cooking task"
                ],
                "success_criteria": "Located in kitchen with appliance interaction",
                "estimated_duration": 120  # seconds
            })
            
        elif any(x in task_lower for x in ["sleep", "bedroom", "bed", "rest"]):
            analysis.update({
                "task_type": "resting",
                "target_room": "BEDROOM",
                "required_objects": ["bed"],
                "action_sequence": [
                    "Navigate to bedroom",
                    "Locate bed",
                    "Approach bed area"
                ],
                "success_criteria": "Located in bedroom near bed",
                "estimated_duration": 60
            })
            
        elif any(x in task_lower for x in ["bathroom", "toilet", "wash", "shower"]):
            analysis.update({
                "task_type": "hygiene",
                "target_room": "BATHROOM",
                "required_objects": ["toilet", "sink", "shower"],
                "action_sequence": [
                    "Navigate to bathroom",
                    "Use bathroom facilities",
                    "Complete hygiene activities"
                ],
                "success_criteria": "Located in bathroom with facility interaction",
                "estimated_duration": 90
            })
            
        elif any(x in task_lower for x in ["living", "watch", "tv", "relax"]):
            analysis.update({
                "task_type": "entertainment",
                "target_room": "LIVING_ROOM",
                "required_objects": ["sofa", "tv", "chair"],
                "action_sequence": [
                    "Navigate to living room",
                    "Find seating",
                    "Engage in leisure activity"
                ],
                "success_criteria": "Located in living room near seating",
                "estimated_duration": 180
            })
        
        # Add current position context
        actor = bpy.data.objects.get("Actor")
        if actor:
            current_room = _identify_current_room(actor.location)
            analysis["current_room"] = current_room
            
            if analysis["target_room"] and analysis["target_room"] != current_room:
                path_suggestion = _suggest_path_to_room(actor.location, analysis["target_room"])
                analysis["navigation_guidance"] = path_suggestion
            else:
                analysis["navigation_guidance"] = "Already in target room or no specific room required"
        
        return analysis
        
    except Exception as e:
        return {"error": f"Task analysis failed: {str(e)}"}


@mcp.tool()
def get_navigation_history_analysis() -> Dict[str, Any]:
    """
    Analyze recent navigation history to identify patterns and issues.
    
    Returns:
        Analysis of movement patterns, efficiency, and recommendations
    """
    try:
        # This would access navigation logs stored in Blender or external file
        history = {
            "recent_positions": [],
            "movement_patterns": {},
            "efficiency_metrics": {},
            "stuck_detection": False,
            "recommendations": []
        }
        
        # Get recent position history from game logic
        if hasattr(bpy.context.scene, 'game_settings'):
            position_history = getattr(bpy.context.scene.game_settings, 'position_history', [])
            
            if len(position_history) > 1:
                history["recent_positions"] = position_history[-10:]  # Last 10 positions
                
                # Detect repetitive movement (stuck behavior)
                recent_coords = [f"{p[0]:.1f},{p[1]:.1f}" for p in position_history[-5:]]
                if len(set(recent_coords)) <= 2:
                    history["stuck_detection"] = True
                    history["recommendations"].append("Try different movement direction - possible stuck behavior detected")
                
                # Calculate movement efficiency
                total_distance = sum(_distance_between_points(position_history[i], position_history[i+1]) 
                                   for i in range(len(position_history)-1))
                direct_distance = _distance_between_points(position_history[0], position_history[-1])
                
                if total_distance > 0:
                    efficiency = direct_distance / total_distance
                    history["efficiency_metrics"] = {
                        "path_efficiency": round(efficiency, 3),
                        "total_distance": round(total_distance, 2),
                        "direct_distance": round(direct_distance, 2)
                    }
                    
                    if efficiency < 0.5:
                        history["recommendations"].append("Consider more direct navigation path")
        
        return history
        
    except Exception as e:
        return {"error": f"History analysis failed: {str(e)}"}


@mcp.tool()
def simulate_sensor_network() -> Dict[str, Any]:
    """
    Simulate smart home sensor network based on actor position and actions.
    
    Returns:
        Current sensor states and activations for CASAS dataset generation
    """
    try:
        actor = bpy.data.objects.get("Actor")
        if not actor:
            return {"error": "Actor not found"}
            
        sensors = {
            "motion_sensors": {},
            "door_sensors": {},
            "appliance_sensors": {},
            "environmental_sensors": {},
            "timestamp": bpy.context.scene.frame_current
        }
        
        current_room = _identify_current_room(actor.location)
        
        # Motion sensor activation based on room presence
        for room in ["KITCHEN", "BEDROOM", "LIVING_ROOM", "BATHROOM", "OFFICE"]:
            sensor_id = f"M{_get_room_sensor_id(room)}"
            sensors["motion_sensors"][sensor_id] = {
                "state": "ON" if room == current_room else "OFF",
                "room": room,
                "last_triggered": bpy.context.scene.frame_current if room == current_room else None
            }
        
        # Door sensors (triggered when crossing thresholds)
        door_interactions = _check_door_interactions(actor.location)
        for door_name, state in door_interactions.items():
            sensor_id = f"D{_get_door_sensor_id(door_name)}"
            sensors["door_sensors"][sensor_id] = {
                "state": state,
                "door": door_name,
                "triggered": state == "OPEN"
            }
        
        # Appliance sensors (based on proximity and interaction)
        nearby_appliances = _get_nearby_appliances(actor.location)
        for appliance in nearby_appliances:
            sensor_id = f"A{_get_appliance_sensor_id(appliance.name)}"
            sensors["appliance_sensors"][sensor_id] = {
                "state": "STANDBY",  # Would be "ACTIVE" during actual use
                "appliance": appliance.name,
                "room": current_room
            }
        
        # Environmental sensors (temperature, light, etc.)
        sensors["environmental_sensors"] = {
            "TEMP_001": {"value": 22.5, "unit": "celsius", "room": current_room},
            "LIGHT_001": {"value": 75, "unit": "percent", "room": current_room}
        }
        
        return sensors
        
    except Exception as e:
        return {"error": f"Sensor simulation failed: {str(e)}"}


# ============================================================================
# HELPER FUNCTIONS (would be implemented based on your Blender scene)
# ============================================================================

def _get_nearby_objects(position: Vector, radius: float) -> List:
    """Get objects within radius of position"""
    nearby = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            distance = (Vector(obj.location) - position).length
            if distance <= radius:
                nearby.append(obj)
    return nearby

def _direction_to_offset(direction: str, step_size: float) -> Tuple[float, float, float]:
    """Convert direction string to 3D offset"""
    offsets = {
        "UP": (0, step_size, 0),
        "DOWN": (0, -step_size, 0), 
        "LEFT": (-step_size, 0, 0),
        "RIGHT": (step_size, 0, 0),
        "FORWARD": (0, step_size, 0),
        "BACK": (0, -step_size, 0)
    }
    return offsets.get(direction, (0, 0, 0))

def _identify_current_room(position: Vector) -> str:
    """Identify which room the position is in"""
    # This would use your room boundary detection logic
    return "UNKNOWN"

def _detect_all_rooms() -> Dict[str, Dict]:
    """Detect all rooms in the scene"""
    # This would analyze your Blender scene structure
    return {}

def _check_path_obstacles(start_pos: Vector, end_pos: Vector) -> List[str]:
    """Check for obstacles between two positions"""
    # This would use Blender's collision detection
    return []

# Additional helper functions would be implemented based on your specific Blender setup...

if __name__ == "__main__":
    print("🚀 VESPER FastMCP Tools Server Starting...")
    print("📡 Available Tools:")
    print("   1. 🖼️  Multi-View Image Analysis") 
    print("   2. 🗺️  Spatial Awareness & Coordinates")
    print("   3. 🎮 Action Execution & Control")
    print("   4. 📋 Task Context Analysis")
    print("   5. 📊 Navigation History Analysis") 
    print("   6. 🏠 Smart Home Sensor Simulation")
    
    # Start the FastMCP server
    mcp.run()
