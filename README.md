
# VESPER Starter (Polycam → Blender/UPBGE → FastAPI → External LLM → SmartThings)

This repository is a **ready-to-run scaffold** for your VESPER project:
- Import your **Polycam** scan into **Blender/UPBGE**
- Run a **FastAPI** backend that calls your **external LLM** (OpenWebUI-compatible)
- Stream **plans** to the simulator over **WebSocket**
- Simulate device state locally (swap to SmartThings later)

> This starter includes a mocked device layer so you can validate the loop before wiring SmartThings.

---

## ✨ Features
- **LLM-backed planner** (`backend/app/llm/planner.py`) that prompts your model to return **strict JSON** plans.
- **External LLM client** (`backend/app/llm/client.py`) reading settings from `.env`.
- **WebSocket bus** (`/sim/ws`) to push new plans to UPBGE.
- **UPBGE scripts** for receiving plans and moving the actor.
- **CLI scripts** to send tasks and broadcast the last plan to WS.

---

## 🧰 Prerequisites
- Python 3.10+
- UPBGE 0.3.x (or newer) for the game engine
- (Optional) Polycam export as `.glb` or `.fbx`

---

## ⚙️ Setup

1) **Install dependencies**
```bash
pip install -r requirements.txt
```

2) **Configure environment** — copy `.env.example` to `.env` and set your values:
```
LLM_API_URL=http://cci-siscluster1.charlotte.edu:8080/api/chat/completions
LLM_API_KEY=sk-REDACTED
LLM_MODEL=gpt-oss:120b
LLM_REQUEST_TIMEOUT=30

# Optional overrides
BACKEND_URL=http://127.0.0.1:8000
BACKEND_WS_URL=ws://127.0.0.1:8000/sim/ws
```

3) **Run the backend**
```bash
uvicorn backend.app.main:app --reload
# -> http://127.0.0.1:8000
```

4) **Generate a plan via your LLM**
```bash
python scripts/send_plan.py "Make coffee and turn off living room lights"
# Plan is saved to .runtime/last_plan.json
```

5) **Push plan to the simulator bus**
```bash
python scripts/push_plan_to_ws.py
# Sends {"event":"new_plan","plan":...} to ws://127.0.0.1:8000/sim/ws
```

6) **UPBGE hookup**
- Import your Polycam scan into UPBGE.
- Add an Actor object and attach the script:
  - Logic Editor → Always (pulse) → Python module: `game.actor_controller.update`
- Press **Play** to see the actor follow waypoints from the plan.

> See **UPBGE notes** at the bottom for a quick scene setup.

---

## 🧪 Local device simulator
Endpoints:
- `GET /devices` → list in-memory device states
- `POST /devices/action?device_id=<id>&op=ON|OFF` → toggle a device

Device map: `configs/devices.yaml`  
Rooms map: `configs/rooms.yaml` (used by the planner to validate rooms & inject fallback waypoints)

---

## 🧠 Planner contract (JSON)
The planner returns:
```json
{
  "steps": [
    {
      "room": "Kitchen",
      "waypoints": [[3.0, -1.0]],
      "actions": [
        {"type": "interact", "target_device_id": "coffee_maker_1", "op": "ON"}
      ]
    }
  ]
}
```

---

## 🧩 Swapping to SmartThings (later)
- Replace logic inside `backend/app/devices/sim_state.py` with a real SmartThings client.
- Keep the same `/devices` routes to preserve the simulator contract.

---

## 🕹️ UPBGE quick notes
- Set walls/furniture to **Physics → Collision (Static)**.
- The Actor should be **Dynamic**, with rotation locked if you don’t want it to tip.
- Add `blender/game` to UPBGE Script Paths **or** load the files as Text blocks.

---

## 📁 Repo layout

```
backend/                 # FastAPI + LLM + device simulator + WS bus
configs/                 # rooms & devices maps
blender/                 # UPBGE scripts and Blender add-on
scripts/                 # helper CLI to test pipeline
polycam/                 # put your exports here
.runtime/                # last plan (for dev scripts)
```

---

## ✅ Sanity check script
```bash
# 1) Start backend
uvicorn backend.app.main:app --reload

# 2) Ask LLM to create a plan
python scripts/send_plan.py "Make coffee and turn off living room lights"

# 3) Broadcast plan to WS (UPBGE will receive if running)
python scripts/push_plan_to_ws.py
```

---

## 📜 License
MIT (or your preferred license).
