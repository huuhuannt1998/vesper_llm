#!/usr/bin/env python3
"""
Advanced Statistical Comparison for VESPER vs CASAS Datasets
Provides comprehensive statistical analysis for research publications

Includes:
- Temporal analysis (event timing, sequences)
- Spatial analysis (room transitions, coverage)
- Behavioral metrics (activity patterns, task completion)
- Statistical tests (correlation, significance)
- Performance benchmarks
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.spatial.distance import jensenshannon
import warnings
warnings.filterwarnings('ignore')

# Set publication-quality plot style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")


class AdvancedStatisticalComparison:
    """
    Advanced statistical comparison between VESPER and CASAS datasets
    Generates research-quality metrics and visualizations
    """
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = Path(r"c:\Users\hbui11\Desktop\vesper_llm")
        else:
            self.base_dir = Path(base_dir)
        
        self.vesper_dir = self.base_dir / "casas_testbed" / "vesper_datasets"
        self.casas_dir = self.base_dir / "casas_testbed" / "data" / "casas_ground_truth"
        self.results_dir = self.base_dir / "casas_testbed" / "data" / "statistical_analysis"
        
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        print("="*80)
        print("ADVANCED STATISTICAL COMPARISON PIPELINE")
        print("="*80)
        print(f"[DATA] VESPER datasets: {self.vesper_dir}")
        print(f"[DATA] CASAS ground truth: {self.casas_dir}")
        print(f"[DATA] Statistical output: {self.results_dir}")
    
    def load_vesper_datasets(self):
        """Load all VESPER datasets"""
        print("\n Loading VESPER datasets...")
        
        datasets = []
        metrics_files = list(self.vesper_dir.glob("vesper_metrics_p*.json"))
        
        for file in metrics_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Extract key information
                    dataset = {
                        'filename': file.name,
                        'session_id': data.get('session_id'),
                        'participant': file.name.split('_')[2],  # p001, p002, etc.
                        'tasks_completed': data.get('tasks_completed', 0),
                        'tasks_failed': data.get('tasks_failed', 0),
                        'total_steps': data.get('total_steps', 0),
                        'sensor_events': data.get('virtual_sensor_events', []),
                        'task_details': data.get('task_details', []),
                        'llm_calls': data.get('total_llm_calls', 0),
                        'screenshots': data.get('total_screenshots', 0)
                    }
                    datasets.append(dataset)
                    
            except Exception as e:
                print(f"   Error loading {file.name}: {e}")
        
        print(f"   Loaded {len(datasets)} VESPER datasets")
        return datasets
    
    def load_casas_datasets(self):
        """Load CASAS ground truth datasets"""
        print("\n Loading CASAS ground truth datasets...")
        
        datasets = []
        
        for category in ['adl_noerror', 'adl_error']:
            category_dir = self.casas_dir / category
            if not category_dir.exists():
                continue
            
            csv_files = list(category_dir.glob("*.csv"))
            
            for file in csv_files:
                try:
                    events = []
                    with open(file, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            events.append({
                                'timestamp': f"{row['date']} {row['time']}",
                                'sensor': row['sensor'],
                                'message': row['message']
                            })
                    
                    # Extract participant and task from filename (e.g., p01.t1.csv)
                    name_parts = file.stem.split('.')
                    participant = name_parts[0]  # p01, p02, etc.
                    task = name_parts[1] if len(name_parts) > 1 else 't1'
                    
                    dataset = {
                        'filename': file.name,
                        'participant': participant,
                        'task': task,
                        'category': category,
                        'events': events,
                        'num_events': len(events)
                    }
                    datasets.append(dataset)
                    
                except Exception as e:
                    print(f"   Error loading {file.name}: {e}")
        
        print(f"   Loaded {len(datasets)} CASAS datasets")
        return datasets
    
    def compute_temporal_metrics(self, vesper_datasets, casas_datasets):
        """Compute temporal analysis metrics"""
        print("\n Computing temporal metrics...")
        
        metrics = {
            'vesper': {},
            'casas': {},
            'comparison': {}
        }
        
        # VESPER temporal metrics
        vesper_event_counts = [len(d['sensor_events']) for d in vesper_datasets]
        vesper_durations = []
        vesper_event_rates = []
        
        for dataset in vesper_datasets:
            if dataset['sensor_events']:
                timestamps = [e['timestamp'] for e in dataset['sensor_events']]
                if len(timestamps) > 1:
                    duration = max(timestamps) - min(timestamps)
                    vesper_durations.append(duration)
                    vesper_event_rates.append(len(timestamps) / (duration + 1))  # events per second
        
        metrics['vesper'] = {
            'total_datasets': len(vesper_datasets),
            'total_events': sum(vesper_event_counts),
            'avg_events_per_dataset': np.mean(vesper_event_counts) if vesper_event_counts else 0,
            'std_events_per_dataset': np.std(vesper_event_counts) if vesper_event_counts else 0,
            'median_events': np.median(vesper_event_counts) if vesper_event_counts else 0,
            'avg_duration_seconds': np.mean(vesper_durations) if vesper_durations else 0,
            'avg_event_rate': np.mean(vesper_event_rates) if vesper_event_rates else 0
        }
        
        # CASAS temporal metrics
        casas_event_counts = [d['num_events'] for d in casas_datasets]
        
        metrics['casas'] = {
            'total_datasets': len(casas_datasets),
            'total_events': sum(casas_event_counts),
            'avg_events_per_dataset': np.mean(casas_event_counts) if casas_event_counts else 0,
            'std_events_per_dataset': np.std(casas_event_counts) if casas_event_counts else 0,
            'median_events': np.median(casas_event_counts) if casas_event_counts else 0
        }
        
        # Statistical comparison
        if vesper_event_counts and casas_event_counts:
            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(vesper_event_counts, casas_event_counts)
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt((np.std(vesper_event_counts)**2 + np.std(casas_event_counts)**2) / 2)
            cohens_d = (np.mean(vesper_event_counts) - np.mean(casas_event_counts)) / pooled_std if pooled_std > 0 else 0
            
            metrics['comparison'] = {
                't_statistic': t_stat,
                'p_value': p_value,
                'cohens_d': cohens_d,
                'significant': p_value < 0.05
            }
        
        print(f"   VESPER: {metrics['vesper']['avg_events_per_dataset']:.1f}  {metrics['vesper']['std_events_per_dataset']:.1f} events/dataset")
        print(f"   CASAS: {metrics['casas']['avg_events_per_dataset']:.1f}  {metrics['casas']['std_events_per_dataset']:.1f} events/dataset")
        
        return metrics
    
    def compute_sensor_distribution(self, vesper_datasets, casas_datasets):
        """Analyze sensor usage distribution"""
        print("\n Computing sensor distribution metrics...")
        
        # VESPER sensor distribution
        vesper_sensor_counts = Counter()
        for dataset in vesper_datasets:
            for event in dataset['sensor_events']:
                vesper_sensor_counts[event['sensor_id']] += 1
        
        # CASAS sensor distribution
        casas_sensor_counts = Counter()
        for dataset in casas_datasets:
            for event in dataset['events']:
                casas_sensor_counts[event['sensor']] += 1
        
        # Normalize to probability distributions
        vesper_total = sum(vesper_sensor_counts.values())
        casas_total = sum(casas_sensor_counts.values())
        
        vesper_dist = {k: v/vesper_total for k, v in vesper_sensor_counts.items()} if vesper_total > 0 else {}
        casas_dist = {k: v/casas_total for k, v in casas_sensor_counts.items()} if casas_total > 0 else {}
        
        # Get all unique sensors
        all_sensors = sorted(set(list(vesper_sensor_counts.keys()) + list(casas_sensor_counts.keys())))
        
        # Create aligned probability vectors for Jensen-Shannon divergence
        vesper_probs = np.array([vesper_dist.get(s, 0) for s in all_sensors])
        casas_probs = np.array([casas_dist.get(s, 0) for s in all_sensors])
        
        # Compute Jensen-Shannon divergence (0 = identical, 1 = completely different)
        js_divergence = jensenshannon(vesper_probs, casas_probs) if len(vesper_probs) > 0 else 1.0
        
        metrics = {
            'vesper_sensors': dict(vesper_sensor_counts),
            'casas_sensors': dict(casas_sensor_counts),
            'vesper_distribution': vesper_dist,
            'casas_distribution': casas_dist,
            'js_divergence': js_divergence,
            'similarity_score': 1 - js_divergence,  # Higher = more similar
            'common_sensors': set(vesper_sensor_counts.keys()) & set(casas_sensor_counts.keys())
        }
        
        print(f"   VESPER uses {len(vesper_sensor_counts)} unique sensors")
        print(f"   CASAS uses {len(casas_sensor_counts)} unique sensors")
        print(f"   Similarity score: {metrics['similarity_score']:.3f} (1.0 = perfect match)")
        
        return metrics
    
    def compute_task_performance_metrics(self, vesper_datasets):
        """Analyze task performance metrics"""
        print("\n Computing task performance metrics...")
        
        task_metrics = defaultdict(lambda: {
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'avg_steps': [],
            'avg_duration': [],
            'avg_llm_calls': []
        })
        
        for dataset in vesper_datasets:
            for task in dataset['task_details']:
                task_name = task['task_name']
                task_metrics[task_name]['attempts'] += 1
                
                if task['success']:
                    task_metrics[task_name]['successes'] += 1
                else:
                    task_metrics[task_name]['failures'] += 1
                
                # Handle None values
                steps = task.get('steps_taken', 0)
                duration = task.get('completion_time', 0)
                llm_calls = task.get('llm_calls', 0)
                
                if steps is not None:
                    task_metrics[task_name]['avg_steps'].append(steps)
                if duration is not None:
                    task_metrics[task_name]['avg_duration'].append(duration)
                if llm_calls is not None:
                    task_metrics[task_name]['avg_llm_calls'].append(llm_calls)
        
        # Compute aggregated metrics
        performance_summary = {}
        for task_name, metrics in task_metrics.items():
            success_rate = metrics['successes'] / metrics['attempts'] if metrics['attempts'] > 0 else 0
            
            performance_summary[task_name] = {
                'total_attempts': metrics['attempts'],
                'success_rate': success_rate,
                'avg_steps': np.mean(metrics['avg_steps']) if metrics['avg_steps'] else 0,
                'std_steps': np.std(metrics['avg_steps']) if metrics['avg_steps'] else 0,
                'avg_duration': np.mean(metrics['avg_duration']) if metrics['avg_duration'] else 0,
                'std_duration': np.std(metrics['avg_duration']) if metrics['avg_duration'] else 0,
                'avg_llm_calls': np.mean(metrics['avg_llm_calls']) if metrics['avg_llm_calls'] else 0
            }
        
        # Overall performance
        total_attempts = sum(m['attempts'] for m in task_metrics.values())
        total_successes = sum(m['successes'] for m in task_metrics.values())
        overall_success_rate = total_successes / total_attempts if total_attempts > 0 else 0
        
        print(f"   Overall success rate: {overall_success_rate:.1%}")
        print(f"   Total task attempts: {total_attempts}")
        
        return {
            'by_task': performance_summary,
            'overall_success_rate': overall_success_rate,
            'total_attempts': total_attempts,
            'total_successes': total_successes
        }
    
    def compute_sequence_similarity(self, vesper_datasets, casas_datasets, max_samples=10):
        """Compute sequence similarity between VESPER and CASAS"""
        print("\n Computing sequence similarity...")
        
        similarities = []
        
        # Sample datasets for pairwise comparison
        vesper_sample = vesper_datasets[:min(len(vesper_datasets), max_samples)]
        casas_sample = casas_datasets[:min(len(casas_datasets), max_samples)]
        
        for v_dataset in vesper_sample:
            v_sequence = [e['sensor_id'] for e in v_dataset['sensor_events']]
            
            for c_dataset in casas_sample:
                c_sequence = [e['sensor'] for e in c_dataset['events']]
                
                # Longest Common Subsequence (LCS) ratio
                lcs_length = self._lcs_length(v_sequence, c_sequence)
                lcs_ratio = 2 * lcs_length / (len(v_sequence) + len(c_sequence)) if (len(v_sequence) + len(c_sequence)) > 0 else 0
                
                similarities.append({
                    'vesper_file': v_dataset['filename'],
                    'casas_file': c_dataset['filename'],
                    'lcs_ratio': lcs_ratio
                })
        
        avg_similarity = np.mean([s['lcs_ratio'] for s in similarities]) if similarities else 0
        
        print(f"   Average sequence similarity: {avg_similarity:.3f}")
        
        return {
            'pairwise_similarities': similarities,
            'average_similarity': avg_similarity,
            'max_similarity': max([s['lcs_ratio'] for s in similarities]) if similarities else 0,
            'min_similarity': min([s['lcs_ratio'] for s in similarities]) if similarities else 0
        }
    
    def _lcs_length(self, seq1, seq2):
        """Compute Longest Common Subsequence length"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def generate_statistical_report(self, all_metrics):
        """Generate comprehensive statistical report"""
        print("\n Generating statistical report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"statistical_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Advanced Statistical Comparison: VESPER vs CASAS\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write("This report provides a comprehensive statistical comparison between VESPER-generated ")
            f.write("datasets and CASAS ground truth datasets for activity recognition research.\n\n")
            
            # Temporal Metrics
            if 'temporal' in all_metrics:
                f.write("## 1. Temporal Analysis\n\n")
                f.write("### Dataset Statistics\n\n")
                f.write("| Metric | VESPER | CASAS |\n")
                f.write("|--------|--------|-------|\n")
                f.write(f"| Total Datasets | {all_metrics['temporal']['vesper']['total_datasets']} | {all_metrics['temporal']['casas']['total_datasets']} |\n")
                f.write(f"| Total Events | {all_metrics['temporal']['vesper']['total_events']} | {all_metrics['temporal']['casas']['total_events']} |\n")
                f.write(f"| Avg Events/Dataset | {all_metrics['temporal']['vesper']['avg_events_per_dataset']:.1f}  {all_metrics['temporal']['vesper']['std_events_per_dataset']:.1f} | {all_metrics['temporal']['casas']['avg_events_per_dataset']:.1f}  {all_metrics['temporal']['casas']['std_events_per_dataset']:.1f} |\n")
                f.write(f"| Median Events | {all_metrics['temporal']['vesper']['median_events']:.0f} | {all_metrics['temporal']['casas']['median_events']:.0f} |\n")
                
                if 'comparison' in all_metrics['temporal']:
                    f.write("\n### Statistical Significance\n\n")
                    f.write(f"- **t-statistic**: {all_metrics['temporal']['comparison']['t_statistic']:.3f}\n")
                    f.write(f"- **p-value**: {all_metrics['temporal']['comparison']['p_value']:.4f}\n")
                    f.write(f"- **Effect size (Cohen's d)**: {all_metrics['temporal']['comparison']['cohens_d']:.3f}\n")
                    
                    if all_metrics['temporal']['comparison']['significant']:
                        f.write(f"- **Result**: Statistically significant difference (p < 0.05)\n\n")
                    else:
                        f.write(f"- **Result**: No statistically significant difference (p  0.05)\n\n")
            
            # Sensor Distribution
            if 'sensor_distribution' in all_metrics:
                f.write("## 2. Sensor Distribution Analysis\n\n")
                f.write(f"- **VESPER Unique Sensors**: {len(all_metrics['sensor_distribution']['vesper_sensors'])}\n")
                f.write(f"- **CASAS Unique Sensors**: {len(all_metrics['sensor_distribution']['casas_sensors'])}\n")
                f.write(f"- **Common Sensors**: {len(all_metrics['sensor_distribution']['common_sensors'])}\n")
                f.write(f"- **Jensen-Shannon Divergence**: {all_metrics['sensor_distribution']['js_divergence']:.3f}\n")
                f.write(f"- **Distribution Similarity**: {all_metrics['sensor_distribution']['similarity_score']:.3f} (1.0 = perfect match)\n\n")
                
                f.write("### Interpretation\n\n")
                similarity = all_metrics['sensor_distribution']['similarity_score']
                if similarity > 0.8:
                    f.write("- **Excellent similarity**: VESPER sensor usage closely matches CASAS patterns\n\n")
                elif similarity > 0.6:
                    f.write("- **Good similarity**: VESPER captures major CASAS behavioral patterns\n\n")
                elif similarity > 0.4:
                    f.write("- **Moderate similarity**: Some differences in sensor usage patterns\n\n")
                else:
                    f.write("- **Low similarity**: Significant differences in sensor usage patterns\n\n")
            
            # Task Performance
            if 'task_performance' in all_metrics:
                f.write("## 3. Task Performance Analysis\n\n")
                f.write(f"- **Overall Success Rate**: {all_metrics['task_performance']['overall_success_rate']:.1%}\n")
                f.write(f"- **Total Attempts**: {all_metrics['task_performance']['total_attempts']}\n")
                f.write(f"- **Successful Completions**: {all_metrics['task_performance']['total_successes']}\n\n")
                
                f.write("### Per-Task Performance\n\n")
                f.write("| Task | Attempts | Success Rate | Avg Steps | Avg Duration (s) | Avg LLM Calls |\n")
                f.write("|------|----------|--------------|-----------|------------------|---------------|\n")
                
                for task_name, metrics in all_metrics['task_performance']['by_task'].items():
                    f.write(f"| {task_name} | {metrics['total_attempts']} | {metrics['success_rate']:.1%} | ")
                    f.write(f"{metrics['avg_steps']:.1f}  {metrics['std_steps']:.1f} | ")
                    f.write(f"{metrics['avg_duration']:.1f}  {metrics['std_duration']:.1f} | ")
                    f.write(f"{metrics['avg_llm_calls']:.1f} |\n")
                f.write("\n")
            
            # Sequence Similarity
            if 'sequence_similarity' in all_metrics:
                f.write("## 4. Sequence Similarity Analysis\n\n")
                f.write(f"- **Average LCS Ratio**: {all_metrics['sequence_similarity']['average_similarity']:.3f}\n")
                f.write(f"- **Maximum Similarity**: {all_metrics['sequence_similarity']['max_similarity']:.3f}\n")
                f.write(f"- **Minimum Similarity**: {all_metrics['sequence_similarity']['min_similarity']:.3f}\n\n")
                
                f.write("**Note**: LCS (Longest Common Subsequence) ratio measures sequential pattern similarity.\n")
                f.write("Values closer to 1.0 indicate more similar event sequences.\n\n")
            
            # Conclusions
            f.write("## 5. Conclusions\n\n")
            f.write("### Key Findings\n\n")
            
            if 'temporal' in all_metrics and 'comparison' in all_metrics['temporal']:
                if all_metrics['temporal']['comparison']['significant']:
                    f.write("1. **Event Count**: VESPER and CASAS datasets show statistically significant differences in event counts\n")
                else:
                    f.write("1. **Event Count**: VESPER and CASAS datasets show comparable event counts (no significant difference)\n")
            
            if 'sensor_distribution' in all_metrics:
                similarity = all_metrics['sensor_distribution']['similarity_score']
                f.write(f"2. **Sensor Usage**: Distribution similarity of {similarity:.3f} indicates ")
                if similarity > 0.6:
                    f.write("good alignment with real-world patterns\n")
                else:
                    f.write("room for improvement in sensor coverage\n")
            
            if 'task_performance' in all_metrics:
                success_rate = all_metrics['task_performance']['overall_success_rate']
                f.write(f"3. **Task Success**: {success_rate:.1%} overall success rate demonstrates ")
                if success_rate > 0.7:
                    f.write("strong task completion capabilities\n")
                else:
                    f.write("opportunities for navigation improvement\n")
            
            f.write("\n### Research Implications\n\n")
            f.write("This analysis provides quantitative evidence for the validity of VESPER-generated datasets ")
            f.write("as synthetic training data for activity recognition systems. The statistical metrics presented ")
            f.write("support reproducible research and enable fair comparison with other synthetic data generation approaches.\n\n")
            
            f.write("---\n\n")
            f.write("*Report generated by VESPER Advanced Statistical Comparison Pipeline*\n")
        
        print(f"   Report saved: {report_file.name}")
        return report_file
    
    def create_publication_figures(self, all_metrics):
        """Create publication-quality figures"""
        print("\n Creating publication-quality figures...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        figures = []
        
        # Set publication style
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'serif'
        
        # Figure 1: Sensor Distribution Comparison
        if 'sensor_distribution' in all_metrics:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # VESPER distribution
            vesper_sensors = all_metrics['sensor_distribution']['vesper_sensors']
            if vesper_sensors:
                sensors = list(vesper_sensors.keys())
                counts = list(vesper_sensors.values())
                ax1.bar(range(len(sensors)), counts, color='#2196F3', alpha=0.8, edgecolor='black')
                ax1.set_xticks(range(len(sensors)))
                ax1.set_xticklabels(sensors, rotation=45, ha='right')
                ax1.set_ylabel('Event Count')
                ax1.set_title('VESPER Sensor Distribution', fontweight='bold')
                ax1.grid(axis='y', alpha=0.3, linestyle='--')
            
            # CASAS distribution (top sensors)
            casas_sensors = all_metrics['sensor_distribution']['casas_sensors']
            if casas_sensors:
                # Show top 15 most frequent sensors
                top_sensors = dict(sorted(casas_sensors.items(), key=lambda x: x[1], reverse=True)[:15])
                sensors = list(top_sensors.keys())
                counts = list(top_sensors.values())
                ax2.bar(range(len(sensors)), counts, color='#FF9800', alpha=0.8, edgecolor='black')
                ax2.set_xticks(range(len(sensors)))
                ax2.set_xticklabels(sensors, rotation=45, ha='right')
                ax2.set_ylabel('Event Count')
                ax2.set_title('CASAS Sensor Distribution (Top 15)', fontweight='bold')
                ax2.grid(axis='y', alpha=0.3, linestyle='--')
            
            plt.tight_layout()
            fig_file = self.results_dir / f"fig1_sensor_distribution_{timestamp}.png"
            plt.savefig(fig_file, dpi=300, bbox_inches='tight')
            plt.close()
            figures.append(fig_file)
            print(f"   Created: {fig_file.name}")
        
        # Figure 2: Task Performance Summary
        if 'task_performance' in all_metrics:
            task_data = all_metrics['task_performance']['by_task']
            if task_data:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                tasks = list(task_data.keys())
                success_rates = [task_data[t]['success_rate'] for t in tasks]
                avg_steps = [task_data[t]['avg_steps'] for t in tasks]
                
                # Success rates
                colors = ['#4CAF50' if sr > 0.7 else '#FFC107' if sr > 0.4 else '#F44336' for sr in success_rates]
                ax1.barh(tasks, success_rates, color=colors, alpha=0.8, edgecolor='black')
                ax1.set_xlabel('Success Rate')
                ax1.set_xlim(0, 1)
                ax1.set_title('Task Success Rates', fontweight='bold')
                ax1.grid(axis='x', alpha=0.3, linestyle='--')
                
                # Average steps
                ax2.barh(tasks, avg_steps, color='#9C27B0', alpha=0.8, edgecolor='black')
                ax2.set_xlabel('Average Steps')
                ax2.set_title('Task Complexity (Steps Required)', fontweight='bold')
                ax2.grid(axis='x', alpha=0.3, linestyle='--')
                
                plt.tight_layout()
                fig_file = self.results_dir / f"fig2_task_performance_{timestamp}.png"
                plt.savefig(fig_file, dpi=300, bbox_inches='tight')
                plt.close()
                figures.append(fig_file)
                print(f"   Created: {fig_file.name}")
        
        # Figure 3: Event Count Distribution
        if 'temporal' in all_metrics:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            vesper_avg = all_metrics['temporal']['vesper']['avg_events_per_dataset']
            vesper_std = all_metrics['temporal']['vesper']['std_events_per_dataset']
            casas_avg = all_metrics['temporal']['casas']['avg_events_per_dataset']
            casas_std = all_metrics['temporal']['casas']['std_events_per_dataset']
            
            categories = ['VESPER', 'CASAS']
            means = [vesper_avg, casas_avg]
            stds = [vesper_std, casas_std]
            
            x_pos = np.arange(len(categories))
            ax.bar(x_pos, means, yerr=stds, capsize=10, color=['#2196F3', '#FF9800'], 
                   alpha=0.8, edgecolor='black', error_kw={'linewidth': 2})
            ax.set_ylabel('Events per Dataset')
            ax.set_title('Average Event Count Comparison', fontweight='bold')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(categories)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add significance marker if applicable
            if 'comparison' in all_metrics['temporal'] and all_metrics['temporal']['comparison']['significant']:
                y_max = max(means) + max(stds) + 10
                ax.plot([0, 1], [y_max, y_max], 'k-', linewidth=1.5)
                ax.text(0.5, y_max + 5, '***' if all_metrics['temporal']['comparison']['p_value'] < 0.001 else '**' if all_metrics['temporal']['comparison']['p_value'] < 0.01 else '*',
                       ha='center', va='bottom', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            fig_file = self.results_dir / f"fig3_event_count_comparison_{timestamp}.png"
            plt.savefig(fig_file, dpi=300, bbox_inches='tight')
            plt.close()
            figures.append(fig_file)
            print(f"   Created: {fig_file.name}")
        
        print(f"\n   Total figures created: {len(figures)}")
        return figures
    
    def export_statistical_data(self, all_metrics):
        """Export statistical data to CSV for further analysis"""
        print("\n Exporting statistical data...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export task performance data
        if 'task_performance' in all_metrics:
            task_df = pd.DataFrame([
                {
                    'Task': task_name,
                    'Attempts': metrics['total_attempts'],
                    'Success_Rate': metrics['success_rate'],
                    'Avg_Steps': metrics['avg_steps'],
                    'Std_Steps': metrics['std_steps'],
                    'Avg_Duration': metrics['avg_duration'],
                    'Std_Duration': metrics['std_duration'],
                    'Avg_LLM_Calls': metrics['avg_llm_calls']
                }
                for task_name, metrics in all_metrics['task_performance']['by_task'].items()
            ])
            
            csv_file = self.results_dir / f"task_performance_{timestamp}.csv"
            task_df.to_csv(csv_file, index=False)
            print(f"   Exported: {csv_file.name}")
        
        # Export temporal comparison
        if 'temporal' in all_metrics:
            temporal_data = {
                'Metric': ['Total Datasets', 'Total Events', 'Avg Events', 'Std Events', 'Median Events'],
                'VESPER': [
                    all_metrics['temporal']['vesper']['total_datasets'],
                    all_metrics['temporal']['vesper']['total_events'],
                    all_metrics['temporal']['vesper']['avg_events_per_dataset'],
                    all_metrics['temporal']['vesper']['std_events_per_dataset'],
                    all_metrics['temporal']['vesper']['median_events']
                ],
                'CASAS': [
                    all_metrics['temporal']['casas']['total_datasets'],
                    all_metrics['temporal']['casas']['total_events'],
                    all_metrics['temporal']['casas']['avg_events_per_dataset'],
                    all_metrics['temporal']['casas']['std_events_per_dataset'],
                    all_metrics['temporal']['casas']['median_events']
                ]
            }
            
            temporal_df = pd.DataFrame(temporal_data)
            csv_file = self.results_dir / f"temporal_comparison_{timestamp}.csv"
            temporal_df.to_csv(csv_file, index=False)
            print(f"   Exported: {csv_file.name}")
    
    def run_complete_analysis(self):
        """Run complete statistical analysis pipeline"""
        print("\n" + "="*80)
        print("RUNNING COMPLETE STATISTICAL ANALYSIS")
        print("="*80)
        
        # Load datasets
        vesper_datasets = self.load_vesper_datasets()
        casas_datasets = self.load_casas_datasets()
        
        if not vesper_datasets:
            print("\n No VESPER datasets found!")
            return
        
        if not casas_datasets:
            print("\n No CASAS datasets found!")
            return
        
        # Compute all metrics
        all_metrics = {}
        
        all_metrics['temporal'] = self.compute_temporal_metrics(vesper_datasets, casas_datasets)
        all_metrics['sensor_distribution'] = self.compute_sensor_distribution(vesper_datasets, casas_datasets)
        all_metrics['task_performance'] = self.compute_task_performance_metrics(vesper_datasets)
        all_metrics['sequence_similarity'] = self.compute_sequence_similarity(vesper_datasets, casas_datasets)
        
        # Generate outputs
        report_file = self.generate_statistical_report(all_metrics)
        figures = self.create_publication_figures(all_metrics)
        self.export_statistical_data(all_metrics)
        
        # Save complete metrics as JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = self.results_dir / f"complete_metrics_{timestamp}.json"
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(convert_numpy(all_metrics), f, indent=2)
        
        print(f"\n Complete metrics saved: {json_file.name}")
        
        print("\n" + "="*80)
        print("STATISTICAL ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n All results saved to: {self.results_dir}")
        print(f" Statistical report: {report_file.name}")
        print(f" Figures generated: {len(figures)}")
        
        return all_metrics


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Advanced Statistical Comparison for VESPER vs CASAS"
    )
    parser.add_argument("--base-dir", help="Base directory", default=None)
    args = parser.parse_args()
    
    analyzer = AdvancedStatisticalComparison(args.base_dir)
    results = analyzer.run_complete_analysis()
    
    print("\n Analysis complete!")


if __name__ == "__main__":
    main()
