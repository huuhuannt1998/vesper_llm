"""
Updated navigation function with few-shot prompting
This replaces the existing get_navigation_sequence_with_vlm function
"""

import os
import json

def get_navigation_sequence_with_vlm_fewshot(screenshot_path, current_task):
    """Get movement sequence from VLM using few-shot prompting - MUST have a real screenshot"""
    if not LLM_AVAILABLE:
        raise Exception("❌ LLM not available - cannot proceed without vision capabilities")

    if not screenshot_path or not os.path.exists(screenshot_path):
        raise Exception(f"❌ No valid screenshot available at: {screenshot_path}")

    # Get current actor position and movement history for context
    import bge
    scene = bge.logic.getCurrentScene()
    actor = scene.objects.get("Actor")
    current_pos = f"[{actor.worldPosition.x:.1f}, {actor.worldPosition.y:.1f}]" if actor else "[unknown]"
    
    # Track position history to detect looping and drift
    if not hasattr(bge.logic, 'position_history'):
        bge.logic.position_history = []
    if not hasattr(bge.logic, 'analysis_count'):
        bge.logic.analysis_count = 0
    
    bge.logic.analysis_count += 1
    
    if actor:
        pos = (round(actor.worldPosition.x, 1), round(actor.worldPosition.y, 1))
        bge.logic.position_history.append(pos)
        # Keep only last 8 positions for loop detection
        if len(bge.logic.position_history) > 8:
            bge.logic.position_history.pop(0)
            
        # Detect looping behavior
        if len(bge.logic.position_history) >= 6:
            recent_positions = bge.logic.position_history[-6:]
            unique_positions = len(set(recent_positions))
            if unique_positions <= 3:
                print(f"⚠️ BGE: Loop detected in positions: {recent_positions}")

    print(f"🔍 BGE: Analyzing image: {os.path.basename(screenshot_path)} - Actor at {current_pos}")

    # Build few-shot prompt
    if few_shot_system:
        prompt = few_shot_system.build_few_shot_prompt(current_task, screenshot_path)
        print("🎯 Using few-shot prompting for navigation")
    else:
        # Fallback to original prompt if few-shot system not available
        prompt = f"""You are a navigation assistant for a house exploration game. The pink dot represents the actor's position.

Task: {current_task}
Actor position: {current_pos}
Analysis #{bge.logic.analysis_count}

MOVEMENT RULES:
- MAXIMUM 1-2 moves per sequence (be efficient!)
- Only move through areas with visible floors and furniture
- Stop immediately when you reach the correct room with target furniture
- If you've been analyzing many times, prioritize finding and completing the task quickly
- If image is unclear, use STAY and request new analysis rather than guessing directions
- NEVER suggest moves that could lead outside the visible house structure

JSON Response Format:
{{
  "current_room": "Based on furniture around pink dot: [BEDROOM/KITCHEN/LIVING_ROOM/BATHROOM/UNKNOWN]",
  "furniture_visible": "List the specific furniture items you can see near the pink dot",
  "task_complete": true/false,
  "movement_sequence": ["UP", "RIGHT"] or ["STAY"],
  "reasoning": "ROOM ANALYSIS: [describe furniture seen]. TASK STATUS: [complete/continue]. PATH: [next moves]"
}}

CRITICAL: movement_sequence must contain ONLY these exact words: "UP", "DOWN", "LEFT", "RIGHT", "STAY"
"""

    # Get response from vision model
    response = chat_completion_with_vision(prompt, image_path=screenshot_path)
    print("✅ BGE: Vision-based navigation analysis completed")
    print(f"🔍 BGE: VLM Response → {response[:300]}...")  # Show first 300 chars
    print(f"📏 BGE: Full response length: {len(response)} characters")

    # Validate response using few-shot validation
    if few_shot_system:
        from backend.app.llm.few_shot_navigation import validate_json_response
        is_valid, result = validate_json_response(response)
        if not is_valid:
            print(f"⚠️ Invalid JSON response: {result}")
            print("🔄 Retrying with stricter prompt...")
            
            # Retry with stricter prompt
            retry_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no extra text."
            response = chat_completion_with_vision(retry_prompt, image_path=screenshot_path)
            is_valid, result = validate_json_response(response)
            
            if not is_valid:
                print(f"❌ Retry failed: {result}")
                # Return safe fallback
                return {
                    "current_room": "UNKNOWN",
                    "furniture_visible": [],
                    "task_complete": False,
                    "movement_sequence": ["STAY"],
                    "reasoning": "JSON parsing failed, staying put for safety"
                }
        
        print("✅ JSON validation passed")
        
        # Anti-oscillation check
        sequence = result["movement_sequence"]
        if len(sequence) == 1 and hasattr(bge.logic, 'last_move'):
            current_move = sequence[0]
            last_move = bge.logic.last_move
            
            # Detect left-right or up-down oscillation
            oscillation_pairs = [("LEFT", "RIGHT"), ("RIGHT", "LEFT"), ("UP", "DOWN"), ("DOWN", "UP")]
            if (last_move, current_move) in oscillation_pairs:
                print(f"⚠️ BGE: Oscillation detected: {last_move} → {current_move}, forcing alternative")
                # Choose a different direction or STAY
                valid_moves = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
                alternatives = [m for m in valid_moves if m not in [last_move, current_move]]
                if alternatives:
                    result["movement_sequence"] = [alternatives[0]]
                else:
                    result["movement_sequence"] = ["STAY"]
        
        bge.logic.last_move = result["movement_sequence"][0] if result["movement_sequence"] else "STAY"
        return result
    
    # Original parsing logic (fallback)
    try:
        # Try to find JSON in the response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            print("❌ BGE: No JSON boundaries found")
            return None
            
        json_str = response[json_start:json_end]
        
        if not json_str.strip():
            print("❌ BGE: No JSON string extracted from response")
            print(f"🔍 BGE: FULL VLM RESPONSE DEBUG:")
            print(f"'{response}'")
            raise Exception(f"❌ Vision analysis failed - see debug output above")
        
        try:
            result = json.loads(json_str)
            print("✅ BGE: JSON parsed successfully")
            
            # Validate required fields and fix issues
            if "movement_sequence" in result and isinstance(result["movement_sequence"], list):
                # Clean and validate movement sequence
                raw_sequence = result["movement_sequence"]
                valid_moves = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
                
                # Filter to only valid moves
                clean_sequence = []
                for move in raw_sequence:
                    if isinstance(move, str):
                        move_upper = move.upper().strip()
                        if move_upper in valid_moves:
                            clean_sequence.append(move_upper)
                        else:
                            print(f"⚠️ BGE: Invalid move '{move}' filtered out")
                
                # Limit to maximum 2 moves
                if len(clean_sequence) > 2:
                    print(f"⚠️ BGE: Truncating {len(clean_sequence)} moves to 2")
                    clean_sequence = clean_sequence[:2]
                elif len(clean_sequence) == 0:
                    print(f"⚠️ BGE: No valid moves found, defaulting to STAY")
                    clean_sequence = ["STAY"]
                
                sequence = clean_sequence
                print(f"🔍 BGE: Final movement sequence: {sequence}")
                
                # Anti-oscillation check
                if len(sequence) == 1 and hasattr(bge.logic, 'last_move'):
                    current_move = sequence[0]
                    last_move = bge.logic.last_move
                    
                    # Detect left-right or up-down oscillation
                    oscillation_pairs = [("LEFT", "RIGHT"), ("RIGHT", "LEFT"), ("UP", "DOWN"), ("DOWN", "UP")]
                    if (last_move, current_move) in oscillation_pairs:
                        print(f"⚠️ BGE: Oscillation detected: {last_move} → {current_move}, forcing alternative")
                        # Choose a different direction or STAY
                        alternatives = [m for m in valid_moves if m not in [last_move, current_move]]
                        if alternatives:
                            sequence = [alternatives[0]]
                        else:
                            sequence = ["STAY"]
                
                bge.logic.last_move = sequence[0] if sequence else "STAY"
                
                return {
                        "movement_sequence": sequence, 
                        "current_room": result.get("current_room", "UNKNOWN"),
                        "furniture_visible": result.get("furniture_visible", []),
                        "task_complete": result.get("task_complete", False),
                        "reasoning": result.get("reasoning", "Navigation analysis completed")
                    }
            else:
                print(f"❌ BGE: Missing or invalid movement_sequence in result: {list(result.keys())}")
                if "task_complete" in result and result["task_complete"]:
                    return {
                            "movement_sequence": ["STAY"], 
                            "current_room": result.get("current_room", "UNKNOWN"),
                            "furniture_visible": result.get("furniture_visible", []),
                            "task_complete": True,
                            "reasoning": result.get("reasoning", "Task marked complete")
                        }
                
                print(f"❌ BGE: Missing or invalid movement_sequence in result: {list(result.keys())}")
                raise Exception(f"❌ Vision analysis failed - see debug output above")
                
        except json.JSONDecodeError as e:
            print(f"❌ BGE: JSON decode error: {e}")
            print(f"🔍 BGE: Attempted to parse: '{json_str[:200]}...'")
            raise Exception(f"❌ Vision analysis failed - see debug output above")
            
    except Exception as e:
        print(f"❌ BGE: VLM analysis error: {e}")
        raise Exception(f"❌ Vision analysis failed - see debug output above")
