#!/usr/bin/env python3
"""
VESPER ADL System - Blender Integration

Integration of VESPER ADL Enhancement with existing BGE navigation system.
This extends the current llm_bge_navigation.py with full ADL capabilities.

Location: blender/vesper_adl_system/
Integration with: ../llm_bge_navigation.py, ../enhanced_llm_bge_navigation.py
"""

import bge
import mathutils
import time
import json
import sys
import os
from typing import Dict, List, Any, Optional

# Import existing BGE navigation components
try:
    sys.path.append('..')  # Access parent blender directory
    from llm_bge_navigation import *  # Import existing navigation functions
    print("✅ Existing BGE navigation system imported")
except ImportError as e:
    print(f"⚠️  Could not import existing navigation: {e}")

# Import VESPER ADL components
from object_interaction_system import CASASObjectManager, VLMObjectInteraction
from adl_task_execution_system import ADLTaskExecutor, CASASTaskLibrary, TaskStatus
from vlm_intelligence_enhancement import IntelligentTaskPlanner, AdvancedVLMProcessor
from vesper_adl_integrated_system import VESPERADLIntegratedSystem, SystemConfiguration, SystemMode

class VESPERADLBlenderIntegration:
    """
    Integrates VESPER ADL Enhancement with existing Blender BGE navigation system.
    Extends current VLM navigation with full ADL task execution capabilities.
    """
    
    def __init__(self):
        # Initialize VESPER ADL components
        self.config = SystemConfiguration(
            mode=SystemMode.DEMONSTRATION,
            vlm_model="llava:7b",
            evaluation_dataset="blender_live",
            target_similarity=0.70,
            max_execution_time=300.0,
            safety_mode=True,
            logging_level="INFO"
        )
        
        self.vesper_system = VESPERADLIntegratedSystem(self.config)
        self.system_ready = False
        
        # Integration with existing BGE navigation
        self.navigation_integration = True
        self.screenshot_integration = True
        
    def initialize_adl_system(self) -> bool:
        """Initialize VESPER ADL system within existing BGE framework"""
        
        print("🚀 Initializing VESPER ADL System in Blender...")
        
        try:
            # Initialize the integrated system
            init_success = self.vesper_system.initialize_system()
            
            if init_success:
                # Integrate with existing BGE logic
                self._integrate_with_existing_bge()
                
                # Setup ADL-specific scene monitoring
                self._setup_adl_scene_monitoring()
                
                # Integrate with existing screenshot system
                self._integrate_screenshot_system()
                
                # Setup CASAS object detection
                self._setup_casas_object_detection()
                
                self.system_ready = True
                print("✅ VESPER ADL System initialized successfully")
                return True
            else:
                print("❌ VESPER ADL System initialization failed")
                return False
                
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
    
    def _integrate_with_existing_bge(self):
        """Integrate with existing BGE navigation system"""
        
        # Store VESPER system in BGE logic alongside existing systems
        bge.logic.vesper_adl_system = self.vesper_system
        bge.logic.vesper_adl_integration = self
        
        # Extend existing evaluation log if present
        if hasattr(bge.logic, 'evaluation_log'):
            if 'vesper_adl_events' not in bge.logic.evaluation_log:
                bge.logic.evaluation_log['vesper_adl_events'] = []
        
        # Integrate with existing actor tracking
        scene = bge.logic.getCurrentScene()
        if 'Actor' in scene.objects:
            bge.logic.vesper_actor = scene.objects['Actor']
            print("✅ Integrated with existing Actor object")
    
    def _setup_adl_scene_monitoring(self):
        """Setup ADL-specific scene monitoring"""
        
        scene = bge.logic.getCurrentScene()
        
        # Monitor CASAS objects in the scene
        casas_objects = ["oatmeal", "raisins", "brown_sugar", "bowl", 
                        "measuring_spoon", "medicine", "pot", "phone_book"]
        
        bge.logic.vesper_scene_objects = {}
        for obj_name in casas_objects:
            if obj_name in scene.objects:
                bge.logic.vesper_scene_objects[obj_name] = scene.objects[obj_name]
                print(f"✅ Found CASAS object: {obj_name}")
        
        print(f"✅ ADL scene monitoring: {len(bge.logic.vesper_scene_objects)} CASAS objects")
    
    def _integrate_screenshot_system(self):
        """Integrate with existing screenshot capture system"""
        
        # Use existing screenshot system if available
        if hasattr(bge.logic, 'latest_screenshot'):
            bge.logic.vesper_screenshot_path = bge.logic.latest_screenshot
            print("✅ Using existing screenshot system")
        else:
            # Setup new screenshot system
            bge.logic.vesper_screenshot_counter = 0
            print("✅ Setup new screenshot system for VESPER ADL")
    
    def _setup_casas_object_detection(self):
        """Setup CASAS object detection in current scene"""
        
        scene = bge.logic.getCurrentScene()
        
        # Initialize object manager with scene integration
        obj_manager = self.vesper_system.object_manager
        
        # Update object positions based on actual scene objects
        for sensor_id, obj_data in obj_manager.casas_objects.items():
            obj_name = obj_data["name"]
            if obj_name in scene.objects:
                scene_obj = scene.objects[obj_name]
                obj_data["scene_object"] = scene_obj
                obj_data["current_position"] = tuple(scene_obj.worldPosition)
                print(f"✅ CASAS object {obj_name} linked to scene object")
    
    def execute_adl_navigation_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute ADL task with integrated navigation.
        Combines existing navigation with ADL task execution.
        """
        
        if not self.system_ready:
            return {"success": False, "error": "System not ready"}
        
        print(f"🎯 Executing ADL navigation task: {task_description}")
        
        try:
            # Capture current screenshot using existing system
            screenshot_path = self._capture_screenshot()
            
            # Get current actor position
            actor_position = self._get_actor_position()
            
            # Use existing navigation for movement, VESPER for task execution
            task_result = self._execute_adl_task_with_navigation(
                task_description, 
                actor_position, 
                screenshot_path
            )
            
            # Log to existing evaluation system
            self._log_to_existing_evaluation(task_result)
            
            return task_result
            
        except Exception as e:
            print(f"❌ ADL navigation task failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_adl_task_with_navigation(self, task_description: str, 
                                        actor_position: tuple, 
                                        screenshot_path: str) -> Dict[str, Any]:
        """Execute ADL task with integrated navigation support"""
        
        # Start single-task session
        session_result = self.vesper_system.execute_adl_session(
            [task_description], 
            evaluation_mode=True
        )
        
        if session_result["task_results"]:
            task_result = session_result["task_results"][0]
            
            # Add navigation integration info
            task_result["navigation_integration"] = {
                "actor_position": actor_position,
                "screenshot_used": screenshot_path is not None,
                "scene_objects_available": len(bge.logic.vesper_scene_objects),
                "existing_navigation_active": True
            }
            
            return task_result
        else:
            return {"success": False, "error": "No task results"}
    
    def _capture_screenshot(self) -> Optional[str]:
        """Capture screenshot using existing or new system"""
        
        try:
            # Use existing screenshot capture if available
            if hasattr(bge.logic, 'capture_screenshot'):
                return bge.logic.capture_screenshot()
            else:
                # Use basic BGE screenshot
                timestamp = int(time.time())
                screenshot_path = f"captures/vesper_adl_{timestamp}.png"
                bge.render.makeScreenshot(screenshot_path)
                bge.logic.vesper_latest_screenshot = screenshot_path
                return screenshot_path
                
        except Exception as e:
            print(f"⚠️  Screenshot capture failed: {e}")
            return None
    
    def _get_actor_position(self) -> tuple:
        """Get actor position from existing navigation system"""
        
        if hasattr(bge.logic, 'vesper_actor'):
            return tuple(bge.logic.vesper_actor.worldPosition)
        else:
            scene = bge.logic.getCurrentScene()
            if 'Actor' in scene.objects:
                return tuple(scene.objects['Actor'].worldPosition)
            else:
                return (0.0, 0.0, 0.0)
    
    def _log_to_existing_evaluation(self, task_result: Dict[str, Any]):
        """Log ADL task result to existing evaluation system"""
        
        if hasattr(bge.logic, 'evaluation_log'):
            adl_event = {
                "timestamp": time.time(),
                "event_type": "vesper_adl_task",
                "task_description": task_result.get("description", "unknown"),
                "success": task_result.get("success", False),
                "duration": task_result.get("duration", 0),
                "steps_completed": task_result.get("steps_completed", 0),
                "casas_compatibility": True
            }
            
            bge.logic.evaluation_log['vesper_adl_events'].append(adl_event)
            print("✅ ADL task logged to existing evaluation system")

# Global integration functions for existing BGE navigation system

def initialize_vesper_adl_integration():
    """Initialize VESPER ADL integration - call from existing navigation system"""
    
    if not hasattr(bge.logic, 'vesper_adl_integration'):
        integration = VESPERADLBlenderIntegration()
        success = integration.initialize_adl_system()
        
        if success:
            # Add ADL functions to existing BGE logic
            bge.logic.execute_adl_task = lambda task: integration.execute_adl_navigation_task(task)
            bge.logic.vesper_adl_ready = True
            
            print("🎉 VESPER ADL integration ready!")
            return True
        else:
            print("❌ VESPER ADL integration failed")
            return False
    else:
        print("✅ VESPER ADL integration already active")
        return True

def execute_adl_cooking_task():
    """Execute cooking ADL task - available globally"""
    if hasattr(bge.logic, 'execute_adl_task'):
        return bge.logic.execute_adl_task("Make oatmeal with raisins and brown sugar")
    else:
        print("❌ VESPER ADL not initialized")

def execute_adl_medication_task():
    """Execute medication ADL task - available globally"""
    if hasattr(bge.logic, 'execute_adl_task'):
        return bge.logic.execute_adl_task("Take morning medication")
    else:
        print("❌ VESPER ADL not initialized")

def execute_adl_communication_task():
    """Execute communication ADL task - available globally"""
    if hasattr(bge.logic, 'execute_adl_task'):
        return bge.logic.execute_adl_task("Make a phone call using phone book")
    else:
        print("❌ VESPER ADL not initialized")

def get_vesper_adl_status():
    """Get VESPER ADL system status"""
    if hasattr(bge.logic, 'vesper_adl_integration'):
        integration = bge.logic.vesper_adl_integration
        return integration.vesper_system.get_system_status_report()
    else:
        return {"status": "not_initialized"}

# Auto-initialize when imported
def auto_initialize_vesper_adl():
    """Auto-initialize VESPER ADL when this module is imported"""
    try:
        initialize_vesper_adl_integration()
    except Exception as e:
        print(f"⚠️  Auto-initialization failed: {e}")

# Run auto-initialization
if __name__ == "__main__":
    auto_initialize_vesper_adl()
elif 'bge' in globals():
    # Also auto-initialize when imported in BGE
    auto_initialize_vesper_adl()
