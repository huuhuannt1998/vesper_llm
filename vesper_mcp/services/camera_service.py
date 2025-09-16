"""
Camera & Visual Input Service
============================

Dedicated service for dual-camera management and image capture.
Provides both bird-eye and first-person camera capture tools for MCP agents.
The VLM agent can intelligently choose which camera view to capture based on context.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from mcp import FastMCP, types
import bpy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance for camera service
mcp = FastMCP("Dual Camera Service")

# Configuration
CAMERA_SERVICE_PORT = 8001
BIRD_EYE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "captures", "bird_eye")
FIRST_PERSON_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "captures", "first_person")
os.makedirs(BIRD_EYE_DIR, exist_ok=True)
os.makedirs(FIRST_PERSON_DIR, exist_ok=True)

@mcp.tool()
async def setup_first_person_camera(
    actor_name: str = "Actor"
) -> Dict[str, Any]:
    """
    Set up first-person camera for the specified actor in Blender BGE.
    
    Args:
        actor_name: Name of the actor object to attach camera to
        
    Returns:
        Dictionary with setup status and camera configuration
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
        
        # Create or get first-person camera
        camera_name = f"{actor_name}_FirstPersonCamera"
        camera = bpy.data.objects.get(camera_name)
        
        if not camera:
            # Create new camera
            bpy.ops.object.camera_add()
            camera = bpy.context.active_object
            camera.name = camera_name
            
            # Create camera data with specific settings
            camera_data = camera.data
            camera_data.name = f"{camera_name}_Data"
            camera_data.lens = 35  # Appropriate focal length for first-person view
            camera_data.clip_start = 0.1
            camera_data.clip_end = 100.0
        
        # Position camera at actor's eye level
        camera.parent = actor
        camera.parent_type = 'OBJECT'
        
        # Set camera position relative to actor (eye-level offset)
        camera.location = (0, 0, 1.6)  # 1.6 meters for human eye height
        camera.rotation_euler = (0, 0, 0)  # Looking forward
        
        # Set as active camera for rendering
        scene = bpy.context.scene
        scene.camera = camera
        
        logger.info(f"First-person camera setup complete for {actor_name}")
        
        return {
            "success": True,
            "camera_name": camera_name,
            "actor_name": actor_name,
            "position": list(camera.location),
            "rotation": list(camera.rotation_euler),
            "lens": camera.data.lens
        }
        
    except Exception as e:
        logger.error(f"Error setting up first-person camera: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def capture_bird_eye_view(
    filename: Optional[str] = None,
    resolution_x: int = 1024,
    resolution_y: int = 768
) -> Dict[str, Any]:
    """
    Capture bird-eye view screenshot for spatial navigation and room layout understanding.
    
    Use this tool when you need:
    - Overall room layout and spatial relationships
    - Path planning and obstacle avoidance
    - Understanding furniture arrangement
    - Navigation context and room transitions
    
    Args:
        filename: Optional custom filename (auto-generated if not provided)
        resolution_x: Image width in pixels
        resolution_y: Image height in pixels
        
    Returns:
        Dictionary with capture results and file path
    """
    try:
        # Generate filename if not provided
        if not filename:
            import time
            timestamp = int(time.time() * 1000)
            filename = f"bird-eye_{timestamp}.png"
        
        # Ensure .png extension
        if not filename.endswith('.png'):
            filename += '.png'
        
        filepath = os.path.join(BIRD_EYE_DIR, filename)
        
        # Configure render settings for bird-eye view
        scene = bpy.context.scene
        render = scene.render
        
        # Store original settings
        original_resolution_x = render.resolution_x
        original_resolution_y = render.resolution_y
        original_filepath = render.filepath
        original_camera = scene.camera
        
        try:
            # Find bird-eye camera
            bird_eye_camera = None
            for obj in bpy.data.objects:
                if obj.type == 'CAMERA' and 'bird' in obj.name.lower():
                    bird_eye_camera = obj
                    break
            
            if not bird_eye_camera:
                return {
                    "success": False,
                    "error": "Bird-eye camera not found. Please create a camera with 'bird' in its name."
                }
            
            # Set bird-eye camera as active
            scene.camera = bird_eye_camera
            
            # Configure render settings
            render.resolution_x = resolution_x
            render.resolution_y = resolution_y
            render.filepath = filepath
            render.image_settings.file_format = 'PNG'
            
            # Ensure bird-eye camera is positioned appropriately
            if bird_eye_camera.location.z < 5.0:
                logger.warning(f"Bird-eye camera height is {bird_eye_camera.location.z:.1f}. Consider positioning it higher (Z > 8) for better overview.")
            
            # Render the image
            bpy.ops.render.render(write_still=True)
            
            # Verify file was created
            if not os.path.exists(filepath):
                return {
                    "success": False,
                    "error": "Screenshot file was not created"
                }
            
            file_size = os.path.getsize(filepath)
            
            logger.info(f"Bird-eye screenshot captured: {filename} ({file_size} bytes)")
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "camera_used": bird_eye_camera.name,
                "file_size": file_size,
                "resolution": f"{resolution_x}x{resolution_y}",
                "camera_type": "bird_eye",
                "description": "Top-down view for spatial navigation and room layout"
            }
            
        finally:
            # Restore original settings
            render.resolution_x = original_resolution_x
            render.resolution_y = original_resolution_y
            render.filepath = original_filepath
            if original_camera:
                scene.camera = original_camera
        
    except Exception as e:
        logger.error(f"Error capturing bird-eye view: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def capture_first_person_view(
    actor_name: str = "Actor",
    filename: Optional[str] = None,
    resolution_x: int = 1024,
    resolution_y: int = 768
) -> Dict[str, Any]:
    """
    Capture first-person view screenshot from actor's eye-level perspective.
    
    Use this tool when you need:
    - Detailed object interaction and identification
    - Understanding what's directly accessible to the actor
    - Reading labels, signs, or fine details
    - Precise positioning and manipulation context
    
    Args:
        actor_name: Name of the actor whose perspective to capture
        filename: Optional custom filename (auto-generated if not provided)
        resolution_x: Image width in pixels
        resolution_y: Image height in pixels
        
    Returns:
        Dictionary with capture results and file path
    """
    try:
        # Ensure camera is set up
        camera_setup = await setup_first_person_camera(actor_name)
        if not camera_setup["success"]:
            return camera_setup
        
        # Generate filename if not provided
        if not filename:
            import time
            timestamp = int(time.time() * 1000)
            filename = f"first_person_{actor_name}_{timestamp}.png"
        
        # Ensure .png extension
        if not filename.endswith('.png'):
            filename += '.png'
        
        filepath = os.path.join(FIRST_PERSON_DIR, filename)
        
        # Configure render settings
        scene = bpy.context.scene
        render = scene.render
        
        # Store original settings
        original_resolution_x = render.resolution_x
        original_resolution_y = render.resolution_y
        original_filepath = render.filepath
        
        # Set render parameters
        render.resolution_x = resolution_x
        render.resolution_y = resolution_y
        render.resolution_percentage = 100
        render.filepath = filepath
        
        # Ensure we're using the first-person camera
        camera_name = f"{actor_name}_FirstPersonCamera"
        camera = bpy.data.objects.get(camera_name)
        if camera:
            scene.camera = camera
        
        # Render the image
        bpy.ops.render.render(write_still=True)
        
        # Restore original settings
        render.resolution_x = original_resolution_x
        render.resolution_y = original_resolution_y
        render.filepath = original_filepath
        
        # Verify file was created
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            logger.info(f"First-person screenshot captured: {filepath} ({file_size} bytes)")
            
            return {
                "success": True,
                "filepath": filepath,
                "filename": filename,
                "resolution": [resolution_x, resolution_y],
                "file_size": file_size,
                "actor_name": actor_name,
                "camera_name": camera_name
            }
        else:
            return {
                "success": False,
                "error": "Screenshot file was not created"
            }
            
    except Exception as e:
        logger.error(f"Error capturing first-person view: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_camera_recommendations(
    current_task: str,
    actor_position: Optional[str] = None,
    recent_actions: Optional[str] = None,
    current_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get intelligent camera selection recommendations based on current context.
    
    This tool helps you decide whether to use bird-eye or first-person view
    based on your current task and situation.
    
    Args:
        current_task: Description of the current task or goal
        actor_position: Current actor position and room information
        recent_actions: Recent movement or action history
        current_context: Additional context about the situation
        
    Returns:
        Dictionary with camera recommendations and reasoning
    """
    try:
        recommendations = {
            "bird_eye": {
                "score": 0,
                "reasons": []
            },
            "first_person": {
                "score": 0,
                "reasons": []
            }
        }
        
        task_lower = current_task.lower() if current_task else ""
        
        # Analyze task requirements
        if any(word in task_lower for word in ["navigate", "go to", "move to", "find room", "explore"]):
            recommendations["bird_eye"]["score"] += 3
            recommendations["bird_eye"]["reasons"].append("Navigation tasks benefit from spatial overview")
        
        if any(word in task_lower for word in ["use", "interact", "read", "operate", "cook", "clean"]):
            recommendations["first_person"]["score"] += 3
            recommendations["first_person"]["reasons"].append("Interaction tasks need detailed object view")
        
        if any(word in task_lower for word in ["stuck", "lost", "confused", "path"]):
            recommendations["bird_eye"]["score"] += 2
            recommendations["bird_eye"]["reasons"].append("Problem-solving benefits from room layout view")
        
        # Analyze context
        if recent_actions and "repeated" in recent_actions.lower():
            recommendations["bird_eye"]["score"] += 2
            recommendations["bird_eye"]["reasons"].append("Repeated actions suggest need for spatial reorientation")
        
        if current_context and any(word in current_context.lower() for word in ["detail", "precise", "close"]):
            recommendations["first_person"]["score"] += 2
            recommendations["first_person"]["reasons"].append("Context suggests need for detailed view")
        
        # Determine recommendation
        if recommendations["bird_eye"]["score"] > recommendations["first_person"]["score"]:
            recommended = "bird_eye"
        elif recommendations["first_person"]["score"] > recommendations["bird_eye"]["score"]:
            recommended = "first_person"
        else:
            recommended = "bird_eye"  # Default to bird-eye for navigation
            recommendations["bird_eye"]["reasons"].append("Default choice for general navigation")
        
        return {
            "success": True,
            "recommended_camera": recommended,
            "confidence": max(recommendations[recommended]["score"] / 5.0, 0.5),
            "bird_eye_score": recommendations["bird_eye"]["score"],
            "first_person_score": recommendations["first_person"]["score"],
            "bird_eye_reasons": recommendations["bird_eye"]["reasons"],
            "first_person_reasons": recommendations["first_person"]["reasons"],
            "guidance": {
                "bird_eye": "Use for: navigation, room layout, path planning, spatial understanding",
                "first_person": "Use for: object interaction, reading details, precise manipulation"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating camera recommendations: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "recommended_camera": "bird_eye"  # Safe fallback
        }

@mcp.tool()
async def get_available_cameras() -> Dict[str, Any]:
    """
    List all available cameras in the Blender scene.
    
    Returns:
        Dictionary with information about available cameras
    """
    try:
        cameras = []
        
        for obj in bpy.data.objects:
            if obj.type == 'CAMERA':
                camera_info = {
                    "name": obj.name,
                    "location": [obj.location.x, obj.location.y, obj.location.z],
                    "rotation": [obj.rotation_euler.x, obj.rotation_euler.y, obj.rotation_euler.z],
                    "is_active": bpy.context.scene.camera == obj,
                    "camera_type": "unknown"
                }
                
                # Determine camera type based on name and position
                name_lower = obj.name.lower()
                if 'bird' in name_lower or 'eye' in name_lower:
                    camera_info["camera_type"] = "bird_eye"
                elif 'fp' in name_lower or 'first' in name_lower or 'actor' in name_lower:
                    camera_info["camera_type"] = "first_person"
                elif obj.location.z > 5.0:
                    camera_info["camera_type"] = "bird_eye"
                else:
                    camera_info["camera_type"] = "first_person"
                
                cameras.append(camera_info)
        
        return {
            "success": True,
            "cameras": cameras,
            "total_count": len(cameras),
            "active_camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None
        }
        
    except Exception as e:
        logger.error(f"Error listing cameras: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "cameras": []
        }

@mcp.tool()
async def get_camera_info(
    actor_name: str = "Actor"
) -> Dict[str, Any]:
    """
    Get current first-person camera information and status.
    
    Args:
        actor_name: Name of the actor to check camera for
        
    Returns:
        Dictionary with camera information
    """
    try:
        camera_name = f"{actor_name}_FirstPersonCamera"
        camera = bpy.data.objects.get(camera_name)
        
        if not camera:
            return {
                "success": False,
                "error": f"First-person camera not found for {actor_name}"
            }
        
        # Get actor information
        actor = bpy.data.objects.get(actor_name)
        actor_info = {}
        if actor:
            actor_info = {
                "position": list(actor.location),
                "rotation": list(actor.rotation_euler)
            }
        
        # Calculate world position of camera
        world_matrix = camera.matrix_world
        world_position = list(world_matrix.translation)
        world_rotation = list(world_matrix.to_euler())
        
        return {
            "success": True,
            "camera_name": camera_name,
            "actor_name": actor_name,
            "camera_local_position": list(camera.location),
            "camera_local_rotation": list(camera.rotation_euler),
            "camera_world_position": world_position,
            "camera_world_rotation": world_rotation,
            "actor_info": actor_info,
            "lens": camera.data.lens,
            "clip_start": camera.data.clip_start,
            "clip_end": camera.data.clip_end,
            "is_active_camera": bpy.context.scene.camera == camera
        }
        
    except Exception as e:
        logger.error(f"Error getting camera info: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def list_camera_captures(
    actor_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all captured first-person screenshots.
    
    Args:
        actor_name: Optional filter by actor name
        
    Returns:
        Dictionary with list of captured files
    """
    try:
        if not os.path.exists(SCREENSHOT_DIR):
            return {
                "success": True,
                "captures": [],
                "count": 0
            }
        
        # Get all PNG files in captures directory
        captures = []
        for filename in os.listdir(SCREENSHOT_DIR):
            if filename.endswith('.png'):
                # Filter by actor name if specified
                if actor_name and f"first_person_{actor_name}_" not in filename:
                    continue
                
                filepath = os.path.join(SCREENSHOT_DIR, filename)
                file_stats = os.stat(filepath)
                
                captures.append({
                    "filename": filename,
                    "filepath": filepath,
                    "size": file_stats.st_size,
                    "modified": file_stats.st_mtime
                })
        
        # Sort by modification time (newest first)
        captures.sort(key=lambda x: x["modified"], reverse=True)
        
        return {
            "success": True,
            "captures": captures,
            "count": len(captures),
            "directory": SCREENSHOT_DIR,
            "filter_actor": actor_name
        }
        
    except Exception as e:
        logger.error(f"Error listing captures: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Service health check
@mcp.tool()
async def camera_service_health() -> Dict[str, Any]:
    """Check camera service health and capabilities"""
    try:
        # Check Blender availability
        blender_available = 'bpy' in globals()
        
        # Check screenshot directory
        screenshot_dir_exists = os.path.exists(SCREENSHOT_DIR)
        screenshot_dir_writable = os.access(SCREENSHOT_DIR, os.W_OK) if screenshot_dir_exists else False
        
        return {
            "success": True,
            "service": "Camera Service",
            "status": "healthy",
            "blender_available": blender_available,
            "screenshot_directory": {
                "path": SCREENSHOT_DIR,
                "exists": screenshot_dir_exists,
                "writable": screenshot_dir_writable
            },
            "capabilities": [
                "setup_first_person_camera",
                "capture_first_person_view", 
                "get_camera_info",
                "list_camera_captures"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }

def main():
    """Run the Camera Service"""
    logger.info(f"Starting Camera Service on port {CAMERA_SERVICE_PORT}")
    mcp.run(port=CAMERA_SERVICE_PORT)

if __name__ == "__main__":
    main()
