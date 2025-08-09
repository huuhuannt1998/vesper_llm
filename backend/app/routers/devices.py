
from fastapi import APIRouter
from backend.app.devices.sim_state import DEVICE_STATE, apply_action

router = APIRouter()

@router.get("")
def list_devices():
    return DEVICE_STATE

@router.post("/action")
def device_action(device_id: str, op: str):
    ok, msg = apply_action(device_id, op)
    return {"ok": ok, "message": msg}
