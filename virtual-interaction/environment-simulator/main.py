import asyncio
import json
import logging
import os
import math
import redis
import yaml
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import numpy as np
from fastapi import FastAPI, HTTPException
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Environment Simulator")

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Thermostat serial number
thermostat_serial = os.getenv("THERMOSTAT_SERIAL", "")
config_file = os.getenv("CONFIG_FILE", "medium_house_efficient.yaml")

class ThermalSimulator:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.current_temp = 72.0  # Starting temperature
        self.current_humidity = 45.0  # Starting humidity
        self.outside_temp = 85.0  # Summer default
        self.hvac_state = {
            "is_running": False,
            "mode": "off",
            "last_change": datetime.now(timezone.utc)
        }
        self.simulation_task = None
        self.initialized = False
        self.runtime_minutes = 0
        self.total_energy_kwh = 0.0
        self.last_update = datetime.now(timezone.utc)
        
        # Temperature override tracking
        self.temp_override = None
        self.temp_override_time = None
        self.override_duration_minutes = 30  # Default override duration
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        full_path = f"/config/{config_path}"
        if not os.path.exists(full_path):
            logger.warning(f"Config file {full_path} not found, using defaults")
            return self._get_default_config()
            
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file not found"""
        return {
            "metadata": {
                "name": "Default Medium House",
                "category": "residential_medium"
            },
            "environment": {
                "home_size_sqft": 2000,
                "insulation_rating": 7,
                "occupants": 4,
                "thermal_mass": "medium",
                "windows": 10
            },
            "hvac_system": {
                "cooling_btu": 36000,
                "heating_btu": 40000,
                "cooling_eer": 13.0,
                "heating_efficiency": 0.90
            },
            "thermal_properties": {
                "heat_transfer_coefficient": 0.4,
                "air_changes_per_hour": 0.7,
                "solar_heat_gain": 0.3,
                "internal_heat_gain": 1000
            }
        }
    
    async def initialize(self):
        """Initialize the environment simulator"""
        if self.initialized:
            return
            
        # Load any saved state
        await self.load_state()
        
        # Start simulation loop
        self.simulation_task = asyncio.create_task(self.simulation_loop())
        
        self.initialized = True
        logger.info(f"Environment simulator initialized for {thermostat_serial}")
        logger.info(f"Configuration: {self.config['metadata']['name']}")
    
    async def load_state(self):
        """Load state from Redis"""
        key = f"environment:{thermostat_serial}:state"
        state_data = redis_client.get(key)
        if state_data:
            state = json.loads(state_data)
            self.current_temp = state.get("temperature", self.current_temp)
            self.current_humidity = state.get("humidity", self.current_humidity)
            self.total_energy_kwh = state.get("total_energy_kwh", 0.0)
            logger.info(f"Loaded environment state from Redis")
    
    async def save_state(self):
        """Save state to Redis"""
        key = f"environment:{thermostat_serial}:state"
        # Create a JSON-serializable version of hvac_state
        hvac_state_serializable = {
            "is_running": self.hvac_state["is_running"],
            "mode": self.hvac_state["mode"],
            "last_change": self.hvac_state["last_change"].isoformat() if isinstance(self.hvac_state.get("last_change"), datetime) else None
        }
        state = {
            "temperature": self.current_temp,
            "humidity": self.current_humidity,
            "outside_temp": self.outside_temp,
            "hvac_state": hvac_state_serializable,
            "total_energy_kwh": self.total_energy_kwh,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config_name": self.config['metadata']['name'],
            "home_size_sqft": self.config['environment']['home_size_sqft']
        }
        redis_client.set(key, json.dumps(state))
        
        # Save power consumption data
        power_key = f"environment:{thermostat_serial}:power"
        power_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "instantaneous_power_kw": self._calculate_current_power(),
            "total_energy_kwh": self.total_energy_kwh,
            "hvac_running": self.hvac_state["is_running"],
            "mode": self.hvac_state["mode"]
        }
        redis_client.set(power_key, json.dumps(power_data))
    
    def _calculate_current_power(self) -> float:
        """Calculate current power consumption in kW"""
        if not self.hvac_state["is_running"]:
            return 0.0
            
        if self.hvac_state["mode"] in ["cool", "auto"]:
            # Power = BTU/hr / (EER * 1000) 
            cooling_btu = self.config["hvac_system"]["cooling_btu"]
            cooling_eer = self.config["hvac_system"]["cooling_eer"]
            return cooling_btu / (cooling_eer * 1000)
        elif self.hvac_state["mode"] == "heat":
            # Power = BTU/hr / (efficiency * 3412)
            heating_btu = self.config["hvac_system"]["heating_btu"]
            heating_eff = self.config["hvac_system"]["heating_efficiency"]
            return heating_btu / (heating_eff * 3412)
        
        return 0.0
    
    async def simulation_loop(self):
        """Main simulation loop"""
        while True:
            try:
                # Check for temperature overrides
                await self.check_temperature_override()
                
                # Update outside temperature based on time
                await self.update_outside_temperature()
                
                # Check HVAC state from thermostat
                await self.check_hvac_state()
                
                # Calculate temperature change (only if not overridden)
                if self.temp_override is None:
                    await self.simulate_temperature_change()
                else:
                    # Check if override expired
                    if self.temp_override_time:
                        elapsed_minutes = (datetime.now(timezone.utc) - self.temp_override_time).total_seconds() / 60
                        if elapsed_minutes > self.override_duration_minutes:
                            logger.info("Temperature override expired")
                            self.temp_override = None
                            self.temp_override_time = None
                
                # Send updates to thermostat
                await self.send_temperature_update()
                
                # Save state
                await self.save_state()
                
                # Sleep for simulation interval (10 seconds = 1 minute simulated)
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
                await asyncio.sleep(10)
    
    async def check_temperature_override(self):
        """Check for temperature override from Redis"""
        override_key = f"environment:{thermostat_serial}:temp_override"
        override_data = redis_client.get(override_key)
        
        if override_data:
            override_info = json.loads(override_data)
            new_temp = override_info.get("temperature")
            
            if new_temp != self.temp_override:
                self.temp_override = new_temp
                self.temp_override_time = datetime.now(timezone.utc)
                self.current_temp = new_temp
                logger.info(f"Indoor temperature overridden to {new_temp}°F")
                
                # Clear the override key from Redis
                redis_client.delete(override_key)
    
    async def update_outside_temperature(self):
        """Update outside temperature based on time and weather profile"""
        current_time = datetime.now()
        hour = current_time.hour
        day_name = current_time.strftime("%A").lower()
        
        # Determine if it's summer or winter based on month
        month = current_time.month
        is_summer = 4 <= month <= 9
        
        profile_key = "summer_profile" if is_summer else "winter_profile"
        
        if "outside_temperature" in self.config and profile_key in self.config["outside_temperature"]:
            weekly_profile = self.config["outside_temperature"][profile_key]
            if day_name in weekly_profile:
                daily_temps = weekly_profile[day_name]
                if 0 <= hour < len(daily_temps):
                    self.outside_temp = daily_temps[hour]
                    
                    # Add some random variation (-2 to +2 degrees)
                    variation = np.random.normal(0, 0.5)
                    self.outside_temp += variation
    
    async def check_hvac_state(self):
        """Check HVAC state from thermostat via Redis"""
        key = f"thermostat:{thermostat_serial}:hvac_state"
        state_data = redis_client.get(key)
        
        if state_data:
            new_state = json.loads(state_data)
            
            # Check if state changed
            if new_state["is_running"] != self.hvac_state["is_running"]:
                logger.info(f"HVAC state changed: {self.hvac_state['is_running']} -> {new_state['is_running']}")
                self.hvac_state = new_state
                self.hvac_state["last_change"] = datetime.now(timezone.utc)
    
    async def simulate_temperature_change(self):
        """Simulate temperature change based on thermal dynamics"""
        # Time elapsed since last update (in hours)
        current_time = datetime.now(timezone.utc)
        time_elapsed = (current_time - self.last_update).total_seconds() / 3600.0
        self.last_update = current_time
        
        # Get thermal properties
        thermal_props = self.config.get("thermal_properties", {})
        heat_transfer_coeff = thermal_props.get("heat_transfer_coefficient", 0.4)
        air_changes = thermal_props.get("air_changes_per_hour", 0.7)
        solar_gain = thermal_props.get("solar_heat_gain", 0.3)
        internal_gain = thermal_props.get("internal_heat_gain", 1000)
        
        # Calculate heat transfer from outside
        home_size = self.config["environment"]["home_size_sqft"]
        wall_area = home_size * 0.5  # Approximate wall area
        
        # Q = U * A * ΔT (BTU/hr)
        temp_diff = self.outside_temp - self.current_temp
        heat_transfer = heat_transfer_coeff * wall_area * temp_diff
        
        # Add infiltration losses/gains
        # Q = 1.08 * CFM * ΔT
        volume = home_size * 8  # 8 ft ceiling
        cfm = (volume * air_changes) / 60
        infiltration_heat = 1.08 * cfm * temp_diff
        
        # Add solar heat gain (only during day)
        hour = datetime.now().hour
        if 8 <= hour <= 18:
            solar_heat = solar_gain * 500 * self.config["environment"].get("windows", 10)
        else:
            solar_heat = 0
        
        # Total heat gain/loss
        total_heat_change = heat_transfer + infiltration_heat + solar_heat + internal_gain
        
        # HVAC contribution
        if self.hvac_state["is_running"]:
            if self.hvac_state["mode"] in ["cool", "auto"]:
                # Cooling removes heat
                cooling_btu = self.config["hvac_system"]["cooling_btu"]
                total_heat_change -= cooling_btu
            elif self.hvac_state["mode"] == "heat":
                # Heating adds heat
                heating_btu = self.config["hvac_system"]["heating_btu"]
                total_heat_change += heating_btu
            
            # Update energy consumption
            power_kw = self._calculate_current_power()
            self.total_energy_kwh += power_kw * time_elapsed
            self.runtime_minutes += time_elapsed * 60
        
        # Calculate temperature change
        # Thermal mass consideration
        thermal_mass = 1.0  # Adjustment factor based on home construction
        if self.config["environment"].get("thermal_mass") == "high":
            thermal_mass = 1.5
        elif self.config["environment"].get("thermal_mass") == "low":
            thermal_mass = 0.7
        
        # ΔT = Q / (mass * specific_heat)
        # Approximate: 1°F change requires 1000 BTU per 1000 sqft
        temp_change = (total_heat_change * time_elapsed) / (home_size * thermal_mass)
        
        # Update temperature
        self.current_temp += temp_change
        
        # Limit temperature to realistic bounds
        self.current_temp = max(50, min(100, self.current_temp))
        
        # Simple humidity simulation
        if self.hvac_state["is_running"] and self.hvac_state["mode"] in ["cool", "auto"]:
            # AC removes humidity
            self.current_humidity = max(30, self.current_humidity - 0.1)
        else:
            # Humidity trends toward outside conditions
            target_humidity = 50 + (self.outside_temp - 70) * 0.5
            humidity_diff = target_humidity - self.current_humidity
            self.current_humidity += humidity_diff * 0.01
            self.current_humidity = max(20, min(80, self.current_humidity))
    
    async def send_temperature_update(self):
        """Send temperature update to thermostat"""
        try:
            # Get thermostat container name
            thermostat_url = f"http://thermostat-{thermostat_serial}:8000"
            
            response = requests.post(
                f"{thermostat_url}/api/v1/environment/temperature",
                json={
                    "temperature": round(self.current_temp, 1),
                    "humidity": round(self.current_humidity, 1)
                },
                timeout=5
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send temperature update: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending temperature update: {e}")

# Create simulator instance
simulator = ThermalSimulator(config_file)

@app.on_event("startup")
async def startup_event():
    """Initialize simulator on startup"""
    await simulator.initialize()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "thermostat_serial": thermostat_serial,
        "config": simulator.config['metadata']['name']
    }

@app.get("/api/v1/status")
async def get_status():
    """Get current environment status"""
    return {
        "thermostat_serial": thermostat_serial,
        "config_name": simulator.config['metadata']['name'],
        "current_temp": round(simulator.current_temp, 1),
        "current_humidity": round(simulator.current_humidity, 1),
        "outside_temp": round(simulator.outside_temp, 1),
        "hvac_state": simulator.hvac_state,
        "total_energy_kwh": round(simulator.total_energy_kwh, 2),
        "runtime_minutes": round(simulator.runtime_minutes, 1)
    }

@app.post("/api/v1/override/temperature")
async def override_temperature(temperature: float):
    """Override outside temperature"""
    simulator.outside_temp = temperature
    logger.info(f"Outside temperature overridden to {temperature}°F")
    return {"status": "success", "outside_temp": temperature}

@app.get("/api/v1/power")
async def get_power_consumption():
    """Get current power consumption"""
    return {
        "instantaneous_power_kw": round(simulator._calculate_current_power(), 3),
        "total_energy_kwh": round(simulator.total_energy_kwh, 2),
        "runtime_minutes": round(simulator.runtime_minutes, 1),
        "hvac_running": simulator.hvac_state["is_running"],
        "mode": simulator.hvac_state["mode"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
