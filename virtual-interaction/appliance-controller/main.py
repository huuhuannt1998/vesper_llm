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

app = FastAPI(title="Virtual CASAS Appliance Controller")

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Cloud server URL
cloud_server_url = os.getenv("CLOUD_SERVER_URL", "http://cloud-server:8080")

class ApplianceState(BaseModel):
    # Water sensors (AD1-A, AD1-B)
    hot_water_level: int = 0      # 0-100 (OFF/ON in CASAS)
    cold_water_level: int = 0     # 0-100 (OFF/ON in CASAS)
    water_running: bool = False
    
    # Burner sensor (AD1-C)
    burner_level: int = 0         # 0-100 (OFF/ON in CASAS)
    burner_active: bool = False
    
    # Door sensor (D01)
    cabinet_door: str = "CLOSE"   # OPEN/CLOSE (CASAS format)
    
    # Phone sensor (*)
    phone_state: str = "HANGUP"   # PICKUP/HANGUP (CASAS format)
    
    # General state
    location: str = "kitchen"
    last_updated: str = ""

class WaterControl(BaseModel):
    hot_level: Optional[int] = None
    cold_level: Optional[int] = None
    action: Optional[str] = None  # "turn_on", "turn_off"

class BurnerControl(BaseModel):
    level: Optional[int] = None
    action: Optional[str] = None  # "turn_on", "turn_off", "set_level"

class DoorControl(BaseModel):
    state: str  # "OPEN", "CLOSE"

class PhoneControl(BaseModel):
    state: str  # "PICKUP", "HANGUP"

class ApplianceCommand(BaseModel):
    appliance: str  # "water", "burner", "door", "phone"
    action: str
    value: Optional[int] = None

