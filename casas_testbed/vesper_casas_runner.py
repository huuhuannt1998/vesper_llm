"""
VESPER-CASAS Testbed Main Runner
===============================

Main orchestration script for running VESPER-CASAS evaluations.
Executes all 5 ADL tasks with and without errors, then compares against ground truth.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add VESPER paths
sys.path.insert(0, r"C:\Users\hbui11\Desktop\vesper_llm")

from casas_testbed.simulation.activity_executor import CASASActivityExecutor, TaskType, ErrorType
from casas_testbed.evaluation.casas_comparator import CASASDataComparator, ComparisonMetrics

class VESPERCASASTestbed:
    """Main testbed orchestrator"""
    
    def __init__(self, casas_ground_truth_dir: str, output_dir: str):
        self.casas_data_dir = casas_ground_truth_dir
        self.output_dir = output_dir
        self.comparator = CASASDataComparator(casas_ground_truth_dir)
        
        # Will be initialized with actual VESPER system
        self.vesper_system = None  # TODO: Initialize with actual VESPER
        self.executor = CASASActivityExecutor(self.vesper_system)
        
        # Create output directories
        os.makedirs(f"{output_dir}/vesper_generated", exist_ok=True)
        os.makedirs(f"{output_dir}/comparison_results", exist_ok=True)
        os.makedirs(f"{output_dir}/reports", exist_ok=True)
        
    def run_full_evaluation(self, participant_id: str = "v01") -> Dict[str, Any]:
        """Run complete VESPER-CASAS evaluation suite"""
        
        print("🚀 Starting VESPER-CASAS Testbed Evaluation")
        print("=" * 60)
        
        start_time = time.time()
        results = {
            "evaluation_id": f"vesper_casas_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "participant_id": participant_id,
            "start_time": datetime.now().isoformat(),
            "tasks": {},
            "summary": {}
        }
        
        # Define task execution plan
        task_plan = [
            # Normal executions
            (TaskType.PHONE_CALL, ErrorType.NONE, "p01.t1.csv"),
            (TaskType.WASH_HANDS, ErrorType.NONE, "p01.t2.csv"),
            (TaskType.COOK, ErrorType.NONE, "p01.t3.csv"),
            (TaskType.EAT, ErrorType.NONE, "p01.t4.csv"),
            (TaskType.CLEAN, ErrorType.NONE, "p01.t5.csv"),
            
            # Error executions
            (TaskType.PHONE_CALL, ErrorType.WRONG_NUMBER, "p01.t1.csv"),  # Compare with same ground truth
            (TaskType.WASH_HANDS, ErrorType.WATER_LEFT_ON, "p01.t2.csv"),
            (TaskType.COOK, ErrorType.BURNER_LEFT_ON, "p01.t3.csv"),
            (TaskType.EAT, ErrorType.NO_MEDICINE, "p01.t4.csv"),
            (TaskType.CLEAN, ErrorType.NO_WATER_CLEANING, "p01.t5.csv")
        ]
        
        # Execute each task
        for i, (task_type, error_type, ground_truth_file) in enumerate(task_plan, 1):
            print(f"\n📋 Executing Task {i}/{len(task_plan)}: {task_type.name}")
            print(f"🎭 Error Mode: {error_type.value}")
            print("-" * 40)
            
            try:
                # Execute task with VESPER
                execution = self.executor.execute_task(task_type, participant_id, error_type)
                
                # Export results
                task_key = f"t{task_type.value}_{error_type.value}"
                vesper_csv = f"{self.output_dir}/vesper_generated/{participant_id}.{task_key}.csv"
                vesper_details = f"{self.output_dir}/vesper_generated/{participant_id}.{task_key}_details.json"
                
                self.executor.export_execution(execution, f"{self.output_dir}/vesper_generated")
                
                # Compare against ground truth
                if ground_truth_file in self.comparator.ground_truth_data:
                    metrics = self.comparator.compare_execution(
                        vesper_csv, vesper_details, ground_truth_file
                    )
                    
                    # Save comparison results
                    comparison_file = f"{self.output_dir}/comparison_results/{participant_id}.{task_key}_comparison.json"
                    self.comparator.generate_comparison_report(metrics, comparison_file)
                    
                    # Store in results
                    results["tasks"][task_key] = {
                        "task_type": task_type.name,
                        "error_type": error_type.value,
                        "execution_success": execution.success,
                        "execution_duration": execution.duration,
                        "error_detected": execution.error_detected,
                        "error_corrected": execution.error_corrected,
                        "ground_truth_file": ground_truth_file,
                        "comparison_metrics": {
                            "task_duration_correlation": metrics.task_duration_correlation,
                            "sensor_timing_accuracy": metrics.sensor_timing_accuracy,
                            "sequence_alignment_score": metrics.sequence_alignment_score,
                            "motion_pattern_similarity": metrics.motion_pattern_similarity,
                            "location_visitation_accuracy": metrics.location_visitation_accuracy,
                            "path_efficiency_ratio": metrics.path_efficiency_ratio,
                            "object_interaction_accuracy": metrics.object_interaction_accuracy,
                            "task_completion_fidelity": metrics.task_completion_fidelity,
                            "error_detection_capability": metrics.error_detection_capability,
                            "overall_similarity_score": metrics.overall_similarity_score
                        }
                    }
                    
                    print(f"✅ Task completed - Overall Similarity: {metrics.overall_similarity_score:.3f}")
                    
                else:
                    print(f"⚠️ No ground truth data found for {ground_truth_file}")
                    
            except Exception as e:
                print(f"❌ Task execution failed: {e}")
                results["tasks"][task_key] = {
                    "task_type": task_type.name,
                    "error_type": error_type.value,
                    "execution_success": False,
                    "error": str(e)
                }
                
        # Generate summary statistics
        results["summary"] = self._generate_summary_statistics(results["tasks"])
        results["end_time"] = datetime.now().isoformat()
        results["total_duration"] = time.time() - start_time
        
        # Save final results
        final_report = f"{self.output_dir}/reports/vesper_casas_evaluation_{participant_id}.json"
        with open(final_report, 'w') as f:
            json.dump(results, f, indent=2)
            
        # Print summary
        self._print_evaluation_summary(results)
        
        print(f"\n📊 Evaluation Complete!")
        print(f"📁 Results saved to: {self.output_dir}")
        print(f"📋 Final report: {final_report}")
        
        return results
        
    def _generate_summary_statistics(self, tasks: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics across all tasks"""
        
        completed_tasks = [t for t in tasks.values() if "comparison_metrics" in t]
        
        if not completed_tasks:
            return {"error": "No tasks completed successfully"}
            
        # Aggregate metrics
        metrics_sums = {}
        for task in completed_tasks:
            for metric_name, value in task["comparison_metrics"].items():
                if metric_name not in metrics_sums:
                    metrics_sums[metric_name] = []
                metrics_sums[metric_name].append(value)
                
        # Calculate averages
        avg_metrics = {name: sum(values) / len(values) for name, values in metrics_sums.items()}
        
        # Task success rates
        normal_tasks = [t for t in completed_tasks if t["error_type"] == "none"]
        error_tasks = [t for t in completed_tasks if t["error_type"] != "none"]
        
        normal_success_rate = sum(1 for t in normal_tasks if t["execution_success"]) / len(normal_tasks) if normal_tasks else 0
        error_success_rate = sum(1 for t in error_tasks if t["execution_success"]) / len(error_tasks) if error_tasks else 0
        
        # Error detection stats
        error_detection_rate = sum(1 for t in error_tasks if t.get("error_detected", False)) / len(error_tasks) if error_tasks else 0
        error_correction_rate = sum(1 for t in error_tasks if t.get("error_corrected", False)) / len(error_tasks) if error_tasks else 0
        
        return {
            "total_tasks_executed": len(tasks),
            "successful_comparisons": len(completed_tasks),
            "average_metrics": avg_metrics,
            "task_success_rates": {
                "normal_tasks": normal_success_rate,
                "error_tasks": error_success_rate,
                "overall": (normal_success_rate + error_success_rate) / 2
            },
            "error_handling": {
                "detection_rate": error_detection_rate,
                "correction_rate": error_correction_rate
            },
            "performance_categories": {
                "excellent": len([t for t in completed_tasks if t["comparison_metrics"]["overall_similarity_score"] >= 0.8]),
                "good": len([t for t in completed_tasks if 0.6 <= t["comparison_metrics"]["overall_similarity_score"] < 0.8]),
                "fair": len([t for t in completed_tasks if 0.4 <= t["comparison_metrics"]["overall_similarity_score"] < 0.6]),
                "poor": len([t for t in completed_tasks if t["comparison_metrics"]["overall_similarity_score"] < 0.4])
            }
        }
        
    def _print_evaluation_summary(self, results: Dict[str, Any]):
        """Print formatted evaluation summary"""
        
        summary = results["summary"]
        
        print("\n" + "=" * 60)
        print("📊 VESPER-CASAS EVALUATION SUMMARY")
        print("=" * 60)
        
        print(f"📋 Total Tasks: {summary['total_tasks_executed']}")
        print(f"✅ Successful Comparisons: {summary['successful_comparisons']}")
        print(f"⏱️ Total Duration: {results['total_duration']:.1f}s")
        
        print("\n🎯 Task Success Rates:")
        rates = summary["task_success_rates"]
        print(f"   Normal Tasks: {rates['normal_tasks']:.1%}")
        print(f"   Error Tasks: {rates['error_tasks']:.1%}")
        print(f"   Overall: {rates['overall']:.1%}")
        
        print("\n🔍 Error Handling:")
        error_stats = summary["error_handling"]
        print(f"   Detection Rate: {error_stats['detection_rate']:.1%}")
        print(f"   Correction Rate: {error_stats['correction_rate']:.1%}")
        
        print("\n📈 Performance Distribution:")
        perf = summary["performance_categories"]
        print(f"   Excellent (≥80%): {perf['excellent']} tasks")
        print(f"   Good (60-80%): {perf['good']} tasks")
        print(f"   Fair (40-60%): {perf['fair']} tasks")
        print(f"   Poor (<40%): {perf['poor']} tasks")
        
        if "average_metrics" in summary:
            print("\n📊 Average Metrics:")
            avg = summary["average_metrics"]
            print(f"   Overall Similarity: {avg['overall_similarity_score']:.3f}")
            print(f"   Temporal Accuracy: {avg['sensor_timing_accuracy']:.3f}")
            print(f"   Spatial Similarity: {avg['motion_pattern_similarity']:.3f}")
            print(f"   Behavioral Fidelity: {avg['task_completion_fidelity']:.3f}")
            
    def run_single_task(self, task_type: TaskType, error_type: ErrorType = ErrorType.NONE,
                       participant_id: str = "v01") -> Dict[str, Any]:
        """Run a single task for testing"""
        
        print(f"🔬 Running Single Task: {task_type.name}")
        print(f"🎭 Error Mode: {error_type.value}")
        
        execution = self.executor.execute_task(task_type, participant_id, error_type)
        
        # Export results
        task_key = f"t{task_type.value}_{error_type.value}"
        self.executor.export_execution(execution, f"{self.output_dir}/vesper_generated")
        
        return {
            "task_type": task_type.name,
            "error_type": error_type.value,
            "success": execution.success,
            "duration": execution.duration,
            "sensor_activations": len(execution.sensor_readings),
            "vlm_actions": len(execution.vlm_actions)
        }

def main():
    """Main entry point for VESPER-CASAS testbed"""
    
    # Configuration
    config = {
        "casas_ground_truth_dir": r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\data\casas_ground_truth",
        "output_dir": r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\data",
        "participant_id": "vesper_01"
    }
    
    # Initialize testbed
    testbed = VESPERCASASTestbed(
        config["casas_ground_truth_dir"],
        config["output_dir"]
    )
    
    # Run evaluation
    try:
        results = testbed.run_full_evaluation(config["participant_id"])
        print("\n🎉 VESPER-CASAS Evaluation Completed Successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Evaluation interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
