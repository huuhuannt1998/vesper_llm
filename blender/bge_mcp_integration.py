"""
BGE MCP Integration Adapter
===========================

This script provides a drop-in replacement for direct function calls in llm_bge_navigation.py,
redirecting them to MCP microservices while maintaining backward compatibility.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for BGE imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from bge_mcp_client import get_bge_mcp_client, initialize_bge_mcp_integration
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ MCP client not available: {e}")
    MCP_AVAILABLE = False

class MCPIntegrationAdapter:
    """Adapter class that provides backward compatibility for existing BGE code"""
    
    def __init__(self):
        self.mcp_client = None
        self.initialized = False
        self.fallback_mode = False
        
        if MCP_AVAILABLE:
            self.initialize_mcp_integration()
    
    def initialize_mcp_integration(self) -> bool:
        """Initialize MCP integration"""
        
        try:
            self.initialized = initialize_bge_mcp_integration()
            
            if self.initialized:
                self.mcp_client = get_bge_mcp_client()
                print("✅ MCP integration adapter ready")
            else:
                print("⚠️ MCP services not fully available - using fallback mode")
                self.fallback_mode = True
            
            return self.initialized
            
        except Exception as e:
            print(f"❌ MCP integration failed: {str(e)}")
            self.fallback_mode = True
            return False
    
    def get_enhanced_context(self, current_task: str = None, scene_data: dict = None) -> dict:
        """Get enhanced context from MCP services or fallback"""
        
        if self.mcp_client and not self.fallback_mode:
            try:
                context = self.mcp_client.get_comprehensive_context(
                    current_task=current_task,
                    additional_context={"scene_data": scene_data} if scene_data else None
                )
                
                if context:
                    return context
            except Exception as e:
                print(f"⚠️ MCP context request failed: {str(e)}")
        
        # Fallback to basic context
        return {
            "timestamp": __import__("time").time(),
            "current_task": current_task,
            "scene_data": scene_data or {},
            "mode": "fallback",
            "mcp_available": False
        }
    
    def capture_dual_view_images(self, scene_name: str = None, analysis_focus: str = None) -> dict:
        """Capture images via MCP camera service or fallback"""
        
        if self.mcp_client and not self.fallback_mode:
            try:
                result = self.mcp_client.capture_dual_view_images(scene_name, analysis_focus)
                if result:
                    return result
            except Exception as e:
                print(f"⚠️ MCP image capture failed: {str(e)}")
        
        # Fallback - simulate image capture
        print("🔄 Fallback: Simulating image capture")
        return {
            "success": True,
            "images": {
                "overhead": f"fallback_overhead_{scene_name or 'unknown'}.jpg",
                "first_person": f"fallback_fp_{scene_name or 'unknown'}.jpg"
            },
            "analysis": "Basic fallback analysis",
            "mode": "fallback"
        }
    
    def get_spatial_context(self, include_navigation: bool = True) -> dict:
        """Get spatial context via MCP spatial service or fallback"""
        
        if self.mcp_client and not self.fallback_mode:
            try:
                result = self.mcp_client.get_spatial_context(include_navigation)
                if result:
                    return result
            except Exception as e:
                print(f"⚠️ MCP spatial context failed: {str(e)}")
        
        # Fallback - basic spatial data
        print("🔄 Fallback: Using basic spatial context")
        return {
            "position": {"x": 0, "y": 0, "z": 0},
            "orientation": {"x": 0, "y": 0, "z": 0},
            "room": "unknown",
            "visible_objects": [],
            "navigation_options": ["forward", "turn_left", "turn_right"],
            "mode": "fallback"
        }
    
    def execute_movement_action(self, action: str, parameters: dict = None) -> dict:
        """Execute movement via MCP movement service or fallback"""
        
        if self.mcp_client and not self.fallback_mode:
            try:
                result = self.mcp_client.execute_movement_action(action, parameters or {})
                if result:
                    return result
            except Exception as e:
                print(f"⚠️ MCP movement execution failed: {str(e)}")
        
        # Fallback - simulate movement
        print(f"🔄 Fallback: Simulating movement action '{action}'")
        return {
            "success": True,
            "action": action,
            "parameters": parameters or {},
            "result": f"Fallback execution of {action}",
            "mode": "fallback"
        }
    
    def create_vlm_decision_prompt(self, current_task: str, context: dict = None) -> str:
        """Create VLM decision prompt via MCP orchestration or fallback"""
        
        if self.mcp_client and not self.fallback_mode:
            try:
                prompt_data = self.mcp_client.create_vlm_decision_prompt(current_task, context)
                if prompt_data and "prompt" in prompt_data:
                    return prompt_data["prompt"]
            except Exception as e:
                print(f"⚠️ MCP prompt creation failed: {str(e)}")
        
        # Fallback prompt
        context_str = str(context) if context else "No context available"
        return f"""Task: {current_task}
