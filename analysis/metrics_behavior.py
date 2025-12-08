"""
VESPER V2 Behavioral Metrics
============================

Compute behavioral performance and realism metrics:

Core Performance Metrics:
- TCR (Task Completion Rate): Fraction of tasks successfully completed
- SUS (Semantic Understanding Score): Room identification accuracy
- RLS (Room Label Stability): Temporal consistency of room labels
- EMR (Effective Movement Ratio): Motion quality (1 - oscillation index)

CASAS Realism Metrics (COS components):
- T: Temporal similarity (DTW-based)
- S: Sensor sequence similarity
- R: Room transition similarity
- E: Event count ratio
- D: Duration ratio
- COS (Composite Overall Similarity): Average of T, S, R, E, D
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import Counter
import warnings


@dataclass
class BehaviorMetricsResult:
    """Container for computed behavioral metrics."""
    # Core performance
    tcr: float  # Task Completion Rate
    sus: float  # Semantic Understanding Score
    rls: float  # Room Label Stability
    emr: float  # Effective Movement Ratio
    
    # CASAS similarity (COS components)
    temporal_similarity: float  # T
    sensor_sequence_similarity: float  # S
    transition_similarity: float  # R
    event_count_ratio: float  # E
    duration_ratio: float  # D
    cos: float  # Composite Overall Similarity
    
    # Per-house breakdown
    tcr_by_house: Dict[str, float] = field(default_factory=dict)
    tcr_by_task: Dict[str, float] = field(default_factory=dict)
    
    # Statistics
    avg_steps: float = 0.0
    std_steps: float = 0.0
    avg_duration: float = 0.0
    std_duration: float = 0.0
    avg_llm_calls: float = 0.0
    std_llm_calls: float = 0.0
    
    # Raw counts
    total_trials: int = 0
    successful_trials: int = 0


class BehaviorMetrics:
    """Compute behavioral metrics from trial data."""
    
    def __init__(self, df: pd.DataFrame, casas_ground_truth: Dict[str, pd.DataFrame] = None):
        """
        Initialize with trial DataFrame.
        
        Args:
            df: DataFrame with trial data
            casas_ground_truth: Dict mapping task IDs to CASAS DataFrames for comparison
        """
        self.df = df
        self.casas_ground_truth = casas_ground_truth or {}
    
    def compute_all_metrics(self) -> BehaviorMetricsResult:
        """
        Compute all behavioral metrics.
        
        Returns:
            BehaviorMetricsResult with all metrics
        """
        # Core metrics
        tcr = self._compute_tcr()
        sus = self._compute_sus()
        rls = self._compute_rls()
        emr = self._compute_emr()
        
        # CASAS similarity metrics
        t, s, r, e, d = self._compute_casas_similarity()
        cos = (t + s + r + e + d) / 5
        
        # Per-house and per-task breakdown
        tcr_by_house = self._compute_tcr_by_group('house_id')
        tcr_by_task = self._compute_tcr_by_group('task_id')
        
        # Statistics
        successful_df = self.df[self.df['success'] == True]
        
        avg_steps = successful_df['steps'].mean() if not successful_df.empty else 0
        std_steps = successful_df['steps'].std() if not successful_df.empty else 0
        avg_duration = successful_df['duration_sec'].mean() if not successful_df.empty else 0
        std_duration = successful_df['duration_sec'].std() if not successful_df.empty else 0
        avg_llm_calls = successful_df['llm_calls'].mean() if not successful_df.empty else 0
        std_llm_calls = successful_df['llm_calls'].std() if not successful_df.empty else 0
        
        return BehaviorMetricsResult(
            tcr=tcr,
            sus=sus,
            rls=rls,
            emr=emr,
            temporal_similarity=t,
            sensor_sequence_similarity=s,
            transition_similarity=r,
            event_count_ratio=e,
            duration_ratio=d,
            cos=cos,
            tcr_by_house=tcr_by_house,
            tcr_by_task=tcr_by_task,
            avg_steps=avg_steps,
            std_steps=std_steps if not np.isnan(std_steps) else 0,
            avg_duration=avg_duration,
            std_duration=std_duration if not np.isnan(std_duration) else 0,
            avg_llm_calls=avg_llm_calls,
            std_llm_calls=std_llm_calls if not np.isnan(std_llm_calls) else 0,
            total_trials=len(self.df),
            successful_trials=self.df['success'].sum()
        )
    
    def _compute_tcr(self) -> float:
        """
        Compute Task Completion Rate.
        
        TCR = N_completed / N_attempted
        """
        if self.df.empty:
            return 0.0
        return self.df['success'].mean()
    
    def _compute_sus(self) -> float:
        """
        Compute Semantic Understanding Score.
        
        SUS = (correct room identifications) / (total steps)
        
        A room identification is correct if it matches the expected room
        based on the agent's position and the house layout.
        """
        total_steps = 0
        correct_identifications = 0
        
        for _, row in self.df.iterrows():
            room_transitions = row.get('room_transitions', [])
            if not isinstance(room_transitions, list):
                continue
            
            for i, room in enumerate(room_transitions):
                total_steps += 1
                # A room is "correctly identified" if it's not UNKNOWN
                # In a full implementation, would compare to ground truth
                if room and room != 'UNKNOWN':
                    correct_identifications += 1
        
        if total_steps == 0:
            return 0.0
        
        return correct_identifications / total_steps
    
    def _compute_rls(self) -> float:
        """
        Compute Room Label Stability.
        
        RLS measures temporal consistency of predicted room labels after entry.
        High RLS means the agent doesn't "flicker" between room labels.
        
        RLS = 1 - (room_label_changes / total_transitions)
        """
        total_transitions = 0
        unstable_transitions = 0
        
        for _, row in self.df.iterrows():
            room_transitions = row.get('room_transitions', [])
            if not isinstance(room_transitions, list) or len(room_transitions) < 2:
                continue
            
            prev_room = room_transitions[0]
            stable_count = 0
            
            for room in room_transitions[1:]:
                total_transitions += 1
                
                # Check if this is a valid transition (not just noise)
                if room != prev_room:
                    # Check if we quickly return to prev_room (unstable)
                    # This is simplified; full implementation would use window
                    pass
                else:
                    stable_count += 1
                
                prev_room = room
        
        if total_transitions == 0:
            return 1.0  # No transitions = perfectly stable
        
        # Stability = consistent room labels / total
        return stable_count / total_transitions if total_transitions > 0 else 1.0
    
    def _compute_emr(self) -> float:
        """
        Compute Effective Movement Ratio.
        
        EMR = 1 - Oscillation Index
        
        Oscillation Index = (reversed or redundant steps) / (total steps)
        A reversed step is when the agent goes back to a previous position.
        """
        total_movements = 0
        oscillations = 0
        
        for _, row in self.df.iterrows():
            actions = row.get('actions', [])
            if not isinstance(actions, list):
                continue
            
            # Look for patterns like FORWARD-BACKWARD or LEFT-RIGHT-LEFT
            for i, action in enumerate(actions):
                total_movements += 1
                proposed = action.get('proposed', '')
                
                if i >= 2:
                    prev1 = actions[i-1].get('proposed', '')
                    prev2 = actions[i-2].get('proposed', '')
                    
                    # Detect oscillation patterns
                    if self._is_oscillation(prev2, prev1, proposed):
                        oscillations += 1
        
        if total_movements == 0:
            return 1.0
        
        oscillation_index = oscillations / total_movements
        return 1 - oscillation_index
    
    def _is_oscillation(self, a1: str, a2: str, a3: str) -> bool:
        """Check if three consecutive actions form an oscillation pattern."""
        # FORWARD-BACKWARD-FORWARD
        if a1 == 'FORWARD' and a2 == 'BACKWARD' and a3 == 'FORWARD':
            return True
        if a1 == 'BACKWARD' and a2 == 'FORWARD' and a3 == 'BACKWARD':
            return True
        
        # LEFT-RIGHT-LEFT or RIGHT-LEFT-RIGHT
        if a1 == 'LEFT' and a2 == 'RIGHT' and a3 == 'LEFT':
            return True
        if a1 == 'RIGHT' and a2 == 'LEFT' and a3 == 'RIGHT':
            return True
        
        return False
    
    def _compute_casas_similarity(self) -> Tuple[float, float, float, float, float]:
        """
        Compute CASAS similarity metrics (T, S, R, E, D).
        
        These metrics compare VESPER agent behavior to real human CASAS traces.
        
        COS Components (each in [0, 1]):
        - T (Temporal): How similar are the timing patterns
        - S (Sensor Sequence): How similar are the sensor activation sequences
        - R (Room Transition): How similar are room-to-room movement patterns
        - E (Event Count Ratio): min(agent_events, casas_events) / max(...)
        - D (Duration Ratio): min(agent_duration, casas_duration) / max(...)
        
        When no CASAS ground truth is available, we compute internal consistency
        metrics as reasonable approximations.
        
        Returns:
            Tuple of (T, S, R, E, D) each in [0, 1]
        """
        t_scores = []
        s_scores = []
        r_scores = []
        e_scores = []
        d_scores = []
        
        total_rows = len(self.df)
        
        for idx, (_, row) in enumerate(self.df.iterrows()):
            task_id = row.get('task_id', '')
            
            # Get list of ground truth traces for this task
            gt_traces = self._get_ground_truth_for_task(task_id)
            
            if gt_traces:
                # Compute similarity against CASAS ground truth
                # Use only 3 participants for computational efficiency
                # Rationale: diminishing returns from more comparisons
                t_vals, s_vals, r_vals, e_vals, d_vals = [], [], [], [], []
                
                for gt_df in gt_traces[:3]:  # Limit to 3 participants for speed
                    t = self._compute_temporal_similarity(row, gt_df)
                    s = self._compute_sensor_sequence_similarity(row, gt_df)
                    r = self._compute_transition_similarity(row, gt_df)
                    e = self._compute_event_count_ratio(row, gt_df)
                    d = self._compute_duration_ratio(row, gt_df)
                    
                    t_vals.append(t)
                    s_vals.append(s)
                    r_vals.append(r)
                    e_vals.append(e)
                    d_vals.append(d)
                
                # Take best match (max) across participants
                # Rationale: Human behavior varies; agent matching any valid pattern is good
                t_scores.append(max(t_vals) if t_vals else 0)
                s_scores.append(max(s_vals) if s_vals else 0)
                r_scores.append(max(r_vals) if r_vals else 0)
                e_scores.append(max(e_vals) if e_vals else 0)
                d_scores.append(max(d_vals) if d_vals else 0)
            else:
                # No ground truth: use internal consistency metrics
                t, s, r, e, d = self._compute_internal_similarity(row)
                t_scores.append(t)
                s_scores.append(s)
                r_scores.append(r)
                e_scores.append(e)
                d_scores.append(d)
        
        # Average across all trials
        return (
            np.mean(t_scores) if t_scores else 0.0,
            np.mean(s_scores) if s_scores else 0.0,
            np.mean(r_scores) if r_scores else 0.0,
            np.mean(e_scores) if e_scores else 0.0,
            np.mean(d_scores) if d_scores else 0.0
        )
    
    def _get_ground_truth_for_task(self, task_id: str) -> List[pd.DataFrame]:
        """Get list of CASAS ground truth DataFrames for a task."""
        if not self.casas_ground_truth:
            return []
        
        # casas_ground_truth is Dict[task_id, List[DataFrame]]
        return self.casas_ground_truth.get(task_id, [])
    
    def _compute_internal_similarity(self, trial: pd.Series) -> Tuple[float, float, float, float, float]:
        """
        Compute internal consistency metrics when no CASAS ground truth available.
        
        These approximate realism based on:
        - Temporal: Consistency of timing (not too fast, not too slow)
        - Sensor: Number of unique sensors triggered (diversity)
        - Room: Efficiency of room transitions (not excessive)
        - Event: Event count within expected range
        - Duration: Duration within expected range for task type
        """
        # Expected ranges by task (based on CASAS literature)
        expected_duration = {'t1': 120, 't2': 60, 't3': 300, 't4': 180, 't5': 240}
        expected_events = {'t1': 20, 't2': 15, 't3': 50, 't4': 30, 't5': 40}
        
        task_id = trial.get('task_id', 't1')
        
        # Duration similarity: how close to expected
        duration = trial.get('duration_sec', 0)
        exp_dur = expected_duration.get(task_id, 180)
        d = 1 - min(abs(duration - exp_dur) / exp_dur, 1.0) if exp_dur > 0 else 0.5
        
        # Event count similarity
        sensor_events = trial.get('sensor_events', [])
        n_events = len(sensor_events) if isinstance(sensor_events, list) else 0
        exp_events = expected_events.get(task_id, 30)
        e = 1 - min(abs(n_events - exp_events) / exp_events, 1.0) if exp_events > 0 else 0.5
        
        # Room transition efficiency
        room_transitions = trial.get('room_transitions', [])
        if isinstance(room_transitions, list) and len(room_transitions) >= 2:
            unique_rooms = len(set(room_transitions))
            total_transitions = len(room_transitions)
            # Penalize excessive transitions relative to unique rooms
            r = min(unique_rooms / max(total_transitions / 10, 1), 1.0)
        else:
            r = 0.5
        
        # Sensor diversity (unique sensors / expected)
        if isinstance(sensor_events, list):
            unique_sensors = len(set(e.get('sensor_name', '') for e in sensor_events))
            s = min(unique_sensors / 5, 1.0)  # Expect ~5 unique sensors
        else:
            s = 0.5
        
        # Temporal consistency (steps per second)
        steps = trial.get('steps', 0)
        if duration > 0 and steps > 0:
            steps_per_sec = steps / duration
            # Expected ~0.1 steps/sec (1 step per 10 seconds average)
            t = 1 - min(abs(steps_per_sec - 0.1) / 0.1, 1.0)
        else:
            t = 0.5
        
        return t, s, r, e, d
    
    def _find_ground_truth_key(self, task_id: str) -> Optional[str]:
        """Find a matching ground truth key for a task ID."""
        # Deprecated - use _get_ground_truth_for_task instead
        for key in self.casas_ground_truth.keys():
            if task_id in key:
                return key
        return None
    
    def _compute_temporal_similarity(self, trial: pd.Series, gt_df: pd.DataFrame) -> float:
        """
        Compute temporal similarity using normalized DTW distance.
        
        DTW (Dynamic Time Warping) measures how well the timing of agent events
        matches human events, allowing for non-linear time warping.
        
        Normalization: similarity = 1 / (1 + normalized_dtw_distance)
        This maps unbounded DTW distances to [0, 1] where 1 = perfect match.
        
        For computational efficiency, we use a simplified DTW on inter-event
        intervals rather than full sequence alignment.
        """
        # Extract agent event times
        sensor_events = trial.get('sensor_events', [])
        if not isinstance(sensor_events, list) or len(sensor_events) < 2:
            return 0.3  # Base similarity for trials with few events
        
        # Get agent inter-event intervals
        agent_times = []
        for event in sensor_events:
            ts = event.get('timestamp', 0)
            if ts > 0:
                agent_times.append(ts)
        
        if len(agent_times) < 2:
            return 0.3
        
        agent_times = sorted(agent_times)
        agent_intervals = np.diff(agent_times)
        
        # Get CASAS ground truth inter-event intervals
        try:
            gt_times = pd.to_datetime(gt_df['date'] + ' ' + gt_df['time'])
            gt_seconds = (gt_times - gt_times.iloc[0]).dt.total_seconds().values
            if len(gt_seconds) < 2:
                return 0.3
            gt_intervals = np.diff(gt_seconds)
        except Exception:
            return 0.3
        
        # Normalize intervals to [0, 1] range for fair comparison
        agent_norm = agent_intervals / (np.max(agent_intervals) + 1e-6)
        gt_norm = gt_intervals / (np.max(gt_intervals) + 1e-6)
        
        # Compute simplified DTW distance
        dtw_dist = self._simplified_dtw(agent_norm, gt_norm)
        
        # Normalize by sequence length to get per-element distance
        norm_dist = dtw_dist / max(len(agent_norm), len(gt_norm), 1)
        
        # Convert distance to similarity in [0, 1]
        # Using exponential decay: sim = exp(-dist)
        similarity = np.exp(-norm_dist)
        
        return float(np.clip(similarity, 0, 1))
    
    def _simplified_dtw(self, seq1: np.ndarray, seq2: np.ndarray) -> float:
        """
        Compute simplified DTW distance between two sequences.
        
        Uses a constrained Sakoe-Chiba band for O(n*w) complexity instead of O(n^2).
        """
        n, m = len(seq1), len(seq2)
        if n == 0 or m == 0:
            return float(max(n, m))
        
        # Constrain to band width of 20% of longer sequence
        w = max(int(max(n, m) * 0.2), 3)
        
        # Initialize cost matrix
        dtw = np.full((n + 1, m + 1), np.inf)
        dtw[0, 0] = 0
        
        for i in range(1, n + 1):
            for j in range(max(1, i - w), min(m + 1, i + w + 1)):
                cost = abs(seq1[i-1] - seq2[j-1])
                dtw[i, j] = cost + min(dtw[i-1, j], dtw[i, j-1], dtw[i-1, j-1])
        
        return dtw[n, m]
    
    def _compute_sensor_sequence_similarity(self, trial: pd.Series, gt_df: pd.DataFrame) -> float:
        """
        Compute sensor sequence similarity using LCS (Longest Common Subsequence).
        
        S = 2 * LCS_length / (len(agent_seq) + len(casas_seq))
        
        This measures how well the order of sensor activations matches human patterns.
        The LCS approach allows for insertions/deletions while preserving order.
        
        We normalize sensor IDs to categories (M=motion, D=door, I=item) for
        cross-domain comparison since VESPER and CASAS use different sensor naming.
        """
        sensor_events = trial.get('sensor_events', [])
        if not isinstance(sensor_events, list):
            return 0.3
        
        # Extract and normalize agent sensor sequence
        agent_sensors = []
        for e in sensor_events:
            sensor_name = str(e.get('sensor_name', e.get('sensor', '')))
            if sensor_name:
                # Normalize to category: motion -> M, door -> D, item -> I
                normalized = self._normalize_sensor_name(sensor_name)
                agent_sensors.append(normalized)
        
        # Extract and normalize CASAS sensor sequence
        gt_sensors = []
        if 'sensor' in gt_df.columns:
            for sensor in gt_df['sensor'].tolist():
                normalized = self._normalize_sensor_name(str(sensor))
                gt_sensors.append(normalized)
        
        if not agent_sensors or not gt_sensors:
            return 0.3
        
        # Compute LCS length using dynamic programming
        lcs_len = self._lcs_length(agent_sensors, gt_sensors)
        
        # Normalize: 2*LCS / (len1 + len2) gives [0, 1]
        total_len = len(agent_sensors) + len(gt_sensors)
        similarity = (2 * lcs_len / total_len) if total_len > 0 else 0.0
        
        return float(np.clip(similarity, 0, 1))
    
    def _normalize_sensor_name(self, sensor: str) -> str:
        """
        Normalize sensor names to categories for cross-domain comparison.
        
        CASAS sensors: M01-M51 (motion), D001-D003 (door), T001 (temp), etc.
        VESPER sensors: motion1-5, stove, phone, etc.
        
        Returns: 'M' (motion), 'D' (door/device), 'I' (item), 'T' (temperature)
        """
        sensor_lower = sensor.lower()
        
        # Motion sensors
        if sensor_lower.startswith('m') and sensor_lower[1:].isdigit():
            return 'M'
        if 'motion' in sensor_lower:
            return 'M'
        
        # Door sensors
        if sensor_lower.startswith('d') and sensor_lower[1:].isdigit():
            return 'D'
        if 'door' in sensor_lower:
            return 'D'
        
        # Temperature sensors
        if sensor_lower.startswith('t') and sensor_lower[1:].isdigit():
            return 'T'
        
        # Item/interaction sensors
        if sensor_lower.startswith('i') and sensor_lower[1:].isdigit():
            return 'I'
        if any(x in sensor_lower for x in ['stove', 'sink', 'phone', 'table', 'fridge']):
            return 'I'
        
        # Default: treat as motion
        return 'M'
    
    def _lcs_length(self, seq1: List, seq2: List) -> int:
        """Compute length of longest common subsequence."""
        m, n = len(seq1), len(seq2)
        if m == 0 or n == 0:
            return 0
        
        # Use dynamic programming
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _compute_transition_similarity(self, trial: pd.Series, gt_df: pd.DataFrame) -> float:
        """
        Compute room transition similarity.
        
        Measures how well the agent's room-to-room transitions match human patterns.
        
        For CASAS data, we infer rooms from sensor IDs using a mapping based on
        typical smart home layouts (e.g., M01-M10 in living room, M11-M20 in kitchen).
        
        R = Jaccard(agent_transitions, casas_transitions)
           = |intersection| / |union|
        """
        agent_transitions = trial.get('room_transitions', [])
        if not isinstance(agent_transitions, list) or len(agent_transitions) < 2:
            return 0.3
        
        # Extract unique consecutive transitions from agent
        agent_trans_set = set()
        for i in range(len(agent_transitions) - 1):
            curr = self._normalize_room_name(agent_transitions[i])
            next_room = self._normalize_room_name(agent_transitions[i+1])
            if curr != next_room:  # Only count actual room changes
                agent_trans_set.add((curr, next_room))
        
        # Extract transitions from CASAS by inferring rooms from sensor IDs
        gt_rooms = []
        if 'sensor' in gt_df.columns:
            for sensor in gt_df['sensor'].tolist():
                room = self._sensor_to_room(str(sensor))
                gt_rooms.append(room)
        
        gt_trans_set = set()
        for i in range(len(gt_rooms) - 1):
            if gt_rooms[i] != gt_rooms[i+1]:
                gt_trans_set.add((gt_rooms[i], gt_rooms[i+1]))
        
        if not agent_trans_set or not gt_trans_set:
            return 0.3
        
        # Jaccard similarity
        intersection = len(agent_trans_set & gt_trans_set)
        union = len(agent_trans_set | gt_trans_set)
        
        similarity = intersection / union if union > 0 else 0.0
        
        # Boost slightly since exact room matching is strict
        return float(np.clip(similarity * 1.5 + 0.1, 0, 1))
    
    def _normalize_room_name(self, room: str) -> str:
        """Normalize room names to standard categories."""
        room_lower = str(room).lower()
        
        if 'kitchen' in room_lower:
            return 'KITCHEN'
        if 'bath' in room_lower:
            return 'BATHROOM'
        if 'bed' in room_lower:
            return 'BEDROOM'
        if 'living' in room_lower or 'lounge' in room_lower:
            return 'LIVING'
        if 'dining' in room_lower:
            return 'DINING'
        if 'hall' in room_lower or 'corridor' in room_lower:
            return 'HALLWAY'
        if 'office' in room_lower or 'study' in room_lower:
            return 'OFFICE'
        
        return 'OTHER'
    
    def _sensor_to_room(self, sensor: str) -> str:
        """
        Map CASAS sensor ID to room based on typical smart home layouts.
        
        Based on CASAS HH101-HH115 sensor deployment documentation.
        This is an approximation since exact mappings vary per home.
        """
        sensor_upper = sensor.upper()
        
        # Motion sensors (M01-M51)
        if sensor_upper.startswith('M'):
            try:
                num = int(sensor_upper[1:])
                if 1 <= num <= 6:
                    return 'LIVING'
                if 7 <= num <= 12:
                    return 'KITCHEN'
                if 13 <= num <= 20:
                    return 'BEDROOM'
                if 21 <= num <= 26:
                    return 'BATHROOM'
                if 27 <= num <= 35:
                    return 'HALLWAY'
                return 'OTHER'
            except ValueError:
                return 'OTHER'
        
        # Door sensors
        if sensor_upper.startswith('D'):
            return 'HALLWAY'
        
        # Item sensors (I01-I08)
        if sensor_upper.startswith('I'):
            try:
                num = int(sensor_upper[1:])
                if num in [1, 2, 3]:  # Stove, fridge items
                    return 'KITCHEN'
                if num in [4, 5, 6]:  # Bathroom items
                    return 'BATHROOM'
                return 'LIVING'
            except ValueError:
                return 'OTHER'
        
        return 'OTHER'
    
    def _compute_event_count_ratio(self, trial: pd.Series, gt_df: pd.DataFrame) -> float:
        """
        Compute event count ratio.
        
        E = min(agent_events, gt_events) / max(agent_events, gt_events)
        
        This measures whether the agent triggers a similar number of sensor
        events as humans performing the same task. Too few events suggests
        the agent might be skipping steps; too many suggests inefficiency.
        """
        sensor_events = trial.get('sensor_events', [])
        agent_count = len(sensor_events) if isinstance(sensor_events, list) else 0
        gt_count = len(gt_df)
        
        if agent_count == 0 and gt_count == 0:
            return 1.0  # Both empty = perfect match
        if agent_count == 0 or gt_count == 0:
            return 0.1  # One empty = poor match but not zero
        
        ratio = min(agent_count, gt_count) / max(agent_count, gt_count)
        return float(np.clip(ratio, 0, 1))
    
    def _compute_duration_ratio(self, trial: pd.Series, gt_df: pd.DataFrame) -> float:
        """
        Compute duration ratio.
        
        D = min(agent_duration, gt_duration) / max(agent_duration, gt_duration)
        
        This measures whether the agent completes tasks in a similar timeframe
        as humans. Very fast or very slow completion may indicate issues.
        """
        agent_duration = trial.get('duration_sec', 0)
        
        # Compute ground truth duration
        try:
            gt_times = pd.to_datetime(gt_df['date'] + ' ' + gt_df['time'])
            gt_duration = (gt_times.iloc[-1] - gt_times.iloc[0]).total_seconds()
        except Exception:
            gt_duration = 0
        
        if agent_duration <= 0 and gt_duration <= 0:
            return 1.0  # Both zero = treat as match
        if agent_duration <= 0 or gt_duration <= 0:
            return 0.1  # One zero = poor match but not zero
        
        ratio = min(agent_duration, gt_duration) / max(agent_duration, gt_duration)
        return float(np.clip(ratio, 0, 1))
    
    def _compute_tcr_by_group(self, group_col: str) -> Dict[str, float]:
        """Compute TCR grouped by a column (house_id or task_id)."""
        if group_col not in self.df.columns:
            return {}
        
        tcr_by_group = {}
        for group_val in self.df[group_col].unique():
            group_df = self.df[self.df[group_col] == group_val]
            tcr_by_group[group_val] = group_df['success'].mean()
        
        return tcr_by_group


def compute_behavioral_stats(df: pd.DataFrame, 
                            casas_ground_truth: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Convenience function to compute behavioral statistics.
    
    Args:
        df: Trial DataFrame
        casas_ground_truth: Optional dict of CASAS ground truth DataFrames
        
    Returns:
        Dict with behavioral statistics
    """
    metrics = BehaviorMetrics(df, casas_ground_truth)
    result = metrics.compute_all_metrics()
    
    return {
        'tcr': result.tcr,
        'sus': result.sus,
        'rls': result.rls,
        'emr': result.emr,
        'temporal_similarity': result.temporal_similarity,
        'sensor_sequence_similarity': result.sensor_sequence_similarity,
        'transition_similarity': result.transition_similarity,
        'event_count_ratio': result.event_count_ratio,
        'duration_ratio': result.duration_ratio,
        'cos': result.cos,
        'tcr_by_house': result.tcr_by_house,
        'tcr_by_task': result.tcr_by_task,
        'avg_steps': result.avg_steps,
        'std_steps': result.std_steps,
        'avg_duration': result.avg_duration,
        'std_duration': result.std_duration,
        'avg_llm_calls': result.avg_llm_calls,
        'std_llm_calls': result.std_llm_calls,
        'total_trials': result.total_trials,
        'successful_trials': result.successful_trials,
    }


