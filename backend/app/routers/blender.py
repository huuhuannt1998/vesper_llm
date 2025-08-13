from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from backend.app.llm.visual_decider import decide_with_vision
import base64

router = APIRouter()

class BlenderState(BaseModel):
    actor_position: Dict[str, float]  # {"x": 0.0, "y": 0.0, "z": 0.0}
    tasks: List[str]
    rooms: Dict[str, Dict[str, Any]]  # room definitions
    bird_eye_image: Optional[str] = None  # base64 encoded image
    last_room: Optional[str] = None
    step_count: int = 0
    max_steps: int = 50  # prevent infinite loops

class NavigationDecision(BaseModel):
    direction: str  # "UP", "DOWN", "LEFT", "RIGHT", "STAY"
    target_room: str
    reasoning: str
    task_complete: bool
    next_action: Optional[str] = None  # for device interactions

@router.post("/navigate", response_model=NavigationDecision)
async def navigate_character(state: BlenderState):
    """
    Main endpoint for LLM-controlled character navigation.
    Takes current state + bird-eye view, returns next movement decision.
    """
    
    if state.step_count >= state.max_steps:
        raise HTTPException(status_code=400, detail="Max steps reached")
    
    if not state.tasks:
        return NavigationDecision(
            direction="STAY",
            target_room=state.last_room or "Kitchen",
            reasoning="No tasks to complete",
            task_complete=True
        )
    
    try:
        # Use visual LLM decider if image provided
        if state.bird_eye_image:
            decision = decide_with_vision(
                tasks=state.tasks,
                actor_position=state.actor_position,
                rooms=state.rooms,
                bird_eye_b64=state.bird_eye_image,
                last_room=state.last_room,
                step_count=state.step_count
            )
        else:
            # Fallback to text-only decision
            from backend.app.llm.decider import decide_next
            decision = decide_next(
                tasks=state.tasks,
                actor=state.actor_position,
                rooms=state.rooms,
                last_room=state.last_room,
                bird_eye_b64=None
            )
            decision["reasoning"] = "Text-only navigation (no image)"
            decision["task_complete"] = False
    
        return NavigationDecision(
            direction=decision.get("direction", "STAY"),
            target_room=decision.get("room", state.last_room or "Kitchen"),
            reasoning=decision.get("reasoning", "LLM navigation decision"),
            task_complete=decision.get("task_complete", False),
            next_action=decision.get("next_action")
        )
        
    except Exception as e:
        # Fallback heuristic decision
        return NavigationDecision(
            direction="STAY",
            target_room=state.last_room or "Kitchen", 
            reasoning=f"Error in LLM decision: {str(e)}",
            task_complete=False
        )

@router.post("/complete-task")
async def complete_task(task_name: str, room: str):
    """
    Mark a task as completed and potentially trigger device interactions.
    """
    # This could integrate with your device control system
    return {
        "task": task_name,
        "room": room,
        "completed": True,
        "timestamp": "2025-08-12T00:00:00Z"
    }

@router.get("/status")
async def get_system_status():
    """
    Health check for the visual navigation system.
    """
    return {
        "status": "active",
        "features": {
            "visual_llm": True,
            "text_fallback": True,
            "blender_integration": True,
            "multi_step_navigation": True
        }
    }
