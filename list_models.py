import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("LLAMA_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY or LLAMA_API_KEY in environment")

BASE_URL = "https://api.lambda.ai/v1"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

models = client.models.list()
for m in models.data:
    print(m.id)
