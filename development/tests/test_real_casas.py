#!/usr/bin/env python3
"""
Quick CASAS Integration Test
Shows the real CASAS generator vs simulated events
"""

import sys
import os
from pathlib import Path
import time

# Add project to path
vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
sys.path.insert(0, vesper_root)

def test_real_casas():
    """Test the new real CASAS generator"""
    print("🏠 Testing REAL CASAS (Blender Integration Ready)")
    print("=" * 60)
    
    from casas_testbed.blender_casas_generator import BlenderCASASGenerator
    
    generator = BlenderCASASGenerator()
    
    # Simulate realistic Blender navigation sequence
    session_id = generator.start_session("p01", "vlm_navigation")
    
    print("🚶 Simulating actor navigation with realistic timing:")
    
    # Start in hallway
    print("   📍 Starting in hallway...")
    generator.actor_entered_room("hallway", (0.0, 0.0, 0.0))
    time.sleep(0.5)
    
    # Move to living room for phone call
    print("   🚶 Moving to living room...")
    generator.actor_left_room("hallway")
    generator.actor_entered_room("living_room", (1.0, 2.0, 0.0))
    time.sleep(0.3)
    
    # Execute phone call task
    print("   📞 Starting phone call task...")
    generator.task_started("phone_call")
    time.sleep(1.0)  # Phone call duration
    
    print("   📞 Ending phone call...")
    generator.task_completed("phone_call")
    time.sleep(0.2)
    
    # Move to kitchen for cooking
    print("   🚶 Moving to kitchen...")
    generator.actor_left_room("living_room")
    generator.actor_entered_room("kitchen", (5.0, 1.0, 0.0))
    time.sleep(0.3)
    
    print("   🍳 Starting cooking task...")
    generator.task_started("cook")
    time.sleep(1.5)  # Cooking duration
    
    print("   🍳 Finishing cooking...")
    generator.task_completed("cook")
    time.sleep(0.2)
    
    # Return to living room
    print("   🚶 Returning to living room...")
    generator.actor_left_room("kitchen")
    generator.actor_entered_room("living_room", (1.0, 2.0, 0.0))
    time.sleep(0.3)
    
    # End session
    print("   🏁 Ending navigation session...")
    generator.actor_left_room("living_room")
    
    dataset_file = generator.end_session()
    
    print(f"\n✅ Real navigation simulation completed!")
    print(f"📁 Dataset: {dataset_file}")
    print(f"🏷️ Type: REAL CASAS events (ready for Blender)")
    
    return dataset_file

def analyze_dataset(dataset_file):
    """Analyze the generated dataset"""
    if not dataset_file or not os.path.exists(dataset_file):
        print("❌ No dataset file to analyze")
        return
    
    print(f"\n📊 ANALYZING DATASET: {os.path.basename(dataset_file)}")
    print("=" * 60)
    
    with open(dataset_file, 'r') as f:
        lines = f.readlines()
    
    # Skip header
    events = [line.strip().split(',') for line in lines[1:]]
    
    print(f"📈 Total Events: {len(events)}")
    
    # Count by sensor type
    sensor_types = {}
    for event in events:
        if len(event) >= 3:
            sensor = event[2]
            sensor_type = sensor[0]  # M, D, A, I, T
            sensor_types[sensor_type] = sensor_types.get(sensor_type, 0) + 1
    
    print("📊 Events by Sensor Type:")
    type_names = {'M': 'Motion', 'D': 'Door', 'A': 'Appliance', 'I': 'Item', 'T': 'Temperature'}
    for sensor_type, count in sensor_types.items():
        type_name = type_names.get(sensor_type, 'Unknown')
        print(f"   {sensor_type} ({type_name}): {count} events")
    
    # Show first few events
    print("\n📋 Sample Events:")
    for i, event in enumerate(events[:8]):  # Show first 8 events
        if len(event) >= 4:
            date, time, sensor, message = event[:4]
            print(f"   {time} {sensor} {message}")
    
    if len(events) > 8:
        print(f"   ... and {len(events) - 8} more events")
    
    return len(events), sensor_types

def show_next_steps():
    """Show what to do next"""
    print("\n🎯 NEXT STEPS FOR REAL BLENDER INTEGRATION")
    print("=" * 60)
    
    print("1. 📂 Files are now organized:")
    print("   ✅ casas_testbed/blender_casas_generator.py (CASAS generator)")
    print("   ✅ casas_testbed/BLENDER_INTEGRATION_GUIDE.md (instructions)")
    print("   ✅ blender/llm_bge_navigation.py (VLM navigation - needs modification)")
    
    print("\n2. 🔗 Integration process:")
    print("   → Add CASAS imports to blender/llm_bge_navigation.py")
    print("   → Track actor room changes during navigation")
    print("   → Generate events when tasks start/complete")
    print("   → Save dataset when Blender session ends")
    
    print("\n3. 🧪 Testing:")
    print("   → Run Blender with modified navigation script")
    print("   → Execute VLM tasks (phone call, cooking, etc.)")
    print("   → Check casas_testbed/blender_datasets/ for real datasets")
    print("   → Compare with ground truth using existing evaluation system")
    
    print("\n4. 📊 Expected results:")
    print("   → Higher similarity scores vs simulated data")
    print("   → Realistic timing based on actual movement")
    print("   → Room-accurate sensor activation")
    print("   → Task-specific device interactions")

if __name__ == "__main__":
    print("🏠 VESPER-CASAS Real Integration Test")
    print("=" * 60)
    
    # Test the real CASAS generator
    dataset_file = test_real_casas()
    
    # Analyze the generated dataset
    event_count, sensor_types = analyze_dataset(dataset_file)
    
    # Show next steps
    show_next_steps()
    
    print(f"\n🎉 SUMMARY:")
    print(f"   ✅ CASAS generator working: {event_count} events generated")
    print(f"   ✅ Files organized in casas_testbed/ folder")
    print(f"   🎯 Ready for Blender VLM navigation integration")
    print(f"   📖 Next: Follow BLENDER_INTEGRATION_GUIDE.md")
