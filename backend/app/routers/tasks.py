
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.llm.planner import plan_tasks
from pathlib import Path
import json

router = APIRouter()

class TaskIn(BaseModel):
    task_id: str
    natural_text: str
    context: dict = {}

@router.post("/plan")
def plan(task: TaskIn):
    plan = plan_tasks(task.natural_text, task.context)
    rt = Path(".runtime"); rt.mkdir(exist_ok=True)
    with open(rt / "last_plan.json", "w", encoding="utf-8") as f:
        json.dump({"task_id": task.task_id, "plan": plan}, f, indent=2)
    return {"task_id": task.task_id, "plan": plan}
