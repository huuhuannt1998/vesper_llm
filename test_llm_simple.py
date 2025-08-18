# test_gemma.py
import os
from openai import OpenAI

# --- Config ---
BASE_URL = "http://100.98.151.66:1234/v1"
API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")  # some servers ignore this

# Init client
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def main():
    try:
        # List models
        models = client.models.list()
        print("✅ Available models:")
        for m in models.data:
            print(" -", m.id)

        # Run a simple chat test with Gemma
        response = client.chat.completions.create(
            model="google/gemma-3-27b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in one short sentence."}
            ],
            max_tokens=50,
        )

        print("\n✅ Chat test output:")
        print(response.choices[0].message.content)

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
