"""
Device API Integration with Time Tracking
==========================================

Integrates device API calls with proper logging and time tracking.
Shows curl/API responses in console and handles turn ON/OFF properly.

Key Features:
1. Call device API when actor is close
2. Log API responses (show curl results)
3. Automatically turn OFF device based on task duration
4. Track interaction time using virtual time

Usage in llm_bge_navigation.py:
    from interaction_system.device_api_integration import check_and_trigger_device_interaction
"""

import requests
import json
import time


class DeviceAPIManager:
    """Manages device API calls with proper logging and timing"""
    
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
        self.active_devices = {}  # device_id: {start_time, virtual_start_time, expected_duration}
        
    def call_device_api(self, device_id, action, show_curl=True):
        """
        Call device API and log the response.
        
        Supports:
        - Appliance Controller (port 8003): Phone, Stove, Sink, Kitchen Sink, Bathroom Sink
        - Motion Sensors (ports 9000-9002): motion1, motion2, motion3
        - Item Sensors (ports 9201-9206): phone-item, stove-item, sink-item, diningtable-item
        
        Args:
            device_id: Device name (e.g., "Phone", "Stove", "motion1", "kitchensink")
            action: "on" or "off" or "use" or "active" or "inactive"
            show_curl: Whether to print curl equivalent command
        
        Returns:
            dict: API response or None if failed
        """
        device_name = device_id.lower()
        
        # === APPLIANCE CONTROLLER (port 8003) ===
        appliance_devices = {
            'phone': {
                'url': f"{self.base_url}/phone",
                'on_body': {'state': 'PICKUP'},
                'off_body': {'state': 'HANGUP'}
            },
            'stove': {
                'url': f"{self.base_url}/burner",
                'on_body': {'action': 'turn_on', 'level': 70},
                'off_body': {'action': 'turn_off'}
            },
            'sink': {
                'url': f"{self.base_url}/water",
                'on_body': {'action': 'turn_on', 'hot_level': 50},
                'off_body': {'action': 'turn_off'}
            },
            'kitchensink': {
                'url': f"{self.base_url}/water",
                'on_body': {'action': 'turn_on', 'hot_level': 50},
                'off_body': {'action': 'turn_off'}
            },
            'bathroomsink1': {
                'url': f"{self.base_url}/water",
                'on_body': {'action': 'turn_on', 'hot_level': 50},
                'off_body': {'action': 'turn_off'}
            },
            'bathroomsink2': {
                'url': f"{self.base_url}/water",
                'on_body': {'action': 'turn_on', 'hot_level': 50},
                'off_body': {'action': 'turn_off'}
            }
        }
        
        # === MOTION SENSORS (ports 9000-9002) ===
        motion_sensors = {
            'motion1': {'port': 9000},
            'motion2': {'port': 9001},
            'motion3': {'port': 9002}
        }
        
        # === ITEM SENSORS (ports 9201-9206) ===
        item_sensors = {
            'phone-item': {'port': 9201},
            'bathroomsink1-item': {'port': 9202},
            'stove-item': {'port': 9203},
            'diningtable-item': {'port': 9204},
            'kitchensink-item': {'port': 9205},
            'bathroomsink2-item': {'port': 9206}
        }
        
        url = None
        body = None
        
        # Determine which API to call
        if device_name in appliance_devices:
            # Appliance controller
            config = appliance_devices[device_name]
            url = config['url']
            if action.lower() == 'on':
                body = config['on_body']
            elif action.lower() == 'off':
                body = config['off_body']
            else:
                print(f"⚠️  Unknown action for appliance: {action}")
                return None
                
        elif device_name in motion_sensors:
            # Motion sensor
            port = motion_sensors[device_name]['port']
            url = f"http://localhost:{port}/manual_trigger"
            if action.lower() in ['on', 'active']:
                body = {'motion': 'active'}
            elif action.lower() in ['off', 'inactive']:
                body = {'motion': 'inactive'}
            else:
                print(f"⚠️  Unknown action for motion sensor: {action}")
                return None
                
        elif device_name in item_sensors:
            # Item sensor
            port = item_sensors[device_name]['port']
            url = f"http://localhost:{port}/interaction"
            if action.lower() in ['on', 'use']:
                body = {'action': 'use'}
            else:
                print(f"⚠️  Unknown action for item sensor: {action}")
                return None
                
        else:
            print(f"⚠️  Unknown device: {device_id}")
            print(f"   Supported: {list(appliance_devices.keys()) + list(motion_sensors.keys()) + list(item_sensors.keys())}")
            return None
        
        # Show curl command (PowerShell format)
        if show_curl:
            print(f"\n📞 API Call [{device_name}]:")
            body_json = json.dumps(body)
            print(f'   $body = \'{body_json}\' | ConvertFrom-Json | ConvertTo-Json')
            print(f'   Invoke-WebRequest -Uri "{url}" -Method POST -Body $body -ContentType "application/json"')
        
        try:
            # Make API call
            response = requests.post(url, json=body, timeout=5)
            
            # Log response
            print(f"\n📡 API Response ({response.status_code}):")
            try:
                response_data = response.json()
                print(f"   {json.dumps(response_data, indent=2)}")
                return response_data
            except:
                print(f"   {response.text}")
                return {"status": response.status_code, "text": response.text}
                
        except requests.exceptions.ConnectionError:
            print(f"❌ API Connection Failed: Device service not running for {device_name}")
            return None
        except requests.exceptions.Timeout:
            print(f"⏱️  API Timeout: Request took longer than 5 seconds")
            return None
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def turn_on_device(self, device_id, task_name="", expected_duration=None, virtual_time_manager=None):
        """
        Turn ON device and track interaction.
        
        Args:
            device_id: Device ID
            task_name: Name of task (for logging)
            expected_duration: How long device should be ON (seconds, virtual time)
            virtual_time_manager: VirtualTimeManager instance
        
        Returns:
            bool: Success status
        """
        print(f"\n🔵 Turning ON device: {device_id}")
        print(f"   Task: {task_name}")
        if expected_duration:
            print(f"   Expected duration: {expected_duration}s ({expected_duration/60:.1f} min)")
        
        # Call API
        response = self.call_device_api(device_id, "on")
        
        if response:
            # Track active device
            self.active_devices[device_id] = {
                'start_time': time.time(),
                'virtual_start_time': virtual_time_manager.get_current_time() if virtual_time_manager else None,
                'expected_duration': expected_duration,
                'task_name': task_name
            }
            print(f"✅ Device ON: {device_id}")
            return True
        else:
            print(f"❌ Failed to turn ON device: {device_id}")
            return False
    
    def turn_off_device(self, device_id, virtual_time_manager=None):
        """
        Turn OFF device and log duration.
        
        Args:
            device_id: Device ID
            virtual_time_manager: VirtualTimeManager instance
        
        Returns:
            bool: Success status
        """
        if device_id not in self.active_devices:
            print(f"⚠️  Device not tracked as active: {device_id}")
            # Still try to turn it off
        
        print(f"\n⚪ Turning OFF device: {device_id}")
        
        # Calculate duration if tracked
        if device_id in self.active_devices:
            device_info = self.active_devices[device_id]
            real_duration = time.time() - device_info['start_time']
            
            if virtual_time_manager and device_info['virtual_start_time']:
                virtual_duration = (virtual_time_manager.get_current_time() - device_info['virtual_start_time']).total_seconds()
                print(f"   Real duration: {real_duration:.1f}s")
                print(f"   Virtual duration: {virtual_duration:.1f}s ({virtual_duration/60:.1f} min)")
            else:
                print(f"   Duration: {real_duration:.1f}s")
        
        # Call API
        response = self.call_device_api(device_id, "off")
        
        if response:
            # Remove from active tracking
            if device_id in self.active_devices:
                del self.active_devices[device_id]
            print(f"✅ Device OFF: {device_id}")
            return True
        else:
            print(f"❌ Failed to turn OFF device: {device_id}")
            return False
    
    def check_auto_turnoff(self, virtual_time_manager=None):
        """
        Check if any devices should be automatically turned OFF based on expected duration.
        
        Args:
            virtual_time_manager: VirtualTimeManager instance
        
        Returns:
            list: Device IDs that were turned OFF
        """
        turned_off = []
        
        if not virtual_time_manager:
            return turned_off
        
        current_virtual_time = virtual_time_manager.get_current_time()
        
        for device_id, info in list(self.active_devices.items()):
            if info['expected_duration'] and info['virtual_start_time']:
                # Check if expected duration has elapsed (in virtual time)
                elapsed_virtual = (current_virtual_time - info['virtual_start_time']).total_seconds()
                
                if elapsed_virtual >= info['expected_duration']:
                    print(f"\n⏰ Auto turn-OFF triggered: {device_id}")
                    print(f"   Expected: {info['expected_duration']}s")
                    print(f"   Elapsed: {elapsed_virtual:.1f}s")
                    
                    if self.turn_off_device(device_id, virtual_time_manager):
                        turned_off.append(device_id)
        
        return turned_off


