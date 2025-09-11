"""
VESPER MCP Tools - Blender Integration Bridge
============================================

Handles integration between FastMCP tools and Blender Game Engine.
Provides seamless communication and state synchronization.
"""

import bpy
import json
import sys
import os
from typing import Dict, List, Optional, Any

# Note: MCP tools are now integrated directly in vesper_mcp_server.py
# No separate tools modules to import

class VESPERBlenderBridge:
    """Bridge between VESPER MCP tools and Blender Game Engine"""
    
    def __init__(self):
        self.tools_available = {
            "mcp_server": "All tools integrated in vesper_mcp_server.py",
            "total_tools": 9,
            "connection_status": "ready"
        }
        self.session_data = {}
        self.debug_mode = True
        
    def initialize_mcp_session(self) -> Dict[str, Any]:
        """Initialize MCP session with current Blender state"""
        try:
            session_info = {
                "session_id": f"vesper_{int(bpy.context.scene.frame_current)}",
                "blender_file": bpy.data.filepath,
                "available_tools": self.tools_available,
                "scene_objects": [],
                "actor_status": {},
                "initialization_successful": True
            }
            
            # Get scene objects
            session_info["scene_objects"] = [
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": [round(obj.location.x, 2), round(obj.location.y, 2), round(obj.location.z, 2)]
                }
                for obj in bpy.context.scene.objects
                if obj.type in ['MESH', 'CAMERA']
            ]
            
            # Get actor status
            actor = bpy.data.objects.get("Actor")
            if actor:
                session_info["actor_status"] = {
                    "found": True,
                    "position": [round(actor.location.x, 2), round(actor.location.y, 2), round(actor.location.z, 2)],
                    "rotation": [round(r, 2) for r in actor.rotation_euler]
                }
            else:
                session_info["actor_status"] = {"found": False}
            
            self.session_data = session_info
            return session_info
            
        except Exception as e:
            return {"error": f"MCP session initialization failed: {str(e)}"}
    
    def execute_mcp_tool(self, tool_name: str, method_name: str, **kwargs) -> Dict[str, Any]:
        """Execute MCP tool method with error handling"""
        try:
            if not self.tools_available.get(tool_name, False):
                return {"error": f"Tool {tool_name} not available"}
            
            # Route to appropriate tool
            if tool_name == "image_analysis" and image_analyzer:
                return self._execute_image_analysis_method(method_name, **kwargs)
            elif tool_name == "spatial_awareness" and spatial_analyzer:
                return self._execute_spatial_analysis_method(method_name, **kwargs)
            elif tool_name == "action_control" and action_controller:
                return self._execute_action_control_method(method_name, **kwargs)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def _execute_image_analysis_method(self, method_name: str, **kwargs) -> Dict[str, Any]:
        """Execute image analysis tool methods"""
        if method_name == "capture_dual_view_images":
            return image_analyzer.capture_dual_view_images(**kwargs)
        elif method_name == "analyze_room_from_images":
            return image_analyzer.analyze_room_from_images(**kwargs)
        else:
            return {"error": f"Unknown image analysis method: {method_name}"}
    
    def _execute_spatial_analysis_method(self, method_name: str, **kwargs) -> Dict[str, Any]:
        """Execute spatial awareness tool methods"""
        if method_name == "get_spatial_context":
            return spatial_analyzer.get_spatial_context()
        elif method_name == "get_room_connectivity_map":
            return spatial_analyzer.get_room_connectivity_map()
        elif method_name == "get_actor_position_detailed":
            return spatial_analyzer.get_actor_position_detailed()
        else:
            return {"error": f"Unknown spatial analysis method: {method_name}"}
    
    def _execute_action_control_method(self, method_name: str, **kwargs) -> Dict[str, Any]:
        """Execute action control tool methods"""
        if method_name == "execute_movement_action":
            return action_controller.execute_movement_action(**kwargs)
        elif method_name == "execute_interaction_action":
            return action_controller.execute_interaction_action(**kwargs)
        elif method_name == "get_available_actions":
            return action_controller.get_available_actions()
        else:
            return {"error": f"Unknown action control method: {method_name}"}
    
    def get_comprehensive_context(self) -> Dict[str, Any]:
        """Get comprehensive context from all available tools"""
        context = {
            "timestamp": bpy.context.scene.frame_current,
            "tools_status": self.tools_available,
            "context_data": {}
        }
        
        try:
            # Get spatial context
            if spatial_analyzer:
                spatial_context = spatial_analyzer.get_spatial_context()
                context["context_data"]["spatial"] = spatial_context
            
            # Get image analysis
            if image_analyzer:
                image_data = image_analyzer.capture_dual_view_images(
                    include_first_person=True,
                    include_bird_eye=True,
                    include_reference=False
                )
                context["context_data"]["images"] = image_data
                
                # Analyze current room
                room_analysis = image_analyzer.analyze_room_from_images()
                context["context_data"]["room_analysis"] = room_analysis
            
            # Get available actions
            if action_controller:
                available_actions = action_controller.get_available_actions()
                context["context_data"]["available_actions"] = available_actions
            
            return context
            
        except Exception as e:
            context["error"] = f"Context gathering failed: {str(e)}"
            return context
    
    def create_vlm_decision_prompt(self, task: str, use_all_tools: bool = True) -> Dict[str, Any]:
        """Create comprehensive prompt for VLM decision making"""
        prompt_data = {
            "task": task,
            "tools_available": [],
            "context": {},
            "recommended_approach": [],
            "prompt_text": ""
        }
        
        try:
            # Get comprehensive context
            context = self.get_comprehensive_context()
            prompt_data["context"] = context.get("context_data", {})
            
            # Build available tools list
            for tool_name, available in self.tools_available.items():
                if available:
                    prompt_data["tools_available"].append({
                        "name": tool_name,
                        "description": self._get_tool_description(tool_name),
                        "methods": self._get_tool_methods(tool_name)
                    })
            
            # Create task-specific recommendations
            prompt_data["recommended_approach"] = self._get_task_recommendations(task, context)
            
            # Build comprehensive prompt text
            prompt_data["prompt_text"] = self._build_vlm_prompt(task, prompt_data)
            
            return prompt_data
            
        except Exception as e:
            prompt_data["error"] = f"Prompt creation failed: {str(e)}"
            return prompt_data
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Get description for tool"""
        descriptions = {
            "image_analysis": "Capture and analyze visual information from multiple camera views (first-person, bird's-eye, reference)",
            "spatial_awareness": "Analyze spatial context, room layouts, and navigation possibilities",
            "action_control": "Execute movement and interaction actions with environment objects"
        }
        return descriptions.get(tool_name, "Unknown tool")
    
    def _get_tool_methods(self, tool_name: str) -> List[Dict[str, str]]:
        """Get available methods for tool"""
        methods = {
            "image_analysis": [
                {"name": "capture_dual_view_images", "description": "Capture first-person and bird's-eye view images"},
                {"name": "analyze_room_from_images", "description": "Analyze room type and furniture from images"}
            ],
            "spatial_awareness": [
                {"name": "get_spatial_context", "description": "Get comprehensive spatial analysis"},
                {"name": "get_room_connectivity_map", "description": "Get room connectivity and navigation graph"},
                {"name": "get_actor_position_detailed", "description": "Get detailed actor position with context"}
            ],
            "action_control": [
                {"name": "execute_movement_action", "description": "Execute movement actions (step, turn, goto, explore)"},
                {"name": "execute_interaction_action", "description": "Interact with environment objects"},
                {"name": "get_available_actions", "description": "Get all available actions from current position"}
            ]
        }
        return methods.get(tool_name, [])
    
    def _get_task_recommendations(self, task: str, context: Dict) -> List[str]:
        """Get task-specific tool usage recommendations"""
        recommendations = []
        task_lower = task.lower()
        
        # Navigation tasks
        if any(x in task_lower for x in ["go to", "navigate", "move", "find"]):
            recommendations.extend([
                "1. Use image_analysis.capture_dual_view_images to understand current environment",
                "2. Use spatial_awareness.get_spatial_context to plan navigation route", 
                "3. Use action_control.execute_movement_action to move toward target",
                "4. Repeat until target reached"
            ])
        
        # Interaction tasks
        elif any(x in task_lower for x in ["use", "cook", "prepare", "wash"]):
            recommendations.extend([
                "1. Use spatial_awareness.get_spatial_context to locate target room",
                "2. Use action_control.execute_movement_action to reach target area",
                "3. Use action_control.execute_interaction_action to interact with objects",
                "4. Use image_analysis to verify task completion"
            ])
        
        # Exploration tasks
        elif any(x in task_lower for x in ["explore", "look", "examine"]):
            recommendations.extend([
                "1. Use image_analysis.capture_dual_view_images for visual assessment",
                "2. Use spatial_awareness.get_room_connectivity_map to understand layout",
                "3. Use action_control.execute_movement_action with explore mode",
                "4. Use action_control.execute_interaction_action to examine objects"
            ])
        
        else:
            recommendations.extend([
                "1. Start with image_analysis.capture_dual_view_images to assess situation",
                "2. Use spatial_awareness.get_spatial_context for navigation planning",
                "3. Use action_control.get_available_actions to see options",
                "4. Execute appropriate actions based on task requirements"
            ])
        
        return recommendations
    
    def _build_vlm_prompt(self, task: str, prompt_data: Dict) -> str:
        """Build comprehensive VLM prompt"""
        prompt = f"""
