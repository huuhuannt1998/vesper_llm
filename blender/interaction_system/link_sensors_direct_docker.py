"""
Direct Docker Container Mapping Script
Parse running Docker containers and map them directly to item sensors
This bypasses the backend console API
"""

import subprocess
import json
import re
import sys
import os

# Add interaction_system to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from device_docker_integration import get_device_docker_bridge
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    print("❌ Docker integration not available")
    sys.exit(1)


def parse_container_name(container_name):
    """
    Parse container name to extract device info
    
    Format: <device>-<type>-<serial>
    Examples:
        phone-item-sensor-VSI-DF8A-CE65-08F5
        bathroomsink1-item-sensor-VSI-A699-1704-65F5
        kitchensink-item-sensor-VSI-7A48-71F9-D909
    
    Returns:
        dict with device_name, device_type, serial, room (guessed)
    """
    # Pattern: <name>-<type>-<serial>
    pattern = r'^(.+?)-(item-sensor|motion-sensor|thermostat|appliance-controller)-(.+)$'
    match = re.match(pattern, container_name)
    
    if not match:
        return None
    
    device_name = match.group(1)
    device_type = match.group(2)
    serial = match.group(3)
    
    # Guess room from device name
    room = "unknown"
    device_name_lower = device_name.lower()
    
    if "kitchen" in device_name_lower or device_name_lower in ["stove", "fridge", "microwave", "coffemaker", "kettle", "sink"]:
        room = "Kitchen"
    elif "bathroom" in device_name_lower or device_name_lower in ["bathroomsink", "shower", "toilet", "medicine"]:
        room = "Bathroom"
    elif "dining" in device_name_lower or device_name_lower in ["diningtable", "phone"]:
        room = "DiningRoom"
    elif "bedroom" in device_name_lower or device_name_lower in ["bed", "closet", "lamp"]:
        room = "Bedroom"
    elif "living" in device_name_lower or device_name_lower in ["tv", "couch", "book"]:
        room = "LivingRoom"
    
    # Special handling for multi-word devices
    if "kitchensink" in device_name_lower:
        device_name = "KitchenSink"
        room = "Kitchen"
    elif "bathroomsink" in device_name_lower:
        device_name = "BathroomSink"
        room = "Bathroom"
    elif "diningtable" in device_name_lower:
        device_name = "DiningTable"
        room = "DiningRoom"
    else:
        # Capitalize first letter
        device_name = device_name.capitalize()
    
    return {
        "device_name": device_name,
        "device_type": device_type,
        "serial": serial,
        "room": room
    }


