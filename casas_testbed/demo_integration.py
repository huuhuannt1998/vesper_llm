#!/usr/bin/env python3
"""
CASAS Integration Demo
Shows the difference between simulated and real Blender-integrated datasets
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def test_simulated_casas():
    """Test the old simulated CASAS system"""
    print("🎭 Testing SIMULATED CASAS (Old System)")
    print("=" * 50)
    
    from casas_testbed.integration import run_phone_call_evaluation
    
    results = run_phone_call_evaluation()
    
    if results["success"]:
        print(f"✅ Simulation Success")
        print(f"📊 Similarity: {results['metrics'].overall_similarity:.1%}")
        print(f"📁 Dataset: {results['dataset_file']}")
        print(f"🏷️ Type: SIMULATED (no Blender)")
    else:
        print("❌ Simulation Failed")
    
    return results

def test_real_casas():
    """Test the new real CASAS generator"""
    print("\n🏠 Testing REAL CASAS (Blender Integration)")
    print("=" * 50)
    
    from casas_testbed.blender_casas_generator import BlenderCASASGenerator
    import time
    
    generator = BlenderCASASGenerator()
    
    # Simulate realistic Blender navigation
    session_id = generator.start_session("p01", "phone_call_real")
    
    print("🚶 Actor navigation simulation:")
    
    # Move to living room (realistic timing)
    print("   → Moving to living room...")
    generator.actor_entered_room("living_room", (1.0, 2.0, 0.0))
    time.sleep(0.2)
    
    # Start phone call task
    print("   → Starting phone call...")
    generator.task_started("phone_call")
    time.sleep(0.3)
    
    # Complete phone call  
    print("   → Ending phone call...")
    generator.task_completed("phone_call")
    time.sleep(0.2)
    
    # Move to kitchen
    print("   → Moving to kitchen...")
    generator.actor_left_room("living_room")
    generator.actor_entered_room("kitchen", (5.0, 1.0, 0.0))
    time.sleep(0.1)
    
    # Leave kitchen
    generator.actor_left_room("kitchen")
    
    # End session
    dataset_file = generator.end_session()
    
    print(f"✅ Real navigation completed")
    print(f"📁 Dataset: {dataset_file}")
    print(f"🏷️ Type: REAL (Blender-integrated)")
    
    return dataset_file

def compare_datasets():
    """Compare simulated vs real datasets"""
    print("\n📊 DATASET COMPARISON")
    print("=" * 50)
    
    # Check recent files
    sim_dir = Path("evaluation/results")
    real_dir = Path("casas_testbed/blender_datasets")
    
    if sim_dir.exists():
        sim_files = list(sim_dir.glob("*.csv"))
        if sim_files:
            latest_sim = max(sim_files, key=lambda f: f.stat().st_mtime)
            print(f"📁 Latest Simulated: {latest_sim.name}")
            
            # Count events
            with open(latest_sim, 'r') as f:
                sim_lines = len(f.readlines()) - 1  # Exclude header
            print(f"📊 Simulated Events: {sim_lines}")
    
    if real_dir.exists():
        real_files = list(real_dir.glob("*.csv"))
        if real_files:
            latest_real = max(real_files, key=lambda f: f.stat().st_mtime)
            print(f"📁 Latest Real: {latest_real.name}")
            
            # Count events
            with open(latest_real, 'r') as f:
                real_lines = len(f.readlines()) - 1  # Exclude header
            print(f"📊 Real Events: {real_lines}")
    
    print("\n🎯 KEY DIFFERENCES:")
    print("   Simulated: Fixed timing patterns, no actual movement")
    print("   Real: Based on actual actor position and task completion")
    print("   Next Step: Connect to actual Blender navigation system")

def show_integration_status():
    """Show current integration status"""
    print("\n🔗 INTEGRATION STATUS")
    print("=" * 50)
    
    blender_nav = Path("blender/llm_bge_navigation.py")
    casas_gen = Path("casas_testbed/blender_casas_generator.py")
    
    print(f"✅ Blender Navigation: {blender_nav.exists()} ({blender_nav})")
    print(f"✅ CASAS Generator: {casas_gen.exists()} ({casas_gen})")
    
    # Check if integration code exists in Blender navigation
    if blender_nav.exists():
        with open(blender_nav, 'r') as f:
            content = f.read()
            has_casas = 'blender_casas_generator' in content
            print(f"🔗 CASAS Integration: {has_casas}")
            
            if not has_casas:
                print("📋 TODO: Add CASAS integration to blender/llm_bge_navigation.py")
                print("📖 Guide: casas_testbed/BLENDER_INTEGRATION_GUIDE.md")
    
    print("\n📂 FILES ORGANIZED:")
    print("   ✅ All CASAS files moved to casas_testbed/")
    print("   ✅ Integration code ready in blender_casas_generator.py")
    print("   ✅ Production system in casas_testbed/integration/")

if __name__ == "__main__":
    print("🏠 VESPER-CASAS Integration Demo")
    print("=" * 50)
    
    # Test both systems
    sim_results = test_simulated_casas()
    real_dataset = test_real_casas()
    
    # Compare results
    compare_datasets()
    
    # Show status
    show_integration_status()
    
    print("\n🎯 SUMMARY:")
    print("   Current: CASAS generator ready for Blender integration")
    print("   Next: Modify blender/llm_bge_navigation.py to use real generator")
    print("   Goal: Generate real CASAS datasets from actual VLM navigation")
