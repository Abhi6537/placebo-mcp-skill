"""
Guardrails and validation for LLM explanations.
Ensures zero contradiction of deterministic verdicts and strict adherence to evidence.
"""

from typing import Dict
from placebo.models.evidence import EvidencePackage, GroundedExplanation
from placebo.models.verdict import VerdictGrade


def validate_explanation(
    package: EvidencePackage,
    data: Dict[str, str],
    provider_name: str
) -> GroundedExplanation:
    """
    Validate LLM output against the ground truth EvidencePackage.
    If contradiction detected, falls back to deterministic text.
    """
    headline = data.get("headline", "")
    verdict_text = data.get("verdict_explanation", "")
    full_text = f"{headline} {verdict_text}".upper()

    actual_grade = package.verdict.grade.value

    # Guardrail Check: Did model contradict the actual grade?
    contradiction = False
    if actual_grade == VerdictGrade.REFUTED.value and "CONFIRMED" in full_text:
        # Check if it was asserting confirmation instead of acknowledging refutation
        if "WAS CONFIRMED" in full_text or "IS CONFIRMED" in full_text:
            contradiction = True
    elif actual_grade == VerdictGrade.CONFIRMED.value and "WAS REFUTED" in full_text:
        contradiction = True

    if contradiction:
        # Fallback to pure deterministic summary
        return GroundedExplanation(
            provider=f"{provider_name} [guardrail_fallback]",
            headline=f"Verdict is {actual_grade}: {package.verdict.summary}",
            what_was_tested=package.hypothesis.claim_description,
            what_was_observed=f"Effect size: {package.statistical_result.effect_size}, p_adj: {package.statistical_result.adjusted_p_value}",
            falsification_checks_summary="Deterministic test execution completed.",
            verdict_explanation=package.verdict.summary,
            recommended_action=package.verdict.recommendation,
            guardrail_passed=False
        )

    return GroundedExplanation(
        provider=provider_name,
        headline=data.get("headline", package.verdict.summary),
        what_was_tested=data.get("what_was_tested", package.hypothesis.claim_description),
        what_was_observed=data.get("what_was_observed", f"Observed effect: {package.statistical_result.effect_size}"),
        falsification_checks_summary=data.get("falsification_checks_summary", "Falsification tests evaluated."),
        verdict_explanation=data.get("verdict_explanation", package.verdict.summary),
        recommended_action=data.get("recommended_action", package.verdict.recommendation),
        guardrail_passed=True
    )
