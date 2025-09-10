#!/usr/bin/env python3
"""
VESPER ADL System - Blender Startup Integration

Startup script to initialize VESPER ADL Enhancement within existing Blender BGE setup.
This integrates with your existing blender setup and navigation systems.

Usage:
1. Run this script when starting Blender
2. Integrates with existing setup_bge_logic.py
3. Can be called from existing navigation startup scripts
"""

import bge
import sys
import os
import time
from pathlib import Path

def setup_vesper_adl_startup():
    """
    Setup VESPER ADL system on Blender startup.
    Integrates with existing BGE logic and navigation systems.
    """
    
    print("🚀 VESPER ADL Startup Integration")
    print("=" * 50)
    
    try:
        # Add VESPER ADL system path
        vesper_adl_path = str(Path(__file__).parent)
        if vesper_adl_path not in sys.path:
            sys.path.append(vesper_adl_path)
            print(f"✅ Added VESPER ADL path: {vesper_adl_path}")
        
        # Initialize VESPER ADL integration
        from vesper_adl_blender_integration import initialize_vesper_adl_integration
        
        init_success = initialize_vesper_adl_integration()
        
        if init_success:
            print("✅ VESPER ADL system initialized successfully")
            
            # Add VESPER ADL functions to BGE logic for easy access
            setup_vesper_adl_bge_functions()
            
            # Setup keyboard shortcuts for testing
            setup_vesper_adl_shortcuts()
            
            # Log successful startup
            log_vesper_adl_startup()
            
            print("🎉 VESPER ADL startup complete!")
            return True
        else:
            print("❌ VESPER ADL initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ VESPER ADL startup error: {e}")
        return False

def setup_vesper_adl_bge_functions():
    """Setup VESPER ADL functions in BGE logic for easy access"""
    
    # Import ADL test functions
    from vesper_adl_bge_test import (
        run_vesper_adl_test,
        quick_vesper_adl_test,
        execute_adl_cooking_task,
        execute_adl_medication_task,
        execute_adl_communication_task
    )
    
    # Add functions to BGE logic
    bge.logic.vesper_adl_functions = {
        'run_full_test': run_vesper_adl_test,
        'quick_test': quick_vesper_adl_test,
        'cooking_task': execute_adl_cooking_task,
        'medication_task': execute_adl_medication_task,
        'communication_task': execute_adl_communication_task
    }
    
    # Add direct access functions
    bge.logic.vesper_run_test = run_vesper_adl_test
    bge.logic.vesper_quick_test = quick_vesper_adl_test
    
    print("✅ VESPER ADL functions added to BGE logic")

def setup_vesper_adl_shortcuts():
    """Setup keyboard shortcuts for VESPER ADL testing"""
    
    # Define keyboard shortcuts for ADL tasks
    vesper_shortcuts = {
        'F5': 'quick_vesper_adl_test',  # F5 for quick test
        'F6': 'execute_adl_cooking_task',  # F6 for cooking task
        'F7': 'execute_adl_medication_task',  # F7 for medication task
        'F8': 'execute_adl_communication_task'  # F8 for communication task
    }
    
    # Store shortcuts in BGE logic
    bge.logic.vesper_adl_shortcuts = vesper_shortcuts
    
    print("✅ VESPER ADL keyboard shortcuts configured")
    print("   F5: Quick ADL Test")
    print("   F6: Cooking Task") 
    print("   F7: Medication Task")
    print("   F8: Communication Task")

def log_vesper_adl_startup():
    """Log VESPER ADL startup to evaluation system"""
    
    # Create startup log entry
    startup_log = {
        "timestamp": time.time(),
        "event": "vesper_adl_startup",
        "status": "successful",
        "integration_mode": "blender_bge",
        "system_ready": True
    }
    
    # Add to existing evaluation log if present
    if hasattr(bge.logic, 'evaluation_log'):
        if 'vesper_adl_events' not in bge.logic.evaluation_log:
            bge.logic.evaluation_log['vesper_adl_events'] = []
        bge.logic.evaluation_log['vesper_adl_events'].append(startup_log)
    else:
        # Create new evaluation log
        bge.logic.evaluation_log = {
            'vesper_adl_events': [startup_log]
        }
    
    print("✅ VESPER ADL startup logged to evaluation system")

def handle_vesper_adl_keyboard(key_code):
    """
    Handle VESPER ADL keyboard shortcuts.
    Can be called from existing keyboard handlers.
    """
    
    if not hasattr(bge.logic, 'vesper_adl_shortcuts'):
        return False
    
    # Map key codes to shortcut names
    key_map = {
        bge.events.F5KEY: 'F5',
        bge.events.F6KEY: 'F6', 
        bge.events.F7KEY: 'F7',
        bge.events.F8KEY: 'F8'
    }
    
    if key_code in key_map:
        shortcut_key = key_map[key_code]
        
        if shortcut_key in bge.logic.vesper_adl_shortcuts:
            function_name = bge.logic.vesper_adl_shortcuts[shortcut_key]
            
            # Execute the corresponding function
            if hasattr(bge.logic, 'vesper_adl_functions'):
                functions = bge.logic.vesper_adl_functions
                
                if function_name == 'quick_vesper_adl_test':
                    result = functions['quick_test']()
                    print(f"🧪 Quick ADL Test: {'✅ PASSED' if result else '❌ FAILED'}")
                    return True
                elif function_name == 'execute_adl_cooking_task':
                    result = functions['cooking_task']()
                    print(f"🍳 Cooking Task: {'✅ SUCCESS' if result and result.get('success') else '❌ FAILED'}")
                    return True
                elif function_name == 'execute_adl_medication_task':
                    result = functions['medication_task']()
                    print(f"💊 Medication Task: {'✅ SUCCESS' if result and result.get('success') else '❌ FAILED'}")
                    return True
                elif function_name == 'execute_adl_communication_task':
                    result = functions['communication_task']()
                    print(f"📞 Communication Task: {'✅ SUCCESS' if result and result.get('success') else '❌ FAILED'}")
                    return True
    
    return False

