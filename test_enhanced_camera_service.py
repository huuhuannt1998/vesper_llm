"""
Test script for the enhanced MCP camera service
"""
import sys
import os

# Add the vesper_mcp directory to the path
vesper_mcp_path = os.path.join(os.path.dirname(__file__), 'vesper_mcp')
sys.path.append(vesper_mcp_path)

try:
    from services.camera_service import (
        get_camera_recommendations, 
        get_available_cameras,
        camera_service_health
    )
    print("✓ Successfully imported camera service functions")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

async def test_camera_recommendations():
    """Test the camera recommendation system"""
    print("\n=== Testing Camera Recommendations ===")
    
    # Test navigation task
    nav_result = await get_camera_recommendations(
        current_task="navigate to the kitchen",
        actor_position="living room",
        recent_actions="walking around",
        current_context="trying to find cooking area"
    )
    print(f"Navigation task recommendation: {nav_result.get('recommended_camera', 'unknown')}")
    print(f"Confidence: {nav_result.get('confidence', 0):.2f}")
    
    # Test interaction task
    interact_result = await get_camera_recommendations(
        current_task="use the stove to cook dinner",
        actor_position="kitchen",
        recent_actions="approached stove",
        current_context="need to see precise controls"
    )
    print(f"Interaction task recommendation: {interact_result.get('recommended_camera', 'unknown')}")
    print(f"Confidence: {interact_result.get('confidence', 0):.2f}")

async def test_service_health():
    """Test service health check"""
    print("\n=== Testing Service Health ===")
    health = await camera_service_health()
    print(f"Service status: {health.get('status', 'unknown')}")
    print(f"Blender available: {health.get('blender_available', False)}")
    
    screenshot_info = health.get('screenshot_directory', {})
    print(f"Screenshot directory: {screenshot_info.get('path', 'unknown')}")
    print(f"Directory exists: {screenshot_info.get('exists', False)}")

async def main():
    """Run all tests"""
    print("Testing Enhanced MCP Camera Service")
    print("=" * 50)
    
    await test_service_health()
    await test_camera_recommendations()
    
    print("\n✓ All tests completed successfully!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
