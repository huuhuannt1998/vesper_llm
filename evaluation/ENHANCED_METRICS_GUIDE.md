# VESPER Enhanced Evaluation Metrics System

## Overview

The VESPER navigation system now includes comprehensive logging and evaluation metrics that track all aspects of navigation performance according to research paper standards. The system automatically captures detailed data during navigation sessions and generates research-quality metrics.

## Research Metrics Implemented

### 1. Reported Task Success Rate (RTSR)
**Formula:** `RTSR = (# tasks flagged "completed" by controller) / (# tasks issued) × 100`

Measures the fraction of tasks that the controller itself marked as complete. This reflects the system's self-reported success.

### 2. Semantic Task Success Rate (STSR)  
**Formula:** `STSR = (# tasks judged complete by manual review) / (# tasks issued) × 100`

Measures tasks judged complete through automated log review. A task is successful only if logs indicate the agent actually reached the intended room with correct room detection.

### 3. Effective Movement Ratio (EMR)
**Formula:** `EMR = (# non-STAY actions) / (# total actions) × 100`

Captures how often the agent executed meaningful movements. Higher values indicate more active and exploratory behavior rather than idle staying.

### 4. Oscillation Index (OI)
Measures the proportion of step triples that contained immediate reversals (LEFT→RIGHT, UP→DOWN, A→B→A patterns), indicating indecision or unstable navigation.

### 5. Room-Label Stability (RLS)
**Formula:** `RLS = (# concrete room labels) / (# total room detections) × 100`

Fraction of steps where the model provided concrete room labels (LIVING_ROOM, KITCHEN) rather than UNKNOWN, reflecting stability in room classification.

### 6. Timeout Rate (TR)
**Formula:** `TR = (# timeout calls) / (# total LLM calls) × 100`

Records the fraction of LLM calls that failed to respond within the 180-second timeout window.

## System Components

### 1. Enhanced Navigation Logger (`llm_bge_navigation.py`)
- **VESPERMetricsLogger class**: Comprehensive logging system
- **Automatic session tracking**: Creates timestamped log files
- **Real-time metrics**: Tracks steps, screenshots, LLM calls, timeouts
- **Task completion validation**: Semantic verification of task success

### 2. Log Analyzer (`evaluation/log_analyzer.py`)
- **VESPERLogAnalyzer class**: Processes navigation logs
- **Research metrics calculation**: All 6 research metrics implemented
- **LaTeX output generation**: Ready-to-use tables for papers
- **Comprehensive reporting**: Detailed analysis with failure reasons

### 3. Evaluation Runner (`evaluation/run_evaluation.py`)
- **Real-time monitoring**: Watches for new log files
- **Automatic analysis**: Processes logs as they're created
- **Results storage**: Saves detailed metrics for research tracking

## Usage Guide

### Running Navigation with Enhanced Logging

1. **Start Navigation Session**:
   ```bash
   # In Blender BGE, the enhanced logging automatically activates
   # Look for: "📊 VESPER: Metrics logging initialized"
   ```

2. **Monitor Real-time Metrics**:
   ```
   📊 METRICS: Starting task 1: 'Cook in kitchen'
   📸 METRICS: Screenshot 1 captured - Analysis #1
   🧠 METRICS: LLM Call 1 (2.3s) - Room: LIVING_ROOM, Task Complete: False
   📊 METRICS: Step 1 - LEFT from [-2.0, -0.6] to [-2.3, -0.6]
   ```

3. **View Session Summary**:
   ```
   📊 VESPER NAVIGATION METRICS SUMMARY
   ⏱️  Session Duration: 120.5s
   🎯 Tasks Completed: 2/3 (66.7%)
   👣 Total Steps: 15
   📸 Screenshots Taken: 8
   🧠 LLM Calls Made: 8
   ```

### Analyzing Results

1. **Real-time Analysis**:
   ```bash
   cd evaluation
   python run_evaluation.py
   # Choose option 1 for real-time monitoring
   ```

2. **Analyze Latest Session**:
   ```bash
   cd evaluation
   python run_evaluation.py
   # Choose option 2 for latest log analysis
   ```

3. **Manual Analysis**:
   ```python
   from evaluation.log_analyzer import VESPERLogAnalyzer
   analyzer = VESPERLogAnalyzer("path/to/log/file.json")
   metrics = analyzer.generate_detailed_metrics()
   ```

### Output Files

1. **Navigation Logs**: `blender/evaluation_logs/vesper_navigation_log_TIMESTAMP.json`
   - Complete session data with all navigation details
   - Movement paths, room detections, LLM responses
   - Timing information, timeout tracking

2. **Analysis Results**: `evaluation/results/evaluation_results_TIMESTAMP.json`
   - Research metrics calculations
   - Additional performance metrics
   - Failure analysis and recommendations

### LaTeX Integration

The system automatically generates LaTeX-formatted tables:

```latex
\begin{table}[h]
\centering
\begin{tabular}{|l|c|}
\hline
\textbf{Metric} & \textbf{Value} \\
\hline
RTSR (Reported Task Success Rate) & 66.7\% \\
STSR (Semantic Task Success Rate) & 66.7\% \\
EMR (Effective Movement Ratio) & 86.7\% \\
OI (Oscillation Index) & 77.8\% \\
RLS (Room-Label Stability) & 75.0\% \\
TR (Timeout Rate) & 12.5\% \\
\hline
\end{tabular}
\caption{VESPER Navigation System Performance Metrics}
\label{tab:vesper_metrics}
\end{table}
```

## Key Features

### ✅ Automatic Data Collection
- No manual intervention required
- Captures all navigation events in real-time
- Preserves complete audit trail for research reproducibility

### ✅ Research-Standard Metrics
- Implements all metrics from research paper specifications
- Provides both controller-reported and semantically-verified success rates
- Includes movement quality and stability measures

### ✅ Real-time Monitoring
- Live feedback during navigation sessions
- Immediate identification of issues (timeouts, oscillations, failures)
- Performance tracking across multiple sessions

### ✅ Export-Ready Results
- LaTeX tables ready for academic papers
- JSON format for further analysis
- Human-readable summaries for quick assessment

## Example Output

```
🔬 RESEARCH METRICS:
   RTSR (Reported Task Success Rate): 66.7%
   STSR (Semantic Task Success Rate): 66.7%
   EMR (Effective Movement Ratio): 86.7%
   OI (Oscillation Index): 77.8%
   RLS (Room-Label Stability): 75.0%
   TR (Timeout Rate): 12.5%

📊 ADDITIONAL METRICS:
🎯 Task Success Rate: 66.7% (2/3)
👣 Average Steps per Task: 5.0
⚡ Average Completion Time: 38.7s
🧠 LLM Calls per Task: 2.7
🏠 Room Detection Accuracy: 85.0%
📊 Overall Performance Score: 72.3/100
```

This enhanced evaluation system provides comprehensive research-quality metrics for evaluating VESPER's navigation performance, making it suitable for academic publication and detailed performance analysis.
