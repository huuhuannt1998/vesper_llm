"""
VESPER V2 Analysis Pipeline
============================

Analysis modules for safety-focused evaluation of LLM-driven embodied agents.

Modules:
    - loader: Load and normalize trial logs
    - metrics_safety: VR, VCT, PR, FPR, RSR
    - metrics_behavior: TCR, SUS, RLS, EMR, COS
    - stats_tests: Chi-square, t-test, ANOVA, effect sizes
    - export_tables: CSV export + LaTeX row generators
"""

from .loader import TrialDataLoader, normalize_trial_logs
from .metrics_safety import SafetyMetrics, compute_violation_stats
from .metrics_behavior import BehaviorMetrics, compute_behavioral_stats
from .stats_tests import StatisticalTests
from .export_tables import TableExporter

__all__ = [
    'TrialDataLoader',
    'normalize_trial_logs',
    'SafetyMetrics',
    'compute_violation_stats',
    'BehaviorMetrics',
    'compute_behavioral_stats',
    'StatisticalTests',
    'TableExporter'
]
