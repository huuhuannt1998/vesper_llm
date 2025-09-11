"""
VESPER Backend MCP Integration
=============================

Integrates FastMCP tools with the existing VESPER backend API.
This allows VLMs to use enhanced navigation tools through the web interface.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import asyncio
import sys
import os

# Add MCP tools to path
mcp_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'vesper_mcp')
sys.path.append(mcp_dir)

try:
    # Import MCP bridge if available
    from blender_integration.mcp_bridge import VESPERBlenderBridge
    MCP_AVAILABLE = True
except ImportError:
    print("Warning: MCP tools not available, using fallback mode")
    MCP_AVAILABLE = False

router = APIRouter()

# Pydantic models for MCP requests
class MCPToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}

class MCPImageCaptureRequest(BaseModel):
    include_first_person: bool = True
    include_bird_eye: bool = True
    include_reference: bool = False

class MCPMovementRequest(BaseModel):
    action_type: str  # "step", "turn", "goto", "explore", "stop"
    direction: Optional[str] = None  # "UP", "DOWN", "LEFT", "RIGHT", "FORWARD", "BACK"
    target_position: Optional[List[float]] = None
    steps: int = 1

class MCPInteractionRequest(BaseModel):
    object_name: str
    interaction_type: str  # "pickup", "activate", "use", "examine"

# MCP Bridge instance
mcp_bridge = None

def get_mcp_bridge():
    """Get or create MCP bridge instance"""
    global mcp_bridge
    if mcp_bridge is None and MCP_AVAILABLE:
        mcp_bridge = VESPERBlenderBridge()
    return mcp_bridge

@router.get("/mcp/status")
async def get_mcp_status():
    """Get MCP system status"""
    bridge = get_mcp_bridge()
    
    if not MCP_AVAILABLE:
        return {
            "mcp_available": False,
            "message": "MCP tools not available - check installation",
            "fallback_mode": True
        }
    
    if bridge:
        try:
            status = bridge.get_system_status()
            return {
                "mcp_available": True,
                "blender_integration": status.get("blender_ready", False),
                "tools_loaded": len(status.get("available_tools", [])),
                "session_active": status.get("session_active", False),
                "message": "MCP system operational"
            }
        except Exception as e:
            return {
                "mcp_available": True,
                "error": str(e),
                "message": "MCP system error"
            }
    
    return {
        "mcp_available": False,
        "message": "MCP bridge not initialized"
    }

@router.get("/mcp/tools")
async def list_mcp_tools():
    """List all available MCP tools"""
    # Updated to reflect actual implemented tools in vesper_mcp_server.py
    tools = [
        {
            "name": "setup_actor_first_person_camera",
            "category": "camera_setup",
            "description": "Set up first-person camera attached to actor for VLM visual input"
        },
        {
            "name": "capture_vlm_decision_context", 
            "category": "decision_support",
            "description": "Capture complete visual and spatial context when VLM is uncertain"
        },
        {
            "name": "get_actor_first_person_view",
            "category": "visual_input",
            "description": "Get first-person view from actor's camera for object recognition"
        },
        {
            "name": "capture_dual_view_images",
            "category": "image_analysis",
            "description": "Capture multiple camera views for comprehensive scene analysis"
        },
        {
            "name": "analyze_room_from_images", 
            "category": "image_analysis",
            "description": "Analyze room type and objects from captured images"
        },
        {
            "name": "get_spatial_context",
            "category": "spatial_awareness", 
            "description": "Get comprehensive spatial context and navigation options"
        },
        {
            "name": "get_room_connectivity_map",
            "category": "spatial_awareness",
            "description": "Map room connections and navigation paths"
        },
        {
            "name": "execute_movement_action",
            "category": "action_control",
            "description": "Execute movement actions for the actor"
        },
        {
            "name": "execute_interaction_action",
            "category": "action_control", 
            "description": "Interact with objects in the environment"
        },
        {
            "name": "get_task_context_analysis",
            "category": "advanced",
            "description": "Analyze current task and requirements"
        },
        {
            "name": "get_navigation_history_analysis",
            "category": "advanced", 
            "description": "Get history and analysis of navigation actions"
        },
        {
            "name": "simulate_sensor_network",
            "category": "advanced",
            "description": "Simulate smart home sensors for CASAS evaluation"
        }
    ]
    
    return {
        "tools": tools,
        "total_count": len(tools),
        "categories": ["camera_setup", "decision_support", "visual_input", "image_analysis", "spatial_awareness", "action_control", "advanced"],
        "mcp_available": MCP_AVAILABLE,
        "new_features": "Enhanced first-person camera system for VLM decision-making"
    }

@router.post("/mcp/setup_camera")
async def mcp_setup_actor_camera(actor_name: str = "Actor"):
    """Set up first-person camera for actor"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "fallback": {
                "success": True,
                "camera_name": f"{actor_name}_FPCamera",
                "message": "Mock camera setup (MCP not available)"
            }
        }
    
    try:
        result = bridge.execute_tool("setup_actor_first_person_camera", {"actor_name": actor_name})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera setup failed: {str(e)}")

