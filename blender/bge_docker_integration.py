"""
BGE Docker Integration for Virtual Smart Home
Connects Blender Game Engine with Docker container virtual devices
"""

import bge
import time

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


def trigger_virtual_device_on_interaction(object_name, state_on=True):
    """
    Trigger virtual device when actor interacts with object
    
    Args:
        object_name: Name of object being interacted with (Phone, Stove, etc.)
        state_on: True for interaction start (ON), False for interaction end (OFF)
    
    Returns:
        bool: True if device triggered successfully
    """
    if not hasattr(bge.logic, 'docker_bridge'):
        return False
    
    bridge = bge.logic.docker_bridge
    
    # Get device state (includes serial and port if linked)
    device_state = bridge.get_device_state(object_name)
    
    if not device_state.get("serial"):
        print(f"⚠️ No Docker container linked to {object_name}")
        return False
    
    # Flag device and trigger sensor
    success = bridge.flag_device_in_use(
        object_name,
        device_state["serial"],
        device_state["port"],
        in_use=state_on
    )
    
    return success


def check_virtual_device_health(object_name):
    """
    Check if Docker container for object is healthy
    
    Args:
        object_name: Name of object
    
    Returns:
        bool: True if container is healthy
    """
    if not hasattr(bge.logic, 'docker_bridge'):
        return True  # Allow interaction if Docker not available
    
    bridge = bge.logic.docker_bridge
    device_state = bridge.get_device_state(object_name)
    
    if not device_state.get("serial"):
        return True  # Allow interaction if not linked
    
    # Check container health
    is_healthy = bridge.check_container_health(
        device_state["serial"],
        device_state["port"]
    )
    
    return is_healthy


def get_virtual_device_status_summary():
    """
    Get summary of all virtual device states
    
    Returns:
        dict: Status summary
    """
    if not hasattr(bge.logic, 'docker_bridge'):
        return {"available": False}
    
    bridge = bge.logic.docker_bridge
    
    summary = {
        "available": True,
        "devices": {},
        "healthy_count": 0,
        "in_use_count": 0
    }
    
    for obj_name, state in bridge.device_states.items():
        summary["devices"][obj_name] = {
            "in_use": state.get("in_use", False),
            "healthy": state.get("healthy", False),
            "serial": state.get("serial", "N/A"),
            "port": state.get("port", "N/A")
        }
        
        if state.get("healthy"):
            summary["healthy_count"] += 1
        if state.get("in_use"):
            summary["in_use_count"] += 1
    
    return summary


def export_docker_tracking_on_exit():
    """
    Export Docker tracking data when simulation ends
    Should be called at end of navigation
    """
    if not hasattr(bge.logic, 'docker_bridge'):
        return
    
    bridge = bge.logic.docker_bridge
    
    # Get output directory from interaction system
    if hasattr(bge.logic, 'interaction_system'):
        output_dir = bge.logic.interaction_system.item_sensor_manager.dataset_dir
    else:
        output_dir = "vesper_logs"
    
    # Export tracking data
    bridge.export_device_tracking_log(output_dir)
    
    # Print summary
    bridge.print_status_summary()


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
