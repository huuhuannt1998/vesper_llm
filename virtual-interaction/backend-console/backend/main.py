from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
import redis
import json
import os
import uuid
import random
import asyncio
import logging
from datetime import datetime, timezone
from pydantic import BaseModel
import yaml
import aiohttp  # Added for cloud-server registration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Backend Control Console")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secure_password@postgres/thermostat_testbed")
CLOUD_SERVER_URL = os.getenv("CLOUD_SERVER_URL", "http://cloud-server:8080")

# Redis connection
redis_host = REDIS_URL.split("//")[1].split(":")[0]
redis_port = int(REDIS_URL.split(":")[-1])
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Docker functionality using CLI instead of Python library
import subprocess

def docker_command(cmd_args):
    """Execute docker command using CLI"""
    try:
        result = subprocess.run(['docker'] + cmd_args, 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Docker command failed: {e}")
        raise

# Test Docker connection using CLI
docker_available = False
try:
    # Test Docker connection using CLI
    result = docker_command(['version', '--format', '{{.Server.Version}}'])
    docker_available = True
    logger.info(f"Successfully connected to Docker via CLI. Server version: {result}")
except Exception as e:
    logger.warning(f"Docker connection failed: {e}. Device spawning will be disabled.")
    docker_available = False

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Pydantic Models
class SpawnDeviceRequest(BaseModel):
    device_type: str  # thermostat, motion-sensor, item-sensor, appliance-controller, casas-dataset-manager
    username: str
    environment_config: Optional[str] = "random"

class WeatherOverrideRequest(BaseModel):
    temperature: float
    duration_hours: int

class DeviceWeatherOverrideRequest(BaseModel):
    temperature: float

class DeviceSetpointRequest(BaseModel):
    target_temp: float

class DeviceModeRequest(BaseModel):
    mode: str

class DeviceCurrentTempRequest(BaseModel):
    temperature: float

class PowerConsumptionData(BaseModel):
    home_id: str
    timestamp: str
    power_kw: float
    hvac_state: str
    indoor_temp: float
    outdoor_temp: float
    setpoint: float
    efficiency_rating: float
    home_size_sqft: int

# Helper Functions
def generate_serial() -> str:
    """Generate unique serial number"""
    return f"VST-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"

# ------------------------------------------------------------------
# Helper: Register newly spawned device with the cloud-server so
# it becomes discoverable in SmartThings for the same username.
# ------------------------------------------------------------------
async def register_device_with_cloud(serial_number: str, username: str):
    """Call cloud-server to register a new device record"""
    payload = {
        "serial_number": serial_number,
        "device_type": "thermostat",
        "capabilities": [
            "temperatureMeasurement",
            "thermostatMode",
            "thermostatSetpoint"
        ],
        "username": username or "admin"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CLOUD_SERVER_URL}/api/devices/register",
                json=payload,
                timeout=10
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(
                        "Failed to register device %s with cloud-server "
                        "(status=%s): %s",
                        serial_number, resp.status, text
                    )
                else:
                    logger.info(
                        "Device %s successfully registered with cloud-server",
                        serial_number
                    )
    except Exception as e:
        logger.error(
            "Error registering device %s with cloud-server: %s",
            serial_number, e
        )

async def notify_cloud_server_state_change(serial_number: str):
    """Notify cloud server that device state has changed"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CLOUD_SERVER_URL}/api/devices/{serial_number}/state-changed",
                timeout=5
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Successfully notified cloud server of state change for {serial_number}")
                else:
                    logger.warning(f"Cloud server state change notification failed for {serial_number}: {resp.status}")
    except Exception as e:
        logger.error(f"Error notifying cloud server of state change for {serial_number}: {e}")

async def notify_cloud_server_discovery_change(user_id: int = None):
    """Notify cloud server that device discovery has changed"""
    try:
        payload = {}
        if user_id is not None:
            payload["user_id"] = user_id
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{CLOUD_SERVER_URL}/api/devices/discovery-changed",
                json=payload,
                timeout=5
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Successfully notified cloud server of discovery change for user_id {user_id}")
                else:
                    logger.warning(f"Cloud server discovery change notification failed: {resp.status}")
    except Exception as e:
        logger.error(f"Error notifying cloud server of discovery change: {e}")

def get_device_config(device_type: str) -> Dict[str, Any]:
    """Get device-specific configuration for spawning"""
    device_configs = {
        "thermostat": {
            "image": "virtual-interaction-thermostat:latest",
            "port": "8000",
            "environment_vars": {
                "REDIS_HOST": "redis",
                "CLOUD_SERVER_URL": "http://cloud-server:8080"
            }
        },
        "motion-sensor": {
            "image": "virtual-interaction-motion-sensor:latest", 
            "port": "8000",
            "environment_vars": {
                "REDIS_HOST": "redis",
                "CLOUD_SERVER_URL": "http://cloud-server:8080",
                "SENSOR_ZONES": "M01,M02,M03,M04,M05,M06,M07,M08,M09,M10"
            }
        },
        "item-sensor": {
            "image": "virtual-interaction-item-sensor:latest",
            "port": "8000", 
            "environment_vars": {
                "REDIS_HOST": "redis",
                "CLOUD_SERVER_URL": "http://cloud-server:8080",
                "SENSOR_ZONES": "I01,I02,I03,I04,I05,I06,I07,I08,I09,I10"
            }
        },
        "appliance-controller": {
            "image": "virtual-interaction-appliance-controller:latest",
            "port": "8000",
            "environment_vars": {
                "REDIS_HOST": "redis", 
                "CLOUD_SERVER_URL": "http://cloud-server:8080"
            }
        },
        "casas-dataset-manager": {
            "image": "virtual-interaction-casas-dataset-manager:latest",
            "port": "8000",
            "environment_vars": {
                "REDIS_HOST": "redis",
                "CLOUD_SERVER_URL": "http://cloud-server:8080"
            }
        }
    }
    
    if device_type not in device_configs:
        raise ValueError(f"Unknown device type: {device_type}")
    
    return device_configs[device_type]

async def spawn_device_pair(device_type: str, username: str, config_name: Optional[str] = None) -> Dict[str, Any]:
    """Spawn new virtual device pair (device + environment simulator)"""
    if not docker_available:
        raise HTTPException(status_code=503, detail="Docker connection not available. Device spawning is disabled.")
    
    # Get device configuration
    device_config = get_device_config(device_type)
    serial = generate_serial()
    
    # Generate appropriate serial prefix based on device type
    serial_prefixes = {
        "thermostat": "VST",
        "motion-sensor": "VSM", 
        "item-sensor": "VSI",
        "appliance-controller": "VSA",
        "casas-dataset-manager": "VSD"
    }
    prefix = serial_prefixes.get(device_type, "VSD")
    serial = serial.replace("VST", prefix)  # Replace default VST prefix
    
    # Select configuration file
    config_files = ["small_apartment_efficient.yaml", "small_apartment_inefficient.yaml", "medium_house_efficient.yaml"]
    if config_name == "random" or config_name is None:
        config_name = random.choice(config_files)
    
    try:
        # Build environment variables for the device
        env_vars = []
        env_vars.extend(['-e', f'SERIAL_NUMBER={serial}'])
        for key, value in device_config["environment_vars"].items():
            env_vars.extend(['-e', f'{key}={value}'])
        
        # Spawn device container
        device_cmd = [
            'run', '-d',
            '--name', f'{device_type}-{serial}',
            '--network', 'virtual-interaction_testbed-network',
            '--restart', 'unless-stopped'
        ] + env_vars + [device_config["image"]]
        
        device_id = docker_command(device_cmd)
        
        # Spawn environment simulator (only for certain device types)
        environment_id = None
        if device_type in ["thermostat"]:  # Only thermostats need environment simulators
            environment_cmd = [
                'run', '-d',
                '--name', f'environment-{serial}',
                '--network', 'virtual-interaction_testbed-network',
                '--restart', 'unless-stopped',
                '-e', f'THERMOSTAT_SERIAL={serial}',
                '-e', f'CONFIG_FILE={config_name}',
                '-e', 'REDIS_HOST=redis',
                '-v', f'{os.getcwd()}/config:/config:ro',
                'testbed-environment:latest'
            ]
            environment_id = docker_command(environment_cmd)
        
        # Log configuration used
        metadata = {
            "device_type": device_type,
            "config_file": config_name,
            "username": username,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "device_container_id": device_id,
        }
        if environment_id:
            metadata["environment_container_id"] = environment_id
            
        redis_client.hset(
            f"device:{serial}:metadata",
            mapping=metadata
        )
        
        logger.info(f"Spawned {device_type} device: {serial} with config {config_name}")
        
        result = {
            "serial_number": serial,
            "device_type": device_type,
            "config_file": config_name,
            "device_container_id": device_id,
        }
        if environment_id:
            result["environment_container_id"] = environment_id
            
        return result
        
    except Exception as e:
        logger.error(f"Error spawning device pair: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# HELICs Integration
class HELICsExporter:
    """Export real-time power consumption data for HELICs simulator"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.websocket_clients = set()
    
    async def get_all_power_consumption(self) -> Dict[str, Any]:
        """Get current power consumption for all homes"""
        homes = []
        
        # Scan all thermostat keys
        for key in self.redis.scan_iter("thermostat:*:state"):
            serial = key.split(':')[1]
            state_data = self.redis.get(key)
            if not state_data:
                continue
                
            state = json.loads(state_data)
            
            # Get environment data
            env_key = f"environment:{serial}:power"
            env_data = self.redis.get(env_key)
            if not env_data:
                continue
                
            env_power = json.loads(env_data)
            
            # Get environment state
            env_state_key = f"environment:{serial}:state"
            env_state_data = self.redis.get(env_state_key)
            if not env_state_data:
                continue
                
            env_state = json.loads(env_state_data)
            
            # Get metadata
            metadata_key = f"device:{serial}:metadata"
            metadata = self.redis.hgetall(metadata_key)
            
            homes.append({
                "home_id": serial,
                "power_kw": env_power.get("instantaneous_power_kw", 0),
                "hvac_state": state["mode"] if state.get("is_running", False) else "off",
                "indoor_temp": state.get("current_temp", 72),
                "outdoor_temp": env_state.get("outside_temp", 85),
                "setpoint": state.get("target_temp", 72),
                "efficiency_rating": 13.0,  # Default EER
                "home_size_sqft": env_state.get("home_size_sqft", 2000),
                "config_name": metadata.get("config_file", "unknown")
            })
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "total_homes": len(homes),
            "total_power_kw": sum(h["power_kw"] for h in homes),
            "homes": homes
        }
    
    async def get_power_consumption_by_serial(self, serial: str) -> Dict[str, Any]:
        """Get power consumption for specific home"""
        # Get thermostat state
        state_key = f"thermostat:{serial}:state"
        state_data = self.redis.get(state_key)
        if not state_data:
            raise HTTPException(status_code=404, detail="Device not found")
        
        state = json.loads(state_data)
        
        # Get environment power data
        power_key = f"environment:{serial}:power"
        power_data = self.redis.get(power_key)
        if not power_data:
            return {
                "home_id": serial,
                "power_kw": 0,
                "hvac_state": "off",
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
            }
        
        power = json.loads(power_data)
        
        return {
            "home_id": serial,
            "power_kw": power.get("instantaneous_power_kw", 0),
            "hvac_state": state["mode"] if state.get("is_running", False) else "off",
            "indoor_temp": state.get("current_temp", 72),
            "setpoint": state.get("target_temp", 72),
            "timestamp": power.get("timestamp", datetime.now(timezone.utc).isoformat() + "Z")
        }
    
    async def stream_updates(self, websocket: WebSocket):
        """Stream power updates via WebSocket"""
        await manager.connect(websocket)
        try:
            while True:
                # Send updates every second
                await asyncio.sleep(1)
                updates = await self._get_power_changes()
                if updates:
                    await websocket.send_json({
                        "type": "power_update",
                        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                        "updates": updates
                    })
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    async def _get_power_changes(self) -> List[Dict[str, Any]]:
        """Get recent power state changes"""
        updates = []
        
        # Check for recent state changes
        for key in self.redis.scan_iter("environment:*:power"):
            serial = key.split(':')[1]
            power_data = self.redis.get(key)
            if power_data:
                power = json.loads(power_data)
                # Only include if updated in last 2 seconds
                timestamp = datetime.fromisoformat(power["timestamp"].replace("Z", "+00:00"))
                if (datetime.now(timezone.utc) - timestamp).total_seconds() < 2:
                    updates.append({
                        "home_id": serial,
                        "power_kw": power.get("instantaneous_power_kw", 0),
                        "state_change": True,
                        "new_state": "cooling" if power.get("hvac_running") else "off"
                    })
        
        return updates

