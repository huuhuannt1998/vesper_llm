#!/usr/bin/env python3
"""
VESPER Metrics Calculator
========================

Comprehensive metrics computation system for VESPER evaluation.
Processes Blender navigation logs and computes all research paper metrics.

Usage:
    from evaluation.vesper_metrics_calculator import VESPERMetricsCalculator
    
    # Calculate metrics for single log
    calculator = VESPERMetricsCalculator()
    metrics = calculator.compute_all_metrics("path/to/log.json")
    
    # Calculate metrics for all logs
    batch_metrics = calculator.compute_batch_metrics()
"""

import json
import os
import math
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path


class VESPERMetricsCalculator:
    """Calculates comprehensive evaluation metrics for VESPER research"""
    
    def __init__(self, logs_directory: str = None):
        if logs_directory is None:
            self.logs_dir = Path(r"C:\Users\hbui11\Desktop\vesper_llm\blender\evaluation_logs")
        else:
            self.logs_dir = Path(logs_directory)
        
        self.casas_dir = Path(r"C:\Users\hbui11\Desktop\vesper_llm\casas_testbed\data\casas_ground_truth\adl_noerror")
        
    def load_blender_log(self, log_path: str) -> Dict[str, Any]:
        """Load and parse Blender navigation log"""
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading log {log_path}: {e}")
            return {}
    
    def compute_all_metrics(self, log_path: str, casas_reference: str = None) -> Dict[str, float]:
        """Compute all evaluation metrics for a single log"""
        log_data = self.load_blender_log(log_path)
        if not log_data:
            return {}
        
        print(f"📊 Computing metrics for: {os.path.basename(log_path)}")
        
        metrics = {}
        
        # Core navigation metrics
        metrics.update(self._compute_task_completion_metrics(log_data))
        metrics.update(self._compute_navigation_efficiency_metrics(log_data))
        metrics.update(self._compute_temporal_metrics(log_data))
        metrics.update(self._compute_behavioral_metrics(log_data))
        
        # CASAS comparison metrics (if reference provided)
        if casas_reference and os.path.exists(casas_reference):
            metrics.update(self._compute_casas_similarity_metrics(log_data, casas_reference))
        
        # Research paper specific metrics
        metrics.update(self._compute_research_paper_metrics(log_data))
        
        return metrics
    
    def _compute_task_completion_metrics(self, log_data: Dict) -> Dict[str, float]:
        """Compute Task Completion Rate (TCR) and related metrics"""
        task_details = log_data.get('task_details', [])
        
        if not task_details:
            return {
                'task_completion_rate': 0.0,
                'task_success_rate': 0.0,
                'task_attempt_rate': 1.0
            }
        
        # Count different types of task outcomes
        total_tasks = len(task_details)
        completed_tasks = sum(1 for task in task_details if task.get('success', False))
        attempted_tasks = sum(1 for task in task_details if task.get('steps_taken', 0) > 0)
        
        # Semantic success - check if agent reached appropriate room for task
        semantic_success = 0
        for task in task_details:
            if self._check_semantic_task_success(task):
                semantic_success += 1
        
        return {
            'task_completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0.0,
            'task_success_rate': semantic_success / total_tasks if total_tasks > 0 else 0.0,
            'task_attempt_rate': attempted_tasks / total_tasks if total_tasks > 0 else 0.0
        }
    
    def _compute_navigation_efficiency_metrics(self, log_data: Dict) -> Dict[str, float]:
        """Compute Navigation Efficiency (NE) and path-related metrics"""
        task_details = log_data.get('task_details', [])
        
        if not task_details:
            return {'navigation_efficiency': 0.0, 'path_directness': 0.0, 'redundant_moves': 0.0}
        
        efficiencies = []
        directness_scores = []
        redundant_move_ratios = []
        
        for task in task_details:
            movement_path = task.get('movement_path', [])
            if len(movement_path) < 2:
                continue
            
            # Extract positions
            positions = []
            for step in movement_path:
                from_pos = step.get('from_position', [0, 0])
                to_pos = step.get('to_position', [0, 0])
                positions.append(from_pos)
                if step == movement_path[-1]:  # Add final position
                    positions.append(to_pos)
            
            if len(positions) < 2:
                continue
            
            # Calculate actual path length
            actual_distance = 0
            for i in range(1, len(positions)):
                actual_distance += self._euclidean_distance(positions[i-1], positions[i])
            
            # Calculate optimal path length (straight line)
            optimal_distance = self._euclidean_distance(positions[0], positions[-1])
            
            # Navigation efficiency
            if actual_distance > 0:
                efficiency = optimal_distance / actual_distance
                efficiencies.append(efficiency)
            
            # Path directness (how direct the path is)
            if optimal_distance > 0:
                directness = optimal_distance / actual_distance if actual_distance > 0 else 0
                directness_scores.append(directness)
            
            # Redundant moves (repeated actions)
            actions = [step.get('action', '') for step in movement_path]
            unique_actions = len(set(actions))
            total_actions = len(actions)
            redundant_ratio = 1 - (unique_actions / total_actions) if total_actions > 0 else 0
            redundant_move_ratios.append(redundant_ratio)
        
        return {
            'navigation_efficiency': np.mean(efficiencies) if efficiencies else 0.0,
            'path_directness': np.mean(directness_scores) if directness_scores else 0.0,
            'redundant_moves': np.mean(redundant_move_ratios) if redundant_move_ratios else 0.0
        }
    
    def _compute_temporal_metrics(self, log_data: Dict) -> Dict[str, float]:
        """Compute temporal pattern metrics"""
        task_details = log_data.get('task_details', [])
        
        if not task_details:
            return {
                'average_task_duration': 0.0,
                'response_time_avg': 0.0,
                'response_time_consistency': 0.0
            }
        
        durations = []
        response_times = []
        
        for task in task_details:
            # Task duration
            start_time = task.get('start_time')
            completion_time = task.get('completion_time')
            if start_time and completion_time:
                duration = completion_time - start_time
                durations.append(duration)
            
            # VLM response times
            vlm_responses = task.get('vlm_responses', [])
            for response in vlm_responses:
                response_time = response.get('response_time', 0)
                if response_time > 0:
                    response_times.append(response_time)
        
        return {
            'average_task_duration': np.mean(durations) if durations else 0.0,
            'response_time_avg': np.mean(response_times) if response_times else 0.0,
            'response_time_consistency': 1 - (np.std(response_times) / np.mean(response_times)) 
                                       if response_times and np.mean(response_times) > 0 else 0.0
        }
    
    def _compute_behavioral_metrics(self, log_data: Dict) -> Dict[str, float]:
        """Compute behavioral pattern metrics"""
        task_details = log_data.get('task_details', [])
        
        if not task_details:
            return {
                'room_exploration_rate': 0.0,
                'action_diversity': 0.0,
                'exploration_efficiency': 0.0
            }
        
        all_rooms = set()
        all_actions = []
        
        for task in task_details:
            movement_path = task.get('movement_path', [])
            
            # Collect rooms visited
            for step in movement_path:
                room = step.get('room_detected', '')
                if room and room != 'UNKNOWN':
                    all_rooms.add(room)
            
            # Collect actions taken
            for step in movement_path:
                action = step.get('action', '')
                if action:
                    all_actions.append(action)
        
        # Room exploration metrics
        unique_rooms = len(all_rooms)
        # Assume typical house has 6-8 rooms
        expected_rooms = 7
        room_exploration_rate = min(unique_rooms / expected_rooms, 1.0)
        
        # Action diversity
        unique_actions = len(set(all_actions))
        total_actions = len(all_actions)
        action_diversity = unique_actions / total_actions if total_actions > 0 else 0.0
        
        # Exploration efficiency (unique rooms per step)
        total_steps = sum(len(task.get('movement_path', [])) for task in task_details)
        exploration_efficiency = unique_rooms / total_steps if total_steps > 0 else 0.0
        
        return {
            'room_exploration_rate': room_exploration_rate,
            'action_diversity': action_diversity,
            'exploration_efficiency': exploration_efficiency
        }
    
    def _compute_casas_similarity_metrics(self, log_data: Dict, casas_file: str) -> Dict[str, float]:
        """Compute similarity with CASAS ground truth"""
        try:
            # Load CASAS data
            casas_data = pd.read_csv(casas_file, names=['date', 'time', 'sensor', 'message'])
            
            # Extract VLM sensor activations
            vlm_sensors = self._extract_vlm_sensors(log_data)
            casas_sensors = set(casas_data['sensor'].tolist())
            
            # Sensor activation accuracy
            if casas_sensors:
                sensor_intersection = vlm_sensors.intersection(casas_sensors)
                sensor_accuracy = len(sensor_intersection) / len(casas_sensors)
            else:
                sensor_accuracy = 0.0
            
            # Temporal pattern similarity (simplified)
            vlm_duration = self._get_session_duration(log_data)
            casas_duration = self._get_casas_duration(casas_data)
            
            if casas_duration > 0:
                duration_similarity = min(vlm_duration, casas_duration) / max(vlm_duration, casas_duration)
            else:
                duration_similarity = 0.0
            
            return {
                'sensor_activation_accuracy': sensor_accuracy,
                'temporal_pattern_similarity': duration_similarity,
                'casas_overall_similarity': (sensor_accuracy + duration_similarity) / 2
            }
            
        except Exception as e:
            print(f"❌ Error computing CASAS similarity: {e}")
            return {
                'sensor_activation_accuracy': 0.0,
                'temporal_pattern_similarity': 0.0,
                'casas_overall_similarity': 0.0
            }
    
    def _compute_research_paper_metrics(self, log_data: Dict) -> Dict[str, float]:
        """Compute specific metrics for research paper"""
        task_details = log_data.get('task_details', [])
        
        if not task_details:
            return {
                'effective_movement_ratio': 0.0,
                'oscillation_index': 0.0,
                'room_label_stability': 0.0,
                'semantic_understanding_score': 0.0
            }
        
        # Effective Movement Ratio (EMR)
        total_actions = 0
        movement_actions = 0
        
        for task in task_details:
            movement_path = task.get('movement_path', [])
            for step in movement_path:
                action = step.get('action', '')
                total_actions += 1
                if action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
                    movement_actions += 1
        
        emr = movement_actions / total_actions if total_actions > 0 else 0.0
        
        # Oscillation Index (OI) - detect back-and-forth movement
        oscillations = 0
        total_transitions = 0
        
        for task in task_details:
            movement_path = task.get('movement_path', [])
            actions = [step.get('action', '') for step in movement_path]
            
            for i in range(len(actions) - 2):
                total_transitions += 1
                # Check for oscillation pattern (A -> B -> A)
                if (actions[i] == 'UP' and actions[i+1] == 'DOWN' and actions[i+2] == 'UP') or \
                   (actions[i] == 'DOWN' and actions[i+1] == 'UP' and actions[i+2] == 'DOWN') or \
                   (actions[i] == 'LEFT' and actions[i+1] == 'RIGHT' and actions[i+2] == 'LEFT') or \
                   (actions[i] == 'RIGHT' and actions[i+1] == 'LEFT' and actions[i+2] == 'RIGHT'):
                    oscillations += 1
        
        oi = oscillations / total_transitions if total_transitions > 0 else 0.0
        
        # Room Label Stability (RLS)
        total_room_detections = 0
        stable_room_detections = 0
        
        for task in task_details:
            vlm_responses = task.get('vlm_responses', [])
            for response in vlm_responses:
                room = response.get('room_detected', '')
                total_room_detections += 1
                if room and room != 'UNKNOWN' and '|' not in room:
                    stable_room_detections += 1
        
        rls = stable_room_detections / total_room_detections if total_room_detections > 0 else 0.0
        
        # Semantic Understanding Score (simplified)
        # Based on whether VLM reasoning matches task requirements
        semantic_scores = []
        for task in task_details:
            task_name = task.get('task_name', '').lower()
            rooms_visited = set()
            
            movement_path = task.get('movement_path', [])
            for step in movement_path:
                room = step.get('room_detected', '')
                if room and room != 'UNKNOWN':
                    rooms_visited.add(room.lower())
            
            # Simple semantic matching
            if 'phone' in task_name and 'living' in str(rooms_visited):
                semantic_scores.append(1.0)
            elif 'cook' in task_name and 'kitchen' in str(rooms_visited):
                semantic_scores.append(1.0)
            elif 'bathroom' in task_name and 'bathroom' in str(rooms_visited):
                semantic_scores.append(1.0)
            else:
                semantic_scores.append(0.5)  # Partial credit for exploration
        
        sus = np.mean(semantic_scores) if semantic_scores else 0.0
        
        return {
            'effective_movement_ratio': emr,
            'oscillation_index': oi,
            'room_label_stability': rls,
            'semantic_understanding_score': sus
        }
    
    def compute_batch_metrics(self, output_file: str = None) -> pd.DataFrame:
        """Compute metrics for all log files in the directory"""
        log_files = list(self.logs_dir.glob("vesper_navigation_log_*.json"))
        
        if not log_files:
            print("❌ No log files found in directory")
            return pd.DataFrame()
        
        print(f"📊 Computing metrics for {len(log_files)} log files...")
        
        all_metrics = []
        
        for log_file in log_files:
            print(f"📋 Processing: {log_file.name}")
            
            # Find corresponding CASAS file (if exists)
            casas_file = self._find_matching_casas_file(log_file.name)
            
            # Compute metrics
            metrics = self.compute_all_metrics(str(log_file), casas_file)
            
            if metrics:
                metrics['log_file'] = log_file.name
                metrics['timestamp'] = self._extract_timestamp(log_file.name)
                all_metrics.append(metrics)
        
        # Create DataFrame
        df = pd.DataFrame(all_metrics)
        
        # Save to file if requested
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"📁 Metrics saved to: {output_file}")
        
        return df
    
    def generate_metrics_report(self, metrics_df: pd.DataFrame, output_file: str = None) -> str:
        """Generate comprehensive metrics report"""
        if metrics_df.empty:
            return "No metrics data available"
        
        report = []
        report.append("VESPER Navigation Metrics Report")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Sessions Analyzed: {len(metrics_df)}")
        report.append("")
        
        # Core metrics summary
        core_metrics = [
            'task_completion_rate', 'task_success_rate', 'navigation_efficiency',
            'sensor_activation_accuracy', 'casas_overall_similarity'
        ]
        
        report.append("Core Performance Metrics:")
        report.append("-" * 30)
        for metric in core_metrics:
            if metric in metrics_df.columns:
                mean_val = metrics_df[metric].mean()
                std_val = metrics_df[metric].std()
                report.append(f"{metric:30s}: {mean_val:.3f} ± {std_val:.3f}")
        report.append("")
        
        # Research metrics summary
        research_metrics = [
            'effective_movement_ratio', 'oscillation_index', 'room_label_stability',
            'semantic_understanding_score'
        ]
        
        report.append("Research Paper Metrics:")
        report.append("-" * 30)
        for metric in research_metrics:
            if metric in metrics_df.columns:
                mean_val = metrics_df[metric].mean()
                std_val = metrics_df[metric].std()
                report.append(f"{metric:30s}: {mean_val:.3f} ± {std_val:.3f}")
        report.append("")
        
        # Best performing sessions
        if 'casas_overall_similarity' in metrics_df.columns:
            best_session = metrics_df.loc[metrics_df['casas_overall_similarity'].idxmax()]
            report.append("Best Performing Session:")
            report.append("-" * 30)
            report.append(f"File: {best_session.get('log_file', 'Unknown')}")
            report.append(f"CASAS Similarity: {best_session['casas_overall_similarity']:.3f}")
            report.append(f"Task Success: {best_session.get('task_success_rate', 0):.3f}")
            report.append("")
        
        # Recommendations
        report.append("Recommendations for Improvement:")
        report.append("-" * 30)
        
        avg_completion = metrics_df.get('task_completion_rate', pd.Series([0])).mean()
        if avg_completion < 0.5:
            report.append("• Focus on task completion strategies")
        
        avg_efficiency = metrics_df.get('navigation_efficiency', pd.Series([0])).mean()
        if avg_efficiency < 0.6:
            report.append("• Improve path planning algorithms")
        
        avg_oscillation = metrics_df.get('oscillation_index', pd.Series([0])).mean()
        if avg_oscillation > 0.3:
            report.append("• Reduce oscillatory behavior patterns")
        
        report_text = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"📋 Report saved to: {output_file}")
        
        return report_text
    
    # Helper methods
    def _euclidean_distance(self, pos1: List[float], pos2: List[float]) -> float:
        """Calculate Euclidean distance between two positions"""
        if len(pos1) != 2 or len(pos2) != 2:
            return 0.0
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def _check_semantic_task_success(self, task: Dict) -> bool:
        """Check if task was semantically successful based on room visits"""
        task_name = task.get('task_name', '').lower()
        movement_path = task.get('movement_path', [])
        
        rooms_visited = set()
        for step in movement_path:
            room = step.get('room_detected', '')
            if room and room != 'UNKNOWN':
                rooms_visited.add(room.lower())
        
        # Basic semantic matching
        if 'phone' in task_name:
            return 'living_room' in rooms_visited or 'living' in str(rooms_visited)
        elif 'cook' in task_name or 'kitchen' in task_name:
            return 'kitchen' in rooms_visited
        elif 'bathroom' in task_name or 'wash' in task_name:
            return 'bathroom' in rooms_visited
        
        return len(rooms_visited) > 0  # At least moved to some room
    
    def _extract_vlm_sensors(self, log_data: Dict) -> set:
        """Extract sensors that would be activated based on VLM movement"""
        sensors = set()
        task_details = log_data.get('task_details', [])
        
        for task in task_details:
            movement_path = task.get('movement_path', [])
            for step in movement_path:
                room = step.get('room_detected', '')
                if room and room != 'UNKNOWN':
                    # Map rooms to motion sensors
                    room_sensor_map = {
                        'LIVING_ROOM': 'M01',
                        'KITCHEN': 'M02',
                        'BEDROOM': 'M03',
                        'BATHROOM': 'M04',
                        'DINING_ROOM': 'M05',
                        'OFFICE': 'M06'
                    }
                    sensor = room_sensor_map.get(room.upper())
                    if sensor:
                        sensors.add(sensor)
        
        return sensors
    
    def _get_session_duration(self, log_data: Dict) -> float:
        """Get total session duration in seconds"""
        start_time = log_data.get('start_time', 0)
        task_details = log_data.get('task_details', [])
        
        if not task_details:
            return 0.0
        
        # Find latest timestamp
        latest_time = start_time
        for task in task_details:
            movement_path = task.get('movement_path', [])
            for step in movement_path:
                timestamp = step.get('timestamp', 0)
                latest_time = max(latest_time, timestamp)
        
        return latest_time - start_time
    
    def _get_casas_duration(self, casas_data: pd.DataFrame) -> float:
        """Get CASAS session duration"""
        if casas_data.empty:
            return 0.0
        
        try:
            casas_data['datetime'] = pd.to_datetime(casas_data['date'] + ' ' + casas_data['time'])
            duration = (casas_data['datetime'].max() - casas_data['datetime'].min()).total_seconds()
            return duration
        except:
            return 0.0
    
    def _find_matching_casas_file(self, log_filename: str) -> Optional[str]:
        """Find corresponding CASAS file for comparison"""
        # Try to match with common CASAS files
        casas_files = ['p01.t1.csv', 'p01.t2.csv', 'p01.t3.csv']
        
        for casas_file in casas_files:
            casas_path = self.casas_dir / casas_file
            if casas_path.exists():
                return str(casas_path)
        
        return None
    
    def _extract_timestamp(self, filename: str) -> str:
        """Extract timestamp from log filename"""
        try:
            # Extract from vesper_navigation_log_YYYYMMDD_HHMMSS.json
            parts = filename.replace('.json', '').split('_')
            if len(parts) >= 4:
                return f"{parts[-2]}_{parts[-1]}"
        except:
            pass
        return ""


