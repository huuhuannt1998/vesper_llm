#!/usr/bin/env python3
"""
VESPER V2 Evaluation Runner
===========================

Main orchestrator for running the complete VESPER evaluation pipeline.

Usage:
    python run_eval.py                    # Run full evaluation
    python run_eval.py --tables-only      # Generate tables only
    python run_eval.py --stats-only       # Run statistical tests only
    python run_eval.py --house H1         # Evaluate specific house

Output:
    - CSV files with raw metrics
    - LaTeX table snippets for paper
    - JSON summary for archiving
    - Console output with key findings
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add analysis directory to path
sys.path.insert(0, str(Path(__file__).parent))

from analysis.loader import TrialDataLoader, load_casas_ground_truth
from analysis.metrics_safety import SafetyMetrics, compute_violation_stats
from analysis.metrics_behavior import BehaviorMetrics, compute_behavioral_stats
from analysis.stats_tests import StatisticalTests, format_stat_result_latex
from analysis.export_tables import TableExporter


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_metric(name: str, value: float, fmt: str = ".1%"):
    """Print a formatted metric."""
    if fmt == ".1%":
        print(f"  {name}: {value*100:.1f}%")
    elif fmt == ".2f":
        print(f"  {name}: {value:.2f}")
    elif fmt == ".1f":
        print(f"  {name}: {value:.1f}")
    else:
        print(f"  {name}: {value}")


def run_full_evaluation(args):
    """Run the complete VESPER V2 evaluation pipeline."""
    
    print_header("VESPER V2 Evaluation Pipeline")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Output directory: {args.output_dir}")
    
    # =========================================================================
    # 1. LOAD DATA
    # =========================================================================
    print_header("1. Loading Trial Data")
    
    loader = TrialDataLoader(args.data_dir)
    df = loader.load_all_trials()
    
    print(f"  Total trials loaded: {len(df)}")
    print(f"  Houses: {df['house_id'].unique().tolist()}")
    print(f"  Tasks: {df['task_id'].unique().tolist()}")
    print(f"  Modes: {df['mode'].unique().tolist()}")
    print(f"  Conditions: {df['condition'].unique().tolist()}")
    
    if df.empty:
        print("\n⚠️  No trial data found! Creating synthetic data for testing...")
        df = create_synthetic_data()
        print(f"  Created {len(df)} synthetic trials")
    
    # Filter by house if specified
    if args.house:
        df = df[df['house_id'] == args.house]
        print(f"  Filtered to house {args.house}: {len(df)} trials")
    
    # Split by mode
    baseline_df = df[df['mode'] == 'baseline']
    enforced_df = df[df['mode'] == 'enforced']
    
    print(f"\n  Baseline trials: {len(baseline_df)}")
    print(f"  Enforced trials: {len(enforced_df)}")
    
    # Load CASAS ground truth
    casas_gt = load_casas_ground_truth()
    print(f"  CASAS ground truth files: {len(casas_gt)}")
    
    # =========================================================================
    # 2. COMPUTE SAFETY METRICS
    # =========================================================================
    print_header("2. Safety Metrics")
    
    safety_metrics = SafetyMetrics(df)
    safety_result = safety_metrics.compute_all_metrics(baseline_df, enforced_df)
    
    print("\n  📊 Baseline Violation Rates:")
    print_metric("    Overall VR", safety_result.violation_rate)
    print_metric("    VCT (per trial)", safety_result.violation_count_per_trial, ".2f")
    
    print("\n  📊 VR by Category (Baseline):")
    for cat, vr in safety_result.vr_by_category.items():
        print_metric(f"    {cat}", vr)
    
    print("\n  📊 VR by House (Baseline):")
    for house, vr in safety_result.vr_by_house.items():
        print_metric(f"    {house}", vr)
    
    print("\n  🛡️ Enforcement Effectiveness:")
    print_metric("    Prevention Rate (PR)", safety_result.prevention_rate)
    print_metric("    False Positive Rate (FPR)", safety_result.false_positive_rate)
    print_metric("    Recovery Success Rate (RSR)", safety_result.recovery_success_rate)
    
    # =========================================================================
    # 3. COMPUTE BEHAVIORAL METRICS
    # =========================================================================
    print_header("3. Behavioral Metrics")
    
    # Baseline
    behavior_baseline = BehaviorMetrics(baseline_df, casas_gt)
    baseline_result = behavior_baseline.compute_all_metrics()
    
    print("\n  📊 Baseline Performance:")
    print_metric("    TCR (Task Completion Rate)", baseline_result.tcr)
    print_metric("    SUS (Semantic Understanding)", baseline_result.sus)
    print_metric("    RLS (Room Label Stability)", baseline_result.rls)
    print_metric("    EMR (Effective Movement Ratio)", baseline_result.emr)
    
    print("\n  📊 CASAS Similarity (Baseline):")
    print_metric("    COS (Overall Similarity)", baseline_result.cos)
    print_metric("    T (Temporal)", baseline_result.temporal_similarity)
    print_metric("    S (Sensor Sequence)", baseline_result.sensor_sequence_similarity)
    print_metric("    R (Transition)", baseline_result.transition_similarity)
    print_metric("    E (Event Count)", baseline_result.event_count_ratio)
    print_metric("    D (Duration)", baseline_result.duration_ratio)
    
    print("\n  📊 TCR by House:")
    for house, tcr in baseline_result.tcr_by_house.items():
        print_metric(f"    {house}", tcr)
    
    print("\n  📊 TCR by Task:")
    for task, tcr in baseline_result.tcr_by_task.items():
        print_metric(f"    {task}", tcr)
    
    print(f"\n  📊 Efficiency Statistics (successful trials):")
    print(f"    Avg Steps: {baseline_result.avg_steps:.1f} ± {baseline_result.std_steps:.1f}")
    print(f"    Avg Duration: {baseline_result.avg_duration:.1f}s ± {baseline_result.std_duration:.1f}s")
    print(f"    Avg LLM Calls: {baseline_result.avg_llm_calls:.1f} ± {baseline_result.std_llm_calls:.1f}")
    
    # Enforced (if data available)
    enforced_result = None
    if not enforced_df.empty:
        behavior_enforced = BehaviorMetrics(enforced_df, casas_gt)
        enforced_result = behavior_enforced.compute_all_metrics()
        
        print("\n  📊 Enforced Performance:")
        print_metric("    TCR", enforced_result.tcr)
        print_metric("    COS", enforced_result.cos)
        
        # Compare
        tcr_delta = enforced_result.tcr - baseline_result.tcr
        cos_delta = enforced_result.cos - baseline_result.cos
        print(f"\n  📊 Enforcement Impact:")
        print(f"    ΔTCR: {tcr_delta*100:+.1f}%")
        print(f"    ΔCOS: {cos_delta*100:+.1f}%")
    
    # =========================================================================
    # 4. STATISTICAL TESTS
    # =========================================================================
    if not args.tables_only:
        print_header("4. Statistical Tests")
        
        stat_tests = StatisticalTests()
        stat_results = stat_tests.run_all_comparisons(df)
        
        # Complexity vs Success
        if 'complexity_vs_success' in stat_results.get('summary', {}):
            result = stat_results['summary']['complexity_vs_success']
            print("\n  📊 Environment Complexity vs Success:")
            print(f"    Test: {result.test_name}")
            print(f"    χ² = {result.statistic:.1f}, p = {result.p_value:.4f}")
            print(f"    Effect size (Cramér's V) = {result.effect_size:.2f}")
            print(f"    Significant: {'Yes' if result.significant else 'No'}")
            print(f"    Interpretation: {result.interpretation}")
        
        # Across houses ANOVA
        for metric, result in stat_results.get('across_houses', {}).items():
            print(f"\n  📊 ANOVA for {metric} across houses:")
            print(f"    F = {result.statistic:.2f}, p = {result.p_value:.4f}")
            print(f"    η² = {result.effect_size:.3f}")
            print(f"    Interpretation: {result.interpretation}")
    
    # =========================================================================
    # 5. EXPORT TABLES
    # =========================================================================
    print_header("5. Exporting Tables")
    
    exporter = TableExporter(args.output_dir)
    
    # Prepare stats dicts for export
    baseline_stats = {
        'tcr': baseline_result.tcr,
        'sus': baseline_result.sus,
        'rls': baseline_result.rls,
        'emr': baseline_result.emr,
        'cos': baseline_result.cos,
        'temporal_similarity': baseline_result.temporal_similarity,
        'sensor_sequence_similarity': baseline_result.sensor_sequence_similarity,
        'transition_similarity': baseline_result.transition_similarity,
        'event_count_ratio': baseline_result.event_count_ratio,
        'duration_ratio': baseline_result.duration_ratio
    }
    
    enforced_stats = None
    if enforced_result:
        enforced_stats = {
            'tcr': enforced_result.tcr,
            'sus': enforced_result.sus,
            'rls': enforced_result.rls,
            'emr': enforced_result.emr,
            'cos': enforced_result.cos,
            'temporal_similarity': enforced_result.temporal_similarity,
            'sensor_sequence_similarity': enforced_result.sensor_sequence_similarity,
            'transition_similarity': enforced_result.transition_similarity,
            'event_count_ratio': enforced_result.event_count_ratio,
            'duration_ratio': enforced_result.duration_ratio
        }
    
    table_results = exporter.export_all_tables(df, baseline_stats, enforced_stats)
    
    # =========================================================================
    # 6. SUMMARY
    # =========================================================================
    print_header("6. Evaluation Summary")
    
    print("\n  📊 Key Findings:")
    print(f"    • Baseline TCR: {baseline_result.tcr*100:.1f}%")
    print(f"    • Overall VR (baseline): {safety_result.violation_rate*100:.1f}%")
    print(f"    • Prevention Rate: {safety_result.prevention_rate*100:.1f}%")
    print(f"    • CASAS Similarity (COS): {baseline_result.cos*100:.1f}%")
    
    print("\n  📁 Output Files:")
    print(f"    • {args.output_dir}/task_success.csv")
    print(f"    • {args.output_dir}/safety_violations.csv")
    print(f"    • {args.output_dir}/casas_comparison.csv")
    print(f"    • {args.output_dir}/all_tables.tex")
    print(f"    • {args.output_dir}/evaluation_summary.json")
    
    print(f"\n✅ Evaluation completed: {datetime.now().isoformat()}")
    
    return {
        'safety': safety_result,
        'baseline_behavior': baseline_result,
        'enforced_behavior': enforced_result,
        'tables': table_results
    }


def create_synthetic_data():
    """Create synthetic trial data for testing when no real data is available."""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    
    trials = []
    
    houses = ['H1', 'H2', 'H3']
    tasks = ['t1', 't2', 't3', 't4', 't5']
    modes = ['baseline', 'enforced']
    
    # Success rates by house (decreasing with complexity)
    success_rates = {'H1': 0.96, 'H2': 0.88, 'H3': 0.68}
    
    # Violation rates by house (increasing with complexity)
    violation_rates = {'H1': 0.32, 'H2': 0.42, 'H3': 0.58}
    
    for house in houses:
        for task in tasks:
            for mode in modes:
                # Generate 30 trials per combination
                for trial_num in range(30):
                    # Adjust success rate for enforcement
                    sr = success_rates[house]
                    if mode == 'enforced':
                        sr *= 0.97  # Slight reduction due to blocked completions
                    
                    success = np.random.random() < sr
                    
                    # Generate violations
                    violations = []
                    if mode == 'baseline' and np.random.random() < violation_rates[house]:
                        categories = ['appliance_safety', 'entry_security', 'sensor_integrity', 'spatial_temporal']
                        n_violations = np.random.randint(1, 3)
                        for _ in range(n_violations):
                            violations.append({
                                'category': np.random.choice(categories),
                                'rule_id': 'synthetic_rule',
                                'step': np.random.randint(1, 20)
                            })
                    
                    # Generate steps and duration
                    base_steps = {'t1': 18, 't2': 25, 't3': 42, 't4': 22, 't5': 38}
                    house_mult = {'H1': 1.0, 'H2': 1.2, 'H3': 1.5}
                    
                    steps = int(base_steps[task] * house_mult[house] * np.random.normal(1, 0.1))
                    duration = steps * np.random.normal(12, 2)
                    llm_calls = max(1, int(steps / 3))
                    
                    trials.append({
                        'house_id': house,
                        'task_id': task,
                        'task_name': f'Task {task}',
                        'condition': 'benign',
                        'mode': mode,
                        'trial_id': f'{house}_{task}_{mode}_{trial_num}',
                        'success': success,
                        'steps': steps,
                        'duration_sec': duration,
                        'llm_calls': llm_calls,
                        'violations': violations,
                        'actions': [],
                        'sensor_events': [],
                        'room_transitions': ['LIVING_ROOM', 'KITCHEN'] if success else [],
                        'screenshots': steps,
                        'source_file': 'synthetic'
                    })
    
    return pd.DataFrame(trials)


def main():
    parser = argparse.ArgumentParser(
        description='VESPER V2 Evaluation Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_eval.py                         # Full evaluation
    python run_eval.py --house H1              # Evaluate House 1 only
    python run_eval.py --tables-only           # Generate tables only
    python run_eval.py --output-dir results/   # Custom output directory
        """
    )
    
    parser.add_argument('--data-dir', type=str, default=None,
                        help='Base directory for VESPER project')
    parser.add_argument('--output-dir', type=str, default='analysis/results',
                        help='Output directory for results')
    parser.add_argument('--house', type=str, choices=['H1', 'H2', 'H3'],
                        help='Evaluate specific house only')
    parser.add_argument('--tables-only', action='store_true',
                        help='Generate tables without statistical tests')
    parser.add_argument('--stats-only', action='store_true',
                        help='Run statistical tests only')
    parser.add_argument('--synthetic', action='store_true',
                        help='Use synthetic data for testing')
    
    args = parser.parse_args()
    
    # Create output directory
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        results = run_full_evaluation(args)
        return 0
    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
