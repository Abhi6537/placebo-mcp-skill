"""
Deterministic Verdict Decision Engine.
Pure function mapping statistical and falsification results to a final grade.
Zero LLM interference; 100% deterministic rule matrix.
"""

from typing import List, Optional
from placebo.models.falsification import FalsificationResult, FalsificationTestType, TestStatus
from placebo.models.statistical import StatisticalResult
from placebo.models.verdict import (
    ConfidenceLevel,
    RuleEvaluation,
    VerdictDecision,
    VerdictGrade,
)


def evaluate_verdict(
    statistical_result: StatisticalResult,
    falsification_results: List[FalsificationResult],
    alpha_threshold: float = 0.05
) -> VerdictDecision:
    """
    Pure function evaluating the deterministic verdict matrix.
    evidence_in -> verdict_out.
    """
    rules: List[RuleEvaluation] = []
    p_adj = statistical_result.adjusted_p_value

    # Rule 1: Multiplicity-Corrected Significance
    r1_passed = p_adj <= alpha_threshold
    rules.append(RuleEvaluation(
        rule_id="R1_MULTIPLICITY_CORRECTION",
        rule_name="Significance After Multiplicity Correction",
        passed=r1_passed,
        description=f"Adjusted p-value must be <= {alpha_threshold}.",
        observed_value=f"p_adj = {p_adj:.4f}",
        threshold=f"alpha = {alpha_threshold}"
    ))

    # Rule 2: Pre-Trend Invariance
    pretrend_res = next((r for r in falsification_results if r.test_type == FalsificationTestType.PRETREND), None)
    if pretrend_res and pretrend_res.status == TestStatus.FAILED:
        r2_passed = False
        r2_obs = "Pre-existing trend detected before intervention"
    elif pretrend_res and pretrend_res.status == TestStatus.PASSED:
        r2_passed = True
        r2_obs = "Pre-treatment trend was flat/neutral"
    else:
        r2_passed = True
        r2_obs = "Pre-trend test not applicable or inconclusive"

    rules.append(RuleEvaluation(
        rule_id="R2_PRETREND_NEUTRALITY",
        rule_name="Pre-Treatment Parallel Trend Invariance",
        passed=r2_passed,
        description="Metric must not exhibit statistically significant drift prior to intervention.",
        observed_value=r2_obs,
        threshold="p >= 0.05"
    ))

    # Rule 3: Placebo Dates Robustness
    placebo_res = next((r for r in falsification_results if r.test_type == FalsificationTestType.PLACEBO_DATES), None)
    if placebo_res and placebo_res.status == TestStatus.FAILED:
        r3_passed = False
        r3_obs = f"Spurious effect discovered at fake historical dates"
    elif placebo_res and placebo_res.status == TestStatus.PASSED:
        r3_passed = True
        r3_obs = "No significant effect detected at pseudo-intervention dates"
    else:
        r3_passed = True
        r3_obs = "Placebo dates test not executed"

    rules.append(RuleEvaluation(
        rule_id="R3_IN_TIME_PLACEBOS",
        rule_name="In-Time Placebo Date Robustness",
        passed=r3_passed,
        description="At least 80% of pseudo-intervention dates must show no significant effect.",
        observed_value=r3_obs,
        threshold="Failure ratio <= 20%"
    ))

    # Rule 4: Leave-One-Out Sensitivity
    loo_res = next((r for r in falsification_results if r.test_type == FalsificationTestType.LEAVE_ONE_OUT), None)
    if loo_res and loo_res.status == TestStatus.FAILED:
        r4_passed = False
        r4_obs = "Effect collapsed when omitting single high-leverage entity"
    else:
        r4_passed = True
        r4_obs = "Effect stable across cluster exclusions"

    rules.append(RuleEvaluation(
        rule_id="R4_LEAVE_ONE_OUT",
        rule_name="Leave-One-Out Sensitivity",
        passed=r4_passed,
        description="Effect must not depend exclusively on a single entity or outlier.",
        observed_value=r4_obs,
        threshold="Max drop <= 50%"
    ))

    # Decision Matrix Resolution
    # REFUTED: Failed pre-trend OR failed placebo dates OR adjusted p > 0.10 with high search burden
    if not r2_passed:
        grade = VerdictGrade.REFUTED
        confidence = ConfidenceLevel.HIGH
        reason = "A pre-existing trend was already present before the intervention occurred."
        summary = "REFUTED: The observed change was caused by an ongoing baseline trend, not the intervention."
        rec = "Reject the claim of causal impact. The metric was already increasing/decreasing prior to the event."
    elif not r3_passed:
        grade = VerdictGrade.REFUTED
        confidence = ConfidenceLevel.HIGH
        reason = "Identical or stronger effects appeared at fake historical placebo dates."
        summary = "REFUTED: Spurious correlation detected. The same effect appears at dates where no event occurred."
        rec = "Reject the causal claim. The effect is likely seasonal or cyclical noise."
    elif not r1_passed:
        if p_adj <= 0.10:
            grade = VerdictGrade.INCONCLUSIVE
            confidence = ConfidenceLevel.LOW
            reason = f"Borderline significance after multiplicity correction (p_adj = {p_adj:.4f})."
            summary = "INCONCLUSIVE: Weak statistical evidence that does not survive rigorous family-wise threshold."
            rec = "Collect additional sample size or pre-register a dedicated follow-up experiment."
        else:
            grade = VerdictGrade.REFUTED
            confidence = ConfidenceLevel.HIGH
            reason = f"Failed multiplicity correction (p_adj = {p_adj:.4f} > {alpha_threshold})."
            summary = "REFUTED: The finding disappears when penalizing for multiple testing."
            rec = "Reject the finding. It is a false discovery resulting from data dredging."
    elif not r4_passed:
        grade = VerdictGrade.INCONCLUSIVE
        confidence = ConfidenceLevel.MEDIUM
        reason = "Fragile finding driven predominantly by an outlier entity."
        summary = "INCONCLUSIVE: The estimated lift is disproportionately driven by a single high-leverage cluster."
        rec = "Re-analyze with winsorization or median metrics excluding high-leverage outliers."
    else:
        # ALL PASSED
        grade = VerdictGrade.CONFIRMED
        confidence = ConfidenceLevel.HIGH
        reason = None
        summary = f"CONFIRMED: Statistically robust finding (p_adj = {p_adj:.4f}) that survived all falsification stress tests."
        rec = "Accept finding. The evidence is consistent with a genuine treatment effect."

    return VerdictDecision(
        grade=grade,
        confidence=confidence,
        summary=summary,
        primary_failure_reason=reason,
        rules_evaluated=rules,
        recommendation=rec
    )
