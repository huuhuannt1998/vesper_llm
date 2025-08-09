
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

router = APIRouter()
connections = set()

@router.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    connections.add(ws)
    try:
        while True:
            msg = await ws.receive_text()
            # broadcast to everyone (simple bus)
            for c in list(connections):
                if c is not ws:
                    try:
                        await c.send_text(msg)
                    except:
                        pass
    except WebSocketDisconnect:
        connections.discard(ws)
