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

app = FastAPI(title="Virtual CASAS Item Sensor")

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Cloud server URL
cloud_server_url = os.getenv("CLOUD_SERVER_URL", "http://cloud-server:8080")

class ItemSensorState(BaseModel):
    presence: str = "PRESENT"  # PRESENT, ABSENT (CASAS format)
    item_name: str = ""
    item_type: str = ""  # ingredient, container, utensil, medicine, etc.
    location: Dict[str, float] = {"x": 0.0, "y": 0.0}
    last_interaction: str = ""
    interaction_count: int = 0

class ItemUpdate(BaseModel):
    presence: str

class ItemInteraction(BaseModel):
    action: str  # pickup, putdown, use, move
    actor_id: Optional[str] = None
    timestamp: Optional[str] = None

class ItemConfiguration(BaseModel):
    item_name: Optional[str] = None
    item_type: Optional[str] = None
    location: Optional[Dict[str, float]] = None

# CASAS Item Mapping
CASAS_ITEMS = {
    "I01": {"name": "oatmeal", "type": "ingredient"},
    "I02": {"name": "raisins", "type": "ingredient"},
    "I03": {"name": "brown_sugar", "type": "ingredient"}, 
    "I04": {"name": "bowl", "type": "container"},
    "I05": {"name": "measuring_spoon", "type": "utensil"},
    "I06": {"name": "medicine_container", "type": "medicine"},
    "I07": {"name": "pot", "type": "cookware"},
    "I08": {"name": "phone_book", "type": "reference"}
}

class VirtualItemSensor:
    def __init__(self):
        self.sensor_id = os.getenv("SENSOR_ID", f"I{int(os.getenv('SENSOR_INDEX', '01')):02d}")
        self.device_id = None
        self.owner_username = None
        self.state = ItemSensorState()
        self.state.last_interaction = datetime.now(timezone.utc).isoformat()
        self.monitoring_task = None
        self.initialized = False
        
        # CASAS event logging
        self.casas_events = []
        
        # Load item configuration
        self.load_item_configuration()
        
    def load_item_configuration(self):
        """Load item configuration based on sensor ID"""
        if self.sensor_id in CASAS_ITEMS:
            item_config = CASAS_ITEMS[self.sensor_id]
            self.state.item_name = item_config["name"]
            self.state.item_type = item_config["type"]
        
        # Override from environment if provided
        self.state.item_name = os.getenv("ITEM_NAME", self.state.item_name)
        self.state.item_type = os.getenv("ITEM_TYPE", self.state.item_type)
        
        # Location
        location_x = float(os.getenv("LOCATION_X", "0.0"))
        location_y = float(os.getenv("LOCATION_Y", "0.0"))
        self.state.location = {"x": location_x, "y": location_y}
        
    async def initialize(self):
        """Initialize item sensor and register with cloud server"""
        if self.initialized:
            return
            
        # Load state from Redis if exists
        await self.load_state()
        
        # Register with cloud server
        await self.register_with_cloud()
        
        # Start monitoring loop
        self.monitoring_task = asyncio.create_task(self.monitoring_loop())
        
        self.initialized = True
        logger.info(f"Item sensor {self.sensor_id} ({self.state.item_name}) initialized")
    
    async def load_state(self):
        """Load state from Redis"""
        key = f"item_sensor:{self.sensor_id}:state"
        state_data = redis_client.get(key)
        if state_data:
            state_dict = json.loads(state_data)
            self.state = ItemSensorState(**state_dict)
            logger.info(f"Loaded state from Redis for {self.sensor_id}")
    
    async def save_state(self):
        """Save state to Redis"""
        key = f"item_sensor:{self.sensor_id}:state"
        self.state.last_interaction = datetime.now(timezone.utc).isoformat()
        redis_client.set(key, json.dumps(self.state.dict()))
        
        # Also save to CASAS event history
        await self.save_casas_event()
    
    async def save_casas_event(self):
        """Save item interaction event in CASAS format"""
        event = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "sensor": self.sensor_id,
            "message": self.state.presence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "item_name": self.state.item_name,
            "item_type": self.state.item_type
        }
        
        # Store in Redis for CASAS dataset
        redis_client.lpush("casas:events", json.dumps(event))
        
        # Store in local buffer
        self.casas_events.append(event)
        
        # Keep only last 1000 events
        if len(self.casas_events) > 1000:
            self.casas_events = self.casas_events[-1000:]
    
    async def register_with_cloud(self):
        """Register item sensor with cloud server"""
        try:
            registration_data = {
                "device_type": "item_sensor",
                "sensor_id": self.sensor_id,
                "capabilities": ["contact_detection", "item_tracking"],
                "item_name": self.state.item_name,
                "item_type": self.state.item_type,
                "location": self.state.location,
                "smartthings_capability": "contactSensor"
            }
            
            response = requests.post(
                f"{cloud_server_url}/api/devices/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.device_id = result.get("device_id")
                logger.info(f"Item sensor {self.sensor_id} registered successfully")
            else:
                logger.error(f"Failed to register item sensor: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Failed to register with cloud server: {e}")
    
    async def monitoring_loop(self):
        """Main monitoring loop for item tracking"""
        while True:
            try:
                # Check for VLM object interactions
                await self.check_object_interactions()
                
                await asyncio.sleep(0.5)  # 2Hz monitoring
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1)
    
    async def check_object_interactions(self):
        """Check for object interaction events from VLM"""
        # Get latest object interactions from Redis
        interaction_key = f"object_interactions:{self.state.item_name}"
        interaction_data = redis_client.get(interaction_key)
        
        if interaction_data:
            try:
                interaction = json.loads(interaction_data)
                action = interaction.get("action", "")
                timestamp = interaction.get("timestamp", "")
                
                # Check if this is a new interaction
                if timestamp != self.state.last_interaction:
                    await self.process_interaction(action, timestamp)
                    
                    # Mark as processed
                    redis_client.delete(interaction_key)
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid interaction data for {self.state.item_name}")
    
    async def process_interaction(self, action: str, timestamp: str):
        """Process object interaction and update state"""
        old_presence = self.state.presence
        
        # Map actions to presence states
        if action in ["pickup", "grab", "take", "remove"]:
            self.state.presence = "ABSENT"
        elif action in ["putdown", "place", "return", "drop"]:
            self.state.presence = "PRESENT"
        elif action in ["use", "interact"]:
            # Toggle state or maintain current for usage
            pass  # State remains the same for usage
        
        # Update interaction tracking
        self.state.interaction_count += 1
        self.state.last_interaction = timestamp
        
        # Save state and notify if changed
        if old_presence != self.state.presence:
            await self.save_state()
            await self.notify_cloud_server()
            
            logger.info(f"Item {self.sensor_id} ({self.state.item_name}): {old_presence} -> {self.state.presence}")
    
    async def notify_cloud_server(self):
        """Notify cloud server of state change"""
        try:
            # Map CASAS format to SmartThings
            contact_value = "open" if self.state.presence == "ABSENT" else "closed"
            
            notification_data = {
                "device_id": self.device_id,
                "sensor_id": self.sensor_id,
                "state": self.state.dict(),
                "smartthings_event": {
                    "capability": "contactSensor",
                    "attribute": "contact",
                    "value": contact_value
                }
            }
            
            response = requests.post(
                f"{cloud_server_url}/api/devices/state_change",
                json=notification_data,
                timeout=5
            )
            
        except requests.RequestException as e:
            logger.error(f"Failed to notify cloud server: {e}")

