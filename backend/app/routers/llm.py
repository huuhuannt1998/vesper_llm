from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.llm.client import get_models, chat_completion, API_URL, MODEL

router = APIRouter()


class ChatTestIn(BaseModel):
    system: str = "You are a helpful assistant."
    user: str = "Say 'pong' only."
    max_tokens: int | None = 16


@router.get("/llm/health")
def llm_health():
    try:
        models = get_models()
    except Exception as e:
        return {
            "ok": False,
            "api_url": API_URL,
            "model": MODEL,
            "error": str(e),
        }
    return {
        "ok": True,
        "api_url": API_URL,
        "model": MODEL,
        "models": models,
    }


@router.post("/llm/test")
def llm_test(body: ChatTestIn):
    try:
        text = chat_completion(body.system, body.user, max_tokens=body.max_tokens)
        return {"ok": True, "response": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
