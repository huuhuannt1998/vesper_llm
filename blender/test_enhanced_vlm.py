"""
Enhanced VESPER VLM System Test
==============================

Test script to demonstrate the new VLM capabilities:
1. Virtual device interactions
2. CASAS subtask management  
3. First-person camera integration
4. Multi-modal visual processing

Usage:
1. Run in Blender Game Engine
2. Load house scene with actor
3. Execute test scenarios
"""

import sys
import os

# Add paths for VESPER modules
vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
sys.path.insert(0, vesper_root)
sys.path.insert(0, os.path.join(vesper_root, "blender"))

try:
    from enhanced_vlm_extensions import get_enhanced_vlm_manager, get_casas_subtask_manager
    from first_person_camera import get_first_person_camera, initialize_first_person_system
    from llm_bge_navigation import get_enhanced_managers
    ENHANCED_VLM_AVAILABLE = True
    print("✅ Enhanced VLM modules loaded successfully")
except ImportError as e:
    print(f"❌ Enhanced VLM modules not available: {e}")
    ENHANCED_VLM_AVAILABLE = False

def test_virtual_devices():
    """Test virtual device interaction system"""
    print("\n" + "="*50)
    print("🎮 TESTING VIRTUAL DEVICE SYSTEM")
    print("="*50)
    
    if not ENHANCED_VLM_AVAILABLE:
        print("❌ Enhanced VLM not available - skipping test")
        return
    
    vlm_manager = get_enhanced_vlm_manager()
    
    # Test kitchen devices
    print("\n🏠 Testing Kitchen Devices:")
    print("-" * 30)
    
    # Test light switch
    result = vlm_manager.interact_with_device("kitchen_light_switch", "toggle", (0, 0, 0))
    print(f"Light switch: {result}")
    
    # Test water control
    result = vlm_manager.interact_with_device("water_control", "turn_on_hot", (0, 0, 0))
    print(f"Water control: {result}")
    
    # Test stove burner
    result = vlm_manager.interact_with_device("stove_burner", "turn_on", (0, 0, 0))
    print(f"Stove burner: {result}")
    
    # Test dining room devices
    print("\n🏠 Testing Dining Room Devices:")
    print("-" * 30)
    
    # Test phone
    result = vlm_manager.interact_with_device("phone", "pickup", (0, 0, 0))
    print(f"Phone pickup: {result}")
    
    # Show generated CASAS events
    print("\n📊 Generated CASAS Events:")
    print("-" * 30)
    events = vlm_manager.get_casas_events()
    for event in events[-5:]:  # Show last 5 events
        print(f"   {event['date']} {event['time']} - {event['sensor']}: {event['message']}")

def test_casas_subtasks():
    """Test CASAS subtask management system"""
    print("\n" + "="*50)
    print("📋 TESTING CASAS SUBTASK SYSTEM")
    print("="*50)
    
    if not ENHANCED_VLM_AVAILABLE:
        print("❌ Enhanced VLM not available - skipping test")
        return
    
    subtask_manager = get_casas_subtask_manager()
    
    # Test phone call task
    print("\n📞 Testing Phone Call Task:")
    print("-" * 30)
    
    success = subtask_manager.start_task("phone call")
    print(f"Task started: {success}")
    
    # Show current subtask
    current_subtask = subtask_manager.get_current_subtask()
    if current_subtask:
        print(f"Current subtask: {current_subtask['description']}")
        print(f"Expected duration: {current_subtask['expected_duration']}s")
        print(f"Required checkpoints: {current_subtask.get('checkpoints', [])}")
    
    # Show task progress
    progress = subtask_manager.get_task_progress()
    print(f"Progress: {progress['progress_percentage']:.1f}%")
    print(f"Remaining time: {progress['estimated_remaining_time']}s")
    
    # Simulate checkpoint completion
    print("\n✅ Simulating checkpoint completion:")
    subtask_manager.complete_checkpoint("interact_phone_book")
    
    # Test subtask completion
    print("\n⏭️ Testing subtask advancement:")
    if subtask_manager.check_subtask_completion():
        print("Subtask can be completed!")
        subtask_manager.advance_subtask()
        
        next_subtask = subtask_manager.get_current_subtask()
        if next_subtask:
            print(f"Advanced to: {next_subtask['description']}")
        else:
            print("All subtasks completed!")
    else:
        print("Subtask not ready for completion")

