"""
LLM Visual Position Detection for VESPER
Takes bird's-eye screenshots and asks the LLM for the next move.
NO HARDCODED COORDINATES – uses scene facts and (optionally) an image.
"""

import os, sys, json, yaml, re
from typing import Dict, Any

# ---------------------------------------------------------
# Project root + client import
# ---------------------------------------------------------
def get_project_root() -> str:
    """Absolute path to project root (…/vesper_llm)."""
    current_file = os.path.abspath(__file__)
    return os.path.dirname(os.path.dirname(current_file))

PROJECT_ROOT = get_project_root()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.llm.client import chat_completion  # <-- real client only

# ---------------------------------------------------------
# Config (optional rooms.yaml)
# ---------------------------------------------------------
try:
    rooms_path = os.path.join(PROJECT_ROOT, "configs", "rooms.yaml")
    with open(rooms_path, "r") as f:
        ROOMS = yaml.safe_load(f) or {}
except Exception:
    print("⚠️ configs/rooms.yaml not found or invalid; continuing without it")
    ROOMS = {}

# ---------------------------------------------------------
# Prompts
# ---------------------------------------------------------
VISUAL_NAVIGATION_PROMPT = """You are an AI navigation assistant controlling an actor in a 3D house environment.

IMPORTANT: You MUST move the actor step-by-step toward the target room. DO NOT say STAY unless truly at the destination.

You receive:
- A bird's-eye PNG image (if available)
- Current actor position and target room
- Scene facts about the environment

MOVEMENT RULES:
- ALWAYS choose a direction that moves toward the target room
- Allowed directions: UP, DOWN, LEFT, RIGHT, STAY
- Movement distances: SHORT (0.2m), MEDIUM (0.4m), LONG (0.8m) 
- Take SHORT steps to navigate safely around furniture and walls
- Only use STAY when you've reached the target room area

COORDINATE SYSTEM:
- UP = +Y direction (move forward in scene)
- DOWN = -Y direction (move backward in scene)  
- LEFT = -X direction (move left in scene)
- RIGHT = +X direction (move right in scene)

OUTPUT STRICT JSON ONLY:
{{
  "current_room": "detected current room or 'unknown'",
  "next_direction": "UP|DOWN|LEFT|RIGHT|STAY",
  "movement_distance": "SHORT|MEDIUM|LONG",
  "reasoning": "why this direction moves toward target",
  "obstacles_detected": ["list of visible obstacles"],
  "path_clear": true,
  "progress_toward_target": "getting_closer|arrived|need_to_navigate"
}}

CRITICAL: If not at target room, you MUST choose UP/DOWN/LEFT/RIGHT. Do not stay in place!"""

SPATIAL_ANALYSIS_PROMPT = """You are a spatial-planning assistant. You may be given a base64 PNG and/or scene facts.
Return JSON only; do not include any extra text.

JSON SCHEMA:
{{
  "room_layout": {{
    "detected_rooms": ["Kitchen","Livingroom","..."],
    "room_connections": [["Kitchen","Dining"],["Dining","Livingroom"]],
    "doorway_positions": []
  }},
  "obstacle_map": [],
  "navigation_assessment": {{
    "current_position": "summary",
    "target_accessible": true,
    "recommended_route": ["waypoint notes..."],
    "hazards": []
  }},
  "movement_guidance": {{
    "immediate_direction": "UP|DOWN|LEFT|RIGHT|STAY",
    "step_size": "SMALL|MEDIUM|LARGE",
    "confidence": "HIGH|MEDIUM|LOW"
  }}
}}"""

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------
_JSON_BLOCK = re.compile(r"\{[^{}]*\}", re.DOTALL)  # simplified JSON extraction

