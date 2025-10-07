#!/usr/bin/env python3
"""
Complete CASAS Integration Setup & Verification
Checks all components and provides final manual setup instructions
"""

import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ MISSING {description}: {filepath}")
        return False

def check_code_presence(filepath, search_string, description):
    """Check if code snippet exists in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"⚠️  NEEDS MANUAL ADD: {description}")
                return False
    except Exception as e:
        print(f"❌ Error checking {description}: {e}")
        return False

def main():
    print("=" * 80)
    print("CASAS MOTION SENSOR INTEGRATION - SETUP VERIFICATION")
    print("=" * 80)
    print()
    
    # Base paths
    base_path = Path(__file__).parent
    blender_path = base_path / "blender"
    
    print("📁 COMPONENT FILES CHECK")
    print("-" * 80)
    
    # Check core files
    casas_logger_exists = check_file_exists(
        blender_path / "casas_motion_logger.py",
        "CASAS Motion Logger"
    )
    
    nav_exists = check_file_exists(
        blender_path / "llm_bge_navigation.py",
        "BGE Navigation System"
    )
    
    eval_exists = check_file_exists(
        base_path / "evaluation" / "vesper_dataset_pipeline.py",
        "Evaluation Pipeline"
    )
    
    print()
    print("🔍 CODE INTEGRATION CHECK")
    print("-" * 80)
    
    nav_file = blender_path / "llm_bge_navigation.py"
    
    # Check imports
    imports_ok = check_code_presence(
        nav_file,
        "from casas_motion_logger import CASASMotionSensorLogger",
        "CASAS logger import"
    )
    
    # Check motion sensor tracking in execute_movement
    tracking_ok = check_code_presence(
        nav_file,
        "casas_motion_logger.check_motion_sensors",
        "Motion sensor tracking in execute_movement()"
    )
    
    # Check logger initialization
    init_ok = check_code_presence(
        nav_file,
        "bge.logic.casas_motion_logger = CASASMotionSensorLogger()",
        "CASAS logger initialization in main()"
    )
    
    # Check task completion export
    task_export_ok = check_code_presence(
        nav_file,
        "_export_datasets",
        "CASAS export on task completion"
    )
    
    print()
    print("=" * 80)
    print("SETUP STATUS SUMMARY")
    print("=" * 80)
    
    all_checks = [
        casas_logger_exists,
        nav_exists,
        eval_exists,
        imports_ok,
        tracking_ok,
        init_ok,
        task_export_ok
    ]
    
    completed = sum(all_checks)
    total = len(all_checks)
    
    print(f"\n✨ Progress: {completed}/{total} components ready")
    
    if completed == total:
        print("\n🎉 COMPLETE! All CASAS integration components are in place!")
        print("\n📊 Your system will now:")
        print("   • Track actor movement through motion sensors (motion1-6)")
        print("   • Generate CASAS-format logs (vesper_motion_sensors.txt)")
        print("   • Export data for ground truth comparison")
        print("\n🚀 Ready to run BGE navigation with CASAS logging!")
    else:
        print("\n⚠️  MANUAL STEPS REQUIRED")
        print("-" * 80)
        
        if not init_ok:
            print("\n📝 STEP 1: Add CASAS Logger Initialization")
            print("   File: blender/llm_bge_navigation.py (around line 1103)")
            print("   Find:")
            print("""
        # Initialize metrics logging
        if not hasattr(bge.logic, 'metrics_logger'):
            bge.logic.metrics_logger = get_metrics_logger()
            print("📊 Metrics logging system initialized")
        
        bge.logic.startup_complete = True
            """)
            print("   Add AFTER metrics initialization:")
            print("""
        # Initialize CASAS motion sensor logging
        if not hasattr(bge.logic, 'casas_motion_logger'):
            try:
                bge.logic.casas_motion_logger = CASASMotionSensorLogger()
                print("🎯 CASAS motion sensor logger initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize CASAS logger: {e}")
            """)
        
        if not task_export_ok:
            print("\n📝 STEP 2: Add CASAS Export on All Tasks Completed")
            print("   File: blender/llm_bge_navigation.py (around line 1126)")
            print("   Find:")
            print("""
            print("🎉 ALL TASKS COMPLETED! Navigation system finished.")
            
            # Print final metrics summary
            if hasattr(bge.logic, 'metrics_logger'):
                bge.logic.metrics_logger._print_task_summary()
            
            return
            """)
            print("   Add BEFORE 'return':")
            print("""
            # Export final CASAS motion sensor data
            if hasattr(bge.logic, 'casas_motion_logger'):
                try:
                    casas_file = bge.logic.casas_motion_logger.export_to_casas_format()
                    print(f"📊 Final CASAS data exported: {casas_file}")
                    print(f"🎯 Motion sensor activations logged for ground truth comparison")
                except Exception as e:
                    print(f"⚠️ Final CASAS export failed: {e}")
            """)
    
    print()
    print("=" * 80)
    print("PRODUCTION DATASET OUTPUT")
    print("=" * 80)
    
    # Check production dataset directory
    vesper_datasets_dir = base_path / "casas_testbed" / "vesper_datasets"
    if vesper_datasets_dir.exists():
        casas_files = list(vesper_datasets_dir.glob("vesper_casas_*.txt"))
        metrics_files = list(vesper_datasets_dir.glob("vesper_metrics_*.json"))
        
        print(f"\n📁 Production output directory: {vesper_datasets_dir}")
        if casas_files or metrics_files:
            print(f"   Existing datasets:")
            if casas_files:
                print(f"     CASAS files: {len(casas_files)}")
            if metrics_files:
                print(f"     Metrics files: {len(metrics_files)}")
        else:
            print(f"   Status: Empty (ready for new datasets)")
    else:
        print(f"\n📁 Production directory will be created: {vesper_datasets_dir}")
    
    print()
    print("=" * 80)
    print("GROUND TRUTH COMPARISON")
    print("=" * 80)
    
    # Check ground truth files in correct location
    casas_gt_dir = base_path / "casas_testbed" / "data" / "casas_ground_truth"
    if casas_gt_dir.exists():
        # Count CSV files (CASAS ground truth format)
        csv_files = list(casas_gt_dir.glob("**/*.csv"))
        txt_files = list(casas_gt_dir.glob("**/*.txt"))
        total_files = len(csv_files) + len(txt_files)
        
        print(f"\n✅ Found {total_files} CASAS ground truth files")
        print(f"   Location: {casas_gt_dir}")
        if csv_files:
            print(f"   CSV files (ground truth): {len(csv_files)}")
            print(f"   Subdirectories:")
            subdirs = set(f.parent.name for f in csv_files if f.parent != casas_gt_dir)
            for subdir in sorted(subdirs):
                count = len(list((casas_gt_dir / subdir).glob("*.csv")))
                print(f"     - {subdir}/: {count} files")
        if txt_files:
            print(f"   TXT files: {len(txt_files)}")
        
        print("\n📊 To compare your generated data with ground truth:")
        print("   python evaluation/vesper_dataset_pipeline.py")
    else:
        print(f"\n⚠️  CASAS ground truth directory not found: {casas_gt_dir}")
    
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n🎮 PRODUCTION WORKFLOW:")
    print("1. Run BGE navigation: python blender/llm_bge_navigation.py")
    print("2. Datasets auto-exported to: casas_testbed/vesper_datasets/")
    print("   - vesper_casas_p01_YYYYMMDD_HHMMSS.txt (motion sensors)")
    print("   - vesper_metrics_p01_YYYYMMDD_HHMMSS.json (VLM logs)")
    print("3. Run comparison: python evaluation/vesper_dataset_pipeline.py")
    print("4. Review results and iterate")
    print()

if __name__ == "__main__":
    main()
