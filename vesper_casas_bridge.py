"""
VESPER-CASAS Bridge Integration
===============================

This module provides the bridge between VESPER VLM navigation and CASAS sensor tracking.
Place this in your VESPER navigation script to automatically generate CASAS datasets.
"""

import requests
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List

class VESPERCASASBridge:
    """Bridge between VESPER navigation and CASAS sensor tracking"""
    
    def __init__(self, casas_base_url="http://localhost:8001"):
        self.motion_url = "http://localhost:8001"
        self.item_url = "http://localhost:8002" 
        self.appliance_url = "http://localhost:8003"
        self.dataset_url = "http://localhost:8004"
        
        # Map VESPER room names to motion sensor zones
        self.room_to_sensors = {
            "kitchen": ["M01", "M02", "M03"],
            "living_room": ["M04", "M05"],
            "dining_room": ["M04", "M05"], 
            "bathroom": ["M06", "M07"],
            "bedroom": ["M08", "M09"],
            "hallway": ["M10", "M11"],
            "office": ["M12", "M13"]
        }
        
        # Map VESPER objects to item sensors
        self.object_to_sensors = {
            "oatmeal": "I01",
            "raisins": "I02", 
            "bowl": "I03",
            "spoon": "I04",
            "water": "I05",
            "medicine": "I06",
            "plate": "I07",
            "cup": "I08"
        }
        
        # Map VESPER appliances to controllers
        self.appliance_to_sensors = {
            "hot_water": "AD1-A",
            "cold_water": "AD1-B",
            "water_faucet": "AD1-A",  # Default to hot water
            "burner": "AD1-C",
            "stove": "AD1-C",
            "door": "D01",
            "phone": "*"
        }
        
        self.current_session_id = None
    
    async def start_task_session(self, task_name: str, participant_id: str = "vesper_vlm") -> str:
        """Start a new CASAS tracking session for a VESPER task"""
        
        self.current_session_id = f"vesper_{participant_id}_{int(datetime.now().timestamp())}"
        
        # Map task name to CASAS task ID
        task_mapping = {
            "make phone call": 1,
            "phone call": 1,
            "call": 1,
            "wash hands": 2,
            "wash": 2,
            "cook oatmeal": 3,
            "cook": 3,
            "oatmeal": 3,
            "eat meal": 4,
            "eat": 4,
            "meal": 4,
            "clean dishes": 5,
            "clean": 5,
            "dishes": 5
        }
        
        task_id = task_mapping.get(task_name.lower(), 1)
        
        # Log task execution start
        task_data = {
            "participant_id": participant_id,
            "task_id": task_id,
            "task_name": task_name,
            "error_type": "none", 
            "start_time": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(f"{self.dataset_url}/task_execution", json=task_data)
            if response.status_code == 200:
                print(f"🔗 CASAS session started: {self.current_session_id}")
                return self.current_session_id
        except Exception as e:
            print(f"⚠️ Failed to start CASAS session: {e}")
        
        return self.current_session_id
    
    async def process_vlm_action(self, action_data: Dict[str, Any]):
        """Process VLM action and trigger appropriate CASAS sensors"""
        
        if not self.current_session_id:
            print("⚠️ No active CASAS session. Call start_task_session() first.")
            return
        
        action_type = action_data.get("type", "").lower()
        location = action_data.get("location", "").lower()
        object_name = action_data.get("object", "").lower()
        appliance = action_data.get("appliance", "").lower()
        
        print(f"🔗 Processing VLM action: {action_type}")
        
        if action_type in ["move_to", "navigate_to", "go_to"]:
            await self.trigger_motion_sequence(location)
        
        elif action_type in ["interact_with", "pick_up", "take", "get"]:
            await self.trigger_item_interaction(object_name, "ABSENT")
        
        elif action_type in ["put_down", "place", "return"]:
            await self.trigger_item_interaction(object_name, "PRESENT")
        
        elif action_type in ["use_appliance", "turn_on", "activate"]:
            await self.control_appliance(appliance, "ON")
        
        elif action_type in ["turn_off", "deactivate", "stop"]:
            await self.control_appliance(appliance, "OFF")
        
        elif action_type in ["phone_call", "call"]:
            await self.handle_phone_sequence()
    
    async def trigger_motion_sequence(self, target_location: str):
        """Trigger motion sensors based on navigation to location"""
        
        sensors = self.room_to_sensors.get(target_location, [])
        
        if not sensors:
            # Try partial matching
            for room, room_sensors in self.room_to_sensors.items():
                if target_location in room or room in target_location:
                    sensors = room_sensors
                    break
        
        for sensor_id in sensors:
            try:
                response = requests.post(f"{self.motion_url}/trigger", json={
                    "sensor_id": sensor_id,
                    "state": "ON"
                })
                if response.status_code == 200:
                    print(f"  ✅ Motion: {sensor_id} ON")
                await asyncio.sleep(0.5)  # Brief delay between sensors
            except Exception as e:
                print(f"  ❌ Motion sensor {sensor_id} failed: {e}")
    
    async def trigger_item_interaction(self, object_name: str, state: str):
        """Trigger item sensor based on object interaction"""
        
        sensor_id = self.object_to_sensors.get(object_name)
        
        if not sensor_id:
            # Try partial matching
            for obj, obj_sensor in self.object_to_sensors.items():
                if object_name in obj or obj in object_name:
                    sensor_id = obj_sensor
                    break
        
        if sensor_id:
            try:
                response = requests.post(f"{self.item_url}/interact", json={
                    "sensor_id": sensor_id,
                    "state": state
                })
                if response.status_code == 200:
                    print(f"  ✅ Item: {sensor_id} {state}")
            except Exception as e:
                print(f"  ❌ Item sensor {sensor_id} failed: {e}")
    
    async def control_appliance(self, appliance_name: str, state: str):
        """Control appliance based on VLM action"""
        
        appliance_id = self.appliance_to_sensors.get(appliance_name)
        
        if not appliance_id:
            # Try partial matching
            for app, app_id in self.appliance_to_sensors.items():
                if appliance_name in app or app in appliance_name:
                    appliance_id = app_id
                    break
        
        if appliance_id:
            try:
                response = requests.post(f"{self.appliance_url}/control", json={
                    "appliance_id": appliance_id,
                    "state": state
                })
                if response.status_code == 200:
                    print(f"  ✅ Appliance: {appliance_id} {state}")
            except Exception as e:
                print(f"  ❌ Appliance {appliance_id} failed: {e}")
    
    async def handle_phone_sequence(self):
        """Handle phone call sequence"""
        
        # Phone pickup
        await self.control_appliance("phone", "PICKUP")
        await asyncio.sleep(2)
        
        # Phone hangup
        await self.control_appliance("phone", "HANGUP")
    
    async def end_task_session(self) -> Dict[str, Any]:
        """End current CASAS session and get results"""
        
        if not self.current_session_id:
            return {"error": "No active session"}
        
        session_id = self.current_session_id
        self.current_session_id = None
        
        # Wait a moment for all events to be processed
        await asyncio.sleep(2)
        
        try:
            # Get session summary
            response = requests.get(f"{self.dataset_url}/sessions")
            if response.status_code == 200:
                sessions = response.json().get("active_sessions", [])
                for session in sessions:
                    if session["session_id"] == session_id:
                        print(f"🏁 CASAS session ended: {session['event_count']} events captured")
                        return session
        except Exception as e:
            print(f"⚠️ Failed to get session summary: {e}")
        
        return {"session_id": session_id, "status": "completed"}

# Integration Example for VESPER Navigation Script
"""
Add this to your llm_bge_navigation.py:

# At the top of the file
from vesper_casas_bridge import VESPERCASASBridge

# In your navigation class initialization
class YourVESPERNavigationClass:
    def __init__(self):
        # Your existing initialization
        self.casas_bridge = VESPERCASASBridge()
        self.task_session_active = False
    
    async def execute_task_sequence(self, tasks: List[str]):
        # Start CASAS tracking
        if tasks:
            session_id = await self.casas_bridge.start_task_session(tasks[0])
            self.task_session_active = True
        
        # Your existing task execution
        for task in tasks:
            await self.execute_single_task(task)
        
        # End CASAS tracking
        if self.task_session_active:
            results = await self.casas_bridge.end_task_session()
            print(f"📊 CASAS Results: {results}")
            self.task_session_active = False
    
    async def execute_single_task(self, task: str):
        # Your existing VLM task execution
        
        # NEW: Parse VLM response and trigger CASAS sensors
        if "go to kitchen" in task.lower():
            await self.casas_bridge.process_vlm_action({
                "type": "move_to",
                "location": "kitchen"
            })
        
        elif "pick up oatmeal" in task.lower():
            await self.casas_bridge.process_vlm_action({
                "type": "interact_with", 
                "object": "oatmeal"
            })
        
        elif "turn on burner" in task.lower():
            await self.casas_bridge.process_vlm_action({
                "type": "use_appliance",
                "appliance": "burner"
            })
        
        # Add more VLM action mappings as needed
"""