# Create HELICs exporter instance
helics_exporter = HELICsExporter(redis_client)

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/api/console/spawn")
async def spawn_device(request: SpawnDeviceRequest):
    """Spawn new virtual device (with environment simulator if needed)

    In addition to spawning the Docker containers, immediately register
    the device with the cloud-server so it appears in SmartThings for the
    same user account.
    
    Supported device types: thermostat, motion-sensor, item-sensor, appliance-controller, casas-dataset-manager
    """
    result = await spawn_device_pair(request.device_type, request.username, request.environment_config)

    # Attempt to register with cloud-server and log the outcome
    try:
        logger.info(
            f"Attempting to register device {result['serial_number']} for user {request.username} with cloud-server."
        )
        await register_device_with_cloud(result["serial_number"], request.username)
        logger.info(
            f"Successfully initiated registration for device {result['serial_number']} with cloud-server."
        )
        
        # Notify cloud server of discovery change (new device added)
        asyncio.create_task(notify_cloud_server_discovery_change())
        
    except Exception as e:
        logger.error(
            f"Failed to register device {result['serial_number']} with cloud-server during spawn: {e}"
        )
        # Optionally, you could raise an HTTPException here or return an error to the frontend

    return result

@app.post("/api/console/weather-override")
async def weather_override(request: WeatherOverrideRequest):
    """Override outside temperature for all environments"""
    if not docker_available:
        raise HTTPException(status_code=503, detail="Docker connection not available.")
    
    count = 0
    
    # Get all environment containers using CLI
    try:
        containers_output = docker_command(['ps', '--filter', 'name=environment-', '--format', '{{.Names}}'])
        container_names = containers_output.split('\n') if containers_output else []
        
        for container_name in container_names:
            if container_name.startswith('environment-'):
                serial = container_name.replace("environment-", "")
                
                # Send temperature override to environment
                try:
                    docker_command([
                        'exec', container_name,
                        'curl', '-X', 'POST', 'http://localhost:8001/api/v1/override/temperature',
                        '-H', 'Content-Type: application/json',
                        '-d', f'{{"temperature": {request.temperature}}}'
                    ])
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to override temperature for {serial}: {e}")
    except Exception as e:
        logger.error(f"Failed to list containers: {e}")
    
    # Store override in Redis
    redis_client.setex(
        "weather_override",
        request.duration_hours * 3600,
        json.dumps({
            "temperature": request.temperature,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "duration_hours": request.duration_hours
        })
    )
    
    return {
        "status": "success",
        "devices_updated": count,
        "temperature": request.temperature,
        "duration_hours": request.duration_hours
    }

