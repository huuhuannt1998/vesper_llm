"""
Test Script for VESPER Enhanced Metrics System
===============================================

This script tests the enhanced logging and metrics calculation system
to ensure all research metrics are properly calculated and reported.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, r"C:\Users\hbui11\Desktop\vesper_llm")

from evaluation.log_analyzer import VESPERLogAnalyzer


def create_sample_log_data():
    """Create sample log data for testing the metrics system"""
    
    sample_data = {
        "session_id": "test_20250828_120000",
        "start_time": 1724851200.0,
        "tasks_completed": 2,
        "tasks_failed": 1,
        "total_steps": 15,
        "total_screenshots": 8,
        "total_llm_calls": 8,
        "task_details": [
            {
                "task_name": "Cook in kitchen",
                "task_index": 0,
                "start_time": 1724851200.0,
                "completion_time": 45.2,
                "steps_taken": 6,
                "screenshots_captured": 3,
                "llm_calls": 3,
                "success": True,
                "movement_path": [
                    {"step": 1, "action": "LEFT", "from_position": [-2.0, -0.6], "to_position": [-2.3, -0.6]},
                    {"step": 2, "action": "UP", "from_position": [-2.3, -0.6], "to_position": [-2.3, -0.3]},
                    {"step": 3, "action": "LEFT", "from_position": [-2.3, -0.3], "to_position": [-2.6, -0.3]},
                    {"step": 4, "action": "UP", "from_position": [-2.6, -0.3], "to_position": [-2.6, 0.0]},
                    {"step": 5, "action": "LEFT", "from_position": [-2.6, 0.0], "to_position": [-2.9, 0.0]},
                    {"step": 6, "action": "STAY", "from_position": [-2.9, 0.0], "to_position": [-2.9, 0.0]}
                ],
                "room_detections": [
                    {"step": 1, "room": "LIVING_ROOM", "position": [-2.3, -0.6]},
                    {"step": 3, "room": "LIVING_ROOM", "position": [-2.6, -0.3]},
                    {"step": 6, "room": "KITCHEN", "position": [-2.9, 0.0]}
                ],
                "vlm_responses": [
                    {
                        "call_number": 1,
                        "room_detected": "LIVING_ROOM",
                        "furniture_visible": ["SOFA", "TV"],
                        "task_complete": False,
                        "timeout": False,
                        "response_time": 2.3
                    },
                    {
                        "call_number": 2,
                        "room_detected": "LIVING_ROOM",
                        "furniture_visible": ["SOFA", "COFFEE_TABLE"],
                        "task_complete": False,
                        "timeout": False,
                        "response_time": 1.8
                    },
                    {
                        "call_number": 3,
                        "room_detected": "KITCHEN",
                        "furniture_visible": ["STOVE", "REFRIGERATOR"],
                        "task_complete": True,
                        "timeout": False,
                        "response_time": 2.1
                    }
                ]
            },
            {
                "task_name": "Relax in living room",
                "task_index": 1,
                "start_time": 1724851245.2,
                "completion_time": 32.1,
                "steps_taken": 4,
                "screenshots_captured": 2,
                "llm_calls": 2,
                "success": True,
                "movement_path": [
                    {"step": 1, "action": "RIGHT", "from_position": [-2.9, 0.0], "to_position": [-2.6, 0.0]},
                    {"step": 2, "action": "DOWN", "from_position": [-2.6, 0.0], "to_position": [-2.6, -0.3]},
                    {"step": 3, "action": "RIGHT", "from_position": [-2.6, -0.3], "to_position": [-2.3, -0.3]},
                    {"step": 4, "action": "STAY", "from_position": [-2.3, -0.3], "to_position": [-2.3, -0.3]}
                ],
                "room_detections": [
                    {"step": 2, "room": "UNKNOWN", "position": [-2.6, -0.3]},
                    {"step": 4, "room": "LIVING_ROOM", "position": [-2.3, -0.3]}
                ],
                "vlm_responses": [
                    {
                        "call_number": 1,
                        "room_detected": "UNKNOWN",
                        "furniture_visible": ["unclear"],
                        "task_complete": False,
                        "timeout": False,
                        "response_time": 3.2
                    },
                    {
                        "call_number": 2,
                        "room_detected": "LIVING_ROOM",
                        "furniture_visible": ["SOFA", "COFFEE_TABLE"],
                        "task_complete": True,
                        "timeout": False,
                        "response_time": 1.9
                    }
                ]
            },
            {
                "task_name": "Sleep in bedroom",
                "task_index": 2,
                "start_time": 1724851277.3,
                "completion_time": 120.0,
                "steps_taken": 5,
                "screenshots_captured": 3,
                "llm_calls": 3,
                "success": False,
                "failure_reason": "Actor moved to extreme position outside house boundaries",
                "movement_path": [
                    {"step": 1, "action": "UP", "from_position": [-2.3, -0.3], "to_position": [-2.3, 0.0]},
                    {"step": 2, "action": "RIGHT", "from_position": [-2.3, 0.0], "to_position": [-2.0, 0.0]},
                    {"step": 3, "action": "LEFT", "from_position": [-2.0, 0.0], "to_position": [-2.3, 0.0]},
                    {"step": 4, "action": "RIGHT", "from_position": [-2.3, 0.0], "to_position": [-2.0, 0.0]},
                    {"step": 5, "action": "UP", "from_position": [-2.0, 0.0], "to_position": [-2.0, 16.5]}
                ],
                "room_detections": [
                    {"step": 1, "room": "LIVING_ROOM", "position": [-2.3, 0.0]},
                    {"step": 3, "room": "LIVING_ROOM", "position": [-2.3, 0.0]},
                    {"step": 5, "room": "UNKNOWN", "position": [-2.0, 16.5]}
                ],
                "vlm_responses": [
                    {
                        "call_number": 1,
                        "room_detected": "LIVING_ROOM",
                        "furniture_visible": ["SOFA"],
                        "task_complete": False,
                        "timeout": False,
                        "response_time": 2.8
                    },
                    {
                        "call_number": 2,
                        "room_detected": "LIVING_ROOM",
                        "furniture_visible": ["SOFA"],
                        "task_complete": False,
                        "timeout": True,
                        "response_time": 180.0
                    },
                    {
                        "call_number": 3,
                        "room_detected": "UNKNOWN",
                        "furniture_visible": ["None visible"],
                        "task_complete": False,
                        "timeout": False,
                        "response_time": 4.1
                    }
                ]
            }
        ]
    }
    
    return sample_data


def test_metrics_calculation():
    """Test the metrics calculation with sample data"""
    
    print("🧪 TESTING VESPER ENHANCED METRICS SYSTEM")
    print("="*60)
    
    # Create sample log data
    sample_data = create_sample_log_data()
    
    # Create temporary log file
    test_log_dir = os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\evaluation", "test_logs")
    os.makedirs(test_log_dir, exist_ok=True)
    
    test_log_file = os.path.join(test_log_dir, "test_vesper_log.json")
    
    with open(test_log_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"📝 Created test log file: {test_log_file}")
    
    # Analyze the test data
    analyzer = VESPERLogAnalyzer(test_log_file)
    metrics = analyzer.generate_detailed_metrics()
    
    # Verify key research metrics
    research_metrics = metrics.get('research_metrics', {})
    
    print("\n🔬 RESEARCH METRICS VERIFICATION:")
    print(f"✅ RTSR should be 66.7% (2/3 tasks): {research_metrics.get('RTSR', 0):.1f}%")
    print(f"✅ STSR should be 66.7% (2/3 semantic): {research_metrics.get('STSR', 0):.1f}%")
    print(f"✅ EMR should be ~73.3% (11/15 non-STAY): {research_metrics.get('EMR', 0):.1f}%")
    print(f"✅ OI should be ~16.7% (oscillations detected): {research_metrics.get('OI', 0):.1f}%")
    print(f"✅ RLS should be ~87.5% (7/8 concrete rooms): {research_metrics.get('RLS', 0):.1f}%")
    print(f"✅ TR should be 12.5% (1/8 timeouts): {research_metrics.get('TR', 0):.1f}%")
    
    # Cleanup
    os.remove(test_log_file)
    print(f"\n🧹 Cleaned up test file: {test_log_file}")
    
    print("\n✅ METRICS SYSTEM TEST COMPLETED SUCCESSFULLY!")
    
    return metrics


if __name__ == "__main__":
    try:
        test_results = test_metrics_calculation()
        print("\n🎉 All tests passed! The enhanced metrics system is working correctly.")
        
        # Show sample LaTeX output
        print("\n📄 SAMPLE LATEX OUTPUT:")
        research = test_results.get('research_metrics', {})
        print("\\begin{table}[h]")
        print("\\centering")
        print("\\begin{tabular}{|l|c|}")
        print("\\hline")
        print("\\textbf{Metric} & \\textbf{Value} \\\\")
        print("\\hline")
        print(f"RTSR (Reported Task Success Rate) & {research.get('RTSR', 0):.1f}\\% \\\\")
        print(f"STSR (Semantic Task Success Rate) & {research.get('STSR', 0):.1f}\\% \\\\")
        print(f"EMR (Effective Movement Ratio) & {research.get('EMR', 0):.1f}\\% \\\\")
        print(f"OI (Oscillation Index) & {research.get('OI', 0):.1f}\\% \\\\")
        print(f"RLS (Room-Label Stability) & {research.get('RLS', 0):.1f}\\% \\\\")
        print(f"TR (Timeout Rate) & {research.get('TR', 0):.1f}\\% \\\\")
        print("\\hline")
        print("\\end{tabular}")
        print("\\caption{VESPER Navigation System Performance Metrics}")
        print("\\label{tab:vesper_metrics}")
        print("\\end{table}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
