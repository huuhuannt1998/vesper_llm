"""
VESPER FastMCP Server Test
=========================

Test version of the MCP server that can run without Blender for validation.
"""

from fastmcp import FastMCP
import asyncio
import json
from typing import Dict, List, Optional, Any

# Initialize FastMCP server
mcp = FastMCP("VESPER Navigation Tools")

@mcp.tool()
def test_connection() -> Dict[str, Any]:
    """Test tool to verify MCP server is working"""
    return {
        "status": "success",
        "message": "VESPER MCP server is running",
        "tools_available": 11,
        "version": "1.0.0"
    }

@mcp.tool()
def get_available_tools() -> Dict[str, Any]:
    """List all available tools in the MCP server"""
    return {
        "core_tools": [
            "capture_dual_view_images",
            "analyze_current_view", 
            "get_spatial_context",
            "get_room_connectivity",
            "execute_movement_action",
            "interact_with_object",
            "get_action_history"
        ],
        "advanced_tools": [
            "analyze_task_context",
            "simulate_casas_sensors", 
            "get_comprehensive_context"
        ],
        "utility_tools": [
            "test_connection"
        ],
        "total_count": 11,
        "framework": "FastMCP"
    }

@mcp.tool()
def get_system_status() -> Dict[str, Any]:
    """Get current system status and capabilities"""
    return {
        "mcp_server": "active",
        "blender_integration": "requires_blender_context",
        "tools_loaded": True,
        "config_loaded": True,
        "ready_for_vlm": True
    }

async def main():
    """Run the MCP server"""
    print("Starting VESPER MCP Server...")
    print("Available tools:")
    
    # List tools manually since decorated functions can't be called directly
    core_tools = [
        "capture_dual_view_images",
        "analyze_current_view", 
        "get_spatial_context",
        "get_room_connectivity",
        "execute_movement_action",
        "interact_with_object",
        "get_action_history"
    ]
    
    advanced_tools = [
        "analyze_task_context",
        "simulate_casas_sensors", 
        "get_comprehensive_context"
    ]
    
    utility_tools = [
        "test_connection",
        "get_available_tools",
        "get_system_status"
    ]
    
    print(f"  Core tools: {', '.join(core_tools)}")
    print(f"  Advanced tools: {', '.join(advanced_tools)}")
    print(f"  Utility tools: {', '.join(utility_tools)}")
    print(f"\nTotal tools: {len(core_tools) + len(advanced_tools) + len(utility_tools)}")
    print("Server ready for VLM integration!")
    
    # Keep server running
    try:
        await mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down VESPER MCP Server...")

if __name__ == "__main__":
    asyncio.run(main())
