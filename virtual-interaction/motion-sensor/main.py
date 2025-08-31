from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone
import redis
import json
import os
import uuid
import asyncio
import logging
import requests
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Virtual CASAS Motion Sensor")

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Cloud server URL
cloud_server_url = os.getenv("CLOUD_SERVER_URL", "http://cloud-server:8080")

class MotionSensorState(BaseModel):
    motion: str = "inactive"  # active, inactive
    detection_zone: Dict[str, float] = {"x": 0.0, "y": 0.0, "radius": 2.0}
    last_triggered: str = ""
    sensitivity: float = 1.0
    cooldown_period: float = 2.0  # seconds
    room_location: str = ""

class MotionUpdate(BaseModel):
    motion: str

class ActorPosition(BaseModel):
    x: float
    y: float
    timestamp: Optional[str] = None

class SensorConfiguration(BaseModel):
    detection_zone: Dict[str, float]
    sensitivity: Optional[float] = None
    cooldown_period: Optional[float] = None
    room_location: Optional[str] = None

class VirtualMotionSensor:
    def __init__(self):
        self.sensor_id = os.getenv("SENSOR_ID", f"M{int(os.getenv('SENSOR_INDEX', '001')):03d}")
        self.device_id = None
        self.owner_username = None
        self.state = MotionSensorState()
        self.state.last_triggered = datetime.now(timezone.utc).isoformat()
        self.last_motion_time = 0
        self.monitoring_task = None
        self.initialized = False
        
        # CASAS event logging
        self.casas_events = []
        
    async def initialize(self):
        """Initialize motion sensor and register with cloud server"""
        if self.initialized:
            return
            
        # Load configuration from environment
        self.load_configuration()
        
        # Load state from Redis if exists
        await self.load_state()
        
        # Register with cloud server
        await self.register_with_cloud()
        
        # Start monitoring loop
        self.monitoring_task = asyncio.create_task(self.monitoring_loop())
        
        self.initialized = True
        logger.info(f"Motion sensor {self.sensor_id} initialized at ({self.state.detection_zone['x']}, {self.state.detection_zone['y']})")
    
    def load_configuration(self):
        """Load sensor configuration from environment variables"""
        # Detection zone
        zone_x = float(os.getenv("ZONE_X", "0.0"))
        zone_y = float(os.getenv("ZONE_Y", "0.0"))
        zone_radius = float(os.getenv("ZONE_RADIUS", "2.0"))
        
        self.state.detection_zone = {
            "x": zone_x,
            "y": zone_y,
            "radius": zone_radius
        }
        
        # Other parameters
        self.state.sensitivity = float(os.getenv("SENSITIVITY", "1.0"))
        self.state.cooldown_period = float(os.getenv("COOLDOWN_PERIOD", "2.0"))
        self.state.room_location = os.getenv("ROOM_LOCATION", "unknown")
    
    async def load_state(self):
        """Load state from Redis"""
        key = f"motion_sensor:{self.sensor_id}:state"
        state_data = redis_client.get(key)
        if state_data:
            state_dict = json.loads(state_data)
            self.state = MotionSensorState(**state_dict)
            logger.info(f"Loaded state from Redis for {self.sensor_id}")
    
    async def save_state(self):
        """Save state to Redis"""
        key = f"motion_sensor:{self.sensor_id}:state"
        self.state.last_triggered = datetime.now(timezone.utc).isoformat()
        redis_client.set(key, json.dumps(self.state.dict()))
        
        # Also save to CASAS event history
        await self.save_casas_event()
    
    async def save_casas_event(self):
        """Save motion event in CASAS format"""
        event = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "sensor": self.sensor_id,
            "message": "ON" if self.state.motion == "active" else "OFF",
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
        """Register motion sensor with cloud server"""
        try:
            registration_data = {
                "device_type": "motion_sensor",
                "sensor_id": self.sensor_id,
                "capabilities": ["motion_detection"],
                "location": self.state.room_location,
                "detection_zone": self.state.detection_zone,
                "smartthings_capability": "motionSensor"
            }
            
            response = requests.post(
                f"{cloud_server_url}/api/devices/register",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.device_id = result.get("device_id")
                logger.info(f"Motion sensor {self.sensor_id} registered successfully")
            else:
                logger.error(f"Failed to register motion sensor: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Failed to register with cloud server: {e}")
    
    async def monitoring_loop(self):
        """Main monitoring loop for motion detection"""
        while True:
            try:
                # Check for actor position updates
                await self.check_actor_position()
                
                # Check for motion timeout (automatic OFF after cooldown)
                await self.check_motion_timeout()
                
                await asyncio.sleep(0.1)  # 10Hz monitoring
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(1)
    
    async def check_actor_position(self):
        """Check if actor is in detection zone"""
        # Get latest actor position from Redis
        position_data = redis_client.get("actor:position")
        if not position_data:
            return
            
        try:
            position = json.loads(position_data)
            actor_x = position.get("x", 0.0)
            actor_y = position.get("y", 0.0)
            
            # Calculate distance from sensor
            distance = math.sqrt(
                (actor_x - self.state.detection_zone["x"])**2 + 
                (actor_y - self.state.detection_zone["y"])**2
            )
            
            # Check if within detection radius
            in_zone = distance <= (self.state.detection_zone["radius"] * self.state.sensitivity)
            
            current_time = datetime.now().timestamp()
            
            # Trigger motion if actor enters zone and cooldown has passed
            if in_zone and self.state.motion == "inactive":
                if current_time - self.last_motion_time > self.state.cooldown_period:
                    await self.trigger_motion()
                    
            elif not in_zone and self.state.motion == "active":
                # Actor left zone, turn off motion
                await self.clear_motion()
                
        except json.JSONDecodeError:
            logger.error("Invalid actor position data")
    
    async def check_motion_timeout(self):
        """Auto-clear motion after timeout period"""
        if self.state.motion == "active":
            current_time = datetime.now().timestamp()
            if current_time - self.last_motion_time > 30.0:  # 30 second timeout
                await self.clear_motion()
    
    async def trigger_motion(self):
        """Trigger motion detection"""
        old_state = self.state.motion
        self.state.motion = "active"
        self.last_motion_time = datetime.now().timestamp()
        
        await self.save_state()
        await self.notify_cloud_server()
        
        logger.info(f"Motion sensor {self.sensor_id} triggered: {old_state} -> active")
    
    async def clear_motion(self):
        """Clear motion detection"""
        old_state = self.state.motion
        self.state.motion = "inactive"
        
        await self.save_state()
        await self.notify_cloud_server()
        
        logger.info(f"Motion sensor {self.sensor_id} cleared: {old_state} -> inactive")
    
    async def notify_cloud_server(self):
        """Notify cloud server of state change"""
        try:
            notification_data = {
                "device_id": self.device_id,
                "sensor_id": self.sensor_id,
                "state": self.state.dict(),
                "smartthings_event": {
                    "capability": "motionSensor",
                    "attribute": "motion",
                    "value": self.state.motion
                }
            }
            
            response = requests.post(
                f"{cloud_server_url}/api/devices/state_change",
                json=notification_data,
                timeout=5
            )
            
        except requests.RequestException as e:
            logger.error(f"Failed to notify cloud server: {e}")

# Initialize global motion sensor
motion_sensor = VirtualMotionSensor()

@app.on_event("startup")
async def startup_event():
    await motion_sensor.initialize()

@app.get("/")
async def root():
    return {"device": "CASAS Motion Sensor", "sensor_id": motion_sensor.sensor_id}

@app.get("/state")
async def get_state():
    return motion_sensor.state

@app.post("/manual_trigger")
async def manual_trigger(motion_update: MotionUpdate):
    """Manually trigger motion state for testing"""
    if motion_update.motion == "active":
        await motion_sensor.trigger_motion()
    else:
        await motion_sensor.clear_motion()
    
    return {"status": "success", "new_state": motion_sensor.state.motion}

@app.post("/actor_position")
async def update_actor_position(position: ActorPosition):
    """Update actor position for motion detection"""
    # Store position in Redis for monitoring loop
    position_data = {
        "x": position.x,
        "y": position.y,
        "timestamp": position.timestamp or datetime.now(timezone.utc).isoformat()
    }
    
    redis_client.set("actor:position", json.dumps(position_data))
    
    return {"status": "position_updated"}

@app.post("/configure")
async def configure_sensor(config: SensorConfiguration):
    """Configure sensor parameters"""
    if config.detection_zone:
        motion_sensor.state.detection_zone = config.detection_zone
    if config.sensitivity is not None:
        motion_sensor.state.sensitivity = config.sensitivity
    if config.cooldown_period is not None:
        motion_sensor.state.cooldown_period = config.cooldown_period
    if config.room_location:
        motion_sensor.state.room_location = config.room_location
    
    await motion_sensor.save_state()
    
    return {"status": "configured", "new_config": motion_sensor.state}

@app.get("/casas_events")
async def get_casas_events():
    """Get CASAS format events for this sensor"""
    return {
        "sensor_id": motion_sensor.sensor_id,
        "events": motion_sensor.casas_events[-100:],  # Last 100 events
        "total_events": len(motion_sensor.casas_events)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "sensor_id": motion_sensor.sensor_id,
        "initialized": motion_sensor.initialized,
        "current_motion": motion_sensor.state.motion,
        "location": motion_sensor.state.room_location
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