VESPER NAVIGATION TASK: {task}

AVAILABLE MCP TOOLS:
"""
        
        for tool in prompt_data["tools_available"]:
            prompt += f"\n{tool['name'].upper()}:\n"
            prompt += f"  Description: {tool['description']}\n"
            prompt += "  Methods:\n"
            for method in tool["methods"]:
                prompt += f"    - {method['name']}: {method['description']}\n"
        
        prompt += f"\nCURRENT CONTEXT:\n"
        
        context = prompt_data["context"]
        if "spatial" in context:
            spatial = context["spatial"]
            if "current_room" in spatial:
                prompt += f"  Current Room: {spatial['current_room']}\n"
            if "actor_position" in spatial:
                pos = spatial["actor_position"]
                prompt += f"  Actor Position: ({pos['x']}, {pos['y']}, {pos['z']})\n"
        
        if "room_analysis" in context:
            room = context["room_analysis"]
            if "room_type" in room:
                prompt += f"  Room Type: {room['room_type']} (confidence: {room.get('confidence', 0):.2f})\n"
        
        prompt += f"\nRECOMMENDED APPROACH:\n"
        for rec in prompt_data["recommended_approach"]:
            prompt += f"  {rec}\n"
        
        prompt += f"""
INSTRUCTIONS:
1. Analyze the current situation using available tools
2. Plan your approach step by step
3. Execute actions one at a time
4. Use tool feedback to adapt your strategy
5. Continue until task is completed

