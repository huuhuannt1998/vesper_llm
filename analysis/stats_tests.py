"""
VESPER V2 Statistical Tests
===========================

Statistical testing utilities for comparing:
- Baseline vs Enforced conditions
- Across house layouts (H1, H2, H3)
- Across task types (t1-t5)

Tests included:
- Chi-square tests for categorical outcomes (success/failure, violation/no-violation)
- Independent t-tests for continuous metrics (VCT, path length, duration)
- One-way ANOVA for multi-group comparisons across houses
- Effect sizes: Cohen's d, Cramér's V
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from scipy import stats
import warnings


@dataclass
class StatTestResult:
    """Container for statistical test results."""
    test_name: str
    statistic: float
    p_value: float
    effect_size: float
    effect_size_name: str
    significant: bool  # at α = 0.05
    interpretation: str
    group1_label: str = ""
    group2_label: str = ""
    n1: int = 0
    n2: int = 0


class StatisticalTests:
    """Perform statistical tests on VESPER trial data."""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize statistical testing.
        
        Args:
            alpha: Significance level (default 0.05)
        """
        self.alpha = alpha
    
    def chi_square_test(self, 
                        group1: pd.Series, 
                        group2: pd.Series,
                        group1_label: str = "Group 1",
                        group2_label: str = "Group 2") -> StatTestResult:
        """
        Perform chi-square test for categorical outcomes.
        
        Use for comparing success rates or violation rates between groups.
        
        Args:
            group1: Boolean series (e.g., success for baseline)
            group2: Boolean series (e.g., success for enforced)
            group1_label: Label for first group
            group2_label: Label for second group
            
        Returns:
            StatTestResult with chi-square statistic, p-value, and Cramér's V
        """
        # Create contingency table
        # Success/Failure counts for each group
        g1_success = group1.sum()
        g1_fail = len(group1) - g1_success
        g2_success = group2.sum()
        g2_fail = len(group2) - g2_success
        
        contingency = np.array([
            [g1_success, g1_fail],
            [g2_success, g2_fail]
        ])
        
        # Perform chi-square test
        try:
            chi2, p, dof, expected = stats.chi2_contingency(contingency)
        except Exception as e:
            return StatTestResult(
                test_name="Chi-square test",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                effect_size_name="Cramér's V",
                significant=False,
                interpretation=f"Test failed: {e}",
                group1_label=group1_label,
                group2_label=group2_label,
                n1=len(group1),
                n2=len(group2)
            )
        
        # Compute Cramér's V (effect size for chi-square)
        n = contingency.sum()
        min_dim = min(contingency.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if n > 0 and min_dim > 0 else 0.0
        
        # Interpret effect size
        if cramers_v < 0.1:
            interpretation = "Negligible association"
        elif cramers_v < 0.3:
            interpretation = "Small association"
        elif cramers_v < 0.5:
            interpretation = "Medium association"
        else:
            interpretation = "Large association"
        
        return StatTestResult(
            test_name="Chi-square test",
            statistic=chi2,
            p_value=p,
            effect_size=cramers_v,
            effect_size_name="Cramér's V",
            significant=p < self.alpha,
            interpretation=interpretation,
            group1_label=group1_label,
            group2_label=group2_label,
            n1=len(group1),
            n2=len(group2)
        )
    
    def independent_t_test(self,
                          group1: pd.Series,
                          group2: pd.Series,
                          group1_label: str = "Group 1",
                          group2_label: str = "Group 2") -> StatTestResult:
        """
        Perform independent samples t-test for continuous variables.
        
        Use for comparing means (e.g., VCT, duration, steps) between groups.
        
        Args:
            group1: Continuous values for first group
            group2: Continuous values for second group
            group1_label: Label for first group
            group2_label: Label for second group
            
        Returns:
            StatTestResult with t-statistic, p-value, and Cohen's d
        """
        # Remove NaN values
        g1 = group1.dropna()
        g2 = group2.dropna()
        
        if len(g1) < 2 or len(g2) < 2:
            return StatTestResult(
                test_name="Independent t-test",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                effect_size_name="Cohen's d",
                significant=False,
                interpretation="Insufficient data",
                group1_label=group1_label,
                group2_label=group2_label,
                n1=len(g1),
                n2=len(g2)
            )
        
        # Perform t-test
        t_stat, p = stats.ttest_ind(g1, g2, equal_var=False)  # Welch's t-test
        
        # Compute Cohen's d (effect size)
        pooled_std = np.sqrt((g1.std()**2 + g2.std()**2) / 2)
        cohens_d = (g1.mean() - g2.mean()) / pooled_std if pooled_std > 0 else 0.0
        
        # Interpret effect size
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            interpretation = "Negligible effect"
        elif abs_d < 0.5:
            interpretation = "Small effect"
        elif abs_d < 0.8:
            interpretation = "Medium effect"
        else:
            interpretation = "Large effect"
        
        return StatTestResult(
            test_name="Independent t-test (Welch's)",
            statistic=t_stat,
            p_value=p,
            effect_size=cohens_d,
            effect_size_name="Cohen's d",
            significant=p < self.alpha,
            interpretation=interpretation,
            group1_label=group1_label,
            group2_label=group2_label,
            n1=len(g1),
            n2=len(g2)
        )
    
    def one_way_anova(self,
                      groups: List[pd.Series],
                      group_labels: List[str] = None) -> StatTestResult:
        """
        Perform one-way ANOVA for multi-group comparisons.
        
        Use for comparing means across house layouts (H1, H2, H3).
        
        Args:
            groups: List of Series, one per group
            group_labels: Labels for each group
            
        Returns:
            StatTestResult with F-statistic, p-value, and eta-squared
        """
        if group_labels is None:
            group_labels = [f"Group {i+1}" for i in range(len(groups))]
        
        # Remove NaN values from each group
        clean_groups = [g.dropna() for g in groups]
        
        # Check for sufficient data
        if any(len(g) < 2 for g in clean_groups):
            return StatTestResult(
                test_name="One-way ANOVA",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                effect_size_name="η² (eta-squared)",
                significant=False,
                interpretation="Insufficient data in one or more groups",
                group1_label=", ".join(group_labels)
            )
        
        # Perform ANOVA
        f_stat, p = stats.f_oneway(*clean_groups)
        
        # Compute eta-squared (effect size)
        # η² = SS_between / SS_total
        grand_mean = np.concatenate([g.values for g in clean_groups]).mean()
        
        ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in clean_groups)
        ss_total = sum(((g - grand_mean)**2).sum() for g in clean_groups)
        
        eta_sq = ss_between / ss_total if ss_total > 0 else 0.0
        
        # Interpret effect size
        if eta_sq < 0.01:
            interpretation = "Negligible effect"
        elif eta_sq < 0.06:
            interpretation = "Small effect"
        elif eta_sq < 0.14:
            interpretation = "Medium effect"
        else:
            interpretation = "Large effect"
        
        total_n = sum(len(g) for g in clean_groups)
        
        return StatTestResult(
            test_name="One-way ANOVA",
            statistic=f_stat,
            p_value=p,
            effect_size=eta_sq,
            effect_size_name="η² (eta-squared)",
            significant=p < self.alpha,
            interpretation=interpretation,
            group1_label=", ".join(group_labels),
            n1=total_n
        )
    
    def compare_baseline_vs_enforced(self, 
                                     df: pd.DataFrame,
                                     metric: str) -> Dict[str, StatTestResult]:
        """
        Compare baseline vs enforced for a specific metric.
        
        Args:
            df: Trial DataFrame
            metric: Column name to compare (e.g., 'success', 'steps', 'duration_sec')
            
        Returns:
            Dict with test results
        """
        baseline = df[df['mode'] == 'baseline'][metric]
        enforced = df[df['mode'] == 'enforced'][metric]
        
        results = {}
        
        if metric == 'success' or df[metric].dtype == bool:
            # Use chi-square for categorical
            results['chi_square'] = self.chi_square_test(
                baseline.astype(bool),
                enforced.astype(bool),
                "Baseline", "Enforced"
            )
        else:
            # Use t-test for continuous
            results['t_test'] = self.independent_t_test(
                baseline, enforced,
                "Baseline", "Enforced"
            )
        
        return results
    
    def compare_across_houses(self, 
                             df: pd.DataFrame,
                             metric: str) -> StatTestResult:
        """
        Compare a metric across house layouts using ANOVA.
        
        Args:
            df: Trial DataFrame
            metric: Column name to compare
            
        Returns:
            ANOVA test result
        """
        houses = ['H1', 'H2', 'H3']
        groups = []
        labels = []
        
        for house in houses:
            house_df = df[df['house_id'] == house]
            if not house_df.empty and metric in house_df.columns:
                groups.append(house_df[metric])
                labels.append(house)
        
        if len(groups) < 2:
            return StatTestResult(
                test_name="One-way ANOVA",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                effect_size_name="η²",
                significant=False,
                interpretation="Insufficient groups for comparison"
            )
        
        return self.one_way_anova(groups, labels)
    
    def run_all_comparisons(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Run all statistical comparisons for the evaluation.
        
        Args:
            df: Trial DataFrame
            
        Returns:
            Dict with all test results organized by comparison type
        """
        results = {
            'baseline_vs_enforced': {},
            'across_houses': {},
            'summary': {}
        }
        
        # Baseline vs Enforced comparisons
        for metric in ['success', 'steps', 'duration_sec', 'llm_calls']:
            if metric in df.columns:
                results['baseline_vs_enforced'][metric] = self.compare_baseline_vs_enforced(df, metric)
        
        # Across houses comparisons (for baseline only)
        baseline_df = df[df['mode'] == 'baseline']
        for metric in ['success', 'steps', 'duration_sec']:
            if metric in baseline_df.columns:
                results['across_houses'][metric] = self.compare_across_houses(baseline_df, metric)
        
        # Environment complexity and success association
        if 'house_id' in df.columns and 'success' in df.columns:
            # Create complexity grouping
            baseline_df = df[df['mode'] == 'baseline']
            if not baseline_df.empty:
                h1_success = baseline_df[baseline_df['house_id'] == 'H1']['success']
                h3_success = baseline_df[baseline_df['house_id'] == 'H3']['success']
                
                if len(h1_success) > 0 and len(h3_success) > 0:
                    results['summary']['complexity_vs_success'] = self.chi_square_test(
                        h1_success.astype(bool),
                        h3_success.astype(bool),
                        "H1 (Simple)",
                        "H3 (Complex)"
                    )
        
        return results


def compute_effect_sizes(group1: pd.Series, group2: pd.Series) -> Dict[str, float]:
    """
    Compute multiple effect size measures.
    
    Args:
        group1: First group data
        group2: Second group data
        
    Returns:
        Dict with effect size measures
    """
    g1 = group1.dropna()
    g2 = group2.dropna()
    
    results = {}
    
    # Cohen's d
    pooled_std = np.sqrt((g1.std()**2 + g2.std()**2) / 2)
    if pooled_std > 0:
        results['cohens_d'] = (g1.mean() - g2.mean()) / pooled_std
    else:
        results['cohens_d'] = 0.0
    
    # Glass's delta (using first group's SD)
    if g1.std() > 0:
        results['glass_delta'] = (g1.mean() - g2.mean()) / g1.std()
    else:
        results['glass_delta'] = 0.0
    
    # Hedges' g (bias-corrected Cohen's d)
    n1, n2 = len(g1), len(g2)
    if n1 + n2 > 4:
        correction = 1 - (3 / (4 * (n1 + n2) - 9))
        results['hedges_g'] = results['cohens_d'] * correction
    else:
        results['hedges_g'] = results['cohens_d']
    
    # Common language effect size (probability of superiority)
    if len(g1) > 0 and len(g2) > 0:
        # Approximate using normal distribution
        d = results['cohens_d']
        results['cles'] = stats.norm.cdf(d / np.sqrt(2))
    else:
        results['cles'] = 0.5
    
    return results


def format_stat_result_latex(result: StatTestResult) -> str:
    """
    Format a statistical test result for LaTeX.
    
    Args:
        result: StatTestResult object
        
    Returns:
        LaTeX-formatted string
    """
    sig_marker = "*" if result.significant else ""
    
    if "Chi-square" in result.test_name:
        return f"$\\chi^2={result.statistic:.1f}$, $p{sig_marker}={result.p_value:.3f}$, $V={result.effect_size:.2f}$"
    elif "t-test" in result.test_name:
        return f"$t={result.statistic:.2f}$, $p{sig_marker}={result.p_value:.3f}$, $d={result.effect_size:.2f}$"
    elif "ANOVA" in result.test_name:
        return f"$F={result.statistic:.2f}$, $p{sig_marker}={result.p_value:.3f}$, $\\eta^2={result.effect_size:.3f}$"
    else:
        return f"stat={result.statistic:.2f}, p={result.p_value:.3f}"


if __name__ == '__main__':
    # Test statistical functions
    print("🔍 Testing VESPER Statistical Tests")
    print("=" * 50)
    
    # Create sample data
    np.random.seed(42)
    
    # Sample trial data
    n = 100
    sample_df = pd.DataFrame({
        'house_id': np.random.choice(['H1', 'H2', 'H3'], n),
        'mode': np.random.choice(['baseline', 'enforced'], n),
        'success': np.random.choice([True, False], n, p=[0.7, 0.3]),
        'steps': np.random.normal(30, 10, n),
        'duration_sec': np.random.normal(400, 100, n),
    })
    
    # Run tests
    st = StatisticalTests()
    results = st.run_all_comparisons(sample_df)
    
    print("\n📊 Baseline vs Enforced:")
    for metric, tests in results['baseline_vs_enforced'].items():
        for test_name, result in tests.items():
            print(f"  {metric}: {result.test_name}")
            print(f"    Statistic: {result.statistic:.3f}")
            print(f"    p-value: {result.p_value:.3f} {'*' if result.significant else ''}")
            print(f"    Effect size ({result.effect_size_name}): {result.effect_size:.3f}")
            print(f"    Interpretation: {result.interpretation}")
    
    print("\n📊 Across Houses:")
    for metric, result in results['across_houses'].items():
        print(f"  {metric}: {result.test_name}")
        print(f"    F-statistic: {result.statistic:.3f}")
        print(f"    p-value: {result.p_value:.3f} {'*' if result.significant else ''}")
        print(f"    η²: {result.effect_size:.3f}")
