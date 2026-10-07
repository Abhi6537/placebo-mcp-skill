"""
Effect size, standard error, and confidence interval computations.
Uses scipy.stats for deterministic calculations.
"""

from typing import List, Tuple
import numpy as np
import scipy.stats as stats
from placebo.models.statistical import StatisticalResult


def compute_two_sample_effect(
    treatment_values: List[float],
    control_values: List[float],
    alpha: float = 0.05
) -> StatisticalResult:
    """
    Compute difference in means, Welch's t-test p-value, standard error,
    and 95% confidence interval for two independent samples.
    """
    t_arr = np.asarray(treatment_values, dtype=float)
    c_arr = np.asarray(control_values, dtype=float)

    # Filter out NaNs / Infs
    t_clean = t_arr[np.isfinite(t_arr)]
    c_clean = c_arr[np.isfinite(c_arr)]

    n_t = len(t_clean)
    n_c = len(c_clean)

    if n_t < 2 or n_c < 2:
        return StatisticalResult(
            effect_size=0.0,
            percentage_change=0.0,
            standard_error=0.0,
            raw_p_value=1.0,
            adjustment_method="none",
            adjusted_p_value=1.0,
            confidence_interval=[0.0, 0.0],
            sample_size=n_t + n_c,
            treatment_sample_size=n_t,
            control_sample_size=n_c,
            test_used="welch_t_test",
            assumptions_met=False,
            assumption_notes="Insufficient sample size: each group must have >= 2 observations."
        )

    mean_t = float(np.mean(t_clean))
    mean_c = float(np.mean(c_clean))
    var_t = float(np.var(t_clean, ddof=1))
    var_c = float(np.var(c_clean, ddof=1))

    effect_size = mean_t - mean_c

    # Relative percentage change
    pct_change = None
    if abs(mean_c) > 1e-9:
        pct_change = (effect_size / abs(mean_c)) * 100.0

    # Welch's standard error: sqrt(s_1^2/n_1 + s_2^2/n_2)
    se = float(np.sqrt((var_t / n_t) + (var_c / n_c)))

    # Welch-Satterthwaite degrees of freedom
    if se > 1e-12:
        df_num = ((var_t / n_t) + (var_c / n_c)) ** 2
        df_den = (((var_t / n_t) ** 2) / (n_t - 1)) + (((var_c / n_c) ** 2) / (n_c - 1))
        df = float(df_num / df_den) if df_den > 0 else float(n_t + n_c - 2)
    else:
        df = float(n_t + n_c - 2)

    # Welch's t-test
    if se > 1e-12:
        t_stat = effect_size / se
        raw_p = float(2.0 * stats.t.sf(np.abs(t_stat), df=df))
        # 1 - alpha Confidence Interval
        t_crit = float(stats.t.ppf(1.0 - (alpha / 2.0), df=df))
        ci_lower = float(effect_size - (t_crit * se))
        ci_upper = float(effect_size + (t_crit * se))
    else:
        raw_p = 1.0 if abs(effect_size) < 1e-12 else 0.0
        ci_lower = effect_size
        ci_upper = effect_size

    return StatisticalResult(
        effect_size=round(effect_size, 6),
        percentage_change=round(pct_change, 2) if pct_change is not None else None,
        standard_error=round(se, 6),
        raw_p_value=round(np.clip(raw_p, 0.0, 1.0), 6),
        adjustment_method="none",
        adjusted_p_value=round(np.clip(raw_p, 0.0, 1.0), 6),
        confidence_interval=[round(ci_lower, 6), round(ci_upper, 6)],
        sample_size=n_t + n_c,
        treatment_sample_size=n_t,
        control_sample_size=n_c,
        test_used="welch_t_test",
        degrees_of_freedom=round(df, 2),
        assumptions_met=True
    )
