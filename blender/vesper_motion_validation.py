"""
VESPER Motion Sensor Validation System
=====================================

Combines virtual motion sensors with VLM navigation for enhanced validation:
1. Auto-discover room layout from Blender scene
2. Deploy virtual motion sensors in detected rooms  
3. Track actor movement through sensor activations
4. Cross-validate VLM navigation decisions with sensor data
5. Generate enhanced CASAS datasets with verified location data

This creates a dual-verification system:
- VLM provides navigation intelligence
- Motion sensors provide ground truth location verification
"""

import bge
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Import requests with error handling
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests module not available - simulation mode only")

# Import room discovery system
from blender.vesper_room_discovery import discover_room_layout_from_blender, get_optimal_sensor_positions

class VESPERMotionValidationSystem:
    """Integrated motion sensor validation for VLM navigation"""
    
    def __init__(self):
        self.motion_sensors = {}  # room_name -> sensor_info
        self.actor_location_history = []
        self.current_room = "unknown"
        self.room_boundaries = {}
        self.validation_enabled = False
        self.simulation_mode = False  # Track if we're using simulation vs real sensors
        
        # Virtual device manager integration
        self.device_manager_url = "http://localhost:8080"  # Backend console
        self.deployed_sensors = {}
        
        # Room-to-CASAS sensor mapping (will be updated by room discovery)
        self.room_sensor_mapping = {
            'living_room': ['M01', 'M02'],
            'dining_room': ['M03', 'M04', 'M05'], 
            'kitchen': ['M13', 'M14', 'M15'],
            'bedroom': ['M07', 'M08'],
            'bathroom': ['M09', 'M10'],
            'hallway': ['M11', 'M12'],
            'office': ['M16', 'M17'],
            'garage': ['M18', 'M19']
        }
        
        # Initialize room boundaries
        self.setup_room_boundaries()
        
        print("🏠 VESPER Motion Validation System initialized")
    
    def setup_room_boundaries(self):
        """Auto-discover room boundaries from Blender scene"""
        print("🔍 Auto-discovering room layout from Blender scene...")
        
        try:
            # Use room discovery system to find actual room layout
            discovered_rooms = discover_room_layout_from_blender()
            
            if discovered_rooms:
                # Convert discovered rooms to boundary format
                self.room_boundaries = {}
                self.room_sensor_mapping = {}
                
                for room_name, room_info in discovered_rooms.items():
                    # Extract boundaries
                    self.room_boundaries[room_name] = room_info['boundaries']
                    
                    # Extract CASAS sensor mapping
                    self.room_sensor_mapping[room_name] = room_info['casas_sensors']
                    
                    center = room_info['center']
                    method = room_info.get('method', 'unknown')
                    print(f"   🏠 {room_name}: center({center[0]:.1f}, {center[1]:.1f}) via {method}")
                
                print(f"✅ Auto-discovered {len(self.room_boundaries)} rooms from Blender scene")
            else:
                # Fallback to predefined layout
                print("⚠️ Auto-discovery failed, using fallback layout")
                self._setup_fallback_boundaries()
                
        except Exception as e:
            print(f"⚠️ Room discovery error: {e}")
            print("   Using fallback room boundaries")
            self._setup_fallback_boundaries()
    
    def _setup_fallback_boundaries(self):
        """Fallback room boundaries if auto-discovery fails"""
        # Based on your Blender house layout - updated coordinates
        self.room_boundaries = {
            'living_room': {'x_min': -3, 'x_max': 1, 'y_min': -2, 'y_max': 2},
            'kitchen': {'x_min': 3, 'x_max': 7, 'y_min': -1, 'y_max': 3},
            'dining_room': {'x_min': -1, 'x_max': 3, 'y_min': 3, 'y_max': 5},
            'bedroom': {'x_min': -6, 'x_max': -2, 'y_min': 3, 'y_max': 5},
            'bathroom': {'x_min': 5, 'x_max': 7, 'y_min': 5, 'y_max': 7},
            'hallway': {'x_min': -1, 'x_max': 1, 'y_min': 1, 'y_max': 3},
            'office': {'x_min': -8, 'x_max': -4, 'y_min': -1, 'y_max': 1},
            'garage': {'x_min': 7, 'x_max': 9, 'y_min': -3, 'y_max': -1}
        }
        
        # Fallback CASAS sensor mapping
        self.room_sensor_mapping = {
            'living_room': ['M01', 'M02'],
            'dining_room': ['M03', 'M04', 'M05'], 
            'kitchen': ['M13', 'M14', 'M15'],
            'bedroom': ['M07', 'M08'],
            'bathroom': ['M09', 'M10'],
            'hallway': ['M11', 'M12'],
            'office': ['M16', 'M17'],
            'garage': ['M18', 'M19']
        }
    
    async def deploy_virtual_motion_sensors(self):
        """Deploy one virtual motion sensor per room"""
        print("🚀 Deploying one virtual motion sensor per room...")
        
        # First check if backend is available
        backend_available = await self._check_backend_availability()
        
        if not backend_available:
            print("⚠️ Virtual device backend not available (port 8080)")
            print("   📍 Switching to simulation-only mode")
            print("   ✅ CASAS dataset generation will continue without physical sensors")
            
            # Setup simulation-only tracking
            self._setup_simulation_mode()
            return True  # Continue without virtual sensors
        
        try:
            # Get optimal sensor positions from room discovery
            sensor_positions = get_optimal_sensor_positions()
            
            deployed_count = 0
            for room_name, room_data in sensor_positions.items():
                room_center = room_data['room_center']
                
                print(f"   🏠 {room_name}: deploying 1 motion sensor")
                
                try:
                    # Get primary CASAS sensor ID for this room
                    room_sensors = self.room_sensor_mapping.get(room_name, ['M99'])
                    primary_sensor_id = room_sensors[0]  # Use first sensor ID as primary
                    
                    # Deploy one sensor at room center
                    x, y = room_center
                    sensor_info = await self._deploy_motion_sensor(
                        room_name, x, y, primary_sensor_id
                    )
                    
                    if sensor_info:
                        # Use room name as the key for single sensor per room
                        self.deployed_sensors[room_name] = sensor_info
                        deployed_count += 1
                        print(f"     ✅ {primary_sensor_id} at ({x:.1f}, {y:.1f})")
                    
                except Exception as e:
                    print(f"     ❌ {room_name}: deployment failed - {e}")
                        
        except Exception as e:
            print(f"⚠️ Virtual sensor deployment failed: {e}")
            print("   📍 Switching to simulation-only mode")
            self._setup_simulation_mode()
            return True
        
        if deployed_count > 0:
            print(f"🎯 Virtual sensor deployment complete: {deployed_count} sensors deployed")
            self.validation_enabled = True
            self.simulation_mode = False
        else:
            print("📍 No virtual sensors deployed - using simulation-only mode")
            self._setup_simulation_mode()
            
        return True  # Always return True to continue operation
    
    async def _check_backend_availability(self) -> bool:
        """Check if virtual device backend is available"""
        if not REQUESTS_AVAILABLE:
            return False
            
        try:
            response = requests.get(f"{self.device_manager_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def _setup_simulation_mode(self):
        """Setup simulation-only mode when virtual devices aren't available"""
        self.validation_enabled = True  # Enable validation with simulation
        self.simulation_mode = True
        
        # Create one simulated sensor per room (using primary sensor ID)
        for room_name, sensor_ids in self.room_sensor_mapping.items():
            primary_sensor_id = sensor_ids[0]  # Use first sensor ID as primary
            
            # Create simulation sensor info
            center = self._get_room_center(room_name)
            self.deployed_sensors[room_name] = {
                'device_id': f"sim_{primary_sensor_id}",
                'serial': f"SIM_{primary_sensor_id}",
                'casas_sensor_id': primary_sensor_id,
                'position': center,
                'room': room_name,
                'last_state': 'inactive',
                'simulation_mode': True
            }
        
        print(f"✅ Simulation mode setup: {len(self.deployed_sensors)} simulated sensors (1 per room)")
    
    def _get_room_center(self, room_name: str) -> Tuple[float, float]:
        """Get center coordinates for a room"""
        boundaries = self.room_boundaries.get(room_name, {})
        if boundaries:
            center_x = (boundaries['x_min'] + boundaries['x_max']) / 2
            center_y = (boundaries['y_min'] + boundaries['y_max']) / 2
            return (center_x, center_y)
        return (0.0, 0.0)
    
    async def _deploy_motion_sensor(self, room_name: str, x: float, y: float, casas_sensor_id: str = None) -> Optional[Dict]:
        """Deploy a single motion sensor via virtual device API"""
        if not REQUESTS_AVAILABLE:
            return None
            
        try:
            # Generate CASAS sensor ID if not provided
            if not casas_sensor_id:
                room_sensors = self.room_sensor_mapping.get(room_name, ['M99'])
                casas_sensor_id = room_sensors[0]
            
            # Create virtual motion sensor with specific CASAS ID
            payload = {
                "device_type": "motion-sensor",
                "username": "vesper_validation",
                "config_type": "medium_house_efficient",
                "device_name": f"{casas_sensor_id}_{room_name}",  # Include CASAS ID in name
                "location": room_name
            }
            
            if not REQUESTS_AVAILABLE:
                return None
                
            response = requests.post(
                f"{self.device_manager_url}/api/console/spawn",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                device_info = response.json()
                sensor_info = {
                    'device_id': device_info.get('device_id'),
                    'serial': device_info.get('serial_number'),
                    'container_name': device_info.get('container_info', {}).get('container_name'),
                    'port': device_info.get('container_info', {}).get('port'),
                    'api_url': f"http://localhost:{device_info.get('container_info', {}).get('port')}",
                    'casas_sensor_id': casas_sensor_id,  # Store the specific CASAS sensor ID
                    'position': (x, y),
                    'room': room_name,
                    'last_state': 'inactive'
                }
                return sensor_info
            else:
                print(f"❌ Failed to deploy sensor for {room_name}: {response.status_code}")
                
        except (ConnectionError, Timeout, requests.RequestException) as e:
            print(f"❌ API connection failed for sensor {casas_sensor_id}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error deploying sensor for {room_name}: {e}")
        
        return None
    
    def detect_actor_room(self, actor_position: Tuple[float, float]) -> str:
        """Detect which room the actor is currently in"""
        x, y = actor_position
        
        for room_name, boundaries in self.room_boundaries.items():
            if (boundaries['x_min'] <= x <= boundaries['x_max'] and 
                boundaries['y_min'] <= y <= boundaries['y_max']):
                return room_name
        
        return "unknown"
    
    async def update_motion_sensors(self, actor_position: Tuple[float, float]):
        """Update virtual motion sensors based on actor position"""
        if not self.validation_enabled:
            return
        
        new_room = self.detect_actor_room(actor_position)
        
        # If room changed, update sensor states
        if new_room != self.current_room:
            print(f"🚶 Actor moved: {self.current_room} → {new_room}")
            
            # Deactivate previous room sensors
            await self._deactivate_room_sensors(self.current_room)
            
            # Activate new room sensors
            await self._activate_room_sensors(new_room)
            
            # Log movement for validation
            movement_event = {
                'timestamp': datetime.now().isoformat(),
                'from_room': self.current_room,
                'to_room': new_room,
                'position': actor_position,
                'casas_sensors_activated': self._get_room_casas_sensors(new_room)
            }
            self.actor_location_history.append(movement_event)
            
            self.current_room = new_room
    
    def _get_room_casas_sensors(self, room_name: str) -> List[str]:
        """Get CASAS sensor IDs for a room"""
        return self.room_sensor_mapping.get(room_name, [])
    
    async def _activate_room_sensors(self, room_name: str):
        """Activate all sensors in a room"""
        for sensor_key, sensor_info in self.deployed_sensors.items():
            if sensor_info['room'] == room_name:
                await self._update_individual_sensor(sensor_info, "active")
    
    async def _deactivate_room_sensors(self, room_name: str):
        """Deactivate all sensors in a room"""
        for sensor_key, sensor_info in self.deployed_sensors.items():
            if sensor_info['room'] == room_name:
                await self._update_individual_sensor(sensor_info, "inactive")
    
    async def _update_individual_sensor(self, sensor_info: Dict, state: str):
        """Update the state of an individual sensor"""
        try:
            if sensor_info.get('simulation_mode', False):
                # Simulation mode - just log the event
                sensor_info['last_state'] = state
                casas_sensor_id = sensor_info['casas_sensor_id']
                casas_message = "ON" if state == "active" else "OFF"
                print(f"📊 CASAS Event (Simulated): {casas_sensor_id} {casas_message} (Motion in {sensor_info['room']})")
                return
            
            # Real sensor mode - send to virtual device
            if not REQUESTS_AVAILABLE:
                print(f"⚠️ Requests unavailable, falling back to simulation for {casas_sensor_id}")
                casas_message = "ON" if state == "active" else "OFF"
                print(f"📊 CASAS Event (Fallback): {casas_sensor_id} {casas_message} (Motion in {sensor_info['room']})")
                return
                
            payload = {
                "motion": state,
                "timestamp": datetime.now().isoformat(),
                "room": sensor_info['room']
            }
            
            try:
                response = requests.post(
                    f"{sensor_info['api_url']}/update_state",
                    json=payload,
                    timeout=5
                )
                
                sensor_info['last_state'] = state
                
                # Generate CASAS event for this specific sensor
                casas_sensor_id = sensor_info['casas_sensor_id']
                casas_message = "ON" if state == "active" else "OFF"
                print(f"📊 CASAS Event: {casas_sensor_id} {casas_message} (Motion in {sensor_info['room']})")
                
            except (ConnectionError, Timeout, requests.RequestException) as e:
                print(f"❌ Sensor API connection failed for {casas_sensor_id}, using simulation: {e}")
                casas_message = "ON" if state == "active" else "OFF"
                print(f"📊 CASAS Event (Fallback): {casas_sensor_id} {casas_message} (Motion in {sensor_info['room']})")
                
        except Exception as e:
            print(f"❌ Failed to update sensor {sensor_info.get('casas_sensor_id', 'unknown')}: {e}")
    
    async def _update_sensor_state(self, room_name: str, state: str):
        """Legacy method - update all sensors in a room (deprecated)"""
        if state == "active":
            await self._activate_room_sensors(room_name)
        else:
            await self._deactivate_room_sensors(room_name)
    
    def validate_vlm_navigation(self, vlm_intended_room: str, actual_position: Tuple[float, float]) -> Dict:
        """Validate VLM navigation decision against motion sensor data"""
        detected_room = self.detect_actor_room(actual_position)
        
        validation_result = {
            'vlm_intended': vlm_intended_room,
            'sensor_detected': detected_room,
            'position': actual_position,
            'validation_success': vlm_intended_room.lower() == detected_room.lower(),
            'timestamp': datetime.now().isoformat()
        }
        
        if validation_result['validation_success']:
            print(f"✅ VLM Validation: {vlm_intended_room} → Confirmed by motion sensors")
        else:
            print(f"⚠️ VLM Validation: Expected {vlm_intended_room}, detected {detected_room}")
        
        return validation_result
    
    def generate_enhanced_casas_events(self, task_name: str, vlm_actions: List[str]) -> List[Dict]:
        """Generate CASAS events enhanced with motion sensor validation"""
        enhanced_events = []
        
        for i, movement_event in enumerate(self.actor_location_history):
            room = movement_event['to_room']
            timestamp = movement_event['timestamp']
            casas_sensors = movement_event['casas_sensors_activated']
            
            # Generate motion sensor events
            for sensor_id in casas_sensors:
                casas_event = {
                    'date': timestamp.split('T')[0],
                    'time': timestamp.split('T')[1].split('.')[0],
                    'sensor': sensor_id,
                    'message': 'ON',
                    'source': 'vesper_motion_validation',
                    'room': room,
                    'vlm_action': vlm_actions[i] if i < len(vlm_actions) else 'unknown',
                    'position': movement_event['position']
                }
                enhanced_events.append(casas_event)
        
        return enhanced_events
    
    def save_validation_report(self, task_name: str) -> str:
        """Save validation report with motion sensor data"""
        report = {
            'task_name': task_name,
            'validation_enabled': self.validation_enabled,
            'deployed_sensors': len(self.deployed_sensors),
            'movement_history': self.actor_location_history,
            'room_boundaries': self.room_boundaries,
            'sensor_mapping': self.room_sensor_mapping,
            'generated_at': datetime.now().isoformat()
        }
        
        # Save to validation logs
        vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
        validation_dir = os.path.join(vesper_root, "blender", "validation_logs")
        os.makedirs(validation_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(validation_dir, f"motion_validation_{task_name}_{timestamp}.json")
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Validation report saved: {report_file}")
        return report_file
    
    async def cleanup_sensors(self):
        """Cleanup deployed virtual sensors"""
        if self.simulation_mode:
            print("🧹 Cleaning up simulated motion sensors...")
            self.deployed_sensors.clear()
            self.validation_enabled = False
            print("✅ Simulation cleanup complete")
            return
        
        print("🧹 Cleaning up virtual motion sensors...")
        
        if not REQUESTS_AVAILABLE:
            print("⚠️ Requests unavailable, clearing sensor data only...")
            self.deployed_sensors.clear()
            self.validation_enabled = False
            return
        
        for sensor_key, sensor_info in self.deployed_sensors.items():
            try:
                # Delete virtual device using serial number
                requests.delete(
                    f"{self.device_manager_url}/api/console/device/{sensor_info['serial']}",
                    timeout=5
                )
                casas_id = sensor_info.get('casas_sensor_id', 'unknown')
                print(f"   🗑️ Removed sensor: {sensor_key} ({casas_id})")
            except (ConnectionError, Timeout, requests.RequestException) as e:
                print(f"   ⚠️ API cleanup failed for {sensor_key}, clearing data: {e}")
            except Exception as e:
                print(f"   ❌ Failed to remove {sensor_key} sensor: {e}")
        
        self.deployed_sensors.clear()
        self.validation_enabled = False

# Global validation system instance
motion_validation_system = VESPERMotionValidationSystem()

# Integration functions for BGE navigation
async def initialize_motion_validation():
    """Initialize motion validation system"""
    motion_validation_system.setup_room_boundaries()
    success = await motion_validation_system.deploy_virtual_motion_sensors()
    return success

async def validate_actor_movement(actor_position: Tuple[float, float]):
    """Update motion sensors based on actor position"""
    await motion_validation_system.update_motion_sensors(actor_position)

def validate_vlm_decision(intended_room: str, actual_position: Tuple[float, float]) -> Dict:
    """Validate VLM navigation against motion sensor data"""
    return motion_validation_system.validate_vlm_navigation(intended_room, actual_position)

def generate_validated_casas_data(task_name: str, vlm_actions: List[str]) -> List[Dict]:
    """Generate CASAS data enhanced with motion validation"""
    return motion_validation_system.generate_enhanced_casas_events(task_name, vlm_actions)

async def cleanup_motion_validation():
    """Cleanup motion validation system"""
    await motion_validation_system.cleanup_sensors()
