"""
VESPER-CASAS Dataset Generation Complete Workflow
================================================

This script demonstrates the complete process of generating VESPER datasets
for comparison with CASAS ground truth data.
"""

import asyncio
import requests
import json
from datetime import datetime
from typing import Dict, List

class VESPERCASASDatasetGenerator:
    """Complete dataset generation workflow"""
    
    def __init__(self):
        # Service URLs for CASAS virtual environment
        self.motion_service = "http://localhost:8001"
        self.item_service = "http://localhost:8002"
        self.appliance_service = "http://localhost:8003"
        self.dataset_manager = "http://localhost:8004"
        
        # CASAS task definitions
        self.casas_tasks = {
            1: {
                "name": "Make phone call",
                "vlm_instruction": "Please make a phone call",
                "expected_sensors": ["*", "M01", "M02"],
                "expected_sequence": [
                    ("M01", "ON"),    # Move to phone area
                    ("*", "PICKUP"),  # Pick up phone
                    ("*", "HANGUP")   # Hang up phone
                ]
            },
            2: {
                "name": "Wash hands", 
                "vlm_instruction": "Please wash your hands",
                "expected_sensors": ["AD1-A", "AD1-B", "M06", "M07"],
                "expected_sequence": [
                    ("M06", "ON"),    # Move to bathroom
                    ("AD1-A", "ON"),  # Turn on hot water
                    ("AD1-B", "ON"),  # Turn on cold water
                    ("AD1-A", "OFF"), # Turn off water
                    ("AD1-B", "OFF")
                ]
            },
            3: {
                "name": "Cook oatmeal",
                "vlm_instruction": "Please cook oatmeal", 
                "expected_sensors": ["I01", "I02", "I03", "AD1-C", "M01"],
                "expected_sequence": [
                    ("M01", "ON"),      # Move to kitchen
                    ("I01", "ABSENT"),  # Take oatmeal
                    ("I02", "ABSENT"),  # Take raisins  
                    ("I03", "PRESENT"), # Get bowl
                    ("AD1-C", "ON"),    # Turn on burner
                    ("AD1-C", "OFF")    # Turn off burner
                ]
            },
            4: {
                "name": "Eat meal",
                "vlm_instruction": "Please eat your meal",
                "expected_sensors": ["I03", "I04", "I07", "M04", "M05"],
                "expected_sequence": [
                    ("M04", "ON"),      # Move to dining area
                    ("I07", "PRESENT"), # Get plate
                    ("I04", "PRESENT"), # Get spoon
                    ("M05", "ON")       # Sit down
                ]
            },
            5: {
                "name": "Clean dishes", 
                "vlm_instruction": "Please clean the dishes",
                "expected_sensors": ["AD1-A", "AD1-B", "I07", "I08"],
                "expected_sequence": [
                    ("M01", "ON"),      # Move to kitchen
                    ("I07", "ABSENT"),  # Take dirty plate
                    ("I08", "PRESENT"), # Get cup
                    ("AD1-A", "ON"),    # Turn on hot water
                    ("AD1-B", "ON"),    # Turn on cold water
                    ("AD1-A", "OFF"),   # Turn off water
                    ("AD1-B", "OFF")
                ]
            }
        }
    
    async def generate_vesper_dataset(self, participant_id: str = "vesper_vlm_001") -> Dict:
        """Generate complete VESPER dataset for all CASAS tasks"""
        
        print("🚀 Starting VESPER Dataset Generation")
        print("=" * 50)
        
        results = {
            "participant_id": participant_id,
            "generation_timestamp": datetime.now().isoformat(),
            "tasks_completed": 0,
            "total_events_generated": 0,
            "session_ids": [],
            "comparison_results": {}
        }
        
        # Generate dataset for each CASAS task
        for task_id, task_info in self.casas_tasks.items():
            print(f"\n📋 Task {task_id}: {task_info['name']}")
            print("-" * 30)
            
            # Execute task and capture session
            session_result = await self.execute_task_with_vlm(
                task_id, task_info, participant_id
            )
            
            results["session_ids"].append(session_result["session_id"])
            results["total_events_generated"] += session_result["event_count"]
            results["tasks_completed"] += 1
            
            # Request comparison with CASAS ground truth
            comparison = await self.request_casas_comparison(
                session_result["session_id"],
                f"p01.t{task_id}.csv",  # CASAS ground truth file
                task_id,
                participant_id
            )
            
            results["comparison_results"][f"task_{task_id}"] = comparison
            
            print(f"✅ Task {task_id} completed - {session_result['event_count']} events generated")
        
        # Export complete dataset
        dataset_export = await self.export_complete_dataset(results["session_ids"])
        results["dataset_file"] = dataset_export["filename"]
        
        print(f"\n🎉 Dataset Generation Complete!")
        print(f"📊 Total Tasks: {results['tasks_completed']}")
        print(f"📈 Total Events: {results['total_events_generated']}")
        print(f"📁 Dataset File: {results['dataset_file']}")
        
        return results
    
    async def execute_task_with_vlm(self, task_id: int, task_info: Dict, participant_id: str) -> Dict:
        """Execute a single task with VLM and capture CASAS events"""
        
        # Start task tracking
        task_data = {
            "participant_id": participant_id,
            "task_id": task_id,
            "task_name": task_info["name"],
            "error_type": "none",
            "start_time": datetime.now().isoformat()
        }
        
        response = requests.post(f"{self.dataset_manager}/task_execution", json=task_data)
        
        # Generate session ID for this task execution
        session_id = f"vesper_task_{task_id}_{int(datetime.now().timestamp())}"
        
        # Simulate VLM execution by triggering expected sensor sequence
        event_count = 0
        for sensor_id, state in task_info["expected_sequence"]:
            await self.trigger_sensor_event(sensor_id, state)
            event_count += 1
            await asyncio.sleep(1)  # Realistic timing between actions
        
        return {
            "session_id": session_id,
            "task_id": task_id,
            "event_count": event_count,
            "completion_time": datetime.now().isoformat()
        }
    
    async def trigger_sensor_event(self, sensor_id: str, state: str):
        """Trigger a specific sensor event in the virtual environment"""
        
        if sensor_id.startswith("M"):
            # Motion sensor
            response = requests.post(f"{self.motion_service}/trigger", json={
                "sensor_id": sensor_id,
                "state": state
            })
        elif sensor_id.startswith("I"):
            # Item sensor
            response = requests.post(f"{self.item_service}/interact", json={
                "sensor_id": sensor_id,
                "state": state
            })
        elif sensor_id.startswith("AD1") or sensor_id == "*":
            # Appliance controller
            response = requests.post(f"{self.appliance_service}/control", json={
                "appliance_id": sensor_id,
                "state": state
            })
        
        if response.status_code == 200:
            print(f"  ✅ {sensor_id}: {state}")
        else:
            print(f"  ❌ Failed to trigger {sensor_id}: {state}")
    
    async def request_casas_comparison(self, session_id: str, casas_file: str, task_id: int, participant_id: str) -> Dict:
        """Request comparison between VESPER data and CASAS ground truth"""
        
        comparison_request = {
            "vesper_session_id": session_id,
            "casas_reference_file": casas_file,
            "task_id": task_id,
            "participant_id": participant_id
        }
        
        response = requests.post(f"{self.dataset_manager}/compare", json=comparison_request)
        
        if response.status_code == 200:
            # Wait a moment for comparison to complete
            await asyncio.sleep(2)
            
            # Get comparison results
            result_response = requests.get(f"{self.dataset_manager}/comparison/{session_id}")
            if result_response.status_code == 200:
                return result_response.json()
        
        return {"error": "Comparison failed"}
    
    async def export_complete_dataset(self, session_ids: List[str]) -> Dict:
        """Export complete VESPER dataset in CASAS format"""
        
        export_request = {
            "session_ids": session_ids,
            "format": "casas_csv",
            "include_comparison": True
        }
        
        response = requests.post(f"{self.dataset_manager}/export", json=export_request)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Export failed"}

# Usage Example
async def main():
    """Main execution example"""
    
    generator = VESPERCASASDatasetGenerator()
    
    # Generate dataset for VESPER VLM participant
    results = await generator.generate_vesper_dataset("vesper_vlm_001")
    
    # Print summary
    print("\n📊 DATASET GENERATION SUMMARY")
    print("=" * 40)
    for task_id, comparison in results["comparison_results"].items():
        if "overall_score" in comparison:
            print(f"Task {task_id}: {comparison['overall_score']:.2f} similarity")
        else:
            print(f"Task {task_id}: Comparison failed")
    
    print(f"\n📁 Complete dataset saved as: {results['dataset_file']}")

if __name__ == "__main__":
    asyncio.run(main())
