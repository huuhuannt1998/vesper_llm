
from __future__ import annotations
import os, httpx
from typing import Dict, Any

API_URL  = os.getenv("LLM_API_URL", "http://localhost:8080/api/chat/completions")
API_KEY  = os.getenv("LLM_API_KEY", "")
MODEL    = os.getenv("LLM_MODEL", "gpt-oss:120b")
TIMEOUT  = float(os.getenv("LLM_REQUEST_TIMEOUT", "30"))

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
}

def chat_completion(system: str, user: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ]
    }
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(API_URL, headers=HEADERS, json=payload)
        r.raise_for_status()
        data = r.json()
    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"LLM: empty choices: {data}")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not content:
        raise RuntimeError(f"LLM: empty message content: {data}")
    return content
