
# Attach this to an Always sensor (true level triggering) → Python module: game.actor_controller.update
try:
    from bge import logic
    from mathutils import Vector
except Exception:
    logic = None
    class Vector:
        def __init__(self, xy): pass

from .device_sync import BRIDGE

state = {"initialized": False, "plan": None, "step_idx": 0}

def on_bus(msg):
    if msg.get("event") == "new_plan":
        state["plan"] = msg["plan"]
        state["step_idx"] = 0

def init():
    if not state["initialized"]:
        if not BRIDGE.thread: BRIDGE.start()
        BRIDGE.on_message = on_bus
        state["initialized"] = True

def move_toward(obj, target_xy, speed=0.05):
    pos = obj.worldPosition.xy if hasattr(obj.worldPosition, "xy") else obj.worldPosition
    tgt = Vector((target_xy[0], target_xy[1]))
    d = tgt - Vector((pos[0], pos[1]))
    if d.length < 0.05: return True
    step = d.normalized() * speed
    obj.worldPosition.x += step.x
    obj.worldPosition.y += step.y
    return False

def update():
    if logic is None:
        return
    cont = logic.getCurrentController()
    own = cont.owner
    init()

    if not state["plan"]: 
        return

    steps = state["plan"]["steps"]
    if state["step_idx"] >= len(steps):
        return

    step = steps[state["step_idx"]]
    wp = step["waypoints"][0]
    arrived = move_toward(own, wp)

    if arrived:
        BRIDGE.send({"event":"actor_progress","status":"arrived","step_index":state["step_idx"]})
        for act in step.get("actions", []):
            BRIDGE.send({"event":"device_action",
                         "device_id": act.get("target_device_id"),
                         "op": act.get("op")})
        state["step_idx"] += 1
