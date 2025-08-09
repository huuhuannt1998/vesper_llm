from __future__ import annotations
import json
from typing import Dict, Any, List, Optional
from .client import chat_completion

SYSTEM = """You are a navigation module for a top-down house sim.
Return STRICT JSON only. No prose. Keys: room, direction.
direction ∈ ["UP","DOWN","LEFT","RIGHT","STAY"].
Pick the room where the next task progress should happen, then a single-step direction from the actor's coordinates toward that room center (grid-like motion)."""

TEMPLATE = """
STATE:
- Tasks: {tasks}
- Actor: {actor}
- Rooms: {rooms}
- LastRoom: {last_room}
- BirdEyeBase64Present: {has_img}

Rules:
1) Choose the room that helps progress the current tasks (lights → LivingRoom, coffee → Kitchen, etc.).
2) Compute the primary axis from actor to that room's center; output one of: UP/DOWN/LEFT/RIGHT (single step).
3) If already near the target (<0.2m), use STAY.

Return JSON ONLY:
{{"room":"<RoomName>","direction":"UP|DOWN|LEFT|RIGHT|STAY"}}
"""

def _extract_json(text: str) -> dict:
    text = text.strip()
    try: return json.loads(text)
    except Exception: pass
    i, j = text.find("{"), text.rfind("}")
    if i >= 0 and j > i: return json.loads(text[i:j+1])
    raise ValueError("No JSON")

def _heuristic(tasks, actor, rooms, last_room):
    # Simple fallback: go toward Kitchen for coffee, LivingRoom for lights, else nearest
    tx = " ".join(tasks).lower()
    target = None
    if "coffee" in tx and "Kitchen" in rooms: target = "Kitchen"
    elif ("light" in tx or "tv" in tx) and "LivingRoom" in rooms: target = "LivingRoom"
    else:
        # nearest by L1
        ax, ay = actor["x"], actor["y"]
        target = min(rooms, key=lambda r: abs(ax-rooms[r]["center"][0]) + abs(ay-rooms[r]["center"][1]))
    cx, cy = rooms[target]["center"]
    dx, dy = cx-actor["x"], cy-actor["y"]
    if abs(dx) < 0.2 and abs(dy) < 0.2:
        direction = "STAY"
    elif abs(dx) >= abs(dy):
        direction = "RIGHT" if dx > 0 else "LEFT"
    else:
        direction = "UP" if dy > 0 else "DOWN"
    return {"room": target, "direction": direction}

def decide_next(tasks: List[str], actor: Dict[str,float], rooms: Dict[str, Any], last_room: Optional[str], bird_eye_b64: Optional[str]):
    user = TEMPLATE.format(
        tasks=tasks,
        actor=actor,
        rooms=rooms,
        last_room=last_room or "None",
        has_img="yes" if bird_eye_b64 else "no"
    )
    try:
        raw = chat_completion(SYSTEM, user)
        data = _extract_json(raw)
        # validate
        room = data.get("room"); direction = str(data.get("direction","")).upper()
        if room not in rooms or direction not in ["UP","DOWN","LEFT","RIGHT","STAY"]:
            raise ValueError("bad values")
        return {"room": room, "direction": direction}
    except Exception:
        return _heuristic(tasks, actor, rooms, last_room)
