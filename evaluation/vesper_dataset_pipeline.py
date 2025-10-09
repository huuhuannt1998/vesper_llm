#!/usr/bin/env python3
"""
VESPER Dataset Evaluation and CASAS Comparison Pipeline (Production)

Analyzes VESPER datasets from casas_testbed/vesper_datasets/ and compares
with CASAS ground truth datasets.
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Add evaluation directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class VESPERDatasetPipeline:
    """Production pipeline for VESPER dataset analysis and CASAS comparison"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            self.base_dir = Path(r"c:\Users\hbui11\Desktop\vesper_llm")
        else:
            self.base_dir = Path(base_dir)
        
        # PRODUCTION PATHS: Use vesper_datasets folder
        self.vesper_datasets_dir = self.base_dir / "casas_testbed" / "vesper_datasets"
        self.casas_ground_truth_dir = self.base_dir / "casas_testbed" / "data" / "casas_ground_truth"
        self.comparison_results_dir = self.base_dir / "casas_testbed" / "data" / "comparison_results"
        
        # Create directories if they don't exist
        self.vesper_datasets_dir.mkdir(parents=True, exist_ok=True)
        self.comparison_results_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 VESPER datasets: {self.vesper_datasets_dir}")
        print(f"📁 Ground truth: {self.casas_ground_truth_dir}")
        print(f"📁 Results output: {self.comparison_results_dir}")
    
    def detect_vesper_datasets(self):
        """Detect VESPER datasets in the production folder"""
        print("\n" + "="*80)
        print("DETECTING VESPER DATASETS")
        print("="*80)
        
        # Find VLM metrics files (sensor events are now embedded in JSON)
        metrics_files = list(self.vesper_datasets_dir.glob("vesper_metrics_*.json"))
        
        print(f"\n📊 Found {len(metrics_files)} VESPER metrics files")
        for f in metrics_files:
            print(f"   - {f.name}")
        
        # Check if metrics files contain virtual sensor events
        datasets_with_sensors = []
        for metrics_file in metrics_files:
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'virtual_sensor_events' in data and len(data['virtual_sensor_events']) > 0:
                        datasets_with_sensors.append(metrics_file)
                        print(f"   ✅ {metrics_file.name}: {len(data['virtual_sensor_events'])} sensor events")
                    else:
                        print(f"   ⚠️ {metrics_file.name}: No sensor events found")
            except Exception as e:
                print(f"   ❌ {metrics_file.name}: Error reading file - {e}")
        
        return {
            'metrics_files': metrics_files,
            'datasets_with_sensors': datasets_with_sensors
        }
    
    def validate_casas_format(self, casas_file: Path):
        """Validate CASAS file format"""
        try:
            with open(casas_file, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return {'valid': False, 'error': 'Empty file'}
            
            # Check format: YYYY-MM-DD HH:MM:SS.mmm SENSOR_ID LOCATION STATE
            sensors = set()
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                parts = line.strip().split()
                if len(parts) < 4:
                    return {'valid': False, 'error': f'Line {i+1}: Invalid format'}
                
                # Validate timestamp
                try:
                    timestamp = f"{parts[0]} {parts[1]}"
                    datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    return {'valid': False, 'error': f'Line {i+1}: Invalid timestamp'}
                
                sensors.add(parts[2])
            
            return {
                'valid': True,
                'events': len(lines),
                'sensors': sorted(sensors),
                'file': casas_file.name
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def analyze_vesper_metrics(self, metrics_file: Path):
        """Analyze VESPER metrics JSON file"""
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract key metrics
            analysis = {
                'file': metrics_file.name,
                'session_id': data.get('session_id', 'unknown'),
                'total_tasks': len(data.get('task_details', [])),
                'tasks_completed': data.get('tasks_completed', 0),
                'tasks_failed': data.get('tasks_failed', 0),
                'total_steps': data.get('total_steps', 0),
                'total_screenshots': data.get('total_screenshots', 0),
                'total_llm_calls': data.get('total_llm_calls', 0),
                'sensor_events': len(data.get('virtual_sensor_events', [])),
                'virtual_sensor_events': data.get('virtual_sensor_events', [])
            }
            
            # Extract sensor statistics
            if analysis['sensor_events'] > 0:
                sensor_types = {}
                for event in analysis['virtual_sensor_events']:
                    sensor_id = event.get('sensor_id', 'unknown')
                    if sensor_id not in sensor_types:
                        sensor_types[sensor_id] = {'ON': 0, 'OFF': 0}
                    sensor_types[sensor_id][event.get('event', 'ON')] += 1
                
                analysis['sensor_types'] = sensor_types
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {metrics_file.name}: {e}")
            return None
    
    def generate_vesper_summary_report(self, analysis_results):
        """Generate summary report for VESPER datasets"""
        report_file = self.comparison_results_dir / f"vesper_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("VESPER DATASET ANALYSIS SUMMARY\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total datasets analyzed: {len(analysis_results)}\n\n")
            
            for result in analysis_results:
                if result:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"Dataset: {result['file']}\n")
                    f.write(f"{'='*80}\n")
                    f.write(f"Session ID: {result['session_id']}\n")
                    f.write(f"Total Tasks: {result['total_tasks']}\n")
                    f.write(f"Tasks Completed: {result['tasks_completed']}\n")
                    f.write(f"Tasks Failed: {result['tasks_failed']}\n")
                    f.write(f"Total Steps: {result['total_steps']}\n")
                    f.write(f"Screenshots: {result['total_screenshots']}\n")
                    f.write(f"LLM Calls: {result['total_llm_calls']}\n")
                    f.write(f"Virtual Sensor Events: {result['sensor_events']}\n\n")
                    
                    if 'sensor_types' in result:
                        f.write("Sensor Activity:\n")
                        for sensor_id, events in result['sensor_types'].items():
                            f.write(f"  {sensor_id}: ON={events['ON']}, OFF={events['OFF']}\n")
                    f.write("\n")
        
        return report_file
    
    def compare_with_ground_truth(self, vesper_casas_file: Path):
        """Compare VESPER CASAS data with ground truth datasets"""
        print("\n" + "="*80)
        print(f"COMPARING: {vesper_casas_file.name}")
        print("="*80)
        
        # Load VESPER data
        vesper_events = []
        with open(vesper_casas_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    vesper_events.append({
                        'timestamp': f"{parts[0]} {parts[1]}",
                        'sensor': parts[2],
                        'location': parts[3] if len(parts) > 3 else '',
                        'state': parts[4] if len(parts) > 4 else parts[3]
                    })
        
        print(f"\n📊 VESPER dataset: {len(vesper_events)} sensor events")
        
        # Analyze sensor distribution
        sensor_counts = Counter(e['sensor'] for e in vesper_events)
        print(f"   Sensor activations:")
        for sensor, count in sorted(sensor_counts.items()):
            print(f"     {sensor}: {count} events")
        
        # Load ground truth files
        print(f"\n🔍 Scanning ground truth datasets...")
        
        # Get all ground truth CSV files
        gt_files = []
        for subdir in ['adl_noerror', 'adl_error']:
            gt_dir = self.casas_ground_truth_dir / subdir
            if gt_dir.exists():
                gt_files.extend(list(gt_dir.glob("*.csv")))
        
        print(f"   Found {len(gt_files)} ground truth files")
        
        # Perform comparison with sample ground truth files
        if gt_files:
            print(f"\n📈 Comparing with ground truth samples...")
            
            # Compare with first few files as examples
            sample_files = gt_files[:5]
            comparison_results = []
            
            for gt_file in sample_files:
                result = self._compare_casas_files(vesper_events, gt_file)
                comparison_results.append(result)
                print(f"   {gt_file.name}: {result['match_percentage']:.1f}% match")
            
            # Calculate average metrics
            avg_match = sum(r['match_percentage'] for r in comparison_results) / len(comparison_results)
            
            return {
                'vesper_file': vesper_casas_file.name,
                'vesper_events': len(vesper_events),
                'ground_truth_files': len(gt_files),
                'samples_compared': len(sample_files),
                'average_match': avg_match,
                'sensor_distribution': dict(sensor_counts),
                'comparisons': comparison_results
            }
        else:
            print("   ⚠️ No ground truth files found for comparison")
            return {
                'vesper_file': vesper_casas_file.name,
                'vesper_events': len(vesper_events),
                'ground_truth_files': 0,
                'sensor_distribution': dict(sensor_counts)
            }
    
    def _compare_casas_files(self, vesper_events: list, gt_file: Path):
        """Compare VESPER events with a ground truth file"""
        try:
            # Load ground truth CSV
            gt_events = []
            with open(gt_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3:
                        gt_events.append({
                            'timestamp': row[0],
                            'sensor': row[1],
                            'location': row[2] if len(row) > 2 else '',
                            'state': row[3] if len(row) > 3 else ''
                        })
            
            # Compare sensor usage patterns
            vesper_sensors = Counter(e['sensor'] for e in vesper_events)
            gt_sensors = Counter(e['sensor'] for e in gt_events)
            
            # Calculate similarity (simple sensor overlap)
            common_sensors = set(vesper_sensors.keys()) & set(gt_sensors.keys())
            total_sensors = set(vesper_sensors.keys()) | set(gt_sensors.keys())
            
            match_percentage = (len(common_sensors) / len(total_sensors) * 100) if total_sensors else 0
            
            return {
                'ground_truth_file': gt_file.name,
                'gt_events': len(gt_events),
                'vesper_events': len(vesper_events),
                'common_sensors': list(common_sensors),
                'match_percentage': match_percentage,
                'vesper_sensor_counts': dict(vesper_sensors),
                'gt_sensor_counts': dict(gt_sensors)
            }
            
        except Exception as e:
            return {
                'ground_truth_file': gt_file.name,
                'error': str(e),
                'match_percentage': 0
            }
    
    def generate_comparison_report(self, all_results: list) -> str:
        """Generate comprehensive comparison report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.comparison_results_dir / f"vesper_comparison_report_{timestamp}.md"
        
        with open(report_file, 'w') as f:
            f.write("# VESPER Dataset vs CASAS Ground Truth Comparison Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Overview\n\n")
            f.write(f"- **VESPER Datasets Analyzed:** {len(all_results)}\n")
            f.write(f"- **Output Directory:** `{self.comparison_results_dir}`\n\n")
            
            # Individual dataset results
            for result in all_results:
                f.write(f"### {result['vesper_file']}\n\n")
                f.write(f"- **VESPER Events:** {result['vesper_events']}\n")
                f.write(f"- **Ground Truth Files Compared:** {result.get('samples_compared', 0)}\n")
                
                if 'average_match' in result:
                    f.write(f"- **Average Match:** {result['average_match']:.1f}%\n")
                
                if 'sensor_distribution' in result:
                    f.write(f"\n**Sensor Distribution:**\n")
                    for sensor, count in sorted(result['sensor_distribution'].items()):
                        f.write(f"  - {sensor}: {count} activations\n")
                
                f.write("\n")
            
            f.write("## Summary\n\n")
            f.write("This report provides an analysis of VESPER-generated motion sensor data\n")
            f.write("compared with CASAS ground truth datasets. The comparison focuses on\n")
            f.write("sensor activation patterns and behavioral similarity.\n\n")
            
            f.write("## Recommendations\n\n")
            f.write("1. Review sensor activation patterns for consistency\n")
            f.write("2. Analyze discrepancies between VESPER and ground truth\n")
            f.write("3. Consider navigation algorithm improvements\n")
            f.write("4. Generate additional datasets for robust comparison\n")
        
        return str(report_file)
    
    def create_vesper_visualizations(self, analysis_results: list) -> list:
        """Create visualization plots for VESPER dataset analysis"""
        print("\n" + "="*80)
        print("GENERATING VISUALIZATION GRAPHS")
        print("="*80)
        
        plot_files = []
        
        if not analysis_results or len(analysis_results) == 0:
            print("⚠️  No results to visualize")
            return plot_files
        
        try:
            # Prepare data
            datasets = []
            for result in analysis_results:
                if result:
                    datasets.append({
                        'name': result.get('session_id', 'Unknown'),
                        'tasks': result.get('total_tasks', 0),
                        'completed': result.get('tasks_completed', 0),
                        'failed': result.get('tasks_failed', 0),
                        'sensor_events': result.get('sensor_events', 0),
                        'steps': result.get('total_steps', 0),
                        'llm_calls': result.get('total_llm_calls', 0),
                        'screenshots': result.get('total_screenshots', 0)
                    })
            
            if not datasets:
                print("⚠️  No valid data for visualization")
                return plot_files
            
            df = pd.DataFrame(datasets)
            
            # 1. Task Completion Overview
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # Pie chart of overall completion
            total_completed = df['completed'].sum()
            total_failed = df['failed'].sum()
            
            # Only create pie chart if there's data
            if total_completed > 0 or total_failed > 0:
                ax1.pie([total_completed, total_failed], labels=['Completed', 'Failed'], 
                       autopct='%1.1f%%', colors=['#4CAF50', '#F44336'], startangle=90)
                ax1.set_title('Overall Task Completion', fontsize=12, fontweight='bold')
            else:
                ax1.text(0.5, 0.5, 'No task data', ha='center', va='center', fontsize=14)
                ax1.set_title('Overall Task Completion', fontsize=12, fontweight='bold')
            
            # Bar chart per dataset
            x = np.arange(len(df))
            width = 0.35
            ax2.bar(x - width/2, df['completed'], width, label='Completed', color='#4CAF50')
            ax2.bar(x + width/2, df['failed'], width, label='Failed', color='#F44336')
            ax2.set_xlabel('Dataset')
            ax2.set_ylabel('Task Count')
            ax2.set_title('Task Completion by Dataset', fontsize=12, fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels([d[:10] + '...' if len(d) > 10 else d for d in df['name']], rotation=45, ha='right')
            ax2.legend()
            ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plot_file_1 = self.comparison_results_dir / "task_completion.png"
            plt.savefig(plot_file_1, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(str(plot_file_1))
            print(f"✅ Created: {plot_file_1.name}")
            
            # 2. Sensor Activity Distribution
            plt.figure(figsize=(12, 6))
            x = np.arange(len(df))
            plt.bar(x, df['sensor_events'], color='#2196F3', alpha=0.7, edgecolor='black')
            plt.xlabel('Dataset', fontsize=11)
            plt.ylabel('Sensor Event Count', fontsize=11)
            plt.title('Virtual Sensor Activity by Dataset', fontsize=14, fontweight='bold')
            plt.xticks(x, [d[:10] + '...' if len(d) > 10 else d for d in df['name']], rotation=45, ha='right')
            plt.grid(True, alpha=0.3, axis='y', linestyle='--')
            
            # Add value labels on bars
            for i, v in enumerate(df['sensor_events']):
                plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            plot_file_2 = self.comparison_results_dir / "sensor_activity.png"
            plt.savefig(plot_file_2, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(str(plot_file_2))
            print(f"✅ Created: {plot_file_2.name}")
            
            # 3. Navigation Metrics Comparison
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            
            # Steps taken
            axes[0, 0].bar(df['name'], df['steps'], color='#9C27B0', alpha=0.7, edgecolor='black')
            axes[0, 0].set_title('Steps Taken per Dataset', fontweight='bold')
            axes[0, 0].set_ylabel('Steps')
            axes[0, 0].tick_params(axis='x', rotation=45)
            axes[0, 0].grid(True, alpha=0.3, axis='y')
            
            # LLM calls
            axes[0, 1].bar(df['name'], df['llm_calls'], color='#FF9800', alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('LLM Calls per Dataset', fontweight='bold')
            axes[0, 1].set_ylabel('LLM Calls')
            axes[0, 1].tick_params(axis='x', rotation=45)
            axes[0, 1].grid(True, alpha=0.3, axis='y')
            
            # Screenshots
            axes[1, 0].bar(df['name'], df['screenshots'], color='#00BCD4', alpha=0.7, edgecolor='black')
            axes[1, 0].set_title('Screenshots Taken per Dataset', fontweight='bold')
            axes[1, 0].set_ylabel('Screenshots')
            axes[1, 0].tick_params(axis='x', rotation=45)
            axes[1, 0].grid(True, alpha=0.3, axis='y')
            
            # Efficiency: Steps per Task
            df['efficiency'] = df['steps'] / df['tasks']
            axes[1, 1].bar(df['name'], df['efficiency'], color='#4CAF50', alpha=0.7, edgecolor='black')
            axes[1, 1].set_title('Efficiency (Steps per Task)', fontweight='bold')
            axes[1, 1].set_ylabel('Steps/Task')
            axes[1, 1].tick_params(axis='x', rotation=45)
            axes[1, 1].grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            plot_file_3 = self.comparison_results_dir / "navigation_metrics.png"
            plt.savefig(plot_file_3, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(str(plot_file_3))
            print(f"✅ Created: {plot_file_3.name}")
            
            # 4. Sensor Activity Heatmap (if sensor distribution available)
            sensor_data = []
            for result in analysis_results:
                if result and 'sensor_types' in result:
                    for sensor_id, counts in result['sensor_types'].items():
                        total_count = counts.get('ON', 0) + counts.get('OFF', 0)
                        sensor_data.append({
                            'Dataset': result.get('session_id', 'Unknown')[:15],
                            'Sensor': sensor_id,
                            'Count': total_count
                        })
            
            if sensor_data:
                sensor_df = pd.DataFrame(sensor_data)
                pivot_table = sensor_df.pivot_table(values='Count', index='Sensor', columns='Dataset', fill_value=0)
                
                plt.figure(figsize=(12, 8))
                sns.heatmap(pivot_table, annot=True, fmt='g', cmap='YlOrRd', 
                           linewidths=0.5, cbar_kws={'label': 'Activation Count'})
                plt.title('Sensor Activation Heatmap', fontsize=14, fontweight='bold')
                plt.xlabel('Dataset', fontsize=11)
                plt.ylabel('Sensor ID', fontsize=11)
                plt.tight_layout()
                plot_file_4 = self.comparison_results_dir / "sensor_heatmap.png"
                plt.savefig(plot_file_4, dpi=300, bbox_inches='tight')
                plt.close()
                plot_files.append(str(plot_file_4))
                print(f"✅ Created: {plot_file_4.name}")
            
        except Exception as e:
            print(f"⚠️  Error creating visualizations: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n📊 Total graphs created: {len(plot_files)}")
        return plot_files
    
    def create_visualizations(self, all_results: list) -> list:
        """Create visualization plots for VESPER dataset comparison results"""
        print("\n" + "="*80)
        print("GENERATING VISUALIZATION GRAPHS")
        print("="*80)
        
        plot_files = []
        
        # Prepare data for visualizations
        if not all_results or len(all_results) == 0:
            print("⚠️  No results to visualize")
            return plot_files
        
        # Extract comparison data
        comparison_data = []
        for result in all_results:
            if 'comparisons' in result:
                for comp in result['comparisons']:
                    comparison_data.append({
                        'vesper_file': result['vesper_file'],
                        'vesper_events': result['vesper_events'],
                        'gt_events': comp.get('gt_events', 0),
                        'match_percentage': comp.get('match_percentage', 0),
                        'common_sensors': len(comp.get('common_sensors', []))
                    })
        
        if not comparison_data:
            print("⚠️  No comparison data available for visualization")
            return plot_files
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(comparison_data)
        
        try:
            # 1. Match Percentage Distribution
            plt.figure(figsize=(10, 6))
            plt.hist(df['match_percentage'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            plt.title('Match Percentage Distribution (VESPER vs Ground Truth)', fontsize=14, fontweight='bold')
            plt.xlabel('Match Percentage (%)')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.axvline(df['match_percentage'].mean(), color='red', linestyle='--', 
                       label=f'Mean: {df["match_percentage"].mean():.1f}%')
            plt.legend()
            plt.tight_layout()
            plot_file_1 = self.comparison_results_dir / "similarity_distribution.png"
            plt.savefig(plot_file_1, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(str(plot_file_1))
            print(f"✅ Created: {plot_file_1.name}")
            
            # 2. Event Count Comparison
            plt.figure(figsize=(10, 8))
            plt.scatter(df['gt_events'], df['vesper_events'], alpha=0.6, s=100, c=df['match_percentage'], 
                       cmap='viridis', edgecolors='black')
            max_count = max(df['gt_events'].max(), df['vesper_events'].max())
            plt.plot([0, max_count], [0, max_count], 'r--', linewidth=2, label='Perfect Agreement', alpha=0.7)
            plt.colorbar(label='Match %')
            plt.title('Event Count: VESPER vs Ground Truth', fontsize=14, fontweight='bold')
            plt.xlabel('Ground Truth Event Count')
            plt.ylabel('VESPER Event Count')
            plt.legend()
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            plot_file_2 = self.comparison_results_dir / "event_count_scatter.png"
            plt.savefig(plot_file_2, dpi=300, bbox_inches='tight')
            plt.close()
            plot_files.append(str(plot_file_2))
            print(f"✅ Created: {plot_file_2.name}")
            
            # 3. Sensor Distribution Comparison
            plt.figure(figsize=(12, 6))
            sensor_data = []
            for result in all_results:
                if 'sensor_distribution' in result:
                    for sensor, count in result['sensor_distribution'].items():
                        sensor_data.append({
                            'dataset': result['vesper_file'],
                            'sensor': sensor,
                            'activations': count
                        })
            
            if sensor_data:
                sensor_df = pd.DataFrame(sensor_data)
                sensors = sorted(sensor_df['sensor'].unique())
                datasets = sensor_df['dataset'].unique()
                
                x = np.arange(len(sensors))
                width = 0.8 / len(datasets)
                
                for i, dataset in enumerate(datasets):
                    dataset_data = sensor_df[sensor_df['dataset'] == dataset]
                    counts = [dataset_data[dataset_data['sensor'] == s]['activations'].sum() 
                             if s in dataset_data['sensor'].values else 0 for s in sensors]
                    plt.bar(x + i * width, counts, width, label=dataset[:20] + '...' if len(dataset) > 20 else dataset)
                
                plt.title('Sensor Activation Distribution by Dataset', fontsize=14, fontweight='bold')
                plt.xlabel('Sensor ID')
                plt.ylabel('Activation Count')
                plt.xticks(x + width * (len(datasets) - 1) / 2, sensors)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.grid(True, alpha=0.3, axis='y', linestyle='--')
                plt.tight_layout()
                plot_file_3 = self.comparison_results_dir / "metric_comparison.png"
                plt.savefig(plot_file_3, dpi=300, bbox_inches='tight')
                plt.close()
                plot_files.append(str(plot_file_3))
                print(f"✅ Created: {plot_file_3.name}")
            
            # 4. Dataset Statistics Heatmap
            plt.figure(figsize=(10, 8))
            heatmap_data = []
            for result in all_results:
                row = {
                    'Dataset': result['vesper_file'][:20],
                    'Events': result['vesper_events'],
                    'Sensors': len(result.get('sensor_distribution', {})),
                    'Avg Match': result.get('average_match', 0)
                }
                heatmap_data.append(row)
            
            if heatmap_data:
                heatmap_df = pd.DataFrame(heatmap_data)
                heatmap_df = heatmap_df.set_index('Dataset')
                
                # Normalize for better visualization
                normalized_df = (heatmap_df - heatmap_df.min()) / (heatmap_df.max() - heatmap_df.min())
                
                sns.heatmap(normalized_df.T, annot=heatmap_df.T, fmt='.1f', cmap='YlOrRd', 
                           cbar_kws={'label': 'Normalized Score'}, linewidths=0.5)
                plt.title('VESPER Dataset Statistics Comparison', fontsize=14, fontweight='bold')
                plt.tight_layout()
                plot_file_4 = self.comparison_results_dir / "correlation_heatmap.png"
                plt.savefig(plot_file_4, dpi=300, bbox_inches='tight')
                plt.close()
                plot_files.append(str(plot_file_4))
                print(f"✅ Created: {plot_file_4.name}")
            
        except Exception as e:
            print(f"⚠️  Error creating visualizations: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n📊 Total graphs created: {len(plot_files)}")
        return plot_files
    
    def run_complete_pipeline(self) -> dict:
        """Run the complete VESPER dataset analysis and comparison pipeline"""
        print("\n" + "="*80)
        print("VESPER DATASET ANALYSIS & CASAS COMPARISON PIPELINE")
        print("="*80)
        
        # Step 1: Detect VESPER datasets
        datasets = self.detect_vesper_datasets()
        
        if not datasets['metrics_files']:
            print("\n⚠️ No VESPER datasets found!")
            print(f"   Expected location: {self.vesper_datasets_dir}")
            print("   Run BGE navigation first to generate datasets.")
            return {'status': 'no_data'}
        
        if not datasets['datasets_with_sensors']:
            print("\n⚠️ VESPER datasets found, but no virtual sensor events!")
            print("   Make sure virtual sensor logging is enabled in BGE navigation.")
            print(f"   Files found: {len(datasets['metrics_files'])}")
            return {'status': 'no_sensor_data'}
        
        # Step 2: Analyze VESPER metrics
        print("\n" + "="*80)
        print("ANALYZING VESPER METRICS")
        print("="*80)
        
        analysis_results = []
        for metrics_file in datasets['datasets_with_sensors']:
            result = self.analyze_vesper_metrics(metrics_file)
            analysis_results.append(result)
            if result:
                print(f"\n✅ {metrics_file.name}")
                print(f"   Tasks: {result.get('total_tasks', 0)}")
                print(f"   Sensor events: {result.get('sensor_events', 0)}")
                print(f"   Steps: {result.get('total_steps', 0)}")
            else:
                print(f"\n❌ {metrics_file.name}: Analysis failed")
        
        # Step 3: Generate summary report
        print("\n" + "="*80)
        print("GENERATING SUMMARY REPORT")
        print("="*80)
        
        report_file = self.generate_vesper_summary_report(analysis_results)
        print(f"\n✅ Report saved: {os.path.basename(report_file)}")
        
        # Step 4: Create visualization graphs
        plot_files = self.create_vesper_visualizations(analysis_results)
        
        # Save pipeline results JSON first
        results_json = self.comparison_results_dir / f"vesper_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Compile final results
        pipeline_results = {
            'vesper_datasets': len(datasets['datasets_with_sensors']),
            'metrics_files': len(datasets['metrics_files']),
            'analysis_results': analysis_results,
            'report_file': str(report_file),
            'json_file': str(results_json),
            'plot_files': plot_files,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(results_json, 'w', encoding='utf-8') as f:
            json.dump(pipeline_results, f, indent=2)
        
        print(f"✅ Results JSON: {results_json.name}")
        print(f"\n📁 All outputs: {self.comparison_results_dir}")
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
        return pipeline_results


def main():
    """Main execution function for VESPER dataset pipeline"""
    parser = argparse.ArgumentParser(
        description="VESPER Dataset Analysis and CASAS Comparison Pipeline (Production)"
    )
    parser.add_argument("--base-dir", help="Base directory for VESPER project", default=None)
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = VESPERDatasetPipeline(args.base_dir)
    
    try:
        # Run complete analysis and comparison
        results = pipeline.run_complete_pipeline()
        
        if results['status'] == 'completed':
            print("\n✅ Pipeline completed successfully!")
            print(f"   VESPER datasets analyzed: {results['vesper_datasets']}")
            print(f"   Datasets analyzed: {len(results['analysis_results'])}")
            print(f"   Report: {os.path.basename(results['report_file'])}")
            print(f"   JSON results: {os.path.basename(results['json_file'])}")
            if results.get('plot_files'):
                print(f"   Graphs generated: {len(results['plot_files'])}")
                for plot in results['plot_files']:
                    print(f"      - {os.path.basename(plot)}")
        elif results['status'] == 'no_data':
            print("\n⚠️  No VESPER datasets found to analyze")
            print("   Run BGE navigation first: python blender/llm_bge_navigation.py")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
