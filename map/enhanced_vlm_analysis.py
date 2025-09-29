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

def analyze_navigation_with_position_map(fp_image_path, position_map_path, house_layout_path, task, current_position, step_number, world_coords, room_detected=None, llm_func=None):
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
        llm_func: LLM completion function to use
        
    Returns:
        Navigation result with enhanced spatial awareness
    """
    try:
        # Use passed LLM function or try to import from BGE navigation
        if llm_func:
            llm_complete_func = llm_func
        else:
            # Try to import from the BGE navigation module
            try:
                import sys
                current_dir = os.path.dirname(os.path.dirname(__file__))
                blender_dir = os.path.join(current_dir, 'blender')
                if blender_dir not in sys.path:
                    sys.path.insert(0, blender_dir)
                
                import llm_bge_navigation
                llm_complete_func = getattr(llm_bge_navigation, 'llm_complete_func', None)
            except Exception as e:
                print(f"❌ Could not import LLM function: {e}")
                llm_complete_func = None
        
        if not llm_complete_func:
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
        
        # Wait for screenshot readiness with fallback
        screenshot_result = _wait_for_screenshot(fp_image_path)
        if not screenshot_result:
            print("❌ Screenshot not ready")
            return None
        elif isinstance(screenshot_result, str):
            # Fallback screenshot path returned
            fp_image_path = screenshot_result
            print(f"📷 Enhanced analysis using fallback image: {os.path.basename(fp_image_path)}")
        # else screenshot_result is True, use original fp_image_path
        
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
    """Wait for screenshot to be ready for analysis with fallback logic"""
    import time
    wait_interval = 0.3
    attempts = int(max_wait / wait_interval)
    
    # First, try to wait for the current screenshot
    for attempt in range(attempts):
        if os.path.exists(fp_image_path):
            try:
                file_size = os.path.getsize(fp_image_path)
                if file_size >= min_size:
                    print(f"✅ Enhanced analysis screenshot ready: {os.path.basename(fp_image_path)} ({file_size:,} bytes)")
                    return True
            except:
                pass
        time.sleep(wait_interval)
    
    # If current screenshot not ready, look for recent screenshots (same logic as standard analysis)
    print(f"⏳ Current screenshot not ready in enhanced analysis, checking for recent screenshots...")
    captures_dir = os.path.dirname(fp_image_path)
    if os.path.exists(captures_dir):
        existing_files = [f for f in os.listdir(captures_dir) if f.startswith("fp_view_") and f.endswith(".png")]
        if existing_files:
            existing_files.sort(reverse=True)
            recent_screenshot = os.path.join(captures_dir, existing_files[0])
            
            if os.path.exists(recent_screenshot):
                try:
                    file_size = os.path.getsize(recent_screenshot)
                    if file_size > 1000:  # Lower threshold for fallback
                        print(f"📸 Enhanced analysis using recent screenshot: {os.path.basename(recent_screenshot)} ({file_size:,} bytes)")
                        # Update the fp_image_path to point to the recent screenshot
                        # Note: This is a bit hacky but needed for compatibility
                        return recent_screenshot  # Return the path instead of True
                except:
                    pass
    
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
def enhanced_analyze_dual_image_navigation(fp_image_path, house_layout_path, task, current_position, step_number, world_coords=None, room_detected=None, llm_func=None):
    """Drop-in replacement for analyze_dual_image_navigation with position mapping
    
    This function can replace the existing analyze_dual_image_navigation function
    to add position mapping capabilities.
    """
    
    # Generate position map if coordinates are available
    position_map_path = None
    
    if world_coords:
        try:
            # Try to import the mapping integration from BGE
            from bge_integration import update_actor_position_map
            
            world_x, world_y = world_coords
            position_map_path = update_actor_position_map(
                world_x, world_y, 
                room=room_detected, 
                task=task, 
                target_room=_extract_target_room(task)
            )
            
        except ImportError:
            # BGE integration not available - try position mapper directly
            try:
                from position_mapper import VESPERPositionMapper
                
                world_x, world_y = world_coords
                mapper = VESPERPositionMapper()
                
                # Generate position map for this analysis step
                position_map_path = mapper.create_actor_position_map(
                    world_x, world_y,
                    room_name=room_detected or "UNKNOWN",
                    task_name=task,
                    target_room=_extract_target_room(task),
                    step_number=step_number
                )
                
            except Exception as e:
                print(f"⚠️ Position mapping not available: {e}")
    
    # Use enhanced analysis if position map is available
    if position_map_path:
        return analyze_navigation_with_position_map(
            fp_image_path, position_map_path, house_layout_path,
            task, current_position, step_number, world_coords, room_detected, llm_func
        )
    else:
        # Fallback to standard VLM analysis without position mapping
        print("⚠️ Falling back to standard VLM analysis")
        
        # Perform standard VLM analysis with available images
        if not llm_func:
            print("❌ No LLM function available for fallback analysis")
            return None
            
        try:
            # Build basic navigation prompt
            prompt = f"""You are an expert AI navigation assistant analyzing indoor environments.

TASK: {task}
CURRENT POSITION: {current_position}
STEP: {step_number}
ROOM DETECTED: {room_detected or "Unknown"}

Analyze the provided first-person view image and provide navigation guidance.

RESPONSE FORMAT (JSON):
{{
    "movement_decision": "FORWARD|BACKWARD|LEFT|RIGHT|STOP",
    "reasoning": "Brief explanation of decision",
    "current_room": "Room type detected",
    "confidence": "0.0-1.0",
    "task_complete": false
}}"""

            # Call VLM with just the first-person view
            images = [fp_image_path]
            if house_layout_path and os.path.exists(house_layout_path):
                images.append(house_layout_path)
                
            result = llm_func(prompt, images)
            
            if result:
                print(f"✅ Standard VLM analysis completed")
                return _parse_navigation_result(result)
            else:
                print("❌ Standard VLM analysis failed")
                return None
                
        except Exception as e:
            print(f"❌ Fallback analysis failed: {e}")
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

def _parse_navigation_result(llm_result):
    """Parse LLM result into structured navigation response"""
    if not llm_result:
        return None
        
    import json
    import re
    
    try:
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*?\}', llm_result, re.DOTALL)
        if json_match:
            result_data = json.loads(json_match.group())
        else:
            # Create basic response from text
            result_data = {
                "movement_decision": "FORWARD",
                "reasoning": llm_result[:100] + "..." if len(llm_result) > 100 else llm_result,
                "current_room": "UNKNOWN",
                "confidence": 0.5,
                "task_complete": False
            }
        
        return result_data
        
    except Exception as e:
        print(f"⚠️ Could not parse LLM result: {e}")
        return {
            "movement_decision": "FORWARD",
            "reasoning": "Parse error - proceeding forward",
            "current_room": "UNKNOWN",
            "confidence": 0.3,
            "task_complete": False
        }

if __name__ == "__main__":
    print("🗺️ Enhanced VLM Position-Aware Analysis Module")
    print("This module provides enhanced navigation analysis using position maps.")
    print("Use enhanced_analyze_dual_image_navigation() as a drop-in replacement.")