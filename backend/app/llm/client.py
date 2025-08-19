# client.py
import os
import sys
import base64
import requests
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# --- Load .env if present ---
load_dotenv()

# --- Config ---
BASE_URL = os.getenv("LLM_API_URL", "http://100.98.151.66:1234/v1").rstrip("/")
API_KEY = os.getenv("OPENAI_API_KEY") or "not-needed"  # local server ignores this
MODEL = "google/gemma-3-27b"

MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))
OPENAI_TIMEOUT = os.getenv("OPENAI_TIMEOUT", "180")  # Increased from 120 to 180 for vision
os.environ["OPENAI_TIMEOUT"] = OPENAI_TIMEOUT

# --- Init client ---
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def chat_completion(
    system: str,
    user: str,
    *,
    max_tokens: Optional[int] = None,
    temperature: float = 0.3,
    image_base64: Optional[str] = None,  # Backward compatibility
) -> str:
    """Simple text-only chat using google/gemma-3-27b."""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=int(max_tokens or MAX_TOKENS),
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()

def chat_completion_with_vision(prompt, image_path=None, image_base64=None):
    """Chat completion with vision (backward compatible with image_base64 parameter)"""
    try:
        # Support both image_path and image_base64 for backward compatibility
        if image_base64:
            encoded_image = image_base64
        elif image_path and os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        else:
            print("No valid image provided - using text-only completion")
            return chat_completion(prompt)
        
        data = {
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": MAX_TOKENS
        }
        
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=180  # 3 minutes for vision processing
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        print("VLM vision request timed out after 180 seconds")
        return "TIMEOUT_ERROR: Vision processing timeout - please wait for VLM reconnection"
    except Exception as e:
        print(f"VLM vision error: {e}")
        return f"CONNECTION_ERROR: {e} - please wait for VLM reconnection"

# --- Simple CLI test ---
if __name__ == "__main__":
    print(f"BASE_URL : {BASE_URL}")
    print(f"MODEL    : {MODEL}")

    try:
        txt = chat_completion(
            "You are a helpful assistant.",
            "Say only the word: pong",
            max_tokens=8,
            temperature=0.0,
        )
        print("✅ Text ping:", txt)
    except Exception as e:
        print("❌ LLM request failed:", e)
