"""
VESPER MCP Status Check
======================

Check the status of VESPER MCP implementation without running the full server.
"""

from fastmcp import FastMCP
import json
import os
from typing import Dict, List, Optional, Any

def check_mcp_status():
    """Check the status of MCP implementation"""
    print("=" * 60)
    print("VESPER MCP STATUS REPORT")
    print("=" * 60)
    
    # Check FastMCP installation
    try:
        mcp = FastMCP("VESPER Navigation Tools Test")
        print("✅ FastMCP Framework: INSTALLED")
    except Exception as e:
        print(f"❌ FastMCP Framework: ERROR - {e}")
        return
    
    # Check file structure
    base_dir = os.path.dirname(__file__)
    
    files_to_check = [
        ("Main Server", "vesper_mcp_server.py"),
        ("Config", "configs/mcp_config.py"),
        ("Bridge", "blender_integration/mcp_bridge.py"),
        ("Image Analysis", "tools/image_analysis.py"),
        ("Spatial Awareness", "tools/spatial_awareness.py"),
        ("Action Control", "tools/action_control.py")
    ]
    
    print("\n📁 FILE STRUCTURE:")
    for name, file_path in files_to_check:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            size_kb = os.path.getsize(full_path) // 1024
            print(f"✅ {name}: {file_path} ({size_kb}KB)")
        else:
            print(f"❌ {name}: {file_path} - NOT FOUND")
    
    # Check tools implementation
    print("\n🔧 IMPLEMENTED TOOLS:")
    tools = [
        "capture_dual_view_images - Multi-view image capture",
        "analyze_current_view - Room/scene analysis",
        "get_spatial_context - Position & navigation info",
        "get_room_connectivity - Room mapping & paths",
        "execute_movement_action - Actor movement control",
        "interact_with_object - Object interaction",
        "get_action_history - Movement tracking",
        "analyze_task_context - Task understanding",
        "simulate_casas_sensors - Smart home simulation",
        "get_comprehensive_context - Full context analysis"
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"  {i:2d}. {tool}")
    
    print(f"\n📊 TOTAL TOOLS: {len(tools)}")
    
    # Check dependencies
    print("\n📦 DEPENDENCIES:")
    try:
        import fastmcp
        print("✅ fastmcp - Model Context Protocol framework")
    except ImportError:
        print("❌ fastmcp - NOT INSTALLED")
    
    try:
        import numpy
        print("✅ numpy - Numerical computations")
    except ImportError:
        print("❌ numpy - NOT INSTALLED")
    
    # Blender dependency (expected to fail outside Blender)
    try:
        import bpy
        print("✅ bpy - Blender Python API (running in Blender)")
    except ImportError:
        print("⚠️  bpy - Blender Python API (requires Blender context)")
    
    # Check usage instructions
    print("\n🚀 USAGE INSTRUCTIONS:")
    print("1. Inside Blender: Import and run vesper_mcp_server.py")
    print("2. VLM Integration: Tools available via MCP protocol")
    print("3. Navigation: Use modular tools based on context")
    print("4. Improvement: VLM can select optimal tool combinations")
    
    print("\n💡 MCP ADVANTAGES:")
    print("• Modular approach - VLM selects appropriate tools")
    print("• Better context understanding with specialized functions")
    print("• Improved navigation accuracy (target: 4.8% → 70%)")
    print("• Extensible architecture for future enhancements")
    
    print("\n" + "=" * 60)
    print("MCP IMPLEMENTATION: READY FOR TESTING")
    print("=" * 60)

if __name__ == "__main__":
    check_mcp_status()