def get_running_item_sensor_containers():
    """
    Get all running item sensor containers with their port mappings
    
    Returns:
        list of dicts with container info
    """
    print("\n" + "="*70)
    print("SCANNING DOCKER CONTAINERS FOR ITEM SENSORS")
    print("="*70 + "\n")
    
    try:
        # Get all running containers
        result = subprocess.run(
            ["docker", "ps", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"❌ Docker error: {result.stderr}")
            return []
        
        lines = result.stdout.strip().split('\n')
        containers = [json.loads(line) for line in lines if line]
        
        # Filter for item sensor containers with proper names
        item_sensors = []
        
        for container in containers:
            name = container['Names']
            
            # Skip containers without proper naming
            if not re.match(r'^.+-(item-sensor|motion-sensor)-VSI-.+$', name):
                continue
            
            # Parse container name
            info = parse_container_name(name)
            if not info:
                continue
            
            # Get detailed container info for port mapping
            inspect_result = subprocess.run(
                ["docker", "inspect", name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if inspect_result.returncode == 0:
                inspect_data = json.loads(inspect_result.stdout)[0]
                network_settings = inspect_data['NetworkSettings']
                ports = network_settings.get('Ports', {})
                
                # Extract host port (usually 9201, 9202, etc.)
                host_port = None
                for internal_port, mappings in ports.items():
                    if mappings and '8000/tcp' in internal_port:
                        host_port = int(mappings[0]['HostPort'])
                        break
                
                if host_port:
                    info['container_name'] = name
                    info['port'] = host_port
                    info['status'] = container['State']
                    item_sensors.append(info)
                    
                    print(f"✅ Found: {info['device_name']}")
                    print(f"   Serial: {info['serial']}")
                    print(f"   Port: {info['port']}")
                    print(f"   Room: {info['room']}")
                    print(f"   Type: {info['device_type']}")
                    print()
        
        return item_sensors
        
    except Exception as e:
        print(f"❌ Error scanning containers: {e}")
        import traceback
        traceback.print_exc()
        return []


def link_sensors_to_docker_containers():
    """
    Link item sensors directly to Docker containers
    by parsing container names
    """
    if not INTEGRATION_AVAILABLE:
        return False
    
    # Get running item sensor containers
    containers = get_running_item_sensor_containers()
    
    if not containers:
        print("⚠️ No item sensor containers found with proper naming")
        return False
    
    print("\n" + "="*70)
    print("LINKING ITEM SENSORS TO DOCKER CONTAINERS")
    print("="*70 + "\n")
    
    # Get Docker bridge
    bridge = get_device_docker_bridge()
    
    # Map our item sensors to containers
    sensor_mappings = {
        "Phone": {"preferred_room": "DiningRoom", "sensor_id": "I008"},
        "BathroomSink": {"preferred_room": "Bathroom", "sensor_id": "I010"},
        "KitchenSink": {"preferred_room": "Kitchen", "sensor_id": "I001"},
        "Stove": {"preferred_room": "Kitchen", "sensor_id": "I002"},
        "DiningTable": {"preferred_room": "DiningRoom", "sensor_id": "I009"}
    }
    
    linked_count = 0
    
    for sensor_name, sensor_info in sensor_mappings.items():
        # Find matching container
        matched_container = None
        
        for container in containers:
            # Match by device name and room
            if (container['device_name'].lower() == sensor_name.lower() or
                container['device_name'].lower().replace(' ', '') == sensor_name.lower().replace(' ', '')):
                
                # Prefer room match if available
                if container['room'] == sensor_info['preferred_room']:
                    matched_container = container
                    break
                elif not matched_container:  # Use as fallback
                    matched_container = container
        
        if matched_container:
            # Check container health
            is_healthy = bridge.check_container_health(
                matched_container['serial'],
                matched_container['port']
            )
            
            # Link sensor to container
            bridge.device_states[sensor_name] = {
                "serial": matched_container['serial'],
                "port": matched_container['port'],
                "in_use": False,
                "healthy": is_healthy,
                "room": matched_container['room'],
                "device_type": matched_container['device_type'],
                "sensor_id": sensor_info['sensor_id'],
                "container_name": matched_container['container_name'],
                "linked_at": __import__('time').time()
            }
            
            health_status = "✅ HEALTHY" if is_healthy else "❌ UNHEALTHY"
            print(f"✅ LINKED: {sensor_name} ({sensor_info['sensor_id']}) → {matched_container['serial']}:{matched_container['port']} {health_status}")
            linked_count += 1
        else:
            print(f"⚠️ NO MATCH: {sensor_name} - no matching container found")
    
    print("\n" + "="*70)
    print(f"LINKING COMPLETE: {linked_count}/{len(sensor_mappings)} sensors linked")
    print("="*70 + "\n")
    
    if linked_count > 0:
        print("✅ Item sensors are now linked to Docker containers")
        print("   Interactions will trigger virtual sensors in containers\n")
        
        # Print summary
        print("📊 Linked Devices:")
        for sensor_name, state in bridge.device_states.items():
            print(f"   {sensor_name} → port {state['port']} ({state['room']})")
        
        return True
    else:
        print("⚠️ No sensors were linked")
        return False


if __name__ == "__main__":
    success = link_sensors_to_docker_containers()
    
    if success:
        print("\n✅ Direct container mapping successful!")
        print("   You can now use these mappings in BGE")
    else:
        print("\n❌ Container mapping failed")
        print("   Check that containers are running with proper names")
