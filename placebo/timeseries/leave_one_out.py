"""
Leave-One-Out (Jackknife Sensitivity) Falsification Test.
Tests whether the estimated effect size is driven by a single high-leverage entity/cluster.
"""

from typing import List, Optional
import numpy as np
import pandas as pd
from placebo.models.falsification import (
    FalsificationResult,
    FalsificationTestType,
    LeaveOneOutDetail,
    TestStatus,
)
from placebo.statistics.effects import compute_two_sample_effect


def run_leave_one_out_test(
    df: pd.DataFrame,
    entity_col: str,
    date_col: str,
    metric_col: str,
    intervention_date: str,
    max_drop_threshold: float = 0.50
) -> FalsificationResult:
    """
    Sequentially omit each top entity/cluster and re-estimate the treatment effect.
    If dropping one entity causes the effect to collapse (> 50% drop or sign flip),
    the finding is classified as fragile (FAILED).
    """
    df_clean = df.copy()
    df_clean[date_col] = pd.to_datetime(df_clean[date_col])
    t_date = pd.to_datetime(intervention_date)

    # Compute baseline effect
    post_vals = df_clean[df_clean[date_col] >= t_date][metric_col].dropna().tolist()
    pre_vals = df_clean[df_clean[date_col] < t_date][metric_col].dropna().tolist()

    baseline_res = compute_two_sample_effect(post_vals, pre_vals)
    baseline_effect = baseline_res.effect_size

    if df_clean[entity_col].nunique() <= 1:
        return FalsificationResult(
            test_type=FalsificationTestType.LEAVE_ONE_OUT,
            status=TestStatus.NOT_APPLICABLE,
            details=f"Single entity detected ({df_clean[entity_col].iloc[0]}); jackknife sensitivity requires >= 2 entities.",
            metrics={"unique_entities": 1}
        )

    # Identify top entities by both metric sum (whales) and row count (high frequency)
    by_metric = df_clean.groupby(entity_col)[metric_col].apply(lambda s: s.abs().sum()).sort_values(ascending=False)
    by_counts = df_clean[entity_col].value_counts()
    candidate_entities = list(dict.fromkeys(by_metric.head(10).index.tolist() + by_counts.head(10).index.tolist()))

    effects_without_entity: List[float] = []
    influential_entities: List[str] = []

    for ent in candidate_entities:
        subset = df_clean[df_clean[entity_col] != ent]
        sub_post = subset[subset[date_col] >= t_date][metric_col].dropna().tolist()
        sub_pre = subset[subset[date_col] < t_date][metric_col].dropna().tolist()

        res_sub = compute_two_sample_effect(sub_post, sub_pre)
        sub_eff = res_sub.effect_size
        effects_without_entity.append(sub_eff)

        # Check drop ratio
        drop_ratio = (abs(baseline_effect) - abs(sub_eff)) / abs(baseline_effect)
        sign_flip = (baseline_effect > 0 and sub_eff < 0) or (baseline_effect < 0 and sub_eff > 0)

        if drop_ratio > max_drop_threshold or sign_flip:
            influential_entities.append(str(ent))

    min_eff = float(np.min(effects_without_entity)) if effects_without_entity else baseline_effect
    max_eff = float(np.max(effects_without_entity)) if effects_without_entity else baseline_effect

    max_drop = 0.0
    for eff in effects_without_entity:
        d = (abs(baseline_effect) - abs(eff)) / abs(baseline_effect)
        if d > max_drop:
            max_drop = d

    is_fragile = len(influential_entities) > 0

    if is_fragile:
        status = TestStatus.FAILED
        details = (
            f"Fragile finding: Removing entity {influential_entities[0]} causes the effect "
            f"to collapse by {max_drop * 100:.1f}% (threshold {max_drop_threshold * 100:.0f}%)."
        )
    else:
        status = TestStatus.PASSED
        details = (
            f"Robust across entities: The effect survived jackknife exclusion across all top clusters "
            f"(max drop: {max_drop * 100:.1f}%)."
        )

    detail_obj = LeaveOneOutDetail(
        baseline_effect=round(baseline_effect, 6),
        min_effect=round(min_eff, 6),
        max_effect=round(max_eff, 6),
        max_percentage_drop=round(max_drop * 100, 2),
        is_fragile=is_fragile,
        influential_entities=influential_entities
    )

    return FalsificationResult(
        test_type=FalsificationTestType.LEAVE_ONE_OUT,
        status=status,
        details=details,
        metrics={
            "max_percentage_drop": round(max_drop * 100, 2),
            "influential_entities_count": len(influential_entities),
            "min_effect": round(min_eff, 6),
            "max_effect": round(max_eff, 6)
        },
        leave_one_out_detail=detail_obj
    )
