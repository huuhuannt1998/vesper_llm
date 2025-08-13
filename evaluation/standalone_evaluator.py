"""
Standalone VESPER LLM Evaluation System
======================================

This evaluation system runs independently from Blender and measures
the correctness of LLM-controlled navigation through various methods.

Usage:
    python standalone_evaluator.py
"""

import json
import time
import random
import requests
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

class VESPERStandaloneEvaluator:
    """Standalone evaluation system that doesn't require Blender"""
    
    def __init__(self):
        self.llm_server = "http://cci-siscluster1.charlotte.edu:8080"
        self.test_results = []
        self.room_configs = {
            "Kitchen": {"center": [2.0, 1.5], "tasks": ["make coffee", "cook meal", "get water"]},
            "LivingRoom": {"center": [-2.0, 1.5], "tasks": ["watch tv", "relax", "read book"]},
            "Bedroom": {"center": [-3.0, -2.0], "tasks": ["go to bed", "get dressed", "sleep"]},
            "Bathroom": {"center": [1.0, -2.0], "tasks": ["brush teeth", "shower", "wash hands"]},
            "Office": {"center": [3.0, 3.0], "tasks": ["work on computer", "make calls", "study"]},
            "DiningRoom": {"center": [0.0, 1.0], "tasks": ["eat dinner", "have breakfast", "family meal"]}
        }
    
    def run_complete_evaluation(self) -> str:
        """Run complete standalone evaluation suite"""
        print("🔬 VESPER Standalone LLM Navigation Evaluation")
        print("=" * 60)
        print("This evaluation runs independently from Blender\n")
        
        # Method 1: LLM Room Selection Accuracy
        print("📍 Method 1: Testing LLM Room Selection Accuracy...")
        room_accuracy = self.evaluate_llm_room_selection()
        
        # Method 2: Task-Room Mapping Correctness
        print("\n🎯 Method 2: Testing Task-Room Mapping Logic...")
        mapping_accuracy = self.evaluate_task_room_mapping()
        
        # Method 3: Navigation Path Planning
        print("\n🗺️ Method 3: Testing Navigation Path Planning...")
        path_quality = self.evaluate_path_planning()
        
        # Method 4: Multi-step Task Planning
        print("\n📋 Method 4: Testing Multi-step Task Planning...")
        planning_accuracy = self.evaluate_multi_step_planning()
        
        # Method 5: Error Handling and Edge Cases
        print("\n⚠️ Method 5: Testing Error Handling...")
        error_handling = self.evaluate_error_handling()
        
        # Method 6: Response Time and Reliability
        print("\n⏱️ Method 6: Testing Response Time and Reliability...")
        reliability_metrics = self.evaluate_llm_reliability()
        
        # Compile comprehensive results
        evaluation_results = self.compile_evaluation_results(
            room_accuracy, mapping_accuracy, path_quality,
            planning_accuracy, error_handling, reliability_metrics
        )
        
        # Generate research report
        report_path = self.generate_research_report(evaluation_results)
        
        return report_path
    
    def evaluate_llm_room_selection(self) -> Dict:
        """Method 1: Evaluate how accurately LLM selects appropriate rooms"""
        print("  Testing LLM room selection with various task descriptions...")
        
        test_cases = [
            {"task": "I need to make coffee for breakfast", "expected": "Kitchen", "category": "clear"},
            {"task": "Time to watch the evening news", "expected": "LivingRoom", "category": "clear"},
            {"task": "I'm tired and want to sleep", "expected": "Bedroom", "category": "clear"},
            {"task": "Need to brush my teeth before bed", "expected": "Bathroom", "category": "clear"},
            {"task": "Have to finish my work presentation", "expected": "Office", "category": "clear"},
            
            # Ambiguous cases
            {"task": "I want to relax and read", "expected": ["LivingRoom", "Bedroom"], "category": "ambiguous"},
            {"task": "Need to get ready", "expected": ["Bathroom", "Bedroom"], "category": "ambiguous"},
            {"task": "Time for a snack", "expected": ["Kitchen", "DiningRoom"], "category": "ambiguous"},
            
            # Complex cases
            {"task": "Prepare for dinner with guests", "expected": "Kitchen", "category": "complex"},
            {"task": "Clean up after the party", "expected": ["LivingRoom", "Kitchen"], "category": "complex"},
        ]
        
        correct_predictions = 0
        total_tests = len(test_cases)
        category_results = {"clear": [], "ambiguous": [], "complex": []}
        
        for i, test in enumerate(test_cases):
            print(f"    Test {i+1}: '{test['task']}'")
            
            # Query LLM for room selection
            predicted_room = self.query_llm_for_room(test["task"])
            
            # Check correctness
            expected = test["expected"]
            if isinstance(expected, list):
                is_correct = predicted_room in expected
            else:
                is_correct = predicted_room == expected
            
            if is_correct:
                correct_predictions += 1
                print(f"      ✅ Predicted: {predicted_room} (Correct)")
            else:
                print(f"      ❌ Predicted: {predicted_room}, Expected: {expected}")
            
            # Store result by category
            category_results[test["category"]].append(is_correct)
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        # Calculate category-specific accuracy
        category_accuracy = {}
        for category, results in category_results.items():
            if results:
                category_accuracy[category] = sum(results) / len(results)
            else:
                category_accuracy[category] = 0
        
        overall_accuracy = correct_predictions / total_tests
        
        print(f"  📊 Overall Room Selection Accuracy: {overall_accuracy:.1%}")
        print(f"      Clear tasks: {category_accuracy['clear']:.1%}")
        print(f"      Ambiguous tasks: {category_accuracy['ambiguous']:.1%}")
        print(f"      Complex tasks: {category_accuracy['complex']:.1%}")
        
        return {
            "overall_accuracy": overall_accuracy,
            "category_accuracy": category_accuracy,
            "total_tests": total_tests,
            "correct_predictions": correct_predictions
        }
    
    def evaluate_task_room_mapping(self) -> Dict:
        """Method 2: Evaluate task-to-room mapping logic"""
        print("  Testing systematic task-room associations...")
        
        # Test each room's associated tasks
        mapping_results = {}
        total_correct = 0
        total_tests = 0
        
        for room, config in self.room_configs.items():
            print(f"    Testing {room} tasks...")
            room_correct = 0
            
            for task in config["tasks"]:
                predicted_room = self.query_llm_for_room(f"I need to {task}")
                is_correct = predicted_room == room
                
                if is_correct:
                    room_correct += 1
                    total_correct += 1
                    print(f"      ✅ '{task}' → {predicted_room}")
                else:
                    print(f"      ❌ '{task}' → {predicted_room} (expected {room})")
                
                total_tests += 1
                time.sleep(0.1)
            
            room_accuracy = room_correct / len(config["tasks"])
            mapping_results[room] = {
                "accuracy": room_accuracy,
                "correct": room_correct,
                "total": len(config["tasks"])
            }
        
        overall_mapping_accuracy = total_correct / total_tests
        
        print(f"  📊 Task-Room Mapping Accuracy: {overall_mapping_accuracy:.1%}")
        for room, result in mapping_results.items():
            print(f"      {room}: {result['accuracy']:.1%}")
        
        return {
            "overall_accuracy": overall_mapping_accuracy,
            "room_specific": mapping_results,
            "total_correct": total_correct,
            "total_tests": total_tests
        }
    
    def evaluate_path_planning(self) -> Dict:
        """Method 3: Evaluate navigation path planning quality"""
        print("  Testing LLM path planning and spatial reasoning...")
        
        # Test scenarios with different room combinations
        path_tests = [
            {
                "start": "Bedroom",
                "end": "Kitchen", 
                "task": "Morning coffee routine",
                "optimal_path": ["Bedroom", "Kitchen"],
                "distance": 5.1  # Approximate distance
            },
            {
                "start": "Office",
                "end": "LivingRoom",
                "task": "Take a break from work",
                "optimal_path": ["Office", "LivingRoom"], 
                "distance": 5.4
            },
            {
                "start": "Kitchen",
                "end": "Bathroom",
                "task": "Wash hands after cooking",
                "optimal_path": ["Kitchen", "Bathroom"],
                "distance": 2.3
            }
        ]
        
        path_quality_scores = []
        
        for test in path_tests:
            print(f"    Testing path: {test['start']} → {test['end']}")
            
            # Query LLM for navigation strategy
            path_plan = self.query_llm_for_path_planning(test)
            
            # Evaluate path quality
            quality_score = self.calculate_path_quality(path_plan, test)
            path_quality_scores.append(quality_score)
            
            print(f"      Path quality score: {quality_score:.2f}")
            time.sleep(0.1)
        
        average_quality = sum(path_quality_scores) / len(path_quality_scores)
        
        print(f"  📊 Average Path Planning Quality: {average_quality:.2f}/1.0")
        
        return {
            "average_quality": average_quality,
            "individual_scores": path_quality_scores,
            "total_tests": len(path_tests)
        }
    
    def evaluate_multi_step_planning(self) -> Dict:
        """Method 4: Evaluate multi-step task planning"""
        print("  Testing complex multi-step task planning...")
        
        multi_step_tasks = [
            {
                "task": "Complete morning routine",
                "expected_sequence": ["Bedroom", "Bathroom", "Kitchen"],
                "description": "Wake up, brush teeth, make coffee"
            },
            {
                "task": "Prepare for dinner guests", 
                "expected_sequence": ["Kitchen", "DiningRoom", "LivingRoom"],
                "description": "Cook meal, set table, prepare living area"
            },
            {
                "task": "End of work day routine",
                "expected_sequence": ["Office", "LivingRoom", "Bedroom"],
                "description": "Finish work, relax, go to bed"
            }
        ]
        
        planning_scores = []
        
        for task in multi_step_tasks:
            print(f"    Testing: {task['task']}")
            
            # Query LLM for task sequence
            planned_sequence = self.query_llm_for_task_sequence(task)
            
            # Calculate sequence similarity
            sequence_score = self.calculate_sequence_similarity(
                planned_sequence, task["expected_sequence"]
            )
            planning_scores.append(sequence_score)
            
            print(f"      Planned: {planned_sequence}")
            print(f"      Expected: {task['expected_sequence']}")
            print(f"      Similarity score: {sequence_score:.2f}")
            time.sleep(0.2)
        
        average_planning_score = sum(planning_scores) / len(planning_scores)
        
        print(f"  📊 Multi-step Planning Accuracy: {average_planning_score:.2f}/1.0")
        
        return {
            "average_accuracy": average_planning_score,
            "individual_scores": planning_scores,
            "total_tests": len(multi_step_tasks)
        }
    
    def evaluate_error_handling(self) -> Dict:
        """Method 5: Evaluate error handling and edge cases"""
        print("  Testing error handling and edge cases...")
        
        error_test_cases = [
            {"task": "Go to the garage", "type": "nonexistent_room"},
            {"task": "Teleport to Mars", "type": "impossible_task"},
            {"task": "asdf jkl qwerty", "type": "nonsense_input"},
            {"task": "", "type": "empty_input"},
            {"task": "Do something", "type": "vague_task"}
        ]
        
        error_handling_results = []
        
        for test in error_test_cases:
            print(f"    Testing {test['type']}: '{test['task']}'")
            
            try:
                response = self.query_llm_for_room(test["task"])
                
                # Check if LLM handled error appropriately
                handles_error_well = self.evaluate_error_response(response, test["type"])
                error_handling_results.append(handles_error_well)
                
                if handles_error_well:
                    print(f"      ✅ Good error handling: {response}")
                else:
                    print(f"      ❌ Poor error handling: {response}")
                    
            except Exception as e:
                print(f"      ⚠️ Exception occurred: {e}")
                error_handling_results.append(False)
            
            time.sleep(0.1)
        
        error_handling_score = sum(error_handling_results) / len(error_handling_results)
        
        print(f"  📊 Error Handling Score: {error_handling_score:.1%}")
        
        return {
            "error_handling_score": error_handling_score,
            "total_tests": len(error_test_cases),
            "successful_handling": sum(error_handling_results)
        }
    
    def evaluate_llm_reliability(self) -> Dict:
        """Method 6: Evaluate LLM response time and reliability"""
        print("  Testing LLM response time and reliability...")
        
        # Test the same query multiple times to check consistency
        test_query = "I need to make coffee"
        expected_response = "Kitchen"
        
        response_times = []
        consistency_results = []
        
        print(f"    Running consistency test with: '{test_query}'")
        
        for i in range(10):  # Test 10 times
            start_time = time.time()
            
            try:
                response = self.query_llm_for_room(test_query)
                response_time = time.time() - start_time
                
                response_times.append(response_time)
                is_consistent = response == expected_response
                consistency_results.append(is_consistent)
                
                status = "✅" if is_consistent else "❌"
                print(f"      Test {i+1}: {response} ({response_time:.2f}s) {status}")
                
            except Exception as e:
                response_times.append(10.0)  # Penalty for failure
                consistency_results.append(False)
                print(f"      Test {i+1}: Error - {e}")
            
            time.sleep(0.1)
        
        avg_response_time = sum(response_times) / len(response_times)
        consistency_rate = sum(consistency_results) / len(consistency_results)
        
        print(f"  📊 Average Response Time: {avg_response_time:.2f} seconds")
        print(f"  📊 Consistency Rate: {consistency_rate:.1%}")
        
        return {
            "average_response_time": avg_response_time,
            "consistency_rate": consistency_rate,
            "response_times": response_times,
            "total_tests": len(consistency_results)
        }
    
    def query_llm_for_room(self, task: str) -> str:
        """Query the LLM server for room selection"""
        try:
            system_prompt = "You are a smart house navigation assistant. Given a task, return ONLY the room name where the task should be performed. Available rooms: Kitchen, LivingRoom, Bedroom, Bathroom, Office, DiningRoom"
            
            payload = {
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Task: {task}"}
                ],
                "max_tokens": 20,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.llm_server}/v1/chat/completions",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                room = result["choices"][0]["message"]["content"].strip()
                
                # Clean up response to extract room name
                room_names = ["Kitchen", "LivingRoom", "Bedroom", "Bathroom", "Office", "DiningRoom"]
                for room_name in room_names:
                    if room_name.lower() in room.lower():
                        return room_name
                
                return room  # Return as-is if no match
            else:
                print(f"      ⚠️ LLM request failed: {response.status_code}")
                return "Unknown"
                
        except Exception as e:
            print(f"      ⚠️ LLM query error: {e}")
            return "Error"
    
    def query_llm_for_path_planning(self, path_test: Dict) -> str:
        """Query LLM for path planning strategy"""
        try:
            prompt = f"Plan navigation from {path_test['start']} to {path_test['end']} for: {path_test['task']}"
            
            payload = {
                "model": "openai/gpt-oss-20b", 
                "messages": [
                    {"role": "system", "content": "You are a navigation planner. Describe the optimal path."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.llm_server}/v1/chat/completions",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "Failed to plan path"
                
        except Exception as e:
            return f"Error: {e}"
    
    def query_llm_for_task_sequence(self, task: Dict) -> List[str]:
        """Query LLM for multi-step task sequence"""
        try:
            prompt = f"Plan the room sequence for: {task['description']}. List rooms in order."
            
            payload = {
                "model": "openai/gpt-oss-20b",
                "messages": [
                    {"role": "system", "content": "Return a JSON list of room names in order."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 50,
                "temperature": 0.1
            }
            
            response = requests.post(
                f"{self.llm_server}/v1/chat/completions",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Try to extract room names from response
                room_names = ["Kitchen", "LivingRoom", "Bedroom", "Bathroom", "Office", "DiningRoom"]
                found_rooms = []
                
                for room in room_names:
                    if room.lower() in content.lower():
                        found_rooms.append(room)
                
                return found_rooms[:3]  # Limit to 3 rooms
            else:
                return []
                
        except Exception as e:
            print(f"Error querying task sequence: {e}")
            return []
    
    def calculate_path_quality(self, path_plan: str, test: Dict) -> float:
        """Calculate quality score for path planning"""
        # Simple scoring based on whether plan mentions correct rooms
        start_room = test["start"]
        end_room = test["end"]
        
        score = 0.0
        
        if start_room.lower() in path_plan.lower():
            score += 0.3
        if end_room.lower() in path_plan.lower():
            score += 0.3
        if "direct" in path_plan.lower() or "straight" in path_plan.lower():
            score += 0.2
        if len(path_plan) > 10:  # Has some planning detail
            score += 0.2
        
        return min(score, 1.0)
    
    def calculate_sequence_similarity(self, predicted: List[str], expected: List[str]) -> float:
        """Calculate similarity between predicted and expected sequences"""
        if not predicted or not expected:
            return 0.0
        
        # Calculate overlap and order similarity
        overlap = len(set(predicted) & set(expected))
        max_length = max(len(predicted), len(expected))
        
        overlap_score = overlap / len(expected) if expected else 0
        
        # Bonus for correct order
        order_score = 0.0
        for i, room in enumerate(predicted[:len(expected)]):
            if i < len(expected) and room == expected[i]:
                order_score += 1.0 / len(expected)
        
        return (overlap_score + order_score) / 2
    
    def evaluate_error_response(self, response: str, error_type: str) -> bool:
        """Evaluate if error response is appropriate"""
        response_lower = response.lower()
        
        if error_type == "nonexistent_room":
            return "unknown" in response_lower or "not found" in response_lower or "kitchen" in response_lower  # Fallback to kitchen
        elif error_type == "impossible_task":
            return "cannot" in response_lower or "impossible" in response_lower or "unknown" in response_lower
        elif error_type == "nonsense_input":
            return "unknown" in response_lower or "unclear" in response_lower
        elif error_type == "empty_input":
            return "unknown" in response_lower or "empty" in response_lower
        elif error_type == "vague_task":
            return len(response) > 0  # Any response is better than none
        
        return False
    
    def compile_evaluation_results(self, *method_results) -> Dict:
        """Compile results from all evaluation methods"""
        room_acc, mapping_acc, path_qual, planning_acc, error_hand, reliability = method_results
        
        # Calculate overall scores
        overall_accuracy = (
            room_acc["overall_accuracy"] * 0.25 +
            mapping_acc["overall_accuracy"] * 0.25 +
            path_qual["average_quality"] * 0.2 +
            planning_acc["average_accuracy"] * 0.15 +
            error_hand["error_handling_score"] * 0.1 +
            reliability["consistency_rate"] * 0.05
        )
        
        return {
            "overall_llm_performance": overall_accuracy,
            "method_1_room_selection": room_acc,
            "method_2_task_mapping": mapping_acc,
            "method_3_path_planning": path_qual,
            "method_4_multi_step_planning": planning_acc,
            "method_5_error_handling": error_hand,
            "method_6_reliability": reliability,
            "evaluation_summary": {
                "total_tests": (room_acc["total_tests"] + mapping_acc["total_tests"] + 
                              path_qual["total_tests"] + planning_acc["total_tests"] +
                              error_hand["total_tests"] + reliability["total_tests"]),
                "average_response_time": reliability["average_response_time"],
                "overall_accuracy": overall_accuracy
            }
        }
    
    def generate_research_report(self, results: Dict) -> str:
        """Generate comprehensive research report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"vesper_standalone_evaluation_{timestamp}.json"
        
        # Add metadata
        research_report = {
            "metadata": {
                "evaluation_type": "Standalone LLM Navigation Evaluation",
                "evaluation_date": datetime.now().isoformat(),
                "vesper_version": "2.3.0",
                "llm_server": self.llm_server,
                "evaluation_methods": 6
            },
            "results": results,
            "research_metrics": {
                "llm_room_selection_accuracy": results["method_1_room_selection"]["overall_accuracy"],
                "task_mapping_accuracy": results["method_2_task_mapping"]["overall_accuracy"],
                "path_planning_quality": results["method_3_path_planning"]["average_quality"],
                "multi_step_planning_accuracy": results["method_4_multi_step_planning"]["average_accuracy"],
                "error_handling_score": results["method_5_error_handling"]["error_handling_score"],
                "response_consistency": results["method_6_reliability"]["consistency_rate"],
                "average_response_time": results["method_6_reliability"]["average_response_time"],
                "overall_performance_score": results["overall_llm_performance"]
            },
            "research_conclusions": {
                "key_findings": [
                    f"LLM room selection accuracy: {results['method_1_room_selection']['overall_accuracy']:.1%}",
                    f"Task-room mapping accuracy: {results['method_2_task_mapping']['overall_accuracy']:.1%}",
                    f"Path planning quality: {results['method_3_path_planning']['average_quality']:.1%}",
                    f"Multi-step planning: {results['method_4_multi_step_planning']['average_accuracy']:.1%}",
                    f"Error handling capability: {results['method_5_error_handling']['error_handling_score']:.1%}",
                    f"Response consistency: {results['method_6_reliability']['consistency_rate']:.1%}"
                ],
                "overall_assessment": f"LLM navigation correctness: {results['overall_llm_performance']:.1%}",
                "recommendation": "Suitable for autonomous navigation tasks" if results['overall_llm_performance'] > 0.8 else "Requires improvement for reliable navigation"
            }
        }
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(research_report, f, indent=2)
        
        # Print summary
        print(f"\n📊 EVALUATION COMPLETE!")
        print("=" * 60)
        print(f"🎯 Overall LLM Performance: {results['overall_llm_performance']:.1%}")
        print(f"📍 Room Selection Accuracy: {results['method_1_room_selection']['overall_accuracy']:.1%}")
        print(f"🗺️ Task Mapping Accuracy: {results['method_2_task_mapping']['overall_accuracy']:.1%}")
        print(f"🧠 Multi-step Planning: {results['method_4_multi_step_planning']['average_accuracy']:.1%}")
        print(f"⚠️ Error Handling: {results['method_5_error_handling']['error_handling_score']:.1%}")
        print(f"⏱️ Avg Response Time: {results['method_6_reliability']['average_response_time']:.2f}s")
        print(f"\n📁 Full report saved: {report_path}")
        
        return report_path

def main():
    """Main evaluation function"""
    print("🚀 Starting VESPER Standalone LLM Evaluation")
    print("This evaluation runs independently from Blender\n")
    
    # Create evaluator
    evaluator = VESPERStandaloneEvaluator()
    
    # Run complete evaluation
    report_path = evaluator.run_complete_evaluation()
    
    print(f"\n🎉 STANDALONE EVALUATION COMPLETE!")
    print("📊 This provides comprehensive LLM correctness metrics")
    print("📈 Use these results for your research paper evaluation section")
    
    return report_path

if __name__ == "__main__":
    main()
