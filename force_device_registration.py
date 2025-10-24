"""
Force Device Registration with SmartThings
Triggers all devices to report their status to the cloud server
"""

import requests
import json
import time

DEVICES = {
    "Phone": 9201,
    "Stove": 9203,
    "DiningTable": 9204,
    "KitchenSink": 9205,
    "BathroomSink1": 9202,
    "BathroomSink2": 9206
}

NGROK_URL = "https://9104a04a38e2.ngrok-free.app"


def trigger_device_state_update(device_name, port):
    """Trigger a device to report its state"""
    print(f"\n📡 {device_name} (port {port})")
    
    try:
        # Get current state
        url = f"http://localhost:{port}/state"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            state = response.json()
            presence = state.get("presence", "UNKNOWN")
            print(f"   Current state: {presence}")
            
            # Trigger a state refresh (this should notify cloud server)
            # Try using the manual_update endpoint
            url = f"http://localhost:{port}/manual_update"
            payload = {"presence": presence}
            response = requests.post(url, json=payload, timeout=2)
            
            if response.status_code == 200:
                print(f"   ✅ State update sent to cloud server")
                return True
            else:
                print(f"   ⚠️ State update failed: HTTP {response.status_code}")
                return False
        else:
            print(f"   ❌ Failed to get state: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def trigger_smartthings_state_callback():
    """
    Trigger SmartThings to query device states
    This simulates what SmartThings does when opening the app
    """
    print(f"\n{'='*60}")
    print("📱 Triggering SmartThings State Refresh")
    print(f"{'='*60}")
    
    try:
        url = f"{NGROK_URL}/schema"
        
        # Get list of devices first
        payload = {
            "headers": {
                "schema": "st-schema",
                "version": "1.0",
                "interactionType": "discoveryRequest",
                "requestId": "force-discovery-001"
            },
            "devices": []
        }
        
        print(f"\n1️⃣ Discovering devices...")
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            devices = result.get("devices", [])
            print(f"   ✅ Found {len(devices)} devices")
            
            # Now request state for each VESPER device
            vesper_device_ids = [
                "VSI-DF8A-CE65-08F5",  # Phone
                "VSI-F6AF-676E-2BBD",  # Stove
                "VSI-13CB-B4F7-2611",  # DiningTable
                "VSI-7A48-71F9-D909",  # KitchenSink
                "VSI-A699-1704-65F5",  # BathroomSink1
                "VSI-1B6D-D44D-8FFC"   # BathroomSink2
            ]
            
            print(f"\n2️⃣ Requesting state for VESPER devices...")
            state_payload = {
                "headers": {
                    "schema": "st-schema",
                    "version": "1.0",
                    "interactionType": "stateRefreshRequest",
                    "requestId": "force-state-001"
                },
                "devices": [
                    {"externalDeviceId": device_id, "deviceCookie": {}}
                    for device_id in vesper_device_ids
                ]
            }
            
            response = requests.post(url, json=state_payload, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                device_states = result.get("deviceState", [])
                print(f"   ✅ Received state for {len(device_states)} devices")
                
                for state in device_states:
                    device_id = state.get('externalDeviceId')
                    states = state.get('states', [])
                    print(f"\n   Device: {device_id}")
                    for s in states:
                        cap = s.get('capability')
                        attr = s.get('attribute')
                        value = s.get('value')
                        print(f"      {cap}.{attr} = {value}")
                
                return True
            else:
                print(f"   ❌ State refresh failed: HTTP {response.status_code}")
                return False
        else:
            print(f"   ❌ Discovery failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n" + "="*70)
    print("🔄 FORCE DEVICE REGISTRATION WITH SMARTTHINGS")
    print("="*70)
    
    # Step 1: Update all device states
    print("\n### STEP 1: Update Device States ###")
    for device_name, port in DEVICES.items():
        trigger_device_state_update(device_name, port)
        time.sleep(0.5)
    
    print("\n⏳ Waiting 3 seconds for cloud sync...")
    time.sleep(3)
    
    # Step 2: Trigger SmartThings state refresh
    print("\n### STEP 2: Trigger SmartThings State Refresh ###")
    trigger_smartthings_state_callback()
    
    print("\n\n" + "="*70)
    print("✅ REGISTRATION COMPLETE")
    print("="*70)
    print("\n📱 Now check your SmartThings app:")
    print("   1. Open the SmartThings mobile app")
    print("   2. Go to 'Devices'")
    print("   3. Devices should now appear as 'Online'")
    print("   4. If still offline, pull down to refresh the device list")
    print("\n💡 Note: Devices may still show offline until you:")
    print("   - Add them to your SmartThings account (if not already added)")
    print("   - Or wait for the next automatic sync (typically 30-60 seconds)")


if __name__ == "__main__":
    main()
