"""
Placebo Dates (In-Time Placebo) Falsification Test.
Tests whether an identical or stronger effect appears at arbitrary historical dates
where NO intervention occurred.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
from placebo.models.falsification import (
    FalsificationResult,
    FalsificationTestType,
    PlaceboDatesDetail,
    TestStatus,
)
from placebo.statistics.effects import compute_two_sample_effect


def run_placebo_dates_test(
    df: pd.DataFrame,
    date_col: str,
    metric_col: str,
    actual_intervention_date: str,
    real_effect: float,
    num_fake_dates: int = 5,
    min_window_days: int = 7
) -> FalsificationResult:
    """
    Execute In-Time Placebo test strictly using historical data prior to actual_intervention_date.

    Rule: No placebo date may leak into the actual treatment period.
    """
    df_clean = df.copy()
    df_clean[date_col] = pd.to_datetime(df_clean[date_col])
    actual_t = pd.to_datetime(actual_intervention_date)

    # Filter strictly to pre-intervention period
    pre_data = df_clean[df_clean[date_col] < actual_t].sort_values(by=date_col)

    unique_dates = pre_data[date_col].dt.normalize().unique()
    total_pre_days = len(unique_dates)

    # Need enough dates to define pre and post pseudo-windows
    if total_pre_days < (2 * min_window_days + num_fake_dates):
        return FalsificationResult(
            test_type=FalsificationTestType.PLACEBO_DATES,
            status=TestStatus.NOT_APPLICABLE,
            details=f"Insufficient pre-treatment duration ({total_pre_days} days). Requires >= {2 * min_window_days + num_fake_dates} days.",
            metrics={"total_pre_days": total_pre_days}
        )

    # Pick candidate pseudo intervention dates evenly spaced in the valid pre-period range
    valid_range = unique_dates[min_window_days : total_pre_days - min_window_days]
    if len(valid_range) < num_fake_dates:
        candidate_indices = np.arange(len(valid_range))
    else:
        candidate_indices = np.linspace(0, len(valid_range) - 1, num_fake_dates, dtype=int)

    selected_fake_dates = [valid_range[i] for i in candidate_indices]

    placebo_effects: List[float] = []
    fake_date_strings: List[str] = []
    failed_dates_count = 0

    for fake_dt in selected_fake_dates:
        dt_str = pd.Timestamp(fake_dt).strftime("%Y-%m-%d")
        fake_date_strings.append(dt_str)

        # Pre vs Post around this fake date, bounded strictly within pre_data
        post_fake = pre_data[pre_data[date_col] >= fake_dt][metric_col].dropna().tolist()
        pre_fake = pre_data[pre_data[date_col] < fake_dt][metric_col].dropna().tolist()

        res = compute_two_sample_effect(post_fake, pre_fake)
        fake_effect = res.effect_size
        placebo_effects.append(round(fake_effect, 6))

        # Check if the fake date showed an effect comparable to the real effect
        # or statistically significant at alpha=0.05
        is_significant_fake = res.raw_p_value < 0.05
        effect_ratio = abs(fake_effect) / (abs(real_effect) + 1e-9)

        if is_significant_fake and effect_ratio > 0.5:
            failed_dates_count += 1

    total_tested = len(selected_fake_dates)
    failure_ratio = (failed_dates_count / total_tested) if total_tested > 0 else 0.0

    # Verdict on test: Passed if <= 20% of placebo dates show false effect
    if failure_ratio <= 0.20:
        status = TestStatus.PASSED
        details = f"Passed: Only {failed_dates_count} of {total_tested} placebo dates showed significant effects (threshold <= 20%)."
    else:
        status = TestStatus.FAILED
        details = f"Failed: Spurious effect detected at {failed_dates_count} of {total_tested} placebo dates prior to intervention."

    detail_obj = PlaceboDatesDetail(
        fake_dates=fake_date_strings,
        placebo_effects=placebo_effects,
        real_effect=round(real_effect, 6),
        dates_failed=failed_dates_count,
        total_dates_tested=total_tested,
        failure_ratio=round(failure_ratio, 3)
    )

    return FalsificationResult(
        test_type=FalsificationTestType.PLACEBO_DATES,
        status=status,
        details=details,
        metrics={
            "failed_count": failed_dates_count,
            "total_tested": total_tested,
            "failure_ratio": round(failure_ratio, 3),
            "max_placebo_effect": round(float(np.max(np.abs(placebo_effects))), 6) if placebo_effects else 0.0
        },
        placebo_dates_detail=detail_obj
    )
