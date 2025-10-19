"""
BGE Docker Integration for Virtual Smart Home
Connects Blender Game Engine with Docker container virtual devices
Uses REST API protocol for device interaction (pickup, putdown, use)
"""

import bge
import time
import requests
import json

# Import Docker bridge
try:
    from interaction_system.device_docker_integration import get_device_docker_bridge
    # Use direct Docker container mapping instead of backend API
    from interaction_system.link_sensors_direct_docker import link_sensors_to_docker_containers
    DOCKER_BRIDGE_AVAILABLE = True
except ImportError:
    DOCKER_BRIDGE_AVAILABLE = False
    print("⚠️ Docker bridge not available")

# Import virtual device manager
try:
    from virtual_device_manager import VirtualDeviceManager
    DEVICE_MANAGER_AVAILABLE = True
except ImportError:
    DEVICE_MANAGER_AVAILABLE = False
    print("⚠️ Virtual device manager not available")

# Device port mappings (based on running containers)
DEVICE_PORT_MAP = {
    "Phone": 9201,
    "BathroomSink1": 9202,
    "Stove": 9203,
    "DiningTable": 9204,
    "KitchenSink": 9205,
    "BathroomSink2": 9206,
    # Add more devices as needed
}

# Device type mappings
DEVICE_TYPE_MAP = {
    "Phone": "communication",
    "BathroomSink1": "fixture",
    "BathroomSink2": "fixture",
    "Stove": "appliance",
    "DiningTable": "furniture",
    "KitchenSink": "fixture",
}

# Track device ON/OFF status in BGE
# This provides a simplified view: ON = device is being used, OFF = device is idle
DEVICE_STATUS = {}  # Will store {"Phone": "ON", "Stove": "OFF", ...}


def initialize_docker_integration_for_bge():
    """
    Initialize Docker integration for BGE
    Sets up connection between Blender objects and Docker containers
    """
    print("\n" + "="*70)
    print("🐳 INITIALIZING DOCKER VIRTUAL SMART HOME INTEGRATION")
    print("="*70 + "\n")
    
    if not DOCKER_BRIDGE_AVAILABLE:
        print("❌ Docker bridge not available - skipping integration")
        return False
    
    try:
        # Get Docker bridge instance
        bridge = get_device_docker_bridge()
        bge.logic.docker_bridge = bridge
        
        # Check backend health (optional - not required for direct Docker mapping)
        backend_available = bridge.check_backend_health()
        if backend_available:
            print("✅ Backend console is reachable at http://localhost:8088")
        else:
            print("⚠️ Backend console not reachable - using direct Docker container mapping")
        
        # Link item sensors to Docker containers using direct container scanning
        print("\n🔗 Linking item sensors to Docker containers...")
        print("   Scanning Docker containers directly (bypassing backend API)...\n")
        success = link_sensors_to_docker_containers()
        
        if not success:
            print("⚠️ Some sensors could not be linked")
            print("   Check if Docker containers are running with proper names")
            print("   Expected format: <device>-item-sensor-<serial>")
            return False
        
        print("\n✅ Docker integration initialized successfully!")
        print("   Item sensors linked to virtual devices via direct container mapping")
        print("   Interactions will trigger Docker containers\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing Docker integration: {e}")
        import traceback
        traceback.print_exc()
        return False


