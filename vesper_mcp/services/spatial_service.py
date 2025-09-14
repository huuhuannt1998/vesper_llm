"""
Spatial Awareness Service
========================

Dedicated service for spatial awareness, position tracking, and room detection.
Extracted from monolithic vesper_mcp_server.py to provide focused spatial navigation capabilities.
"""

import asyncio
import os
from typing import Dict, Any, List, Tuple, Optional
import logging
import json
import math

from mcp import FastMCP, types
import bpy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance for spatial service
mcp = FastMCP("Spatial Awareness Service")

# Configuration
SPATIAL_SERVICE_PORT = 8003

# Room definitions and spatial data
ROOM_BOUNDARIES = {
    "living_room": {
        "bounds": {"x_min": -5, "x_max": 5, "y_min": -5, "y_max": 5, "z_min": 0, "z_max": 3},
        "center": (0, 0, 1.5),
        "connections": ["kitchen", "hallway"]
    },
    "kitchen": {
        "bounds": {"x_min": 5, "x_max": 10, "y_min": -3, "y_max": 3, "z_min": 0, "z_max": 3},
        "center": (7.5, 0, 1.5),
        "connections": ["living_room", "dining_room"]
    },
    "bedroom": {
        "bounds": {"x_min": -10, "x_max": -5, "y_min": -3, "y_max": 3, "z_min": 0, "z_max": 3},
        "center": (-7.5, 0, 1.5),
        "connections": ["hallway"]
    },
    "bathroom": {
        "bounds": {"x_min": -10, "x_max": -7, "y_min": 3, "y_max": 6, "z_min": 0, "z_max": 3},
        "center": (-8.5, 4.5, 1.5),
        "connections": ["hallway"]
    },
    "hallway": {
        "bounds": {"x_min": -7, "x_max": -3, "y_min": -1, "y_max": 1, "z_min": 0, "z_max": 3},
        "center": (-5, 0, 1.5),
        "connections": ["living_room", "bedroom", "bathroom"]
    }
}

