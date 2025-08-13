"""
Real-time VESPER LLM Evaluation in Blender
==========================================

This script integrates with the Blender VESPER system to perform
real-time evaluation of LLM navigation performance.

Run this script within Blender to collect actual performance data.
"""

import bpy
import json
import time
import math
import os
from mathutils import Vector
from typing import Dict, List, Tuple

class VESPERLiveEvaluator:
    """Live evaluation system that works with actual Blender VESPER addon"""
    
    def __init__(self):
        self.evaluation_data = []
        self.current_test = None
        self.start_time = None
        
    def start_evaluation_test(self, test_id: str, target_room: str, task_description: str):
        """Start a new evaluation test"""
        actor = bpy.context.scene.objects.get("Player")
        if not actor:
            print("❌ No Player actor found!")
            return False
        
        self.current_test = {
            "test_id": test_id,
            "target_room": target_room,
            "task_description": task_description,
            "start_position": list(actor.location),
            "start_time": time.time(),
            "path_points": [list(actor.location)],
            "llm_commands": [],
            "screenshots_taken": 0,
            "completed": False
        }
        
        print(f"🔬 Starting evaluation test: {test_id}")
        print(f"📍 Starting position: {actor.location}")
        print(f"🎯 Target room: {target_room}")
        
        return True
    
    def record_movement_step(self):
        """Record each movement step for path analysis"""
        if not self.current_test:
            return
        
        actor = bpy.context.scene.objects.get("Player")
        if actor:
            self.current_test["path_points"].append(list(actor.location))
    
    def record_llm_command(self, command: str):
        """Record LLM command for analysis"""
        if not self.current_test:
            return
        
        self.current_test["llm_commands"].append({
            "command": command,
            "timestamp": time.time() - self.current_test["start_time"]
        })
    
    def record_screenshot(self):
        """Record screenshot capture for analysis"""
        if not self.current_test:
            return
        
        self.current_test["screenshots_taken"] += 1
    
    def end_evaluation_test(self, success: bool, final_room: str = None):
        """End the current evaluation test"""
        if not self.current_test:
            return
        
        actor = bpy.context.scene.objects.get("Player")
        if actor:
            self.current_test["final_position"] = list(actor.location)
        
        self.current_test["completion_time"] = time.time() - self.current_test["start_time"]
        self.current_test["success"] = success
        self.current_test["final_room"] = final_room or "Unknown"
        self.current_test["completed"] = True
        
        # Calculate metrics
        self.current_test["metrics"] = self.calculate_test_metrics()
        
        # Store the test
        self.evaluation_data.append(self.current_test)
        
        print(f"✅ Test {self.current_test['test_id']} completed")
        print(f"🎯 Success: {success}")
        print(f"⏱️ Time: {self.current_test['completion_time']:.2f}s")
        print(f"👣 Steps: {len(self.current_test['path_points']) - 1}")
        
        self.current_test = None
    
    def calculate_test_metrics(self) -> Dict:
        """Calculate detailed metrics for the current test"""
        if not self.current_test:
            return {}
        
        # Path analysis
        path_length = self.calculate_path_length(self.current_test["path_points"])
        straight_line_distance = self.calculate_distance(
            self.current_test["start_position"],
            self.current_test["final_position"]
        )
        
        path_efficiency = straight_line_distance / path_length if path_length > 0 else 0
        
        # Accuracy analysis
        target_accuracy = self.current_test["final_room"] == self.current_test["target_room"]
        
        # LLM analysis
        llm_responsiveness = len(self.current_test["llm_commands"]) / max(1, self.current_test["completion_time"])
        
        return {
            "path_length": path_length,
            "straight_line_distance": straight_line_distance,
            "path_efficiency": path_efficiency,
            "target_accuracy": target_accuracy,
            "steps_taken": len(self.current_test["path_points"]) - 1,
            "llm_commands_count": len(self.current_test["llm_commands"]),
            "llm_responsiveness": llm_responsiveness,
            "screenshots_per_step": self.current_test["screenshots_taken"] / max(1, len(self.current_test["path_points"]) - 1)
        }
    
    def calculate_path_length(self, path_points: List[List[float]]) -> float:
        """Calculate total path length"""
        total_length = 0.0
        for i in range(1, len(path_points)):
            total_length += self.calculate_distance(path_points[i-1], path_points[i])
        return total_length
    
    def calculate_distance(self, pos1: List[float], pos2: List[float]) -> float:
        """Calculate distance between two points"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def generate_live_report(self) -> str:
        """Generate evaluation report from actual test data"""
        if not self.evaluation_data:
            return "No evaluation data available"
        
        # Aggregate metrics
        total_tests = len(self.evaluation_data)
        successful_tests = sum(1 for test in self.evaluation_data if test["success"])
        
        avg_completion_time = sum(test["completion_time"] for test in self.evaluation_data) / total_tests
        avg_steps = sum(test["metrics"]["steps_taken"] for test in self.evaluation_data) / total_tests
        avg_path_efficiency = sum(test["metrics"]["path_efficiency"] for test in self.evaluation_data) / total_tests
        
        target_accuracy = sum(1 for test in self.evaluation_data if test["metrics"]["target_accuracy"]) / total_tests
        
        report = {
            "evaluation_summary": {
                "total_tests": total_tests,
                "success_rate": successful_tests / total_tests,
                "target_accuracy": target_accuracy,
                "average_completion_time": avg_completion_time,
                "average_steps_per_task": avg_steps,
                "average_path_efficiency": avg_path_efficiency
            },
            "detailed_results": self.evaluation_data
        }
        
        # Save report
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = f"vesper_live_evaluation_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Live Evaluation Report Generated: {report_path}")
        print(f"🎯 Success Rate: {successful_tests/total_tests:.1%}")
        print(f"📍 Target Accuracy: {target_accuracy:.1%}")
        print(f"⏱️ Avg Completion Time: {avg_completion_time:.2f}s")
        print(f"👣 Avg Steps per Task: {avg_steps:.1f}")
        
        return report_path

# Global evaluator instance for use in Blender
live_evaluator = VESPERLiveEvaluator()

# Convenience functions for use in VESPER addon
def start_test(test_id: str, target_room: str, task: str):
    """Start evaluation test - call from VESPER addon"""
    return live_evaluator.start_evaluation_test(test_id, target_room, task)

def record_step():
    """Record movement step - call from VESPER addon"""
    live_evaluator.record_movement_step()

def record_command(command: str):
    """Record LLM command - call from VESPER addon"""
    live_evaluator.record_llm_command(command)

def record_screenshot():
    """Record screenshot capture - call from VESPER addon"""
    live_evaluator.record_screenshot()

def end_test(success: bool, final_room: str = None):
    """End evaluation test - call from VESPER addon"""
    live_evaluator.end_evaluation_test(success, final_room)

def generate_report():
    """Generate evaluation report"""
    return live_evaluator.generate_live_report()

# Integration helper for your VESPER addon
def integrate_with_vesper():
    """Instructions for integrating with your VESPER addon"""
    integration_code = '''
    # Add these lines to your VESPER addon __init__.py:
    
    # Import evaluation system
    import sys
    import os
    eval_path = os.path.join(bpy.path.abspath("//"), "evaluation")
    if eval_path not in sys.path:
        sys.path.append(eval_path)
    
    try:
        from blender_evaluation import start_test, record_step, record_command, record_screenshot, end_test, generate_report
        EVALUATION_ENABLED = True
        print("✅ Evaluation system integrated")
    except ImportError:
        EVALUATION_ENABLED = False
        print("⚠️ Evaluation system not available")
    
    # Modify your move_actor_step_by_step function:
    def move_actor_step_by_step(self, target_x, target_y, step_size=0.12, max_steps=25):
        if EVALUATION_ENABLED:
            record_step()  # Record each movement
        
        # ... rest of your movement code ...
    
    # Modify your capture_birds_eye_view function:
    def capture_birds_eye_view(self):
        if EVALUATION_ENABLED:
            record_screenshot()  # Record screenshot capture
        
        # ... rest of your screenshot code ...
    
    # Modify your get_llm_room_order function:
    def get_llm_room_order(self, task):
        if EVALUATION_ENABLED:
            record_command(f"Task: {task}")  # Record LLM command
        
        # ... rest of your LLM code ...
    '''
    
    print("🔧 Integration code for VESPER addon:")
    print(integration_code)
    return integration_code

if __name__ == "__main__":
    print("🔬 VESPER Live Evaluation System Ready")
    print("Use integrate_with_vesper() for integration instructions")
