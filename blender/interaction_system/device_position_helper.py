"""
Device Position Extractor for VLM Navigation Enhancement
=========================================================

This module extracts positions of all interactive objects (item sensors, devices)
from the Blender scene and formats them for VLM to improve navigation efficiency.

Features:
1. Extract all device/item sensor positions from scene
2. Calculate distance from actor to each device
3. Format device locations for VLM prompt
4. Auto-trigger device interactions when actor is close
5. Integrate with virtual time tracking (pause during VLM)

Usage:
    from device_position_helper import get_devices_for_vlm, auto_trigger_nearby_devices
"""

import bge
import json
from mathutils import Vector


def extract_all_device_positions():
    """
    Extract positions of all devices and item sensors in the scene.
    
    Returns:
        dict: {device_name: {'position': [x, y, z], 'type': str, 'room': str}}
    """
    scene = bge.logic.getCurrentScene()
    devices = {}
    
    # Define device name patterns and their types
    device_patterns = {
        'Phone': {'type': 'item', 'room': 'Kitchen'},
        'Stove': {'type': 'appliance', 'room': 'Kitchen'},
        'DiningTable': {'type': 'furniture', 'room': 'DiningRoom'},
        'KitchenSink': {'type': 'appliance', 'room': 'Kitchen'},
        'BathroomSink1': {'type': 'appliance', 'room': 'Bathroom1'},
        'BathroomSink2': {'type': 'appliance', 'room': 'Bathroom2'},
        # Motion sensors
        'motion1': {'type': 'motion_sensor', 'room': 'LivingRoom'},
        'motion2': {'type': 'motion_sensor', 'room': 'LivingRoom'},
        'motion3': {'type': 'motion_sensor', 'room': 'Kitchen'},
        'motion4': {'type': 'motion_sensor', 'room': 'Bedroom'},
        'motion5': {'type': 'motion_sensor', 'room': 'Bathroom1'},
        'motion6': {'type': 'motion_sensor', 'room': 'Bathroom2'},
    }
    
    # Search for objects in scene
    for obj in scene.objects:
        obj_name = obj.name
        
        # Check if object matches any device pattern
        for pattern, info in device_patterns.items():
            if pattern.lower() in obj_name.lower():
                pos = obj.worldPosition
                devices[obj_name] = {
                    'position': [round(pos.x, 2), round(pos.y, 2), round(pos.z, 2)],
                    'type': info['type'],
                    'room': info['room'],
                    'blender_object': obj  # Keep reference
                }
                break
    
    return devices


def calculate_distances_to_actor(devices, actor_position):
    """
    Calculate distance from actor to each device.
    
    Args:
        devices: Dictionary from extract_all_device_positions()
        actor_position: [x, y, z] position of actor
    
    Returns:
        dict: Same as input but with 'distance' added to each device
    """
    actor_pos = Vector(actor_position)
    
    for device_name, device_info in devices.items():
        device_pos = Vector(device_info['position'])
        distance = (actor_pos - device_pos).length
        device_info['distance'] = round(distance, 2)
        device_info['reachable'] = distance <= 1.5  # Within 1.5 units
    
    return devices


def format_devices_for_vlm(devices, task_name="", max_devices=5):
    """
    Format device positions for inclusion in VLM prompt.
    
    Args:
        devices: Dictionary with distances calculated
        task_name: Current task (to filter relevant devices)
        max_devices: Maximum devices to include (closest ones)
    
    Returns:
        str: Formatted string for VLM prompt
    """
    # Filter by relevance to task
    task_keywords = {
        'phone call': ['Phone', 'DiningTable'],
        'wash hands': ['Sink', 'BathroomSink', 'KitchenSink'],
        'cook': ['Stove', 'KitchenSink', 'DiningTable'],
        'eat': ['DiningTable', 'Stove'],
        'clean': ['KitchenSink', 'Stove', 'DiningTable']
    }
    
    # Get relevant keywords for this task
    task_lower = task_name.lower()
    relevant_keywords = []
    for key, keywords in task_keywords.items():
        if key in task_lower:
            relevant_keywords = keywords
            break
    
    # Filter devices by type (exclude motion sensors from VLM prompt)
    interactive_devices = {
        name: info for name, info in devices.items()
        if info['type'] in ['item', 'appliance', 'furniture']
    }
    
    # Sort by distance (closest first)
    sorted_devices = sorted(
        interactive_devices.items(),
        key=lambda x: x[1]['distance']
    )
    
    # Build formatted string
    lines = ["📍 Available Devices:"]
    
    count = 0
    for device_name, info in sorted_devices:
        # Prioritize relevant devices
        is_relevant = any(kw.lower() in device_name.lower() for kw in relevant_keywords)
        
        if is_relevant or count < max_devices:
            status = "✓ REACHABLE" if info['reachable'] else f"{info['distance']:.1f}m away"
            lines.append(
                f"  • {device_name}: {info['room']} - {status} "
                f"at position ({info['position'][0]:.1f}, {info['position'][1]:.1f})"
            )
            count += 1
            
            if count >= max_devices and not is_relevant:
                break
    
    return "\n".join(lines)


def get_devices_for_vlm(actor_position, task_name=""):
    """
    Main function: Get formatted device information for VLM.
    
    Args:
        actor_position: [x, y, z] position of actor
        task_name: Current task name
    
    Returns:
        str: Formatted device information for VLM prompt
    """
    devices = extract_all_device_positions()
    devices_with_distances = calculate_distances_to_actor(devices, actor_position)
    formatted_text = format_devices_for_vlm(devices_with_distances, task_name)
    
    return formatted_text


