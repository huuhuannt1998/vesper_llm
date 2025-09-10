#!/usr/bin/env python3
"""
VESPER ADL - Game Engine Integration

This script integrates VESPER ADL with your existing VLM navigation system
for live testing in Blender Game Engine mode.

Integration Points:
- Works with existing llm_bge_navigation.py
- Uses live VLM screenshot analysis
- Integrates with actor movement control
- Provides real-time ADL task execution
"""

import time
import json
import sys
import os
from pathlib import Path

# Only import bge when running in Blender
try:
    import bge
    BGE_AVAILABLE = True
except ImportError:
    BGE_AVAILABLE = False
    print("⚠️  BGE module not available - run this script inside Blender Game Engine")

# Add VESPER ADL system to path
current_dir = Path(__file__).parent
vesper_adl_path = current_dir / "vesper_adl_system"
if str(vesper_adl_path) not in sys.path:
    sys.path.append(str(vesper_adl_path))

class VESPERADLGameEngineIntegration:
    """
    VESPER ADL integration for live Game Engine testing.
    Works with existing VLM navigation and screenshot analysis.
    """
    
    def __init__(self):
        self.initialized = False
        self.current_adl_task = None
        self.task_start_time = None
        self.vlm_responses = []
        self.frame_count = 0
        
    def initialize_for_game_engine(self):
        """Initialize VESPER ADL for Game Engine mode"""
        
        if not BGE_AVAILABLE:
            print("❌ BGE not available - must run inside Blender")
            return False
            
        if self.initialized:
            return True
            
        print("🎮 Initializing VESPER ADL for Game Engine...")
        
        try:
            # Import VESPER ADL components
            from vesper_adl_blender_integration import initialize_vesper_adl_integration
            
            # Initialize the integration
            success = initialize_vesper_adl_integration()
            
            if success:
                # Setup Game Engine specific integration
                self.setup_game_engine_integration()
                self.initialized = True
                
                print("✅ VESPER ADL Game Engine integration ready!")
                print("🎯 Use F6-F8 for live ADL testing during VLM navigation")
                return True
            else:
                print("❌ VESPER ADL initialization failed")
                return False
                
        except Exception as e:
            print(f"❌ Game Engine integration error: {e}")
            return False
    
    def setup_game_engine_integration(self):
        """Setup integration with existing Game Engine systems"""
        
        # Store reference in BGE logic
        bge.logic.vesper_adl_game_integration = self
        
        # Setup frame-based monitoring
        bge.logic.vesper_adl_frame_monitor = self.frame_monitor
        
        # Integration with existing VLM navigation
        self.integrate_with_vlm_navigation()
        
        # Setup ADL task monitoring
        self.setup_adl_task_monitoring()
        
        print("✅ Game Engine integration components setup complete")
    
    def integrate_with_vlm_navigation(self):
        """Integrate with existing VLM navigation system"""
        
        # Check if VLM navigation is active
        if hasattr(bge.logic, 'latest_screenshot'):
            print("✅ Found existing VLM navigation system")
            bge.logic.vesper_uses_vlm_screenshots = True
        else:
            print("⚠️  VLM navigation not detected - using basic mode")
            bge.logic.vesper_uses_vlm_screenshots = False
        
        # Check for existing evaluation system
        if hasattr(bge.logic, 'evaluation_log'):
            print("✅ Enhanced existing evaluation system with VESPER ADL")
        else:
            # Create new evaluation system
            bge.logic.evaluation_log = {
                'vesper_adl_game_events': [],
                'start_time': time.time()
            }
        
        # Store actor reference
        scene = bge.logic.getCurrentScene()
        if 'Actor' in scene.objects:
            bge.logic.vesper_actor = scene.objects['Actor']
            print("✅ Connected to Actor object for ADL tasks")
    
    def setup_adl_task_monitoring(self):
        """Setup monitoring for ADL task execution in Game Engine"""
        
        # ADL task queue for Game Engine
        bge.logic.vesper_adl_task_queue = []
        bge.logic.vesper_adl_active_task = None
        
        # Performance monitoring
        bge.logic.vesper_adl_metrics = {
            'tasks_attempted': 0,
            'tasks_completed': 0,
            'total_duration': 0,
            'vlm_responses_used': 0
        }
        
        print("✅ ADL task monitoring system ready")
    
    def frame_monitor(self):
        """
        Frame-by-frame monitoring for Game Engine.
        Call this every frame to monitor ADL progress.
        """
        
        self.frame_count += 1
        
        # Monitor active ADL task
        if bge.logic.vesper_adl_active_task:
            self.monitor_active_adl_task()
        
        # Process task queue
        if bge.logic.vesper_adl_task_queue and not bge.logic.vesper_adl_active_task:
            self.start_next_adl_task()
        
        # Periodic status updates (every 5 seconds)
        if self.frame_count % 300 == 0:  # Assuming 60 FPS
            self.log_periodic_status()
    
    def monitor_active_adl_task(self):
        """Monitor progress of currently active ADL task"""
        
        active_task = bge.logic.vesper_adl_active_task
        
        # Check for task timeout (60 seconds max)
        if time.time() - active_task['start_time'] > 60:
            print(f"⏰ ADL Task timeout: {active_task['description']}")
            self.complete_adl_task(success=False, reason="timeout")
            return
        
        # Check for VLM feedback integration
        if hasattr(bge.logic, 'latest_vlm_response'):
            vlm_response = bge.logic.latest_vlm_response
            if vlm_response and vlm_response not in self.vlm_responses:
                self.vlm_responses.append(vlm_response)
                active_task['vlm_responses_count'] = len(self.vlm_responses)
                
                print(f"📸 VLM Response for ADL task: {vlm_response[:50]}...")
    
    def start_next_adl_task(self):
        """Start the next ADL task from the queue"""
        
        if not bge.logic.vesper_adl_task_queue:
            return
        
        task = bge.logic.vesper_adl_task_queue.pop(0)
        
        print(f"🎯 Starting ADL Task: {task['description']}")
        
        bge.logic.vesper_adl_active_task = {
            'description': task['description'],
            'type': task['type'],
            'start_time': time.time(),
            'vlm_responses_count': 0,
            'actor_position_start': tuple(bge.logic.vesper_actor.worldPosition) if hasattr(bge.logic, 'vesper_actor') else None
        }
        
        # Execute the actual ADL task
        try:
            if hasattr(bge.logic, 'vesper_adl_functions'):
                task_function = bge.logic.vesper_adl_functions.get(task['type'])
                if task_function:
                    # Execute in background (non-blocking for Game Engine)
                    self.execute_adl_task_async(task_function, task)
                else:
                    print(f"❌ ADL Task function not found: {task['type']}")
                    self.complete_adl_task(success=False, reason="function_not_found")
            else:
                print("❌ VESPER ADL functions not available")
                self.complete_adl_task(success=False, reason="functions_not_available")
                
        except Exception as e:
            print(f"❌ ADL Task execution error: {e}")
            self.complete_adl_task(success=False, reason=str(e))
    
    def execute_adl_task_async(self, task_function, task):
        """Execute ADL task asynchronously for Game Engine"""
        
        # Store task execution context
        bge.logic.vesper_adl_execution_context = {
            'function': task_function,
            'task': task,
            'execution_start': time.time()
        }
        
        # For Game Engine, we'll execute immediately but monitor results
        try:
            result = task_function()
            
            if result:
                success = result.get('success', False)
                duration = result.get('duration', time.time() - bge.logic.vesper_adl_active_task['start_time'])
                
                self.complete_adl_task(
                    success=success,
                    duration=duration,
                    result=result
                )
            else:
                self.complete_adl_task(success=False, reason="no_result")
                
        except Exception as e:
            print(f"❌ Async ADL task error: {e}")
            self.complete_adl_task(success=False, reason=str(e))
    
    def complete_adl_task(self, success, duration=None, result=None, reason=None):
        """Complete the current ADL task and log results"""
        
        if not bge.logic.vesper_adl_active_task:
            return
        
        active_task = bge.logic.vesper_adl_active_task
        
        if duration is None:
            duration = time.time() - active_task['start_time']
        
        # Create completion record
        completion_record = {
            'timestamp': time.time(),
            'description': active_task['description'],
            'type': active_task['type'],
            'success': success,
            'duration': duration,
            'vlm_responses_used': active_task['vlm_responses_count'],
            'frame_count_during_task': self.frame_count,
            'result': result,
            'failure_reason': reason if not success else None
        }
        
        # Update metrics
        bge.logic.vesper_adl_metrics['tasks_attempted'] += 1
        if success:
            bge.logic.vesper_adl_metrics['tasks_completed'] += 1
        bge.logic.vesper_adl_metrics['total_duration'] += duration
        bge.logic.vesper_adl_metrics['vlm_responses_used'] += active_task['vlm_responses_count']
        
        # Log to evaluation system
        bge.logic.evaluation_log['vesper_adl_game_events'].append(completion_record)
        
        # Clear active task
        bge.logic.vesper_adl_active_task = None
        
        # Print result
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} ADL Task: {active_task['description']} ({duration:.1f}s)")
        if reason:
            print(f"   Reason: {reason}")
    
    def log_periodic_status(self):
        """Log periodic status during Game Engine runtime"""
        
        metrics = bge.logic.vesper_adl_metrics
        success_rate = (metrics['tasks_completed'] / metrics['tasks_attempted']) * 100 if metrics['tasks_attempted'] > 0 else 0
        avg_duration = metrics['total_duration'] / metrics['tasks_completed'] if metrics['tasks_completed'] > 0 else 0
        
        print(f"📊 VESPER ADL Status: {metrics['tasks_completed']}/{metrics['tasks_attempted']} tasks ({success_rate:.1f}% success, {avg_duration:.1f}s avg)")