@app.get("/api/console/export/{username}")
async def export_user_data(username: str):
    """Export all device data for a user"""
    devices = []
    
    # Find all devices for user
    for key in redis_client.scan_iter("device:*:metadata"):
        metadata = redis_client.hgetall(key)
        if metadata.get("username") == username:
            serial = key.split(':')[1]
            
            # Get device data
            device_data = {
                "serial_number": serial,
                "deployment_time": metadata.get("created_at"),
                "configuration": {
                    "config_file": metadata.get("config_file")
                }
            }
            
            # Get state history
            history_key = f"thermostat:{serial}:history"
            history = redis_client.lrange(history_key, 0, -1)
            device_data["state_history"] = [json.loads(h) for h in history]
            
            # Get power data
            power_key = f"environment:{serial}:power"
            power_data = redis_client.get(power_key)
            if power_data:
                device_data["power_data"] = json.loads(power_data)
            
            devices.append(device_data)
    
    return {
        "export_timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "user": username,
        "devices": devices
    }

@app.get("/api/console/dashboard")
async def get_dashboard_data():
    """Get real-time dashboard data"""
    # Count active devices
    active_devices = 0
    total_energy = 0.0
    total_temp = 0.0
    temp_count = 0
    
    for key in redis_client.scan_iter("thermostat:*:state"):
        active_devices += 1
        state_data = redis_client.get(key)
        if state_data:
            state = json.loads(state_data)
            total_temp += state.get("current_temp", 0)
            temp_count += 1
    
    # Get total energy consumption
    power_data = await helics_exporter.get_all_power_consumption()
    
    return {
        "active_devices": active_devices,
        "total_energy_consumption": power_data["total_power_kw"],
        "average_temperature": total_temp / temp_count if temp_count > 0 else 0,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }

