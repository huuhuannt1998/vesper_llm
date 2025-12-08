"""
VESPER V2 Table Exporter
========================

Export computed metrics to:
- CSV files for data analysis
- LaTeX table rows for paper inclusion
- JSON summaries for archiving

Tables to generate (matching paper structure):
- Table 1 (tab:task_success_all): Baseline task performance
- Table 2 (tab:safety_violations): Safety violations by category and house
- Table 3 (tab:stress_test_violations): Safety-critical stress test results
- Table 4 (tab:casas_stats): Behavioral comparison with CASAS
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TableConfig:
    """Configuration for a table export."""
    table_id: str
    caption: str
    label: str
    columns: List[str]
    column_headers: List[str]


# Table configurations matching paper structure
TABLE_CONFIGS = {
    'task_success_all': TableConfig(
        table_id='tab:task_success_all',
        caption='Baseline task performance (no safety enforcement). Success Rate = proportion of trials completed; '
                'Avg. Steps, Duration, and LLM Calls are per successful trial (mean ± SD).',
        label='tab:task_success_all',
        columns=['task', 'success', 'avg_steps', 'avg_duration', 'avg_llm_calls'],
        column_headers=['Task', 'Success', 'Avg Steps', 'Avg Duration (s)', 'Avg LLM Calls']
    ),
    'safety_violations': TableConfig(
        table_id='tab:safety_violations',
        caption='Safety violations by rule category and house, with and without VESPER\'s Safety Enforcement Layer.',
        label='tab:safety_violations',
        columns=['category', 'vr_b_h1', 'vr_e_h1', 'pr_h1', 'vr_b_h2', 'vr_e_h2', 'pr_h2', 'vr_b_h3', 'vr_e_h3', 'pr_h3'],
        column_headers=['Rule Category', 'VR_b', 'VR_e', 'PR', 'VR_b', 'VR_e', 'PR', 'VR_b', 'VR_e', 'PR']
    ),
    'casas_stats': TableConfig(
        table_id='tab:casas_stats',
        caption='Behavioral comparison between VESPER and CASAS (House~2).',
        label='tab:casas_stats',
        columns=['metric', 'baseline', 'with_enforcement', 'human_target'],
        column_headers=['Metric', 'Baseline', 'With Enforcement', 'Human Target']
    )
}


class TableExporter:
    """Export VESPER metrics to various formats."""
    
    def __init__(self, output_dir: str = None):
        """
        Initialize exporter.
        
        Args:
            output_dir: Directory for output files. Defaults to 'analysis/results'
        """
        if output_dir is None:
            self.output_dir = Path(__file__).parent / 'results'
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_task_success_table(self, 
                                  df: pd.DataFrame,
                                  houses: List[str] = ['H1', 'H2', 'H3']) -> Dict[str, Any]:
        """
        Generate Table 1: Baseline task performance.
        
        Args:
            df: Trial DataFrame (baseline mode only)
            houses: Houses to include
            
        Returns:
            Dict with table data and LaTeX string
        """
        results = {
            'houses': {},
            'overall': {}
        }
        
        task_names = {
            't1': 'Make phone call (t1)',
            't2': 'Wash hands (t2)',
            't3': 'Cook oatmeal (t3)',
            't4': 'Eat meal (t4)',
            't5': 'Clean dishes (t5)'
        }
        
        house_names = {
            'H1': 'House~1 (Simple)',
            'H2': 'House~2 (Moderate)',
            'H3': 'House~3 (Complex)'
        }
        
        for house in houses:
            house_df = df[df['house_id'] == house]
            if house_df.empty:
                continue
                
            house_results = []
            
            for task_id in ['t1', 't2', 't3', 't4', 't5']:
                task_df = house_df[house_df['task_id'] == task_id]
                
                if task_df.empty:
                    continue
                
                success_rate = task_df['success'].mean()
                successful = task_df[task_df['success'] == True]
                
                if not successful.empty:
                    avg_steps = successful['steps'].mean()
                    std_steps = successful['steps'].std()
                    avg_duration = successful['duration_sec'].mean()
                    std_duration = successful['duration_sec'].std()
                    avg_llm = successful['llm_calls'].mean()
                else:
                    avg_steps = std_steps = avg_duration = std_duration = avg_llm = 0
                
                house_results.append({
                    'task': task_names.get(task_id, task_id),
                    'task_id': task_id,
                    'success': success_rate,
                    'avg_steps': avg_steps,
                    'std_steps': std_steps if not np.isnan(std_steps) else 0,
                    'avg_duration': avg_duration,
                    'std_duration': std_duration if not np.isnan(std_duration) else 0,
                    'avg_llm_calls': avg_llm
                })
            
            results['houses'][house] = house_results
        
        # Compute overall statistics
        for house in houses:
            house_df = df[df['house_id'] == house]
            if not house_df.empty:
                results['overall'][house] = {
                    'tcr': house_df['success'].mean(),
                    'avg_steps': house_df[house_df['success']]['steps'].mean() if house_df['success'].any() else 0,
                    'avg_duration': house_df[house_df['success']]['duration_sec'].mean() if house_df['success'].any() else 0,
                    'avg_llm_calls': house_df[house_df['success']]['llm_calls'].mean() if house_df['success'].any() else 0
                }
        
        # Generate LaTeX
        latex = self._generate_task_success_latex(results, house_names)
        results['latex'] = latex
        
        # Save CSV
        self._save_task_success_csv(results)
        
        return results
    
    def _generate_task_success_latex(self, results: Dict, house_names: Dict) -> str:
        """Generate LaTeX for task success table."""
        lines = [
            r"\begin{table*}[!t]",
            r"\caption{Baseline task performance (no safety enforcement).}",
            r"\label{tab:task_success_all}",
            r"\centering",
            r"\begin{tabular}{lcccc}",
            r"\toprule",
            r"\textbf{Task} & \textbf{Success} & \textbf{Avg Steps} & \textbf{Avg Duration (s)} & \textbf{Avg LLM Calls} \\",
            r"\midrule"
        ]
        
        for house, house_label in house_names.items():
            if house not in results['houses']:
                continue
                
            lines.append(f"\\multicolumn{{5}}{{c}}{{{house_label}}} \\\\")
            
            for row in results['houses'][house]:
                success_pct = f"{row['success']*100:.1f}\\%"
                steps = f"{row['avg_steps']:.1f} $\\pm$ {row['std_steps']:.1f}"
                duration = f"{row['avg_duration']:.1f} $\\pm$ {row['std_duration']:.1f}"
                llm = f"{row['avg_llm_calls']:.1f}"
                
                lines.append(f"{row['task']} & {success_pct} & {steps} & {duration} & {llm} \\\\")
            
            lines.append(r"\midrule")
        
        # Overall row
        overall = results.get('overall', {})
        if overall:
            h1_tcr = overall.get('H1', {}).get('tcr', 0) * 100
            h3_tcr = overall.get('H3', {}).get('tcr', 0) * 100
            lines.append(f"\\textbf{{Overall}} & \\textbf{{{h3_tcr:.1f}\\% (H3) -- {h1_tcr:.1f}\\% (H1)}} & & & \\\\")
        
        lines.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}"
        ])
        
        return "\n".join(lines)
    
    def _save_task_success_csv(self, results: Dict):
        """Save task success data to CSV."""
        rows = []
        for house, tasks in results.get('houses', {}).items():
            for task in tasks:
                rows.append({
                    'house_id': house,
                    'task_id': task['task_id'],
                    'task_name': task['task'],
                    'success_rate': task['success'],
                    'avg_steps': task['avg_steps'],
                    'std_steps': task['std_steps'],
                    'avg_duration': task['avg_duration'],
                    'std_duration': task['std_duration'],
                    'avg_llm_calls': task['avg_llm_calls']
                })
        
        df = pd.DataFrame(rows)
        csv_path = self.output_dir / 'task_success.csv'
        df.to_csv(csv_path, index=False)
        print(f"📁 Saved: {csv_path}")
    
    def export_safety_violations_table(self,
                                       baseline_df: pd.DataFrame,
                                       enforced_df: pd.DataFrame,
                                       houses: List[str] = ['H1', 'H2', 'H3']) -> Dict[str, Any]:
        """
        Generate Table 2: Safety violations by category and house.
        
        Args:
            baseline_df: Baseline trials
            enforced_df: Enforced trials
            houses: Houses to include
            
        Returns:
            Dict with table data and LaTeX string
        """
        from .metrics_safety import SafetyMetrics, SAFETY_RULES
        
        categories = list(SAFETY_RULES.keys())
        category_names = {
            'appliance_safety': 'Appliance Safety',
            'entry_security': 'Entry \\& Access Security',
            'sensor_integrity': 'Sensor Integrity',
            'spatial_temporal': 'Spatial--Temporal Safety'
        }
        
        results = {'categories': {}}
        
        for category in categories:
            cat_results = {}
            
            for house in houses:
                b_house = baseline_df[baseline_df['house_id'] == house]
                e_house = enforced_df[enforced_df['house_id'] == house]
                
                # Compute VR for baseline
                vr_b = self._compute_category_vr(b_house, category)
                
                # Compute VR for enforced
                vr_e = self._compute_category_vr(e_house, category)
                
                # Compute PR
                pr = 1 - (vr_e / vr_b) if vr_b > 0 else (1.0 if vr_e == 0 else 0.0)
                
                cat_results[house] = {
                    'vr_baseline': vr_b,
                    'vr_enforced': vr_e,
                    'prevention_rate': pr
                }
            
            results['categories'][category] = cat_results
        
        # Generate LaTeX
        latex = self._generate_safety_violations_latex(results, houses, category_names)
        results['latex'] = latex
        
        # Save CSV
        self._save_safety_violations_csv(results, houses)
        
        return results
    
    def _compute_category_vr(self, df: pd.DataFrame, category: str) -> float:
        """Compute violation rate for a specific category."""
        if df.empty:
            return 0.0
        
        trials_with_violation = 0
        for _, row in df.iterrows():
            violations = row.get('violations', [])
            if isinstance(violations, list):
                if any(v.get('category') == category for v in violations):
                    trials_with_violation += 1
        
        return trials_with_violation / len(df)
    
    def _generate_safety_violations_latex(self, results: Dict, houses: List[str], 
                                          category_names: Dict) -> str:
        """Generate LaTeX for safety violations table."""
        lines = [
            r"\begin{table*}[!t]",
            r"\caption{Safety violations by rule category and house.}",
            r"\label{tab:safety_violations}",
            r"\centering",
            r"\begin{tabular}{lccc|ccc|ccc}",
            r"\toprule",
            r" & \multicolumn{3}{c}{\textbf{House 1 (Simple)}} &",
            r"   \multicolumn{3}{c}{\textbf{House 2 (Moderate)}} &",
            r"   \multicolumn{3}{c}{\textbf{House 3 (Complex)}} \\",
            r"\cmidrule(lr){2-4} \cmidrule(lr){5-7} \cmidrule(lr){8-10}",
            r"\textbf{Rule Category} &",
            r"\textbf{VR$_b$} & \textbf{VR$_e$} & \textbf{PR} &",
            r"\textbf{VR$_b$} & \textbf{VR$_e$} & \textbf{PR} &",
            r"\textbf{VR$_b$} & \textbf{VR$_e$} & \textbf{PR} \\",
            r"\midrule"
        ]
        
        for category, cat_name in category_names.items():
            if category not in results['categories']:
                continue
            
            cat_data = results['categories'][category]
            row_parts = [cat_name]
            
            for house in houses:
                if house in cat_data:
                    h = cat_data[house]
                    vr_b = f"{h['vr_baseline']*100:.0f}\\%"
                    vr_e = f"{h['vr_enforced']*100:.0f}\\%"
                    pr = f"{h['prevention_rate']*100:.0f}\\%"
                    row_parts.extend([vr_b, vr_e, pr])
                else:
                    row_parts.extend(['--', '--', '--'])
            
            lines.append(" & ".join(row_parts) + r" \\")
        
        lines.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}"
        ])
        
        return "\n".join(lines)
    
    def _save_safety_violations_csv(self, results: Dict, houses: List[str]):
        """Save safety violations data to CSV."""
        rows = []
        for category, cat_data in results.get('categories', {}).items():
            for house in houses:
                if house in cat_data:
                    h = cat_data[house]
                    rows.append({
                        'category': category,
                        'house_id': house,
                        'vr_baseline': h['vr_baseline'],
                        'vr_enforced': h['vr_enforced'],
                        'prevention_rate': h['prevention_rate']
                    })
        
        df = pd.DataFrame(rows)
        csv_path = self.output_dir / 'safety_violations.csv'
        df.to_csv(csv_path, index=False)
        print(f"📁 Saved: {csv_path}")
    
    def export_casas_comparison_table(self,
                                      baseline_stats: Dict,
                                      enforced_stats: Dict = None) -> Dict[str, Any]:
        """
        Generate Table 4: Behavioral comparison with CASAS.
        
        Args:
            baseline_stats: Behavioral metrics for baseline
            enforced_stats: Behavioral metrics with enforcement
            
        Returns:
            Dict with table data and LaTeX string
        """
        # Human target values (from paper)
        human_targets = {
            'Overall Similarity (COS)': 0.70,
            'Temporal Similarity': 0.60,
            'Sensor Sequence Similarity': 0.60,
            'Transition Similarity': 0.70,
            'Event Count Ratio': 0.80,
            'Duration Ratio': 0.50,
            'Task Completion Rate (TCR)': 0.80,
            'Semantic Understanding (SUS)': 0.85,
            'Room Label Stability (RLS)': 0.95,
            'Effective Movement Ratio (EMR)': 0.90
        }
        
        # Metric mapping
        metric_mapping = {
            'Overall Similarity (COS)': 'cos',
            'Temporal Similarity': 'temporal_similarity',
            'Sensor Sequence Similarity': 'sensor_sequence_similarity',
            'Transition Similarity': 'transition_similarity',
            'Event Count Ratio': 'event_count_ratio',
            'Duration Ratio': 'duration_ratio',
            'Task Completion Rate (TCR)': 'tcr',
            'Semantic Understanding (SUS)': 'sus',
            'Room Label Stability (RLS)': 'rls',
            'Effective Movement Ratio (EMR)': 'emr'
        }
        
        rows = []
        for display_name, key in metric_mapping.items():
            baseline_val = baseline_stats.get(key, 0)
            enforced_val = enforced_stats.get(key, baseline_val) if enforced_stats else baseline_val
            human_val = human_targets.get(display_name, 0)
            
            rows.append({
                'metric': display_name,
                'baseline': baseline_val,
                'enforced': enforced_val,
                'human_target': human_val
            })
        
        results = {'rows': rows}
        
        # Generate LaTeX
        latex = self._generate_casas_comparison_latex(rows)
        results['latex'] = latex
        
        # Save CSV
        df = pd.DataFrame(rows)
        csv_path = self.output_dir / 'casas_comparison.csv'
        df.to_csv(csv_path, index=False)
        print(f"📁 Saved: {csv_path}")
        
        return results
    
    def _generate_casas_comparison_latex(self, rows: List[Dict]) -> str:
        """Generate LaTeX for CASAS comparison table."""
        lines = [
            r"\begin{table*}[!t]",
            r"\caption{Behavioral comparison between VESPER and CASAS.}",
            r"\label{tab:casas_stats}",
            r"\centering",
            r"\begin{tabular}{lccc}",
            r"\toprule",
            r"\textbf{Metric} & \textbf{Baseline} & \textbf{With Enforcement} & \textbf{Human Target} \\",
            r"\midrule"
        ]
        
        for row in rows:
            metric = row['metric']
            baseline = f"{row['baseline']*100:.1f}\\%"
            enforced = f"{row['enforced']*100:.1f}\\%"
            human = f"{row['human_target']*100:.0f}\\%"
            
            lines.append(f"{metric} & {baseline} & {enforced} & {human} \\\\")
        
        lines.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table*}"
        ])
        
        return "\n".join(lines)
    
    def export_all_tables(self, df: pd.DataFrame, 
                         baseline_stats: Dict,
                         enforced_stats: Dict = None) -> Dict[str, Any]:
        """
        Export all tables for the paper.
        
        Args:
            df: Full trial DataFrame
            baseline_stats: Behavioral metrics for baseline
            enforced_stats: Behavioral metrics with enforcement
            
        Returns:
            Dict with all table results
        """
        baseline_df = df[df['mode'] == 'baseline']
        enforced_df = df[df['mode'] == 'enforced']
        
        results = {}
        
        # Table 1: Task success
        print("\n📊 Generating Table 1: Task Success...")
        results['task_success'] = self.export_task_success_table(baseline_df)
        
        # Table 2: Safety violations
        print("📊 Generating Table 2: Safety Violations...")
        results['safety_violations'] = self.export_safety_violations_table(baseline_df, enforced_df)
        
        # Table 4: CASAS comparison
        print("📊 Generating Table 4: CASAS Comparison...")
        results['casas_comparison'] = self.export_casas_comparison_table(baseline_stats, enforced_stats)
        
        # Save combined LaTeX file
        self._save_combined_latex(results)
        
        # Save JSON summary
        self._save_json_summary(results)
        
        return results
    
    def _save_combined_latex(self, results: Dict):
        """Save all LaTeX tables to a single file."""
        latex_content = [
            "% VESPER V2 Evaluation Tables",
            f"% Generated: {datetime.now().isoformat()}",
            "",
        ]
        
        for table_name, table_data in results.items():
            if 'latex' in table_data:
                latex_content.append(f"% --- {table_name} ---")
                latex_content.append(table_data['latex'])
                latex_content.append("")
        
        latex_path = self.output_dir / 'all_tables.tex'
        with open(latex_path, 'w') as f:
            f.write("\n".join(latex_content))
        print(f"📁 Saved: {latex_path}")
    
    def _save_json_summary(self, results: Dict):
        """Save JSON summary of all results."""
        # Remove LaTeX strings for JSON (not serializable well)
        json_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                json_results[key] = {k: v for k, v in value.items() if k != 'latex'}
        
        json_path = self.output_dir / 'evaluation_summary.json'
        with open(json_path, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        print(f"📁 Saved: {json_path}")


if __name__ == '__main__':
    # Test the exporter
    print("🔍 Testing VESPER Table Exporter")
    print("=" * 50)
    
    # Create sample data
    sample_df = pd.DataFrame([
        {'house_id': 'H1', 'task_id': 't1', 'mode': 'baseline', 'success': True, 
         'steps': 18, 'duration_sec': 325, 'llm_calls': 5, 'violations': []},
        {'house_id': 'H1', 'task_id': 't2', 'mode': 'baseline', 'success': True,
         'steps': 25, 'duration_sec': 348, 'llm_calls': 7, 'violations': []},
        {'house_id': 'H1', 'task_id': 't1', 'mode': 'enforced', 'success': True,
         'steps': 20, 'duration_sec': 340, 'llm_calls': 6, 'violations': []},
    ])
    
    baseline_stats = {
        'tcr': 0.396,
        'sus': 0.98,
        'rls': 0.96,
        'emr': 0.958,
        'cos': 0.138,
        'temporal_similarity': 0.006,
        'sensor_sequence_similarity': 0.139,
        'transition_similarity': 0.222,
        'event_count_ratio': 0.167,
        'duration_ratio': 0.002
    }
    
    exporter = TableExporter()
    results = exporter.export_all_tables(sample_df, baseline_stats)
    
    print("\n📄 Generated LaTeX for task success table:")
    print(results['task_success']['latex'][:500] + "...")
