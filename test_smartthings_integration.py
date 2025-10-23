"""
Test SmartThings Integration
Verifies that device interactions propagate from Docker containers to SmartThings cloud
"""

import requests
import json
import time

# Device mappings from Docker containers
DEVICES = {
    "Phone": {
        "port": 9201,
        "device_id": "VSI-DF8A-CE65-08F5",
        "friendly_name": "Virtual Item Sensor 08F5"
    },
    "Stove": {
        "port": 9203,
        "device_id": "VSI-F6AF-676E-2BBD",
        "friendly_name": "Virtual Item Sensor 2BBD"
    },
    "DiningTable": {
        "port": 9204,
        "device_id": "VSI-13CB-B4F7-2611",
        "friendly_name": "Virtual Item Sensor 2611"
    },
    "KitchenSink": {
        "port": 9205,
        "device_id": "VSI-7A48-71F9-D909",
        "friendly_name": "Virtual Item Sensor D909"
    },
    "BathroomSink1": {
        "port": 9202,
        "device_id": "VSI-A699-1704-65F5",
        "friendly_name": "Virtual Item Sensor 65F5"
    },
    "BathroomSink2": {
        "port": 9206,
        "device_id": "VSI-1B6D-D44D-8FFC",
        "friendly_name": "Virtual Item Sensor 8FFC"
    }
}

NGROK_URL = "https://9104a04a38e2.ngrok-free.app"


def test_device_direct_api(device_name):
    """Test direct API call to device container"""
    device = DEVICES.get(device_name)
    if not device:
        print(f"❌ Device {device_name} not found")
        return False
    
    port = device["port"]
    print(f"\n{'='*60}")
    print(f"Testing {device_name} (port {port})")
    print(f"{'='*60}")
    
    try:
        # Test 1: Get device state
        print(f"\n1️⃣ Getting device state...")
        url = f"http://localhost:{port}/state"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            state = response.json()
            print(f"✅ Current state: {json.dumps(state, indent=2)}")
        else:
            print(f"❌ Failed to get state: HTTP {response.status_code}")
            return False
        
        # Test 2: Trigger interaction (pickup)
        print(f"\n2️⃣ Triggering 'pickup' interaction...")
        url = f"http://localhost:{port}/interaction"
        payload = {"action": "pickup"}
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Interaction successful: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Interaction failed: HTTP {response.status_code}")
            return False
        
        # Wait for cloud sync
        print(f"\n⏳ Waiting 2 seconds for cloud sync...")
        time.sleep(2)
        
        # Test 3: Get device state again
        print(f"\n3️⃣ Getting updated device state...")
        url = f"http://localhost:{port}/state"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            state = response.json()
            print(f"✅ Updated state: {json.dumps(state, indent=2)}")
        else:
            print(f"❌ Failed to get updated state: HTTP {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_smartthings_discovery():
    """Test SmartThings device discovery"""
    print(f"\n{'='*60}")
    print("Testing SmartThings Discovery via Schema Connector")
    print(f"{'='*60}")
    
    try:
        url = f"{NGROK_URL}/schema"
        payload = {
            "headers": {
                "schema": "st-schema",
                "version": "1.0",
                "interactionType": "discoveryRequest",
                "requestId": "test-discovery-123"
            },
            "devices": []
        }
        
        print(f"\n📡 Sending discovery request to {url}...")
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            devices = result.get("devices", [])
            
            print(f"✅ Discovery successful! Found {len(devices)} devices")
            print(f"\n📋 VESPER Task Devices:")
            
            for device_name, device_info in DEVICES.items():
                device_id = device_info["device_id"]
                found = any(d.get("externalDeviceId") == device_id for d in devices)
                
                if found:
                    print(f"   ✅ {device_name:15} → {device_id} (FOUND)")
                else:
                    print(f"   ❌ {device_name:15} → {device_id} (NOT FOUND)")
            
            return True
        else:
            print(f"❌ Discovery failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_device_state_query(device_name):
    """Test SmartThings state query for a device"""
    device = DEVICES.get(device_name)
    if not device:
        print(f"❌ Device {device_name} not found")
        return False
    
    device_id = device["device_id"]
    print(f"\n{'='*60}")
    print(f"Testing SmartThings State Query: {device_name}")
    print(f"{'='*60}")
    
    try:
        url = f"{NGROK_URL}/schema"
        payload = {
            "headers": {
                "schema": "st-schema",
                "version": "1.0",
                "interactionType": "stateRefreshRequest",
                "requestId": "test-state-123"
            },
            "devices": [
                {
                    "externalDeviceId": device_id,
                    "deviceCookie": {}
                }
            ]
        }
        
        print(f"\n📡 Querying state for {device_id}...")
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            device_states = result.get("deviceState", [])
            
            if device_states:
                print(f"✅ State query successful!")
                for state in device_states:
                    print(f"\n   Device: {state.get('externalDeviceId')}")
                    states = state.get('states', [])
                    for s in states:
                        cap = s.get('capability')
                        attr = s.get('attribute')
                        value = s.get('value')
                        print(f"   - {cap}.{attr} = {value}")
            else:
                print(f"⚠️ No state returned for device")
            
            return True
        else:
            print(f"❌ State query failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_full_integration_test():
    """Run complete integration test"""
    print("\n" + "="*70)
    print("🧪 SMARTTHINGS INTEGRATION TEST")
    print("="*70)
    
    # Test 1: SmartThings Discovery
    print("\n\n### TEST 1: SmartThings Device Discovery ###")
    discovery_success = test_smartthings_discovery()
    
    # Test 2: Direct device interaction
    print("\n\n### TEST 2: Direct Device Interaction (Phone) ###")
    device_success = test_device_direct_api("Phone")
    
    # Test 3: SmartThings state query
    print("\n\n### TEST 3: SmartThings State Query (Phone) ###")
    state_success = test_device_state_query("Phone")
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"   SmartThings Discovery:  {'✅ PASS' if discovery_success else '❌ FAIL'}")
    print(f"   Device Interaction:     {'✅ PASS' if device_success else '❌ FAIL'}")
    print(f"   SmartThings State Query:{'✅ PASS' if state_success else '❌ FAIL'}")
    print("="*70)
    
    if discovery_success and device_success and state_success:
        print("\n🎉 All tests passed! SmartThings integration is working correctly!")
        print("\n📱 Next steps:")
        print("   1. Open SmartThings mobile app")
        print("   2. Go to 'Devices' → 'Add Device'")
        print("   3. Search for 'VESPER Smart Home Integration'")
        print("   4. You should see all 6 devices available")
        print("   5. When Blender actor interacts with objects, device states will update in app")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    run_full_integration_test()