Context: {context_str}
Mode: Fallback (MCP services unavailable)

Please provide navigation instructions for this task."""
    
    def execute_tool_action(self, tool_name: str, parameters: dict) -> dict:
        """Execute tool action via MCP orchestration or fallback"""
        
        if self.mcp_client and not self.fallback_mode:
            try:
                result = self.mcp_client.execute_tool_action(tool_name, parameters)
                if result:
                    return result
            except Exception as e:
                print(f"⚠️ MCP tool execution failed: {str(e)}")
        
        # Fallback tool execution
        print(f"🔄 Fallback: Simulating tool '{tool_name}'")
        return {
            "success": True,
            "tool": tool_name,
            "parameters": parameters,
            "result": f"Fallback execution of {tool_name}",
            "mode": "fallback"
        }
    
    def plan_task_sequence(self, task_description: str, constraints: list = None) -> dict:
        """Plan task sequence via MCP task planning service or fallback"""
        
        if self.mcp_client and not self.fallback_mode:
            try:
                result = self.mcp_client.plan_task_sequence(task_description, constraints)
                if result:
                    return result
            except Exception as e:
                print(f"⚠️ MCP task planning failed: {str(e)}")
        
        # Fallback planning
        print(f"🔄 Fallback: Basic task planning for '{task_description}'")
        return {
            "task_sequence": [
                {"step": 1, "action": "analyze_environment"},
                {"step": 2, "action": "plan_navigation"},
                {"step": 3, "action": "execute_movement"}
            ],
            "estimated_duration": 30,
            "complexity": "medium",
            "mode": "fallback"
        }

# Global adapter instance
_mcp_adapter = None

def get_mcp_adapter() -> MCPIntegrationAdapter:
    """Get or create MCP integration adapter"""
    
    global _mcp_adapter
    
    if _mcp_adapter is None:
        _mcp_adapter = MCPIntegrationAdapter()
    
    return _mcp_adapter

# Convenience functions for direct use in llm_bge_navigation.py

def initialize_mcp_for_bge() -> bool:
    """Initialize MCP integration for BGE"""
    
    adapter = get_mcp_adapter()
    return adapter.initialized

def get_enhanced_context_for_navigation(current_task: str = None, scene_data: dict = None) -> dict:
    """Get enhanced context for navigation"""
    
    adapter = get_mcp_adapter()
    return adapter.get_enhanced_context(current_task, scene_data)

def capture_scene_images(scene_name: str = None, focus: str = None) -> dict:
    """Capture scene images"""
    
    adapter = get_mcp_adapter()
    return adapter.capture_dual_view_images(scene_name, focus)

def get_navigation_context() -> dict:
    """Get navigation context"""
    
    adapter = get_mcp_adapter()
    return adapter.get_spatial_context(include_navigation=True)

def execute_navigation_action(action: str, params: dict = None) -> dict:
    """Execute navigation action"""
    
    adapter = get_mcp_adapter()
    return adapter.execute_movement_action(action, params)

def create_llm_prompt_for_task(task: str, context: dict = None) -> str:
    """Create LLM prompt for task"""
    
    adapter = get_mcp_adapter()
    return adapter.create_vlm_decision_prompt(task, context)

def execute_llm_tool_suggestion(tool_name: str, params: dict) -> dict:
    """Execute LLM tool suggestion"""
    
    adapter = get_mcp_adapter()
    return adapter.execute_tool_action(tool_name, params)

# Utility functions

def check_mcp_services_status() -> dict:
    """Check status of MCP services"""
    
    adapter = get_mcp_adapter()
    
    if adapter.mcp_client and not adapter.fallback_mode:
        try:
            return adapter.mcp_client.check_services_health()
        except Exception as e:
            print(f"⚠️ Health check failed: {str(e)}")
    
    return {
        "orchestration": False,
        "camera": False,
        "spatial": False,
        "movement": False,
        "task_planning": False
    }

def get_mcp_integration_info() -> dict:
    """Get MCP integration information"""
    
    adapter = get_mcp_adapter()
    
    return {
        "mcp_available": MCP_AVAILABLE,
        "initialized": adapter.initialized,
        "fallback_mode": adapter.fallback_mode,
        "services_status": check_mcp_services_status()
    }
