"""
VESPER Interaction System Integration Guide for llm_bge_navigation.py

This file shows the exact changes needed to integrate the interaction system.
"""

# ============================================================================
# STEP 1: Add import at the top of llm_bge_navigation.py
# ============================================================================

# Add this AFTER the Smart Pathfinding import section (around line 95-105):

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


# ============================================================================
# STEP 2: Initialize in main() function
# ============================================================================

# Add this AFTER the CASAS motion sensor initialization (around line 1234):

        # Initialize VESPER Interaction System (NEW)
        if INTERACTION_SYSTEM_AVAILABLE and not hasattr(bge.logic, 'interaction_system'):
            try:
                if initialize_interaction_system_for_bge():
                    print("✅ VESPER Interaction System integrated with BGE")
                else:
                    print("⚠️ Interaction system initialization failed")
            except Exception as e:
                print(f"⚠️ Failed to initialize interaction system: {e}")


# ============================================================================
# STEP 3: Add task start tracking in run_continuous_navigation()
# ============================================================================

# Find where task starts (around line 1260-1280) and add this
# AFTER the current_task_logged check:

        # Start task with interaction system (NEW)
        if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
            scene = bge.logic.getCurrentScene()
            actor = scene.objects.get("Actor")
            
            if actor and not hasattr(bge.logic, 'task_interaction_started'):
                actor_pos = [actor.worldPosition.x, actor.worldPosition.y]
                
                try:
                    # Start task with full interaction support
                    task_context = bge.logic.interaction_system.start_task_with_interactions(
                        current_task,
                        actor_pos
                    )
                    
                    bge.logic.task_interaction_started = True
                    
                    print(f"🎯 Interaction system started for task: {current_task}")
                    if task_context.get('time_acceleration'):
                        print(f"⏩ Time acceleration available for this task")
                except Exception as e:
                    print(f"⚠️ Failed to start task interactions: {e}")


# ============================================================================
# STEP 4: Update interaction state during navigation
# ============================================================================

# Add this AFTER the screenshot capture and BEFORE VLM analysis (around line 1320-1340):

        # Update interaction state during navigation (NEW)
        if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
            actor = scene.objects.get("Actor")
            if actor:
                actor_pos = [actor.worldPosition.x, actor.worldPosition.y]
                
                try:
                    # Check for auto-interactions with nearby objects
                    events = bge.logic.interaction_system.update_interaction_state(
                        actor_pos,
                        current_task
                    )
                    
                    # Log interaction events
                    for event in events:
                        print(f"🤝 Interaction event: {event['type']} - {event['object']}")
                except Exception as e:
                    print(f"⚠️ Interaction update failed: {e}")


# ============================================================================
# STEP 5: Handle task completion with interactions
# ============================================================================

# Find where task_complete is True (around line 1380-1400) and REPLACE
# the task completion section with:

            if task_complete:
                print(f"✅ VLM reports task '{current_task}' is COMPLETE!")
                
                # Complete task with interaction system (NEW)
                if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
                    try:
                        bge.logic.interaction_system.complete_task(current_task, success=True)
                        bge.logic.task_interaction_started = False
                        print("🎯 Interaction system task completed")
                    except Exception as e:
                        print(f"⚠️ Interaction task completion failed: {e}")
                
                # Log successful task completion (existing code)
                if hasattr(bge.logic, 'metrics_logger'):
                    scene = bge.logic.getCurrentScene()
                    actor = scene.objects.get("Actor")
                    final_pos = [actor.worldPosition.x, actor.worldPosition.y] if actor else None
                    bge.logic.metrics_logger.complete_task(
                        success=True,
                        final_position=final_pos
                    )
                
                # Move to next task
                bge.logic.current_task_index += 1
                bge.logic.navigation_step = 0
                time.sleep(2.0)
                return


# ============================================================================
# STEP 6: Handle task failure with interactions
# ============================================================================

