
import sys, json, httpx, uuid, os
URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def main():
    natural = " ".join(sys.argv[1:]) or "Make coffee and turn off living room lights"
    payload = {"task_id": str(uuid.uuid4()), "natural_text": natural, "context": {}}
    r = httpx.post(f"{URL}/tasks/plan", json=payload, timeout=30)
    r.raise_for_status()
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    main()
