#!/usr/bin/env python3
"""
VESPER ADL System - BGE Integration Test

Test script for VESPER ADL enhancement integrated with existing BGE navigation.
This extends your existing BGE testing framework with comprehensive ADL testing.

Usage:
1. Run from within Blender Game Engine
2. Can be called from existing navigation test scripts
3. Integrates with existing evaluation framework
"""

import bge
import time
import json
import os
from typing import Dict, List, Any

# Import VESPER ADL integration
from vesper_adl_blender_integration import (
    initialize_vesper_adl_integration,
    execute_adl_cooking_task,
    execute_adl_medication_task,
    execute_adl_communication_task,
    get_vesper_adl_status
)

class VESPERADLBGETest:
    """
    Test harness for VESPER ADL system within existing BGE navigation framework.
    Extends existing testing with ADL task evaluation.
    """
    
    def __init__(self):
        self.test_results = []
        self.integration_ready = False
        self.start_time = time.time()
        
    def run_full_adl_test_suite(self) -> Dict[str, Any]:
        """
        Run comprehensive VESPER ADL test suite.
        Integrates with existing BGE navigation testing.
        """
        
        print("🧪 Starting VESPER ADL BGE Test Suite...")
        print("=" * 60)
        
        # Test 1: Integration initialization
        init_result = self.test_integration_initialization()
        
        if not init_result["success"]:
            return {
                "success": False,
                "error": "Integration initialization failed",
                "results": self.test_results
            }
        
        # Test 2: Basic ADL task execution
        basic_adl_result = self.test_basic_adl_execution()
        
        # Test 3: Navigation-integrated ADL tasks
        navigation_adl_result = self.test_navigation_integrated_adl()
        
        # Test 4: CASAS compatibility testing
        casas_result = self.test_casas_compatibility()
        
        # Test 5: Performance and stability
        performance_result = self.test_performance_stability()
        
        # Generate comprehensive report
        final_report = self.generate_test_report()
        
        print("🎉 VESPER ADL BGE Test Suite Complete!")
        return final_report
    
    def test_integration_initialization(self) -> Dict[str, Any]:
        """Test VESPER ADL integration with existing BGE system"""
        
        print("\n🔧 Test 1: Integration Initialization")
        print("-" * 40)
        
        test_result = {
            "test_name": "integration_initialization",
            "start_time": time.time(),
            "success": False,
            "details": {}
        }
        
        try:
            # Initialize VESPER ADL integration
            init_success = initialize_vesper_adl_integration()
            
            if init_success:
                # Verify integration components
                has_vesper_system = hasattr(bge.logic, 'vesper_adl_system')
                has_execute_function = hasattr(bge.logic, 'execute_adl_task')
                has_ready_flag = hasattr(bge.logic, 'vesper_adl_ready')
                
                test_result["details"] = {
                    "initialization_success": init_success,
                    "vesper_system_available": has_vesper_system,
                    "execute_function_available": has_execute_function,
                    "ready_flag_set": has_ready_flag,
                    "integration_status": "active" if all([has_vesper_system, has_execute_function, has_ready_flag]) else "partial"
                }
                
                if all([has_vesper_system, has_execute_function, has_ready_flag]):
                    test_result["success"] = True
                    self.integration_ready = True
                    print("✅ Integration initialization successful")
                else:
                    print("⚠️  Partial integration - some components missing")
            else:
                test_result["details"]["error"] = "Initialization returned False"
                print("❌ Integration initialization failed")
                
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"❌ Integration initialization error: {e}")
        
        test_result["duration"] = time.time() - test_result["start_time"]
        self.test_results.append(test_result)
        return test_result
    
    def test_basic_adl_execution(self) -> Dict[str, Any]:
        """Test basic ADL task execution capabilities"""
        
        print("\n🎯 Test 2: Basic ADL Task Execution")
        print("-" * 40)
        
        test_result = {
            "test_name": "basic_adl_execution",
            "start_time": time.time(),
            "success": False,
            "details": {
                "tasks_tested": [],
                "tasks_successful": 0,
                "tasks_failed": 0
            }
        }
        
        if not self.integration_ready:
            test_result["details"]["error"] = "Integration not ready"
            self.test_results.append(test_result)
            return test_result
        
        # Test each ADL task type
        adl_tasks = [
            ("cooking", execute_adl_cooking_task),
            ("medication", execute_adl_medication_task),
            ("communication", execute_adl_communication_task)
        ]
        
        for task_name, task_function in adl_tasks:
            print(f"  Testing {task_name} task...")
            
            try:
                task_result = task_function()
                
                task_info = {
                    "task_name": task_name,
                    "success": task_result.get("success", False) if task_result else False,
                    "duration": task_result.get("duration", 0) if task_result else 0,
                    "steps_completed": task_result.get("steps_completed", 0) if task_result else 0
                }
                
                test_result["details"]["tasks_tested"].append(task_info)
                
                if task_info["success"]:
                    test_result["details"]["tasks_successful"] += 1
                    print(f"    ✅ {task_name} task successful")
                else:
                    test_result["details"]["tasks_failed"] += 1
                    print(f"    ❌ {task_name} task failed")
                    
            except Exception as e:
                test_result["details"]["tasks_tested"].append({
                    "task_name": task_name,
                    "success": False,
                    "error": str(e)
                })
                test_result["details"]["tasks_failed"] += 1
                print(f"    ❌ {task_name} task error: {e}")
        
        # Determine overall success
        if test_result["details"]["tasks_successful"] > 0:
            test_result["success"] = True
            print(f"✅ Basic ADL execution: {test_result['details']['tasks_successful']}/{len(adl_tasks)} tasks successful")
        else:
            print("❌ No ADL tasks executed successfully")
        
        test_result["duration"] = time.time() - test_result["start_time"]
        self.test_results.append(test_result)
        return test_result
    
    def test_navigation_integrated_adl(self) -> Dict[str, Any]:
        """Test ADL tasks integrated with existing navigation system"""
        
        print("\n🗺️  Test 3: Navigation-Integrated ADL")
        print("-" * 40)
        
        test_result = {
            "test_name": "navigation_integrated_adl",
            "start_time": time.time(),
            "success": False,
            "details": {}
        }
        
        if not self.integration_ready:
            test_result["details"]["error"] = "Integration not ready"
            self.test_results.append(test_result)
            return test_result
        
        try:
            # Check navigation integration components
            scene = bge.logic.getCurrentScene()
            has_actor = 'Actor' in scene.objects
            has_scene_objects = hasattr(bge.logic, 'vesper_scene_objects')
            has_screenshot_system = hasattr(bge.logic, 'vesper_latest_screenshot') or hasattr(bge.logic, 'latest_screenshot')
            
            test_result["details"] = {
                "actor_available": has_actor,
                "scene_objects_detected": len(bge.logic.vesper_scene_objects) if has_scene_objects else 0,
                "screenshot_system_active": has_screenshot_system,
                "navigation_integration": has_actor and has_scene_objects
            }
            
            if has_actor and has_scene_objects:
                # Get current actor position
                actor = scene.objects['Actor']
                actor_position = tuple(actor.worldPosition)
                
                test_result["details"]["actor_position"] = actor_position
                test_result["details"]["scene_objects_list"] = list(bge.logic.vesper_scene_objects.keys()) if has_scene_objects else []
                
                # Test navigation-aware ADL task
                if hasattr(bge.logic, 'execute_adl_task'):
                    navigation_task_result = bge.logic.execute_adl_task("Navigate to kitchen and prepare simple meal")
                    
                    test_result["details"]["navigation_task"] = {
                        "attempted": True,
                        "success": navigation_task_result.get("success", False) if navigation_task_result else False,
                        "navigation_integration_used": navigation_task_result.get("navigation_integration", {}) if navigation_task_result else {}
                    }
                    
                    if test_result["details"]["navigation_task"]["success"]:
                        test_result["success"] = True
                        print("✅ Navigation-integrated ADL task successful")
                    else:
                        print("⚠️  Navigation-integrated ADL task failed")
                else:
                    test_result["details"]["error"] = "execute_adl_task function not available"
            else:
                print("⚠️  Navigation integration components missing")
                
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"❌ Navigation integration test error: {e}")
        
        test_result["duration"] = time.time() - test_result["start_time"]
        self.test_results.append(test_result)
        return test_result
    
    def test_casas_compatibility(self) -> Dict[str, Any]:
        """Test CASAS dataset compatibility"""
        
        print("\n📊 Test 4: CASAS Compatibility")
        print("-" * 40)
        
        test_result = {
            "test_name": "casas_compatibility",
            "start_time": time.time(),
            "success": False,
            "details": {}
        }
        
        try:
            # Get VESPER ADL system status
            status_report = get_vesper_adl_status()
            
            if status_report.get("status") != "not_initialized":
                test_result["details"] = {
                    "system_status": status_report.get("status", "unknown"),
                    "casas_objects_managed": status_report.get("object_manager", {}).get("objects_managed", 0),
                    "casas_tasks_available": status_report.get("task_executor", {}).get("tasks_available", 0),
                    "vlm_processor_active": status_report.get("vlm_processor", {}).get("status", "unknown"),
                    "casas_compatibility_score": status_report.get("performance_metrics", {}).get("casas_compatibility", 0.0)
                }
                
                # Check for CASAS compatibility indicators
                casas_score = test_result["details"]["casas_compatibility_score"]
                objects_managed = test_result["details"]["casas_objects_managed"]
                tasks_available = test_result["details"]["casas_tasks_available"]
                
                if casas_score > 0.5 or (objects_managed >= 5 and tasks_available >= 3):
                    test_result["success"] = True
                    print(f"✅ CASAS compatibility: {casas_score:.1%} score, {objects_managed} objects, {tasks_available} tasks")
                else:
                    print(f"⚠️  Limited CASAS compatibility: {casas_score:.1%} score")
            else:
                test_result["details"]["error"] = "VESPER system not initialized"
                print("❌ Cannot test CASAS compatibility - system not initialized")
                
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"❌ CASAS compatibility test error: {e}")
        
        test_result["duration"] = time.time() - test_result["start_time"]
        self.test_results.append(test_result)
        return test_result
    
    def test_performance_stability(self) -> Dict[str, Any]:
        """Test performance and stability under load"""
        
        print("\n⚡ Test 5: Performance & Stability")
        print("-" * 40)
        
        test_result = {
            "test_name": "performance_stability",
            "start_time": time.time(),
            "success": False,
            "details": {
                "multiple_tasks_completed": 0,
                "average_task_duration": 0.0,
                "memory_stable": True,
                "errors_encountered": 0
            }
        }
        
        if not self.integration_ready:
            test_result["details"]["error"] = "Integration not ready"
            self.test_results.append(test_result)
            return test_result
        
        try:
            # Run multiple ADL tasks in sequence
            task_durations = []
            
            for i in range(3):  # Run 3 tasks for stability testing
                print(f"  Running stability test {i+1}/3...")
                
                task_start = time.time()
                task_result = execute_adl_cooking_task()  # Use cooking task for stability test
                task_duration = time.time() - task_start
                
                task_durations.append(task_duration)
                
                if task_result and task_result.get("success", False):
                    test_result["details"]["multiple_tasks_completed"] += 1
                else:
                    test_result["details"]["errors_encountered"] += 1
                
                # Brief pause between tasks
                time.sleep(0.1)
            
            # Calculate performance metrics
            if task_durations:
                test_result["details"]["average_task_duration"] = sum(task_durations) / len(task_durations)
                test_result["details"]["max_task_duration"] = max(task_durations)
                test_result["details"]["min_task_duration"] = min(task_durations)
            
            # Determine success criteria
            completed_ratio = test_result["details"]["multiple_tasks_completed"] / 3
            avg_duration = test_result["details"]["average_task_duration"]
            
            if completed_ratio >= 0.67 and avg_duration < 30.0:  # 67% success rate, under 30s average
                test_result["success"] = True
                print(f"✅ Performance stable: {completed_ratio:.1%} success rate, {avg_duration:.1f}s average")
            else:
                print(f"⚠️  Performance concerns: {completed_ratio:.1%} success rate, {avg_duration:.1f}s average")
                
        except Exception as e:
            test_result["details"]["error"] = str(e)
            print(f"❌ Performance test error: {e}")
        
        test_result["duration"] = time.time() - test_result["start_time"]
        self.test_results.append(test_result)
        return test_result
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        
        total_duration = time.time() - self.start_time
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        
        report = {
            "vesper_adl_bge_test_report": {
                "timestamp": time.time(),
                "total_duration": total_duration,
                "tests_run": total_tests,
                "tests_successful": successful_tests,
                "tests_failed": total_tests - successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0.0,
                "integration_ready": self.integration_ready,
                "overall_success": successful_tests >= 3  # At least 3/5 tests should pass
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        # Save report to file
        self._save_test_report(report)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 VESPER ADL BGE Test Report Summary")
        print("=" * 60)
        print(f"Tests Run: {total_tests}")
        print(f"Tests Successful: {successful_tests}")
        print(f"Success Rate: {report['vesper_adl_bge_test_report']['success_rate']:.1%}")
        print(f"Total Duration: {total_duration:.1f}s")
        print(f"Integration Ready: {self.integration_ready}")
        print(f"Overall Status: {'✅ PASS' if report['vesper_adl_bge_test_report']['overall_success'] else '❌ FAIL'}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        
        # Check integration initialization
        init_test = next((r for r in self.test_results if r["test_name"] == "integration_initialization"), None)
        if init_test and not init_test["success"]:
            recommendations.append("Fix VESPER ADL integration initialization issues")
        
        # Check basic ADL execution
        adl_test = next((r for r in self.test_results if r["test_name"] == "basic_adl_execution"), None)
        if adl_test and adl_test["details"]["tasks_failed"] > 0:
            recommendations.append("Improve ADL task execution reliability")
        
        # Check navigation integration
        nav_test = next((r for r in self.test_results if r["test_name"] == "navigation_integrated_adl"), None)
        if nav_test and not nav_test["success"]:
            recommendations.append("Enhance navigation-ADL integration")
        
        # Check CASAS compatibility
        casas_test = next((r for r in self.test_results if r["test_name"] == "casas_compatibility"), None)
        if casas_test and not casas_test["success"]:
            recommendations.append("Improve CASAS dataset compatibility")
        
        # Check performance
        perf_test = next((r for r in self.test_results if r["test_name"] == "performance_stability"), None)
        if perf_test and not perf_test["success"]:
            recommendations.append("Optimize performance and stability")
        
        if not recommendations:
            recommendations.append("All tests passed - system ready for production use")
        
        return recommendations
    
    def _save_test_report(self, report: Dict[str, Any]):
        """Save test report to file"""
        
        try:
            os.makedirs("../evaluation_logs", exist_ok=True)
            
            timestamp = int(time.time())
            filename = f"../evaluation_logs/vesper_adl_bge_test_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📁 Test report saved: {filename}")
            
        except Exception as e:
            print(f"⚠️  Could not save test report: {e}")

# Standalone test execution functions
def run_vesper_adl_test():
    """Run VESPER ADL test suite - can be called from existing test scripts"""
    test_harness = VESPERADLBGETest()
    return test_harness.run_full_adl_test_suite()

def quick_vesper_adl_test():
    """Quick VESPER ADL test - just initialization and one task"""
    print("🧪 Quick VESPER ADL Test")
    
    # Test initialization
    init_success = initialize_vesper_adl_integration()
    
    if init_success:
        # Test one ADL task
        result = execute_adl_cooking_task()
        success = result.get("success", False) if result else False
        
        print(f"✅ Quick test {'PASSED' if success else 'FAILED'}")
        return success
    else:
        print("❌ Quick test FAILED - initialization failed")
        return False

# Integration with existing BGE testing
def integrate_with_existing_bge_tests():
    """Add VESPER ADL tests to existing BGE test suite"""
    
    # Add VESPER ADL test functions to BGE logic for existing tests to call
    bge.logic.run_vesper_adl_test = run_vesper_adl_test
    bge.logic.quick_vesper_adl_test = quick_vesper_adl_test
    
    print("✅ VESPER ADL tests integrated with existing BGE test suite")

# Auto-run integration when imported
if 'bge' in globals():
    integrate_with_existing_bge_tests()

# Main execution
if __name__ == "__main__":
    print("🚀 Running VESPER ADL BGE Test Suite...")
    result = run_vesper_adl_test()
    
    if result["vesper_adl_bge_test_report"]["overall_success"]:
        print("🎉 VESPER ADL BGE Integration: ALL SYSTEMS GO!")
    else:
        print("⚠️  VESPER ADL BGE Integration: Issues detected, see report for details")
