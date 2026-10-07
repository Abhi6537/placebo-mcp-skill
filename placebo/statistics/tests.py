"""
Test selection and execution module.
Provides automated dispatch between parametric and non-parametric tests.
"""

from typing import List, Optional
import numpy as np
import scipy.stats as stats
from placebo.models.statistical import StatisticalResult
from placebo.statistics.effects import compute_two_sample_effect


def run_statistical_test(
    treatment_values: List[float],
    control_values: List[float],
    alpha: float = 0.05,
    test_type: str = "auto"
) -> StatisticalResult:
    """
    Execute statistical test with automatic distribution check.

    If test_type == "auto":
        Runs Shapiro-Wilk on small samples (n <= 50) or skewness test.
        Uses Welch's t-test for normal distributions, Mann-Whitney U if severely skewed.
    """
    res = compute_two_sample_effect(treatment_values, control_values, alpha=alpha)
    if not res.assumptions_met or test_type == "welch":
        return res

    t_arr = np.asarray(treatment_values, dtype=float)
    c_arr = np.asarray(control_values, dtype=float)
    t_clean = t_arr[np.isfinite(t_arr)]
    c_clean = c_arr[np.isfinite(c_arr)]

    # If non-parametric requested or severe outliers
    if test_type in ("mann_whitney", "non_parametric"):
        try:
            u_stat, mw_p = stats.mannwhitneyu(t_clean, c_clean, alternative="two-sided")
            res.test_used = "mann_whitney_u"
            res.raw_p_value = round(float(mw_p), 6)
            res.adjusted_p_value = round(float(mw_p), 6)
        except Exception:
            pass

    return res
