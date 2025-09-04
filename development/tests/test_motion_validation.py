"""
Test VESPER Motion Validation System
===================================

Simple test script to verify motion sensor validation works
"""

import asyncio
import sys
import os

# Add the blender directory to path
blender_dir = r"C:\Users\hbui11\Desktop\vesper_llm\blender"
if blender_dir not in sys.path:
    sys.path.insert(0, blender_dir)

from vesper_motion_validation import VESPERMotionValidationSystem

async def test_motion_validation():
    """Test the motion validation system"""
    print("🧪 Testing VESPER Motion Validation System")
    print("=" * 50)
    
    # Initialize system
    validation_system = VESPERMotionValidationSystem()
    validation_system.setup_room_boundaries()
    
    print(f"📐 Room boundaries configured: {len(validation_system.room_boundaries)} rooms")
    
    # Test room detection
    test_positions = [
        (-3, -2, "living_room"),    # Living room
        (4, 1, "kitchen"),          # Kitchen  
        (1, 4, "dining_room"),      # Dining room
        (-4, 4, "bedroom"),         # Bedroom
        (6, 6, "bathroom"),         # Bathroom
        (0, 1, "hallway"),          # Hallway
        (-6, 0, "office"),          # Office
        (8, -2, "garage"),          # Garage
        (15, 15, "unknown")         # Outside boundaries
    ]
    
    print("\n🎯 Testing room detection:")
    for x, y, expected_room in test_positions:
        detected_room = validation_system.detect_actor_room((x, y))
        status = "✅" if detected_room == expected_room else "❌"
        print(f"   {status} Position ({x:2}, {y:2}) → Expected: {expected_room:12} | Detected: {detected_room}")
    
    # Test virtual sensor deployment (requires backend)
    print("\n🚀 Testing virtual sensor deployment:")
    try:
        deployment_success = await validation_system.deploy_virtual_motion_sensors()
        if deployment_success:
            print("✅ Virtual sensors deployed successfully")
            
            # Test sensor updates
            print("\n🔄 Testing sensor updates:")
            test_movement = [
                (-3, -2),  # Living room
                (0, 1),    # Hallway
                (4, 1),    # Kitchen
                (1, 4),    # Dining room
            ]
            
            for position in test_movement:
                await validation_system.update_motion_sensors(position)
                await asyncio.sleep(0.5)  # Small delay
            
            # Test VLM validation
            print("\n🎯 Testing VLM validation:")
            validation_tests = [
                ("living_room", (-3, -2)),  # Correct
                ("kitchen", (4, 1)),        # Correct  
                ("bedroom", (1, 4)),        # Incorrect - should be dining_room
            ]
            
            for intended_room, actual_pos in validation_tests:
                result = validation_system.validate_vlm_navigation(intended_room, actual_pos)
                status = "✅" if result['validation_success'] else "❌"
                print(f"   {status} VLM: {intended_room} | Actual: {result['sensor_detected']}")
            
            # Generate test report
            report_file = validation_system.save_validation_report("test_navigation")
            print(f"\n📊 Test report saved: {report_file}")
            
            # Cleanup
            await validation_system.cleanup_sensors()
            print("🧹 Cleanup complete")
            
        else:
            print("⚠️ Virtual sensor deployment failed (backend not available?)")
            print("   This is normal if Docker backend is not running")
            
    except Exception as e:
        print(f"⚠️ Virtual sensor test failed: {e}")
        print("   This is expected if backend is not running")
    
    print("\n🎉 Motion validation system test complete!")

if __name__ == "__main__":
    asyncio.run(test_motion_validation())