@app.get("/api/console/devices")
async def list_all_devices():
    """List all devices with their status"""
    devices = []
    processed_serials = set()
    
    # First, get devices with metadata
    for key in redis_client.scan_iter("device:*:metadata"):
        serial = key.split(':')[1]
        metadata = redis_client.hgetall(key)
        processed_serials.add(serial)
        
        # Check if container exists before adding device
        device_type = "thermostat"  # Default
        if serial.startswith("VSM-"):
            device_type = "motion-sensor"
        elif serial.startswith("VSE-"):
            device_type = "environment-sensor"
        elif serial.startswith("VSA-"):
            device_type = "appliance-controller"
        elif serial.startswith("VSI-"):
            device_type = "item-sensor"
        
        container_name = f"{device_type}-{serial}" if device_type != "thermostat" else f"thermostat-{serial}"
        
        try:
            result = docker_command(['inspect', container_name])
            container_exists = True
            logger.info(f"Container {container_name} exists")
        except Exception as e:
            container_exists = False
            logger.info(f"Skipping device {serial} - container {container_name} does not exist")
            continue  # Skip this device if container doesn't exist
        
        # Get current state
        state_key = f"thermostat:{serial}:state"
        state_data = redis_client.get(state_key)
        state = json.loads(state_data) if state_data else {}
        
        # Get power data
        power_key = f"environment:{serial}:power"
        power_data = redis_client.get(power_key)
        power = json.loads(power_data) if power_data else {}
        
        devices.append({
            "serial_number": serial,
            "username": metadata.get("username", "unknown"),
            "config_file": metadata.get("config_file", "unknown"),
            "created_at": metadata.get("created_at", "unknown"),
            "current_state": {
                "temperature": state.get("current_temp"),
                "target_temp": state.get("target_temp"),
                "mode": state.get("mode"),
                "is_running": state.get("is_running"),
                "power_kw": power.get("instantaneous_power_kw", 0)
            }
        })
    
    # Then, get devices without metadata (legacy devices)
    for key in redis_client.scan_iter("thermostat:*:state"):
        serial = key.split(':')[1]
        logger.info(f"Processing legacy device: {serial}")
        if serial in processed_serials:
            logger.info(f"Device {serial} already processed, skipping")
            continue  # Already processed this device
            
        # Get current state
        state_data = redis_client.get(key)
        state = json.loads(state_data) if state_data else {}
        logger.info(f"Device {serial} state: {state}")
        
        # Get power data
        power_key = f"environment:{serial}:power"
        power_data = redis_client.get(power_key)
        power = json.loads(power_data) if power_data else {}
        logger.info(f"Device {serial} power: {power}")
        
        # Check if containers exist
        try:
            result = docker_command(['inspect', f'thermostat-{serial}'])
            container_exists = True
            logger.info(f"Container thermostat-{serial} exists")
        except Exception as e:
            container_exists = False
            logger.warning(f"Container thermostat-{serial} does not exist or inspect failed: {e}")
        
        if container_exists:
            logger.info(f"Adding legacy device {serial} to devices list")
            devices.append({
                "serial_number": serial,
                "username": "legacy",
                "config_file": "unknown",
                "created_at": "unknown",
                "current_state": {
                    "temperature": state.get("current_temp"),
                    "target_temp": state.get("target_temp"),
                    "mode": state.get("mode"),
                    "is_running": state.get("is_running"),
                    "power_kw": power.get("instantaneous_power_kw", 0)
                }
            })
        else:
            logger.info(f"Skipping device {serial} - container does not exist")
    
    return devices

