
import threading, json, time, os
from websocket import WebSocketApp

WS_URL = os.getenv("BACKEND_WS_URL", "ws://127.0.0.1:8000/sim/ws")

class SimBridge:
    def __init__(self, url=WS_URL):
        self.url = url
        self.ws = None
        self.thread = None
        self.on_message = None

    def _run(self):
        def _on_message(_, msg):
            try:
                data = json.loads(msg)
            except Exception:
                data = {"raw": msg}
            if self.on_message: 
                try: self.on_message(data)
                except Exception: pass
        self.ws = WebSocketApp(self.url, on_message=_on_message)
        self.ws.run_forever()

    def start(self): 
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        time.sleep(0.2)

    def send(self, payload: dict):
        if self.ws and self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(payload))

BRIDGE = SimBridge()
