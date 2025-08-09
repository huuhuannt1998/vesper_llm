from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.llm.decider import decide_next

router = APIRouter()

class TickIn(BaseModel):
    tasks: list[str]
    # optional, but helps the LLM: numeric state + coarse map
    actor: dict  # {"x": float, "y": float}
    rooms: dict  # name -> {"center":[x,y]}
    last_room: str | None = None
    # OPTIONAL: bird's-eye image as base64 (we pass it through to the LLM prompt text)
    bird_eye_b64: str | None = None

@router.post("/decide")
def decide(tick: TickIn):
    decision = decide_next(
        tasks=tick.tasks,
        actor=tick.actor,
        rooms=tick.rooms,
        last_room=tick.last_room,
        bird_eye_b64=tick.bird_eye_b64
    )
    # {"room":"Kitchen","direction":"RIGHT"}
    return decision