@router.get("/mcp/decision_context")
async def mcp_get_decision_context(actor_name: str = "Actor"):
    """Get complete decision context for VLM when uncertain"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "fallback": {
                "visual_context": {"first_person_view": "mock_base64_data"},
                "spatial_context": {"actor_position": {"x": 0, "y": 0, "z": 0}},
                "vlm_guidance": {"when_to_use": ["Mock guidance"]}
            }
        }
    
    try:
        result = bridge.execute_tool("capture_vlm_decision_context", {"actor_name": actor_name})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decision context failed: {str(e)}")

@router.get("/mcp/first_person_view")
async def mcp_get_first_person_view(actor_name: str = "Actor", width: int = 1024, height: int = 768):
    """Get first-person view from actor's camera"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "fallback": {
                "first_person_view": "mock_base64_data",
                "camera_position": {"x": 0, "y": 0, "z": 1.6},
                "visible_objects": []
            }
        }
    
    try:
        result = bridge.execute_tool("get_actor_first_person_view", {
            "actor_name": actor_name,
            "resolution_width": width,
            "resolution_height": height
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"First-person view failed: {str(e)}")

@router.post("/mcp/capture_images")
async def mcp_capture_images(request: MCPImageCaptureRequest):
    """Capture dual-view images using MCP tools"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "fallback": {
                "first_person_view": "mock_base64_data",
                "bird_eye_view": "mock_base64_data", 
                "views_captured": ["mock_first_person", "mock_bird_eye"]
            }
        }
    
    try:
        result = bridge.execute_tool(
            "capture_dual_view_images",
            {
                "include_first_person": request.include_first_person,
                "include_bird_eye": request.include_bird_eye,
                "include_reference": request.include_reference
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image capture failed: {str(e)}")

@router.post("/mcp/move")
async def mcp_execute_movement(request: MCPMovementRequest):
    """Execute movement using MCP tools"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "fallback": {
                "action_executed": request.action_type,
                "direction": request.direction,
                "success": True,
                "new_position": {"x": 0.0, "y": 0.0, "z": 0.0}
            }
        }
    
    try:
        result = bridge.execute_tool(
            "execute_movement_action",
            {
                "action_type": request.action_type,
                "direction": request.direction,
                "target_position": request.target_position,
                "steps": request.steps
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Movement failed: {str(e)}")

@router.get("/mcp/spatial_context")
async def mcp_get_spatial_context():
    """Get spatial context using MCP tools"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "fallback": {
                "actor_position": {"x": 0.0, "y": 0.0, "z": 0.0},
                "current_room": "Unknown",
                "navigation_options": {"available_directions": []}
            }
        }
    
    try:
        result = bridge.execute_tool("get_spatial_context", {})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spatial analysis failed: {str(e)}")

@router.post("/mcp/interact")
async def mcp_interact_object(request: MCPInteractionRequest):
    """Interact with object using MCP tools"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available", 
            "fallback": {
                "object_name": request.object_name,
                "interaction_type": request.interaction_type,
                "success": True,
                "result": f"Mock {request.interaction_type} with {request.object_name}"
            }
        }
    
    try:
        result = bridge.execute_tool(
            "interact_with_object",
            {
                "object_name": request.object_name,
                "interaction_type": request.interaction_type
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interaction failed: {str(e)}")

@router.get("/mcp/comprehensive_context")
async def mcp_get_comprehensive_context():
    """Get comprehensive context using MCP tools"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "fallback": {
                "visual_analysis": "Mock visual analysis",
                "spatial_awareness": "Mock spatial data",
                "task_progress": "Mock task progress",
                "confidence_score": 0.5
            }
        }
    
    try:
        result = bridge.execute_tool("get_comprehensive_context", {})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context analysis failed: {str(e)}")

@router.post("/mcp/tool")
async def mcp_execute_tool(request: MCPToolRequest):
    """Execute any MCP tool with custom parameters"""
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "tool_name": request.tool_name,
            "parameters": request.parameters,
            "fallback": True
        }
    
    try:
        result = bridge.execute_tool(request.tool_name, request.parameters)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

# Enhanced VLM endpoint with MCP integration
@router.post("/mcp/vlm_navigate")
async def mcp_vlm_navigate(task: str, current_context: Dict[str, Any] = None):
    """
    Enhanced VLM navigation using MCP tools.
    This demonstrates the modular approach where VLM can select optimal tools.
    """
    bridge = get_mcp_bridge()
    
    if not bridge:
        return {
            "error": "MCP bridge not available",
            "task": task,
            "recommendation": "Use traditional navigation method"
        }
    
    try:
        # Step 1: Analyze current situation
        images = bridge.execute_tool("capture_dual_view_images", {
            "include_first_person": True,
            "include_bird_eye": True
        })
        
        spatial = bridge.execute_tool("get_spatial_context", {})
        
        # Step 2: Analyze task requirements
        task_analysis = bridge.execute_tool("analyze_task_context", {
            "task_description": task,
            "current_context": current_context or {}
        })
        
        # Step 3: Get comprehensive context for VLM decision
        comprehensive = bridge.execute_tool("get_comprehensive_context", {})
        
        return {
            "task": task,
            "mcp_analysis": {
                "visual_context": images,
                "spatial_context": spatial, 
                "task_analysis": task_analysis,
                "comprehensive_context": comprehensive
            },
            "vlm_ready": True,
            "message": "Complete context available for VLM navigation decision"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"VLM navigation analysis failed: {str(e)}")
