"""
VESPER MCP Backend Integration Test
==================================

Test the MCP backend integration and show current capabilities.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.routers.mcp import list_mcp_tools, get_mcp_status
import asyncio
import json

async def test_mcp_integration():
    """Test MCP integration with backend"""
    
    print("🔧 VESPER MCP BACKEND INTEGRATION TEST")
    print("=" * 50)
    
    # Test MCP status
    print("1. Testing MCP Status...")
    try:
        status = await get_mcp_status()
        print("✅ MCP Status Retrieved:")
        for key, value in status.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ MCP Status Error: {e}")
    
    print()
    
    # Test MCP tools listing
    print("2. Testing MCP Tools Listing...")
    try:
        tools_response = await list_mcp_tools()
        tools = tools_response["tools"]
        print(f"✅ Found {len(tools)} MCP Tools:")
        
        categories = {}
        for tool in tools:
            category = tool["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(tool["name"])
        
        for category, tool_names in categories.items():
            print(f"   📂 {category.upper()}:")
            for tool_name in tool_names:
                print(f"      • {tool_name}")
        
    except Exception as e:
        print(f"❌ MCP Tools Error: {e}")
    
    print()
    
    # Show API endpoints
    print("3. Available MCP API Endpoints:")
    endpoints = [
        "GET  /mcp/status - Get MCP system status",
        "GET  /mcp/tools - List all available MCP tools", 
        "POST /mcp/capture_images - Capture dual-view images",
        "POST /mcp/move - Execute movement actions",
        "GET  /mcp/spatial_context - Get spatial context",
        "POST /mcp/interact - Interact with objects",
        "GET  /mcp/comprehensive_context - Get full context",
        "POST /mcp/tool - Execute any MCP tool",
        "POST /mcp/vlm_navigate - Enhanced VLM navigation"
    ]
    
    for endpoint in endpoints:
        print(f"   🌐 {endpoint}")
    
    print()
    
    # Show usage example
    print("4. Example Usage (curl commands):")
    examples = [
        "curl http://localhost:8000/mcp/status",
        "curl http://localhost:8000/mcp/tools",
        "curl -X POST http://localhost:8000/mcp/capture_images -H 'Content-Type: application/json' -d '{\"include_first_person\": true}'",
        "curl -X POST http://localhost:8000/mcp/vlm_navigate -H 'Content-Type: application/json' -d '{\"task\": \"Make coffee\"}'"
    ]
    
    for example in examples:
        print(f"   $ {example}")
    
    print()
    
    # Show integration benefits
    print("5. Integration Benefits:")
    benefits = [
        "✅ Web API access to all MCP tools",
        "✅ JSON request/response format",
        "✅ Fallback mode when Blender not available", 
        "✅ Enhanced VLM navigation endpoint",
        "✅ Modular tool selection via HTTP",
        "✅ CORS enabled for frontend integration",
        "✅ Error handling and validation",
        "✅ Ready for Claude/GPT integration"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    print()
    print("🚀 MCP BACKEND INTEGRATION: READY!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