def main():
    """Example usage of the metrics calculator"""
    calculator = VESPERMetricsCalculator()
    
    # Option 1: Analyze single log file
    log_file = r"C:\Users\hbui11\Desktop\vesper_llm\blender\evaluation_logs\vesper_navigation_log_20250910_140025.json"
    
    if os.path.exists(log_file):
        print("📊 Analyzing single log file...")
        metrics = calculator.compute_all_metrics(log_file)
        
        print("\n🎯 Computed Metrics:")
        print("-" * 40)
        for metric_name, value in metrics.items():
            print(f"{metric_name:30s}: {value:.3f}")
    
    print("\n" + "="*60)
    
    # Option 2: Analyze all log files
    print("📊 Analyzing all log files...")
    metrics_df = calculator.compute_batch_metrics(
        output_file=r"C:\Users\hbui11\Desktop\vesper_llm\evaluation\results\vesper_metrics.csv"
    )
    
    if not metrics_df.empty:
        print(f"\n📋 Processed {len(metrics_df)} log files")
        print("\n🔍 Summary Statistics:")
        print(metrics_df.describe())
        
        # Generate report
        report = calculator.generate_metrics_report(
            metrics_df,
            output_file=r"C:\Users\hbui11\Desktop\vesper_llm\evaluation\results\vesper_metrics_report.txt"
        )
        
        print("\n📄 Generated Report Preview:")
        print(report[:500] + "...")


if __name__ == "__main__":
    main()
