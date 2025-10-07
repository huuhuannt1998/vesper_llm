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
        
        # Find CASAS motion sensor files
        casas_files = list(self.vesper_datasets_dir.glob("vesper_casas_*.txt"))
        
        # Find VLM metrics files
        metrics_files = list(self.vesper_datasets_dir.glob("vesper_metrics_*.json"))
        
        print(f"\n📊 Found {len(casas_files)} CASAS sensor files")
        for f in casas_files:
            print(f"   - {f.name}")
        
        print(f"\n📊 Found {len(metrics_files)} VLM metrics files")
        for f in metrics_files:
            print(f"   - {f.name}")
        
        return {
            'casas_files': casas_files,
            'metrics_files': metrics_files
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
        
        if not datasets['casas_files']:
            print("\n⚠️ No VESPER datasets found!")
            print(f"   Expected location: {self.vesper_datasets_dir}")
            print("   Run BGE navigation first to generate datasets.")
            return {'status': 'no_data'}
        
        # Step 2: Validate CASAS files
        print("\n" + "="*80)
        print("VALIDATING CASAS FORMAT")
        print("="*80)
        
        validation_results = []
        for casas_file in datasets['casas_files']:
            result = self.validate_casas_format(casas_file)
            validation_results.append(result)
            if result['valid']:
                print(f"\n✅ {result['file']}")
                print(f"   Events: {result['events']}")
                print(f"   Sensors: {', '.join(result['sensors'])}")
            else:
                print(f"\n❌ {casas_file.name}: {result.get('error', 'Unknown error')}")
        
        # Step 3: Compare with ground truth
        comparison_results = []
        for casas_file in datasets['casas_files']:
            result = self.compare_with_ground_truth(casas_file)
            comparison_results.append(result)
        
        # Step 4: Generate report
        print("\n" + "="*80)
        print("GENERATING COMPARISON REPORT")
        print("="*80)
        
        report_file = self.generate_comparison_report(comparison_results)
        print(f"\n✅ Report saved: {os.path.basename(report_file)}")
        
        # Step 5: Generate visualizations
        plot_files = self.create_visualizations(comparison_results)
        
        # Compile final results
        pipeline_results = {
            'vesper_datasets': len(datasets['casas_files']),
            'metrics_files': len(datasets['metrics_files']),
            'validations': validation_results,
            'comparisons': comparison_results,
            'report_file': str(report_file),
            'plot_files': plot_files,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        # Save pipeline results JSON
        results_json = self.comparison_results_dir / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_json, 'w') as f:
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
            print(f"   Comparisons performed: {len(results['comparisons'])}")
            print(f"   Report: {os.path.basename(results['report_file'])}")
            print(f"   Graphs generated: {len(results.get('plot_files', []))}")
            if results.get('plot_files'):
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