def get_vesper_adl_status_display():
    """Get VESPER ADL status for display in existing UI"""
    
    if hasattr(bge.logic, 'vesper_adl_ready') and bge.logic.vesper_adl_ready:
        status = "🟢 VESPER ADL: READY"
    elif hasattr(bge.logic, 'vesper_adl_system'):
        status = "🟡 VESPER ADL: INITIALIZING"
    else:
        status = "🔴 VESPER ADL: NOT INITIALIZED"
    
    return status

def integrate_with_existing_setup():
    """
    Integrate VESPER ADL with existing setup_bge_logic.py
    This should be called from existing setup scripts.
    """
    
    print("🔗 Integrating VESPER ADL with existing BGE setup...")
    
    # Check if existing setup is present
    scene = bge.logic.getCurrentScene()
    has_existing_actor = 'Actor' in scene.objects
    has_existing_evaluation = hasattr(bge.logic, 'evaluation_log')
    
    integration_info = {
        "existing_actor_found": has_existing_actor,
        "existing_evaluation_system": has_existing_evaluation,
        "vesper_adl_integrated": True
    }
    
    # Enhance existing evaluation system with VESPER ADL
    if has_existing_evaluation:
        print("✅ Enhanced existing evaluation system with VESPER ADL")
    
    # Work with existing actor
    if has_existing_actor:
        print("✅ VESPER ADL will use existing Actor object")
    
    # Store integration info
    bge.logic.vesper_adl_integration_info = integration_info
    
    return integration_info

# Helper functions for existing scripts
def is_vesper_adl_ready():
    """Check if VESPER ADL system is ready"""
    return hasattr(bge.logic, 'vesper_adl_ready') and bge.logic.vesper_adl_ready

def run_vesper_adl_demo():
    """Run VESPER ADL demonstration - can be called from existing demo scripts"""
    
    if not is_vesper_adl_ready():
        print("❌ VESPER ADL not ready - run setup first")
        return False
    
    print("🎬 Running VESPER ADL Demonstration")
    print("-" * 40)
    
    # Run each ADL task as demonstration
    tasks = [
        ("Cooking Task", bge.logic.vesper_adl_functions['cooking_task']),
        ("Medication Task", bge.logic.vesper_adl_functions['medication_task']),
        ("Communication Task", bge.logic.vesper_adl_functions['communication_task'])
    ]
    
    demo_results = []
    
    for task_name, task_function in tasks:
        print(f"\n🎯 Demonstrating: {task_name}")
        
        try:
            result = task_function()
            success = result.get("success", False) if result else False
            
            demo_results.append({
                "task": task_name,
                "success": success,
                "result": result
            })
            
            if success:
                print(f"   ✅ {task_name} completed successfully")
            else:
                print(f"   ❌ {task_name} failed")
                
            # Brief pause between demonstrations
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ {task_name} error: {e}")
            demo_results.append({
                "task": task_name,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    successful_tasks = sum(1 for r in demo_results if r["success"])
    print(f"\n📊 Demonstration Summary: {successful_tasks}/{len(tasks)} tasks successful")
    
    return demo_results

# Main startup execution
def main():
    """Main startup function"""
    
    print("🚀 Starting VESPER ADL Blender Integration...")
    
    # Setup VESPER ADL
    startup_success = setup_vesper_adl_startup()
    
    if startup_success:
        # Integrate with existing setup
        integration_info = integrate_with_existing_setup()
        
        print("\n" + "=" * 50)
        print("🎉 VESPER ADL Integration Complete!")
        print("=" * 50)
        print("Status:", get_vesper_adl_status_display())
        print("Ready for ADL task execution and testing")
        print("\nKeyboard Shortcuts:")
        print("  F5: Quick ADL Test")
        print("  F6: Cooking Task Demo")
        print("  F7: Medication Task Demo") 
        print("  F8: Communication Task Demo")
        print("\nTo run full test: bge.logic.vesper_run_test()")
        print("To run demo: run_vesper_adl_demo()")
        
        return True
    else:
        print("❌ VESPER ADL startup failed")
        return False

# Auto-initialize when imported in BGE
if 'bge' in globals():
    main()

# Make functions available for import
__all__ = [
    'setup_vesper_adl_startup',
    'handle_vesper_adl_keyboard', 
    'get_vesper_adl_status_display',
    'integrate_with_existing_setup',
    'is_vesper_adl_ready',
    'run_vesper_adl_demo',
    'main'
]
