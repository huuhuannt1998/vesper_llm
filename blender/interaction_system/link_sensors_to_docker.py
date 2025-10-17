"""
VESPER Item Sensor to Docker Container Linking Script
Automatically links item sensors (Phone, Stove, etc.) to active Docker containers
"""

import sys
import os

# Add interaction_system to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from device_docker_integration import get_device_docker_bridge
    import requests
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    print("❌ Docker integration not available")
    sys.exit(1)


def link_item_sensors_to_containers():
    """
    Link item sensors to Docker containers
    Queries backend for active devices and maps them to item sensors
    """
    print("\n" + "="*70)
    print("LINKING ITEM SENSORS TO DOCKER CONTAINERS")
    print("="*70 + "\n")
    
    bridge = get_device_docker_bridge()
    
    # Check backend health
    if not bridge.check_backend_health():
        print("❌ Backend console not reachable at http://localhost:8088")
        print("   Make sure backend-console is running")
        return False
    
    print("✅ Backend console is reachable\n")
    
    # Get active devices
    try:
        response = requests.get(f"{bridge.backend_api}/api/console/devices", timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to get devices: status {response.status_code}")
            return False
        
        devices = response.json()
        
        if not devices:
            print("⚠️ No active devices found")
            print("   Spawn devices using the backend console web UI or virtual_device_manager.py")
            return False
        
        print(f"📱 Found {len(devices)} active devices:\n")
        
        # Group devices by type
        devices_by_type = {}
        for device in devices:
            device_type = device.get("device_type", "unknown")
            serial = device.get("serial_number", "unknown")
            port = device.get("container_port", "unknown")
            room = device.get("room", "unknown")
            
            if device_type not in devices_by_type:
                devices_by_type[device_type] = []
            
            devices_by_type[device_type].append({
                "serial": serial,
                "port": port,
                "room": room
            })
            
            print(f"   - {device_type.upper()} | Serial: {serial} | Port: {port} | Room: {room}")
        
        print("\n" + "-"*70)
        print("LINKING ITEM SENSORS TO CONTAINERS")
        print("-"*70 + "\n")
        
        # Define item sensor to device type mapping with room preferences
        sensor_mappings = [
            {
                "sensor": "Phone",
                "device_type": "smart_speaker",
                "preferred_room": "DiningRoom",
                "fallback_room": None
            },
            {
                "sensor": "BathroomSink",
                "device_type": "smart_faucet",
                "preferred_room": "Bathroom",
                "fallback_room": None
            },
            {
                "sensor": "KitchenSink",
                "device_type": "smart_faucet",
                "preferred_room": "Kitchen",
                "fallback_room": None
            },
            {
                "sensor": "Stove",
                "device_type": "thermostat",
                "preferred_room": "Kitchen",
                "fallback_room": None
            },
            {
                "sensor": "DiningTable",
                "device_type": "motion_sensor",
                "preferred_room": "DiningRoom",
                "fallback_room": None
            }
        ]
        
        linked_count = 0
        
        for mapping in sensor_mappings:
            sensor_name = mapping["sensor"]
            device_type = mapping["device_type"]
            preferred_room = mapping["preferred_room"]
            
            # Find matching device
            if device_type in devices_by_type:
                # Try to match by room first
                matching_device = None
                
                for device in devices_by_type[device_type]:
                    if device["room"].lower() == preferred_room.lower():
                        matching_device = device
                        break
                
                # Fallback: use first available device of this type
                if not matching_device and devices_by_type[device_type]:
                    matching_device = devices_by_type[device_type][0]
                
                if matching_device:
                    # Check container health
                    is_healthy = bridge.check_container_health(
                        matching_device["serial"],
                        matching_device["port"]
                    )
                    
                    # Link sensor to container
                    bridge.device_states[sensor_name] = {
                        "serial": matching_device["serial"],
                        "port": matching_device["port"],
                        "in_use": False,
                        "healthy": is_healthy,
                        "room": matching_device["room"],
                        "device_type": device_type,
                        "linked_at": __import__('time').time()
                    }
                    
                    health_status = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
                    print(f"✅ LINKED: {sensor_name} → {matching_device['serial']}:{matching_device['port']} ({device_type}) {health_status}")
                    linked_count += 1
                else:
                    print(f"⚠️ NO MATCH: {sensor_name} (no {device_type} available)")
            else:
                print(f"⚠️ NO MATCH: {sensor_name} (no {device_type} devices found)")
        
        print("\n" + "="*70)
        print(f"LINKING COMPLETE: {linked_count}/{len(sensor_mappings)} sensors linked")
        print("="*70 + "\n")
        
        if linked_count > 0:
            print("✅ Item sensors are now linked to Docker containers")
            print("   Interactions will be tracked and devices will be flagged during use")
            print("   Time tracking will record usage duration for each device\n")
            return True
        else:
            print("⚠️ No sensors were linked - spawn more devices or check device types\n")
            return False
        
    except Exception as e:
        print(f"❌ Error linking sensors: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_current_links():
    """Print currently linked sensors and their container status"""
    bridge = get_device_docker_bridge()
    
    if not bridge.device_states:
        print("⚠️ No item sensors are currently linked to Docker containers")
        print("   Run link_item_sensors_to_containers() first")
        return
    
    print("\n" + "="*70)
    print("CURRENT ITEM SENSOR → DOCKER CONTAINER LINKS")
    print("="*70 + "\n")
    
    for sensor_name, state in bridge.device_states.items():
        serial = state.get("serial", "N/A")
        port = state.get("port", "N/A")
        device_type = state.get("device_type", "unknown")
        in_use = state.get("in_use", False)
        healthy = state.get("healthy", False)
        room = state.get("room", "unknown")
        
        status_icon = "🔴" if in_use else "🟢"
        health_icon = "✅" if healthy else "❌"
        
        print(f"{status_icon} {sensor_name} ({room})")
        print(f"   → Container: {serial}:{port} ({device_type})")
        print(f"   → Status: {'IN USE' if in_use else 'AVAILABLE'} | Health: {health_icon}")
        print()
    
    print("="*70 + "\n")


if __name__ == "__main__":
    if INTEGRATION_AVAILABLE:
        success = link_item_sensors_to_containers()
        
        if success:
            print("\n📊 Current link status:")
            print_current_links()
    else:
        print("Docker integration not available")
