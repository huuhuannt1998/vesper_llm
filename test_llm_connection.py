import os
import requests

# Load environment variables or defaults
BASE_URL = os.getenv("LLM_API_URL", "http://100.98.151.66:1234/v1")
API_URL = f"{BASE_URL}/chat/completions"
API_KEY = os.getenv("LLM_API_KEY", "sk-a6af2053d49649d2925ff91fef71cb65")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

def check_llm_connection():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you tell me a fun fact about space?"}
        ],
        "max_tokens": 100
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        print("✅ LLM Connection Successful!")
        print("Response:", result["choices"][0]["message"]["content"])
    except Exception as e:
        print("❌ LLM Connection Failed:", str(e))
        if response is not None:
            print("Response content:", response.text)

if __name__ == "__main__":
    check_llm_connection()
