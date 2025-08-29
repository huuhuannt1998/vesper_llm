"""
VESPER Navigation Evaluation Runner
==================================

This script runs the enhanced navigation system and automatically generates
evaluation metrics from the logged data.

Usage:
    python run_evaluation.py

This will:
1. Monitor for new navigation log files
2. Analyze the logs automatically
3. Generate comprehensive evaluation reports
4. Save results for research tracking
"""

import os
import time
import json
from datetime import datetime
import sys

# Add the project root to the path
sys.path.insert(0, r"C:\Users\hbui11\Desktop\vesper_llm")

from evaluation.log_analyzer import VESPERLogAnalyzer


def monitor_and_analyze_logs():
    """Monitor for new navigation logs and analyze them automatically"""
    
    log_dir = os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\blender", "evaluation_logs")
    results_dir = os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\evaluation", "results")
    
    # Create results directory if it doesn't exist
    os.makedirs(results_dir, exist_ok=True)
    
    print("🔍 VESPER EVALUATION MONITOR")
    print("="*50)
    print(f"📂 Monitoring: {log_dir}")
    print(f"💾 Results saved to: {results_dir}")
    print("🔄 Press Ctrl+C to stop monitoring")
    print("="*50)
    
    processed_files = set()
    
    try:
        while True:
            if not os.path.exists(log_dir):
                print("⏳ Waiting for log directory to be created...")
                time.sleep(5)
                continue
            
            # Check for new log files
            log_files = [f for f in os.listdir(log_dir) 
                        if f.startswith("vesper_navigation_log_") and f.endswith(".json")]
            
            new_files = [f for f in log_files if f not in processed_files]
            
            for log_file in new_files:
                log_path = os.path.join(log_dir, log_file)
                
                # Wait a moment to ensure file is fully written
                time.sleep(2)
                
                print(f"\n📊 Processing new log: {log_file}")
                
                try:
                    # Analyze the log
                    analyzer = VESPERLogAnalyzer(log_path)
                    metrics = analyzer.generate_detailed_metrics()
                    
                    if metrics:
                        # Save detailed results
                        session_id = metrics.get('session_info', {}).get('session_id', 'unknown')
                        results_file = os.path.join(results_dir, f"evaluation_results_{session_id}.json")
                        
                        with open(results_file, 'w', encoding='utf-8') as f:
                            json.dump(metrics, f, indent=2, ensure_ascii=False)
                        
                        print(f"✅ Analysis complete - Results saved: {results_file}")
                        
                        # Print key metrics
                        task_perf = metrics.get('task_performance', {})
                        print(f"📈 Quick Summary:")
                        print(f"   Success Rate: {task_perf.get('completion_rate', 0):.1f}%")
                        print(f"   Tasks Completed: {task_perf.get('successful_tasks', 0)}")
                        print(f"   Overall Score: {metrics.get('overall_score', 0):.1f}/100")
                    
                    processed_files.add(log_file)
                    
                except Exception as e:
                    print(f"❌ Error processing {log_file}: {e}")
            
            if not new_files:
                print("⏳ No new logs... (waiting for navigation session)")
            
            time.sleep(10)  # Check every 10 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
        print(f"📊 Total files processed: {len(processed_files)}")


def analyze_specific_log(log_file_path: str):
    """Analyze a specific log file"""
    if not os.path.exists(log_file_path):
        print(f"❌ Log file not found: {log_file_path}")
        return
    
    print(f"📊 Analyzing specific log: {log_file_path}")
    
    analyzer = VESPERLogAnalyzer(log_file_path)
    metrics = analyzer.generate_detailed_metrics()
    
    if metrics:
        # Save results
        results_dir = os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\evaluation", "results")
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(results_dir, f"manual_analysis_{timestamp}.json")
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved: {results_file}")
        return metrics
    
    return None


def analyze_latest_log():
    """Analyze the most recent log file"""
    print("🔍 Searching for latest navigation log...")
    
    analyzer = VESPERLogAnalyzer()
    if analyzer.analyze_latest_log():
        metrics = analyzer.generate_detailed_metrics()
        
        if metrics:
            results_dir = os.path.join(r"C:\Users\hbui11\Desktop\vesper_llm\evaluation", "results")
            os.makedirs(results_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = os.path.join(results_dir, f"latest_analysis_{timestamp}.json")
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Latest log analysis saved: {results_file}")
            return metrics
    
    print("❌ No logs found to analyze")
    return None


if __name__ == "__main__":
    print("🎯 VESPER Navigation Evaluation System")
    print("Choose an option:")
    print("1. Monitor for new logs (real-time)")
    print("2. Analyze latest log")
    print("3. Analyze specific log file")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            monitor_and_analyze_logs()
        elif choice == "2":
            analyze_latest_log()
        elif choice == "3":
            log_path = input("Enter log file path: ").strip()
            analyze_specific_log(log_path)
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Evaluation system stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