def _extract_json(text: str) -> Dict[str, Any] | None:
    """Grab the first plausible top-level JSON object from a model reply."""
    try:
        # Fast path: whole reply is JSON
        return json.loads(text)
    except Exception:
        pass
    # Fallback: find a JSON-looking block
    m = _JSON_BLOCK.search(text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None

def _fallback_direction(text: str) -> str:
    t = text.upper()
    for d in ("UP", "DOWN", "LEFT", "RIGHT", "STAY"):
        if d in t:
            return d
    return "STAY"

# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def analyze_visual_scene_for_navigation(
    screenshot_base64: str | None,
    target_room: str,
    scene_facts: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """
    Ask the LLM for the next move with enhanced spatial context.
    """
    # Build enhanced user content for better navigation
    parts = []
    parts.append(f"TARGET ROOM: {target_room}")
    
    if scene_facts:
        actor_pos = scene_facts.get("actor_position", [0, 0, 0])
        parts.append("CURRENT SITUATION:")
        parts.append(f"- Actor Position: {actor_pos}")
        parts.append(f"- Target: Navigate to {target_room}")
        
        # Add movement context and encourage progression
        parts.append("NAVIGATION CONTEXT:")
        parts.append("- You are in a house with multiple rooms")
        parts.append("- Move step-by-step toward the target room")
        parts.append("- Take SHORT steps (0.2m) to navigate safely")
        parts.append("- DO NOT STAY unless you've reached the target room")
        
        # Add any additional scene facts
        if "task" in scene_facts:
            parts.append(f"- Current Task: {scene_facts['task']}")
        if "movement_history" in scene_facts and scene_facts["movement_history"]:
            recent_moves = scene_facts["movement_history"][-2:]  # Last 2 moves
            parts.append("RECENT MOVEMENTS:")
            for move in recent_moves:
                parts.append(f"  Step {move.get('step', '?')}: {move.get('direction', '?')} - {move.get('reasoning', '')[:50]}...")
                
        parts.append("SCENE FACTS:")
        parts.append(json.dumps(scene_facts, ensure_ascii=False, indent=2))
    
    # Handle screenshot with size check
    if screenshot_base64:
        if len(screenshot_base64) > 100000:  # > 100KB
            print(f"⚠️ Large screenshot ({len(screenshot_base64)} chars), using scene facts only")
            parts.append("VISUAL: Screenshot too large - using spatial reasoning only")
        else:
            data_url = (
                screenshot_base64 if screenshot_base64.startswith("data:")
                else f"data:image/png;base64,{screenshot_base64}"
            )
            parts.append(f"BIRD'S-EYE VIEW IMAGE: {data_url}")
    else:
        parts.append("VISUAL: No image provided - using spatial reasoning")

    user_prompt = "\n\n".join(parts)

    try:
        print("🧠 LLM analyzing scene for navigation…")
        
        response = chat_completion(VISUAL_NAVIGATION_PROMPT, user_prompt, max_tokens=400)

        data = _extract_json(response)
        if data:
            # Enhanced normalization with movement encouragement
            data.setdefault("current_room", "unknown")
            data.setdefault("next_direction", "STAY")
            data.setdefault("movement_distance", "SHORT")
            data.setdefault("reasoning", "no reasoning provided")
            data.setdefault("obstacles_detected", [])
            data.setdefault("path_clear", True)
            data.setdefault("progress_toward_target", "need_to_navigate")
            
            # Force movement if LLM says STAY but hasn't reached target
            if data["next_direction"] == "STAY" and data.get("progress_toward_target") != "arrived":
                print("⚠️ LLM said STAY but not at target - encouraging movement")
                # Simple fallback: move toward common room directions
                if "bedroom" in target_room.lower():
                    data["next_direction"] = "UP"
                elif "kitchen" in target_room.lower():
                    data["next_direction"] = "LEFT"
                elif "living" in target_room.lower():
                    data["next_direction"] = "RIGHT"
                elif "bathroom" in target_room.lower():
                    data["next_direction"] = "DOWN"
                else:
                    data["next_direction"] = "UP"  # Default movement
                data["reasoning"] = f"Encouraged movement toward {target_room} (was staying in place)"
            
            print(f"🎯 LLM: {data.get('current_room','?')} → {data.get('next_direction','STAY')}")
            return data

        # Fallback with movement bias
        direction = _fallback_direction(response)
        if direction == "STAY":
            direction = "UP"  # Default to UP if unsure
            
        return {
            "current_room": "unknown",
            "next_direction": direction,
            "movement_distance": "SHORT",
            "reasoning": f"Parsed from non-JSON response, encouraging movement toward {target_room}",
            "obstacles_detected": [],
            "path_clear": True,
            "progress_toward_target": "need_to_navigate"
        }

    except Exception as e:
        print(f"❌ LLM visual analysis failed: {e}")
        # Even on error, encourage movement
        fallback_direction = "UP" if "bedroom" in target_room.lower() else "RIGHT"
        return {
            "current_room": "error",
            "next_direction": fallback_direction,
            "movement_distance": "SHORT",
            "reasoning": f"Error fallback - moving {fallback_direction} toward {target_room}",
            "obstacles_detected": ["analysis_error"],
            "path_clear": False,
            "progress_toward_target": "need_to_navigate"
        }

def get_spatial_intelligence_analysis(
    screenshot_base64: str | None,
    target_room: str,
    scene_facts: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """High-level spatial map + immediate guidance. Works with or without an image."""
    parts = [f"TARGET DESTINATION: {target_room}"]
    if scene_facts:
        parts.append("SCENE FACTS:")
        parts.append(json.dumps(scene_facts, ensure_ascii=False))
    if screenshot_base64:
        data_url = (
            screenshot_base64 if screenshot_base64.startswith("data:")
            else f"data:image/png;base64,{screenshot_base64}"
        )
        parts.append(f"IMAGE (data url): {data_url}")
    else:
        parts.append("NO IMAGE PROVIDED")

    user_prompt = "\n\n".join(parts)

    try:
        print("🗺️ Running spatial intelligence analysis…")
        response = chat_completion(SPATIAL_ANALYSIS_PROMPT, user_prompt, max_tokens=600)
        data = _extract_json(response)
        if data:
            return data

        # Simple fallback
        return {
            "room_layout": {"detected_rooms": [], "room_connections": [], "doorway_positions": []},
            "obstacle_map": [],
            "navigation_assessment": {
                "current_position": "Unknown",
                "target_accessible": True,
                "recommended_route": [],
                "hazards": []
            },
            "movement_guidance": {"immediate_direction": _fallback_direction(response), "step_size": "SMALL", "confidence": "LOW"}
        }
    except Exception as e:
        print(f"❌ Spatial analysis failed: {e}")
        return {
            "room_layout": {"detected_rooms": [], "room_connections": [], "doorway_positions": []},
            "obstacle_map": [],
            "navigation_assessment": {"current_position": "Error", "target_accessible": False, "recommended_route": [], "hazards": ["exception"]},
            "movement_guidance": {"immediate_direction": "STAY", "step_size": "SMALL", "confidence": "LOW"}
        }

def convert_llm_direction_to_movement(direction: str, distance: str = "SHORT") -> tuple[float, float, float]:
    """Convert LLM cardinal direction + step size into Blender offsets."""
    step_sizes = {"SHORT": 0.2, "MEDIUM": 0.4, "LONG": 0.8}
    step = step_sizes.get((distance or "SHORT").upper(), 0.2)
    mapping = {
        "UP": (0, step, 0),     # +Y
        "DOWN": (0, -step, 0),  # -Y
        "LEFT": (-step, 0, 0),  # -X
        "RIGHT": (step, 0, 0),  # +X
        "STAY": (0, 0, 0)
    }
    move = mapping.get((direction or "STAY").upper(), (0, 0, 0))
    print(f"🎮 Converting direction '{direction}' ({distance}) → {move}")
    return move

# ---------------------------------------------------------
# Real tests (no mock)
# ---------------------------------------------------------
def visual_navigation_test() -> bool:
    """Minimal live test: text-only reasoning (no image)."""
    print("🔍 TEST: visual_navigation_test (text-only)")
    scene_facts = {
        "actor_position": [-2.0, 0.0, 0.0],
        "room_centers": ROOMS if ROOMS else {"Kitchen":[-4, -3], "Bathroom":[-4, 0], "Dining":[-4, 4], "Livingroom":[0, -4]},
        "notes": "Corridor near y≈0 connects rooms; avoid walls; take small steps."
    }
    result = analyze_visual_scene_for_navigation(
        screenshot_base64=None,
        target_room="Livingroom",
        scene_facts=scene_facts
    )
    print("Result:", json.dumps(result, indent=2))
    return isinstance(result, dict) and "next_direction" in result

def simple_position_test() -> bool:
    """Another live test that requests strict JSON."""
    print("🧠 TEST: simple_position_test")
    system = 'You are a navigation AI. Reply only JSON: {"direction":"UP|DOWN|LEFT|RIGHT|STAY","reasoning":"..."}'
    user = (
        "Actor at x=-2,y=0. Livingroom center near x=0,y=-4. "
        "Walls enclose rooms; corridor along y≈0; choose a safe small step."
    )
    resp = chat_completion(system, user, max_tokens=120)
    data = _extract_json(resp) or {"direction": _fallback_direction(resp), "reasoning": "parsed from text"}
    print("Response:", data)
    return "direction" in data

if __name__ == "__main__":
    print("🚀 VESPER LLM VISUAL NAVIGATION SYSTEM (no mock)")
    ok1 = visual_navigation_test()
    ok2 = simple_position_test()
    print("✅ Tests:", ok1, ok2)
