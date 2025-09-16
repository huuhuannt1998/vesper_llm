"""
Camera & Visual Input Service
============================

Dedicated service for dual-camera management and image capture.
Provides both bird-eye and first-person camera capture tools for MCP agents.
The VLM agent can intelligently choose which camera view to capture based on context.
Supports both Blender edit mode and BGE runtime camera switching.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from mcp import FastMCP, types
import bpy

# BGE imports for runtime switching
try:
    import bge
    BGE_AVAILABLE = True
    
    # Check if we're in BGE runtime
    def is_bge_runtime():
        try:
            bge.logic.getCurrentScene()
            return True
        except:
            return False
    
    BGE_RUNTIME = is_bge_runtime()
    
except ImportError:
    BGE_AVAILABLE = False
    BGE_RUNTIME = False

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

# Hardcoded camera names for the specific setup
BIRD_EYE_CAMERA_NAME = "BirdEyeCamera"
FIRST_PERSON_CAMERA_NAME = "Actor_FPCamera"

def reset_bge_capture_state():
    """
    Reset any stuck capture states in BGE runtime.
    """
    if not BGE_RUNTIME:
        return
    
    try:
        scene = bge.logic.getCurrentScene()
        
        # Reset any sequential dual camera system
        if hasattr(scene, 'dual_camera_system'):
            scene.dual_camera_system._reset_capture_state()
            logger.info("BGE: Reset sequential dual camera system")
        
        # Clear any capture flags
        for obj in scene.objects:
            if hasattr(obj, 'capture_in_progress'):
                obj.capture_in_progress = False
        
        logger.info("BGE: Capture state reset complete")
        
    except Exception as e:
        logger.warning(f"BGE: Error during capture state reset: {e}")

def switch_camera_runtime(camera_name: str) -> Dict[str, Any]:
    """
    Switch active camera during BGE runtime.
    
    Args:
        camera_name: Name of the camera to switch to
        
    Returns:
        Dictionary with switch result
    """
    try:
        if BGE_RUNTIME:
            # BGE runtime camera switching
            scene = bge.logic.getCurrentScene()
            
            # Find the camera object in BGE scene
            camera = None
            for obj in scene.objects:
                if obj.name == camera_name:
                    camera = obj
                    break
            
            if not camera:
                return {
                    "success": False,
                    "error": f"Camera '{camera_name}' not found in BGE scene"
                }
            
            # Store previous camera
            previous_camera = scene.active_camera
            
            # Switch to new camera
            scene.active_camera = camera
            
            # Force camera update and small delay
            import time
            time.sleep(0.05)
            
            logger.info(f"BGE Runtime: Switched from {previous_camera.name if previous_camera else 'None'} to {camera_name}")
            
            return {
                "success": True,
                "previous_camera": previous_camera.name if previous_camera else None,
                "current_camera": camera_name,
                "mode": "bge_runtime"
            }
        else:
            # Blender edit mode camera switching
            camera = bpy.data.objects.get(camera_name)
            if not camera:
                return {
                    "success": False,
                    "error": f"Camera '{camera_name}' not found in Blender scene"
                }
            
            previous_camera = bpy.context.scene.camera
            bpy.context.scene.camera = camera
            
            logger.info(f"Blender Edit: Switched from {previous_camera.name if previous_camera else 'None'} to {camera_name}")
            
            return {
                "success": True,
                "previous_camera": previous_camera.name if previous_camera else None,
                "current_camera": camera_name,
                "mode": "blender_edit"
            }
            
    except Exception as e:
        logger.error(f"Error switching camera to {camera_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def capture_screenshot_runtime(filepath: str) -> Dict[str, Any]:
    """
    Capture screenshot using appropriate method for current mode.
    
    Args:
        filepath: Full path where to save the screenshot
        
    Returns:
        Dictionary with capture result
    """
    try:
        if BGE_RUNTIME:
            # BGE runtime screenshot using makeScreenshot
            # Need to ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # BGE makeScreenshot call - returns True/False
            screenshot_result = bge.render.makeScreenshot(filepath)
            
            # Small delay to ensure file is written
            import time
            time.sleep(0.1)
            
            # Verify file was created and has content
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                file_size = os.path.getsize(filepath)
                logger.info(f"BGE Runtime screenshot captured: {filepath} ({file_size} bytes)")
                return {
                    "success": True,
                    "filepath": filepath,
                    "file_size": file_size,
                    "method": "bge_makeScreenshot",
                    "screenshot_result": screenshot_result
                }
            else:
                return {
                    "success": False,
                    "error": f"Screenshot file was not created by BGE (result: {screenshot_result})"
                }
        else:
            # Blender edit mode rendering
            original_filepath = bpy.context.scene.render.filepath
            bpy.context.scene.render.filepath = filepath
            
            bpy.ops.render.render(write_still=True)
            
            # Restore original filepath
            bpy.context.scene.render.filepath = original_filepath
            
            # Verify file was created
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Blender Edit screenshot captured: {filepath} ({file_size} bytes)")
                return {
                    "success": True,
                    "filepath": filepath,
                    "file_size": file_size,
                    "method": "blender_render"
                }
            else:
                return {
                    "success": False,
                    "error": "Screenshot file was not created by Blender render"
                }
                
    except Exception as e:
        logger.error(f"Error capturing screenshot to {filepath}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

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
        
        # Reset any stuck capture states first
        reset_bge_capture_state()
        
        # Use hardcoded bird-eye camera name
        bird_eye_camera_name = BIRD_EYE_CAMERA_NAME
        
        # Verify camera exists
        camera_exists = False
        if BGE_RUNTIME:
            scene = bge.logic.getCurrentScene()
            camera_exists = bird_eye_camera_name in scene.objects
        else:
            camera_exists = bpy.data.objects.get(bird_eye_camera_name) is not None
        
        if not camera_exists:
            return {
                "success": False,
                "error": f"Bird-eye camera '{bird_eye_camera_name}' not found in scene"
            }
        
        # Switch to bird-eye camera
        camera_switch = switch_camera_runtime(bird_eye_camera_name)
        if not camera_switch["success"]:
            return {
                "success": False,
                "error": f"Failed to switch to bird-eye camera: {camera_switch['error']}"
            }
        
        # Store original settings for non-BGE mode
        original_settings = {}
        if not BGE_RUNTIME:
            render = bpy.context.scene.render
            original_settings = {
                "resolution_x": render.resolution_x,
                "resolution_y": render.resolution_y,
                "filepath": render.filepath
            }
            
            # Configure render settings
            render.resolution_x = resolution_x
            render.resolution_y = resolution_y
            render.resolution_percentage = 100
        
        try:
            # Capture screenshot
            capture_result = capture_screenshot_runtime(filepath)
            
            if capture_result["success"]:
                return {
                    "success": True,
                    "filepath": filepath,
                    "filename": filename,
                    "camera_used": bird_eye_camera_name,
                    "file_size": capture_result["file_size"],
                    "resolution": f"{resolution_x}x{resolution_y}",
                    "camera_type": "bird_eye",
                    "description": "Top-down view for spatial navigation and room layout",
                    "capture_method": capture_result["method"],
                    "runtime_mode": "bge" if BGE_RUNTIME else "blender_edit"
                }
            else:
                return capture_result
            
        finally:
            # Restore original settings for non-BGE mode
            if not BGE_RUNTIME and original_settings:
                render = bpy.context.scene.render
                render.resolution_x = original_settings["resolution_x"]
                render.resolution_y = original_settings["resolution_y"]
                render.filepath = original_settings["filepath"]
            
            # Restore previous camera if needed
            if camera_switch.get("previous_camera"):
                switch_camera_runtime(camera_switch["previous_camera"])
        
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
        # Use hardcoded first-person camera name
        first_person_camera_name = FIRST_PERSON_CAMERA_NAME
        
        # Verify camera exists
        camera_exists = False
        if BGE_RUNTIME:
            scene = bge.logic.getCurrentScene()
            camera_exists = first_person_camera_name in scene.objects
        else:
            camera_exists = bpy.data.objects.get(first_person_camera_name) is not None
        
        if not camera_exists:
            return {
                "success": False,
                "error": f"First-person camera '{first_person_camera_name}' not found in scene"
            }
        
        # Generate filename if not provided
        if not filename:
            import time
            timestamp = int(time.time() * 1000)
            filename = f"first_person_{actor_name}_{timestamp}.png"
        
        # Ensure .png extension
        if not filename.endswith('.png'):
            filename += '.png'
        
        filepath = os.path.join(FIRST_PERSON_DIR, filename)
        
        # Reset any stuck capture states first
        reset_bge_capture_state()
        
        # Switch to first-person camera with retry logic
        switch_attempts = 0
        max_attempts = 3
        camera_switch = None
        
        while switch_attempts < max_attempts:
            camera_switch = switch_camera_runtime(first_person_camera_name)
            if camera_switch["success"]:
                break
            switch_attempts += 1
            logger.warning(f"Camera switch attempt {switch_attempts} failed: {camera_switch.get('error', 'Unknown')}")
            if BGE_RUNTIME:
                import time
                time.sleep(0.1)
        
        if not camera_switch or not camera_switch["success"]:
            return {
                "success": False,
                "error": f"Failed to switch to first-person camera after {max_attempts} attempts: {camera_switch.get('error', 'Unknown error') if camera_switch else 'No response'}"
            }
        
        # Store original settings for non-BGE mode
        original_settings = {}
        if not BGE_RUNTIME:
            render = bpy.context.scene.render
            original_settings = {
                "resolution_x": render.resolution_x,
                "resolution_y": render.resolution_y,
                "filepath": render.filepath
            }
            
            # Configure render settings
            render.resolution_x = resolution_x
            render.resolution_y = resolution_y
            render.resolution_percentage = 100
        
        try:
            # Capture screenshot with retry logic
            capture_attempts = 0
            max_capture_attempts = 3
            capture_result = None
            
            while capture_attempts < max_capture_attempts:
                capture_result = capture_screenshot_runtime(filepath)
                if capture_result["success"]:
                    break
                capture_attempts += 1
                logger.warning(f"Screenshot capture attempt {capture_attempts} failed: {capture_result.get('error', 'Unknown')}")
                if BGE_RUNTIME:
                    import time
                    time.sleep(0.2)
            
            if capture_result and capture_result["success"]:
                return {
                    "success": True,
                    "filepath": filepath,
                    "filename": filename,
                    "camera_used": first_person_camera_name,
                    "file_size": capture_result["file_size"],
                    "resolution": [resolution_x, resolution_y],
                    "actor_name": actor_name,
                    "camera_type": "first_person",
                    "description": "Actor's eye-level perspective for detailed interaction",
                    "capture_method": capture_result["method"],
                    "runtime_mode": "bge" if BGE_RUNTIME else "blender_edit",
                    "capture_attempts": capture_attempts + 1,
                    "switch_attempts": switch_attempts + 1
                }
            else:
                return {
                    "success": False,
                    "error": f"Screenshot capture failed after {max_capture_attempts} attempts: {capture_result.get('error', 'Unknown error') if capture_result else 'No response'}"
                }
            
        finally:
            # Restore original settings for non-BGE mode
            if not BGE_RUNTIME and original_settings:
                render = bpy.context.scene.render
                render.resolution_x = original_settings["resolution_x"]
                render.resolution_y = original_settings["resolution_y"]
                render.filepath = original_settings["filepath"]
            
            # Restore previous camera if needed
            if camera_switch.get("previous_camera"):
                switch_camera_runtime(camera_switch["previous_camera"])
            
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
