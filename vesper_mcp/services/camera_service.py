"""
Camera & Visual Input Service
============================

Dedicated service for first-person camera management and image capture.
Extracted from monolithic vesper_mcp_server.py to provide focused visual input capabilities.
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
mcp = FastMCP("Camera Service")

# Configuration
CAMERA_SERVICE_PORT = 8001
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "captures", "first_person")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

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
async def capture_first_person_view(
    actor_name: str = "Actor",
    filename: Optional[str] = None,
    resolution_x: int = 800,
    resolution_y: int = 600
) -> Dict[str, Any]:
    """
    Capture first-person view screenshot from actor's perspective.
    
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
        
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        
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