# Global functions for Game Engine keyboard control
def queue_adl_cooking_task():
    """Queue cooking ADL task for Game Engine execution"""
    if hasattr(bge.logic, 'vesper_adl_task_queue'):
        task = {
            'description': 'Make oatmeal with raisins and brown sugar',
            'type': 'cooking_task'
        }
        bge.logic.vesper_adl_task_queue.append(task)
        print(f"🍳 Queued cooking task (Queue: {len(bge.logic.vesper_adl_task_queue)})")

def queue_adl_medication_task():
    """Queue medication ADL task for Game Engine execution"""
    if hasattr(bge.logic, 'vesper_adl_task_queue'):
        task = {
            'description': 'Take morning medication',
            'type': 'medication_task'
        }
        bge.logic.vesper_adl_task_queue.append(task)
        print(f"💊 Queued medication task (Queue: {len(bge.logic.vesper_adl_task_queue)})")

def queue_adl_communication_task():
    """Queue communication ADL task for Game Engine execution"""
    if hasattr(bge.logic, 'vesper_adl_task_queue'):
        task = {
            'description': 'Make phone call using phone book',
            'type': 'communication_task'
        }
        bge.logic.vesper_adl_task_queue.append(task)
        print(f"📞 Queued communication task (Queue: {len(bge.logic.vesper_adl_task_queue)})")