def trigger_virtual_device_on_interaction(object_name, action="use", state_on=True):
    """
    Trigger virtual device when actor interacts with object using REST API
    Also updates ON/OFF status for simplified tracking
    
    Args:
        object_name: Name of object being interacted with (Phone, Stove, etc.)
        action: Type of interaction ("pickup", "putdown", "use")
        state_on: True for interaction start, False for interaction end (DEPRECATED - use action instead)
    
    Returns:
        bool: True if device triggered successfully
    """
    # Map object name to port
    port = DEVICE_PORT_MAP.get(object_name)
    
    if not port:
        print(f"⚠️ No port mapping found for {object_name}")
        return False
    
    # Determine action based on state_on if action is still "use"
    if action == "use" and not state_on:
        action = "putdown"
    
    # Determine ON/OFF status based on action
    # ON = device is being actively used (pickup or use)
    # OFF = device is idle (putdown)
    if action in ["pickup", "use"]:
        new_status = "ON"
    else:  # putdown
        new_status = "OFF"
    
    # Send interaction to device via REST API
    try:
        url = f"http://localhost:{port}/interaction"
        payload = {"action": action}
        
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            result = response.json()
            
            # Update ON/OFF status
            DEVICE_STATUS[object_name] = new_status
            
            # Store status in bge.logic for persistence
            if not hasattr(bge.logic, 'device_status'):
                bge.logic.device_status = {}
            bge.logic.device_status[object_name] = new_status
            
            print(f"✅ {object_name} - {action}: {result.get('new_presence', 'OK')} [Status: {new_status}]")
            
            # Store last interaction in bge.logic for tracking
            if not hasattr(bge.logic, 'device_interactions'):
                bge.logic.device_interactions = []
            
            bge.logic.device_interactions.append({
                "object": object_name,
                "action": action,
                "status": new_status,
                "timestamp": time.time(),
                "response": result
            })
            
            return True
        else:
            print(f"❌ {object_name} interaction failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error triggering {object_name}: {e}")
        return False


def update_device_status(object_name, presence_state="PRESENT"):
    """
    Manually update device presence status
    
    Args:
        object_name: Name of object (Phone, Stove, etc.)
        presence_state: "PRESENT", "ABSENT", or "in_use"
    
    Returns:
        bool: True if update successful
    """
    port = DEVICE_PORT_MAP.get(object_name)
    
    if not port:
        print(f"⚠️ No port mapping found for {object_name}")
        return False
    
    try:
        url = f"http://localhost:{port}/manual_update"
        payload = {"presence": presence_state}
        
        response = requests.post(url, json=payload, timeout=2)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {object_name} status updated: {presence_state}")
            return True
        else:
            print(f"❌ Status update failed: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating {object_name}: {e}")
        return False


def get_device_state(object_name):
    """
    Get current state of virtual device
    
    Args:
        object_name: Name of object
    
    Returns:
        dict: Device state or None
    """
    port = DEVICE_PORT_MAP.get(object_name)
    
    if not port:
        return None
    
    try:
        url = f"http://localhost:{port}/state"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None


def trigger_virtual_device_on_interaction_legacy(object_name, state_on=True):
    """
    LEGACY: Trigger virtual device when actor interacts with object
    This function is kept for backward compatibility
    Use trigger_virtual_device_on_interaction() with action parameter instead
    
    Args:
        object_name: Name of object being interacted with (Phone, Stove, etc.)
        state_on: True for interaction start (ON), False for interaction end (OFF)
    
    Returns:
        bool: True if device triggered successfully
    """
    # Translate state_on to action
    action = "use" if state_on else "putdown"
    return trigger_virtual_device_on_interaction(object_name, action=action, state_on=state_on)


def check_virtual_device_health(object_name):
    """
    Check if Docker container for object is healthy
    
    Args:
        object_name: Name of object
    
    Returns:
        bool: True if container is healthy
    """
    port = DEVICE_PORT_MAP.get(object_name)
    
    if not port:
        return True  # Allow interaction if not mapped
    
    try:
        url = f"http://localhost:{port}/health"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            health_data = response.json()
            return health_data.get("status") == "healthy"
        else:
            return False
            
    except requests.exceptions.RequestException:
        return False  # Container not reachable