# Global instance
_device_api_manager = None


def get_device_api_manager(base_url="http://localhost:8003"):
    """Get or create global device API manager"""
    global _device_api_manager
    if _device_api_manager is None:
        _device_api_manager = DeviceAPIManager(base_url)
    return _device_api_manager


def check_and_trigger_device_interaction(actor_position, task_name, virtual_time_manager=None, 
                                         interaction_distance=1.5):
    """
    Check if actor is close to a device and trigger interaction with API call.
    
    This is the main function to call from navigation loop.
    
    Args:
        actor_position: [x, y, z] position of actor
        task_name: Current task name (e.g., "Make a phone call")
        virtual_time_manager: VirtualTimeManager instance
        interaction_distance: Maximum distance for interaction
    
    Returns:
        dict: {
            'interaction': bool,  # Whether interaction happened
            'device_id': str,     # Device ID
            'action': str,        # "turn_on" or "turn_off"
            'task': str          # Task name
        }
    """
    print(f"🔍 DEBUG (device_api_integration): check_and_trigger_device_interaction called")
    print(f"   Actor position: {actor_position}")
    print(f"   Task: {task_name}")
    print(f"   Interaction distance: {interaction_distance}")
    
    try:
        from interaction_system.device_position_helper import get_reachable_devices
        print(f"✅ Successfully imported get_reachable_devices from interaction_system")
    except ImportError:
        # Fallback: try without package prefix (if running from blender/ directory)
        try:
            from device_position_helper import get_reachable_devices
            print(f"✅ Successfully imported get_reachable_devices (fallback)")
        except ImportError as e:
            print(f"⚠️  Device position helper not available: {e}")
            return {'interaction': False, 'device_id': None, 'action': None, 'task': task_name, 'error': str(e)}
    
    # Get devices within reach
    try:
        print(f"🔍 DEBUG: Calling get_reachable_devices...")
        reachable = get_reachable_devices(actor_position, interaction_distance)
        print(f"🔍 DEBUG: get_reachable_devices returned: {reachable}")
    except Exception as e:
        print(f"⚠️  Error getting reachable devices: {e}")
        return {'interaction': False, 'device_id': None, 'action': None, 'task': task_name, 'error': str(e)}
    
    if not reachable:
        # Check for nearby devices (within 6x interaction distance) to give navigation hints
        try:
            nearby_threshold = interaction_distance * 6  # Show hints for devices within 6x the interaction range
            nearby = get_reachable_devices(actor_position, interaction_distance=nearby_threshold)
            if nearby:
                closest_nearby = nearby[0]
                print(f"💡 Device nearby but not close enough:")
                print(f"   {closest_nearby['name']}: {closest_nearby['distance']:.2f} units away")
                print(f"   Need to move within {interaction_distance} units to interact")
        except:
            pass
        
        # No devices nearby - this is normal, not an error
        return {'interaction': False, 'device_id': None, 'action': None, 'task': task_name}
    
    
    # Get API manager
    api_manager = get_device_api_manager()
    
    # Filter devices by task type
    task_lower = task_name.lower()
    task_device_map = {
        'phone call': ['phone'],
        'wash hands': ['sink', 'bathroomsink', 'kitchensink'],
        'cook': ['stove'],
        'eat': ['table', 'diningtable'],
        'clean': ['sink', 'kitchensink']
    }
    
    # Find relevant devices for this task
    relevant_devices = []
    for task_key, device_types in task_device_map.items():
        if task_key in task_lower:
            for device in reachable:
                device_name_lower = device['name'].lower()
                if any(dtype.lower() in device_name_lower for dtype in device_types):
                    relevant_devices.append(device)
            break
    
    if not relevant_devices:
        print(f"💡 No task-relevant devices within reach for '{task_name}'")
        print(f"   Reachable devices: {[d['name'] for d in reachable]}")
        print(f"   Required device types: {task_device_map.get(task_key, ['unknown'])}")
        return {'interaction': False, 'device_id': None, 'action': None, 'task': task_name}
    
    # Get closest task-relevant device
    closest = relevant_devices[0]
    device_name = closest['name']
    
    # Map device name to ID
    device_id = device_name
    
    # Determine expected duration based on task
    task_durations = {
        'phone call': 300,      # 5 minutes
        'wash hands': 120,      # 2 minutes
        'cook': 900,            # 15 minutes
        'eat': 1200,            # 20 minutes
        'clean': 600            # 10 minutes
    }
    
    task_lower = task_name.lower()
    expected_duration = None
    for key, duration in task_durations.items():
        if key in task_lower:
            expected_duration = duration
            break
    
    # Check if device should be turned ON or OFF
    if device_id in api_manager.active_devices:
        # Device already ON - check if should turn OFF
        # For now, turn OFF when task changes or actor moves away
        # Auto turn-OFF is handled by check_auto_turnoff()
        return {'interaction': False, 'device_id': device_id, 'action': 'already_on', 'task': task_name}
    else:
        # Turn ON device
        success = api_manager.turn_on_device(
            device_id,
            task_name,
            expected_duration,
            virtual_time_manager
        )
        
        if success:
            return {
                'interaction': True,
                'device_id': device_id,
                'action': 'turn_on',
                'task': task_name,
                'expected_duration': expected_duration
            }
        else:
            return {'interaction': False, 'device_id': device_id, 'action': 'failed', 'task': task_name}


def check_auto_turnoff_devices(virtual_time_manager):
    """
    Check and auto-turn OFF devices that have exceeded their expected duration.
    Call this periodically from navigation loop.
    
    Args:
        virtual_time_manager: VirtualTimeManager instance
    
    Returns:
        list: Device IDs that were turned OFF
    """
    api_manager = get_device_api_manager()
    return api_manager.check_auto_turnoff(virtual_time_manager)


# Example usage in navigation loop:
"""
# At start of navigation:
from interaction_system.device_api_integration import (
    check_and_trigger_device_interaction,
    check_auto_turnoff_devices
)

# In navigation loop (after each movement):
result = check_and_trigger_device_interaction(
    actor_position,
    current_task,
    metrics_logger.virtual_time_manager,
    interaction_distance=1.5
)

if result['interaction']:
    print(f"✅ Device interaction: {result['device_id']} - {result['action']}")

# Periodically check for auto turn-OFF:
if step % 5 == 0:  # Every 5 steps
    turned_off = check_auto_turnoff_devices(metrics_logger.virtual_time_manager)
    for device_id in turned_off:
        print(f"✅ Auto-turned OFF: {device_id}")
"""