class VirtualApplianceController:
    def __init__(self):
        self.device_id = None
        self.owner_username = None
        self.state = ApplianceState()
        self.state.last_updated = datetime.now(timezone.utc).isoformat()
        self.monitoring_task = None
        self.initialized = False
        
        # CASAS event logging
        self.casas_events = []
        
        # Appliance sensor IDs
        self.sensor_ids = {
            "hot_water": "AD1-A",
            "cold_water": "AD1-B", 
            "burner": "AD1-C",
            "door": "D01",
            "phone": "*"
        }
        
    async def initialize(self):
        """Initialize appliance controller and register with cloud server"""
        if self.initialized:
            return
            
        # Load state from Redis if exists
        await self.load_state()
        
        # Register with cloud server
        await self.register_with_cloud()
        
        # Start monitoring loop
        self.monitoring_task = asyncio.create_task(self.monitoring_loop())
        
        self.initialized = True
        logger.info("Appliance controller initialized")
    
    async def load_state(self):
        """Load state from Redis"""
        key = "appliance_controller:state"
        state_data = redis_client.get(key)
        if state_data:
            state_dict = json.loads(state_data)
            self.state = ApplianceState(**state_dict)
            logger.info("Loaded state from Redis")
    
    async def save_state(self):
        """Save state to Redis"""
        key = "appliance_controller:state"
        self.state.last_updated = datetime.now(timezone.utc).isoformat()
        redis_client.set(key, json.dumps(self.state.dict()))
    
    async def save_casas_event(self, sensor_id: str, message: str):
        """Save appliance event in CASAS format"""
        event = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "sensor": sensor_id,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in Redis for CASAS dataset
        redis_client.lpush("casas:events", json.dumps(event))
        
        # Store in local buffer
        self.casas_events.append(event)
        
        # Keep only last 1000 events
        if len(self.casas_events) > 1000:
            self.casas_events = self.casas_events[-1000:]
    
    async def register_with_cloud(self):
        """Register appliance controller with cloud server"""
        try:
            registration_data = {
                "device_type": "appliance_controller",
                "device_id": "kitchen_appliances",
                "capabilities": ["switch", "level", "contact_sensor"],
                "appliances": ["water_sensors", "burner", "cabinet_door", "phone"],
                "location": self.state.location,
                "smartthings_capabilities": ["switch", "switchLevel", "contactSensor"]
            }
            
            response = requests.post(
                f"{cloud_server_url}/api/devices/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.device_id = result.get("device_id")
                logger.info("Appliance controller registered successfully")
            else:
                logger.error(f"Failed to register appliance controller: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Failed to register with cloud server: {e}")
    
    async def monitoring_loop(self):
        """Main monitoring loop for appliance states"""
        while True:
            try:
                # Check for VLM appliance commands
                await self.check_appliance_commands()
                
                await asyncio.sleep(0.5)  # 2Hz monitoring
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1)
    
    async def check_appliance_commands(self):
        """Check for appliance control commands from VLM"""
        # Check for water commands
        water_cmd = redis_client.get("appliance_command:water")
        if water_cmd:
            await self.process_water_command(json.loads(water_cmd))
            redis_client.delete("appliance_command:water")
        
        # Check for burner commands
        burner_cmd = redis_client.get("appliance_command:burner")
        if burner_cmd:
            await self.process_burner_command(json.loads(burner_cmd))
            redis_client.delete("appliance_command:burner")
        
        # Check for door commands
        door_cmd = redis_client.get("appliance_command:door")
        if door_cmd:
            await self.process_door_command(json.loads(door_cmd))
            redis_client.delete("appliance_command:door")
        
        # Check for phone commands
        phone_cmd = redis_client.get("appliance_command:phone")
        if phone_cmd:
            await self.process_phone_command(json.loads(phone_cmd))
            redis_client.delete("appliance_command:phone")
    
    async def process_water_command(self, command: Dict):
        """Process water control command"""
        action = command.get("action", "")
        value = command.get("value", 50)
        
        old_hot = self.state.hot_water_level
        old_cold = self.state.cold_water_level
        
        if action == "turn_on":
            self.state.hot_water_level = value
            self.state.cold_water_level = value
            self.state.water_running = True
        elif action == "turn_off":
            self.state.hot_water_level = 0
            self.state.cold_water_level = 0
            self.state.water_running = False
        elif action == "set_level":
            self.state.hot_water_level = command.get("hot_level", value)
            self.state.cold_water_level = command.get("cold_level", value)
            self.state.water_running = (self.state.hot_water_level > 0 or self.state.cold_water_level > 0)
        
        # Log CASAS events for water sensors
        if old_hot != self.state.hot_water_level:
            await self.save_casas_event("AD1-A", str(self.state.hot_water_level))
        if old_cold != self.state.cold_water_level:
            await self.save_casas_event("AD1-B", str(self.state.cold_water_level))
        
        await self.save_state()
        await self.notify_cloud_server("water")
        
        logger.info(f"Water control: Hot {old_hot}->{self.state.hot_water_level}, Cold {old_cold}->{self.state.cold_water_level}")
    
    async def process_burner_command(self, command: Dict):
        """Process burner control command"""
        action = command.get("action", "")
        value = command.get("value", 70)
        
        old_level = self.state.burner_level
        
        if action == "turn_on":
            self.state.burner_level = value
            self.state.burner_active = True
        elif action == "turn_off":
            self.state.burner_level = 0
            self.state.burner_active = False
        elif action == "set_level":
            self.state.burner_level = value
            self.state.burner_active = (value > 0)
        
        # Log CASAS event for burner
        if old_level != self.state.burner_level:
            await self.save_casas_event("AD1-C", str(self.state.burner_level))
        
        await self.save_state()
        await self.notify_cloud_server("burner")
        
        logger.info(f"Burner control: {old_level} -> {self.state.burner_level}")
    
    async def process_door_command(self, command: Dict):
        """Process door control command"""
        new_state = command.get("state", "CLOSE")
        old_state = self.state.cabinet_door
        
        if new_state in ["OPEN", "CLOSE"] and new_state != old_state:
            self.state.cabinet_door = new_state
            
            # Log CASAS event for door
            await self.save_casas_event("D01", new_state)
            
            await self.save_state()
            await self.notify_cloud_server("door")
            
            logger.info(f"Door control: {old_state} -> {new_state}")
    
    async def process_phone_command(self, command: Dict):
        """Process phone control command"""
        new_state = command.get("state", "HANGUP")
        old_state = self.state.phone_state
        
        if new_state in ["PICKUP", "HANGUP"] and new_state != old_state:
            self.state.phone_state = new_state
            
            # Log CASAS event for phone
            await self.save_casas_event("*", new_state)
            
            await self.save_state()
            await self.notify_cloud_server("phone")
            
            logger.info(f"Phone control: {old_state} -> {new_state}")
    
    async def notify_cloud_server(self, appliance_type: str):
        """Notify cloud server of appliance state change"""
        try:
            notification_data = {
                "device_id": self.device_id,
                "appliance_type": appliance_type,
                "state": self.state.dict(),
                "smartthings_events": []
            }
            
            # Generate SmartThings events based on appliance type
            if appliance_type == "water":
                notification_data["smartthings_events"].extend([
                    {
                        "component": "hot_water",
                        "capability": "switchLevel",
                        "attribute": "level",
                        "value": self.state.hot_water_level
                    },
                    {
                        "component": "cold_water", 
                        "capability": "switchLevel",
                        "attribute": "level",
                        "value": self.state.cold_water_level
                    }
                ])
            elif appliance_type == "burner":
                notification_data["smartthings_events"].append({
                    "component": "burner",
                    "capability": "switchLevel",
                    "attribute": "level",
                    "value": self.state.burner_level
                })
            elif appliance_type == "door":
                contact_value = "open" if self.state.cabinet_door == "OPEN" else "closed"
                notification_data["smartthings_events"].append({
                    "component": "cabinet_door",
                    "capability": "contactSensor",
                    "attribute": "contact",
                    "value": contact_value
                })
            elif appliance_type == "phone":
                switch_value = "on" if self.state.phone_state == "PICKUP" else "off"
                notification_data["smartthings_events"].append({
                    "component": "phone",
                    "capability": "switch",
                    "attribute": "switch",
                    "value": switch_value
                })
            
            response = requests.post(
                f"{cloud_server_url}/api/devices/state_change",
                json=notification_data,
                timeout=5
            )
            
        except requests.RequestException as e:
            logger.error(f"Failed to notify cloud server: {e}")

