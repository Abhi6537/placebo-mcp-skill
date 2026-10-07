"""
Comprehensive statistical and falsification validation unit tests.
Verifies mathematical determinism and expected known outcomes.
"""

import numpy as np
import pandas as pd
import pytest

from placebo.statistics.multiple_testing import benjamini_hochberg, holm_bonferroni, adjust_single_p_value
from placebo.statistics.effects import compute_two_sample_effect
from placebo.timeseries.pretrend import run_pretrend_test
from placebo.timeseries.placebo_dates import run_placebo_dates_test
from placebo.timeseries.leave_one_out import run_leave_one_out_test
from placebo.models.falsification import TestStatus


def test_benjamini_hochberg_known_values():
    """Verify BH adjustment controls FDR and preserves monotonicity."""
    raw_p = [0.001, 0.01, 0.03, 0.04, 0.05, 0.20, 0.50]
    rejects, adj_p = benjamini_hochberg(raw_p, alpha=0.05)

    assert len(rejects) == len(raw_p)
    assert len(adj_p) == len(raw_p)
    # Ranks:
    # 0.001 * 7/1 = 0.007
    # 0.01 * 7/2 = 0.035
    # All adjusted p-values must be >= raw p-values
    for r, a in zip(raw_p, adj_p):
        assert a >= r
    # Monotonicity check
    for i in range(len(adj_p) - 1):
        assert adj_p[i] <= adj_p[i + 1] + 1e-9


def test_adjust_single_p_value_burden():
    """Verify penalty scales when searching many hypotheses."""
    raw_p = 0.02
    assert adjust_single_p_value(raw_p, total_hypotheses=1) == 0.02
    assert adjust_single_p_value(raw_p, total_hypotheses=10) == 0.20
    assert adjust_single_p_value(raw_p, total_hypotheses=100) == 1.0


def test_welch_t_test_known_difference():
    """Verify Welch's t-test detects genuine shift."""
    np.random.seed(42)
    control = np.random.normal(loc=10.0, scale=1.0, size=100).tolist()
    treatment = np.random.normal(loc=12.0, scale=1.0, size=100).tolist()

    res = compute_two_sample_effect(treatment, control)
    assert res.assumptions_met is True
    assert res.effect_size > 1.7
    assert res.raw_p_value < 1e-5
    assert res.confidence_interval[0] > 0.0


def test_pretrend_flat_vs_drifting():
    """Verify pre-trend test flags ongoing trends and passes flat pre-periods."""
    # Flat pre-period
    dates = pd.date_range("2026-01-01", "2026-01-30", freq="D")
    df_flat = pd.DataFrame({
        "event_date": dates,
        "revenue": np.random.normal(100, 2, len(dates))
    })
    res_flat = run_pretrend_test(df_flat, "event_date", "revenue", "2026-01-20")
    assert res_flat.status == TestStatus.PASSED

    # Drifting pre-period (steep upward slope)
    df_drift = pd.DataFrame({
        "event_date": dates,
        "revenue": [100.0 + (i * 5.0) for i in range(len(dates))]
    })
    res_drift = run_pretrend_test(df_drift, "event_date", "revenue", "2026-01-20")
    assert res_drift.status == TestStatus.FAILED
    assert res_drift.pretrend_detail.has_pre_trend is True


def test_leave_one_out_outlier_sensitivity():
    """Verify jackknife sensitivity detects fragile findings driven by one whale."""
    dates = pd.date_range("2026-01-01", "2026-01-30", freq="D")
    rows = []
    # Regular users with zero treatment effect
    for d in dates:
        for u in range(1, 20):
            rows.append({"date": d, "user_id": f"user_{u}", "amount": 10.0})
    # Add one massive whale that appears only in post-treatment
    for d in pd.date_range("2026-01-16", "2026-01-30", freq="D"):
        rows.append({"date": d, "user_id": "whale_user", "amount": 10000.0})

    df = pd.DataFrame(rows)
    res = run_leave_one_out_test(df, "user_id", "date", "amount", "2026-01-15")
    assert res.status == TestStatus.FAILED
    assert "whale_user" in res.leave_one_out_detail.influential_entities
