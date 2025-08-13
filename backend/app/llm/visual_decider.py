from __future__ import annotations
import json
from typing import Dict, Any, List, Optional
from .client import chat_completion

VISION_SYSTEM_PROMPT = """You are a navigation AI for a virtual character in an OPEN-TOP HOUSE simulation.

🏠 OPEN-TOP DESIGN ADVANTAGE: No ceilings obstruct the perfect bird's-eye view!

The character has ENHANCED VISUAL MARKERS for guaranteed identification:
🔴 BRIGHT RED GLOWING FIGURE = The character you must control (emits intense red light)
🟡 YELLOW FLOATING MARKER = Height indicator above character
🟢 GREEN GLOWING CIRCLE = Ground position marker below character

PERFECT VISIBILITY: The open-top house design eliminates ALL visual obstruction!
The bright red character is impossible to miss against the clear, unobstructed view.

You will receive:
1. Crystal-clear bird's-eye view image (no ceiling interference)
2. The character's exact position coordinates
3. A list of tasks to complete
4. Room locations and layout

Your job: Analyze the perfect visual scene and decide the next movement step.

IMPORTANT RULES:
- The BRIGHT RED GLOWING object is your character - impossible to miss!
- Return STRICT JSON only, no markdown or explanations
- Move ONE step at a time toward the target room
- The open-top design gives you perfect visibility of all obstacles
- direction must be exactly one of: "UP", "DOWN", "LEFT", "RIGHT", "STAY"
- Always mention the red character in your reasoning
- Mark task_complete=true only when character reaches the target room

JSON Response Format:
{
  "direction": "UP|DOWN|LEFT|RIGHT|STAY",
  "room": "<target_room_name>",
  "reasoning": "Perfect visibility shows the bright red character at [position]. Open-top design reveals [analysis]. Moving [direction] toward [goal]...",
  "task_complete": false,
  "next_action": "<optional: device interaction>"
}
"""

def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown and extra text."""
    text = text.strip()
    
    # Remove markdown code blocks if present
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
    
    try:
        return json.loads(text)
    except Exception:
        pass
    
    # Fallback: find JSON object boundaries
    i, j = text.find("{"), text.rfind("}")
    if i >= 0 and j > i:
        try:
            return json.loads(text[i:j+1])
        except Exception:
            pass
    
    raise ValueError("No valid JSON found in LLM response")

def _validate_decision(decision: dict, rooms: Dict[str, Any]) -> dict:
    """Validate and sanitize the LLM decision."""
    
    # Ensure required fields
    direction = str(decision.get("direction", "STAY")).upper()
    if direction not in ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]:
        direction = "STAY"
    
    room = decision.get("room")
    if not room or room not in rooms:
        room = list(rooms.keys())[0] if rooms else "Kitchen"
    
    reasoning = decision.get("reasoning", "Visual navigation decision")
    task_complete = bool(decision.get("task_complete", False))
    next_action = decision.get("next_action")
    
    return {
        "direction": direction,
        "room": room,
        "reasoning": reasoning,
        "task_complete": task_complete,
        "next_action": next_action
    }

def _create_visual_prompt(tasks: List[str], actor_position: Dict[str, float], 
                         rooms: Dict[str, Any], last_room: Optional[str], step_count: int) -> str:
    """Create the enhanced visual prompt with clear marker guidance."""
    
    tasks_str = ", ".join(tasks)
    pos_str = f"({actor_position.get('x', 0):.2f}, {actor_position.get('y', 0):.2f})"
    
    # Calculate room distances for context
    room_distances = []
    actor_pos = [actor_position.get('x', 0), actor_position.get('y', 0)]
    for name, data in rooms.items():
        center = data.get('center', [0, 0])
        distance = abs(center[0] - actor_pos[0]) + abs(center[1] - actor_pos[1])
        room_distances.append(f"- {name}: {distance:.1f} units away (center at {center[0]}, {center[1]})")
    
    return f"""🎯 ENHANCED VISUAL NAVIGATION REQUEST

## CURRENT TASK: {tasks_str}

## CHARACTER STATUS:
- Position: {pos_str}
- Last Room: {last_room or "Starting area"}  
- Step: {step_count + 1}/50

## 🔍 VISUAL MARKERS TO FIND:
Look for these BRIGHT, GLOWING objects in the bird's-eye image:

