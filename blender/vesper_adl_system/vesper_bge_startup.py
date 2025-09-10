#!/usr/bin/env python3
"""
VESPER ADL Enhancement - Blender Startup Integration

This script automatically initializes the VESPER ADL Enhancement system
when Blender starts with BGE enabled.

Installation:
1. Copy this file to Blender's scripts/startup directory
2. Open Blender with house layout
3. VESPER system will be automatically available

Usage:
- Access via bge.logic.vesper_adl_system
- Run bge.logic.vesper_start_adl_session(tasks) to execute ADL tasks
- Check bge.logic.vesper_system_status for current status
"""

import bge
import mathutils
import time
import sys
import os

def initialize_vesper_adl_system():
    """Initialize VESPER ADL Enhancement system in Blender BGE"""
    
    print("🚀 Initializing VESPER ADL Enhancement System in Blender...")
    
    try:
        # Add VESPER implementation path
        script_dir = os.path.dirname(__file__)
        vesper_path = os.path.join(script_dir, '..', '..', 'implementation')
        vesper_path = os.path.abspath(vesper_path)
        
        if vesper_path not in sys.path:
            sys.path.insert(0, vesper_path)
        
        # Import VESPER components
        from vesper_adl_integrated_system import VESPERADLIntegratedSystem, SystemConfiguration, SystemMode
        from object_interaction_system import CASASObjectManager
        from adl_task_execution_system import ADLTaskExecutor
        from vlm_intelligence_enhancement import IntelligentTaskPlanner
        
        print("✅ VESPER modules imported successfully")
        
        # Create system configuration for Blender environment
        config = SystemConfiguration(
            mode=SystemMode.DEMONSTRATION,
            vlm_model="llava:7b",
            evaluation_dataset="blender_demo",
            target_similarity=0.70,
            max_execution_time=300.0,
            safety_mode=True,
            logging_level="INFO"
        )
        
        # Initialize VESPER system
        vesper_system = VESPERADLIntegratedSystem(config)
        
        # Custom BGE initialization
        init_success = initialize_bge_specific_components(vesper_system)
        
        if init_success:
            # Store in BGE logic for global access
            bge.logic.vesper_adl_system = vesper_system
            bge.logic.vesper_system_status = "ready"
            
            # Add convenience functions to BGE logic
            bge.logic.vesper_start_adl_session = lambda tasks: start_adl_session_wrapper(vesper_system, tasks)
            bge.logic.vesper_get_status = lambda: get_system_status_wrapper(vesper_system)
            bge.logic.vesper_execute_task = lambda task_desc: execute_single_task_wrapper(vesper_system, task_desc)
            
            print("🎉 VESPER ADL Enhancement System ready!")
            print("📋 Available functions:")
            print("  - bge.logic.vesper_start_adl_session(tasks)")
            print("  - bge.logic.vesper_get_status()")
            print("  - bge.logic.vesper_execute_task(task_description)")
            
            return True
        else:
            print("❌ VESPER system initialization failed")
            bge.logic.vesper_system_status = "error"
            return False
            
    except Exception as e:
        print(f"❌ VESPER initialization error: {e}")
        bge.logic.vesper_system_status = "error"
        return False

def initialize_bge_specific_components(vesper_system):
    """Initialize BGE-specific components"""
    
    try:
        # Initialize BGE integration
        vesper_system._initialize_bge_integration()
        
        # Setup scene monitoring
        setup_scene_monitoring()
        
        # Initialize object tracking
        setup_object_tracking()
        
        # Setup screenshot system
        setup_screenshot_system()
        
        print("✅ BGE-specific components initialized")
        return True
        
    except Exception as e:
        print(f"❌ BGE component initialization failed: {e}")
        return False

def setup_scene_monitoring():
    """Setup scene monitoring for VESPER system"""
    
    scene = bge.logic.getCurrentScene()
    
    # Store scene reference
    bge.logic.vesper_scene = scene
    
    # Find and track Actor object
    actor = scene.objects.get("Actor")
    if actor:
        bge.logic.vesper_actor = actor
        print(f"✅ Actor found at position: {actor.worldPosition}")
    else:
        print("⚠️  Actor object not found in scene")
    
    # Count available objects
    bge.logic.vesper_scene_objects = list(scene.objects)
    print(f"✅ Scene monitoring: {len(scene.objects)} objects tracked")

def setup_object_tracking():
    """Setup CASAS object tracking in BGE"""
    
    scene = bge.logic.getCurrentScene()
    
    # CASAS object names to look for
    casas_object_names = ["oatmeal", "raisins", "brown_sugar", "bowl", 
                         "measuring_spoon", "medicine", "pot", "phone_book"]
    
    # Track which CASAS objects are present in scene
    bge.logic.vesper_casas_objects_in_scene = {}
    
    for obj_name in casas_object_names:
        scene_obj = scene.objects.get(obj_name)
        if scene_obj:
            bge.logic.vesper_casas_objects_in_scene[obj_name] = scene_obj
            print(f"✅ CASAS object found: {obj_name}")
        else:
            print(f"⚠️  CASAS object not in scene: {obj_name}")
    
    print(f"✅ Object tracking: {len(bge.logic.vesper_casas_objects_in_scene)} CASAS objects available")

def setup_screenshot_system():
    """Setup screenshot capture system for VLM"""
    
    # Initialize screenshot counter and path
    bge.logic.vesper_screenshot_counter = 0
    bge.logic.vesper_screenshot_path = "captures/"
    
    # Create captures directory if it doesn't exist
    import os
    os.makedirs(bge.logic.vesper_screenshot_path, exist_ok=True)
    
    print("✅ Screenshot system initialized")

