
import json, asyncio, os, pathlib, websockets

WS_URL = os.getenv("BACKEND_WS_URL", "ws://127.0.0.1:8000/sim/ws")

async def main():
    rt = pathlib.Path(".runtime") / "last_plan.json"
    if not rt.exists():
        print("No .runtime/last_plan.json found. Run scripts/send_plan.py first.")
        return
    data = json.loads(rt.read_text(encoding="utf-8"))
    payload = {"event": "new_plan", "plan": data["plan"]}
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps(payload))
        print("Sent:", json.dumps(payload))

if __name__ == "__main__":
    asyncio.run(main())
