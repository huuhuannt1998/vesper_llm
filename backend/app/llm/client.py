from __future__ import annotations
import os
from dotenv import load_dotenv
from typing import Dict, Any
import time
import random

# Load environment variables from the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Configure API settings
BASE_URL = os.getenv("LLM_API_URL", "http://100.98.151.66:1234/v1")
API_URL = BASE_URL
API_KEY = os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
TIMEOUT = float(os.getenv("LLM_REQUEST_TIMEOUT", "30"))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "256"))
DEBUG = os.getenv("LLM_DEBUG", "0") not in ("", "0", "false", "False")


# Enable mock mode when real server is not accessible
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "auto").lower()

def mock_chat_completion(system: str, user: str, max_tokens: int = 50) -> str:
    """Mock LLM response for testing when real server is unavailable"""
    time.sleep(0.1)  # Simulate processing delay
    
    user_lower = user.lower()
    system_lower = system.lower()
    
    # Navigation-specific responses for visual analysis
    if "navigation" in system_lower and "json" in system_lower:
        # This matches the visual_decider system prompt format
        directions = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
        direction = random.choice(directions)
        rooms = ["Kitchen", "Living Room", "Bedroom", "Bathroom"]
        target_room = random.choice(rooms)
        
        # Return properly formatted JSON for visual navigation
        return f'{{"direction": "{direction}", "room": "{target_room}", "reasoning": "Mock LLM: Perfect visibility shows the bright red character. Open-top design reveals clear path. Moving {direction} toward {target_room}...", "task_complete": false, "next_action": ""}}'
    
    # Simple direction responses
    elif "direction" in system_lower or "move" in user_lower:
        directions = ["UP", "DOWN", "LEFT", "RIGHT", "STAY"]
        direction = random.choice(directions)
        return direction
    
    # Room detection
    elif "room" in user_lower or "location" in user_lower:
        rooms = ["Kitchen", "Living Room", "Bedroom", "Bathroom"]
        room = random.choice(rooms)
        return room
    
    # Simple test responses
    elif "ok" in user_lower or "test" in user_lower:
        return "OK"
    elif "hello" in user_lower:
        return "Hello! Mock LLM is working."
    
    return "Mock LLM: Processing request successfully."

def try_real_llm_connection() -> bool:
    """Test if real LLM server is accessible with timeout"""
    try:
        # Quick network test first
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        result = sock.connect_ex(('100.98.151.66', 1234))
        sock.close()
        
        if result != 0:
            return False
            
        # If socket connects, try OpenAI client
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=3)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5,
        )
        return True
    except Exception:
        return False


def chat_completion(system: str, user: str, max_tokens: int | None = None) -> str:
    # Check if we should use mock LLM
    if USE_MOCK_LLM == "true" or (USE_MOCK_LLM == "auto" and not try_real_llm_connection()):
        if DEBUG or USE_MOCK_LLM == "auto":
            print("🔧 Using Mock LLM - Real server not accessible")
        return mock_chat_completion(system, user, max_tokens or MAX_TOKENS)
    
    # Try real LLM
    try:
        from openai import OpenAI
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT)
        
        if DEBUG:
            print(f"LLM DEBUG: Using OpenAI client with base_url={BASE_URL} model={MODEL} max_tokens={int(max_tokens or MAX_TOKENS)}")
            
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=int(max_tokens or MAX_TOKENS),
        )
        
        if DEBUG:
            print(f"LLM DEBUG: Response received successfully")
            
        choices = response.choices
        if not choices:
            raise RuntimeError(f"LLM: empty choices in response")
            
        message = choices[0].message
        content = message.content
        
        if content is None:
            raise RuntimeError(f"LLM: empty message content in response")
            
        return content
        
    except Exception as e:
        if DEBUG:
            print(f"LLM DEBUG: Real LLM failed ({e}), falling back to mock")
        # Fall back to mock LLM
        return mock_chat_completion(system, user, max_tokens or MAX_TOKENS)

def get_models(base_url: str | None = None) -> list[str]:
    """Return available model IDs from the LLM server, if it exposes /v1/models."""
    if USE_MOCK_LLM == "true":
        return ["mock-llm-model"]
    
    try:
        from openai import OpenAI
        if base_url and base_url != BASE_URL:
            temp_client = OpenAI(base_url=base_url, api_key=API_KEY, timeout=TIMEOUT)
            models_response = temp_client.models.list()
        else:
            client = OpenAI(base_url=BASE_URL, api_key=API_KEY, timeout=TIMEOUT)
            models_response = client.models.list()
            
        return [model.id for model in models_response.data]
        
    except Exception as e:
        if DEBUG:
            print(f"LLM DEBUG: Failed to get models: {e}")
        return ["mock-llm-model"]