def capture_screenshot_for_vlm():
    """Capture screenshot for VLM analysis"""
    
    try:
        bge.logic.vesper_screenshot_counter += 1
        screenshot_filename = f"vesper_screenshot_{bge.logic.vesper_screenshot_counter:04d}.png"
        screenshot_path = os.path.join(bge.logic.vesper_screenshot_path, screenshot_filename)
        
        # Capture screenshot using BGE
        bge.render.makeScreenshot(screenshot_path)
        
        # Store latest screenshot path
        bge.logic.vesper_latest_screenshot = screenshot_path
        
        print(f"📸 Screenshot captured: {screenshot_path}")
        return screenshot_path
        
    except Exception as e:
        print(f"❌ Screenshot capture failed: {e}")
        return None

# Wrapper functions for easy BGE access
def start_adl_session_wrapper(vesper_system, tasks):
    """Wrapper for starting ADL session from BGE"""
    
    print(f"🎬 Starting VESPER ADL session with {len(tasks)} tasks...")
    
    # Capture screenshot before starting
    screenshot_path = capture_screenshot_for_vlm()
    
    # Execute session
    results = vesper_system.execute_adl_session(tasks, evaluation_mode=True)
    
    # Store results in BGE logic
    bge.logic.vesper_last_session_results = results
    
    # Display summary
    if results.get("overall_performance"):
        perf = results["overall_performance"]
        print(f"📊 Session completed:")
        print(f"  - Task completion: {perf['task_completion_rate']:.1%}")
        print(f"  - Execution efficiency: {perf['execution_efficiency']:.2f}")
        
        if "casas_compatibility" in results:
            casas = results["casas_compatibility"]
            print(f"  - CASAS similarity: {casas['overall_similarity']:.1%}")
    
    return results

def get_system_status_wrapper(vesper_system):
    """Wrapper for getting system status from BGE"""
    
    status = vesper_system.get_system_status_report()
    
    # Add BGE-specific status
    status["bge_info"] = {
        "scene_name": bge.logic.getCurrentScene().name,
        "actor_available": hasattr(bge.logic, 'vesper_actor'),
        "casas_objects_count": len(getattr(bge.logic, 'vesper_casas_objects_in_scene', {})),
        "screenshots_captured": getattr(bge.logic, 'vesper_screenshot_counter', 0)
    }
    
    return status

def execute_single_task_wrapper(vesper_system, task_description):
    """Wrapper for executing single task from BGE"""
    
    print(f"🎯 Executing single task: {task_description}")
    
    # Execute as single-task session
    results = start_adl_session_wrapper(vesper_system, [task_description])
    
    if results.get("task_results"):
        task_result = results["task_results"][0]
        if task_result["success"]:
            print(f"✅ Task completed successfully in {task_result['duration']:.1f}s")
        else:
            print(f"❌ Task failed: {task_result.get('error', 'Unknown error')}")
    
    return results

# BGE Logic Functions - Available globally after initialization
def vesper_demo_cooking_task():
    """Demo function: Execute cooking task"""
    if hasattr(bge.logic, 'vesper_start_adl_session'):
        return bge.logic.vesper_start_adl_session(["Make oatmeal with raisins and brown sugar"])
    else:
        print("❌ VESPER system not initialized")

def vesper_demo_medication_task():
    """Demo function: Execute medication task"""
    if hasattr(bge.logic, 'vesper_start_adl_session'):
        return bge.logic.vesper_start_adl_session(["Take morning medication"])
    else:
        print("❌ VESPER system not initialized")

def vesper_demo_communication_task():
    """Demo function: Execute communication task"""
    if hasattr(bge.logic, 'vesper_start_adl_session'):
        return bge.logic.vesper_start_adl_session(["Make a phone call using phone book"])
    else:
        print("❌ VESPER system not initialized")

def vesper_demo_complete_session():
    """Demo function: Execute complete ADL session"""
    if hasattr(bge.logic, 'vesper_start_adl_session'):
        tasks = [
            "Make oatmeal with raisins and brown sugar",
            "Take morning medication", 
            "Make a phone call using phone book"
        ]
        return bge.logic.vesper_start_adl_session(tasks)
    else:
        print("❌ VESPER system not initialized")

# Add demo functions to BGE logic
def add_demo_functions():
    """Add demo functions to BGE logic for easy access"""
    
    bge.logic.vesper_demo_cooking = vesper_demo_cooking_task
    bge.logic.vesper_demo_medication = vesper_demo_medication_task
    bge.logic.vesper_demo_communication = vesper_demo_communication_task
    bge.logic.vesper_demo_complete = vesper_demo_complete_session
    
    print("✅ Demo functions added to bge.logic")

# Auto-initialization when script loads
def auto_initialize():
    """Auto-initialize VESPER system when Blender starts"""
    
    try:
        # Only initialize if BGE is available and not already initialized
        if not hasattr(bge.logic, 'vesper_adl_system'):
            success = initialize_vesper_adl_system()
            
            if success:
                add_demo_functions()
                print("\n🎉 VESPER ADL Enhancement System is ready!")
                print("📋 Try these demo commands:")
                print("  bge.logic.vesper_demo_cooking()")
                print("  bge.logic.vesper_demo_medication()")
                print("  bge.logic.vesper_demo_communication()")
                print("  bge.logic.vesper_demo_complete()")
            
    except Exception as e:
        print(f"❌ Auto-initialization failed: {e}")

# Run auto-initialization
if __name__ == "__main__":
    auto_initialize()
else:
    # Also run when imported
    auto_initialize()
