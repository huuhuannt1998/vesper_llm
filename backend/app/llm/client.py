# client.py
import os
import base64
import requests
from typing import Optional
from dotenv import load_dotenv
import ollama

load_dotenv()

# Debug environment variables
# raw_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
raw_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
print(f"🔍 DEBUG: Raw OLLAMA_HOST = '{raw_host}'")

HOST = raw_host.rstrip("/")
# Ensure the host has a proper scheme
if not HOST.startswith(('http://', 'https://')):
    if HOST.startswith('localhost:') or HOST.startswith('127.0.0.1:'):
        HOST = f"http://{HOST}"
    elif HOST in ['localhost', '127.0.0.1']:
        HOST = f"http://{HOST}:11434"
    elif HOST == '0.0.0.0':
        # 0.0.0.0 is a server bind address, convert to localhost for client
        print(f"🔧 Converting server address '0.0.0.0' to 'localhost' for client")
        HOST = "http://localhost:11434"
    else:
        # Fallback to localhost if something went wrong
        print(f"⚠️ Invalid HOST format: '{HOST}', falling back to localhost")
        HOST = "http://localhost:11434"

print(f"🔍 DEBUG: Final HOST = '{HOST}'")

MODEL = (os.getenv("OLLAMA_MODEL", "llava:7b")).strip()
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))

# Create an Ollama client explicitly bound to host
client = ollama.Client(host=HOST)

def _chat_via_ollama_client(system: str, user: str, temperature: float) -> str:
    """
    Primary path: use ollama.Client.chat (modern Ollama servers).
    """
    resp = client.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        options={"temperature": temperature},
    )
    return (resp["message"]["content"] or "").strip()

def _chat_via_http_chat(system: str, user: str, temperature: float) -> str:
    """
    Fallback #1: direct HTTP to /api/chat (some environments prefer this).
    """
    url = f"{HOST}/api/chat"
    print(f"🔍 DEBUG: Trying HTTP chat at: {url}")
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "options": {"temperature": temperature},
    }
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    # streaming vs non-streaming responses:
    if "message" in data and data["message"].get("content"):
        return data["message"]["content"].strip()
    # If server streamed chunks (rare for /api/chat), join them:
    if "messages" in data and isinstance(data["messages"], list):
        return "".join(m.get("content", "") for m in data["messages"]).strip()
    return ""

def _chat_via_http_generate(system: str, user: str, temperature: float) -> str:
    """
    Fallback #2: very old Ollama servers without /api/chat.
    Uses /api/generate with a single prompt.
    """
    url = f"{HOST}/api/generate"
    print(f"🔍 DEBUG: Trying HTTP generate at: {url}")
    prompt = (system + "\n\nUser:\n" + user).strip()
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "options": {"temperature": temperature},
        # "stream": False  # default is streaming; most servers will still return the full text in 'response'
    }
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    # For non-streaming, Ollama returns a single JSON with 'response'
    return (data.get("response") or "").strip()

def chat_completion(
    system: str,
    user: str,
    *,
    max_tokens: Optional[int] = None,  # kept for API compatibility; Ollama ignores this today
    temperature: float = 0.3,
    image_base64: Optional[str] = None,  # not used (Ollama text-only)
) -> str:
    try:
        return _chat_via_ollama_client(system, user, temperature)
    except Exception as e1:
        print(f"⚠️ ollama.Client.chat failed: {e1} — trying HTTP /api/chat ...")
        try:
            return _chat_via_http_chat(system, user, temperature)
        except Exception as e2:
            print(f"⚠️ HTTP /api/chat failed: {e2} — trying /api/generate ...")
            try:
                return _chat_via_http_generate(system, user, temperature)
            except Exception as e3:
                print(f"❌ All Ollama paths failed: {e3}")
                return f"CONNECTION_ERROR: {e3}"

def chat_completion_with_vision(prompt, image_path=None, image_base64=None):
    """
    Chat completion with vision support using Ollama vision models (llava, moondream, etc.)
    """
    try:
        print(f"🔍 DEBUG: Vision completion starting with HOST='{HOST}', MODEL='{MODEL}'")
        
        # Prepare the image for Ollama
        images = []
        if image_path and os.path.exists(image_path):
            import base64
            with open(image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
                images.append(image_data)
        elif image_base64:
            images.append(image_base64)
        
        if not images:
            print("⚠️ No image provided, falling back to text-only")
            return chat_completion("You are a helpful assistant.", prompt)
        
        # Use ollama.Client for vision
        print(f"🔍 DEBUG: Sending vision request to Ollama client...")
        response = client.chat(
            model=MODEL,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'images': images
                }
            ],
            options={'temperature': 0.3}
        )
        result = response['message']['content'].strip()
        print(f"🔍 DEBUG: Vision completion successful, response length: {len(result)}")
        return result
        
    except Exception as e:
        print(f"❌ Vision completion failed: {e}")
        print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        print("ℹ️ Falling back to text-only completion")
        return chat_completion("You are a helpful assistant.", prompt)

# --- Simple CLI test ---
if __name__ == "__main__":
    print(f"HOST     : {HOST}")
    print(f"MODEL    : {MODEL}")

    txt = chat_completion(
        "You are a helpful assistant.",
        "Say only the word: pong",
        temperature=0.0,
    )
    print("Ping result:", txt)