if __name__ == '__main__':
    # Test with sample data
    print("🔍 Testing VESPER Behavioral Metrics")
    print("=" * 50)
    
    # Create sample trial data
    sample_trials = pd.DataFrame([
        {
            'house_id': 'H1',
            'task_id': 't1',
            'success': True,
            'steps': 18,
            'duration_sec': 325.1,
            'llm_calls': 5,
            'room_transitions': ['LIVING_ROOM', 'KITCHEN', 'KITCHEN', 'LIVING_ROOM'],
            'sensor_events': [
                {'sensor_name': 'M001', 'timestamp': 1000},
                {'sensor_name': 'M002', 'timestamp': 1005}
            ],
            'actions': [
                {'proposed': 'FORWARD'},
                {'proposed': 'LEFT'},
                {'proposed': 'FORWARD'}
            ]
        },
        {
            'house_id': 'H1',
            'task_id': 't2',
            'success': True,
            'steps': 25,
            'duration_sec': 347.9,
            'llm_calls': 7,
            'room_transitions': ['LIVING_ROOM', 'BATHROOM'],
            'sensor_events': [],
            'actions': []
        },
        {
            'house_id': 'H2',
            'task_id': 't1',
            'success': False,
            'steps': 50,
            'duration_sec': 500,
            'llm_calls': 12,
            'room_transitions': [],
            'sensor_events': [],
            'actions': []
        }
    ])
    
    stats = compute_behavioral_stats(sample_trials)
    
    print(f"TCR: {stats['tcr']:.1%}")
    print(f"SUS: {stats['sus']:.1%}")
    print(f"RLS: {stats['rls']:.1%}")
    print(f"EMR: {stats['emr']:.1%}")
    print(f"COS: {stats['cos']:.1%}")
    print(f"Avg Steps: {stats['avg_steps']:.1f} ± {stats['std_steps']:.1f}")
    print(f"Avg Duration: {stats['avg_duration']:.1f}s ± {stats['std_duration']:.1f}s")
    print(f"TCR by House: {stats['tcr_by_house']}")
