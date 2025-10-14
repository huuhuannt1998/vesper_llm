"""
Auto-Integration Script for VESPER Interaction System
This script will help integrate the interaction system into llm_bge_navigation.py
"""

import os
import re

def show_integration_instructions():
    """Display step-by-step integration instructions"""
    
    print("="*80)
    print("VESPER INTERACTION SYSTEM - INTEGRATION GUIDE")
    print("="*80)
    print()
    print("This guide shows you exactly where to add code in llm_bge_navigation.py")
    print()
    
    print("📝 STEP 1: ADD IMPORT (After line ~105)")
    print("-" * 80)
    print("""
# VESPER Interaction System (NEW)
try:
    from vesper_interaction_integration import (
        get_interaction_system,
        initialize_interaction_system_for_bge
    )
    INTERACTION_SYSTEM_AVAILABLE = True
    print("✅ VESPER Interaction System available")
except ImportError as e:
    INTERACTION_SYSTEM_AVAILABLE = False
    print(f"⚠️ Interaction system not available: {e}")
""")
    print()
    
    print("📝 STEP 2: INITIALIZE IN main() (After CASAS logger init, around line ~1234)")
    print("-" * 80)
    print("""
        # Initialize VESPER Interaction System (NEW)
        if INTERACTION_SYSTEM_AVAILABLE and not hasattr(bge.logic, 'interaction_system'):
            try:
                if initialize_interaction_system_for_bge():
                    print("✅ VESPER Interaction System integrated with BGE")
            except Exception as e:
                print(f"⚠️ Failed to initialize interaction system: {e}")
""")
    print()
    
    print("📝 STEP 3: START TASK (In run_continuous_navigation, after task logging)")
    print("-" * 80)
    print("""
        # Start task with interaction system (NEW)
        if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            if actor and not hasattr(bge.logic, 'task_interaction_started'):
                actor_pos = [actor.worldPosition.x, actor.worldPosition.y]
                try:
                    task_context = bge.logic.interaction_system.start_task_with_interactions(
                        current_task, actor_pos
                    )
                    bge.logic.task_interaction_started = True
                except Exception as e:
                    print(f"⚠️ Task interaction start failed: {e}")
""")
    print()
    
    print("📝 STEP 4: UPDATE INTERACTIONS (During navigation loop)")
    print("-" * 80)
    print("""
        # Update interaction state (NEW)
        if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
            actor = scene.objects.get("Actor")
            if actor:
                actor_pos = [actor.worldPosition.x, actor.worldPosition.y]
                try:
                    events = bge.logic.interaction_system.update_interaction_state(
                        actor_pos, current_task
                    )
                    for event in events:
                        print(f"🤝 {event['type']}: {event['object']}")
                except Exception as e:
                    print(f"⚠️ Interaction update failed: {e}")
""")
    print()
    
    print("📝 STEP 5: COMPLETE TASK (When task_complete == True)")
    print("-" * 80)
    print("""
            # Complete with interaction system (NEW)
            if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
                try:
                    bge.logic.interaction_system.complete_task(current_task, success=True)
                    bge.logic.task_interaction_started = False
                except Exception as e:
                    print(f"⚠️ Interaction completion failed: {e}")
""")
    print()
    
    print("📝 STEP 6: EXPORT DATA (When all tasks complete)")
    print("-" * 80)
    print("""
            # Export interaction data (NEW)
            if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
                try:
                    bge.logic.interaction_system.print_session_summary()
                    bge.logic.interaction_system.export_all_data()
                except Exception as e:
                    print(f"⚠️ Export failed: {e}")
""")
    print()
    
    print("="*80)
    print("✅ INTEGRATION COMPLETE")
    print("="*80)
    print()
    print("📊 BENEFITS:")
    print("  • Automatic item sensor tracking (CASAS format)")
    print("  • Virtual device control (SmartThings-style)")
    print("  • Time acceleration for long tasks")
    print("  • Complete interaction logging")
    print()
    print("📁 OUTPUT FILES (in vesper_datasets/):")
    print("  • item_sensor_log_*.txt (CASAS format)")
    print("  • item_interactions_*.json (detailed)")
    print("  • device_log_*.json")
    print("  • virtual_time_log.json")
    print()
    print("🧪 TEST:")
    print("  1. Add the code snippets above to llm_bge_navigation.py")
    print("  2. Run your navigation in BGE")
    print("  3. Check vesper_datasets/ folder for output files")
    print()
    print("💡 TIP: See INTEGRATION_PATCHES.py for complete code with comments")
    print("="*80)


def create_minimal_example():
    """Create a minimal working example"""
    
    example_code = '''
# ============================================================================
# MINIMAL INTEGRATION EXAMPLE
# ============================================================================
# Add these 3 sections to llm_bge_navigation.py

# SECTION 1: Import (top of file, after other imports)
from vesper_interaction_integration import initialize_interaction_system_for_bge
INTERACTION_SYSTEM_AVAILABLE = True

# SECTION 2: Initialize (in main function)
if INTERACTION_SYSTEM_AVAILABLE:
    initialize_interaction_system_for_bge()

# SECTION 3: Export (when all tasks complete)
if hasattr(bge.logic, 'interaction_system'):
    bge.logic.interaction_system.export_all_data()

# That's it! The system works automatically from there.
'''
    
    output_file = os.path.join(
        os.path.dirname(__file__),
        "MINIMAL_INTEGRATION_EXAMPLE.txt"
    )
    
    with open(output_file, 'w') as f:
        f.write(example_code)
    
    print(f"✅ Created: {output_file}")
    return output_file


def check_current_integration():
    """Check if integration is already present"""
    
    nav_file = os.path.join(
        os.path.dirname(__file__),
        "llm_bge_navigation.py"
    )
    
    if not os.path.exists(nav_file):
        print(f"⚠️  Navigation file not found: {nav_file}")
        return False
    
    with open(nav_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "Import": "vesper_interaction_integration" in content,
        "Initialize": "initialize_interaction_system_for_bge" in content,
        "System Available": "INTERACTION_SYSTEM_AVAILABLE" in content,
    }
    
    print("\n" + "="*60)
    print("INTEGRATION STATUS CHECK")
    print("="*60)
    
    for check_name, result in checks.items():
        status = "✅ FOUND" if result else "❌ MISSING"
        print(f"{status} - {check_name}")
    
    print("="*60)
    
    all_present = all(checks.values())
    
    if all_present:
        print("✅ Interaction system appears to be integrated!")
        print("   Run BGE navigation to test it.")
    else:
        print("⚠️  Integration incomplete - follow steps above")
    
    print()
    return all_present


if __name__ == "__main__":
    print("\n")
    print("🚀 VESPER INTERACTION SYSTEM - AUTO-INTEGRATION HELPER")
    print()
    
    # Check current status
    is_integrated = check_current_integration()
    
    if not is_integrated:
        # Show instructions
        show_integration_instructions()
        
        # Create minimal example
        create_minimal_example()
    else:
        print("✅ System is already integrated!")
        print()
        print("📝 To use the interaction features:")
        print("   1. Run your BGE navigation")
        print("   2. Check vesper_datasets/ for output files")
        print("   3. Review INTERACTION_SYSTEM_README.md for details")
        print()
    
    print("📚 Documentation:")
    print("   • INTERACTION_SYSTEM_README.md - Full documentation")
    print("   • INTEGRATION_PATCHES.py - Detailed code snippets")
    print("   • QUICK_REFERENCE.md - Visual guide")
    print("   • demo_interaction_system.py - Standalone demo")
    print()
