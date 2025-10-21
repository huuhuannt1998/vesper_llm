"""
Quick analysis of generated VESPER datasets
"""
import json
from pathlib import Path
from collections import defaultdict

def analyze_datasets():
    dataset_dir = Path("casas_testbed/vesper_datasets")
    metrics_files = sorted(dataset_dir.glob("vesper_metrics_*.json"))
    
    if not metrics_files:
        print("❌ No datasets found!")
        return
    
    print("=" * 80)
    print(f"ANALYZING {len(metrics_files)} GENERATED DATASETS")
    print("=" * 80)
    
    total_tasks = 0
    completed_tasks = 0
    failed_tasks = 0
    
    for metrics_file in metrics_files:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get high-level completion stats
        tasks_completed = data.get('tasks_completed', 0)
        tasks_failed = data.get('tasks_failed', 0)
        
        total_tasks += (tasks_completed + tasks_failed)
        completed_tasks += tasks_completed
        failed_tasks += tasks_failed
    
    # Overall statistics
    overall_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    print(f"\n📊 OVERALL STATISTICS")
    print("=" * 80)
    print(f"Total datasets: {len(metrics_files)}")
    print(f"Total tasks: {total_tasks}")
    print(f"Completed tasks: {completed_tasks}")
    print(f"Failed tasks: {failed_tasks}")
    print(f"\n🎯 OVERALL SUCCESS RATE: {overall_rate:.2f}%")
    
    # Task-specific statistics - commented out since structure doesn't have task details
    # print(f"\n📋 TASK-SPECIFIC SUCCESS RATES")
    # print("=" * 80)
    
    # Target comparison
    print(f"\n🎯 TARGET COMPARISON")
    print("=" * 80)
    print(f"Target range: 60-80%")
    print(f"Achieved: {overall_rate:.2f}%")
    
    if 60 <= overall_rate <= 80:
        print("✅ SUCCESS: Within target range!")
    elif overall_rate < 60:
        print(f"❌ BELOW TARGET: {60 - overall_rate:.2f}% below minimum")
    else:
        print(f"⚠️ ABOVE TARGET: {overall_rate - 80:.2f}% above maximum")
    
    print("=" * 80)

if __name__ == "__main__":
    analyze_datasets()