Start by choosing which tool to use first and explain your reasoning.
"""
        
        return prompt

# Create global bridge instance
blender_bridge = VESPERBlenderBridge()

# Blender operator for MCP integration
class VESPER_OT_MCPToolExecution(bpy.types.Operator):
    """Execute VESPER MCP Tool"""
    bl_idname = "vesper.mcp_tool_execution"
    bl_label = "Execute MCP Tool"
    bl_description = "Execute VESPER MCP tool method"
    
    tool_name: bpy.props.StringProperty(name="Tool Name")
    method_name: bpy.props.StringProperty(name="Method Name")
    parameters: bpy.props.StringProperty(name="Parameters (JSON)")
    
    def execute(self, context):
        try:
            # Parse parameters
            params = {}
            if self.parameters:
                params = json.loads(self.parameters)
            
            # Execute tool
            result = blender_bridge.execute_mcp_tool(self.tool_name, self.method_name, **params)
            
            # Display result
            if "error" in result:
                self.report({'ERROR'}, f"Tool execution failed: {result['error']}")
            else:
                self.report({'INFO'}, f"Tool executed successfully: {self.tool_name}.{self.method_name}")
                print(f"MCP Tool Result: {json.dumps(result, indent=2)}")
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Execution error: {str(e)}")
            return {'CANCELLED'}

# Panel for MCP tools
class VESPER_PT_MCPToolsPanel(bpy.types.Panel):
    """VESPER MCP Tools Panel"""
    bl_label = "VESPER MCP Tools"
    bl_idname = "VESPER_PT_mcp_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "VESPER"
    
    def draw(self, context):
        layout = self.layout
        
        # Initialize session button
        layout.operator("vesper.mcp_initialize_session", text="Initialize MCP Session")
        
        # Tool status
        box = layout.box()
        box.label(text="Tool Status:")
        for tool_name, available in blender_bridge.tools_available.items():
            status = "✓" if available else "✗"
            box.label(text=f"{status} {tool_name}")
        
        # Quick actions
        box = layout.box()
        box.label(text="Quick Actions:")
        box.operator("vesper.mcp_capture_images", text="Capture All Views")
        box.operator("vesper.mcp_analyze_spatial", text="Analyze Spatial Context")
        box.operator("vesper.mcp_get_actions", text="Get Available Actions")

class VESPER_OT_MCPInitializeSession(bpy.types.Operator):
    """Initialize MCP Session"""
    bl_idname = "vesper.mcp_initialize_session"
    bl_label = "Initialize MCP Session"
    
    def execute(self, context):
        result = blender_bridge.initialize_mcp_session()
        if "error" in result:
            self.report({'ERROR'}, f"Initialization failed: {result['error']}")
        else:
            self.report({'INFO'}, f"MCP session initialized: {result['session_id']}")
        return {'FINISHED'}

class VESPER_OT_MCPCaptureImages(bpy.types.Operator):
    """Capture All Image Views"""
    bl_idname = "vesper.mcp_capture_images"
    bl_label = "Capture All Views"
    
    def execute(self, context):
        if image_analyzer:
            result = image_analyzer.capture_dual_view_images(
                include_first_person=True,
                include_bird_eye=True,
                include_reference=True
            )
            if "error" in result:
                self.report({'ERROR'}, f"Image capture failed: {result['error']}")
            else:
                views = result.get("views_captured", [])
                self.report({'INFO'}, f"Captured {len(views)} views: {', '.join(views)}")
        else:
            self.report({'ERROR'}, "Image analyzer not available")
        return {'FINISHED'}

class VESPER_OT_MCPAnalyzeSpatial(bpy.types.Operator):
    """Analyze Spatial Context"""
    bl_idname = "vesper.mcp_analyze_spatial"
    bl_label = "Analyze Spatial Context"
    
    def execute(self, context):
        if spatial_analyzer:
            result = spatial_analyzer.get_spatial_context()
            if "error" in result:
                self.report({'ERROR'}, f"Spatial analysis failed: {result['error']}")
            else:
                current_room = result.get("current_room", "Unknown")
                self.report({'INFO'}, f"Current room: {current_room}")
                print(f"Spatial Context: {json.dumps(result, indent=2)}")
        else:
            self.report({'ERROR'}, "Spatial analyzer not available")
        return {'FINISHED'}

class VESPER_OT_MCPGetActions(bpy.types.Operator):
    """Get Available Actions"""
    bl_idname = "vesper.mcp_get_actions"
    bl_label = "Get Available Actions"
    
    def execute(self, context):
        if action_controller:
            result = action_controller.get_available_actions()
            if "error" in result:
                self.report({'ERROR'}, f"Action analysis failed: {result['error']}")
            else:
                movement_count = len(result.get("movement_actions", []))
                interaction_count = len(result.get("interaction_actions", []))
                self.report({'INFO'}, f"Available: {movement_count} movements, {interaction_count} interactions")
                print(f"Available Actions: {json.dumps(result, indent=2)}")
        else:
            self.report({'ERROR'}, "Action controller not available")
        return {'FINISHED'}

# Registration
classes = [
    VESPER_OT_MCPToolExecution,
    VESPER_PT_MCPToolsPanel,
    VESPER_OT_MCPInitializeSession,
    VESPER_OT_MCPCaptureImages,
    VESPER_OT_MCPAnalyzeSpatial,
    VESPER_OT_MCPGetActions
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
    print("VESPER MCP Blender Bridge registered successfully!")