def get_vesper_adl_game_status():
    """Get VESPER ADL status during Game Engine runtime"""
    if hasattr(bge.logic, 'vesper_adl_metrics'):
        metrics = bge.logic.vesper_adl_metrics
        return {
            'active': hasattr(bge.logic, 'vesper_adl_active_task') and bge.logic.vesper_adl_active_task is not None,
            'queue_length': len(bge.logic.vesper_adl_task_queue) if hasattr(bge.logic, 'vesper_adl_task_queue') else 0,
            'tasks_completed': metrics['tasks_completed'],
            'tasks_attempted': metrics['tasks_attempted'],
            'success_rate': (metrics['tasks_completed'] / metrics['tasks_attempted']) * 100 if metrics['tasks_attempted'] > 0 else 0
        }
    return {'status': 'not_initialized'}

# Main Game Engine integration function
def initialize_vesper_adl_for_game_engine():
    """Initialize VESPER ADL for Game Engine testing"""
    
    if not BGE_AVAILABLE:
        print("❌ BGE not available - this function requires Game Engine mode")
        print("📋 To use VESPER ADL:")
        print("1. Setup the BGE logic first")
        print("2. Press 'P' to start Game Engine")
        print("3. VESPER ADL will auto-initialize in Game Engine mode")
        return False
    
    if not hasattr(bge.logic, 'vesper_adl_game_integration'):
        integration = VESPERADLGameEngineIntegration()
        success = integration.initialize_for_game_engine()
        
        if success:
            # Add global functions to BGE logic
            bge.logic.queue_adl_cooking = queue_adl_cooking_task
            bge.logic.queue_adl_medication = queue_adl_medication_task
            bge.logic.queue_adl_communication = queue_adl_communication_task
            bge.logic.get_vesper_adl_status = get_vesper_adl_game_status
            
            print("🎮 VESPER ADL Game Engine integration complete!")
            return True
        else:
            print("❌ VESPER ADL Game Engine integration failed")
            return False
    else:
        print("✅ VESPER ADL Game Engine integration already active")
        return True

# Keyboard handler for Game Engine
def handle_vesper_adl_keyboard_in_game():
    """Handle VESPER ADL keyboard input during Game Engine runtime"""
    
    keyboard = bge.logic.getCurrentController().sensors.get('Keyboard')
    if not keyboard or not keyboard.positive:
        return
    
    for key in keyboard.events:
        if keyboard.events[key] == bge.logic.KX_INPUT_JUST_ACTIVATED:
            
            if key == bge.events.F6KEY:
                queue_adl_cooking_task()
                
            elif key == bge.events.F7KEY:
                queue_adl_medication_task()
                
            elif key == bge.events.F8KEY:
                queue_adl_communication_task()
                
            elif key == bge.events.F9KEY:
                status = get_vesper_adl_game_status()
                print(f"📊 VESPER ADL Status: {status}")

# Auto-initialize when imported (only in BGE)
if BGE_AVAILABLE:
    initialize_vesper_adl_for_game_engine()

# Main function for text editor execution
def main():
    """Main function when run from text editor"""
    if not BGE_AVAILABLE:
        print("❌ This script must be run inside Blender!")
        print("📋 Instructions:")
        print("1. Open Blender")
        print("2. Go to Scripting tab")
        print("3. Open this file in Blender's text editor")
        print("4. Click 'Run Script' button")
        print("5. Then press 'P' to start Game Engine")
        return False
    print("🎮 VESPER ADL Game Engine Integration")
    print("=====================================")
    print("This script sets up VESPER ADL for live Game Engine testing.")
    print("")
    print("📋 Usage:")
    print("1. Run this script in Blender text editor")
    print("2. Press 'P' to start Game Engine")
    print("3. Use F6-F9 keys during VLM navigation:")
    print("   F6: Queue cooking task")
    print("   F7: Queue medication task") 
    print("   F8: Queue communication task")
    print("   F9: Show status")
    print("")
    print("🎯 The system will:")
    print("- Integrate with existing VLM screenshot analysis")
    print("- Execute ADL tasks during live navigation")
    print("- Monitor performance in real-time")
    print("- Log results to evaluation system")

if __name__ == "__main__":
    main()
