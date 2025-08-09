
from typing import Dict, Any

DEVICE_STATE: Dict[str, Dict[str, Any]] = {
    "living_light_1": {"type": "light", "room": "LivingRoom", "on": True, "brightness": 0.8},
    "coffee_maker_1": {"type": "switch", "room": "Kitchen", "on": False},
}

def apply_action(device_id: str, op: str):
    dev = DEVICE_STATE.get(device_id)
    if not dev:
        return False, f"device {device_id} not found"
    op = op.upper()
    if op == "ON":
        dev["on"] = True
        return True, f"{device_id} turned ON"
    if op == "OFF":
        dev["on"] = False
        return True, f"{device_id} turned OFF"
    return False, f"unsupported op {op}"
