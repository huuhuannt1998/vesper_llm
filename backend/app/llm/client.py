import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from repo root if present
_here = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(_here, ".env")
if os.path.isfile(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# ---- Config ----
BASE_URL = os.getenv("LLM_API_URL", "http://100.98.151.66:1234/v1").rstrip("/")
API_KEY = os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "30"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "256"))
DEBUG = os.getenv("LLM_DEBUG", "0") not in ("", "0", "false", "False")

# ---- Client ----
client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT)

def chat_completion(system: str, user: str, max_tokens: int | None = None) -> str:
    """Send a chat completion request to the LLM server."""
    if DEBUG:
        print(f"LLM DEBUG: Sending request to {BASE_URL} model={MODEL}")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=int(max_tokens or MAX_TOKENS),
    )

    if not response.choices:
        raise RuntimeError("LLM: empty choices in response")

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("LLM: empty message content in response")

    return content

def get_models(base_url: str | None = None) -> list[str]:
    """List models available from the LLM server (if supported)."""
    url = base_url or BASE_URL
    c = OpenAI(base_url=url, api_key=API_KEY, timeout=TIMEOUT)
    models = c.models.list()
    return [m.id for m in models.data]

# ---- Simple test ----
if __name__ == "__main__":
    try:
        reply = chat_completion("You are a helpful assistant.", "Hello! Can you tell me a fun fact about space?")
        print("✅ LLM Response:", reply)
    except Exception as e:
        print("❌ LLM request failed:", e)
