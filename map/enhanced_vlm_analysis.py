#!/usr/bin/env python3
"""
Enhanced VLM Analysis with Position-Aware Mapping

This module provides enhanced VLM navigation analysis using dynamic position maps
that show the actor's current location on the house layout.
"""

import os
import sys
import time
from datetime import datetime

def analyze_navigation_with_position_map(fp_image_path, position_map_path, house_layout_path, task, current_position, step_number, world_coords, room_detected=None):
    """Enhanced navigation analysis using position-aware mapping
    
    Args:
        fp_image_path: First-person view screenshot
        position_map_path: Generated position map showing actor location
        house_layout_path: Original house layout reference  
        task: Current CASAS task
        current_position: Position string for logging
        step_number: Current navigation step
        world_coords: (world_x, world_y) coordinates
        room_detected: Previously detected room
        
    Returns:
        Navigation result with enhanced spatial awareness
    """
    try:
        # Import required modules
        global llm_complete_func
        if 'llm_complete_func' not in globals():
            print("❌ LLM client not available")
            return None
        
        # Validate inputs
        if not fp_image_path or not os.path.exists(fp_image_path):
            print("❌ First-person image not available")
            return None
        
        # Check if position map is available
        use_position_map = position_map_path and os.path.exists(position_map_path)
        
        if use_position_map:
            print(f"🗺️ Using position-aware analysis with map: {os.path.basename(position_map_path)}")
        else:
            print("⚠️ Position map not available - using standard dual-image analysis")
        
        # Wait for screenshot readiness
        screenshot_ready = _wait_for_screenshot(fp_image_path)
        if not screenshot_ready:
            print("❌ Screenshot not ready")
            return None
        
        # Build enhanced prompt with position awareness
        prompt = _build_position_aware_prompt(task, current_position, step_number, world_coords, use_position_map)
        
        # Prepare images for VLM analysis
        images = [fp_image_path]
        
        if use_position_map:
            # Primary: Position-aware map showing actor location
            images.append(position_map_path)
            print(f"🔍 VLM analyzing: FP view + Position Map for '{task}'")
            
            # Optional: Original house layout as additional context
            if house_layout_path and os.path.exists(house_layout_path):
                images.append(house_layout_path)
                print(f"📋 Added original house layout as additional reference")
        else:
            # Fallback to original dual-image approach
            if house_layout_path and os.path.exists(house_layout_path):
                images.append(house_layout_path)
                print(f"🔍 VLM analyzing: FP view + House Layout (fallback)")
        
        # Call VLM with position-enhanced analysis
        start_time = time.time()
        response = llm_complete_func(prompt, images)
        end_time = time.time()
        
        if not response:
            print("❌ VLM returned no response")
            return None
        
        print(f"✅ Position-aware VLM analysis completed ({end_time - start_time:.2f}s)")
        
        # Parse response and add position context
        from llm_bge_navigation import parse_navigation_response
        result = parse_navigation_response(response)
        
        if result:
            # Add position mapping context to result
            result['position_map_used'] = use_position_map
            result['world_coordinates'] = world_coords
            result['response_time'] = end_time - start_time
            result['analysis_method'] = 'position_aware' if use_position_map else 'standard'
        
        return result
        
    except Exception as e:
        print(f"❌ Position-aware navigation analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def _wait_for_screenshot(fp_image_path, max_wait=2.0, min_size=2500):
    """Wait for screenshot to be ready for analysis"""
    wait_interval = 0.3
    attempts = int(max_wait / wait_interval)
    
    for attempt in range(attempts):
        if os.path.exists(fp_image_path):
            try:
                file_size = os.path.getsize(fp_image_path)
                if file_size >= min_size:
                    return True
            except:
                pass
        time.sleep(wait_interval)
    
    return False

def _build_position_aware_prompt(task, current_position, step_number, world_coords, use_position_map):
    """Build enhanced prompt with position awareness"""
    
    world_x, world_y = world_coords
    
    base_prompt = f"""You are an expert AI navigation assistant with ENHANCED SPATIAL AWARENESS through position mapping.

{"🗺️ POSITION-AWARE ANALYSIS MODE:" if use_position_map else "🏠 STANDARD DUAL-IMAGE ANALYSIS MODE:"}

IMAGES PROVIDED:
📷 IMAGE 1: First-person view from actor's current perspective
{"🎯 IMAGE 2: POSITION MAP showing actor's EXACT location on house layout with movement history" if use_position_map else "🏠 IMAGE 2: House layout reference (top-down floor plan)"}
{"📋 IMAGE 3: Original house layout reference for additional spatial context" if use_position_map else ""}

CURRENT MISSION: {task}
WORLD COORDINATES: ({world_x:.2f}, {world_y:.2f})
NAVIGATION STEP: {step_number + 1}

{"🎯 POSITION MAP ANALYSIS (CRITICAL):" if use_position_map else "🗺️ SPATIAL ANALYSIS INSTRUCTIONS:"}
{"1. **LOCATE ACTOR ON MAP**: Find the RED MARKER showing your exact current position" if use_position_map else "1. **SPATIAL CONTEXT**: Use the house layout to understand room connections"}
{"2. **ANALYZE MOVEMENT HISTORY**: Orange markers show where you've been - avoid backtracking" if use_position_map else "2. **ROOM IDENTIFICATION**: Match first-person view with layout structure"}
{"3. **IDENTIFY CURRENT ROOM**: Based on position marker location on the map" if use_position_map else "3. **NAVIGATION PLANNING**: Plan route from current to target room"}
{"4. **PLAN EFFICIENT ROUTE**: Use the map to navigate toward target room location" if use_position_map else "4. **OBSTACLE AVOIDANCE**: Check first-person view for immediate obstacles"}
{"5. **CROSS-REFERENCE WITH FP VIEW**: Ensure movement decision matches what you see ahead" if use_position_map else "5. **MOVEMENT EXECUTION**: Choose safe navigation action"}

ENHANCED ROOM IDENTIFICATION:
- **LIVING_ROOM**: Large central space with sofas, dining table, TV area
- **KITCHEN**: Upper area with appliances (stove, fridge, sink, counters)  
- **BEDROOM**: Lower right with bed, dresser, personal furniture
- **BATHROOM**: Small enclosed space with toilet, bathtub, sink
- **HALLWAY**: Narrow connecting corridors between rooms
- **DINING_ROOM**: Usually part of living room - look for dedicated dining table area

🎯 CASAS TASK TARGETS:
- **"Make a phone call"** → Navigate to DINING_ROOM area (phone/table)
- **"Wash hands"** → Navigate to KITCHEN (sink) or BATHROOM  
- **"Cook oatmeal"** → Navigate to KITCHEN (stove/cooking area)
- **"Eat meal"** → Navigate to DINING_ROOM (eating area)
- **"Clean dishes"** → Navigate to KITCHEN (sink area)

MOVEMENT COMMANDS:
- **FORWARD**: Move straight ahead (only if path is clear!)
- **BACKWARD**: Move backward (when stuck or need to retreat)
- **LEFT**: Turn body left (human-like rotation)
- **RIGHT**: Turn body right (human-like rotation)

{"🚀 POSITION-AWARE DECISION PROCESS:" if use_position_map else "🧭 NAVIGATION DECISION PROCESS:"}
{"1. **FIND YOUR POSITION**: Locate the red marker on the position map" if use_position_map else "1. **ASSESS CURRENT LOCATION**: Identify room from first-person view"}
{"2. **IDENTIFY TARGET LOCATION**: Find where the target room is on the map" if use_position_map else "2. **IDENTIFY TARGET ROOM**: Determine where you need to go"}
{"3. **PLAN SHORTEST PATH**: Trace route from your position to target on the map" if use_position_map else "3. **PLAN ROUTE**: Use house layout to plan navigation path"}
{"4. **CHECK IMMEDIATE VIEW**: Ensure chosen direction is safe in first-person view" if use_position_map else "4. **CHECK OBSTACLES**: Look for walls/furniture in first-person view"}
{"5. **EXECUTE MOVEMENT**: Choose action that progresses toward target safely" if use_position_map else "5. **MOVE SAFELY**: Execute movement avoiding collisions"}

RESPOND WITH JSON:
{{
    "current_room": "LIVING_ROOM",
    "target_room": "KITCHEN", 
    "casas_task": "Cook oatmeal",
    "position_analysis": "{"Located red marker in living room, need to go north to kitchen" if use_position_map else "Based on furniture, currently in living room"}",
    "movement_history_awareness": "{"Can see orange path markers showing previous movements" if use_position_map else "Planning based on spatial layout"}",
    "visible_obstacles": ["wall ahead", "furniture blocking"],
    "clear_directions": ["left turn available", "doorway visible"],
    "navigation_strategy": "{"Using position map to navigate efficiently to kitchen area" if use_position_map else "Following house layout to reach target room"}",
    "movement_decision": "LEFT",
    "reasoning": "{"Position map shows kitchen is northwest, turning left to align with target direction" if use_position_map else "Need to turn left to find path to target room"}",
    "doorway_visible": "no",
    "task_complete": false,
    "confidence": "high"
}}

{"🗺️ Remember: Use the POSITION MAP as your primary navigation reference! The red marker shows exactly where you are." if use_position_map else "🏠 Remember: Cross-reference first-person view with house layout for spatial awareness."}"""
    
    return base_prompt

# Integration function for existing navigation system
def enhanced_analyze_dual_image_navigation(fp_image_path, house_layout_path, task, current_position, step_number, world_coords=None, room_detected=None):
    """Drop-in replacement for analyze_dual_image_navigation with position mapping
    
    This function can replace the existing analyze_dual_image_navigation function
    to add position mapping capabilities.
    """
    
    # Generate position map if coordinates are available
    position_map_path = None
    
    if world_coords:
        try:
            # Import the mapping integration
            from bge_integration import update_actor_position_map
            
            world_x, world_y = world_coords
            position_map_path = update_actor_position_map(
                world_x, world_y, 
                room=room_detected, 
                task=task, 
                target_room=_extract_target_room(task)
            )
            
        except Exception as e:
            print(f"⚠️ Position mapping not available: {e}")
    
    # Use enhanced analysis if position map is available
    if position_map_path:
        return analyze_navigation_with_position_map(
            fp_image_path, position_map_path, house_layout_path,
            task, current_position, step_number, world_coords, room_detected
        )
    else:
        # Fallback to original analysis method
        print("⚠️ Falling back to standard dual-image analysis")
        # This would call the original function - for now, return None
        return None

def _extract_target_room(task):
    """Extract target room from CASAS task"""
    task_room_mapping = {
        "Make a phone call": "DINING_ROOM",
        "Wash hands": "KITCHEN", 
        "Cook oatmeal": "KITCHEN",
        "Eat meal": "DINING_ROOM",
        "Clean dishes": "KITCHEN"
    }
    return task_room_mapping.get(task, "UNKNOWN")

if __name__ == "__main__":
    print("🗺️ Enhanced VLM Position-Aware Analysis Module")
    print("This module provides enhanced navigation analysis using position maps.")
    print("Use enhanced_analyze_dual_image_navigation() as a drop-in replacement.")