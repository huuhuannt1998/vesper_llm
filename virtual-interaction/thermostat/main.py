from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import redis
import json
import os
import uuid
import asyncio
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Virtual Smart Thermostat")

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Cloud server URL
cloud_server_url = os.getenv("CLOUD_SERVER_URL", "http://cloud-server:8080")

class ThermostatState(BaseModel):
    mode: str = "cool"  # off, heat, cool, auto
    current_temp: float = 72.0
    current_humidity: float = 45.0
    target_temp: float = 72.0
    fan_mode: str = "auto"  # on, auto
    is_running: bool = False
    last_updated: str = ""

class SetpointUpdate(BaseModel):
    target_temp: float

class ModeUpdate(BaseModel):
    mode: str

class FanModeUpdate(BaseModel):
    fan_mode: str

class EnvironmentUpdate(BaseModel):
    temperature: float
    humidity: Optional[float] = None

class CloudCommand(BaseModel):
    command: str
    params: Dict[str, Any]

class VirtualThermostat:
    def __init__(self):
        self.serial_number = os.getenv("SERIAL_NUMBER", self._generate_serial())
        self.device_id = None
        self.owner_username = None
        self.state = ThermostatState()
        self.state.last_updated = datetime.now(timezone.utc).isoformat()
        self.control_task = None
        self.initialized = False
        
    def _generate_serial(self) -> str:
        """Generate unique serial number"""
        return f"VST-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"
    
    async def initialize(self):
        """Initialize thermostat and register with cloud server"""
        if self.initialized:
            return
            
        # Load state from Redis if exists
        await self.load_state()
        
        # Register with cloud server
        await self.register_with_cloud()
        
        # Start control loop
        self.control_task = asyncio.create_task(self.control_loop())
        
        self.initialized = True
        logger.info(f"Thermostat {self.serial_number} initialized")
    
    async def load_state(self):
        """Load state from Redis"""
        key = f"thermostat:{self.serial_number}:state"
        state_data = redis_client.get(key)
        if state_data:
            state_dict = json.loads(state_data)
            self.state = ThermostatState(**state_dict)
            logger.info(f"Loaded state from Redis for {self.serial_number}")
    
    async def save_state(self):
        """Save state to Redis"""
        key = f"thermostat:{self.serial_number}:state"
        self.state.last_updated = datetime.now(timezone.utc).isoformat()
        redis_client.set(key, json.dumps(self.state.dict()))
        
        # Also save to history
        history_key = f"thermostat:{self.serial_number}:history"
        history_entry = {
            "timestamp": self.state.last_updated,
            "state": self.state.dict()
        }
        redis_client.lpush(history_key, json.dumps(history_entry))
        redis_client.ltrim(history_key, 0, 999)  # Keep last 1000 entries
    
    async def register_with_cloud(self):
        """Register device with cloud server"""
        try:
            response = requests.post(
                f"{cloud_server_url}/api/devices/register",
                json={
                    "serial_number": self.serial_number,
                    "device_type": "thermostat",
                    "capabilities": ["temperature", "humidity", "heating", "cooling", "fan"]
                },
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.device_id = data.get("device_id")
                self.owner_username = data.get("username")
                logger.info(f"Registered with cloud server: device_id={self.device_id}")
            else:
                logger.error(f"Failed to register with cloud server: {response.status_code}")
        except Exception as e:
            logger.error(f"Error registering with cloud server: {e}")
    
    async def control_loop(self):
        """Main control loop for thermostat operation"""
        while True:
            try:
                # Check if we need to run HVAC
                await self.evaluate_hvac_state()
                
                # Save state
                await self.save_state()
                
                # Sync with cloud
                await self.sync_with_cloud()
                
                # Check for commands
                await self.process_commands()
                
                # Sleep for control interval
                await asyncio.sleep(5)  # 5 second control loop
                
            except Exception as e:
                logger.error(f"Error in control loop: {e}")
                await asyncio.sleep(5)
    
    async def evaluate_hvac_state(self):
        """Determine if HVAC should be running"""
        previous_state = self.state.is_running
        
        if self.state.mode == "off":
            self.state.is_running = False
        elif self.state.mode == "heat":
            # Heat if current temp is 1 degree below target
            if self.state.current_temp < self.state.target_temp - 1:
                self.state.is_running = True
            elif self.state.current_temp > self.state.target_temp + 0.5:
                self.state.is_running = False
        elif self.state.mode == "cool":
            # Cool if current temp is 1 degree above target
            if self.state.current_temp > self.state.target_temp + 1:
                self.state.is_running = True
            elif self.state.current_temp < self.state.target_temp - 0.5:
                self.state.is_running = False
        elif self.state.mode == "auto":
            # Auto mode - heat or cool as needed
            if self.state.current_temp < self.state.target_temp - 2:
                self.state.is_running = True
            elif self.state.current_temp > self.state.target_temp + 2:
                self.state.is_running = True
            elif abs(self.state.current_temp - self.state.target_temp) < 0.5:
                self.state.is_running = False
        
        # Log state changes
        if previous_state != self.state.is_running:
            logger.info(f"HVAC state changed: {previous_state} -> {self.state.is_running}")
            
            # Notify environment simulator
            await self.notify_environment_simulator()
    
    async def notify_environment_simulator(self):
        """Notify environment simulator of HVAC state change"""
        key = f"thermostat:{self.serial_number}:hvac_state"
        redis_client.set(key, json.dumps({
            "is_running": self.state.is_running,
            "mode": self.state.mode,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))
    
    async def sync_with_cloud(self):
        """Sync state with cloud server"""
        if not self.device_id:
            return
            
        try:
            response = requests.post(
                f"{cloud_server_url}/api/devices/{self.device_id}/state",
                json=self.state.dict(),
                timeout=5
            )
            if response.status_code != 200:
                logger.error(f"Failed to sync with cloud: {response.status_code}")
        except Exception as e:
            logger.error(f"Error syncing with cloud: {e}")
    
    async def process_commands(self):
        """Process pending commands from cloud"""
        key = f"thermostat:{self.serial_number}:commands"
        
        while True:
            command_data = redis_client.rpop(key)
            if not command_data:
                break
                
            try:
                command = json.loads(command_data)
                await self.execute_command(command)
            except Exception as e:
                logger.error(f"Error processing command: {e}")
    
    async def execute_command(self, command: dict):
        """Execute a command from cloud"""
        cmd_type = command.get("command")
        params = command.get("params", {})
        
        logger.info(f"Executing command: {cmd_type} with params: {params}")
        
        if cmd_type == "set_temperature":
            self.state.target_temp = params.get("temperature", self.state.target_temp)
        elif cmd_type == "set_mode":
            self.state.mode = params.get("mode", self.state.mode)
        elif cmd_type == "set_fan_mode":
            self.state.fan_mode = params.get("fan_mode", self.state.fan_mode)
        
        await self.save_state()

# Create thermostat instance
thermostat = VirtualThermostat()

@app.on_event("startup")
async def startup_event():
    """Initialize thermostat on startup"""
    await thermostat.initialize()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "serial_number": thermostat.serial_number}

@app.get("/api/v1/device/status")
async def get_status():
    """Get current device state"""
    return {
        "serial_number": thermostat.serial_number,
        "device_id": thermostat.device_id,
        "owner": thermostat.owner_username,
        "state": thermostat.state.dict()
    }

@app.post("/api/v1/device/setpoint")
async def update_setpoint(update: SetpointUpdate):
    """Update temperature setpoint"""
    thermostat.state.target_temp = update.target_temp
    await thermostat.save_state()
    return {"status": "success", "target_temp": thermostat.state.target_temp}

@app.post("/api/v1/device/mode")
async def update_mode(update: ModeUpdate):
    """Change operating mode"""
    if update.mode not in ["off", "heat", "cool", "auto"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    thermostat.state.mode = update.mode
    await thermostat.save_state()
    return {"status": "success", "mode": thermostat.state.mode}

@app.post("/api/v1/device/fan")
async def update_fan_mode(update: FanModeUpdate):
    """Change fan mode"""
    if update.fan_mode not in ["on", "auto"]:
        raise HTTPException(status_code=400, detail="Invalid fan mode")
    
    thermostat.state.fan_mode = update.fan_mode
    await thermostat.save_state()
    return {"status": "success", "fan_mode": thermostat.state.fan_mode}

@app.post("/api/v1/cloud/command")
async def receive_cloud_command(command: CloudCommand):
    """Receive command from cloud server"""
    await thermostat.execute_command(command.dict())
    return {"status": "success"}

@app.get("/api/v1/cloud/sync")
async def sync_with_cloud():
    """Sync state with cloud server"""
    await thermostat.sync_with_cloud()
    return {"status": "success"}

@app.post("/api/v1/cloud/register")
async def register_with_cloud():
    """Register with cloud server"""
    await thermostat.register_with_cloud()
    return {
        "status": "success",
        "device_id": thermostat.device_id,
        "serial_number": thermostat.serial_number
    }

@app.post("/api/v1/environment/temperature")
async def update_environment_temperature(update: EnvironmentUpdate):
    """Receive temperature update from environment simulator"""
    thermostat.state.current_temp = update.temperature
    if update.humidity is not None:
        thermostat.state.current_humidity = update.humidity
    
    await thermostat.save_state()
    return {"status": "success"}

@app.post("/api/v1/environment/humidity")
async def update_environment_humidity(humidity: float):
    """Receive humidity update from environment simulator"""
    thermostat.state.current_humidity = humidity
    await thermostat.save_state()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
