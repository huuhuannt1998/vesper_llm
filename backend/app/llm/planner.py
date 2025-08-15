
from __future__ import annotations
import json, yaml, os
from typing import Dict, Any, List
from .client import chat_completion

# Get the project root directory
def get_project_root():
    """Get the absolute path to the project root directory."""
    current_file = os.path.abspath(__file__)
    # Navigate from backend/app/llm/planner.py to project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
    return project_root

PROJECT_ROOT = get_project_root()

# Load configuration files with absolute paths
try:
    rooms_path = os.path.join(PROJECT_ROOT, "configs", "rooms.yaml")
    devices_path = os.path.join(PROJECT_ROOT, "configs", "devices.yaml")
    
    ROOMS = yaml.safe_load(open(rooms_path, "r", encoding="utf-8"))
    DEVICES = yaml.safe_load(open(devices_path, "r", encoding="utf-8"))
except FileNotFoundError as e:
    print(f"Configuration file not found: {e}")
    # Fallback configuration
    ROOMS = {
        "Kitchen": {"center": [3.0, -1.0]},
        "LivingRoom": {"center": [-2.0, 1.5]},
        "Bedroom": {"center": [-3.0, -2.0]},
        "Bathroom": {"center": [1.0, 3.0]}
    }
    DEVICES = {}

SYSTEM_PROMPT = """You are a planning module for a home simulation.
You must output ONLY a JSON object that conforms to the schema shown in the user message.
Do not include any prose or code fences. No explanations—JSON only.
"""

SCHEMA_BLOCK = """
Return a JSON object:

{
  "steps": [
    {
      "room": "<NameOfRoom, exact match from ROOMS>",
      "waypoints": [[x, y], ...],
      "actions": [
        {
          "type": "interact",
          "target_device_id": "<id from DEVICES map>",
          "op": "ON" | "OFF"
        }
      ]
    }
  ]
}

Rules:
- Rooms MUST be chosen from ROOMS keys.
- target_device_id MUST be a key from DEVICES.
- waypoints MUST be realistic positions inside the chosen room.
- If the natural task doesn't need an action in some room, you may still include a waypoint-only step.
- If no device action is implied, return a single step to the most relevant room and an empty actions list.
"""

def _build_user_prompt(natural_text: str, context: Dict[str, Any]) -> str:
    rooms_str = json.dumps(ROOMS, indent=2)
    devices_str = json.dumps(DEVICES, indent=2)
    ctx_str = json.dumps(context or {}, indent=2)
    return f"""You convert natural tasks into a stepwise plan.

NATURAL_TASK:
{natural_text}

CONTEXT:
{ctx_str}

ROOMS (dictionary):
{rooms_str}

DEVICES (dictionary):
{devices_str}

{SCHEMA_BLOCK}
"""

def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m_open = text.find("{")
    m_close = text.rfind("}")
    if m_open != -1 and m_close != -1 and m_close > m_open:
        candidate = text[m_open:m_close+1]
        return json.loads(candidate)
    raise ValueError("LLM did not return valid JSON")

def _validate_and_repair(plan: Dict[str, Any]) -> Dict[str, Any]:
    steps = plan.get("steps") or []
    valid_steps: List[Dict[str, Any]] = []
    for s in steps:
        room = s.get("room")
        if room not in ROOMS:
            continue
        wps = s.get("waypoints") or []
        if not isinstance(wps, list) or not wps:
            wps = [ROOMS[room].get("center", [0.0, 0.0])]
        acts = []
        for a in s.get("actions") or []:
            if a.get("type") != "interact":
                continue
            dev_id = a.get("target_device_id")
            if dev_id not in DEVICES:
                continue
            op = str(a.get("op", "")).upper()
            if op not in ("ON", "OFF"):
                continue
            acts.append({"type": "interact", "target_device_id": dev_id, "op": op})
        valid_steps.append({"room": room, "waypoints": wps, "actions": acts})
    if not valid_steps:
        # fallback: first room center
        first_room = next(iter(ROOMS.keys()))
        valid_steps = [{"room": first_room, "waypoints": [ROOMS[first_room].get("center", [0.0, 0.0])], "actions": []}]
    return {"steps": valid_steps}

def _heuristic_fallback(natural_text: str) -> Dict[str, Any]:
    tx = natural_text.lower()
    steps: List[Dict[str, Any]] = []
    def room_step(room_name, actions):
        center = ROOMS.get(room_name, {}).get("center", [0.0, 0.0])
        return {"room": room_name, "waypoints": [center], "actions": actions}
    if "coffee" in tx and "coffee_maker_1" in DEVICES:
        steps.append(room_step("Kitchen", [{"type":"interact","target_device_id":"coffee_maker_1","op":"ON"}]))
    if ("living" in tx or "living room" in tx) and "living_light_1" in DEVICES:
        steps.append(room_step("LivingRoom", [{"type":"interact","target_device_id":"living_light_1","op":"OFF"}]))
    if not steps:
        steps.append(room_step(next(iter(ROOMS.keys())), []))
    return {"steps": steps}

def plan_tasks(natural_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
    user = _build_user_prompt(natural_text, context)
    try:
        raw = chat_completion(SYSTEM_PROMPT, user)
        plan = _extract_json(raw)
        plan = _validate_and_repair(plan)
        return plan
    except Exception:
        return _validate_and_repair(_heuristic_fallback(natural_text))
