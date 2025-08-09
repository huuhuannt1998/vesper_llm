# Attach this to an Always sensor (pulse/true level) on your Actor:
# Logic Editor → Always (true level) → Python module: game.actor_controller.update

import os, time, json, base64
from mathutils import Vector

# Use stdlib HTTP so you don't need extra deps inside UPBGE
import urllib.request

# ---- Config (override via environment if needed) ----
BACKEND_URL        = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")  # FastAPI root
STEP_SIZE          = float(os.getenv("STEP_SIZE", "0.25"))               # meters per tick
TICK_SECS          = float(os.getenv("TICK_SECS", "0.25"))               # seconds between decisions
CAPTURE_BIRDEYE    = os.getenv("CAPTURE_BIRDEYE", "1") not in ("0","false","False")
DEBUG_AI_TICKS     = os.getenv("DEBUG_AI_TICKS", "1") not in ("0","false","False")
MAX_BIRDEYE_BYTES  = int(os.getenv("MAX_BIRDEYE_BYTES", "200000"))  # safety cap (~200 KB)

# Default tasks for quick testing (you can override from Python console or another script)
DEFAULT_TASKS = ["Make coffee", "Turn off living room lights"]

try:
    from bge import logic, render
except Exception:
    logic = None  # allows import outside UPBGE for linting

# Optional WS bridge (safe if not running)
try:
    from .device_sync import BRIDGE
except Exception:
    BRIDGE = None

state = {
    "last_tick": 0.0,
    "last_room": None,
    "tasks": DEFAULT_TASKS[:],
    "tick_count": 0,
}

def _debug(msg: str):
    if DEBUG_AI_TICKS:
        try:
            print(f"[actor_controller] {msg}")
        except Exception:
            pass

def _encode_birdeye_png_b64() -> str | None:
    """
    Capture the current viewport to PNG and return base64 string.
    Works while the game is running (Play).
    """
    if logic is None or not CAPTURE_BIRDEYE:
        return None
    tmp_path = os.path.join(logic.expandPath("//"), "_birdeye.png")
    try:
        render.makeScreenshot(tmp_path)
        with open(tmp_path, "rb") as f:
            data = f.read()
        if len(data) > MAX_BIRDEYE_BYTES:
            _debug(f"birdeye skipped (size {len(data)} > {MAX_BIRDEYE_BYTES})")
            return None
        b64 = base64.b64encode(data).decode("ascii")
        return b64
    except Exception as e:
        _debug(f"birdeye capture failed: {e}")
        return None

def _http_post_json(url: str, payload: dict, timeout_sec: float = 5.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _grid_step(own, direction: str):
    d = direction.upper()
    if d == "LEFT":
        own.worldPosition.x -= STEP_SIZE
    elif d == "RIGHT":
        own.worldPosition.x += STEP_SIZE
    elif d == "UP":
        own.worldPosition.y += STEP_SIZE
    elif d == "DOWN":
        own.worldPosition.y -= STEP_SIZE
    # STAY → no move

def update():
    if logic is None:
        return

    cont = logic.getCurrentController()
    own  = cont.owner

    now = time.time()
    if now - state["last_tick"] < TICK_SECS:
        return
    state["last_tick"] = now
    state["tick_count"] += 1

    # Allow external scripts (e.g., another text block) to override tasks dynamically
    override_tasks = logic.globalDict.get("vesper_tasks") if hasattr(logic, 'globalDict') else None
    if isinstance(override_tasks, list) and override_tasks:
        state["tasks"] = [str(t) for t in override_tasks]

    # --- (1) Capture bird-eye view (optional for text-only LLMs) ---
    img64 = _encode_birdeye_png_b64()
    if img64:
        _debug(f"birdeye size chars={len(img64)}")
    else:
        _debug("birdeye not captured (disabled or failed)")

    # --- (2) Build numeric state & rooms map ---
    # You can set this from another init script:
    # logic.globalDict["vesper_rooms"] = {"Kitchen":{"center":[...]} , ...}
    rooms = logic.globalDict.get("vesper_rooms", {
        "Kitchen":    {"center": [3.0, -1.0]},
        "LivingRoom": {"center": [-2.0, 1.5]},
        "Bedroom":    {"center": [-3.0, -2.0]},
    })
    actor = {"x": float(own.worldPosition.x), "y": float(own.worldPosition.y)}

    payload = {
        "tasks": state["tasks"],
        "actor": actor,
        "rooms": rooms,
        "last_room": state["last_room"],
        "bird_eye_b64": img64,  # OK if None
    }

    # --- (3) Ask backend for next {room, direction} ---
    try:
        decision = _http_post_json(BACKEND_URL + "/decider/decide", payload)
        room = decision.get("room", state["last_room"])
        direction = decision.get("direction", "STAY").upper()
        _debug(f"tick={state['tick_count']} decision room={room} dir={direction} actor={actor}")
    except Exception as e:
        _debug(f"backend request failed: {e}")
        return

    # --- (4) Move one grid step in that direction ---
    _grid_step(own, direction)

    # --- (5) Notify progress (optional) ---
    if BRIDGE:
        try:
            BRIDGE.send({"event": "tick", "actor": actor, "decision": decision})
        except Exception:
            pass

    state["last_room"] = room
