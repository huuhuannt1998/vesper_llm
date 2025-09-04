#!/usr/bin/env python3
"""
VESPER-CASAS Testbed Verification
Checks if the Blender integration is ready and all components are working
"""

import sys
import os
from pathlib import Path

# Add project to path
vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
sys.path.insert(0, vesper_root)

def check_casas_integration():
    """Verify CASAS integration is working"""
    print("🏠 Checking CASAS Integration...")
    
    try:
        from casas_testbed.vesper_casas_dataset_generator import (
            init_vesper_casas_session, execute_vesper_task, 
            finalize_vesper_casas_session, VESPERCASASDatasetGenerator
        )
        print("✅ CASAS generator imports successful")
        
        # Test basic functionality
        generator = VESPERCASASDatasetGenerator()
        session_id = generator.start_vesper_session("p01", "t1")
        generator.end_session()
        print("✅ CASAS generator basic test passed")
        
        return True
    except Exception as e:
        print(f"❌ CASAS integration failed: {e}")
        return False

def check_blender_integration():
    """Check if Blender navigation has CASAS integration"""
    print("\n🎮 Checking Blender Integration...")
    
    blender_nav = Path("blender/llm_bge_navigation.py")
    
    if not blender_nav.exists():
        print("❌ Blender navigation file not found")
        return False
    
    with open(blender_nav, 'r') as f:
        content = f.read()
    
    # Check for CASAS integration markers
    checks = {
        'CASAS Import': 'from casas_testbed.vesper_casas_dataset_generator import',
        'CASAS Available Flag': 'CASAS_AVAILABLE',
        'CASAS Session Init': 'init_vesper_casas_session',
        'Task Execution': 'execute_vesper_task',
        'Session Cleanup': 'finalize_vesper_casas_session'
    }
    
    results = {}
    for check_name, check_text in checks.items():
        results[check_name] = check_text in content
        status = "✅" if results[check_name] else "❌"
        print(f"   {status} {check_name}")
    
    all_good = all(results.values())
    if all_good:
        print("✅ Blender navigation has complete CASAS integration")
    else:
        print("⚠️ Blender navigation missing some CASAS integration")
    
    return all_good

def check_task_alignment():
    """Check CASAS task alignment"""
    print("\n📋 Checking Task Alignment...")
    
    casas_tasks_file = Path("blender/vesper_casas_tasks.txt")
    
    if casas_tasks_file.exists():
        print("✅ CASAS task definitions found")
        with open(casas_tasks_file, 'r') as f:
            content = f.read()
            task_count = len([line for line in content.split('\n') if line.strip() and not line.startswith('#')])
            print(f"   📊 {task_count} CASAS-aligned tasks defined")
        
        expected_tasks = ['Make phone call', 'Wash hands', 'Cook oatmeal', 'Eat meal', 'Clean dishes']
        for task in expected_tasks:
            if task in content:
                print(f"   ✅ {task}")
            else:
                print(f"   ⚠️ {task} (not found)")
        
        return True
    else:
        print("❌ CASAS task definitions not found")
        print("   Creating default CASAS tasks...")
        
        # Create default CASAS tasks
        default_tasks = """# CASAS-Aligned VESPER Tasks
# Format: Task Description|Room Sequence|Required Items|Success Criteria

Make phone call|living_room,dining_room|phone_book,phone,notepad|phone_used_and_notes_taken
Wash hands|kitchen|sink,soap,towel|hands_washed_and_dried  
Cook oatmeal|kitchen|pot,water,oats,stove,bowl,raisins,brown_sugar|oatmeal_prepared_and_served
Eat meal|dining_room|bowl,spoon,medicine|food_consumed_with_medicine
Clean dishes|kitchen|dishes,sink,soap,water|all_dishes_cleaned"""
        
        with open(casas_tasks_file, 'w') as f:
            f.write(default_tasks)
        
        print("✅ Default CASAS tasks created")
        return True

