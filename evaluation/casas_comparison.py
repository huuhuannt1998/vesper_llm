#!/usr/bin/env python3
"""
CASAS Dataset Comparison Tool

Compares VLM-generated datasets with CASAS ground truth for behavioral analysis.
Provides similarity scoring and pattern analysis.
"""

import csv
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import logging


class CASASComparator:
    """Compares VLM datasets with CASAS ground truth"""
    
    def __init__(self, vlm_dir: str, casas_dir: str, output_dir: str):
        self.vlm_dir = vlm_dir
        self.casas_dir = casas_dir
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_casas_file(self, filepath: str) -> pd.DataFrame:
        """Load and parse CASAS CSV file"""
        try:
            df = pd.read_csv(filepath)
            # Handle different datetime formats in CASAS files
            try:
                df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
            except:
                # Try alternative format for mixed datetime formats
                df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'], format='mixed', errors='coerce')
            
            # Remove rows with invalid datetime
            df = df.dropna(subset=['datetime'])
            return df
        except Exception as e:
            self.logger.error(f"Error loading CASAS file {filepath}: {e}")
            return pd.DataFrame()
    
    def load_vlm_file(self, filepath: str) -> pd.DataFrame:
        """Load and parse VLM CSV file"""
        try:
            df = pd.read_csv(filepath)
            df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
            return df
        except Exception as e:
            self.logger.error(f"Error loading VLM file {filepath}: {e}")
            return pd.DataFrame()
    
    def extract_features(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract behavioral features from dataset"""
        features = {}
        
        # Temporal features
        features['duration'] = (df['datetime'].max() - df['datetime'].min()).total_seconds()
        features['event_count'] = len(df)
        features['events_per_minute'] = features['event_count'] / (features['duration'] / 60) if features['duration'] > 0 else 0
        
        # Sensor activity patterns
        sensor_counts = df['sensor'].value_counts()
        features['unique_sensors'] = len(sensor_counts)
        features['most_active_sensor'] = sensor_counts.index[0] if len(sensor_counts) > 0 else None
        features['sensor_distribution'] = sensor_counts.to_dict()
        
        # Room transition patterns
        room_sensors = [s for s in df['sensor'].unique() if s.startswith('M')]
        room_transitions = self._count_transitions(df, room_sensors)
        features['room_transitions'] = room_transitions
        
        # Activity patterns (ON/OFF sequences)
        on_events = df[df['message'] == 'ON']
        off_events = df[df['message'] == 'OFF']
        features['on_off_ratio'] = len(on_events) / len(off_events) if len(off_events) > 0 else float('inf')
        
        # Time distribution
        df['hour'] = df['datetime'].dt.hour
        hourly_dist = df['hour'].value_counts().sort_index()
        features['hourly_distribution'] = hourly_dist.to_dict()
        
        return features
    
    def _count_transitions(self, df: pd.DataFrame, sensors: List[str]) -> int:
        """Count room-to-room transitions"""
        transitions = 0
        current_room = None
        
        for _, row in df.iterrows():
            if row['sensor'] in sensors and row['message'] == 'ON':
                if current_room and current_room != row['sensor']:
                    transitions += 1
                current_room = row['sensor']
        
        return transitions
    
    def calculate_similarity_score(self, vlm_features: Dict, casas_features: Dict) -> Dict[str, float]:
        """Calculate similarity scores between VLM and CASAS features"""
        scores = {}
        
        # Temporal similarity
        duration_diff = abs(vlm_features['duration'] - casas_features['duration'])
        max_duration = max(vlm_features['duration'], casas_features['duration'])
        scores['temporal_similarity'] = 1 - (duration_diff / max_duration) if max_duration > 0 else 1
        
        # Event count similarity
        event_diff = abs(vlm_features['event_count'] - casas_features['event_count'])
        max_events = max(vlm_features['event_count'], casas_features['event_count'])
        scores['event_count_similarity'] = 1 - (event_diff / max_events) if max_events > 0 else 1
        
        # Sensor usage similarity
        vlm_sensors = set(vlm_features['sensor_distribution'].keys())
        casas_sensors = set(casas_features['sensor_distribution'].keys())
        sensor_overlap = len(vlm_sensors.intersection(casas_sensors))
        sensor_union = len(vlm_sensors.union(casas_sensors))
        scores['sensor_similarity'] = sensor_overlap / sensor_union if sensor_union > 0 else 0
        
        # Room transition similarity
        transition_diff = abs(vlm_features['room_transitions'] - casas_features['room_transitions'])
        max_transitions = max(vlm_features['room_transitions'], casas_features['room_transitions'])
        scores['transition_similarity'] = 1 - (transition_diff / max_transitions) if max_transitions > 0 else 1
        
        # Hourly pattern similarity (cosine similarity)
        vlm_hourly = [vlm_features['hourly_distribution'].get(h, 0) for h in range(24)]
        casas_hourly = [casas_features['hourly_distribution'].get(h, 0) for h in range(24)]
        
        vlm_norm = np.linalg.norm(vlm_hourly)
        casas_norm = np.linalg.norm(casas_hourly)
        
        if vlm_norm > 0 and casas_norm > 0:
            scores['hourly_pattern_similarity'] = np.dot(vlm_hourly, casas_hourly) / (vlm_norm * casas_norm)
        else:
            scores['hourly_pattern_similarity'] = 0
        
        # Overall similarity score (weighted average)
        weights = {
            'temporal_similarity': 0.2,
            'event_count_similarity': 0.2,
            'sensor_similarity': 0.25,
            'transition_similarity': 0.2,
            'hourly_pattern_similarity': 0.15
        }
        
        scores['overall_similarity'] = sum(scores[k] * weights[k] for k in weights.keys())
        
        return scores
    
    def compare_datasets(self, vlm_file: str, casas_file: str) -> Dict[str, Any]:
        """Compare a VLM dataset with a CASAS ground truth dataset"""
        # Load datasets
        vlm_df = self.load_vlm_file(vlm_file)
        casas_df = self.load_casas_file(casas_file)
        
        if vlm_df.empty or casas_df.empty:
            return None
        
        # Extract features
        vlm_features = self.extract_features(vlm_df)
        casas_features = self.extract_features(casas_df)
        
        # Calculate similarity scores
        similarity_scores = self.calculate_similarity_score(vlm_features, casas_features)
        
        # Compile comparison result
        comparison = {
            'vlm_file': os.path.basename(vlm_file),
            'casas_file': os.path.basename(casas_file),
            'vlm_features': vlm_features,
            'casas_features': casas_features,
            'similarity_scores': similarity_scores
        }
        
        return comparison
    
    def run_comprehensive_comparison(self) -> List[Dict[str, Any]]:
        """Run comparison between all VLM files and CASAS ground truth files"""
        results = []
        
        # Get all VLM files
        vlm_files = [f for f in os.listdir(self.vlm_dir) if f.endswith('.csv')]
        
        # Get CASAS files from no-error directory only
        casas_noerror_dir = os.path.join(self.casas_dir, "adl_noerror")
        casas_files = []
        if os.path.exists(casas_noerror_dir):
            for file in os.listdir(casas_noerror_dir):
                if file.endswith('.csv'):
                    casas_files.append(os.path.join(casas_noerror_dir, file))
        
        self.logger.info(f"Found {len(vlm_files)} VLM files and {len(casas_files)} CASAS files")
        
        # Compare each VLM file with each CASAS file
        for vlm_file in vlm_files[:5]:  # Limit to first 5 for demo
            vlm_path = os.path.join(self.vlm_dir, vlm_file)
            
            for casas_file in casas_files[:3]:  # Limit to first 3 for demo
                self.logger.info(f"Comparing {vlm_file} with {os.path.basename(casas_file)}")
                
                comparison = self.compare_datasets(vlm_path, casas_file)
                if comparison:
                    results.append(comparison)
        
        return results
    
    def generate_comparison_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate comprehensive comparison report"""
        report_file = os.path.join(self.output_dir, "comparison_report.txt")
        
        with open(report_file, 'w') as f:
            f.write("VLM vs CASAS Dataset Comparison Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Summary statistics
            overall_scores = [r['similarity_scores']['overall_similarity'] for r in results]
            f.write(f"Total Comparisons: {len(results)}\n")
            f.write(f"Average Similarity Score: {np.mean(overall_scores):.3f}\n")
            f.write(f"Best Similarity Score: {np.max(overall_scores):.3f}\n")
            f.write(f"Worst Similarity Score: {np.min(overall_scores):.3f}\n\n")
            
            # Detailed results
            f.write("Detailed Comparison Results:\n")
            f.write("-" * 30 + "\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"\n{i}. {result['vlm_file']} vs {result['casas_file']}\n")
                f.write(f"   Overall Similarity: {result['similarity_scores']['overall_similarity']:.3f}\n")
                f.write(f"   Temporal Similarity: {result['similarity_scores']['temporal_similarity']:.3f}\n")
                f.write(f"   Sensor Similarity: {result['similarity_scores']['sensor_similarity']:.3f}\n")
                f.write(f"   Transition Similarity: {result['similarity_scores']['transition_similarity']:.3f}\n")
                
                # Feature comparison
                vlm_f = result['vlm_features']
                casas_f = result['casas_features']
                f.write(f"   VLM Events: {vlm_f['event_count']}, CASAS Events: {casas_f['event_count']}\n")
                f.write(f"   VLM Duration: {vlm_f['duration']:.1f}s, CASAS Duration: {casas_f['duration']:.1f}s\n")
        
        return report_file
    
    def create_visualization(self, results: List[Dict[str, Any]]) -> str:
        """Create visualization plots for comparison results"""
        # Extract similarity scores
        scores_df = pd.DataFrame([r['similarity_scores'] for r in results])
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('VLM vs CASAS Dataset Comparison Analysis', fontsize=16)
        
        # 1. Overall similarity distribution
        axes[0, 0].hist(scores_df['overall_similarity'], bins=20, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('Overall Similarity Score Distribution')
        axes[0, 0].set_xlabel('Similarity Score')
        axes[0, 0].set_ylabel('Frequency')
        
        # 2. Similarity metrics comparison
        metrics = ['temporal_similarity', 'event_count_similarity', 'sensor_similarity', 'transition_similarity']
        metric_means = [scores_df[m].mean() for m in metrics]
        axes[0, 1].bar(range(len(metrics)), metric_means, color=['red', 'green', 'blue', 'orange'])
        axes[0, 1].set_title('Average Similarity by Metric')
        axes[0, 1].set_xlabel('Metrics')
        axes[0, 1].set_ylabel('Average Score')
        axes[0, 1].set_xticks(range(len(metrics)))
        axes[0, 1].set_xticklabels([m.replace('_', '\n') for m in metrics], rotation=45)
        
        # 3. Feature comparison scatter
        event_counts_vlm = [r['vlm_features']['event_count'] for r in results]
        event_counts_casas = [r['casas_features']['event_count'] for r in results]
        axes[1, 0].scatter(event_counts_casas, event_counts_vlm, alpha=0.6)
        axes[1, 0].plot([0, max(max(event_counts_casas), max(event_counts_vlm))], 
                       [0, max(max(event_counts_casas), max(event_counts_vlm))], 'r--')
        axes[1, 0].set_title('Event Count: VLM vs CASAS')
        axes[1, 0].set_xlabel('CASAS Event Count')
        axes[1, 0].set_ylabel('VLM Event Count')
        
        # 4. Correlation heatmap
        correlation_matrix = scores_df[metrics].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1, 1])
        axes[1, 1].set_title('Similarity Metrics Correlation')
        
        plt.tight_layout()
        
        # Save plot
        plot_file = os.path.join(self.output_dir, "comparison_analysis.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_file


def main():
    """Main execution function"""
    # Set up paths
    base_dir = r"c:\Users\hbui11\Desktop\vesper_llm"
    vlm_dir = os.path.join(base_dir, "casas_testbed", "data", "vesper_generated")
    casas_dir = os.path.join(base_dir, "casas_testbed", "data", "casas_ground_truth")
    output_dir = os.path.join(base_dir, "casas_testbed", "data", "comparison_results")
    
    # Create comparator and run analysis
    comparator = CASASComparator(vlm_dir, casas_dir, output_dir)
    
    print("Running comprehensive dataset comparison...")
    results = comparator.run_comprehensive_comparison()
    
    if results:
        # Generate report
        report_file = comparator.generate_comparison_report(results)
        
        # Create visualizations
        plot_file = comparator.create_visualization(results)
        
        print(f"\nComparison complete!")
        print(f"Results: {len(results)} comparisons")
        print(f"Report: {report_file}")
        print(f"Visualizations: {plot_file}")
    else:
        print("No comparison results generated. Check data availability.")


if __name__ == "__main__":
    main()
