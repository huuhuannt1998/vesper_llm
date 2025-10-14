"""
Quick Start: Integrating VESPER Interaction System with BGE Navigation

This guide shows how to add interaction capabilities to the existing
llm_bge_navigation.py system.
"""

# ============================================================================
# STEP 1: Add imports at the top of llm_bge_navigation.py
# ============================================================================

# Add after existing imports:
try:
    from vesper_interaction_integration import (
        get_interaction_system,
        initialize_interaction_system_for_bge
    )
    INTERACTION_SYSTEM_AVAILABLE = True
except ImportError:
    INTERACTION_SYSTEM_AVAILABLE = False
    print("⚠️ Interaction system not available")


# ============================================================================
# STEP 2: Initialize in main() function
# ============================================================================

def main():
    """Main BGE navigation function - with interaction support"""
    global scene_running
    
    if not scene_running:
        scene_running = True
        print("🚀 BGE Continuous Navigation System Starting...")
        
        # ... existing initialization code ...
        
        # NEW: Initialize interaction system
        if INTERACTION_SYSTEM_AVAILABLE:
            if initialize_interaction_system_for_bge():
                print("✅ Interaction system integrated")
            else:
                print("⚠️ Interaction system initialization failed")
        
        # ... rest of existing code ...


# ============================================================================
# STEP 3: Modify run_continuous_navigation() to use interactions
# ============================================================================

def run_continuous_navigation():
    """Continuous navigation with interaction support"""
    try:
        # ... existing code to get current task ...
        
        current_task = bge.logic.vesper_tasks[bge.logic.current_task_index]
        
        # NEW: Start task with interaction system
        if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            
            if actor and not hasattr(bge.logic, 'task_interaction_started'):
                actor_pos = [actor.worldPosition.x, actor.worldPosition.y]
                
                # Start task with full interaction support
                task_context = bge.logic.interaction_system.start_task_with_interactions(
                    current_task,
                    actor_pos
                )
                
                bge.logic.task_interaction_started = True
                
                # Check if this is a long-duration task
                if task_context.get('time_acceleration'):
                    print(f"⏩ Time acceleration available for this task")
        
        # ... existing navigation code ...
        
        # NEW: Update interaction state during navigation
        if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
            actor = scene.objects.get("Actor")
            if actor:
                actor_pos = [actor.worldPosition.x, actor.worldPosition.y]
                
                # Check for auto-interactions with nearby objects
                events = bge.logic.interaction_system.update_interaction_state(
                    actor_pos,
                    current_task
                )
                
                # Log interaction events
                for event in events:
                    print(f"🤝 {event['type']}: {event['object']}")
        
        # ... existing movement execution ...
        
        # NEW: Check if VLM reports task complete
        if task_complete:
            print(f"✅ VLM reports task '{current_task}' is COMPLETE!")
            
            # Complete task with interaction system
            if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
                bge.logic.interaction_system.complete_task(current_task, success=True)
                bge.logic.task_interaction_started = False
            
            # ... existing task completion code ...
        
        # ... rest of navigation logic ...
        
    except Exception as e:
        print(f"❌ Navigation error: {e}")


# ============================================================================
# STEP 4: Add interaction-aware task completion
# ============================================================================

def complete_current_task(success=True, failure_reason=None):
    """Complete current task with interaction tracking"""
    
    # Complete with interaction system
    if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
        current_task = bge.logic.vesper_tasks[bge.logic.current_task_index]
        bge.logic.interaction_system.complete_task(current_task, success=success)
        bge.logic.task_interaction_started = False
    
    # Existing metrics logging
    if hasattr(bge.logic, 'metrics_logger'):
        scene = bge.logic.getCurrentScene()
        actor = scene.objects.get("Actor")
        final_pos = [actor.worldPosition.x, actor.worldPosition.y] if actor else None
        bge.logic.metrics_logger.complete_task(
            success=success,
            failure_reason=failure_reason,
            final_position=final_pos
        )
    
    # Move to next task
    bge.logic.current_task_index += 1
    bge.logic.navigation_step = 0


# ============================================================================
# STEP 5: Add final export when all tasks complete
# ============================================================================

def finalize_session():
    """Called when all tasks are completed"""
    
    print("🎉 ALL TASKS COMPLETED!")
    
    # Export navigation metrics (existing)
    if hasattr(bge.logic, 'metrics_logger'):
        bge.logic.metrics_logger._print_task_summary()
        if hasattr(bge.logic.metrics_logger, '_export_datasets'):
            bge.logic.metrics_logger._export_datasets()
    
    # NEW: Export interaction data
    if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
        print("\n💾 Exporting interaction data...")
        bge.logic.interaction_system.print_session_summary()
        bge.logic.interaction_system.export_all_data()


# ============================================================================
# STEP 6: Optional - Add VLM-guided interaction decisions
# ============================================================================

def check_for_vlm_interaction(actor_position, task_name):
    """Use VLM to decide whether to interact with nearby objects"""
    
    if not INTERACTION_SYSTEM_AVAILABLE:
        return None
    
    if not hasattr(bge.logic, 'interaction_system'):
        return None
    
    handler = bge.logic.interaction_system.interaction_handler
    
    # Check nearby objects
    nearby = handler.check_nearby_objects(actor_position)
    
    if not nearby:
        return None
    
    # Use VLM to decide (requires llm_complete_func)
    if llm_complete_func:
        decision = handler.vlm_guided_interaction(
            actor_position,
            task_name,
            llm_complete_func
        )
        
        if decision:
            print(f"🤖 VLM interaction decision: {decision['object']}")
            print(f"   Reasoning: {decision['reasoning']}")
            
            # Start interaction based on VLM decision
            duration = decision.get('duration', 5.0)
            
            # Use time acceleration if needed
            if duration > 30:  # More than 30 seconds
                bge.logic.interaction_system.handle_long_duration_task(
                    f"interact_{decision['object']}",
                    duration,
                    max_real_duration=min(10.0, duration/10)
                )
            else:
                # Normal interaction
                import time
                time.sleep(2)  # Brief interaction
            
            return decision
    
    return None


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

"""
The interaction system will automatically:

1. Track when actor interacts with objects (item sensors)
2. Control virtual devices based on tasks (lights, appliances)
3. Accelerate time for long-duration tasks (sleeping, cooking)
4. Export CASAS-compatible logs

No changes needed to existing navigation logic - it enhances automatically!

To use advanced features:
- Call check_for_vlm_interaction() when actor reaches target
- Use handle_long_duration_task() for time-consuming activities
- Query interaction_system for nearby interactive objects
"""


# ============================================================================
# MINIMAL INTEGRATION (Just add to main function)
# ============================================================================

def minimal_integration_example():
    """Minimal code to add interaction system"""
    
    # In main() initialization:
    if INTERACTION_SYSTEM_AVAILABLE:
        initialize_interaction_system_for_bge()
    
    # When task completes (add to existing completion code):
    if hasattr(bge.logic, 'interaction_system'):
        bge.logic.interaction_system.complete_task(current_task, success=True)
    
    # When all tasks done:
    if hasattr(bge.logic, 'interaction_system'):
        bge.logic.interaction_system.export_all_data()
    
    # That's it! System works automatically.