# Find where task exceeds max steps (around line 1280-1295) and REPLACE with:

        if bge.logic.navigation_step >= bge.logic.max_steps_per_task:
            print(f"⏱️ Task '{current_task}' exceeded max steps ({bge.logic.max_steps_per_task})")
            print("➡️ Moving to next task...")
            
            # Complete task with interaction system as failed (NEW)
            if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
                try:
                    bge.logic.interaction_system.complete_task(current_task, success=False)
                    bge.logic.task_interaction_started = False
                except Exception as e:
                    print(f"⚠️ Interaction task failure logging failed: {e}")
            
            # Log task completion/failure (existing code)
            if hasattr(bge.logic, 'metrics_logger'):
                scene = bge.logic.getCurrentScene()
                actor = scene.objects.get("Actor")
                final_pos = [actor.worldPosition.x, actor.worldPosition.y] if actor else None
                bge.logic.metrics_logger.complete_task(
                    success=False, 
                    failure_reason=f"Exceeded max steps ({bge.logic.max_steps_per_task})",
                    final_position=final_pos
                )
            
            bge.logic.current_task_index += 1
            bge.logic.navigation_step = 0
            time.sleep(2.0)
            return


# ============================================================================
# STEP 7: Export all data when session completes
# ============================================================================

# Find where all tasks are completed (around line 1250-1270) and ADD:

        if bge.logic.current_task_index >= len(bge.logic.vesper_tasks):
            print("🎉 ALL TASKS COMPLETED! Navigation system finished.")
            
            # Print final metrics summary and export datasets (existing code)
            if hasattr(bge.logic, 'metrics_logger'):
                bge.logic.metrics_logger._print_task_summary()
                if hasattr(bge.logic.metrics_logger, '_export_datasets'):
                    bge.logic.metrics_logger._export_datasets()
            
            # Export interaction system data (NEW)
            if INTERACTION_SYSTEM_AVAILABLE and hasattr(bge.logic, 'interaction_system'):
                try:
                    print("\n💾 Exporting VESPER Interaction System data...")
                    bge.logic.interaction_system.print_session_summary()
                    bge.logic.interaction_system.export_all_data()
                except Exception as e:
                    print(f"⚠️ Interaction data export failed: {e}")
            
            return


# ============================================================================
# OPTIONAL: Add VLM-guided object interaction
# ============================================================================

# If you want VLM to decide when to interact with objects, add this function:

def check_vlm_object_interaction(actor_position, current_task):
    """
    Use VLM to decide whether to interact with nearby objects
    Call this when actor reaches target location
    """
    if not INTERACTION_SYSTEM_AVAILABLE or not hasattr(bge.logic, 'interaction_system'):
        return None
    
    handler = bge.logic.interaction_system.interaction_handler
    
    # Check nearby objects
    nearby = handler.check_nearby_objects(actor_position)
    
    if not nearby:
        return None
    
    # Use VLM to decide (requires llm_complete_func)
    global llm_complete_func
    if llm_complete_func:
        try:
            decision = handler.vlm_guided_interaction(
                actor_position,
                current_task,
                llm_complete_func
            )
            
            if decision:
                print(f"🤖 VLM interaction decision: {decision['object']}")
                print(f"   Reasoning: {decision['reasoning']}")
                
                # Use time acceleration if needed
                duration = decision.get('duration', 5.0)
                
                if duration > 30:  # More than 30 seconds
                    bge.logic.interaction_system.handle_long_duration_task(
                        f"interact_{decision['object']}",
                        duration,
                        max_real_duration=min(10.0, duration/10)
                    )
                else:
                    # Normal interaction
                    time.sleep(2)
                
                return decision
        except Exception as e:
            print(f"⚠️ VLM interaction decision failed: {e}")
    
    return None


# ============================================================================
# SUMMARY OF CHANGES
# ============================================================================

"""
Total Integration Points:

1. Import statement (1 location)
2. Initialize in main() (1 location)  
3. Start task tracking (1 location)
4. Update interaction state (1 location)
5. Task completion with interactions (1 location)
6. Task failure with interactions (1 location)
7. Export data when done (1 location)

OPTIONAL:
8. VLM-guided interaction function (1 location)

The system integrates seamlessly - minimal code changes required!

All interaction features work automatically:
- Item sensors track object usage
- Devices auto-control based on tasks
- Time acceleration for long tasks
- CASAS-compatible data export

No changes needed to existing navigation logic!
"""
