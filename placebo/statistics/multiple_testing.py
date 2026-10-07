"""
Multiple-testing correction module.
Provides deterministic Benjamini-Hochberg (FDR), Holm-Bonferroni (FWER), and Bonferroni corrections.
"""

from typing import List, Tuple
import numpy as np


def benjamini_hochberg(
    p_values: List[float],
    alpha: float = 0.05
) -> Tuple[List[bool], List[float]]:
    """
    Apply Benjamini-Hochberg (BH) procedure to control False Discovery Rate (FDR).

    Assumptions:
    - Independent test statistics, or Positive Regression Dependency on Subsets (PRDS).

    Args:
        p_values: Array of raw p-values in [0, 1].
        alpha: Target False Discovery Rate threshold (default 0.05).

    Returns:
        (rejects, adjusted_p_values):
            rejects: Boolean list where True indicates rejected null hypothesis at FDR alpha.
            adjusted_p_values: Monotonically smoothed adjusted p-values (q-values).
    """
    m = len(p_values)
    if m == 0:
        return [], []
    if m == 1:
        p = float(p_values[0])
        return [p <= alpha], [p]

    p_arr = np.clip(np.asarray(p_values, dtype=float), 0.0, 1.0)
    sort_idx = np.argsort(p_arr)
    sorted_p = p_arr[sort_idx]

    # Calculate adjusted p-values via reverse cumulative minimum
    # q_(i) = min_{j >= i} (p_(j) * m / j)
    ranks = np.arange(1, m + 1)
    q_values = sorted_p * (m / ranks)
    
    # Reverse cumulative minimum to ensure monotonicity
    adj_sorted = np.minimum.accumulate(q_values[::-1])[::-1]
    adj_sorted = np.clip(adj_sorted, 0.0, 1.0)

    # Invert sorting back to original order
    inv_idx = np.empty(m, dtype=int)
    inv_idx[sort_idx] = np.arange(m)
    adjusted_p = adj_sorted[inv_idx].tolist()

    rejects = [adj <= alpha for adj in adjusted_p]
    return rejects, adjusted_p


def holm_bonferroni(
    p_values: List[float],
    alpha: float = 0.05
) -> Tuple[List[bool], List[float]]:
    """
    Apply Holm-Bonferroni step-down procedure to control Family-Wise Error Rate (FWER).
    Stronger than Bonferroni while preserving exact FWER control under arbitrary dependence.
    """
    m = len(p_values)
    if m == 0:
        return [], []
    if m == 1:
        p = float(p_values[0])
        return [p <= alpha], [p]

    p_arr = np.clip(np.asarray(p_values, dtype=float), 0.0, 1.0)
    sort_idx = np.argsort(p_arr)
    sorted_p = p_arr[sort_idx]

    multiplier = m - np.arange(m)
    adj_sorted = np.maximum.accumulate(sorted_p * multiplier)
    adj_sorted = np.clip(adj_sorted, 0.0, 1.0)

    inv_idx = np.empty(m, dtype=int)
    inv_idx[sort_idx] = np.arange(m)
    adjusted_p = adj_sorted[inv_idx].tolist()

    rejects = [adj <= alpha for adj in adjusted_p]
    return rejects, adjusted_p


def adjust_single_p_value(
    raw_p: float,
    total_hypotheses: int,
    method: str = "benjamini_hochberg"
) -> float:
    """
    Conservatively adjust a single candidate p-value given the known session search burden.
    If only one p-value is observed but total_hypotheses > 1, applies conservative multiplicity bound.
    """
    if total_hypotheses <= 1:
        return float(np.clip(raw_p, 0.0, 1.0))
    
    if method == "benjamini_hochberg":
        # Conservative BH bound: candidate treated as the most significant rank 1 among m tests
        # p_adj = min(1.0, raw_p * total_hypotheses)
        return float(np.clip(raw_p * total_hypotheses, 0.0, 1.0))
    elif method in ("bonferroni", "holm"):
        return float(np.clip(raw_p * total_hypotheses, 0.0, 1.0))
    else:
        return float(np.clip(raw_p, 0.0, 1.0))
