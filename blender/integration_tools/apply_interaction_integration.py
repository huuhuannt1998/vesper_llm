#!/usr/bin/env python3
"""
Automatic Integration Script for VESPER Interaction System
Adds all 6 integration points to llm_bge_navigation.py
"""

import os
import sys
import re

def apply_integration():
    """Apply all integration points to llm_bge_navigation.py"""
    
    # Path to the main navigation file
    nav_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "llm_bge_navigation.py")
    
    if not os.path.exists(nav_file):
        print(f"❌ File not found: {nav_file}")
        return False
    
    print(f"📄 Reading {nav_file}...")
    
    # Read the file with UTF-8 encoding, ignoring errors
    try:
        with open(nav_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    original_content = content
    modifications_made = []
    
    # ========== INTEGRATION POINT 1: Initialize System ==========
    marker1 = "# Initialize CASAS motion sensor logging"
    if marker1 in content and "# Initialize VESPER Interaction System" not in content:
        print("✅ Adding Integration Point 1: Initialize Interaction System")
        
        init_code = """
        # Initialize VESPER Interaction System (Item Sensors + Virtual Devices + Time)
        if INTERACTION_SYSTEM_AVAILABLE and not hasattr(bge.logic, 'interaction_system'):
            try:
                initialize_interaction_system_for_bge()
                print("✅ VESPER Interaction System initialized (Item Sensors + Devices + Time)")
            except Exception as e:
                print(f"⚠️ Failed to initialize interaction system: {e}")
"""
        
        # Find the CASAS logger section and add after it
        casas_section_end = content.find('print(f"⚠️ Failed to initialize CASAS logger: {e}")')
        if casas_section_end != -1:
            # Find the end of that line
            line_end = content.find('\n', casas_section_end)
            if line_end != -1:
                content = content[:line_end+1] + init_code + content[line_end+1:]
                modifications_made.append("✅ Point 1: Initialize system")
    
    # ========== INTEGRATION POINT 2: Start Task Tracking ==========
    marker2 = "bge.logic.metrics_logger.start_task(current_task, bge.logic.current_task_index)"
    if marker2 in content and "interaction_system.start_task" not in content:
        print("✅ Adding Integration Point 2: Start Task Tracking")
        
        start_task_code = """
                # Start interaction tracking for this task
                if INTERACTION_SYSTEM_AVAILABLE:
                    try:
                        interaction_system = get_interaction_system()
                        if interaction_system:
                            interaction_system.start_task_with_interactions(
                                current_task,
                                bge.logic.current_task_index
                            )
                    except Exception as e:
                        print(f"⚠️ Failed to start interaction tracking: {e}")
"""
        
        # Find the start_task line and add after it
        start_task_pos = content.find(marker2)
        if start_task_pos != -1:
            line_end = content.find('\n', start_task_pos)
            if line_end != -1:
                content = content[:line_end+1] + start_task_code + content[line_end+1:]
                modifications_made.append("✅ Point 2: Start task tracking")
    
    # ========== INTEGRATION POINT 3: Update Interaction State ==========
    marker3 = "# Execute navigation step for current task"
    if marker3 in content and "update_interaction_state" not in content:
        print("✅ Adding Integration Point 3: Update Interaction State")
        
        update_code = """
        # Update interaction state (check for nearby objects)
        if INTERACTION_SYSTEM_AVAILABLE:
            try:
                scene = bge.logic.getCurrentScene()
                actor = scene.objects.get("Actor")
                if actor:
                    interaction_system = get_interaction_system()
                    if interaction_system:
                        interaction_system.update_interaction_state(actor)
            except Exception as e:
                print(f"⚠️ Interaction state update failed: {e}")
        
"""
        
        # Find the marker and add before it
        marker_pos = content.find(marker3)
        if marker_pos != -1:
            content = content[:marker_pos] + update_code + content[marker_pos:]
            modifications_made.append("✅ Point 3: Update interaction state")
    
    # ========== INTEGRATION POINT 4: Complete Task (Success) ==========
    marker4_success = 'bge.logic.metrics_logger.complete_task(\n                        success=True,'
    if marker4_success in content:
        # Find all occurrences of successful task completion
        success_positions = [m.start() for m in re.finditer(re.escape(marker4_success), content)]
        
        if success_positions and "interaction_system.complete_task(success=True)" not in content:
            print(f"✅ Adding Integration Point 4: Complete Task (Success) - {len(success_positions)} locations")
            
            complete_task_code = """
                # Complete interaction tracking
                if INTERACTION_SYSTEM_AVAILABLE:
                    try:
                        interaction_system = get_interaction_system()
                        if interaction_system:
                            interaction_system.complete_task(success=True)
                    except Exception as e:
                        print(f"⚠️ Failed to complete interaction tracking: {e}")
                
"""
            
            # Add after each successful completion (work backwards to preserve positions)
            for pos in reversed(success_positions):
                # Find the end of the complete_task call
                closing_pos = content.find(')', pos)
                if closing_pos != -1:
                    line_end = content.find('\n', closing_pos)
                    if line_end != -1:
                        content = content[:line_end+1] + complete_task_code + content[line_end+1:]
            
            modifications_made.append(f"✅ Point 4: Complete task (success) - {len(success_positions)} locations")
    
    # ========== INTEGRATION POINT 5: Complete Task (Failure) ==========
    marker5_fail = 'bge.logic.metrics_logger.complete_task(\n                    success=False,'
    if marker5_fail in content:
        # Find all occurrences of failed task completion
        fail_positions = [m.start() for m in re.finditer(re.escape(marker5_fail), content)]
        
        if fail_positions and "interaction_system.complete_task(success=False)" not in content:
            print(f"✅ Adding Integration Point 5: Complete Task (Failure) - {len(fail_positions)} locations")
            
            fail_task_code = """
                # Complete interaction tracking (task failed)
                if INTERACTION_SYSTEM_AVAILABLE:
                    try:
                        interaction_system = get_interaction_system()
                        if interaction_system:
                            interaction_system.complete_task(success=False)
                    except Exception as e:
                        print(f"⚠️ Failed to complete interaction tracking: {e}")
                
"""
            
            # Add after each failed completion (work backwards)
            for pos in reversed(fail_positions):
                # Find the end of the complete_task call
                closing_pos = content.find(')', pos)
                if closing_pos != -1:
                    line_end = content.find('\n', closing_pos)
                    if line_end != -1:
                        content = content[:line_end+1] + fail_task_code + content[line_end+1:]
            
            modifications_made.append(f"✅ Point 5: Complete task (failure) - {len(fail_positions)} locations")
    
    # ========== INTEGRATION POINT 6: Export All Data ==========
    marker6 = "# Print final metrics summary and export datasets"
    if marker6 in content and "interaction_system.export_all_data" not in content:
        print("✅ Adding Integration Point 6: Export All Data")
        
        export_code = """
            # Export interaction system data (item sensors, devices, time logs)
            if INTERACTION_SYSTEM_AVAILABLE:
                try:
                    interaction_system = get_interaction_system()
                    if interaction_system:
                        print("📊 Exporting interaction system data...")
                        interaction_system.export_all_data()
                except Exception as e:
                    print(f"⚠️ Failed to export interaction data: {e}")
            
"""
        
        # Find the marker and add after it
        marker_pos = content.find(marker6)
        if marker_pos != -1:
            line_end = content.find('\n', marker_pos)
            if line_end != -1:
                content = content[:line_end+1] + export_code + content[line_end+1:]
                modifications_made.append("✅ Point 6: Export all data")
    
    # Check if any modifications were made
    if content == original_content:
        print("\n⚠️ No modifications made - integration may already be complete or markers not found")
        return False
    
    # Backup original file
    backup_file = nav_file + ".backup"
    try:
        with open(backup_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(original_content)
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️ Could not create backup: {e}")
    
    # Write modified content
    try:
        with open(nav_file, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        print(f"\n✅ Successfully updated {nav_file}")
        print(f"\n📋 Modifications Applied:")
        for mod in modifications_made:
            print(f"   {mod}")
        
        print(f"\n🎉 Integration Complete! {len(modifications_made)} integration points added.")
        print(f"\n📝 Summary:")
        print(f"   - Interaction system will initialize on startup")
        print(f"   - Tasks will track item sensor interactions")
        print(f"   - Virtual devices will auto-control")
        print(f"   - Time acceleration will activate")
        print(f"   - All data exports to vesper_datasets/")
        
        return True
        
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        # Restore backup
        if os.path.exists(backup_file):
            try:
                with open(nav_file, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(original_content)
                print("♻️ Restored from backup")
            except:
                pass
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🔧 VESPER Interaction System - Automatic Integration")
    print("=" * 70)
    print("\nThis will add 6 integration points to llm_bge_navigation.py:")
    print("  1. Initialize interaction system")
    print("  2. Start task tracking")
    print("  3. Update interaction state")
    print("  4. Complete task (success)")
    print("  5. Complete task (failure)")
    print("  6. Export all data")
    print("\n" + "=" * 70)
    
    success = apply_integration()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ INTEGRATION SUCCESSFUL!")
        print("=" * 70)
        print("\n🚀 Next Steps:")
        print("   1. Run your BGE navigation")
        print("   2. Complete some tasks")
        print("   3. Check vesper_datasets/ for output files:")
        print("      - item_sensor_log_*.txt (CASAS format)")
        print("      - item_interactions_*.json (detailed)")
        print("      - device_log_*.json (SmartThings)")
        print("      - virtual_time_log.json (time tracking)")
        print("\n" + "=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("⚠️ INTEGRATION INCOMPLETE")
        print("=" * 70)
        print("\nPlease check:")
        print("   - File permissions")
        print("   - File encoding")
        print("   - Integration may already be done")
        print("\n" + "=" * 70)
        sys.exit(1)
