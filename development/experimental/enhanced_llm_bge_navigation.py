"""
VESPER BGE Navigation with CASAS Dataset Generation
===================================================

Enhanced version of your llm_bge_navigation.py that automatically generates
CASAS-format datasets during VLM navigation for research comparison.

Usage:
1. Load this script in Blender Text Editor
2. Run the CASAS virtual environment: docker-compose -f virtual-interaction/docker-compose.casas.yml up -d
3. Press P to start BGE navigation
4. CASAS events will be automatically generated and compared with ground truth
"""

import bge
import json
import requests
import asyncio
from datetime import datetime
from mathutils import Vector

# Import your existing VESPER navigation components
try:
    from vesper_casas_bridge import VESPERCASASBridge
    CASAS_ENABLED = True
    print("🔗 CASAS integration enabled")
except ImportError:
    CASAS_ENABLED = False
    print("⚠️ CASAS integration disabled - bridge not found")

class EnhancedVESPERNavigation:
    """VESPER Navigation with CASAS dataset generation"""
    
    def __init__(self):
        # Your existing VESPER initialization
        self.scene = bge.logic.getCurrentScene()
        self.actor = None
        self.camera = None
        self.movement_speed = 0.05
        self.target_tolerance = 0.1
        
        # CASAS integration
        if CASAS_ENABLED:
            self.casas_bridge = VESPERCASASBridge()
            self.task_session_active = False
            self.current_participant_id = f"vesper_vlm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Task definitions with CASAS mapping
        self.task_routines = {
            "morning_routine": [
                "Go to bathroom",
                "Wash hands", 
                "Go to kitchen",
                "Make coffee"
            ],
            "cooking_routine": [
                "Go to kitchen",
                "Get oatmeal",
                "Get bowl", 
                "Cook oatmeal",
                "Eat meal"
            ],
            "cleaning_routine": [
                "Go to kitchen",
                "Get dirty dishes",
                "Wash dishes",
                "Put away dishes"
            ]
        }
        
        self.setup_actors()
    
    def setup_actors(self):
        """Find and setup Actor and BirdEyeCamera"""
        for obj in self.scene.objects:
            if "Actor" in obj.name:
                self.actor = obj
                print(f"🎮 Found actor: {obj.name}")
            elif "BirdEyeCamera" in obj.name or "Camera" in obj.name:
                self.camera = obj
                print(f"📷 Found camera: {obj.name}")
    
    def start_navigation(self):
        """Main navigation entry point"""
        if not self.actor:
            print("❌ No Actor found in scene")
            return
        
        print("🚀 Starting Enhanced VESPER Navigation with CASAS tracking")
        
        # Select random routine for demonstration
        import random
        routine_name = random.choice(list(self.task_routines.keys()))
        tasks = self.task_routines[routine_name]
        
        print(f"📋 Selected routine: {routine_name}")
        print(f"📋 Tasks: {tasks}")
        
        # Start CASAS session
        if CASAS_ENABLED:
            asyncio.create_task(self.start_casas_session(routine_name, tasks))
        
        # Execute navigation
        self.execute_task_sequence(tasks)
    
    async def start_casas_session(self, routine_name: str, tasks: list):
        """Start CASAS tracking session"""
        try:
            session_id = await self.casas_bridge.start_task_session(
                routine_name, 
                self.current_participant_id
            )
            self.task_session_active = True
            print(f"📊 CASAS tracking started: {session_id}")
        except Exception as e:
            print(f"⚠️ CASAS session start failed: {e}")
    
    def execute_task_sequence(self, tasks: list):
        """Execute sequence of tasks with CASAS tracking"""
        for i, task in enumerate(tasks, 1):
            print(f"\n📍 BGE Step {i} - Task: {task}")
            
            # Execute VLM navigation (your existing code)
            success = self.execute_single_task(task)
            
            # Trigger CASAS sensors based on task
            if CASAS_ENABLED:
                self.trigger_casas_for_task(task)
            
            if not success:
                print(f"❌ Task failed: {task}")
                break
        
        # End CASAS session
        if CASAS_ENABLED and self.task_session_active:
            asyncio.create_task(self.end_casas_session())
    
    def execute_single_task(self, task: str) -> bool:
        """Execute single task with VLM (your existing navigation logic)"""
        
        # Capture screenshot for VLM
        screenshot_path = self.capture_screenshot()
        
        # Get VLM decision (your existing code)
        vlm_response = self.get_vlm_navigation_decision(task, screenshot_path)
        
        if not vlm_response:
            print(f"⚠️ VLM response failed for task: {task}")
            return False
        
        # Parse and execute movement
        direction = self.parse_vlm_response(vlm_response)
        
        if direction and direction != "STAY":
            success = self.move_actor(direction)
            print(f"🎮 BGE: Actor moved {direction}")
            return success
        
        return True
    
    def trigger_casas_for_task(self, task: str):
        """Trigger appropriate CASAS sensors based on task"""
        
        task_lower = task.lower()
        
        # Motion sensors based on navigation
        if "bathroom" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "move_to",
                "location": "bathroom"
            }))
        
        elif "kitchen" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "move_to", 
                "location": "kitchen"
            }))
        
        elif "living room" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "move_to",
                "location": "living_room"
            }))
        
        # Object interactions
        if "oatmeal" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "interact_with",
                "object": "oatmeal"
            }))
        
        elif "bowl" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "interact_with",
                "object": "bowl"
            }))
        
        elif "dish" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "interact_with",
                "object": "plate"
            }))
        
        # Appliance usage
        if "wash hands" in task_lower or "wash" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "use_appliance",
                "appliance": "water_faucet"
            }))
        
        elif "cook" in task_lower or "burner" in task_lower:
            asyncio.create_task(self.casas_bridge.process_vlm_action({
                "type": "use_appliance",
                "appliance": "burner"
            }))
        
        elif "phone call" in task_lower or "call" in task_lower:
            asyncio.create_task(self.casas_bridge.handle_phone_sequence())
    
    async def end_casas_session(self):
        """End CASAS session and get comparison results"""
        try:
            results = await self.casas_bridge.end_task_session()
            self.task_session_active = False
            
            print(f"\n📊 CASAS SESSION COMPLETED")
            print(f"Events captured: {results.get('event_count', 'Unknown')}")
            
            # Request comparison with ground truth
            session_id = results.get('session_id')
            if session_id:
                await self.request_ground_truth_comparison(session_id)
            
        except Exception as e:
            print(f"⚠️ CASAS session end failed: {e}")
    
    async def request_ground_truth_comparison(self, session_id: str):
        """Request comparison with CASAS ground truth data"""
        try:
            # Request comparison (example with cooking task)
            comparison_request = {
                "vesper_session_id": session_id,
                "casas_reference_file": "p01.t3.csv",  # Cook oatmeal ground truth
                "task_id": 3,
                "participant_id": self.current_participant_id
            }
            
            response = requests.post(
                "http://localhost:8004/compare", 
                json=comparison_request
            )
            
            if response.status_code == 200:
                print("📈 Comparison with CASAS ground truth requested")
                
                # Wait and get results
                await asyncio.sleep(3)
                result_response = requests.get(
                    f"http://localhost:8004/comparison/{session_id}"
                )
                
                if result_response.status_code == 200:
                    comparison = result_response.json()
                    print(f"🎯 Similarity Score: {comparison.get('overall_score', 'N/A'):.2f}")
                    print(f"📊 Sensor Coverage: {comparison.get('sensor_coverage', {}).get('coverage_score', 'N/A'):.2f}")
                
        except Exception as e:
            print(f"⚠️ Ground truth comparison failed: {e}")
    
    # Your existing VLM and navigation methods
    def capture_screenshot(self) -> str:
        """Capture bird's eye screenshot"""
        # Your existing screenshot logic
        pass
    
    def get_vlm_navigation_decision(self, task: str, screenshot_path: str) -> str:
        """Get VLM decision for navigation"""
        # Your existing VLM communication logic
        pass
    
    def parse_vlm_response(self, response: str) -> str:
        """Parse VLM response to get direction"""
        # Your existing response parsing logic
        pass
    
    def move_actor(self, direction: str) -> bool:
        """Move actor in specified direction"""
        # Your existing movement logic
        pass

# BGE Main Function
def main():
    """Main BGE execution function"""
    
    # Initialize enhanced navigation
    navigator = EnhancedVESPERNavigation()
    
    # Start navigation with CASAS tracking
    navigator.start_navigation()

# BGE Logic Brick Integration
if __name__ == "__main__":
    main()

"""
Integration Instructions:
========================

1. Deploy CASAS Environment:
   cd virtual-interaction
   docker-compose -f docker-compose.casas.yml up -d

2. Verify Services:
   curl http://localhost:8001/health  # Motion sensors
   curl http://localhost:8004/health  # Dataset manager

3. Load in Blender:
   - Replace your existing llm_bge_navigation.py with this enhanced version
   - Ensure vesper_casas_bridge.py is in your Python path
   - Press P to start BGE navigation

4. Automatic Dataset Generation:
   - CASAS events automatically generated during navigation
   - Comparison with ground truth automatically requested
   - Results displayed in Blender console

5. View Generated Data:
   curl http://localhost:8004/sessions  # View active sessions
   curl http://localhost:8004/export   # Export complete dataset
"""
