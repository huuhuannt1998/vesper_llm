"""
Test Blender Game Engine Device Integration with SmartThings
This script tests that device interactions from BGE sync to SmartThings correctly
"""

import requests
import json
import time

# Device mappings
DEVICES = {
    "Phone": {
        "port": 9201,
        "serial": "VSI-DF8A-CE65-08F5",
        "internal_id": "I01"
    },
    "Stove": {
        "port": 9203,
        "serial": "VSI-F6AF-676E-2BBD",
        "internal_id": "I03"
    }
}

NGROK_URL = "https://9104a04a38e2.ngrok-free.app"


def test_device_interaction_flow(device_name):
    """Test complete flow: interaction -> state change -> SmartThings sync"""
    device = DEVICES[device_name]
    port = device["port"]
    serial = device["serial"]
    
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: {device_name}")
    print(f"{'='*80}\n")
    
    # Step 1: Trigger pickup interaction
    print(f"1️⃣ Sending 'pickup' interaction to {device_name} (port {port})...")
    try:
        url = f"http://localhost:{port}/interaction"
        payload = {"action": "pickup"}
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            result = response.json()
            new_presence = result.get("new_presence")
            print(f"   ✅ Interaction successful: {result}")
            print(f"   📊 New presence: {new_presence}")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 2: Verify container state
    print(f"\n2️⃣ Verifying container state...")
    try:
        url = f"http://localhost:{port}/state"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            state = response.json()
            presence = state.get("presence")
            print(f"   ✅ Container state: {state}")
            print(f"   📊 Presence: {presence}")
            
            if presence != "ABSENT":
                print(f"   ⚠️ WARNING: Expected ABSENT, got {presence}")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 3: Notify SmartThings (simulating BGE sync_device_state_to_smartthings)
    print(f"\n3️⃣ Notifying SmartThings of state change...")
    try:
        url = f"http://localhost:8081/api/devices/{serial}/state-changed"
        response = requests.post(url, json={}, timeout=2)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Notification sent: {result}")
            callback_sent = result.get("callback_sent", False)
            print(f"   📡 Callback sent to SmartThings: {callback_sent}")
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Wait for sync
    print(f"\n4️⃣ Waiting 2 seconds for sync...")
    time.sleep(2)
    
    # Step 5: Verify SmartThings state
    print(f"\n5️⃣ Querying SmartThings state...")
    try:
        url = f"{NGROK_URL}/schema"
        payload = {
            "headers": {
                "schema": "st-schema",
                "version": "1.0",
                "interactionType": "stateRefreshRequest",
                "requestId": f"test-{device_name}-{int(time.time())}"
            },
            "devices": [
                {
                    "externalDeviceId": serial,
                    "deviceCookie": {}
                }
            ]
        }
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            device_state = result.get("deviceState", [])
            
            if device_state and len(device_state) > 0:
                state = device_state[0]
                
                if "states" in state:
                    states = state["states"]
                    print(f"   ✅ SmartThings state retrieved:")
                    
                    for s in states:
                        attr = s.get("attribute")
                        value = s.get("value")
                        print(f"      - {attr}: {value}")
                    
                    # Check if contact is "open" (ABSENT)
                    contact_state = next((s for s in states if s.get("attribute") == "contact"), None)
                    if contact_state:
                        contact_value = contact_state.get("value")
                        if contact_value == "open":
                            print(f"\n   ✅ SUCCESS! {device_name} shows as 'open' (in use) in SmartThings")
                            return True
                        else:
                            print(f"\n   ⚠️ {device_name} shows as '{contact_value}' (expected 'open')")
                            print(f"   💡 Try refreshing SmartThings mobile app")
                            return False
                else:
                    print(f"   ❌ No states in response")
                    return False
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def reset_device(device_name):
    """Reset device back to PRESENT state"""
    device = DEVICES[device_name]
    port = device["port"]
    
    print(f"\n🔄 Resetting {device_name} to PRESENT...")
    try:
        url = f"http://localhost:{port}/interaction"
        payload = {"action": "putdown"}
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            print(f"   ✅ {device_name} reset to PRESENT")
        else:
            print(f"   ⚠️ Reset failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Reset error: {e}")


def main():
    print("\n" + "="*80)
    print("🧪 BLENDER GAME ENGINE → SMARTTHINGS INTEGRATION TEST")
    print("="*80)
    print("\nThis test simulates what happens when Blender Game Engine calls:")
    print("  turn_device_on('Phone')  # or any other device")
    print("\nExpected flow:")
    print("  1. BGE calls /interaction endpoint (pickup/use)")
    print("  2. Container updates its state (PRESENT → ABSENT)")
    print("  3. BGE calls sync_device_state_to_smartthings()")
    print("  4. Cloud server notifies SmartThings via callback")
    print("  5. SmartThings app shows device as 'Open' (in use)")
    print("\n" + "="*80 + "\n")
    
    # Test Phone
    success_phone = test_device_interaction_flow("Phone")
    
    # Reset Phone
    reset_device("Phone")
    
    # Summary
    print("\n\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"   Phone Integration: {'✅ PASS' if success_phone else '❌ FAIL'}")
    print("="*80)
    
    if success_phone:
        print("\n🎉 Integration test PASSED!")
        print("\n✅ Blender Game Engine is ready to sync device states to SmartThings")
        print("\n📱 Usage in Blender:")
        print("   from bge_docker_integration import turn_device_on, turn_device_off")
        print("   turn_device_on('Phone')   # Pickup phone → SmartThings shows 'Open'")
        print("   turn_device_off('Phone')  # Put down → SmartThings shows 'Closed'")
    else:
        print("\n⚠️ Integration test had issues")
        print("\n💡 Manual refresh may be needed in SmartThings app:")
        print("   1. Open SmartThings mobile app")
        print("   2. Go to Devices tab")
        print("   3. Pull down to refresh")


if __name__ == "__main__":
    main()
