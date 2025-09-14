"""
Microservices Orchestration Service
===================================

Central orchestration service that coordinates all VESPER VLM microservices.
Replaces the monolithic vesper_mcp_server.py with a distributed architecture.
"""

import asyncio
import os
import json
from typing import Dict, Any, List, Optional
import logging
import aiohttp
from pathlib import Path

from mcp import FastMCP, types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance for orchestration service
mcp = FastMCP("VLM Orchestration Service")

# Configuration
ORCHESTRATION_SERVICE_PORT = 8000

# Service registry - imported from services package
from . import SERVICES, get_service_url

# VLM prompt templates
VLM_PROMPTS = {
    "navigation": """
You are VESPER, an advanced VLM navigation system for smart home environments.

Current Context:
- Position: {position}
- Room: {current_room}
- Visual Analysis: {visual_analysis}
- Task Context: {task_context}
- Navigation Options: {navigation_options}

Spatial Awareness:
{spatial_context}

Available Actions:
{available_actions}

Task Objective: {task_objective}

Based on the current context, provide navigation guidance and action recommendations.
Consider the visual information, spatial awareness, and task requirements.
""",
    "interaction": """
You are VESPER, managing smart home device interactions.

Current Context:
- Room: {current_room}
- Available Devices: {available_devices}
- Task: {task_description}
- Visual Context: {visual_analysis}

Device States:
{device_states}

Interaction History:
{interaction_history}

Determine the appropriate device interactions to complete the task.
""",
    "analysis": """
You are VESPER, analyzing navigation and task completion.

Current Session Data:
- Navigation History: {navigation_history}
- Task Progress: {task_progress}
- Performance Metrics: {performance_metrics}
- Sensor Data: {sensor_data}

Provide analysis of navigation efficiency and task completion status.
"""
}

