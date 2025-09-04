"""
VESPER Blender-CASAS Integration Bridge
======================================

Connects Blender VLM navigation with CASAS dataset generation.
This creates the missing link between Blender actor movement and CASAS sensor events.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add VESPER root to path
vesper_root = r"C:\Users\hbui11\Desktop\vesper_llm"
if vesper_root not in sys.path:
    sys.path.insert(0, vesper_root)

class BlenderCASASBridge:
    """Bridge between Blender navigation and CASAS dataset generation"""
    
    def __init__(self):
        self.blender_api = "http://localhost:8088"  # Backend console
        self.active_session = None
        self.casas_events = []
        self.position_history = []
        
        # CASAS sensor mapping based on room/location
        self.location_to_casas = {
            "livingroom": ["M01", "M02"],
            "kitchen": ["M03", "M04", "I01", "A01"], 
            "bathroom": ["M05", "M06", "A02"],
            "bedroom": ["M07", "M08"],
            "dining": ["M09", "M10", "I02"],
            "office": ["M11", "M12"],
            "hallway": ["M13", "M14"],
            "entrance": ["M15", "M16"]
        }
        
        # Activity patterns that generate CASAS events
        self.activity_patterns = {
            "phone_call": {
                "sensors": ["M13", "A01"],  # Phone location + appliance
                "sequence": ["M13:ON", "A01:PHONE_PICKUP", "A01:PHONE_HANGUP", "M13:OFF"]
            },
            "wash_hands": {
                "sensors": ["M05", "M06", "A02"],  # Bathroom motion + water
                "sequence": ["M05:ON", "M06:ON", "A02:WATER_ON", "A02:WATER_OFF", "M06:OFF", "M05:OFF"]
            },
            "cook": {
                "sensors": ["M03", "M04", "I01", "A01"],  # Kitchen sensors
                "sequence": ["M03:ON", "I01:ABSENT", "A01:BURNER_ON", "A01:BURNER_OFF", "I01:PRESENT", "M03:OFF"]
            },
            "eat": {
                "sensors": ["M09", "M10", "I02"],  # Dining area
                "sequence": ["M09:ON", "I02:ABSENT", "M10:ON", "I02:PRESENT", "M09:OFF"]
            },
            "clean": {
                "sensors": ["M03", "M04", "A02"],  # Kitchen + water
                "sequence": ["M03:ON", "A02:WATER_ON", "M04:ON", "A02:WATER_OFF", "M03:OFF"]
            }
        }
        
    def start_blender_task_session(self, task_type: str) -> bool:
        """Start a Blender task session with CASAS logging"""
        print(f"🎬 Starting Blender-CASAS session for: {task_type}")
        
        # Initialize session
        self.active_session = {
            "task_type": task_type,
            "start_time": datetime.now(),
            "session_id": f"blender_casas_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "events": []
        }
        
        # Reset tracking
        self.casas_events.clear()
        self.position_history.clear()
        
        print(f"✅ Session started: {self.active_session['session_id']}")
        return True
        
    def check_blender_navigation_status(self) -> Dict[str, Any]:
        """Check current status of Blender navigation"""
        try:
            # This would connect to Blender through the backend console
            response = requests.get(f"{self.blender_api}/api/blender/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except:
            pass
            
        # Simulated status for demo
        return {
            "blender_active": True,
            "actor_position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "current_room": "livingroom",
            "task_active": True
        }
        
    def simulate_blender_task_execution(self, task_type: str, duration: int = 60):
        """Simulate Blender task execution with realistic movement and sensor activation"""
        print(f"\\n🎮 Simulating Blender {task_type} task execution")
        print(f"⏱️  Duration: {duration} seconds")
        print("=" * 50)
        
        if not self.start_blender_task_session(task_type):
            return []
            
        # Get task pattern
        pattern = self.activity_patterns.get(task_type, self.activity_patterns["phone_call"])
        sequence = pattern["sequence"]
        
        print(f"📋 Task pattern: {len(sequence)} steps")
        
        # Execute sequence with realistic timing
        step_duration = duration / len(sequence)
        
        for i, step in enumerate(sequence):
            sensor, message = step.split(":")
            
            print(f"   Step {i+1}/{len(sequence)}: {sensor} → {message}")
            
            # Generate CASAS event
            casas_event = self._generate_casas_event(sensor, message, task_type)
            self.casas_events.append(casas_event)
            self.active_session["events"].append(casas_event)
            
            # Wait between steps
            if i < len(sequence) - 1:  # Don't wait after last step
                time.sleep(step_duration)
                
        print(f"\\n✅ Task execution completed!")
        print(f"📊 Generated {len(self.casas_events)} CASAS events")
        
        return self.casas_events
        
    def _generate_casas_event(self, sensor: str, message: str, context: str) -> Dict[str, Any]:
        """Generate a properly formatted CASAS event"""
        timestamp = datetime.now()
        
        casas_event = {
            "date": timestamp.strftime("%Y-%m-%d"),
            "time": timestamp.strftime("%H:%M:%S.%f")[:-3],
            "sensor": sensor,
            "message": message,
            "context": context,
            "source": "blender_simulation"
        }
        
        # Log the event
        casas_line = f"{casas_event['date']},{casas_event['time']},{sensor},{message}"
        print(f"    🔹 CASAS: {casas_line}")
        
        return casas_event
        
    def save_blender_casas_dataset(self, filename: Optional[str] = None) -> str:
        """Save the generated CASAS dataset from Blender simulation"""
        if not self.active_session:
            raise ValueError("No active session to save")
            
        if filename is None:
            task_type = self.active_session["task_type"]
            session_id = self.active_session["session_id"]
            filename = f"blender_casas_{task_type}_{session_id}.csv"
            
        # Write CASAS format CSV
        with open(filename, 'w') as f:
            f.write("date,time,sensor,message\\n")
            for event in self.casas_events:
                f.write(f"{event['date']},{event['time']},{event['sensor']},{event['message']}\\n")
                
        print(f"💾 CASAS dataset saved: {filename}")
        return filename
        
    def compare_with_ground_truth(self, participant_id: int, task_id: str) -> Dict[str, Any]:
        """Compare Blender-generated CASAS data with ground truth"""
        if not self.casas_events:
            print("❌ No CASAS events to compare")
            return {}
            
        # Load ground truth
        gt_file = f"casas_testbed/data/casas_ground_truth/adl_noerror/p{participant_id:02d}.{task_id}.csv"
        ground_truth = self._load_ground_truth(gt_file)
        
        if not ground_truth:
            print(f"❌ Could not load ground truth: {gt_file}")
            return {}
            
        print(f"\\n🔍 Comparing with ground truth...")
        print(f"   Ground Truth: {len(ground_truth)} events")
        print(f"   Blender CASAS: {len(self.casas_events)} events")
        
        # Basic comparison metrics
        gt_sensors = set(event['sensor'] for event in ground_truth)
        blender_sensors = set(event['sensor'] for event in self.casas_events)
        
        sensor_overlap = len(gt_sensors & blender_sensors)
        sensor_coverage = sensor_overlap / len(gt_sensors) if gt_sensors else 0
        
        event_ratio = min(len(self.casas_events), len(ground_truth)) / max(len(self.casas_events), len(ground_truth), 1)
        
        overall_similarity = (sensor_coverage + event_ratio) / 2
        
        comparison = {
            "ground_truth_events": len(ground_truth),
            "blender_events": len(self.casas_events),
            "sensor_coverage": sensor_coverage,
            "event_ratio": event_ratio,
            "overall_similarity": overall_similarity,
            "gt_sensors": list(gt_sensors),
            "blender_sensors": list(blender_sensors),
            "common_sensors": list(gt_sensors & blender_sensors)
        }
        
        print(f"\\n📊 Comparison Results:")
        print(f"   Sensor Coverage: {sensor_coverage:.1%}")
        print(f"   Event Ratio: {event_ratio:.3f}")
        print(f"   Overall Similarity: {overall_similarity:.3f}")
        
        return comparison
        
    def _load_ground_truth(self, file_path: str) -> List[Dict]:
        """Load ground truth CASAS data"""
        try:
            import csv
            ground_truth = []
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ground_truth.append(row)
            return ground_truth
        except Exception as e:
            print(f"❌ Error loading ground truth: {e}")
            return []
            
    def generate_blender_casas_report(self, participant_id: int, task_id: str) -> str:
        """Generate comprehensive report of Blender-CASAS integration"""
        if not self.active_session:
            raise ValueError("No active session")
            
        task_type = self.active_session["task_type"]
        
        # Perform comparison
        comparison = self.compare_with_ground_truth(participant_id, task_id)
        
        # Generate report
        report_file = f"blender_casas_report_p{participant_id:02d}_{task_id}.md"
        
        with open(report_file, 'w') as f:
            f.write(f"# Blender-CASAS Integration Report\\n\\n")
            f.write(f"**Task Type:** {task_type}\\n")
            f.write(f"**Participant:** P{participant_id:02d}\\n")
            f.write(f"**Task ID:** {task_id}\\n")
            f.write(f"**Session:** {self.active_session['session_id']}\\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
            
            f.write(f"## Execution Summary\\n\\n")
            f.write(f"- **Start Time:** {self.active_session['start_time'].strftime('%H:%M:%S')}\\n")
            f.write(f"- **Blender Events:** {len(self.casas_events)}\\n")
            f.write(f"- **Ground Truth Events:** {comparison.get('ground_truth_events', 0)}\\n")
            f.write(f"- **Overall Similarity:** {comparison.get('overall_similarity', 0):.3f}\\n\\n")
            
            f.write(f"## Sensor Analysis\\n\\n")
            f.write(f"- **Ground Truth Sensors:** {', '.join(comparison.get('gt_sensors', []))}\\n")
            f.write(f"- **Blender Sensors:** {', '.join(comparison.get('blender_sensors', []))}\\n")
            f.write(f"- **Common Sensors:** {', '.join(comparison.get('common_sensors', []))}\\n")
            f.write(f"- **Sensor Coverage:** {comparison.get('sensor_coverage', 0):.1%}\\n\\n")
            
            f.write(f"## Generated CASAS Events\\n\\n")
            for i, event in enumerate(self.casas_events, 1):
                f.write(f"{i}. `{event['date']},{event['time']},{event['sensor']},{event['message']}`\\n")
                
        print(f"\\n📄 Report generated: {report_file}")
        return report_file

def demo_blender_casas_integration():
    """Demo the complete Blender-CASAS integration"""
    print("🎮 VESPER Blender-CASAS Integration Demo")
    print("=" * 60)
    
    bridge = BlenderCASASBridge()
    
    # Simulate phone call task
    task_type = "phone_call"
    print(f"\\n🎯 Demonstrating {task_type} task integration")
    
    # Execute task in Blender (simulated)
    events = bridge.simulate_blender_task_execution(task_type, duration=30)
    
    if events:
        # Save CASAS dataset
        dataset_file = bridge.save_blender_casas_dataset()
        
        # Compare with ground truth
        comparison = bridge.compare_with_ground_truth(participant_id=1, task_id="t1")
        
        # Generate report
        report_file = bridge.generate_blender_casas_report(participant_id=1, task_id="t1")
        
        print(f"\\n🎉 Integration demo completed!")
        print(f"📊 Similarity: {comparison.get('overall_similarity', 0):.1%}")
        print(f"💾 Dataset: {dataset_file}")
        print(f"📄 Report: {report_file}")
        
        return True
    else:
        print("❌ Integration demo failed")
        return False

if __name__ == "__main__":
    demo_blender_casas_integration()