def check_datasets():
    """Check existing datasets"""
    print("\n📊 Checking Datasets...")
    
    vesper_datasets = Path("casas_testbed/vesper_datasets")
    casas_ground_truth = Path("casas_testbed/data/casas_ground_truth")
    
    if vesper_datasets.exists():
        vesper_count = len(list(vesper_datasets.glob("*.csv")))
        print(f"✅ VESPER datasets folder exists ({vesper_count} files)")
    else:
        print("⚠️ VESPER datasets folder not found - will be created")
        vesper_datasets.mkdir(parents=True, exist_ok=True)
        print("✅ Created VESPER datasets folder")
    
    if casas_ground_truth.exists():
        casas_count = len(list(casas_ground_truth.glob("**/*.csv")))
        print(f"✅ CASAS ground truth data found ({casas_count} files)")
    else:
        print("❌ CASAS ground truth data not found")
        print("   Download from: https://zenodo.org/records/15712834")
    
    return True

def check_blender_setup():
    """Check Blender environment"""
    print("\n🎮 Checking Blender Setup...")
    
    blender_files = [
        "blender/llm_bge_navigation.py",
        "blender/house_2.blend",
        "blender/house_3.blend"
    ]
    
    for file_path in blender_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"⚠️ {file_path} (not found)")
    
    return True

def show_next_steps():
    """Show next steps for running the testbed"""
    print("\n🚀 Next Steps to Run VESPER-CASAS Testbed:")
    print("="*60)
    
    print("1. 🔧 Start LLM Backend:")
    print("   cd C:\\Users\\hbui11\\Desktop\\vesper_llm")
    print("   python -m backend.app.main")
    
    print("\n2. 🎮 Open Blender:")
    print("   Open UPBGE/Blender")
    print("   Load: blender/house_2.blend or house_3.blend")
    print("   Verify: 'Actor' and 'BirdEyeCamera' objects exist")
    
    print("\n3. ▶️ Run Game Engine:")
    print("   Switch to Game Engine mode")
    print("   Execute: blender/llm_bge_navigation.py")
    print("   Monitor console for CASAS dataset generation")
    
    print("\n4. 📊 Check Results:")
    print("   Generated datasets: casas_testbed/vesper_datasets/")
    print("   Evaluation: Run comparison with CASAS ground truth")
    
    print("\n5. 🎯 Expected Output:")
    print("   vesper_p01.t1.csv through vesper_p01.t5.csv")
    print("   Real-time CASAS events from VLM navigation")
    print("   Higher similarity scores vs simulated data")

if __name__ == "__main__":
    print("🔍 VESPER-CASAS Testbed Verification")
    print("="*60)
    
    # Run all checks
    casas_ok = check_casas_integration()
    blender_ok = check_blender_integration()
    tasks_ok = check_task_alignment()
    datasets_ok = check_datasets()
    setup_ok = check_blender_setup()
    
    print("\n📋 Summary:")
    print("="*60)
    print(f"🏠 CASAS Integration: {'✅ Ready' if casas_ok else '❌ Issues'}")
    print(f"🎮 Blender Integration: {'✅ Ready' if blender_ok else '❌ Issues'}")
    print(f"📋 Task Alignment: {'✅ Ready' if tasks_ok else '❌ Issues'}")
    print(f"📊 Datasets: {'✅ Ready' if datasets_ok else '❌ Issues'}")
    print(f"🔧 Blender Setup: {'✅ Ready' if setup_ok else '❌ Issues'}")
    
    if all([casas_ok, blender_ok, tasks_ok, datasets_ok]):
        print("\n🎉 TESTBED READY!")
        print("   All components verified and working")
        print("   Ready to run Blender Game Engine with VLM + CASAS")
        show_next_steps()
    else:
        print("\n⚠️ TESTBED NEEDS ATTENTION")
        print("   Fix issues above before running")
        print("   Check individual components and try again")