# Initialize global item sensor
item_sensor = VirtualItemSensor()

@app.on_event("startup")
async def startup_event():
    await item_sensor.initialize()

@app.get("/")
async def root():
    return {
        "device": "CASAS Item Sensor", 
        "sensor_id": item_sensor.sensor_id,
        "item_name": item_sensor.state.item_name,
        "item_type": item_sensor.state.item_type
    }

@app.get("/state")
async def get_state():
    return item_sensor.state

@app.post("/interaction")
async def log_interaction(interaction: ItemInteraction):
    """Log item interaction (pickup, putdown, use)"""
    timestamp = interaction.timestamp or datetime.now(timezone.utc).isoformat()
    await item_sensor.process_interaction(interaction.action, timestamp)
    
    return {
        "status": "interaction_logged",
        "action": interaction.action,
        "new_presence": item_sensor.state.presence
    }

@app.post("/manual_update")
async def manual_update(item_update: ItemUpdate):
    """Manually update item presence for testing"""
    old_presence = item_sensor.state.presence
    item_sensor.state.presence = item_update.presence
    item_sensor.state.interaction_count += 1
    
    await item_sensor.save_state()
    await item_sensor.notify_cloud_server()
    
    return {
        "status": "success",
        "old_presence": old_presence,
        "new_presence": item_sensor.state.presence
    }

@app.post("/configure")
async def configure_sensor(config: ItemConfiguration):
    """Configure item sensor parameters"""
    if config.item_name:
        item_sensor.state.item_name = config.item_name
    if config.item_type:
        item_sensor.state.item_type = config.item_type
    if config.location:
        item_sensor.state.location = config.location
    
    await item_sensor.save_state()
    
    return {"status": "configured", "new_config": item_sensor.state}

@app.get("/casas_events")
async def get_casas_events():
    """Get CASAS format events for this sensor"""
    return {
        "sensor_id": item_sensor.sensor_id,
        "item_name": item_sensor.state.item_name,
        "events": item_sensor.casas_events[-100:],  # Last 100 events
        "total_events": len(item_sensor.casas_events)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "sensor_id": item_sensor.sensor_id,
        "item_name": item_sensor.state.item_name,
        "initialized": item_sensor.initialized,
        "current_presence": item_sensor.state.presence,
        "interaction_count": item_sensor.state.interaction_count
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