# Initialize global appliance controller
appliance_controller = VirtualApplianceController()

@app.on_event("startup")
async def startup_event():
    await appliance_controller.initialize()

@app.get("/")
async def root():
    return {
        "device": "CASAS Appliance Controller",
        "appliances": ["water_sensors", "burner", "cabinet_door", "phone"]
    }

@app.get("/state")
async def get_state():
    return appliance_controller.state

@app.post("/water")
async def control_water(water_control: WaterControl):
    """Control water sensors (AD1-A, AD1-B)"""
    command = {
        "action": water_control.action or "set_level",
        "hot_level": water_control.hot_level,
        "cold_level": water_control.cold_level,
        "value": water_control.hot_level or water_control.cold_level or 50
    }
    
    await appliance_controller.process_water_command(command)
    
    return {
        "status": "water_controlled",
        "hot_level": appliance_controller.state.hot_water_level,
        "cold_level": appliance_controller.state.cold_water_level
    }

@app.post("/burner")
async def control_burner(burner_control: BurnerControl):
    """Control burner sensor (AD1-C)"""
    command = {
        "action": burner_control.action or "set_level",
        "value": burner_control.level or 70
    }
    
    await appliance_controller.process_burner_command(command)
    
    return {
        "status": "burner_controlled",
        "level": appliance_controller.state.burner_level,
        "active": appliance_controller.state.burner_active
    }

@app.post("/door")
async def control_door(door_control: DoorControl):
    """Control cabinet door (D01)"""
    command = {"state": door_control.state}
    
    await appliance_controller.process_door_command(command)
    
    return {
        "status": "door_controlled",
        "state": appliance_controller.state.cabinet_door
    }

@app.post("/phone")
async def control_phone(phone_control: PhoneControl):
    """Control phone sensor (*)"""
    command = {"state": phone_control.state}
    
    await appliance_controller.process_phone_command(command)
    
    return {
        "status": "phone_controlled",
        "state": appliance_controller.state.phone_state
    }

@app.post("/command")
async def appliance_command(command: ApplianceCommand):
    """Generic appliance command interface"""
    if command.appliance == "water":
        await appliance_controller.process_water_command({
            "action": command.action,
            "value": command.value or 50
        })
    elif command.appliance == "burner":
        await appliance_controller.process_burner_command({
            "action": command.action,
            "value": command.value or 70
        })
    elif command.appliance == "door":
        await appliance_controller.process_door_command({
            "state": command.action.upper()
        })
    elif command.appliance == "phone":
        await appliance_controller.process_phone_command({
            "state": command.action.upper()
        })
    
    return {"status": "command_processed", "appliance": command.appliance}

@app.get("/casas_events")
async def get_casas_events():
    """Get CASAS format events for all appliances"""
    return {
        "device": "appliance_controller",
        "sensor_ids": appliance_controller.sensor_ids,
        "events": appliance_controller.casas_events[-100:],  # Last 100 events
        "total_events": len(appliance_controller.casas_events)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "initialized": appliance_controller.initialized,
        "water_running": appliance_controller.state.water_running,
        "burner_active": appliance_controller.state.burner_active,
        "door_state": appliance_controller.state.cabinet_door,
        "phone_state": appliance_controller.state.phone_state
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