def get_virtual_device_status_summary():
    """
    Get summary of all virtual device states via REST API
    
    Returns:
        dict: Status summary
    """
    summary = {
        "available": True,
        "devices": {},
        "healthy_count": 0,
        "in_use_count": 0,
        "present_count": 0,
        "absent_count": 0
    }
    
    for device_name, port in DEVICE_PORT_MAP.items():
        try:
            # Get device state
            state_url = f"http://localhost:{port}/state"
            state_response = requests.get(state_url, timeout=2)
            
            # Get device health
            health_url = f"http://localhost:{port}/health"
            health_response = requests.get(health_url, timeout=2)
            
            state_data = state_response.json() if state_response.status_code == 200 else {}
            health_data = health_response.json() if health_response.status_code == 200 else {}
            
            presence = state_data.get("presence", "UNKNOWN")
            is_healthy = health_data.get("status") == "healthy"
            
            summary["devices"][device_name] = {
                "presence": presence,
                "healthy": is_healthy,
                "port": port,
                "item_type": state_data.get("item_type", "unknown"),
                "interaction_count": state_data.get("interaction_count", 0),
                "last_interaction": state_data.get("last_interaction")
            }
            
            if is_healthy:
                summary["healthy_count"] += 1
            if presence == "in_use":
                summary["in_use_count"] += 1
            if presence == "PRESENT":
                summary["present_count"] += 1
            if presence == "ABSENT":
                summary["absent_count"] += 1
                
        except Exception as e:
            summary["devices"][device_name] = {
                "error": str(e),
                "port": port
            }
    
    return summary


def export_docker_tracking_on_exit():
    """
    Export Docker tracking data when simulation ends
    Should be called at end of navigation
    """
    # Export interaction log
    if hasattr(bge.logic, 'device_interactions'):
        try:
            # Get output directory
            if hasattr(bge.logic, 'interaction_system'):
                output_dir = bge.logic.interaction_system.item_sensor_manager.dataset_dir
            else:
                output_dir = "vesper_logs"
            
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            log_file = os.path.join(output_dir, f"device_interactions_{int(time.time())}.json")
            
            with open(log_file, 'w') as f:
                json.dump(bge.logic.device_interactions, f, indent=2)
            
            print(f"\n✅ Device interactions exported to: {log_file}")
            print(f"   Total interactions: {len(bge.logic.device_interactions)}")
            
        except Exception as e:
            print(f"❌ Error exporting device interactions: {e}")
    
    # Print summary
    print_device_interaction_summary()


def print_device_interaction_summary():
    """Print summary of device interactions during session"""
    if not hasattr(bge.logic, 'device_interactions'):
        print("\nNo device interactions recorded")
        return
    
    interactions = bge.logic.device_interactions
    
    print("\n" + "="*70)
    print("📊 DEVICE INTERACTION SUMMARY")
    print("="*70)
    print(f"Total Interactions: {len(interactions)}\n")
    
    # Count by device
    device_counts = {}
    action_counts = {"pickup": 0, "putdown": 0, "use": 0}
    
    for interaction in interactions:
        obj = interaction["object"]
        action = interaction["action"]
        
        device_counts[obj] = device_counts.get(obj, 0) + 1
        action_counts[action] = action_counts.get(action, 0) + 1
    
    print("By Device:")
    for device, count in sorted(device_counts.items()):
        print(f"  - {device}: {count} interactions")
    
    print("\nBy Action:")
    for action, count in action_counts.items():
        print(f"  - {action}: {count} times")
    
    print("="*70 + "\n")


# Convenience functions for specific interaction types
def pickup_item(object_name):
    """
    Actor picks up an item (item becomes ABSENT)
    
    Args:
        object_name: Name of item to pickup
    
    Returns:
        bool: Success status
    """
    print(f"🖐️  Picking up {object_name}...")
    return trigger_virtual_device_on_interaction(object_name, action="pickup")


def putdown_item(object_name):
    """
    Actor puts down an item (item becomes PRESENT)
    
    Args:
        object_name: Name of item to putdown
    
    Returns:
        bool: Success status
    """
    print(f"🤚 Putting down {object_name}...")
    return trigger_virtual_device_on_interaction(object_name, action="putdown")


def use_item(object_name):
    """
    Actor uses an item (item becomes in_use)
    
    Args:
        object_name: Name of item to use
    
    Returns:
        bool: Success status
    """
    print(f"🔧 Using {object_name}...")
    return trigger_virtual_device_on_interaction(object_name, action="use")


