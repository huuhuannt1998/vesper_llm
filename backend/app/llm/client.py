
from __future__ import annotations
import os, httpx
from dotenv import load_dotenv
from typing import Dict, Any

# Load .env if present so users can configure without modifying code
load_dotenv()

# Defaults tuned to the user's LLM server and model; override via env vars if needed
API_URL  = os.getenv("LLM_API_URL", "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions")
# API_URL  = os.getenv("LLM_API_URL", "http://100.98.151.66:1234/api/chat/completions")
# 100.98.151.66
API_KEY  = os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
MODEL    = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
TIMEOUT  = float(os.getenv("LLM_REQUEST_TIMEOUT", "30"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "256"))
DEBUG = os.getenv("LLM_DEBUG", "0") not in ("", "0", "false", "False")

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    **({"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}),
}

def chat_completion(system: str, user: str, max_tokens: int | None = None) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "max_tokens": int(max_tokens or MAX_TOKENS),
    }

    if DEBUG:
        print(f"LLM DEBUG: POST {API_URL} model={payload['model']} max_tokens={payload['max_tokens']}")
        print(f"LLM DEBUG: Headers: {HEADERS}")
        print(f"LLM DEBUG: Payload: {payload}")
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.post(API_URL, headers=HEADERS, json=payload)
        if DEBUG:
            print(f"LLM DEBUG: status={r.status_code}")
            if r.status_code >= 400:
                print(f"LLM DEBUG: Response text: {r.text}")
        r.raise_for_status()
        data = r.json()

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError(f"LLM: empty choices: {data}")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    
    # Handle servers that use reasoning_content field instead of content
    if content is None:
        reasoning = msg.get("reasoning_content", "")
        if reasoning:
            if DEBUG:
                print(f"LLM DEBUG: Using reasoning_content instead of content")
            return reasoning
        raise RuntimeError(f"LLM: empty message content: {data}")
    return content

def get_models(base_url: str | None = None) -> list[str]:
    """Return available model IDs from the LLM server, if it exposes /v1/models."""
    url = (base_url or API_URL)
    # Replace chat/completions with models endpoint if using OpenAI-compatible server
    if "/chat/completions" in url:
        url = url.split("/chat/completions")[0] + "/models"
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(url, headers={k:v for k,v in HEADERS.items() if k != "Content-Type"})
        r.raise_for_status()
        data = r.json()
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return [m.get("id") for m in data["data"] if isinstance(m, dict) and m.get("id")]
    return []
