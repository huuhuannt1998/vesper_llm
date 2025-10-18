"""
Test Docker Container Triggers
Verify that we can trigger item sensors in Docker containers
"""

import requests
import time

print("\n" + "="*70)
print("TESTING DOCKER CONTAINER ITEM SENSOR TRIGGERS")
print("="*70 + "\n")

# Test each linked container
test_cases = [
    {"name": "Phone", "port": 9201, "sensor_id": "I008", "room": "DiningRoom"},
    {"name": "BathroomSink1", "port": 9202, "sensor_id": "I010", "room": "Bathroom"},
    {"name": "Stove", "port": 9203, "sensor_id": "I002", "room": "Kitchen"},
    {"name": "DiningTable", "port": 9204, "sensor_id": "I009", "room": "DiningRoom"},
    {"name": "KitchenSink", "port": 9205, "sensor_id": "I001", "room": "Kitchen"},
]

success_count = 0
fail_count = 0

for test in test_cases:
    print(f"🧪 Testing {test['name']} (Port {test['port']})...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"http://localhost:{test['port']}/health", timeout=2)
        if response.status_code == 200:
            print(f"   ✅ Health check OK")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            fail_count += 1
            continue
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        fail_count += 1
        continue
    
    # Test 2: Get current state
    try:
        response = requests.get(f"http://localhost:{test['port']}/state", timeout=2)
        if response.status_code == 200:
            state = response.json()
            print(f"   📊 Current state: {state.get('state', 'unknown')}")
        else:
            print(f"   ⚠️ Could not get state: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ State check error: {e}")
    
    # Test 3: Trigger interaction (pickup)
    try:
        interaction_data = {
            "action": "pickup",  # or "putdown", "use"
            "actor_id": "test_actor",
            "timestamp": None  # Let container use current time
        }
        
        response = requests.post(
            f"http://localhost:{test['port']}/interaction",
            json=interaction_data,
            timeout=2
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"   ✅ Logged interaction (pickup): {result.get('message', 'OK')}")
            time.sleep(0.5)  # Wait a bit
        else:
            print(f"   ❌ Interaction (pickup) failed: {response.status_code}")
            print(f"      Response: {response.text[:100]}")
            fail_count += 1
            continue
            
    except Exception as e:
        print(f"   ❌ Interaction (pickup) error: {e}")
        fail_count += 1
        continue
    
    # Test 4: Trigger interaction (putdown)
    try:
        interaction_data = {
            "action": "putdown",
            "actor_id": "test_actor",
            "timestamp": None
        }
        
        response = requests.post(
            f"http://localhost:{test['port']}/interaction",
            json=interaction_data,
            timeout=2
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"   ✅ Logged interaction (putdown): {result.get('message', 'OK')}")
            time.sleep(0.5)  # Wait a bit
        else:
            print(f"   ❌ Interaction (putdown) failed: {response.status_code}")
            fail_count += 1
            continue
            
    except Exception as e:
        print(f"   ❌ Interaction (putdown) error: {e}")
        fail_count += 1
        continue
    
    print(f"   ✅ {test['name']} test PASSED\n")
    success_count += 1

print("="*70)
print(f"TEST RESULTS: {success_count}/{len(test_cases)} devices passed")
print("="*70 + "\n")

if success_count == len(test_cases):
    print("🎉 All container triggers working correctly!")
    print("   BGE can now trigger virtual item sensors")
else:
    print(f"⚠️ {fail_count} devices failed")
    print("   Check container logs: docker logs <container-name>")
