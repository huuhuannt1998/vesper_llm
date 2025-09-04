"""
VESPER-CASAS Device Bridge
=========================

Bridges actual VESPER virtual devices (Docker containers) with CASAS event logging.
Connects real device state changes to CASAS format for ground truth comparison.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import requests
import aiohttp

from casas_testbed.simulation.virtual_sensors import SensorReading, SensorType

@dataclass
class VirtualDeviceInfo:
    """Information about a running virtual device"""
    device_id: str
    device_type: str
    container_name: str
    port: int
    device_name: str  # Custom name from Blender (e.g., "motion1")
    casas_sensor_id: str  # Mapped CASAS sensor ID (e.g., "M01")
    location: str
    api_url: str
    last_state: Dict = None

class VESPERDeviceBridge:
    """Bridge between VESPER virtual devices and CASAS logging system"""
    
    def __init__(self, cloud_server_url: str = "http://localhost:8080"):
        self.cloud_server_url = cloud_server_url
        self.devices: Dict[str, VirtualDeviceInfo] = {}
        self.casas_events: List[SensorReading] = []
        self.event_callbacks: List[Callable] = []
        
        # CASAS sensor mapping - maps device types to sensor IDs
        self.sensor_mapping = {
            "motion-sensor": {"base": "M", "start": 1, "max": 26},
            "item-sensor": {"base": "I", "start": 1, "max": 8},
            "thermostat": {"base": "T", "start": 1, "max": 4},
            "appliance-controller": {"base": "A", "start": 1, "max": 6}
        }
        
        # Location mapping for CASAS format
        self.location_mapping = {
            "living_room": "livingroom",
            "kitchen": "kitchen", 
            "bedroom": "bedroom",
            "bathroom": "bathroom",
            "dining_room": "diningroom",
            "office": "office",
            "garage": "garage",
            "hallway": "hallway"
        }
        
    async def discover_virtual_devices(self) -> List[VirtualDeviceInfo]:
        """Discover all running virtual devices from cloud server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.cloud_server_url}/api/devices") as response:
                    if response.status == 200:
                        devices_data = await response.json()
                        return await self._process_discovered_devices(devices_data)
                    else:
                        print(f"❌ Failed to discover devices: {response.status}")
                        return []
        except Exception as e:
            print(f"❌ Error discovering devices: {e}")
            return []
    
    async def _process_discovered_devices(self, devices_data: List[Dict]) -> List[VirtualDeviceInfo]:
        """Process discovered devices and map them to CASAS sensors"""
        discovered_devices = []
        sensor_counters = {sensor_type: 1 for sensor_type in self.sensor_mapping.keys()}
        
        for device_data in devices_data:
            device_id = device_data.get("device_id")
            if not device_id:
                continue
                
            # Get device type from device_id (e.g., VSM-DD46-1B1E-3C97 -> motion-sensor)
            device_type = self._extract_device_type(device_id)
            
            # Find corresponding Docker container
            container_info = await self._find_device_container(device_id)
            if not container_info:
                continue
                
            # Generate CASAS sensor ID
            casas_sensor_id = self._generate_casas_sensor_id(device_type, sensor_counters)
            
            # Extract custom device name from container name
            device_name = self._extract_custom_name(container_info["container_name"])
            
            device_info = VirtualDeviceInfo(
                device_id=device_id,
                device_type=device_type,
                container_name=container_info["container_name"],
                port=container_info["port"],
                device_name=device_name,
                casas_sensor_id=casas_sensor_id,
                location=device_data.get("location", "unknown"),
                api_url=f"http://localhost:{container_info['port']}",
                last_state={}
            )
            
            discovered_devices.append(device_info)
            self.devices[device_id] = device_info
            
        print(f"✅ Discovered {len(discovered_devices)} virtual devices")
        for device in discovered_devices:
            print(f"  📱 {device.device_name} ({device.device_id}) → {device.casas_sensor_id}")
            
        return discovered_devices
    
    def _extract_device_type(self, device_id: str) -> str:
        """Extract device type from device ID"""
        if device_id.startswith("VSM-"):
            return "motion-sensor"
        elif device_id.startswith("VSI-"):
            return "item-sensor"
        elif device_id.startswith("VST-"):
            return "thermostat"
        elif device_id.startswith("VSA-"):
            return "appliance-controller"
        else:
            return "unknown"
    
    async def _find_device_container(self, device_id: str) -> Optional[Dict]:
        """Find Docker container for a device"""
        import subprocess
        
        try:
            # Search for container with device_id in name
            cmd = ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}", "--filter", f"name={device_id}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        container_name = parts[0]
                        ports = parts[1]
                        
                        # Extract port number
                        port = self._extract_port(ports)
                        if port:
                            return {
                                "container_name": container_name,
                                "port": port
                            }
            return None
        except Exception as e:
            print(f"❌ Error finding container for {device_id}: {e}")
            return None
    
    def _extract_port(self, port_string: str) -> Optional[int]:
        """Extract port number from Docker port string"""
        try:
            # Format: "0.0.0.0:9000->8000/tcp"
            if ":" in port_string and "->" in port_string:
                port_part = port_string.split(":")[1].split("->")[0]
                return int(port_part)
        except:
            pass
        return None
    
    def _extract_custom_name(self, container_name: str) -> str:
        """Extract custom device name from container name"""
        # Format: motion1-motion-sensor-VSM-DD46-1B1E-3C97
        parts = container_name.split("-")
        if len(parts) >= 3:
            return parts[0]  # Return "motion1"
        return "unknown"
    
    def _generate_casas_sensor_id(self, device_type: str, counters: Dict[str, int]) -> str:
        """Generate CASAS sensor ID for device type"""
        if device_type in self.sensor_mapping:
            mapping = self.sensor_mapping[device_type]
            base = mapping["base"]
            counter = counters[device_type]
            
            if counter <= mapping["max"]:
                sensor_id = f"{base}{counter:02d}"  # M01, M02, etc.
                counters[device_type] += 1
                return sensor_id
        
        return f"X{counters.get('unknown', 1):02d}"  # Fallback
    
    async def start_monitoring(self, poll_interval: float = 1.0):
        """Start monitoring all virtual devices for state changes"""
        print(f"🔍 Starting device monitoring (polling every {poll_interval}s)")
        
        while True:
            await self._poll_all_devices()
            await asyncio.sleep(poll_interval)
    
    async def _poll_all_devices(self):
        """Poll all devices for state changes"""
        for device_id, device_info in self.devices.items():
            try:
                await self._poll_device_state(device_info)
            except Exception as e:
                print(f"❌ Error polling {device_id}: {e}")
    
    async def _poll_device_state(self, device_info: VirtualDeviceInfo):
        """Poll a single device for state changes"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{device_info.api_url}/state") as response:
                    if response.status == 200:
                        current_state = await response.json()
                        
                        # Check for state changes
                        if self._state_changed(device_info, current_state):
                            await self._process_state_change(device_info, current_state)
                            device_info.last_state = current_state.copy()
                            
        except Exception as e:
            # Device might not be responding - this is normal for some containers
            pass
    
    def _state_changed(self, device_info: VirtualDeviceInfo, new_state: Dict) -> bool:
        """Check if device state has changed significantly"""
        if not device_info.last_state:
            return True
            
        # Check motion sensor changes
        if device_info.device_type == "motion-sensor":
            old_motion = device_info.last_state.get("motion", "inactive")
            new_motion = new_state.get("motion", "inactive")
            return old_motion != new_motion
            
        # Check item sensor changes
        elif device_info.device_type == "item-sensor":
            old_items = device_info.last_state.get("items", [])
            new_items = new_state.get("items", [])
            return old_items != new_items
            
        # Check thermostat changes
        elif device_info.device_type == "thermostat":
            old_temp = device_info.last_state.get("temperature", 0)
            new_temp = new_state.get("temperature", 0)
            return abs(old_temp - new_temp) > 0.5  # Significant temp change
            
        return False
    
    async def _process_state_change(self, device_info: VirtualDeviceInfo, new_state: Dict):
        """Process a state change and create CASAS event"""
        now = datetime.now()
        
        # Generate CASAS event based on device type
        if device_info.device_type == "motion-sensor":
            motion_state = new_state.get("motion", "inactive")
            message = "ON" if motion_state == "active" else "OFF"
            
        elif device_info.device_type == "item-sensor":
            items = new_state.get("items", [])
            message = "PRESENT" if items else "ABSENT"
            
        elif device_info.device_type == "thermostat":
            temp = new_state.get("temperature", 0)
            message = f"TEMP_{temp:.1f}"
            
        else:
            message = "UNKNOWN"
        
        # Create CASAS sensor reading
        casas_event = SensorReading(
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S.%f"),
            sensor=device_info.casas_sensor_id,
            message=message
        )
        
        # Store event
        self.casas_events.append(casas_event)
        
        # Notify callbacks
        for callback in self.event_callbacks:
            try:
                await callback(device_info, casas_event, new_state)
            except Exception as e:
                print(f"❌ Error in event callback: {e}")
        
        # Log event
        print(f"📊 CASAS Event: {device_info.device_name}({device_info.casas_sensor_id}) → {message}")
    
    def add_event_callback(self, callback: Callable):
        """Add callback for CASAS events"""
        self.event_callbacks.append(callback)
    
    def export_casas_csv(self, filename: str):
        """Export collected events to CASAS CSV format"""
        with open(filename, 'w') as f:
            f.write("date,time,sensor,message\n")
            for event in self.casas_events:
                f.write(event.to_csv_row() + "\n")
        
        print(f"📁 Exported {len(self.casas_events)} CASAS events to {filename}")
    
    def clear_events(self):
        """Clear collected events"""
        self.casas_events.clear()
        print("🗑️ Cleared CASAS event buffer")

# Utility function for easy integration
async def create_vesper_bridge() -> VESPERDeviceBridge:
    """Create and initialize VESPER device bridge"""
    bridge = VESPERDeviceBridge()
    await bridge.discover_virtual_devices()
    return bridge
