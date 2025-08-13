import os, sys
# Ensure repo root is importable when running this script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Use a shorter timeout for quick health checks and enable debug logs
os.environ.setdefault("LLM_REQUEST_TIMEOUT", "10")
os.environ.setdefault("LLM_DEBUG", "1")

from backend.app.llm.client import chat_completion, API_URL, MODEL


def main():
    print(f"API_URL: {API_URL}")
    print(f"MODEL:   {MODEL}")

    # Simple deterministic access check:
    # Ask the model to return an exact token; verify equality.
    EXPECT = "ACCESS_OK"
    system = "You are a helpful assistant. When asked to return an exact string, reply with exactly that string and nothing else."
    user = f"Return exactly: {EXPECT}"

    try:
        resp = chat_completion(system=system, user=user, max_tokens=32)
        print("Raw response:", repr(resp))
        if resp and EXPECT in resp:
            print("PASS: LLM accessible and responded correctly.")
            sys.exit(0)
        else:
            print("FAIL: LLM responded, but did not match expected token.")
            print("Note: Response may be truncated due to token limit.")
            sys.exit(2)
    except Exception as e:
        print("ERROR: Chat request failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
