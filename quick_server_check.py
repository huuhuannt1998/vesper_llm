import requests
import time

def quick_server_check():
    try:
        start = time.time()
        resp = requests.get("http://100.98.151.66:1234/v1/models", timeout=5)
        elapsed = time.time() - start
        print(f"✅ Server responding in {elapsed:.1f}s")
        models = resp.json()
        print(f"Models: {[m.get('id') for m in models.get('data', [])]}")
    except Exception as e:
        print(f"❌ Server check failed: {e}")

quick_server_check()
