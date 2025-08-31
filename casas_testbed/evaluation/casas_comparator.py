"""
CASAS Data Comparator
====================

Compares VESPER-generated sensor data against CASAS ground truth data.
Provides comprehensive evaluation metrics for VLM performance assessment.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import math

@dataclass
class ComparisonMetrics:
    """Comprehensive comparison metrics"""
    
    # Temporal Metrics
    task_duration_correlation: float
    sensor_timing_accuracy: float
    sequence_alignment_score: float
    
    # Spatial Metrics  
    motion_pattern_similarity: float
    location_visitation_accuracy: float
    path_efficiency_ratio: float
    
    # Behavioral Metrics
    object_interaction_accuracy: float
    task_completion_fidelity: float
    error_detection_capability: float
    
    # Overall Score
    overall_similarity_score: float

class CASASDataComparator:
    """Compares VESPER executions against CASAS ground truth"""
    
    def __init__(self, casas_data_dir: str):
        self.casas_data_dir = casas_data_dir
        self.ground_truth_data: Dict[str, pd.DataFrame] = {}
        self.sensor_locations = self._load_sensor_locations()
        self.load_ground_truth_data()
        
    def load_ground_truth_data(self):
        """Load all CASAS ground truth CSV files"""
        for filename in os.listdir(self.casas_data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(self.casas_data_dir, filename)
                try:
                    df = pd.read_csv(filepath, names=['date', 'time', 'sensor', 'message'])
                    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
                    self.ground_truth_data[filename] = df
                    print(f"✅ Loaded ground truth: {filename} ({len(df)} readings)")
                except Exception as e:
                    print(f"❌ Failed to load {filename}: {e}")
                    
    def _load_sensor_locations(self) -> Dict[str, Tuple[float, float]]:
        """Load sensor locations based on CASAS apartment layout"""
        # This should match the locations used in virtual_sensors.py
        return {
            # Motion sensors (M001-M026)
            **{f"M{i:03d}": loc for i, loc in enumerate([
                (-2.0, 1.0), (-1.0, 1.0), (0.0, 1.0), (1.0, 1.0),
                (2.0, 1.0), (3.0, 1.0), (2.0, 0.0), (3.0, 0.0),
                (-2.0, -1.0), (-1.0, -1.0), (0.0, -1.0), (1.0, -1.0),
                (2.0, -1.0), (3.0, -1.0), (4.0, 0.0), (4.0, 1.0),
                (-3.0, 0.0), (-3.0, 1.0), (-3.0, -1.0),
                (0.0, 0.0), (1.0, 0.0), (-1.0, 0.0),
                (-2.0, 2.0), (-1.0, 2.0), (0.0, 2.0), (1.0, 2.0)
            ], 1)},
            
            # Item sensors
            "I01": (-1.0, 1.5),    # oatmeal
            "I02": (-1.2, 1.5),   # raisins
            "I03": (-0.8, 1.5),   # brown_sugar
            "I04": (-1.0, 1.7),   # bowl
            "I05": (-1.5, 1.5),   # measuring_spoon
            "I06": (2.5, 0.5),    # medicine_container
            "I07": (-0.5, 1.5),   # pot
            "I08": (2.8, 1.0),    # phone_book
            
            # Other sensors
            "D01": (-1.0, 2.0),   # kitchen_cabinet
            "AD1-A": (-2.0, 1.5), # water_hot
            "AD1-B": (-2.0, 1.5), # water_cold
            "AD1-C": (0.0, 1.5),  # burner
            "*": (2.8, 1.0)       # phone
        }
        
    def compare_execution(self, vesper_csv_file: str, vesper_details_file: str,
                         ground_truth_key: str) -> ComparisonMetrics:
        """Compare a VESPER execution against CASAS ground truth"""
        
        # Load VESPER data
        vesper_df = pd.read_csv(vesper_csv_file, names=['date', 'time', 'sensor', 'message'])
        vesper_df['datetime'] = pd.to_datetime(vesper_df['date'] + ' ' + vesper_df['time'])
        
        with open(vesper_details_file, 'r') as f:
            vesper_details = json.load(f)
            
        # Get ground truth data
        ground_truth_df = self.ground_truth_data[ground_truth_key]
        
        # Calculate individual metrics
        temporal_metrics = self._analyze_temporal_patterns(vesper_df, ground_truth_df, vesper_details)
        spatial_metrics = self._analyze_spatial_patterns(vesper_df, ground_truth_df, vesper_details)
        behavioral_metrics = self._analyze_behavioral_patterns(vesper_df, ground_truth_df, vesper_details)
        
        # Calculate overall similarity
        overall_score = self._calculate_overall_similarity(temporal_metrics, spatial_metrics, behavioral_metrics)
        
        return ComparisonMetrics(
            task_duration_correlation=temporal_metrics['duration_correlation'],
            sensor_timing_accuracy=temporal_metrics['timing_accuracy'],
            sequence_alignment_score=temporal_metrics['sequence_alignment'],
            motion_pattern_similarity=spatial_metrics['motion_similarity'],
            location_visitation_accuracy=spatial_metrics['location_accuracy'],
            path_efficiency_ratio=spatial_metrics['path_efficiency'],
            object_interaction_accuracy=behavioral_metrics['interaction_accuracy'],
            task_completion_fidelity=behavioral_metrics['completion_fidelity'],
            error_detection_capability=behavioral_metrics['error_detection'],
            overall_similarity_score=overall_score
        )
        
    def _analyze_temporal_patterns(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame,
                                  vesper_details: Dict) -> Dict[str, float]:
        """Analyze temporal execution patterns"""
        
        # Duration correlation
        vesper_duration = vesper_details['duration']
        gt_duration = (ground_truth_df['datetime'].max() - ground_truth_df['datetime'].min()).total_seconds()
        duration_correlation = 1.0 - abs(vesper_duration - gt_duration) / max(vesper_duration, gt_duration)
        
        # Sensor timing accuracy
        timing_accuracy = self._calculate_sensor_timing_accuracy(vesper_df, ground_truth_df)
        
        # Sequence alignment
        sequence_alignment = self._calculate_sequence_alignment(vesper_df, ground_truth_df)
        
        return {
            'duration_correlation': max(0.0, duration_correlation),
            'timing_accuracy': timing_accuracy,
            'sequence_alignment': sequence_alignment
        }
        
    def _analyze_spatial_patterns(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame,
                                 vesper_details: Dict) -> Dict[str, float]:
        """Analyze spatial movement patterns"""
        
        # Motion sensor pattern similarity
        motion_similarity = self._calculate_motion_pattern_similarity(vesper_df, ground_truth_df)
        
        # Location visitation accuracy
        location_accuracy = self._calculate_location_visitation_accuracy(vesper_df, ground_truth_df)
        
        # Path efficiency
        path_efficiency = self._calculate_path_efficiency(vesper_details)
        
        return {
            'motion_similarity': motion_similarity,
            'location_accuracy': location_accuracy,
            'path_efficiency': path_efficiency
        }
        
    def _analyze_behavioral_patterns(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame,
                                   vesper_details: Dict) -> Dict[str, float]:
        """Analyze behavioral execution patterns"""
        
        # Object interaction accuracy
        interaction_accuracy = self._calculate_interaction_accuracy(vesper_df, ground_truth_df)
        
        # Task completion fidelity
        completion_fidelity = self._calculate_completion_fidelity(vesper_df, ground_truth_df, vesper_details)
        
        # Error detection capability
        error_detection = self._calculate_error_detection_capability(vesper_details)
        
        return {
            'interaction_accuracy': interaction_accuracy,
            'completion_fidelity': completion_fidelity,
            'error_detection': error_detection
        }
        
    def _calculate_sensor_timing_accuracy(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> float:
        """Calculate how well sensor timing matches ground truth"""
        
        # Normalize timestamps to start from 0
        vesper_df_norm = vesper_df.copy()
        ground_truth_df_norm = ground_truth_df.copy()
        
        vesper_start = vesper_df_norm['datetime'].min()
        gt_start = ground_truth_df_norm['datetime'].min()
        
        vesper_df_norm['seconds'] = (vesper_df_norm['datetime'] - vesper_start).dt.total_seconds()
        ground_truth_df_norm['seconds'] = (ground_truth_df_norm['datetime'] - gt_start).dt.total_seconds()
        
        # Compare sensor activation timings
        timing_scores = []
        
        for sensor in set(vesper_df['sensor']) & set(ground_truth_df['sensor']):
            vesper_times = vesper_df_norm[vesper_df_norm['sensor'] == sensor]['seconds'].values
            gt_times = ground_truth_df_norm[ground_truth_df_norm['sensor'] == sensor]['seconds'].values
            
            if len(vesper_times) > 0 and len(gt_times) > 0:
                # Calculate DTW distance or similar timing alignment metric
                score = self._calculate_timing_alignment(vesper_times, gt_times)
                timing_scores.append(score)
                
        return np.mean(timing_scores) if timing_scores else 0.0
        
    def _calculate_timing_alignment(self, vesper_times: np.ndarray, gt_times: np.ndarray) -> float:
        """Calculate timing alignment between two sensor activation sequences"""
        
        # Simple approach: compare activation frequency and distribution
        vesper_freq = len(vesper_times)
        gt_freq = len(gt_times)
        
        # Frequency similarity
        freq_similarity = 1.0 - abs(vesper_freq - gt_freq) / max(vesper_freq, gt_freq) if max(vesper_freq, gt_freq) > 0 else 1.0
        
        # Distribution similarity (compare mean activation times)
        if len(vesper_times) > 0 and len(gt_times) > 0:
            vesper_mean = np.mean(vesper_times)
            gt_mean = np.mean(gt_times)
            max_time = max(np.max(vesper_times), np.max(gt_times))
            dist_similarity = 1.0 - abs(vesper_mean - gt_mean) / max_time if max_time > 0 else 1.0
        else:
            dist_similarity = freq_similarity
            
        return (freq_similarity + dist_similarity) / 2.0
        
    def _calculate_sequence_alignment(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> float:
        """Calculate how well the sensor activation sequence matches"""
        
        # Get sensor activation sequences
        vesper_sequence = vesper_df['sensor'].tolist()
        gt_sequence = ground_truth_df['sensor'].tolist()
        
        # Calculate longest common subsequence
        lcs_length = self._longest_common_subsequence(vesper_sequence, gt_sequence)
        max_length = max(len(vesper_sequence), len(gt_sequence))
        
        return lcs_length / max_length if max_length > 0 else 0.0
        
    def _longest_common_subsequence(self, seq1: List[str], seq2: List[str]) -> int:
        """Calculate longest common subsequence length"""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                    
        return dp[m][n]
        
    def _calculate_motion_pattern_similarity(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> float:
        """Calculate similarity of motion sensor activation patterns"""
        
        # Get motion sensors only
        motion_sensors = [s for s in self.sensor_locations.keys() if s.startswith('M')]
        
        vesper_motion = vesper_df[vesper_df['sensor'].isin(motion_sensors)]
        gt_motion = ground_truth_df[ground_truth_df['sensor'].isin(motion_sensors)]
        
        # Compare activation patterns for each motion sensor
        similarities = []
        
        for sensor in motion_sensors:
            vesper_activations = len(vesper_motion[vesper_motion['sensor'] == sensor])
            gt_activations = len(gt_motion[gt_motion['sensor'] == sensor])
            
            if gt_activations > 0:
                similarity = 1.0 - abs(vesper_activations - gt_activations) / gt_activations
                similarities.append(max(0.0, similarity))
                
        return np.mean(similarities) if similarities else 0.0
        
    def _calculate_location_visitation_accuracy(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> float:
        """Calculate how accurately locations were visited"""
        
        # Determine locations visited based on sensor activations
        vesper_locations = self._infer_locations_from_sensors(vesper_df)
        gt_locations = self._infer_locations_from_sensors(ground_truth_df)
        
        # Calculate Jaccard similarity
        intersection = len(vesper_locations & gt_locations)
        union = len(vesper_locations | gt_locations)
        
        return intersection / union if union > 0 else 0.0
        
    def _infer_locations_from_sensors(self, df: pd.DataFrame) -> set:
        """Infer visited locations from sensor activations"""
        locations = set()
        
        # Map sensor activations to location zones
        for _, row in df.iterrows():
            sensor = row['sensor']
            if sensor in self.sensor_locations:
                x, y = self.sensor_locations[sensor]
                # Map coordinates to location zones
                location = self._coordinate_to_location_zone(x, y)
                locations.add(location)
                
        return locations
        
    def _coordinate_to_location_zone(self, x: float, y: float) -> str:
        """Map coordinates to semantic location zones"""
        
        # Define location boundaries based on apartment layout
        if x <= -2.0 and y >= 1.0:
            return "kitchen_sink"
        elif x <= 0.0 and y >= 1.0:
            return "kitchen"
        elif x >= 2.0 and y >= 0.0:
            return "dining_room"
        elif x <= 0.0 and y <= 0.0:
            return "living_room"
        elif x >= 2.0 and y <= 0.0:
            return "bedroom"
        elif x <= -2.0:
            return "bathroom"
        else:
            return "hallway"
            
    def _calculate_path_efficiency(self, vesper_details: Dict) -> float:
        """Calculate path efficiency from VLM actions"""
        
        actions = vesper_details.get('vlm_actions', [])
        navigation_actions = [a for a in actions if a.get('action') == 'navigate']
        
        if len(navigation_actions) < 2:
            return 1.0  # Single location or no navigation
            
        # Calculate total distance traveled
        total_distance = 0.0
        for i in range(1, len(navigation_actions)):
            if 'position' in navigation_actions[i-1] and 'position' in navigation_actions[i]:
                pos1 = navigation_actions[i-1]['position']
                pos2 = navigation_actions[i]['position']
                distance = math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
                total_distance += distance
                
        # Calculate direct distance (start to end)
        if 'position' in navigation_actions[0] and 'position' in navigation_actions[-1]:
            start_pos = navigation_actions[0]['position']
            end_pos = navigation_actions[-1]['position']
            direct_distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
            
            if total_distance > 0:
                return direct_distance / total_distance
                
        return 1.0
        
    def _calculate_interaction_accuracy(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> float:
        """Calculate object interaction accuracy"""
        
        # Get item sensor activations
        item_sensors = [s for s in self.sensor_locations.keys() if s.startswith('I')]
        
        vesper_interactions = vesper_df[vesper_df['sensor'].isin(item_sensors)]
        gt_interactions = ground_truth_df[ground_truth_df['sensor'].isin(item_sensors)]
        
        # Compare interaction patterns
        similarities = []
        
        for sensor in item_sensors:
            vesper_states = vesper_interactions[vesper_interactions['sensor'] == sensor]['message'].tolist()
            gt_states = gt_interactions[gt_interactions['sensor'] == sensor]['message'].tolist()
            
            # Compare state sequences
            if gt_states:
                # Simple state matching
                vesper_present = vesper_states.count('PRESENT')
                vesper_absent = vesper_states.count('ABSENT')
                gt_present = gt_states.count('PRESENT')
                gt_absent = gt_states.count('ABSENT')
                
                present_sim = 1.0 - abs(vesper_present - gt_present) / max(1, gt_present) if gt_present > 0 else (1.0 if vesper_present == 0 else 0.0)
                absent_sim = 1.0 - abs(vesper_absent - gt_absent) / max(1, gt_absent) if gt_absent > 0 else (1.0 if vesper_absent == 0 else 0.0)
                
                similarities.append((present_sim + absent_sim) / 2.0)
                
        return np.mean(similarities) if similarities else 0.0
        
    def _calculate_completion_fidelity(self, vesper_df: pd.DataFrame, ground_truth_df: pd.DataFrame,
                                     vesper_details: Dict) -> float:
        """Calculate task completion fidelity"""
        
        # Check if task was completed successfully
        task_success = vesper_details.get('success', False)
        
        # Compare sensor activation completeness
        vesper_sensors = set(vesper_df['sensor'])
        gt_sensors = set(ground_truth_df['sensor'])
        
        sensor_coverage = len(vesper_sensors & gt_sensors) / len(gt_sensors) if gt_sensors else 0.0
        
        # Combine factors
        return (float(task_success) + sensor_coverage) / 2.0
        
    def _calculate_error_detection_capability(self, vesper_details: Dict) -> float:
        """Calculate error detection and correction capability"""
        
        error_type = vesper_details.get('error_type', 'none')
        error_detected = vesper_details.get('error_detected', False)
        error_corrected = vesper_details.get('error_corrected', False)
        
        if error_type == 'none':
            return 1.0  # No error to detect
            
        # Score based on detection and correction
        score = 0.0
        if error_detected:
            score += 0.6  # Detection worth 60%
        if error_corrected:
            score += 0.4  # Correction worth 40%
            
        return score
        
    def _calculate_overall_similarity(self, temporal: Dict, spatial: Dict, behavioral: Dict) -> float:
        """Calculate weighted overall similarity score"""
        
        # Weights for different metric categories
        weights = {
            'temporal': 0.3,
            'spatial': 0.4,
            'behavioral': 0.3
        }
        
        temporal_score = np.mean(list(temporal.values()))
        spatial_score = np.mean(list(spatial.values()))
        behavioral_score = np.mean(list(behavioral.values()))
        
        overall = (temporal_score * weights['temporal'] + 
                  spatial_score * weights['spatial'] + 
                  behavioral_score * weights['behavioral'])
                  
        return overall
        
    def generate_comparison_report(self, metrics: ComparisonMetrics, output_file: str):
        """Generate detailed comparison report"""
        
        report = {
            "comparison_timestamp": datetime.now().isoformat(),
            "metrics": {
                "temporal": {
                    "task_duration_correlation": metrics.task_duration_correlation,
                    "sensor_timing_accuracy": metrics.sensor_timing_accuracy,
                    "sequence_alignment_score": metrics.sequence_alignment_score
                },
                "spatial": {
                    "motion_pattern_similarity": metrics.motion_pattern_similarity,
                    "location_visitation_accuracy": metrics.location_visitation_accuracy,
                    "path_efficiency_ratio": metrics.path_efficiency_ratio
                },
                "behavioral": {
                    "object_interaction_accuracy": metrics.object_interaction_accuracy,
                    "task_completion_fidelity": metrics.task_completion_fidelity,
                    "error_detection_capability": metrics.error_detection_capability
                },
                "overall": {
                    "similarity_score": metrics.overall_similarity_score
                }
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"📊 Comparison report saved: {output_file}")
        return report