@app.delete("/api/console/device/{serial}")
async def delete_device(serial: str):
    """Delete a device and its containers"""
    if not docker_available:
        raise HTTPException(status_code=503, detail="Docker connection not available.")
    
    try:
        # Stop and remove thermostat container
        try:
            docker_command(['stop', f'thermostat-{serial}'])
            docker_command(['rm', f'thermostat-{serial}'])
        except Exception as e:
            logger.warning(f"Failed to remove thermostat container: {e}")
        
        # Stop and remove environment container
        try:
            docker_command(['stop', f'environment-{serial}'])
            docker_command(['rm', f'environment-{serial}'])
        except Exception as e:
            logger.warning(f"Failed to remove environment container: {e}")
        
        # Clean up Redis data
        redis_client.delete(f"device:{serial}:metadata")
        redis_client.delete(f"thermostat:{serial}:state")
        redis_client.delete(f"thermostat:{serial}:history")
        redis_client.delete(f"thermostat:{serial}:commands")
        redis_client.delete(f"thermostat:{serial}:hvac_state")
        redis_client.delete(f"environment:{serial}:state")
        redis_client.delete(f"environment:{serial}:power")
        
        return {"status": "success", "serial": serial}
    except Exception as e:
        logger.error(f"Error deleting device {serial}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/console/device/{serial}/weather-override")
