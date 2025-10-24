"""
Verify All VESPER Devices Online
Tests that all 6 VESPER task devices are reporting online status to SmartThings
"""

import requests
import json

DEVICES = {
    "Phone": "VSI-DF8A-CE65-08F5",
    "Stove": "VSI-F6AF-676E-2BBD",
    "DiningTable": "VSI-13CB-B4F7-2611",
    "KitchenSink": "VSI-7A48-71F9-D909",
    "BathroomSink1": "VSI-A699-1704-65F5",
    "BathroomSink2": "VSI-1B6D-D44D-8FFC"
}

NGROK_URL = "https://9104a04a38e2.ngrok-free.app"


def check_device_online(device_name, device_id):
    """Check if a device is online and returning state"""
    try:
        url = f"{NGROK_URL}/schema"
        payload = {
            "headers": {
                "schema": "st-schema",
                "version": "1.0",
                "interactionType": "stateRefreshRequest",
                "requestId": f"verify-{device_id}"
            },
            "devices": [
                {
                    "externalDeviceId": device_id,
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
                
                # Check if device has error
                if "deviceError" in state:
                    error = state["deviceError"][0]
                    print(f"❌ {device_name:15} ({device_id}): OFFLINE - {error.get('detail')}")
                    return False
                
                # Check if device has states
                if "states" in state and len(state["states"]) > 0:
                    states = state["states"]
                    
                    # Find health status
                    health = "unknown"
                    contact = "unknown"
                    
                    for s in states:
                        if s.get("attribute") == "healthStatus":
                            health = s.get("value")
                        elif s.get("attribute") == "contact":
                            contact = s.get("value")
                    
                    status_icon = "✅" if health == "online" else "⚠️"
                    print(f"{status_icon} {device_name:15} ({device_id}): {health.upper()} - Contact: {contact}")
                    return health == "online"
                else:
                    print(f"⚠️ {device_name:15} ({device_id}): No state data")
                    return False
            else:
                print(f"❌ {device_name:15} ({device_id}): No device state in response")
                return False
        else:
            print(f"❌ {device_name:15} ({device_id}): HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {device_name:15} ({device_id}): Error - {e}")
        return False


def main():
    print("\n" + "="*80)
    print("🔍 VERIFYING ALL VESPER DEVICES ONLINE STATUS")
    print("="*80 + "\n")
    
    online_count = 0
    total_count = len(DEVICES)
    
    for device_name, device_id in DEVICES.items():
        if check_device_online(device_name, device_id):
            online_count += 1
    
    print("\n" + "="*80)
    print(f"📊 SUMMARY: {online_count}/{total_count} devices online")
    print("="*80)
    
    if online_count == total_count:
        print("\n🎉 SUCCESS! All VESPER devices are online and ready for SmartThings integration!")
        print("\n📱 Next steps:")
        print("   1. Open SmartThings mobile app")
        print("   2. Pull down to refresh device list")
        print("   3. All 6 devices should appear as 'Online'")
        print("   4. Run Blender Game Engine to test real-time synchronization")
    else:
        print(f"\n⚠️ {total_count - online_count} device(s) still offline. Check the errors above.")


if __name__ == "__main__":
    main()