🔴 **BRIGHT RED GLOWING FIGURE** = The CHARACTER you must move
   - Emits bright red light, stands out from everything else
   - This is the actor that needs to navigate to complete tasks

🟡 **YELLOW FLOATING MARKER** = Above the red character
   - Confirms character location from top-down view
   - Floats 2.5 units above the red figure

🟢 **GREEN GLOWING CIRCLE** = Ground position marker  
   - Shows exact floor position beneath red character
   - Marks where the character is standing

## AVAILABLE ROOMS & DISTANCES:
{chr(10).join(room_distances)}

## NAVIGATION INSTRUCTIONS:
1. **LOCATE**: Find the bright red glowing character in the image
2. **ANALYZE**: Identify walls, obstacles, and room boundaries
3. **TARGET**: Determine which room is needed for the current task
4. **DECIDE**: Choose direction (UP/DOWN/LEFT/RIGHT) that moves red character closer
5. **CONFIRM**: Will this move help complete the task?

## MOVEMENT DIRECTIONS:
- UP: Move north (positive Y)
- DOWN: Move south (negative Y)  
- LEFT: Move west (negative X)
- RIGHT: Move east (positive X)
- STAY: Don't move (if already at target or obstacle ahead)

The scene has 500+ objects but the RED CHARACTER is impossible to miss!
Focus on moving the glowing red figure toward the target room."""

def decide_with_vision(tasks: List[str], actor_position: Dict[str, float], 
                      rooms: Dict[str, Any], bird_eye_b64: str,
                      last_room: Optional[str] = None, step_count: int = 0) -> Dict[str, Any]:
    """
    Make navigation decision using visual LLM analysis.
    
    Args:
        tasks: List of tasks to complete
        actor_position: Current character position {"x": float, "y": float}
        rooms: Room definitions with centers
        bird_eye_b64: Base64 encoded bird's-eye view image
        last_room: Previously visited room
        step_count: Number of steps taken so far
    
    Returns:
        Navigation decision dictionary
    """
    
    user_prompt = _create_visual_prompt(tasks, actor_position, rooms, last_room, step_count)
    
    try:
        # For now, we'll use text-only LLM since vision models need special handling
        # In production, you'd use GPT-4V, Claude 3, or similar vision model
        raw_response = chat_completion(VISION_SYSTEM_PROMPT, user_prompt)
        
        decision = _extract_json(raw_response)
        return _validate_decision(decision, rooms)
        
    except Exception as e:
        print(f"Visual decision error: {e}")
        # Fallback to heuristic navigation
        return _heuristic_navigation(tasks, actor_position, rooms, last_room)

def _heuristic_navigation(tasks: List[str], actor_position: Dict[str, float], 
                         rooms: Dict[str, Any], last_room: Optional[str]) -> Dict[str, Any]:
    """Fallback navigation when LLM fails."""
    
    task_text = " ".join(tasks).lower()
    
    # Determine target room based on task
    if "coffee" in task_text and "Kitchen" in rooms:
        target_room = "Kitchen"
    elif any(word in task_text for word in ["light", "tv", "living"]) and "LivingRoom" in rooms:
        target_room = "LivingRoom"
    elif "sleep" in task_text and "Bedroom" in rooms:
        target_room = "Bedroom"
    else:
        # Default to first available room
        target_room = list(rooms.keys())[0] if rooms else "Kitchen"
    
    # Calculate direction to target
    target_center = rooms[target_room]["center"]
    dx = target_center[0] - actor_position.get("x", 0)
    dy = target_center[1] - actor_position.get("y", 0)
    
    # Check if already at target
    if abs(dx) < 0.3 and abs(dy) < 0.3:
        return {
            "direction": "STAY",
            "room": target_room,
            "reasoning": f"Reached {target_room} - task area",
            "task_complete": True,
            "next_action": "interact_with_objects"
        }
    
    # Choose primary movement direction
    if abs(dx) >= abs(dy):
        direction = "RIGHT" if dx > 0 else "LEFT"
    else:
        direction = "UP" if dy > 0 else "DOWN"
    
    return {
        "direction": direction,
        "room": target_room,
        "reasoning": f"Heuristic navigation toward {target_room}",
        "task_complete": False,
        "next_action": None
    }
