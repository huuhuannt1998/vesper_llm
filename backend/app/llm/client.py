# client.py
import os
import base64
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration for Open WebUI server (faster model)
USE_OPENWEBUI = os.getenv("USE_OPENWEBUI", "true").lower() == "true"
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://cci-siscluster1.charlotte.edu:8080/api/chat/completions")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
OPENWEBUI_MODEL = os.getenv("OPENWEBUI_MODEL", "OpenGVLab/InternVL3_5-30B-A3B")
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))  # For Open WebUI

print(f"🔍 LLM Client Configuration:")
print(f"  USE_OPENWEBUI: {USE_OPENWEBUI}")
if USE_OPENWEBUI:
    print(f"  OPENWEBUI_URL: {OPENWEBUI_URL}")
    print(f"  OPENWEBUI_MODEL: {OPENWEBUI_MODEL}")

def _chat_via_openwebui(system: str, user: str, temperature: float) -> str:
    """
    Use Open WebUI server with faster model
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

def _chat_via_openwebui_vision(prompt: str, image_base64, temperature: float) -> str:
    """
    Vision completion using Open WebUI server - supports single image or list of images
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
        }
    ]
    
    # Handle single image or multiple images
    if isinstance(image_base64, str):
        # Single image
        message_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_base64}"
            }
        })
    elif isinstance(image_base64, list):
        # Multiple images
        for i, img_data in enumerate(image_base64):
            message_content.append({
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/png;base64,{img_data}"
                }
            })
            print(f"👁️ Added image {i+1}/{len(image_base64)} to vision request")
    else:
        raise ValueError(f"Invalid image_base64 type: {type(image_base64)}")
    
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

def chat_completion(
    system: str,
    user: str,
    *,
    max_tokens: Optional[int] = None,  # kept for API compatibility
    temperature: float = 0.3,
    image_base64: Optional[str] = None,  # not used for text-only
) -> str:
    """
    Text completion using only Open WebUI server
    """
    if not USE_OPENWEBUI:
        raise Exception("Open WebUI is disabled. Only Open WebUI is supported in this configuration.")
    
    try:
        return _chat_via_openwebui(system, user, temperature)
    except Exception as e:
        print(f"❌ Open WebUI failed: {e}")
        raise Exception(f"Open WebUI connection failed: {e}")

def chat_completion_with_vision(prompt, image_path=None, image_base64=None, image_paths=None):
    """
    Vision completion using only Open WebUI server - supports single or multiple images
    """
    if not USE_OPENWEBUI:
        raise Exception("Open WebUI is disabled. Only Open WebUI is supported in this configuration.")
    
    try:
        print(f"🔍 DEBUG: Vision completion starting...")
        
        # Handle multiple image paths
        if image_paths and len(image_paths) > 0:
            image_data_list = []
            for img_path in image_paths:
                if os.path.exists(img_path):
                    with open(img_path, "rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        image_data_list.append(img_data)
                        print(f"📷 Loaded image: {os.path.basename(img_path)}")
                else:
                    print(f"⚠️ Image not found: {img_path}")
            
            if not image_data_list:
                print("⚠️ No valid images found, falling back to text-only")
                return chat_completion("You are a helpful assistant.", prompt)
            
            print(f"👁️ Using Open WebUI for vision with {len(image_data_list)} images: {OPENWEBUI_MODEL}")
            return _chat_via_openwebui_vision(prompt, image_data_list, 0.3)
        
        # Handle single image (existing logic)
        elif image_path and os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
        elif image_base64:
            image_data = image_base64
        else:
            print("⚠️ No image provided, falling back to text-only")
            return chat_completion("You are a helpful assistant.", prompt)
        
        print(f"👁️ Using Open WebUI for vision: {OPENWEBUI_MODEL}")
        return _chat_via_openwebui_vision(prompt, image_data, 0.3)
        
    except Exception as e:
        print(f"❌ Open WebUI vision failed: {e}")
        print(f"🔍 DEBUG: Exception type: {type(e).__name__}")
        raise Exception(f"Open WebUI vision failed: {e}")

# --- Simple CLI test ---
if __name__ == "__main__":
    if USE_OPENWEBUI:
        print(f"Open WebUI URL: {OPENWEBUI_URL}")
        print(f"Open WebUI MODEL: {OPENWEBUI_MODEL}")
    else:
        print("❌ Open WebUI is disabled")
        exit(1)

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