def get_reachable_devices(actor_position, interaction_distance=1.5):
    """
    Get list of devices that actor can currently interact with.
    
    Args:
        actor_position: [x, y, z] position of actor
        interaction_distance: Maximum distance for interaction (default 1.5 units)
    
    Returns:
        list: List of device names that are reachable
    """
    print(f"🔍 DEBUG (device_position_helper): get_reachable_devices called")
    print(f"   Actor position: {actor_position}, distance threshold: {interaction_distance}")
    
    devices = extract_all_device_positions()
    print(f"🔍 DEBUG: extract_all_device_positions returned {len(devices)} devices")
    if devices:
        print(f"   Device names: {list(devices.keys())}")
    
    devices_with_distances = calculate_distances_to_actor(devices, actor_position)
    print(f"🔍 DEBUG: Calculated distances for {len(devices_with_distances)} devices")
    
    reachable = []
    for device_name, info in devices_with_distances.items():
        print(f"   {device_name}: distance={info['distance']:.2f}, type={info['type']}")
        if info['distance'] <= interaction_distance and info['type'] in ['item', 'appliance']:
            reachable.append({
                'name': device_name,
                'distance': info['distance'],
                'position': info['position'],
                'room': info['room'],
                'type': info['type']
            })
            # Only show "within reach" if using actual interaction distance (< 1.0)
            if interaction_distance < 1.0:
                print(f"      ✅ Within interaction range ({interaction_distance} units)!")
            else:
                print(f"      📍 Within detection range ({interaction_distance} units)")
    
    # Sort by distance
    reachable.sort(key=lambda x: x['distance'])
    
    print(f"🔍 DEBUG: Returning {len(reachable)} reachable devices")
    return reachable


def auto_trigger_nearby_devices(actor_position, task_name="", item_sensor_manager=None):
    """
    Automatically trigger device interactions when actor is nearby.
    Integrates with ItemSensorManager for timing.
    
    Args:
        actor_position: [x, y, z] position of actor
        task_name: Current task (to determine action)
        item_sensor_manager: Instance of ItemSensorManager for logging
    
    Returns:
        dict: {'triggered': bool, 'device': str, 'action': str}
    """
    reachable = get_reachable_devices(actor_position, interaction_distance=1.0)
    
    if not reachable:
        return {'triggered': False, 'device': None, 'action': None}
    
    # Get closest device
    closest = reachable[0]
    device_name = closest['name']
    
    # Determine action based on task
    task_actions = {
        'phone call': {'Phone': 'pickup'},
        'wash hands': {'KitchenSink': 'turn_on', 'BathroomSink1': 'turn_on', 'BathroomSink2': 'turn_on'},
        'cook': {'Stove': 'turn_on'},
        'eat': {'DiningTable': 'sit'},
        'clean': {'KitchenSink': 'turn_on'}
    }
    
    task_lower = task_name.lower()
    action = None
    
    for task_key, device_actions in task_actions.items():
        if task_key in task_lower:
            for device_pattern, device_action in device_actions.items():
                if device_pattern.lower() in device_name.lower():
                    action = device_action
                    break
            break
    
    if action and item_sensor_manager:
        # Trigger interaction through item sensor manager
        current_time = bge.logic.getFrameTime() if hasattr(bge.logic, 'getFrameTime') else time.time()
        
        # Check if this device exists in sensor manager
        if device_name in item_sensor_manager.object_to_sensor:
            sensor_id = item_sensor_manager.object_to_sensor[device_name]
            sensor = item_sensor_manager.sensors[sensor_id]
            
            # Activate if not already active
            if not sensor.is_active:
                sensor.activate(current_time)
                print(f"🎯 AUTO-TRIGGERED: {device_name} - {action}")
                
                return {
                    'triggered': True,
                    'device': device_name,
                    'action': action,
                    'sensor_id': sensor_id,
                    'distance': closest['distance']
                }
    
    return {'triggered': False, 'device': device_name, 'action': action, 'reason': 'too_far_or_no_action'}


def print_device_summary():
    """Print summary of all devices in scene (for debugging)."""
    devices = extract_all_device_positions()
    
    print("\n" + "="*60)
    print("📍 DEVICE POSITION SUMMARY")
    print("="*60)
    
    # Group by type
    by_type = {}
    for name, info in devices.items():
        device_type = info['type']
        if device_type not in by_type:
            by_type[device_type] = []
        by_type[device_type].append((name, info))
    
    for device_type, items in by_type.items():
        print(f"\n{device_type.upper()}:")
        for name, info in items:
            print(f"  • {name:20s} | {info['room']:15s} | "
                  f"Position: ({info['position'][0]:6.2f}, {info['position'][1]:6.2f}, {info['position'][2]:6.2f})")
    
    print("="*60 + "\n")


# Example usage in BGE navigation:
"""
# In your navigation loop:

from device_position_helper import get_devices_for_vlm, auto_trigger_nearby_devices

# Get actor position
actor_position = [actor.worldPosition.x, actor.worldPosition.y, actor.worldPosition.z]

# Get device info for VLM prompt
device_info = get_devices_for_vlm(actor_position, current_task)

# Add to VLM prompt
vlm_prompt += f"\\n\\n{device_info}"

# Auto-trigger nearby devices
result = auto_trigger_nearby_devices(actor_position, current_task, item_sensor_manager)
if result['triggered']:
    print(f"✅ Started interacting with {result['device']}")
"""
