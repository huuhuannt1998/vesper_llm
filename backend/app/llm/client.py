# client.py
import os
import base64
import requests
from typing import Optional
from dotenv import load_dotenv
import ollama

load_dotenv()

# Configuration for Open WebUI server (faster model)
USE_OPENWEBUI = os.getenv("USE_OPENWEBUI", "true").lower() == "true"
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
OPENWEBUI_MODEL = os.getenv("OPENWEBUI_MODEL", "OpenGVLab/InternVL3_5-30B-A3B")

print(f"🔍 LLM Client Configuration:")
print(f"  USE_OPENWEBUI: {USE_OPENWEBUI}")
if USE_OPENWEBUI:
    print(f"  OPENWEBUI_URL: {OPENWEBUI_URL}")
    print(f"  OPENWEBUI_MODEL: {OPENWEBUI_MODEL}")

# Legacy Ollama configuration (fallback)
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

# Create an Ollama client explicitly bound to host (fallback only)
client = ollama.Client(host=HOST)

def _chat_via_openwebui(system: str, user: str, temperature: float) -> str:
    """
    Primary path: Use Open WebUI server with faster model
    """
    headers = {
        'Authorization': f'Bearer {OPENWEBUI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": OPENWEBUI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": user
            }
        ],
        "temperature": temperature,
        "max_tokens": MAX_TOKENS
    }
    
    try:
        print(f"🚀 Sending request to Open WebUI: {OPENWEBUI_MODEL}")
        response = requests.post(OPENWEBUI_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content.strip()
        else:
            raise Exception(f"Unexpected response format: {result}")
            
    except Exception as e:
        print(f"❌ Open WebUI request failed: {e}")
        raise e

def _chat_via_openwebui_vision(prompt: str, image_base64: str, temperature: float) -> str:
    """
    Vision completion using Open WebUI server
    """
    headers = {
        'Authorization': f'Bearer {OPENWEBUI_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Format the message for vision
    message_content = [
        {
            "type": "text",
            "text": prompt
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_base64}"
            }
        }
    ]
    
    data = {
        "model": OPENWEBUI_MODEL,
        "messages": [
            {
                "role": "user",
                "content": message_content
            }
        ],
        "temperature": temperature,
        "max_tokens": MAX_TOKENS
    }
    
    try:
        print(f"👁️ Sending vision request to Open WebUI: {OPENWEBUI_MODEL}")
        response = requests.post(OPENWEBUI_URL, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            return content.strip()
        else:
            raise Exception(f"Unexpected vision response format: {result}")
            
    except Exception as e:
        print(f"❌ Open WebUI vision request failed: {e}")
        raise e

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
    max_tokens: Optional[int] = None,  # kept for API compatibility
    temperature: float = 0.3,
    image_base64: Optional[str] = None,  # not used for text-only
) -> str:
    # Use Open WebUI as primary method if enabled
    if USE_OPENWEBUI:
        try:
            return _chat_via_openwebui(system, user, temperature)
        except Exception as e1:
            print(f"⚠️ Open WebUI failed: {e1} — falling back to Ollama...")
    
    # Fallback to Ollama methods
    try:
        return _chat_via_ollama_client(system, user, temperature)
    except Exception as e2:
        print(f"⚠️ ollama.Client.chat failed: {e2} — trying HTTP /api/chat ...")
        try:
            return _chat_via_http_chat(system, user, temperature)
        except Exception as e3:
            print(f"⚠️ HTTP /api/chat failed: {e3} — trying /api/generate ...")
            try:
                return _chat_via_http_generate(system, user, temperature)
            except Exception as e4:
                print(f"❌ All LLM methods failed: {e4}")
                return f"CONNECTION_ERROR: {e4}"

def chat_completion_with_vision(prompt, image_path=None, image_base64=None):
    """
    Chat completion with vision support using Open WebUI or Ollama vision models
    """
    try:
        print(f"🔍 DEBUG: Vision completion starting...")
        
        # Prepare the image
        if image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
        elif image_base64:
            image_data = image_base64
        else:
            print("⚠️ No image provided, falling back to text-only")
            return chat_completion("You are a helpful assistant.", prompt)
        
        # Use Open WebUI as primary method for vision if enabled
        if USE_OPENWEBUI:
            try:
                print(f"�️ Using Open WebUI for vision: {OPENWEBUI_MODEL}")
                return _chat_via_openwebui_vision(prompt, image_data, 0.3)
            except Exception as e1:
                print(f"⚠️ Open WebUI vision failed: {e1} — falling back to Ollama...")
        
        # Fallback to Ollama vision
        print(f"👁️ Using Ollama for vision: {MODEL}")
        response = client.chat(
            model=MODEL,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    'images': [image_data]
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
    if USE_OPENWEBUI:
        print(f"Open WebUI URL: {OPENWEBUI_URL}")
        print(f"Open WebUI MODEL: {OPENWEBUI_MODEL}")
    else:
        print(f"Ollama HOST: {HOST}")
        print(f"Ollama MODEL: {MODEL}")

    print("\n🧪 Testing text completion...")
    txt = chat_completion(
        "You are a helpful assistant.",
        "Say only the word: pong",
        temperature=0.0,
    )
    print("Ping result:", txt)
    
    print("\n🧪 Testing vision completion...")
    # Test with a simple base64 image
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    vision_result = chat_completion_with_vision(
        "What color is this image?",
        image_base64=test_image_b64
    )
    print("Vision result:", vision_result)