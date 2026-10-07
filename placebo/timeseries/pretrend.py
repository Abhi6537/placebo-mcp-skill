"""
Pre-Trend Detection Falsification Test.
Tests whether the outcome metric was already exhibiting a systematic trend
in the pre-treatment period (violating the parallel trends assumption).
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
from placebo.models.falsification import (
    FalsificationResult,
    FalsificationTestType,
    PreTrendDetail,
    TestStatus,
)


def run_pretrend_test(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str,
    actual_intervention_date: str,
    alpha_threshold: float = 0.05
) -> FalsificationResult:
    """
    Run OLS regression on pre-intervention period:
    metric = beta_0 + beta_1 * time_step + error.

    Null Hypothesis (H0): beta_1 == 0 (Metric was stationary/flat before intervention).
    If p < alpha_threshold: We reject H0 -> A pre-trend was already present -> FAILED.
    """
    df_clean = df.copy()
    df_clean[date_col] = pd.to_datetime(df_clean[date_col])
    actual_t = pd.to_datetime(actual_intervention_date)

    # Isolate pre-intervention window
    pre_df = df_clean[df_clean[date_col] < actual_t].copy()
    if pre_df.empty:
        return FalsificationResult(
            test_type=FalsificationTestType.PRETREND,
            status=TestStatus.NOT_APPLICABLE,
            details="No observations found prior to intervention date.",
            metrics={"observations": 0}
        )

    # Aggregate metric daily
    daily = pre_df.groupby(pre_df[date_col].dt.normalize())[metric_col].mean().reset_index()
    daily = daily.sort_values(by=date_col)
    n_days = len(daily)

    if n_days < 5:
        return FalsificationResult(
            test_type=FalsificationTestType.PRETREND,
            status=TestStatus.INCONCLUSIVE,
            details=f"Insufficient pre-period days for trend estimation ({n_days} days). Minimum required is 5.",
            metrics={"n_days": n_days}
        )

    # Run linear regression over time index (0, 1, 2, ..., n_days - 1)
    x = np.arange(n_days, dtype=float)
    y = daily[metric_col].values.astype(float)

    # Filter any NaNs
    valid = np.isfinite(x) & np.isfinite(y)
    x_valid = x[valid]
    y_valid = y[valid]

    if len(x_valid) < 5 or np.all(y_valid == y_valid[0]):
        return FalsificationResult(
            test_type=FalsificationTestType.PRETREND,
            status=TestStatus.PASSED,
            details="Pre-treatment data is perfectly flat/constant.",
            metrics={"n_days": n_days, "slope": 0.0, "p_value": 1.0}
        )

    slope, intercept, r_value, p_value, std_err = stats.linregress(x_valid, y_valid)

    # If p < alpha_threshold, trend is statistically significant (FALSIFIED)
    has_trend = bool(p_value < alpha_threshold)

    if has_trend:
        status = TestStatus.FAILED
        direction = "upward" if slope > 0 else "downward"
        details = (
            f"Pre-trend detected: Metric exhibited a significant {direction} trend "
            f"(slope: {slope:.5f}/day, p = {p_value:.4f}) before the event occurred."
        )
    else:
        status = TestStatus.PASSED
        details = (
            f"Flat pre-trend confirmed: No statistically significant pre-existing trend "
            f"(slope: {slope:.5f}/day, p = {p_value:.4f} >= {alpha_threshold})."
        )

    detail_obj = PreTrendDetail(
        pre_period_slope=round(float(slope), 6),
        pre_period_p_value=round(float(p_value), 6),
        has_pre_trend=has_trend,
        observations_in_pre_period=int(n_days)
    )

    return FalsificationResult(
        test_type=FalsificationTestType.PRETREND,
        status=status,
        details=details,
        metrics={
            "slope": round(float(slope), 6),
            "p_value": round(float(p_value), 6),
            "r_squared": round(float(r_value ** 2), 4),
            "std_err": round(float(std_err), 6),
            "n_days": int(n_days)
        },
        pretrend_detail=detail_obj
    )
