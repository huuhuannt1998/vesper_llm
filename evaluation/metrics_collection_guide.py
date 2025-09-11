#!/usr/bin/env python3
"""
VESPER Metrics Collection Guide
==============================

Complete workflow for collecting and computing evaluation metrics from Blender datasets.

This script demonstrates the complete pipeline:
1. Data Collection from Blender
2. Metrics Computation
3. CASAS Comparison
4. Report Generation
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path

# Add evaluation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vesper_metrics_calculator import VESPERMetricsCalculator
from vesper_dataset_pipeline import VESPERDatasetPipeline


class VESPERMetricsWorkflow:
    """Complete workflow for VESPER metrics collection and computation"""
    
    def __init__(self):
        self.base_dir = Path(r"C:\Users\hbui11\Desktop\vesper_llm")
        self.logs_dir = self.base_dir / "blender" / "evaluation_logs"
        self.results_dir = self.base_dir / "evaluation" / "results"
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.metrics_calculator = VESPERMetricsCalculator()
        self.dataset_pipeline = VESPERDatasetPipeline()
        
    def step1_collect_blender_data(self):
        """Step 1: Data Collection Instructions"""
        print("🎮 STEP 1: BLENDER DATA COLLECTION")
        print("=" * 50)
        print()
        print("To collect navigation data from Blender:")
        print()
        print("1. Open Blender with your house layout")
        print("2. Load: blender/setup_bge_logic.py (creates Actor and Camera)")
        print("3. Load: blender/llm_bge_navigation.py (VLM navigation system)")
        print("4. Press P to start Game Engine")
        print("5. VLM will navigate automatically and generate logs")
        print()
        print("Expected output files:")
        print(f"   📁 {self.logs_dir}/")
        print("   📄 vesper_navigation_log_YYYYMMDD_HHMMSS.json")
        print()
        
        # Check for existing logs
        log_files = list(self.logs_dir.glob("vesper_navigation_log_*.json"))
        if log_files:
            print(f"✅ Found {len(log_files)} existing log files:")
            for log_file in log_files[-5:]:  # Show latest 5
                print(f"   📄 {log_file.name}")
            if len(log_files) > 5:
                print(f"   ... and {len(log_files) - 5} more")
        else:
            print("❌ No log files found. Please run Blender navigation first.")
        
        return len(log_files) > 0
    
    def step2_convert_to_casas_format(self):
        """Step 2: Convert VLM logs to CASAS format for comparison"""
        print("\n🔄 STEP 2: CASAS FORMAT CONVERSION")
        print("=" * 50)
        print()
        print("Converting VLM navigation logs to CASAS sensor format...")
        
        try:
            conversion_stats = self.dataset_pipeline.convert_vlm_logs()
            
            print(f"✅ Conversion completed:")
            print(f"   📊 Files converted: {conversion_stats['total_files_converted']}")
            print(f"   📁 Output directory: {conversion_stats['output_directory']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Conversion failed: {e}")
            return False
    
    def step3_compute_all_metrics(self):
        """Step 3: Compute comprehensive evaluation metrics"""
        print("\n📊 STEP 3: METRICS COMPUTATION")
        print("=" * 50)
        print()
        
        # Compute metrics for all log files
        print("Computing comprehensive metrics for all log files...")
        
        metrics_file = self.results_dir / "vesper_comprehensive_metrics.csv"
        metrics_df = self.metrics_calculator.compute_batch_metrics(str(metrics_file))
        
        if metrics_df.empty:
            print("❌ No metrics computed - no valid log files found")
            return False
        
        print(f"✅ Metrics computed for {len(metrics_df)} sessions")
        print(f"📁 Saved to: {metrics_file}")
        
        # Display summary
        print("\n📈 METRICS SUMMARY:")
        print("-" * 30)
        
        key_metrics = [
            'task_completion_rate',
            'task_success_rate', 
            'navigation_efficiency',
            'sensor_activation_accuracy',
            'casas_overall_similarity',
            'semantic_understanding_score'
        ]
        
        for metric in key_metrics:
            if metric in metrics_df.columns:
                mean_val = metrics_df[metric].mean()
                std_val = metrics_df[metric].std()
                print(f"{metric:25s}: {mean_val:.3f} ± {std_val:.3f}")
        
        return True
    
    def step4_casas_comparison(self):
        """Step 4: CASAS ground truth comparison"""
        print("\n🏠 STEP 4: CASAS GROUND TRUTH COMPARISON")
        print("=" * 50)
        print()
        
        print("Running comprehensive CASAS comparison analysis...")
        
        try:
            analysis_stats = self.dataset_pipeline.run_comparison_analysis()
            
            if analysis_stats:
                print(f"✅ CASAS comparison completed:")
                print(f"   📊 Total comparisons: {analysis_stats['total_comparisons']}")
                print(f"   📈 Average similarity: {analysis_stats['average_similarity']:.3f}")
                print(f"   🏆 Best similarity: {analysis_stats['best_similarity']:.3f}")
                print(f"   📁 Results: {analysis_stats['output_directory']}")
                
                return True
            else:
                print("❌ No comparison results generated")
                return False
                
        except Exception as e:
            print(f"❌ CASAS comparison failed: {e}")
            return False
    
    def step5_generate_reports(self):
        """Step 5: Generate comprehensive reports"""
        print("\n📋 STEP 5: REPORT GENERATION")
        print("=" * 50)
        print()
        
        # Load metrics data
        metrics_file = self.results_dir / "vesper_comprehensive_metrics.csv"
        if not metrics_file.exists():
            print("❌ Metrics file not found. Run step 3 first.")
            return False
        
        metrics_df = pd.read_csv(metrics_file)
        
        # Generate detailed report
        report_file = self.results_dir / "vesper_evaluation_report.txt"
        report = self.metrics_calculator.generate_metrics_report(metrics_df, str(report_file))
        
        print(f"✅ Evaluation report generated: {report_file}")
        
        # Generate research summary
        research_summary = self.dataset_pipeline.generate_research_summary(
            {'total_files_converted': len(metrics_df)},
            {
                'total_comparisons': len(metrics_df),
                'average_similarity': metrics_df.get('casas_overall_similarity', pd.Series([0])).mean(),
                'best_similarity': metrics_df.get('casas_overall_similarity', pd.Series([0])).max(),
                'worst_similarity': metrics_df.get('casas_overall_similarity', pd.Series([0])).min()
            }
        )
        
        print(f"✅ Research summary generated: {research_summary}")
        
        # Display key findings
        print("\n🔍 KEY FINDINGS:")
        print("-" * 20)
        
        if 'task_completion_rate' in metrics_df.columns:
            tcr = metrics_df['task_completion_rate'].mean()
            print(f"Task Completion Rate: {tcr:.1%}")
            
        if 'casas_overall_similarity' in metrics_df.columns:
            similarity = metrics_df['casas_overall_similarity'].mean()
            print(f"CASAS Similarity: {similarity:.1%}")
            
        if 'navigation_efficiency' in metrics_df.columns:
            efficiency = metrics_df['navigation_efficiency'].mean()
            print(f"Navigation Efficiency: {efficiency:.1%}")
        
        return True
    
    def run_complete_workflow(self):
        """Run the complete metrics collection and computation workflow"""
        print("🚀 VESPER METRICS COLLECTION WORKFLOW")
        print("=" * 60)
        print()
        
        success_steps = 0
        total_steps = 5
        
        # Step 1: Check data collection
        if self.step1_collect_blender_data():
            success_steps += 1
        
        # Step 2: Convert to CASAS format
        if self.step2_convert_to_casas_format():
            success_steps += 1
        
        # Step 3: Compute metrics
        if self.step3_compute_all_metrics():
            success_steps += 1
        
        # Step 4: CASAS comparison
        if self.step4_casas_comparison():
            success_steps += 1
        
        # Step 5: Generate reports
        if self.step5_generate_reports():
            success_steps += 1
        
        # Final summary
        print(f"\n🎉 WORKFLOW COMPLETION: {success_steps}/{total_steps} steps successful")
        print("=" * 60)
        
        if success_steps == total_steps:
            print("✅ Complete workflow executed successfully!")
            print("\n📁 Generated Files:")
            print(f"   📊 Metrics: {self.results_dir}/vesper_comprehensive_metrics.csv")
            print(f"   📋 Report: {self.results_dir}/vesper_evaluation_report.txt")
            print(f"   🔍 Analysis: casas_testbed/data/comparison_results/")
            
            # Show file paths for easy access
            print(f"\n🔗 Quick Access Commands:")
            print(f"   📊 type \"{self.results_dir}/vesper_comprehensive_metrics.csv\"")
            print(f"   📋 type \"{self.results_dir}/vesper_evaluation_report.txt\"")
            
        else:
            print("⚠️  Workflow partially completed. Check error messages above.")
        
        return success_steps == total_steps


def quick_metrics_example():
    """Quick example of computing metrics for a single log file"""
    print("\n🚀 QUICK METRICS EXAMPLE")
    print("=" * 40)
    
    calculator = VESPERMetricsCalculator()
    
    # Find latest log file
    logs_dir = Path(r"C:\Users\hbui11\Desktop\vesper_llm\blender\evaluation_logs")
    log_files = list(logs_dir.glob("vesper_navigation_log_*.json"))
    
    if not log_files:
        print("❌ No log files found")
        return
    
    # Use latest log file
    latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
    print(f"📄 Analyzing: {latest_log.name}")
    
    # Compute metrics
    metrics = calculator.compute_all_metrics(str(latest_log))
    
    # Display results
    print(f"\n📊 METRICS RESULTS:")
    print("-" * 30)
    
    research_metrics = [
        'task_completion_rate',
        'task_success_rate',
        'navigation_efficiency', 
        'sensor_activation_accuracy',
        'effective_movement_ratio',
        'oscillation_index',
        'room_label_stability',
        'semantic_understanding_score'
    ]
    
    for metric in research_metrics:
        if metric in metrics:
            value = metrics[metric]
            print(f"{metric:30s}: {value:.3f}")


def main():
    """Main execution with menu options"""
    print("VESPER METRICS COLLECTION SYSTEM")
    print("=" * 50)
    print()
    print("Choose an option:")
    print("1. Run complete workflow (recommended)")
    print("2. Quick metrics example (single file)")
    print("3. Step-by-step guided workflow")
    print()
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            workflow = VESPERMetricsWorkflow()
            workflow.run_complete_workflow()
            
        elif choice == "2":
            quick_metrics_example()
            
        elif choice == "3":
            workflow = VESPERMetricsWorkflow()
            print("\nStep-by-step workflow:")
            print("Run each step individually? (y/n)")
            
            if input().lower().startswith('y'):
                workflow.step1_collect_blender_data()
                input("\nPress Enter to continue to step 2...")
                workflow.step2_convert_to_casas_format()
                input("\nPress Enter to continue to step 3...")
                workflow.step3_compute_all_metrics()
                input("\nPress Enter to continue to step 4...")
                workflow.step4_casas_comparison()
                input("\nPress Enter to continue to step 5...")
                workflow.step5_generate_reports()
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