class ServiceManager:
    """Manages communication with all microservices"""
    
    def __init__(self):
        self.session = None
        self.service_health = {}
    
    async def initialize(self):
        """Initialize HTTP session for service communication"""
        self.session = aiohttp.ClientSession()
        await self.check_all_services()
    
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def check_all_services(self):
        """Check health of all services"""
        for service_name, service_info in SERVICES.items():
            if service_name == "orchestration":  # Skip self
                continue
            
            health = await self.check_service_health(service_name)
            self.service_health[service_name] = health
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        try:
            url = get_service_url(service_name)
            if not url:
                return {"healthy": False, "error": "Service not found"}
            
            # Try to call health endpoint
            health_endpoint = f"{url}/health"
            async with self.session.get(health_endpoint, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"healthy": True, "data": data}
                else:
                    return {"healthy": False, "error": f"HTTP {response.status}"}
        
        except asyncio.TimeoutError:
            return {"healthy": False, "error": "Service timeout"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def call_service(self, service_name: str, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool on a specific service"""
        try:
            url = get_service_url(service_name)
            if not url:
                return {"success": False, "error": f"Service {service_name} not found"}
            
            endpoint = f"{url}/tools/{tool_name}"
            async with self.session.post(endpoint, json=kwargs, timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
        
        except asyncio.TimeoutError:
            return {"success": False, "error": "Service call timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Global service manager
service_manager = ServiceManager()

@mcp.tool()
async def vlm_navigation_guidance(
    task_description: str,
    actor_name: str = "Actor",
    include_visual_analysis: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive VLM navigation guidance for a task.
    
    Args:
        task_description: Description of the task to complete
        actor_name: Name of the actor to guide
        include_visual_analysis: Whether to include visual analysis
        
    Returns:
        Dictionary with VLM navigation guidance
    """
    try:
        # Gather context from all relevant services
        context = await _gather_navigation_context(actor_name, include_visual_analysis)
        
        # Get task analysis
        task_context = await service_manager.call_service(
            "task_analysis", "analyze_task_description",
            task_description=task_description
        )
        
        # Build VLM prompt
        prompt_data = {
            "position": context.get("position", {}),
            "current_room": context.get("current_room", "unknown"),
            "visual_analysis": context.get("visual_analysis", {}),
            "task_context": task_context.get("analysis", {}),
            "navigation_options": context.get("navigation_options", []),
            "spatial_context": context.get("spatial_context", {}),
            "available_actions": _get_available_actions(),
            "task_objective": task_description
        }
        
        vlm_prompt = VLM_PROMPTS["navigation"].format(**prompt_data)
        
        return {
            "success": True,
            "vlm_prompt": vlm_prompt,
            "context": context,
            "task_analysis": task_context,
            "service_health": service_manager.service_health
        }
        
    except Exception as e:
        logger.error(f"Error generating VLM navigation guidance: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

async def _gather_navigation_context(actor_name: str, include_visual: bool) -> Dict[str, Any]:
    """Gather context from all relevant services"""
    context = {}
    
    try:
        # Get spatial context
        spatial_result = await service_manager.call_service(
            "spatial", "get_navigation_context",
            actor_name=actor_name
        )
        if spatial_result.get("success"):
            context.update({
                "position": spatial_result.get("current_position"),
                "current_room": spatial_result.get("current_room"),
                "navigation_options": spatial_result.get("navigation_options"),
                "spatial_context": spatial_result
            })
        
        # Get visual analysis if requested
        if include_visual:
            # Capture current view
            camera_result = await service_manager.call_service(
                "camera", "capture_first_person_view",
                actor_name=actor_name
            )
            
            if camera_result.get("success"):
                # Analyze the captured image
                image_path = camera_result.get("filepath")
                if image_path:
                    analysis_result = await service_manager.call_service(
                        "image_analysis", "analyze_room_from_image",
                        image_path=image_path
                    )
                    context["visual_analysis"] = analysis_result.get("analysis", {})
        
        # Get device context if in a room with devices
        current_room = context.get("current_room")
        if current_room and current_room != "unknown":
            device_result = await service_manager.call_service(
                "device", "get_room_devices",
                room_name=current_room
            )
            context["available_devices"] = device_result.get("devices", [])
    
    except Exception as e:
        logger.warning(f"Error gathering context: {str(e)}")
        context["context_error"] = str(e)
    
    return context

def _get_available_actions() -> List[str]:
    """Get list of available actions across all services"""
    return [
        "move_to_position",
        "move_to_room", 
        "rotate_actor",
        "capture_image",
        "analyze_room",
        "interact_with_device",
        "activate_sensor",
        "get_navigation_path",
        "check_task_progress"
    ]

@mcp.tool()
async def execute_coordinated_action(
    action_type: str,
    action_params: Dict[str, Any],
    actor_name: str = "Actor"
) -> Dict[str, Any]:
    """
    Execute a coordinated action across multiple services.
    
    Args:
        action_type: Type of action to execute
        action_params: Parameters for the action
        actor_name: Name of the actor
        
    Returns:
        Dictionary with execution results
    """
    try:
        # Action routing to appropriate services
        if action_type == "navigate_to_room":
            # Coordinate spatial planning and movement execution
            room_name = action_params.get("room_name")
            
            # Get navigation context
            nav_context = await service_manager.call_service(
                "spatial", "get_navigation_context",
                actor_name=actor_name,
                target_room=room_name
            )
            
            # Execute movement
            movement_result = await service_manager.call_service(
                "movement", "move_to_room",
                target_room=room_name,
                actor_name=actor_name,
                position_in_room=action_params.get("position", "center")
            )
            
            return {
                "success": movement_result.get("success", False),
                "action_type": action_type,
                "navigation_context": nav_context,
                "movement_result": movement_result
            }
        
        elif action_type == "capture_and_analyze":
            # Coordinate camera capture and image analysis
            capture_result = await service_manager.call_service(
                "camera", "capture_first_person_view",
                actor_name=actor_name
            )
            
            if capture_result.get("success"):
                analysis_result = await service_manager.call_service(
                    "image_analysis", "analyze_room_from_image",
                    image_path=capture_result.get("filepath")
                )
                
                return {
                    "success": True,
                    "action_type": action_type,
                    "capture_result": capture_result,
                    "analysis_result": analysis_result
                }
            else:
                return capture_result
        
        elif action_type == "device_interaction":
            # Coordinate device interaction with context
            device_id = action_params.get("device_id")
            interaction_type = action_params.get("interaction_type")
            
            interaction_result = await service_manager.call_service(
                "interaction", "interact_with_object",
                target_object=device_id,
                interaction_type=interaction_type,
                actor_name=actor_name
            )
            
            return {
                "success": interaction_result.get("success", False),
                "action_type": action_type,
                "interaction_result": interaction_result
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action_type}",
                "available_actions": [
                    "navigate_to_room",
                    "capture_and_analyze", 
                    "device_interaction"
                ]
            }
    
    except Exception as e:
        logger.error(f"Error executing coordinated action: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_comprehensive_status(
    actor_name: str = "Actor"
) -> Dict[str, Any]:
    """
    Get comprehensive status across all services.
    
    Args:
        actor_name: Name of the actor to get status for
        
    Returns:
        Dictionary with comprehensive system status
    """
    try:
        status = {
            "actor_name": actor_name,
            "timestamp": asyncio.get_event_loop().time(),
            "services": {}
        }
        
        # Check each service
        for service_name in SERVICES.keys():
            if service_name == "orchestration":
                continue
            
            try:
                # Call health check for each service
                health = await service_manager.check_service_health(service_name)
                status["services"][service_name] = health
                
                # Get additional status if service is healthy
                if health.get("healthy"):
                    if service_name == "spatial":
                        spatial_status = await service_manager.call_service(
                            service_name, "get_current_position",
                            actor_name=actor_name
                        )
                        status["services"][service_name]["status"] = spatial_status
                    
                    elif service_name == "camera":
                        camera_status = await service_manager.call_service(
                            service_name, "get_camera_info",
                            actor_name=actor_name
                        )
                        status["services"][service_name]["status"] = camera_status
            
            except Exception as e:
                status["services"][service_name] = {
                    "healthy": False,
                    "error": str(e)
                }
        
        # Calculate overall health
        healthy_services = sum(1 for s in status["services"].values() if s.get("healthy"))
        total_services = len(status["services"])
        
        status["overall_health"] = {
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "status": "healthy" if healthy_services == total_services else "degraded"
        }
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting comprehensive status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def initialize_services() -> Dict[str, Any]:
    """
    Initialize all microservices and check connectivity.
    
    Returns:
        Dictionary with initialization results
    """
    try:
        # Initialize service manager
        await service_manager.initialize()
        
        # Check all services
        await service_manager.check_all_services()
        
        # Count healthy services
        healthy_count = sum(1 for s in service_manager.service_health.values() if s.get("healthy"))
        total_count = len(service_manager.service_health)
        
        return {
            "success": True,
            "message": "Services initialized",
            "healthy_services": healthy_count,
            "total_services": total_count,
            "service_health": service_manager.service_health,
            "services_available": list(SERVICES.keys())
        }
        
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Service health check
@mcp.tool()
async def orchestration_service_health() -> Dict[str, Any]:
    """Check orchestration service health and capabilities"""
    try:
        return {
            "success": True,
            "service": "VLM Orchestration Service",
            "status": "healthy",
            "capabilities": [
                "vlm_navigation_guidance",
                "execute_coordinated_action",
                "get_comprehensive_status",
                "initialize_services"
            ],
            "managed_services": list(SERVICES.keys()),
            "service_manager_initialized": service_manager.session is not None
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "unhealthy"
        }

# Lifecycle management
async def startup():
    """Service startup"""
    logger.info("Starting VLM Orchestration Service")
    await service_manager.initialize()

async def shutdown():
    """Service shutdown"""
    logger.info("Shutting down VLM Orchestration Service")
    await service_manager.cleanup()

def main():
    """Run the VLM Orchestration Service"""
    logger.info(f"Starting VLM Orchestration Service on port {ORCHESTRATION_SERVICE_PORT}")
    
    # Set up lifecycle handlers
    import signal
    import sys
    
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        asyncio.create_task(shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the service
    mcp.run(port=ORCHESTRATION_SERVICE_PORT)

if __name__ == "__main__":
    main()