def test_first_person_camera():
    """Test first-person camera system"""
    print("\n" + "="*50)
    print("🎥 TESTING FIRST-PERSON CAMERA SYSTEM")
    print("="*50)
    
    if not ENHANCED_VLM_AVAILABLE:
        print("❌ Enhanced VLM not available - skipping test")
        return
    
    # Initialize first-person system
    success = initialize_first_person_system()
    print(f"First-person system initialized: {success}")
    
    if not success:
        print("❌ First-person camera initialization failed")
        return
    
    camera = get_first_person_camera()
    
    # Test capture
    print("\n📸 Testing first-person capture:")
    print("-" * 30)
    
    # Simulate actor position and orientation
    test_position = (0.0, 2.0, 1.8)  # Kitchen area
    test_orientation = (0.0, 0.0, 0.0)
    
    image_data = camera.capture_first_person_view(test_position, test_orientation)
    
    if image_data:
        print(f"✅ Capture successful - Image size: {len(image_data)} characters")
        print(f"First 50 chars: {image_data[:50]}...")
    else:
        print("❌ Capture failed")
    
    # Test view description
    description = camera._generate_view_description(test_position)
    print(f"View description: {description}")
    
    # Test capture history
    history = camera.get_capture_history(3)
    print(f"Capture history entries: {len(history)}")

def test_multimodal_integration():
    """Test multi-modal VLM integration"""
    print("\n" + "="*50)
    print("🧠 TESTING MULTI-MODAL VLM INTEGRATION")
    print("="*50)
    
    if not ENHANCED_VLM_AVAILABLE:
        print("❌ Enhanced VLM not available - skipping test")
        return
    
    managers = get_enhanced_managers()
    
    print(f"VLM Manager: {'✅' if managers['vlm_manager'] else '❌'}")
    print(f"Subtask Manager: {'✅' if managers['subtask_manager'] else '❌'}")
    print(f"First Person Camera: {'✅' if managers['first_person_camera'] else '❌'}")
    print(f"Multimodal Context: {'✅' if managers['multimodal_context'] else '❌'}")
    
    # Test room device prompts
    if managers['vlm_manager']:
        print("\n🏠 Testing room-specific device prompts:")
        print("-" * 40)
        
        kitchen_prompts = managers['vlm_manager'].get_interaction_prompts_for_room("Kitchen")
        print("Kitchen prompts:")
        print(kitchen_prompts[:200] + "..." if len(kitchen_prompts) > 200 else kitchen_prompts)
        
        dining_prompts = managers['vlm_manager'].get_interaction_prompts_for_room("DiningRoom")
        print("\nDining room prompts:")
        print(dining_prompts[:200] + "..." if len(dining_prompts) > 200 else dining_prompts)

def test_task_scenarios():
    """Test complete task scenarios"""
    print("\n" + "="*50)
    print("🎯 TESTING COMPLETE TASK SCENARIOS")
    print("="*50)
    
    if not ENHANCED_VLM_AVAILABLE:
        print("❌ Enhanced VLM not available - skipping test")
        return
    
    vlm_manager = get_enhanced_vlm_manager()
    subtask_manager = get_casas_subtask_manager()
    
    # Scenario 1: Cooking task
    print("\n🍳 Scenario 1: Cooking Task")
    print("-" * 30)
    
    subtask_manager.start_task("cook oatmeal")
    progress = subtask_manager.get_task_progress()
    print(f"Started cooking task: {progress['task']}")
    
    # Simulate cooking interactions
    actor_pos = (-2.0, 2.0, 1.8)  # Kitchen position
    
    # Turn on water
    result = vlm_manager.interact_with_device("water_control", "turn_on_hot", actor_pos)
    if result.get("success"):
        subtask_manager.complete_checkpoint("interact_with_water_control")
    
    # Turn on stove
    result = vlm_manager.interact_with_device("stove_burner", "turn_on", actor_pos)
    if result.get("success"):
        subtask_manager.complete_checkpoint("interact_with_stove_burner")
    
    # Check subtask completion
    if subtask_manager.check_subtask_completion():
        subtask_manager.advance_subtask()
        print("✅ Cooking subtask advanced")
    
    # Scenario 2: Phone call task
    print("\n📞 Scenario 2: Phone Call Task")
    print("-" * 30)
    
    subtask_manager.start_task("make phone call")
    progress = subtask_manager.get_task_progress()
    print(f"Started phone task: {progress['task']}")
    
    # Simulate phone interaction
    actor_pos = (1.0, 2.0, 1.8)  # Dining room position
    
    result = vlm_manager.interact_with_device("phone", "pickup", actor_pos)
    if result.get("success"):
        subtask_manager.complete_checkpoint("interact_with_phone")
        print("✅ Phone picked up")
    
    # Show final CASAS events
    print("\n📊 Final CASAS Event Summary:")
    print("-" * 30)
    events = vlm_manager.get_casas_events()
    for event in events[-10:]:  # Show last 10 events
        print(f"   {event['time']} - {event['sensor']}: {event['message']}")

def run_all_tests():
    """Run all enhanced VLM tests"""
    print("🚀 VESPER ENHANCED VLM SYSTEM TEST SUITE")
    print("=" * 60)
    
    if not ENHANCED_VLM_AVAILABLE:
        print("❌ Enhanced VLM system not available")
        print("Please ensure enhanced_vlm_extensions.py and first_person_camera.py are accessible")
        return False
    
    try:
        test_virtual_devices()
        test_casas_subtasks()
        test_first_person_camera()
        test_multimodal_integration()
        test_task_scenarios()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("Enhanced VLM system is ready for use")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_all_tests()