# ============================================================================
# ON/OFF STATUS FUNCTIONS
# Simplified interface for device status management
# ============================================================================

def turn_device_on(object_name):
    """
    Turn device ON (flags it as being used)
    Equivalent to pickup (for portable items) or use (for fixtures)
    
    Args:
        object_name: Name of device to turn ON
    
    Returns:
        bool: Success status
    
    Example:
        turn_device_on("Phone")  # Phone is now ON (being used)
        turn_device_on("Stove")  # Stove is now ON (turned on)
    """
    # Determine action type based on device type
    device_type = DEVICE_TYPE_MAP.get(object_name, "unknown")
    
    if device_type == "communication":
        # Portable items use pickup
        action = "pickup"
        print(f"🔛 Turning {object_name} ON (pickup)...")
    else:
        # Fixtures and appliances use "use"
        action = "use"
        print(f"🔛 Turning {object_name} ON (activating)...")
    
    return trigger_virtual_device_on_interaction(object_name, action=action)


def turn_device_off(object_name):
    """
    Turn device OFF (flags it as idle/not in use)
    Always uses putdown action
    
    Args:
        object_name: Name of device to turn OFF
    
    Returns:
        bool: Success status
    
    Example:
        turn_device_off("Phone")  # Phone is now OFF (put down)
        turn_device_off("Stove")  # Stove is now OFF (turned off)
    """
    print(f"⏹️  Turning {object_name} OFF...")
    return trigger_virtual_device_on_interaction(object_name, action="putdown")


def get_device_on_off_status(object_name):
    """
    Get ON/OFF status of a device
    
    Args:
        object_name: Name of device
    
    Returns:
        str: "ON", "OFF", or "UNKNOWN"
    
    Example:
        status = get_device_on_off_status("Phone")
        if status == "ON":
            print("Phone is being used")
    """
    # Check bge.logic first
    if hasattr(bge.logic, 'device_status'):
        return bge.logic.device_status.get(object_name, "UNKNOWN")
    
    # Check module-level dict
    return DEVICE_STATUS.get(object_name, "UNKNOWN")


def get_all_devices_on_off_status():
    """
    Get ON/OFF status of all devices
    
    Returns:
        dict: Device name -> "ON"/"OFF"/"UNKNOWN"
    
    Example:
        statuses = get_all_devices_on_off_status()
        for device, status in statuses.items():
            print(f"{device}: {status}")
    """
    all_statuses = {}
    
    # Get from bge.logic if available
    if hasattr(bge.logic, 'device_status'):
        all_statuses.update(bge.logic.device_status)
    else:
        all_statuses.update(DEVICE_STATUS)
    
    # Add any devices not yet tracked
    for device_name in DEVICE_PORT_MAP.keys():
        if device_name not in all_statuses:
            all_statuses[device_name] = "UNKNOWN"
    
    return all_statuses


def print_device_on_off_status():
    """
    Print ON/OFF status of all devices to console
    
    Example output:
        📊 DEVICE ON/OFF STATUS
        ✅ Phone: ON
        ⚫ Stove: OFF
        ❓ KitchenSink: UNKNOWN
    """
    print("\n" + "="*70)
    print("📊 DEVICE ON/OFF STATUS")
    print("="*70)
    
    statuses = get_all_devices_on_off_status()
    
    on_count = 0
    off_count = 0
    unknown_count = 0
    
    for device_name, status in sorted(statuses.items()):
        if status == "ON":
            icon = "🔛"
            on_count += 1
        elif status == "OFF":
            icon = "⏹️ "
            off_count += 1
        else:
            icon = "❓"
            unknown_count += 1
        
        print(f"{icon} {device_name:20s}: {status}")
    
    print("-" * 70)
    print(f"Summary: {on_count} ON | {off_count} OFF | {unknown_count} UNKNOWN")
    print("="*70 + "\n")


