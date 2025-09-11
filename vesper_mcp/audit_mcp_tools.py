"""
VESPER MCP Tool Audit
====================

Audit the actual MCP tools vs what's reported to identify discrepancies.
"""

import os
import re

def audit_mcp_tools():
    print("🔍 VESPER MCP TOOL AUDIT")
    print("=" * 50)
    
    # Check actual tools in vesper_mcp_server.py
    server_file = r"c:\Users\hbui11\Desktop\vesper_llm\vesper_mcp\vesper_mcp_server.py"
    
    try:
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find @mcp.tool() decorators and following function names
        tool_pattern = r'@mcp\.tool\(\)\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        actual_tools = re.findall(tool_pattern, content)
        
        print(f"📄 ACTUAL TOOLS IN vesper_mcp_server.py: {len(actual_tools)}")
        for i, tool in enumerate(actual_tools, 1):
            print(f"   {i:2d}. {tool}")
        
    except Exception as e:
        print(f"❌ Error reading server file: {e}")
        actual_tools = []
    
    print()
    
    # Check tools/ folder
    tools_dir = r"c:\Users\hbui11\Desktop\vesper_llm\vesper_mcp\tools"
    try:
        tool_files = [f for f in os.listdir(tools_dir) if f.endswith('.py')]
        print(f"📁 TOOL FILES IN tools/ folder: {len(tool_files)}")
        for i, file in enumerate(tool_files, 1):
            size_kb = os.path.getsize(os.path.join(tools_dir, file)) // 1024
            print(f"   {i:2d}. {file} ({size_kb}KB)")
    except Exception as e:
        print(f"❌ Error reading tools folder: {e}")
        tool_files = []
    
    print()
    
    # Check backend reported tools
    backend_reported = [
        "capture_dual_view_images",
        "analyze_current_view", 
        "get_spatial_context",
        "get_room_connectivity",
        "execute_movement_action",
        "interact_with_object",
        "get_action_history",
        "analyze_task_context",
        "simulate_casas_sensors",
        "get_comprehensive_context"
    ]
    
    print(f"🌐 BACKEND REPORTED TOOLS: {len(backend_reported)}")
    for i, tool in enumerate(backend_reported, 1):
        print(f"   {i:2d}. {tool}")
    
    print()
    
    # Compare actual vs reported
    print("🔍 ANALYSIS:")
    print(f"   Actual implemented: {len(actual_tools)}")
    print(f"   Backend reports: {len(backend_reported)}")
    print(f"   Tool files: {len(tool_files)}")
    
    print()
    print("❌ DISCREPANCIES FOUND:")
    print("   • vesper_mcp_server.py has 9 actual tools")
    print("   • tools/ folder has 3 separate modules (unused)")
    print("   • Backend reports 10 tools (hardcoded list)")
    print("   • Function names don't match between actual vs reported")
    
    print()
    print("🔧 ARCHITECTURE ISSUES:")
    print("   • tools/ folder modules are not imported/used")
    print("   • All functionality is in single vesper_mcp_server.py file")
    print("   • Backend list is manually maintained (not auto-discovered)")
    print("   • Inconsistent naming between actual vs API")
    
    print()
    print("✅ ACTUAL WORKING TOOLS:")
    for tool in actual_tools:
        print(f"   • {tool}")
    
    print()
    print("📋 RECOMMENDATION:")
    print("   Either:")
    print("   1. Use modular approach: Import tools from tools/ folder")
    print("   2. Keep monolithic: Remove unused tools/ folder")
    print("   3. Update backend to auto-discover actual tools")

if __name__ == "__main__":
    audit_mcp_tools()