@mcp.tool()
async def get_current_position(
    actor_name: str = "Actor"
) -> Dict[str, Any]:
    """
    Get the current 3D position of the specified actor.
    
    Args:
        actor_name: Name of the actor object
        
    Returns:
        Dictionary with current position and orientation
    """
    try:
        # Check if we're in Blender
        if 'bpy' not in globals():
            return {
                "success": False,
                "error": "Not running in Blender environment"
            }
        
        # Find the actor object
        actor = bpy.data.objects.get(actor_name)
        if not actor:
            return {
                "success": False,
                "error": f"Actor '{actor_name}' not found in scene"
            }
        
        # Get position and rotation
        position = list(actor.location)
        rotation = list(actor.rotation_euler)
        
        # Calculate additional spatial information
        spatial_info = await _calculate_spatial_context(position, rotation)
        
        return {
            "success": True,
            "actor_name": actor_name,
            "position": {
                "x": position[0],
                "y": position[1],
                "z": position[2]
            },
            "rotation": {
                "x": rotation[0],
                "y": rotation[1],
                "z": rotation[2]
            },
            "spatial_context": spatial_info
        }
        
    except Exception as e:
        logger.error(f"Error getting current position: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def _calculate_spatial_context(position: List[float], rotation: List[float]) -> Dict[str, Any]:
    """Calculate spatial context information"""
    x, y, z = position
    
    # Determine current room
    current_room = await _detect_current_room(position)
    
    # Calculate distances to room centers
    room_distances = {}
    for room_name, room_data in ROOM_BOUNDARIES.items():
        center = room_data["center"]
        distance = math.sqrt((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2)
        room_distances[room_name] = round(distance, 2)
    
    # Find nearest rooms
    sorted_rooms = sorted(room_distances.items(), key=lambda x: x[1])
    nearest_rooms = sorted_rooms[:3]
    
    # Calculate facing direction
    facing_direction = _calculate_facing_direction(rotation[2])  # Z rotation (yaw)
    
    return {
        "current_room": current_room,
        "room_distances": room_distances,
        "nearest_rooms": [{"room": room, "distance": dist} for room, dist in nearest_rooms],
        "facing_direction": facing_direction,
        "height": z
    }

async def _detect_current_room(position: List[float]) -> str:
    """Detect which room the position is currently in"""
    x, y, z = position
    
    for room_name, room_data in ROOM_BOUNDARIES.items():
        bounds = room_data["bounds"]
        if (bounds["x_min"] <= x <= bounds["x_max"] and
            bounds["y_min"] <= y <= bounds["y_max"] and
            bounds["z_min"] <= z <= bounds["z_max"]):
            return room_name
    
    return "unknown"

def _calculate_facing_direction(yaw_radians: float) -> str:
    """Calculate cardinal direction from yaw angle"""
    # Convert radians to degrees and normalize
    yaw_degrees = math.degrees(yaw_radians) % 360
    
    if 337.5 <= yaw_degrees or yaw_degrees < 22.5:
        return "North"
    elif 22.5 <= yaw_degrees < 67.5:
        return "Northeast"
    elif 67.5 <= yaw_degrees < 112.5:
        return "East"
    elif 112.5 <= yaw_degrees < 157.5:
        return "Southeast"
    elif 157.5 <= yaw_degrees < 202.5:
        return "South"
    elif 202.5 <= yaw_degrees < 247.5:
        return "Southwest"
    elif 247.5 <= yaw_degrees < 292.5:
        return "West"
    else:  # 292.5 <= yaw_degrees < 337.5
        return "Northwest"

@mcp.tool()
async def detect_room(
    position: Optional[List[float]] = None,
    actor_name: str = "Actor"
) -> Dict[str, Any]:
    """
    Detect which room a position is in.
    
    Args:
        position: Optional 3D position [x, y, z]. If not provided, uses actor's current position
        actor_name: Name of actor to get position from if position not provided
        
    Returns:
        Dictionary with room detection results
    """
    try:
        # Get position if not provided
        if position is None:
            pos_result = await get_current_position(actor_name)
            if not pos_result["success"]:
                return pos_result
            position = [
                pos_result["position"]["x"],
                pos_result["position"]["y"],
                pos_result["position"]["z"]
            ]
        
        # Detect room
        current_room = await _detect_current_room(position)
        
        # Get room information
        room_info = {}
        if current_room in ROOM_BOUNDARIES:
            room_data = ROOM_BOUNDARIES[current_room]
            room_info = {
                "bounds": room_data["bounds"],
                "center": room_data["center"],
                "connections": room_data["connections"]
            }
        
        # Calculate position within room
        relative_position = {}
        if current_room in ROOM_BOUNDARIES:
            bounds = ROOM_BOUNDARIES[current_room]["bounds"]
            relative_position = {
                "x_percent": ((position[0] - bounds["x_min"]) / (bounds["x_max"] - bounds["x_min"])) * 100,
                "y_percent": ((position[1] - bounds["y_min"]) / (bounds["y_max"] - bounds["y_min"])) * 100,
                "z_percent": ((position[2] - bounds["z_min"]) / (bounds["z_max"] - bounds["z_min"])) * 100
            }
        
        return {
            "success": True,
            "position": position,
            "current_room": current_room,
            "room_info": room_info,
            "relative_position": relative_position,
            "is_valid_room": current_room != "unknown"
        }
        
    except Exception as e:
        logger.error(f"Error detecting room: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_navigation_context(
    actor_name: str = "Actor",
    target_room: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive navigation context for the actor.
    
    Args:
        actor_name: Name of the actor
        target_room: Optional target room for path planning
        
    Returns:
        Dictionary with navigation context
    """
    try:
        # Get current position and room
        position_result = await get_current_position(actor_name)
        if not position_result["success"]:
            return position_result
        
        current_position = [
            position_result["position"]["x"],
            position_result["position"]["y"],
            position_result["position"]["z"]
        ]
        
        current_room = position_result["spatial_context"]["current_room"]
        
        # Calculate navigation options
        navigation_options = []
        
        if current_room in ROOM_BOUNDARIES:
            connected_rooms = ROOM_BOUNDARIES[current_room]["connections"]
            
            for connected_room in connected_rooms:
                if connected_room in ROOM_BOUNDARIES:
                    center = ROOM_BOUNDARIES[connected_room]["center"]
                    distance = math.sqrt(
                        (current_position[0] - center[0])**2 +
                        (current_position[1] - center[1])**2 +
                        (current_position[2] - center[2])**2
                    )
                    
                    navigation_options.append({
                        "room": connected_room,
                        "center": center,
                        "distance": round(distance, 2),
                        "direction": _calculate_direction_to_target(current_position, center)
                    })
        
        # Sort by distance
        navigation_options.sort(key=lambda x: x["distance"])
        
        # Path planning if target specified
        path_info = {}
        if target_room:
            path_info = await _plan_path_to_room(current_room, target_room)
        
        return {
            "success": True,
            "actor_name": actor_name,
            "current_position": current_position,
            "current_room": current_room,
            "navigation_options": navigation_options,
            "total_rooms": len(ROOM_BOUNDARIES),
            "path_to_target": path_info
        }
        
    except Exception as e:
        logger.error(f"Error getting navigation context: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def _calculate_direction_to_target(from_pos: List[float], to_pos: Tuple[float, float, float]) -> str:
    """Calculate direction from one position to another"""
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    
    angle = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle) % 360
    
    if 337.5 <= angle_degrees or angle_degrees < 22.5:
        return "East"
    elif 22.5 <= angle_degrees < 67.5:
        return "Northeast"
    elif 67.5 <= angle_degrees < 112.5:
        return "North"
    elif 112.5 <= angle_degrees < 157.5:
        return "Northwest"
    elif 157.5 <= angle_degrees < 202.5:
        return "West"
    elif 202.5 <= angle_degrees < 247.5:
        return "Southwest"
    elif 247.5 <= angle_degrees < 292.5:
        return "South"
    else:  # 292.5 <= angle_degrees < 337.5
        return "Southeast"

async def _plan_path_to_room(from_room: str, to_room: str) -> Dict[str, Any]:
    """Plan a path from one room to another"""
    if from_room == to_room:
        return {
            "path": [from_room],
            "distance": 0,
            "steps": 0,
            "status": "already_at_destination"
        }
    
    # Simple pathfinding using room connections
    visited = set()
    queue = [(from_room, [from_room], 0)]
    
    while queue:
        current_room, path, distance = queue.pop(0)
        
        if current_room == to_room:
            return {
                "path": path,
                "distance": round(distance, 2),
                "steps": len(path) - 1,
                "status": "path_found"
            }
        
        if current_room in visited:
            continue
        
        visited.add(current_room)
        
        if current_room in ROOM_BOUNDARIES:
            for connected in ROOM_BOUNDARIES[current_room]["connections"]:
                if connected not in visited:
                    # Calculate distance between rooms
                    center1 = ROOM_BOUNDARIES[current_room]["center"]
                    center2 = ROOM_BOUNDARIES[connected]["center"]
                    step_distance = math.sqrt(
                        (center1[0] - center2[0])**2 +
                        (center1[1] - center2[1])**2 +
                        (center1[2] - center2[2])**2
                    )
                    
                    queue.append((connected, path + [connected], distance + step_distance))
    
    return {
        "path": [],
        "distance": -1,
        "steps": -1,
        "status": "no_path_found"
    }

@mcp.tool()
async def get_room_layout() -> Dict[str, Any]:
    """
    Get the complete room layout and spatial information.
    
    Returns:
        Dictionary with room layout data
    """
    try:
        return {
            "success": True,
            "rooms": ROOM_BOUNDARIES,
            "total_rooms": len(ROOM_BOUNDARIES),
            "room_connections": {
                room: data["connections"] 
                for room, data in ROOM_BOUNDARIES.items()
            },
            "room_centers": {
                room: data["center"] 
                for room, data in ROOM_BOUNDARIES.items()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting room layout: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def calculate_distance_between_points(
    point1: List[float],
    point2: List[float]
) -> Dict[str, Any]:
    """
    Calculate distance between two 3D points.
    
    Args:
        point1: First point as [x, y, z]
        point2: Second point as [x, y, z]
        
    Returns:
        Dictionary with distance calculation
    """
    try:
        if len(point1) != 3 or len(point2) != 3:
            return {
                "success": False,
                "error": "Points must be 3D coordinates [x, y, z]"
            }
        
        # Calculate 3D distance
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        dz = point2[2] - point1[2]
        
        distance_3d = math.sqrt(dx**2 + dy**2 + dz**2)
        distance_2d = math.sqrt(dx**2 + dy**2)  # Horizontal distance only
        
        # Calculate direction
        direction = _calculate_direction_to_target(point1, point2)
        
        return {
            "success": True,
            "point1": point1,
            "point2": point2,
            "distance_3d": round(distance_3d, 2),
            "distance_2d": round(distance_2d, 2),
            "height_difference": round(dz, 2),
            "direction": direction,
            "displacement": {
                "x": round(dx, 2),
                "y": round(dy, 2),
                "z": round(dz, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error calculating distance: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Service health check
@mcp.tool()
async def spatial_service_health() -> Dict[str, Any]:
    """Check spatial service health and capabilities"""
    try:
        # Check Blender availability
        blender_available = 'bpy' in globals()
        
        return {
            "success": True,
            "service": "Spatial Awareness Service",
            "status": "healthy",
            "blender_available": blender_available,
            "capabilities": [
                "get_current_position",
                "detect_room",
                "get_navigation_context",
                "get_room_layout",
                "calculate_distance_between_points"
            ],
            "room_count": len(ROOM_BOUNDARIES),
            "available_rooms": list(ROOM_BOUNDARIES.keys())
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }

def main():
    """Run the Spatial Awareness Service"""
    logger.info(f"Starting Spatial Awareness Service on port {SPATIAL_SERVICE_PORT}")
    mcp.run(port=SPATIAL_SERVICE_PORT)

if __name__ == "__main__":
    main()