def turn_all_devices_off():
    """
    Turn OFF all devices
    Useful for resetting state or ending simulation
    
    Returns:
        dict: Results for each device
    
    Example:
        results = turn_all_devices_off()
        print(f"Turned off {sum(results.values())} devices")
    """
    print("\n🔄 Turning OFF all devices...")
    
    results = {}
    for device_name in DEVICE_PORT_MAP.keys():
        success = turn_device_off(device_name)
        results[device_name] = success
    
    success_count = sum(results.values())
    print(f"\n✅ Turned OFF {success_count}/{len(results)} devices")
    
    return results


def initialize_all_devices_off():
    """
    Initialize all devices to OFF state
    Call this at the start of simulation
    
    Returns:
        bool: True if all devices initialized
    """
    print("\n🔧 Initializing all devices to OFF state...")
    
    # Set all to OFF in tracking
    for device_name in DEVICE_PORT_MAP.keys():
        DEVICE_STATUS[device_name] = "OFF"
        
        if not hasattr(bge.logic, 'device_status'):
            bge.logic.device_status = {}
        bge.logic.device_status[device_name] = "OFF"
    
    print(f"✅ Initialized {len(DEVICE_PORT_MAP)} devices to OFF")
    return True


def get_casas_events(object_name):
    """
    Get CASAS format events from device
    
    Args:
        object_name: Name of device
    
    Returns:
        list: CASAS events or empty list
    """
    port = DEVICE_PORT_MAP.get(object_name)
    
    if not port:
        return []
    
    try:
        url = f"http://localhost:{port}/casas_events"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("events", [])
        else:
            return []
            
    except requests.exceptions.RequestException:
        return []


def export_all_casas_events(output_dir="vesper_logs"):
    """
    Export CASAS events from all devices
    
    Args:
        output_dir: Directory to save events
    
    Returns:
        str: Path to exported file
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    all_events = []
    
    for device_name in DEVICE_PORT_MAP.keys():
        events = get_casas_events(device_name)
        all_events.extend(events)
    
    # Sort by timestamp
    all_events.sort(key=lambda x: x.get("timestamp", ""))
    
    # Export to file
    output_file = os.path.join(output_dir, f"casas_events_{int(time.time())}.txt")
    
    with open(output_file, 'w') as f:
        for event in all_events:
            f.write(event + "\n")
    
    print(f"\n✅ CASAS events exported to: {output_file}")
    print(f"   Total events: {len(all_events)}")
    
    return output_file


def spawn_virtual_devices_for_scene():
    """
    Automatically spawn virtual devices for current scene
    Only use this if no devices exist yet
    """
    if not DEVICE_MANAGER_AVAILABLE:
        print("⚠️ Virtual device manager not available")
        return False
    
    try:
        manager = VirtualDeviceManager()
        
        # Check if backend is available
        if not manager.check_backend_health():
            print("⚠️ Backend not available - cannot spawn devices")
            return False
        
        # Get current devices
        current_devices = manager.get_active_devices()
        
        if len(current_devices) >= 5:
            print(f"✅ {len(current_devices)} devices already active - no need to spawn")
            return True
        
        print(f"📱 Only {len(current_devices)} devices active - spawning more...")
        
        # Spawn devices (one per sensor type needed)
        device_configs = [
            "medium_house_efficient",  # Has multiple device types
        ]
        
        spawned = []
        for config in device_configs:
            device_info = manager.spawn_device(username="admin", config_type=config)
            if device_info:
                spawned.append(device_info.get("serial_number"))
                time.sleep(2)  # Wait between spawns
        
        print(f"✅ Spawned {len(spawned)} virtual devices: {spawned}")
        return len(spawned) > 0
        
    except Exception as e:
        print(f"❌ Error spawning devices: {e}")
        return False


# Convenience accessors
def get_docker_bridge():
    """Get global Docker bridge instance"""
    return getattr(bge.logic, 'docker_bridge', None)


def is_docker_integration_active():
    """Check if Docker integration is active"""
    return hasattr(bge.logic, 'docker_bridge') and bge.logic.docker_bridge is not None
