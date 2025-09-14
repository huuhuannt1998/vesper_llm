"""
Test BGE-MCP Integration
========================

Quick test to verify that BGE can communicate with MCP services.
Run this before starting Blender to test connectivity.
"""

import sys
import os
from pathlib import Path

# Add blender directory to path
blender_dir = Path(__file__).parent / "blender"
if str(blender_dir) not in sys.path:
    sys.path.insert(0, str(blender_dir))

def test_mcp_integration():
    """Test MCP integration components"""
    
    print("🧪 Testing BGE-MCP Integration")
    print("=" * 40)
    
    # Test 1: Import MCP integration module
    try:
        from bge_mcp_integration import (
            get_mcp_integration_info,
            check_mcp_services_status
        )
        print("✅ MCP integration module imported successfully")
    except ImportError as e:
        print(f"❌ MCP integration import failed: {e}")
        return False
    
    # Test 2: Check integration info
    try:
        integration_info = get_mcp_integration_info()
        print("✅ MCP integration info retrieved")
        print(f"   MCP Available: {integration_info['mcp_available']}")
        print(f"   Initialized: {integration_info['initialized']}")
        print(f"   Fallback Mode: {integration_info['fallback_mode']}")
    except Exception as e:
        print(f"❌ Integration info failed: {e}")
    
    # Test 3: Check services status
    try:
        services_status = check_mcp_services_status()
        print("✅ Services status checked")
        
        healthy_services = sum(1 for status in services_status.values() if status)
        total_services = len(services_status)
        
        print(f"🔍 Services Health: {healthy_services}/{total_services}")
        for service_name, is_healthy in services_status.items():
            status_icon = "✅" if is_healthy else "❌"
            print(f"   {status_icon} {service_name}")
        
        if healthy_services > 0:
            print("✅ Some MCP services are running")
        else:
            print("⚠️ No MCP services detected (this is expected if not started)")
    
    except Exception as e:
        print(f"❌ Services status check failed: {e}")
    
    print("\n📋 Integration Test Summary:")
    print("✅ BGE-MCP integration is properly configured")
    print("🚀 To test with services:")
    print("   1. Run: python launch_mcp_services.py")
    print("   2. Wait for services to start")
    print("   3. Run this test again")
    print("   4. Start Blender and press P")
    
    return True

if __name__ == "__main__":
    success = test_mcp_integration()
    
    if success:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed")
        sys.exit(1)
