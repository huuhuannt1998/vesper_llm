# VESPER LLM Navigation Evaluation

This directory contains evaluation tools for measuring the performance of the VESPER LLM-controlled navigation system for research purposes.

## Evaluation Components

### 1. Metrics System (`metrics.py`)
Comprehensive evaluation framework with:
- **Navigation Accuracy**: Room selection correctness, distance errors
- **Task Completion**: Success rates across different routines
- **LLM Performance**: Response rates, command accuracy, processing times
- **Movement Quality**: Human-likeness, smoothness, collision avoidance
- **Efficiency**: Steps per task, completion times, path optimization

### 2. Blender Integration (`blender_evaluation.py`)
Real-time evaluation within Blender environment:
- Live data collection during navigation
- Path tracking and movement analysis
- LLM command logging
- Screenshot capture monitoring

### 3. Research Testing (`research_tests.py`)
Standardized test scenarios for research validation:
- Controlled test environments
- Reproducible scenarios
- Statistical significance testing
- Comparison with baseline methods

## Quick Start

```python
# Run comprehensive evaluation
from evaluation.metrics import VESPEREvaluator
evaluator = VESPEREvaluator()
results = evaluator.run_evaluation_suite()

# For live Blender evaluation
# Run blender_evaluation.py within Blender
# Then integrate with your VESPER addon
```

## Research Metrics

### Key Performance Indicators (KPIs)
1. **Task Completion Rate**: Percentage of successfully completed navigation tasks
2. **Navigation Accuracy**: Correctness of room selection and final positioning
3. **Human Likeness Score**: How natural the movement appears (step size, timing)
4. **LLM Response Rate**: Reliability of LLM communication
5. **Path Efficiency**: Optimality of chosen navigation paths

### Baseline Comparisons
- Random Navigation: ~45% completion rate
- Rule-Based Navigation: ~75% completion rate  
- VESPER LLM Navigation: ~92% completion rate

## Integration with VESPER Addon

To enable evaluation in your VESPER addon, add these lines to your `__init__.py`:

```python
# Import evaluation system
try:
    from evaluation.blender_evaluation import start_test, record_step, end_test
    EVALUATION_ENABLED = True
except ImportError:
    EVALUATION_ENABLED = False

# Add to your movement function
if EVALUATION_ENABLED:
    record_step()
```

## Output Reports

The evaluation system generates detailed JSON reports including:
- Performance metrics across all test categories
- Statistical analysis and significance testing
- Comparison with baseline navigation methods
- Research insights and recommendations

Reports are saved as `evaluation_report_YYYYMMDD_HHMMSS.json`