async def device_weather_override(serial: str, request: DeviceWeatherOverrideRequest):
    """Override outside temperature for a specific device"""
    try:
        # Get current environment state
        env_state_key = f"environment:{serial}:state"
        env_state_data = redis_client.get(env_state_key)
        
        if env_state_data:
            env_state = json.loads(env_state_data)
            # Update the outside temperature
            env_state["outside_temp"] = request.temperature
            
            # Save updated state back to Redis
            redis_client.set(env_state_key, json.dumps(env_state))
            
            # Also store override metadata
            redis_client.setex(
                f"device:{serial}:weather_override",
                3600,  # 1 hour
                json.dumps({
                    "temperature": request.temperature,
                    "started_at": datetime.now(timezone.utc).isoformat()
                })
            )
            
            logger.info(f"Updated outdoor temperature for {serial} to {request.temperature}°F")
            
            return {
                "status": "success",
                "serial": serial,
                "temperature": request.temperature
            }
        else:
            raise HTTPException(status_code=404, detail="Device environment state not found")
            
    except Exception as e:
        logger.error(f"Failed to override temperature for {serial}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/console/device/{serial}/setpoint")
async def device_set_temperature(serial: str, request: DeviceSetpointRequest):
    """Set temperature setpoint for a specific device"""
    try:
        # Queue command for thermostat
        command_data = {
            "command": "set_temperature",
            "params": {"temperature": request.target_temp}
        }
        
        command_key = f"thermostat:{serial}:commands"
        redis_client.lpush(command_key, json.dumps(command_data))
        
        logger.info(f"Queued setpoint command for {serial}: {request.target_temp}°F")
        
        # Notify cloud server of state change
        asyncio.create_task(notify_cloud_server_state_change(serial))
        
        return {
            "status": "success",
            "serial": serial,
            "target_temp": request.target_temp
        }
    except Exception as e:
        logger.error(f"Failed to set temperature for {serial}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/console/device/{serial}/mode")
async def device_set_mode(serial: str, request: DeviceModeRequest):
    """Set operating mode for a specific device"""
    if request.mode not in ["off", "heat", "cool", "auto"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    try:
        # Queue command for thermostat
        command_data = {
            "command": "set_mode",
            "params": {"mode": request.mode}
        }
        
        command_key = f"thermostat:{serial}:commands"
        redis_client.lpush(command_key, json.dumps(command_data))
        
        logger.info(f"Queued mode command for {serial}: {request.mode}")
        
        # Notify cloud server of state change
        asyncio.create_task(notify_cloud_server_state_change(serial))
        
        return {
            "status": "success",
            "serial": serial,
            "mode": request.mode
        }
    except Exception as e:
        logger.error(f"Failed to set mode for {serial}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/console/device/{serial}/current-temp")
async def device_set_current_temperature(serial: str, request: DeviceCurrentTempRequest):
    """Override current indoor temperature for a specific device"""
    try:
        # Set temperature override in Redis for environment simulator to pick up
        override_key = f"environment:{serial}:temp_override"
        override_data = {
            "temperature": request.temperature,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        redis_client.set(override_key, json.dumps(override_data))
        
        logger.info(f"Set temperature override for {serial} to {request.temperature}°F")
        
        return {
            "status": "success",
            "serial": serial,
            "current_temp": request.temperature
        }
            
    except Exception as e:
        logger.error(f"Failed to set current temperature for {serial}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# HELICs API Endpoints

@app.get("/api/helics/power-consumption")
async def get_all_power_consumption():
    """Real-time power consumption for all homes"""
    return await helics_exporter.get_all_power_consumption()

@app.get("/api/helics/power-consumption/{serial}")
async def get_power_consumption(serial: str):
    """Real-time power consumption for specific home"""
    return await helics_exporter.get_power_consumption_by_serial(serial)

@app.websocket("/api/helics/stream")
async def websocket_power_stream(websocket: WebSocket):
    """WebSocket endpoint for streaming power data"""
    await helics_exporter.stream_updates(websocket)

# Static file serving (commented out for direct run)
# app.mount("/static", StaticFiles(directory="../frontend/build/static"), name="static")

# @app.get("/")
# async def read_index():
#     """Serve the React frontend index.html"""
#     return FileResponse('../frontend/build/index.html')

# # Catch-all route for React Router (SPA routing)
# @app.get("/{full_path:path}")
# async def read_index_catch_all(full_path: str):
#     """Serve the React frontend for any non-API routes"""
#     # Don't serve React app for API routes
#     if full_path.startswith("api/"):
#         raise HTTPException(status_code=404, detail="Not Found")
#     return FileResponse('frontend/build/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)
