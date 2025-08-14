"""
VESPER LLM Task Testing Suite
============================

Comprehensive testing script that uses the extensive task dataset
to test LLM navigation correctness with hundreds of different tasks.

Usage:
    python test_with_comprehensive_tasks.py --mode quick
    python test_with_comprehensive_tasks.py --mode full
    python test_with_comprehensive_tasks.py --category morning_routines
"""

import sys
import os
import argparse
import random
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import our comprehensive task dataset
from comprehensive_task_dataset import (
    get_all_tasks, get_tasks_by_category, get_random_tasks, 
    get_routine_by_type, get_challenging_tasks, create_test_suite,
    print_task_statistics, ALL_TASK_CATEGORIES
)

# Import evaluation system
from simple_evaluator import SimpleLLMEvaluator

class ComprehensiveTaskTester:
    """Test VESPER LLM with comprehensive task dataset"""
    
    def __init__(self):
        self.evaluator = SimpleLLMEvaluator()
        self.results_history = []
        
    def test_individual_tasks(self, tasks: List[str], test_name: str = "Individual Tasks") -> Dict:
        """Test individual tasks one by one"""
        print(f"\n🎯 TESTING: {test_name}")
        print(f"📊 Testing {len(tasks)} tasks")
        print("=" * 50)
        
        results = {
            "test_name": test_name,
            "total_tasks": len(tasks),
            "successful_mappings": 0,
            "failed_mappings": 0,
            "task_results": []
        }
        
        for i, task in enumerate(tasks, 1):
            print(f"  Task {i:3d}: '{task}'", end=" → ")
            
            # Test task-to-room mapping
            predicted_room = self.evaluator.simulate_llm_room_selection(task)
            
            # Simple success criteria (not empty/default response)
            is_successful = predicted_room in ["Kitchen", "LivingRoom", "Bedroom", 
                                             "Bathroom", "Office", "DiningRoom"]
            
            if is_successful:
                results["successful_mappings"] += 1
                print(f"✅ {predicted_room}")
            else:
                results["failed_mappings"] += 1
                print(f"❌ {predicted_room}")
            
            results["task_results"].append({
                "task": task,
                "predicted_room": predicted_room,
                "success": is_successful
            })
        
        success_rate = results["successful_mappings"] / results["total_tasks"]
        print(f"\n📊 Results: {results['successful_mappings']}/{results['total_tasks']} "
              f"({success_rate:.1%} success rate)")
        
        return results
    
    def test_routine_sequences(self, routines: List[Dict], test_name: str = "Routine Sequences") -> Dict:
        """Test multi-step routine sequences"""
        print(f"\n📋 TESTING: {test_name}")
        print(f"📊 Testing {len(routines)} routines")
        print("=" * 50)
        
        results = {
            "test_name": test_name,
            "total_routines": len(routines),
            "successful_routines": 0,
            "routine_results": []
        }
        
        for i, routine in enumerate(routines, 1):
            routine_type = routine.get("type", "unknown")
            tasks = routine.get("tasks", [])
            
            print(f"  Routine {i:2d}: {routine_type} ({len(tasks)} tasks)")
            
            # Test each task in the routine
            routine_result = {
                "type": routine_type,
                "tasks": tasks,
                "task_mappings": [],
                "overall_success": True
            }
            
            for j, task in enumerate(tasks):
                predicted_room = self.evaluator.simulate_llm_room_selection(task)
                is_successful = predicted_room in ["Kitchen", "LivingRoom", "Bedroom", 
                                                 "Bathroom", "Office", "DiningRoom"]
                
                routine_result["task_mappings"].append({
                    "task": task,
                    "predicted_room": predicted_room,
                    "success": is_successful
                })
                
                if not is_successful:
                    routine_result["overall_success"] = False
                
                print(f"    {j+1}. '{task}' → {predicted_room} {'✅' if is_successful else '❌'}")
            
            if routine_result["overall_success"]:
                results["successful_routines"] += 1
                print(f"    → ✅ Routine completed successfully")
            else:
                print(f"    → ❌ Routine had failures")
            
            results["routine_results"].append(routine_result)
        
        success_rate = results["successful_routines"] / results["total_routines"]
        print(f"\n📊 Results: {results['successful_routines']}/{results['total_routines']} "
              f"({success_rate:.1%} routine success rate)")
        
        return results
    
    def test_challenging_tasks(self, tasks: List, test_name: str = "Challenging Tasks") -> Dict:
        """Test challenging and ambiguous tasks"""
        print(f"\n⚠️ TESTING: {test_name}")
        print(f"📊 Testing {len(tasks)} challenging tasks")
        print("=" * 50)
        
        results = {
            "test_name": test_name,
            "total_tasks": len(tasks),
            "appropriate_responses": 0,
            "inappropriate_responses": 0,
            "task_results": []
        }
        
        for i, task in enumerate(tasks, 1):
            if isinstance(task, tuple):  # Contextual tasks
                context, actual_task = task
                print(f"  Task {i:3d}: Context: '{context}' → '{actual_task}'")
                # Test with context
                test_input = f"{context} {actual_task}"
            else:
                print(f"  Task {i:3d}: '{task}'", end=" → ")
                test_input = task
            
            # For error-inducing tasks, test error handling
            if task in get_tasks_by_category("error_inducing_tasks"):
                error_response = self.evaluator.simulate_error_handling({
                    "input": task,
                    "type": "challenging",
                    "expected_behavior": "appropriate_handling"
                })
                
                # Check if error was handled appropriately
                appropriate = any(keyword in error_response.lower() for keyword in 
                                ["don't", "cannot", "unclear", "specify", "help"])
                
                if appropriate:
                    results["appropriate_responses"] += 1
                    print(f"✅ Good error handling: '{error_response[:50]}...'")
                else:
                    results["inappropriate_responses"] += 1
                    print(f"❌ Poor error handling: '{error_response[:50]}...'")
                
                results["task_results"].append({
                    "task": task,
                    "response": error_response,
                    "appropriate": appropriate
                })
            else:
                # Regular challenging task
                predicted_room = self.evaluator.simulate_llm_room_selection(test_input)
                
                # For ambiguous tasks, any reasonable room is acceptable
                is_reasonable = predicted_room in ["Kitchen", "LivingRoom", "Bedroom", 
                                                 "Bathroom", "Office", "DiningRoom"]
                
                if is_reasonable:
                    results["appropriate_responses"] += 1
                    print(f"✅ {predicted_room}")
                else:
                    results["inappropriate_responses"] += 1
                    print(f"❌ {predicted_room}")
                
                results["task_results"].append({
                    "task": task,
                    "predicted_room": predicted_room,
                    "appropriate": is_reasonable
                })
        
        success_rate = results["appropriate_responses"] / results["total_tasks"]
        print(f"\n📊 Results: {results['appropriate_responses']}/{results['total_tasks']} "
              f"({success_rate:.1%} appropriate response rate)")
        
        return results
    
    def run_comprehensive_test(self, test_size: str = "medium") -> Dict:
        """Run comprehensive test with all task types"""
        print(f"🔬 VESPER LLM COMPREHENSIVE TASK TESTING")
        print(f"📊 Test Size: {test_size.upper()}")
        print("=" * 60)
        
        # Create test suite
        test_suite = create_test_suite(test_size)
        
        all_results = {
            "test_metadata": {
                "test_size": test_size,
                "start_time": datetime.now().isoformat(),
                "total_tasks": (len(test_suite["basic_tasks"]) + 
                              sum(len(r["tasks"]) for r in test_suite["routine_tasks"]) +
                              len(test_suite["challenging_tasks"]))
            },
            "results": []
        }
        
        # Test 1: Basic Individual Tasks
        basic_results = self.test_individual_tasks(
            test_suite["basic_tasks"], 
            f"Basic Individual Tasks ({len(test_suite['basic_tasks'])} tasks)"
        )
        all_results["results"].append(basic_results)
        
        # Test 2: Routine Sequences
        routine_results = self.test_routine_sequences(
            test_suite["routine_tasks"],
            f"Routine Sequences ({len(test_suite['routine_tasks'])} routines)"
        )
        all_results["results"].append(routine_results)
        
        # Test 3: Challenging Tasks
        challenging_results = self.test_challenging_tasks(
            test_suite["challenging_tasks"],
            f"Challenging Tasks ({len(test_suite['challenging_tasks'])} tasks)"
        )
        all_results["results"].append(challenging_results)
        
        # Calculate overall statistics
        total_tests = 0
        total_successes = 0
        
        for result in all_results["results"]:
            if "successful_mappings" in result:
                total_tests += result["total_tasks"]
                total_successes += result["successful_mappings"]
            elif "successful_routines" in result:
                total_tests += result["total_routines"]
                total_successes += result["successful_routines"]
            elif "appropriate_responses" in result:
                total_tests += result["total_tasks"]
                total_successes += result["appropriate_responses"]
        
        overall_success_rate = total_successes / total_tests if total_tests > 0 else 0
        
        all_results["overall_statistics"] = {
            "total_tests": total_tests,
            "total_successes": total_successes,
            "overall_success_rate": overall_success_rate,
            "end_time": datetime.now().isoformat()
        }
        
        # Print comprehensive summary
        print(f"\n🎊 COMPREHENSIVE TEST COMPLETE!")
        print("=" * 60)
        print(f"📊 Overall Results: {total_successes}/{total_tests} "
              f"({overall_success_rate:.1%} success rate)")
        print(f"⏱️ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"comprehensive_test_results_{test_size}_{timestamp}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"📄 Detailed results saved: {results_file}")
        
        return all_results
    
    def test_specific_category(self, category: str) -> Dict:
        """Test tasks from a specific category"""
        print(f"🎯 TESTING SPECIFIC CATEGORY: {category}")
        print("=" * 50)
        
        tasks = get_tasks_by_category(category)
        if not tasks:
            print(f"❌ Category '{category}' not found or empty")
            return {}
        
        if "routines" in category:
            # Convert routine lists to routine dicts
            routine_dicts = [{"type": category, "tasks": routine} for routine in tasks]
            return self.test_routine_sequences(routine_dicts, f"{category} Testing")
        else:
            return self.test_individual_tasks(tasks, f"{category} Testing")
    
    def quick_test(self) -> Dict:
        """Run a quick test with a small sample"""
        print(f"⚡ VESPER LLM QUICK TASK TEST")
        print("=" * 40)
        
        # Quick sample from different categories
        quick_tasks = []
        quick_tasks.extend(get_random_tasks(10, "basic_kitchen"))
        quick_tasks.extend(get_random_tasks(10, "basic_living_room"))
        quick_tasks.extend(get_random_tasks(5, "ambiguous_tasks"))
        
        return self.test_individual_tasks(quick_tasks, "Quick Test Sample")

def main():
    """Main testing function with command line arguments"""
    parser = argparse.ArgumentParser(description="VESPER LLM Comprehensive Task Testing")
    parser.add_argument("--mode", choices=["quick", "small", "medium", "large", "comprehensive"], 
                       default="medium", help="Test mode/size")
    parser.add_argument("--category", help="Test specific category only")
    parser.add_argument("--stats", action="store_true", help="Show task dataset statistics")
    
    args = parser.parse_args()
    
    tester = ComprehensiveTaskTester()
    
    if args.stats:
        print_task_statistics()
        return
    
    if args.category:
        result = tester.test_specific_category(args.category)
    elif args.mode == "quick":
        result = tester.quick_test()
    else:
        result = tester.run_comprehensive_test(args.mode)
    
    return result

if __name__ == "__main__":
    main()
