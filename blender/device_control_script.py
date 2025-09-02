"""
BGE Device Control Script
Simple script to control virtual devices from within Blender Game Engine
Place this script on a game object and assign to Logic Bricks

Key Controls:
- S: Spawn new virtual device
- D: Delete selected device (or all if none selected)
- Q: Query/list all devices
- C: Control device (temperature)
- 1,2,3: Quick spawn different device types
"""

import bge
import mathutils

# Import our virtual device manager
try:
    # Add the blender directory to path to import our device manager
    import sys
    import os
    blender_dir = r"C:\Users\hbui11\Desktop\vesper_llm\blender"
    if blender_dir not in sys.path:
        sys.path.insert(0, blender_dir)
    
    from virtual_device_manager import virtual_device_manager, create_device_visual_in_scene, remove_device_visual_from_scene
    DEVICE_MANAGER_AVAILABLE = True
    print("✅ BGE: Virtual Device Manager loaded")
except ImportError as e:
    DEVICE_MANAGER_AVAILABLE = False
    print(f"❌ BGE: Virtual Device Manager not available: {e}")

def main():
    """Main BGE script function - call this from Always sensor"""
    controller = bge.logic.getCurrentController()
    owner = controller.owner
    scene = bge.logic.getCurrentScene()
    
    # Check if device manager is available
    if not DEVICE_MANAGER_AVAILABLE:
        return
    
    # Get keyboard input
    keyboard = bge.logic.keyboard
    
    # Initialize device counter if not exists
    if not hasattr(bge.logic, "device_spawn_count"):
        bge.logic.device_spawn_count = 0
    
    # =========================================================================
    # SPAWN DEVICES
    # =========================================================================
    
    # S key: Spawn new device (default medium house)
    if keyboard.events[bge.events.SKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: S pressed - Spawning medium house device")
        
        device = virtual_device_manager.spawn_device("admin", "medium_house_efficient")
        if device:
            # Create visual at a position based on spawn count
            spawn_pos = mathutils.Vector((bge.logic.device_spawn_count * 2, 0, 1))
            create_device_visual_in_scene(device, spawn_pos)
            bge.logic.device_spawn_count += 1
            
            print(f"✅ BGE: Spawned device {device['serial_number']}")
        else:
            print("❌ BGE: Failed to spawn device")
    
    # 1 key: Spawn small apartment (efficient)
    if keyboard.events[bge.events.ONEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: 1 pressed - Spawning small apartment (efficient)")
        
        device = virtual_device_manager.spawn_device("admin", "small_apartment_efficient")
        if device:
            spawn_pos = mathutils.Vector((bge.logic.device_spawn_count * 2, 2, 1))
            create_device_visual_in_scene(device, spawn_pos)
            bge.logic.device_spawn_count += 1
            print(f"✅ BGE: Spawned efficient apartment {device['serial_number']}")
    
    # 2 key: Spawn small apartment (inefficient)
    if keyboard.events[bge.events.TWOKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: 2 pressed - Spawning small apartment (inefficient)")
        
        device = virtual_device_manager.spawn_device("admin", "small_apartment_inefficient")
        if device:
            spawn_pos = mathutils.Vector((bge.logic.device_spawn_count * 2, -2, 1))
            create_device_visual_in_scene(device, spawn_pos)
            bge.logic.device_spawn_count += 1
            print(f"✅ BGE: Spawned inefficient apartment {device['serial_number']}")
    
    # 3 key: Spawn medium house (efficient)
    if keyboard.events[bge.events.THREEKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: 3 pressed - Spawning medium house (efficient)")
        
        device = virtual_device_manager.spawn_device("admin", "medium_house_efficient")
        if device:
            spawn_pos = mathutils.Vector((bge.logic.device_spawn_count * 2, 4, 1))
            create_device_visual_in_scene(device, spawn_pos)
            bge.logic.device_spawn_count += 1
            print(f"✅ BGE: Spawned efficient house {device['serial_number']}")
    
    # =========================================================================
    # DELETE DEVICES
    # =========================================================================
    
    # D key: Delete device(s)
    if keyboard.events[bge.events.DKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: D pressed - Deleting devices")
        
        # Check if we have a selected object (primitive selection by name)
        selected_device = None
        if hasattr(bge.logic, "spawned_devices"):
            # Try to find the most recently spawned device as "selected"
            devices = list(bge.logic.spawned_devices.keys())
            if devices:
                selected_device = devices[-1]  # Use last spawned as selected
        
        if selected_device:
            # Delete specific device
            if virtual_device_manager.delete_device(selected_device):
                remove_device_visual_from_scene(selected_device)
                print(f"✅ BGE: Deleted device {selected_device}")
            else:
                print(f"❌ BGE: Failed to delete device {selected_device}")
        else:
            # Delete all devices
            deleted_count = virtual_device_manager.cleanup_all_devices()
            print(f"🧹 BGE: Cleaned up {deleted_count} devices")
            
            # Clear visual tracking
            if hasattr(bge.logic, "spawned_devices"):
                bge.logic.spawned_devices.clear()
            bge.logic.device_spawn_count = 0
    
    # =========================================================================
    # QUERY DEVICES
    # =========================================================================
    
    # Q key: Query device status
    if keyboard.events[bge.events.QKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: Q pressed - Querying device status")
        
        devices = virtual_device_manager.get_active_devices()
        print(f"\\n📊 BGE: Device Status Report")
        print(f"    Active devices: {len(devices)}")
        
        if devices:
            print("    Device Details:")
            for i, device in enumerate(devices, 1):
                serial = device.get("serial_number", "unknown")
                config = device.get("config_file", "unknown")
                state = device.get("current_state", {})
                status = "running" if state.get("is_running") else "idle"
                temp = state.get("temperature", "unknown")
                target = state.get("target_temp", "unknown")
                mode = state.get("mode", "unknown")
                power = state.get("power_kw", "unknown")
                
                print(f"    {i}. {serial}:")
                print(f"        Config: {config}")
                print(f"        Status: {status}")
                print(f"        Temperature: {temp}°F (target: {target}°F)")
                print(f"        Mode: {mode}")
                print(f"        Power: {power} kW")
        else:
            print("    No active devices found")
        
        # Also show visual device count
        visual_count = 0
        if hasattr(bge.logic, "spawned_devices"):
            visual_count = len(bge.logic.spawned_devices)
        print(f"    Visual devices in scene: {visual_count}")
    
    # =========================================================================
    # CONTROL DEVICES  
    # =========================================================================
    
    # C key: Control device temperature
    if keyboard.events[bge.events.CKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("🔑 BGE: C pressed - Controlling device temperature")
        
        # Get most recent device as target
        devices = virtual_device_manager.get_active_devices()
        if devices:
            target_device = devices[-1]  # Control most recent device
            serial = target_device.get("serial_number")
            
            # Cycle through some temperature values
            if not hasattr(bge.logic, "control_temp"):
                bge.logic.control_temp = 70
            
            bge.logic.control_temp += 2
            if bge.logic.control_temp > 78:
                bge.logic.control_temp = 70
            
            # Send setpoint command
            if virtual_device_manager.control_device(serial, "setpoint", bge.logic.control_temp):
                print(f"🎛️ BGE: Set {serial} temperature to {bge.logic.control_temp}°F")
            else:
                print(f"❌ BGE: Failed to control {serial}")
        else:
            print("❌ BGE: No devices to control")
    
    # =========================================================================
    # HELP
    # =========================================================================
    
    # H key: Show help
    if keyboard.events[bge.events.HKEY] == bge.logic.KX_INPUT_JUST_ACTIVATED:
        print("\\n🆘 BGE: Virtual Device Control Help")
        print("    Key Controls:")
        print("    S - Spawn new medium house device")
        print("    1 - Spawn small apartment (efficient)")
        print("    2 - Spawn small apartment (inefficient)")
        print("    3 - Spawn medium house (efficient)")
        print("    D - Delete most recent device (or all if none selected)")
        print("    Q - Query/list all device status")
        print("    C - Control device temperature (cycles through values)")
        print("    H - Show this help")
        print("    \\n    Make sure Docker is running:")
        print("    cd C:\\\\Users\\\\hbui11\\\\Desktop\\\\vesper_llm\\\\virtual-interaction")
        print("    docker-compose up -d")

def init():
    """Initialize the device control system"""
    print("🎮 BGE: Device Control Script initialized")
    print("    Press H for help")
    
    # Check if backend is available
    if DEVICE_MANAGER_AVAILABLE:
        if virtual_device_manager.check_backend_health():
            print("✅ BGE: Backend console is available")
        else:
            print("❌ BGE: Backend console is not available")
            print("    Start Docker services with:")
            print("    cd C:\\Users\\hbui11\\Desktop\\vesper_llm\\virtual-interaction")
            print("    docker-compose up -d")

# Call init when script first runs
if not hasattr(bge.logic, "device_control_initialized"):
    init()
    bge.logic.device_control_initialized = True
