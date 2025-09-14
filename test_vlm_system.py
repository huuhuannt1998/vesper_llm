"""
Quick test script for VLM Tool Selection Training System
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

async def test_vlm_system():
    """Test VLM training system components"""
    
    print("🚀 Testing VLM Tool Selection Training System")
    print("=" * 50)
    
    try:
        # Test 1: Import training system
        print("📦 Test 1: Importing VLM Training System...")
        from vlm_tool_selection_training import VLMToolTrainingSystem
        print("   ✅ VLMToolTrainingSystem imported successfully")
        
        # Test 2: Initialize system
        print("\n🔧 Test 2: Initializing system...")
        system = VLMToolTrainingSystem()
        print("   ✅ System initialized successfully")
        
        # Test 3: Check tool metadata
        print(f"\n📊 Test 3: Tool metadata loaded...")
        print(f"   📈 Available tools: {len(system.tool_metadata)}")
        print("   🛠️ Sample tools:")
        for i, tool_name in enumerate(list(system.tool_metadata.keys())[:5]):
            print(f"      {i+1}. {tool_name}")
        
        # Test 4: Generate tool list prompt
        print(f"\n📝 Test 4: Generating tool list prompt...")
        prompt = system.generate_tool_list_prompt()
        print(f"   📏 Prompt length: {len(prompt)} characters")
        print("   ✅ Prompt generated successfully")
        
        # Test 5: Test expert action system
        print(f"\n🧠 Test 5: Testing expert system...")
        
        # Create a simple context
        from vlm_tool_selection_training import ContextState
        test_context = ContextState(
            task_description="Navigate to the kitchen",
            current_room="unknown",
            actor_position=[0.0, 0.0, 0.0],
            actor_rotation=[0.0, 0.0, 0.0],
            visible_objects=[],
            recent_actions=[],
            first_person_image_path=None,
            bird_eye_image_path=None,
            spatial_context={},
            device_states={},
            task_progress={},
            timestamp=0.0
        )
        
        expert_action = await system._get_expert_action(test_context, "Navigate to the kitchen", 0)
        if expert_action:
            print(f"   🎯 Expert action: {expert_action.service_name}.{expert_action.tool_name}")
            print(f"   💭 Reasoning: {expert_action.reasoning}")
            print("   ✅ Expert system working correctly")
        else:
            print("   ⚠️ No expert action generated")
        
        # Test 6: Generate training prompt
        print(f"\n📋 Test 6: Testing training prompt generation...")
        training_prompt = system.generate_training_prompt(test_context)
        print(f"   📏 Training prompt length: {len(training_prompt)} characters")
        print("   ✅ Training prompt generated successfully")
        
        print(f"\n🎉 All tests passed! VLM Training System is ready.")
        
        # Show sample training prompt
        print(f"\n📝 Sample Training Prompt Preview:")
        print("=" * 50)
        print(training_prompt[:500] + "...")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_vlm_system())
    if success:
        print("\n✅ VLM Training System test completed successfully!")
    else:
        print("\n❌ VLM Training System test failed!")
