"""
VESPER Interaction System - Complete Demo
Demonstrates all interaction features working together
"""

import time
import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from vesper_interaction_integration import get_interaction_system


def demo_task_workflow():
    """Demonstrate a complete task workflow with all features"""
    
    print("="*70)
    print("VESPER INTERACTION SYSTEM - COMPLETE DEMO")
    print("="*70)
    print()
    
    # Initialize system
    print("🚀 Initializing VESPER Interaction System...")
    system = get_interaction_system()
    print()
    
    # Simulate actor position
    actor_position = [5.0, 3.0]
    
    # =========================================================================
    # TASK 1: Make a phone call (short duration)
    # =========================================================================
    print("\n" + "="*70)
    print("TASK 1: Make a phone call")
    print("="*70)
    
    task1_context = system.start_task_with_interactions("Make a phone call", actor_position)
    
    # Simulate navigation to phone
    print("\n📍 Navigating to phone...")
    time.sleep(1)
    
    # Actor reaches phone (auto-interaction)
    print("🤝 Near phone - auto-interaction triggered")
    system.interaction_handler.start_interaction("Phone", "Make a phone call")
    
    # Simulate phone call (5 minutes virtual time, 3 seconds real time)
    print("📞 Making phone call (accelerated time)...")
    system.handle_long_duration_task("phone_call", 300, max_real_duration=3.0)
    
    # End interaction
    system.interaction_handler.end_interaction("Phone")
    
    # Complete task
    system.complete_task("Make a phone call", success=True)
    
    time.sleep(1)
    
    # =========================================================================
    # TASK 2: Wash hands (simple task)
    # =========================================================================
    print("\n" + "="*70)
    print("TASK 2: Wash hands")
    print("="*70)
    
    actor_position = [3.0, 5.0]  # Moved to kitchen
    task2_context = system.start_task_with_interactions("Wash hands", actor_position)
    
    print("\n📍 Navigating to sink...")
    time.sleep(1)
    
    # Interact with sink
    print("🤝 Using sink")
    system.interaction_handler.start_interaction("KitchenSink", "Wash hands")
    
    # Wash hands (1 minute virtual, 2 seconds real)
    print("🚰 Washing hands (accelerated)...")
    system.handle_long_duration_task("wash_hands", 60, max_real_duration=2.0)
    
    system.interaction_handler.end_interaction("KitchenSink")
    system.complete_task("Wash hands", success=True)
    
    time.sleep(1)
    
    # =========================================================================
    # TASK 3: Cook oatmeal (complex task with multiple interactions)
    # =========================================================================
    print("\n" + "="*70)
    print("TASK 3: Cook oatmeal")
    print("="*70)
    
    task3_context = system.start_task_with_interactions("Cook oatmeal", actor_position)
    
    # Multiple cooking steps
    print("\n🔥 Step 1: Using stove")
    system.interaction_handler.start_interaction("Stove", "Cook oatmeal")
    system.device_manager.control_device("D002", "on")  # Turn on stove
    
    print("⏱️  Cooking on stove (15 minutes → 4 seconds)...")
    system.handle_long_duration_task("cooking", 900, max_real_duration=4.0)
    
    system.interaction_handler.end_interaction("Stove")
    system.device_manager.control_device("D002", "off")  # Turn off stove
    
    print("\n🍽️  Step 2: Getting bowl from sink area")
    system.interaction_handler.start_interaction("KitchenSink", "Get bowl")
    time.sleep(1)
    system.interaction_handler.end_interaction("KitchenSink")
    
    system.complete_task("Cook oatmeal", success=True)
    
    time.sleep(1)
    
    # =========================================================================
    # TASK 4: Eat meal (using dining table)
    # =========================================================================
    print("\n" + "="*70)
    print("TASK 4: Eat meal")
    print("="*70)
    
    actor_position = [7.0, 2.0]  # Moved to dining room
    task4_context = system.start_task_with_interactions("Eat meal", actor_position)
    
    print("\n🪑 Sitting at dining table")
    system.interaction_handler.start_interaction("DiningTable", "Eat meal")
    
    print("🍴 Eating (20 minutes → 3 seconds)...")
    system.handle_long_duration_task("eating", 1200, max_real_duration=3.0)
    
    system.interaction_handler.end_interaction("DiningTable")
    system.complete_task("Eat meal", success=True)
    
    time.sleep(1)
    
    # =========================================================================
    # TASK 5: Clean dishes
    # =========================================================================
    print("\n" + "="*70)
    print("TASK 5: Clean dishes")
    print("="*70)
    
    actor_position = [3.0, 5.0]  # Back to kitchen
    task5_context = system.start_task_with_interactions("Clean dishes", actor_position)
    
    print("\n🧽 Using sink to clean dishes")
    system.interaction_handler.start_interaction("KitchenSink", "Clean dishes")
    system.interaction_handler.start_interaction("Dishes", "Clean dishes")
    
    print("💧 Cleaning dishes (5 minutes → 2 seconds)...")
    system.handle_long_duration_task("cleaning", 300, max_real_duration=2.0)
    
    system.interaction_handler.end_interaction("Dishes")
    system.interaction_handler.end_interaction("KitchenSink")
    system.complete_task("Clean dishes", success=True)
    
    time.sleep(1)
    
    # =========================================================================
    # BONUS: Demonstrate long sleep task
    # =========================================================================
    print("\n" + "="*70)
    print("BONUS DEMO: Go to sleep (8 hours in 5 seconds)")
    print("="*70)
    
    actor_position = [10.0, 8.0]  # Bedroom
    task_bonus = system.start_task_with_interactions("Go to sleep", actor_position)
    
    print("\n🛏️  Getting into bed")
    system.interaction_handler.start_interaction("Bed", "Go to sleep")
    
    # Turn off bedroom light
    system.device_manager.control_device("D008", "off")
    
    print("😴 Sleeping (8 hours → 5 seconds)...")
    system.handle_long_duration_task("sleep", 8*3600, max_real_duration=5.0)
    
    # Wake up - turn on light
    system.device_manager.control_device("D008", "on")
    
    system.interaction_handler.end_interaction("Bed")
    system.complete_task("Go to sleep", success=True)
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("SESSION COMPLETE - GENERATING REPORTS")
    print("="*70)
    
    # Print comprehensive summary
    system.print_session_summary()
    
    # Export all data
    system.export_all_data()
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETED SUCCESSFULLY")
    print("="*70)
    print("\nAll data has been exported to:")
    print(f"  {system.item_sensor_manager.dataset_dir}")
    print("\nGenerated files:")
    print("  - item_sensor_log_*.txt (CASAS format)")
    print("  - item_interactions_*.json (detailed)")
    print("  - device_log_*.json")
    print("  - virtual_time_log.json")
    print()


if __name__ == "__main__":
    try:
        demo_task_workflow()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
