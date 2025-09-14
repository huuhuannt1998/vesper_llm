"""
Movement Control Service
=======================

Dedicated service for actor movement and path execution.
Extracted from monolithic vesper_mcp_server.py to provide focused movement control capabilities.
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

# Create FastMCP instance for movement service
mcp = FastMCP("Movement Control Service")

# Configuration
MOVEMENT_SERVICE_PORT = 8004

# Movement configuration
MOVEMENT_CONFIG = {
    "default_speed": 2.0,  # Blender units per second
    "rotation_speed": 1.0,  # Radians per second
    "step_size": 0.5,  # Default step size for incremental movement
    "collision_threshold": 0.5,  # Distance to avoid collisions
    "max_movement_distance": 10.0  # Maximum single movement distance
}

@mcp.tool()
async def move_actor_to_position(
    target_position: List[float],
    actor_name: str = "Actor",
    movement_speed: Optional[float] = None,
    check_collisions: bool = True
) -> Dict[str, Any]:
    """
    Move actor to a specific 3D position.
    
    Args:
        target_position: Target position as [x, y, z]
        actor_name: Name of the actor to move
        movement_speed: Optional movement speed override
        check_collisions: Whether to check for collisions
        
    Returns:
        Dictionary with movement execution results
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
        
        # Validate target position
        if len(target_position) != 3:
            return {
                "success": False,
                "error": "Target position must be [x, y, z]"
            }
        
        # Get current position
        current_position = list(actor.location)
        
        # Calculate movement distance
        distance = math.sqrt(
            (target_position[0] - current_position[0])**2 +
            (target_position[1] - current_position[1])**2 +
            (target_position[2] - current_position[2])**2
        )
        
        # Check if movement is within limits
        if distance > MOVEMENT_CONFIG["max_movement_distance"]:
            return {
                "success": False,
                "error": f"Movement distance {distance:.2f} exceeds maximum {MOVEMENT_CONFIG['max_movement_distance']}"
            }
        
        # Perform collision check if requested
        collision_result = {}
        if check_collisions:
            collision_result = await _check_movement_collision(current_position, target_position, actor_name)
            if not collision_result["safe"]:
                return {
                    "success": False,
                    "error": "Movement blocked by collision",
                    "collision_info": collision_result
                }
        
        # Execute movement
        movement_result = await _execute_movement(actor, target_position, movement_speed)
        
        return {
            "success": True,
            "actor_name": actor_name,
            "start_position": current_position,
            "target_position": target_position,
            "distance_moved": round(distance, 2),
            "movement_time": movement_result.get("time", 0),
            "collision_check": collision_result,
            "final_position": list(actor.location)
        }
        
    except Exception as e:
        logger.error(f"Error moving actor to position: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def _check_movement_collision(start_pos: List[float], end_pos: List[float], actor_name: str) -> Dict[str, Any]:
    """Check for collisions along movement path"""
    # Simple collision detection - in real implementation would use raycasting
    
    # Calculate path segments
    num_segments = 10
    collision_points = []
    
    for i in range(num_segments + 1):
        t = i / num_segments
        check_pos = [
            start_pos[0] + t * (end_pos[0] - start_pos[0]),
            start_pos[1] + t * (end_pos[1] - start_pos[1]),
            start_pos[2] + t * (end_pos[2] - start_pos[2])
        ]
        
        # Simple bounds checking (would be more sophisticated in real implementation)
        if check_pos[2] < 0:  # Below ground
            collision_points.append({
                "position": check_pos,
                "type": "ground_collision",
                "segment": i
            })
    
    return {
        "safe": len(collision_points) == 0,
        "collision_points": collision_points,
        "segments_checked": num_segments + 1
    }

async def _execute_movement(actor, target_position: List[float], speed: Optional[float]) -> Dict[str, Any]:
    """Execute the actual movement"""
    movement_speed = speed or MOVEMENT_CONFIG["default_speed"]
    
    # Calculate movement time
    current_pos = list(actor.location)
    distance = math.sqrt(
        (target_position[0] - current_pos[0])**2 +
        (target_position[1] - current_pos[1])**2 +
        (target_position[2] - current_pos[2])**2
    )
    
    movement_time = distance / movement_speed
    
    # Update actor position (immediate for now, could be animated)
    actor.location = target_position
    
    # Update scene
    bpy.context.view_layer.update()
    
    return {
        "time": round(movement_time, 2),
        "speed": movement_speed
    }

@mcp.tool()
async def move_actor_relative(
    displacement: List[float],
    actor_name: str = "Actor",
    local_coordinates: bool = False
) -> Dict[str, Any]:
    """
    Move actor by a relative displacement.
    
    Args:
        displacement: Displacement vector as [dx, dy, dz]
        actor_name: Name of the actor to move
        local_coordinates: Whether displacement is in local actor coordinates
        
    Returns:
        Dictionary with movement results
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
        
        # Validate displacement
        if len(displacement) != 3:
            return {
                "success": False,
                "error": "Displacement must be [dx, dy, dz]"
            }
        
        # Get current position
        current_position = list(actor.location)
        
        # Calculate target position
        if local_coordinates:
            # Transform displacement to world coordinates
            rotation_matrix = actor.rotation_euler.to_matrix()
            world_displacement = rotation_matrix @ displacement
            target_position = [
                current_position[0] + world_displacement[0],
                current_position[1] + world_displacement[1],
                current_position[2] + world_displacement[2]
            ]
        else:
            # World coordinates
            target_position = [
                current_position[0] + displacement[0],
                current_position[1] + displacement[1],
                current_position[2] + displacement[2]
            ]
        
        # Execute movement using absolute movement function
        return await move_actor_to_position(target_position, actor_name, check_collisions=True)
        
    except Exception as e:
        logger.error(f"Error moving actor relatively: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def rotate_actor(
    rotation_change: List[float],
    actor_name: str = "Actor",
    absolute_rotation: bool = False
) -> Dict[str, Any]:
    """
    Rotate actor by specified angles.
    
    Args:
        rotation_change: Rotation change as [rx, ry, rz] in radians
        actor_name: Name of the actor to rotate
        absolute_rotation: Whether to set absolute rotation vs relative change
        
    Returns:
        Dictionary with rotation results
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
        
        # Validate rotation
        if len(rotation_change) != 3:
            return {
                "success": False,
                "error": "Rotation must be [rx, ry, rz] in radians"
            }
        
        # Get current rotation
        current_rotation = list(actor.rotation_euler)
        
        # Calculate new rotation
        if absolute_rotation:
            new_rotation = rotation_change
        else:
            new_rotation = [
                current_rotation[0] + rotation_change[0],
                current_rotation[1] + rotation_change[1],
                current_rotation[2] + rotation_change[2]
            ]
        
        # Apply rotation
        actor.rotation_euler = new_rotation
        
        # Update scene
        bpy.context.view_layer.update()
        
        return {
            "success": True,
            "actor_name": actor_name,
            "previous_rotation": current_rotation,
            "rotation_change": rotation_change,
            "new_rotation": new_rotation,
            "absolute_rotation": absolute_rotation
        }
        
    except Exception as e:
        logger.error(f"Error rotating actor: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def move_to_room(
    target_room: str,
    actor_name: str = "Actor",
    position_in_room: str = "center"
) -> Dict[str, Any]:
    """
    Move actor to a specific room.
    
    Args:
        target_room: Name of the target room
        actor_name: Name of the actor to move
        position_in_room: Where in room to position ("center", "entrance", "random")
        
    Returns:
        Dictionary with movement results
    """
    try:
        # Import spatial service functionality (in real implementation would call spatial service)
        from .spatial_service import ROOM_BOUNDARIES
        
        if target_room not in ROOM_BOUNDARIES:
            return {
                "success": False,
                "error": f"Unknown room: {target_room}",
                "available_rooms": list(ROOM_BOUNDARIES.keys())
            }
        
        room_data = ROOM_BOUNDARIES[target_room]
        
        # Calculate target position based on position_in_room
        if position_in_room == "center":
            target_position = list(room_data["center"])
        elif position_in_room == "entrance":
            # Position near room entrance (simplified)
            center = room_data["center"]
            bounds = room_data["bounds"]
            # Position closer to the room's edge (entrance side)
            target_position = [
                center[0],
                bounds["y_min"] + 0.5,  # Near entrance
                center[2]
            ]
        elif position_in_room == "random":
            # Random position within room bounds
            import random
            bounds = room_data["bounds"]
            target_position = [
                random.uniform(bounds["x_min"] + 0.5, bounds["x_max"] - 0.5),
                random.uniform(bounds["y_min"] + 0.5, bounds["y_max"] - 0.5),
                random.uniform(bounds["z_min"] + 0.1, bounds["z_max"] - 0.1)
            ]
        else:
            return {
                "success": False,
                "error": f"Invalid position_in_room: {position_in_room}. Use 'center', 'entrance', or 'random'"
            }
        
        # Execute movement
        movement_result = await move_actor_to_position(target_position, actor_name)
        
        if movement_result["success"]:
            movement_result.update({
                "target_room": target_room,
                "position_in_room": position_in_room,
                "room_center": room_data["center"],
                "room_bounds": room_data["bounds"]
            })
        
        return movement_result
        
    except Exception as e:
        logger.error(f"Error moving to room: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def execute_movement_path(
    path_points: List[List[float]],
    actor_name: str = "Actor",
    movement_speed: Optional[float] = None,
    pause_between_points: float = 0.0
) -> Dict[str, Any]:
    """
    Execute a movement path with multiple waypoints.
    
    Args:
        path_points: List of [x, y, z] positions to move through
        actor_name: Name of the actor to move
        movement_speed: Optional movement speed override
        pause_between_points: Pause time between waypoints in seconds
        
    Returns:
        Dictionary with path execution results
    """
    try:
        if not path_points:
            return {
                "success": False,
                "error": "Path points list is empty"
            }
        
        # Validate all path points
        for i, point in enumerate(path_points):
            if len(point) != 3:
                return {
                    "success": False,
                    "error": f"Path point {i} must be [x, y, z], got {point}"
                }
        
        # Get starting position
        actor = bpy.data.objects.get(actor_name)
        if not actor:
            return {
                "success": False,
                "error": f"Actor '{actor_name}' not found in scene"
            }
        
        start_position = list(actor.location)
        execution_log = []
        total_distance = 0.0
        
        # Execute movement to each point
        for i, target_point in enumerate(path_points):
            current_pos = list(actor.location)
            
            # Calculate segment distance
            segment_distance = math.sqrt(
                (target_point[0] - current_pos[0])**2 +
                (target_point[1] - current_pos[1])**2 +
                (target_point[2] - current_pos[2])**2
            )
            
            # Move to point
            move_result = await move_actor_to_position(target_point, actor_name, movement_speed, check_collisions=True)
            
            execution_log.append({
                "waypoint": i,
                "target_position": target_point,
                "segment_distance": round(segment_distance, 2),
                "success": move_result["success"],
                "error": move_result.get("error", None)
            })
            
            if not move_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to reach waypoint {i}: {move_result.get('error', 'Unknown error')}",
                    "completed_waypoints": i,
                    "execution_log": execution_log
                }
            
            total_distance += segment_distance
            
            # Pause if requested
            if pause_between_points > 0 and i < len(path_points) - 1:
                await asyncio.sleep(pause_between_points)
        
        final_position = list(actor.location)
        
        return {
            "success": True,
            "actor_name": actor_name,
            "start_position": start_position,
            "final_position": final_position,
            "total_waypoints": len(path_points),
            "total_distance": round(total_distance, 2),
            "execution_log": execution_log,
            "average_segment_distance": round(total_distance / len(path_points), 2) if path_points else 0
        }
        
    except Exception as e:
        logger.error(f"Error executing movement path: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_movement_capabilities(
    actor_name: str = "Actor"
) -> Dict[str, Any]:
    """
    Get movement capabilities and constraints for the actor.
    
    Args:
        actor_name: Name of the actor to check
        
    Returns:
        Dictionary with movement capabilities
    """
    try:
        # Check if actor exists
        if 'bpy' in globals():
            actor = bpy.data.objects.get(actor_name)
            actor_exists = actor is not None
            current_position = list(actor.location) if actor else None
        else:
            actor_exists = False
            current_position = None
        
        return {
            "success": True,
            "actor_name": actor_name,
            "actor_exists": actor_exists,
            "current_position": current_position,
            "movement_config": MOVEMENT_CONFIG,
            "capabilities": {
                "absolute_positioning": True,
                "relative_movement": True,
                "rotation_control": True,
                "room_navigation": True,
                "path_execution": True,
                "collision_detection": True
            },
            "constraints": {
                "max_single_movement": MOVEMENT_CONFIG["max_movement_distance"],
                "collision_avoidance": MOVEMENT_CONFIG["collision_threshold"],
                "ground_constraint": True
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting movement capabilities: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Service health check
@mcp.tool()
async def movement_service_health() -> Dict[str, Any]:
    """Check movement service health and capabilities"""
    try:
        # Check Blender availability
        blender_available = 'bpy' in globals()
        
        return {
            "success": True,
            "service": "Movement Control Service",
            "status": "healthy",
            "blender_available": blender_available,
            "capabilities": [
                "move_actor_to_position",
                "move_actor_relative",
                "rotate_actor",
                "move_to_room",
                "execute_movement_path",
                "get_movement_capabilities"
            ],
            "movement_config": MOVEMENT_CONFIG
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }

def main():
    """Run the Movement Control Service"""
    logger.info(f"Starting Movement Control Service on port {MOVEMENT_SERVICE_PORT}")
    mcp.run(port=MOVEMENT_SERVICE_PORT)

if __name__ == "__main__":
    main()
