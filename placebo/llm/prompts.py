"""
Prompt Contract and formatting for the Gemma / LLM explanation layer.
Strictly constrains the model to translate without calculating or hallucinating.
"""

from placebo.models.evidence import EvidencePackage

SYSTEM_PROMPT = """You are an impartial scientific auditor reviewing a statistical evidence package produced by the Placebo falsification engine.

YOUR ABSOLUTE CONSTRAINTS:
1. You must state the exact deterministic verdict: CONFIRMED, INCONCLUSIVE, or REFUTED.
2. You must NEVER recalculate, modify, or invent any numbers, p-values, sample sizes, or percentages.
3. Every claim you make must be directly backed by the provided JSON package.
4. Use precise econometric terminology: "evidence is consistent with", "insufficient evidence", "the effect was falsified by".
5. Return your output strictly as a JSON object matching the requested schema.

JSON RESPONSE FORMAT:
{
  "headline": "<Executive 1-sentence summary of the finding and verdict>",
  "what_was_tested": "<The business hypothesis, metric, and time window tested>",
  "what_was_observed": "<The observed effect size, standard error, raw and adjusted p-values>",
  "falsification_checks_summary": "<Summary of what passed and failed across placebo dates, pre-trend, and leave-one-out tests>",
  "verdict_explanation": "<Why this deterministic grade was assigned based on the test battery>",
  "recommended_action": "<Concrete advice for the business team>"
}
"""


def build_evidence_prompt(package: EvidencePackage) -> str:
    """Format the EvidencePackage into an explicit, structured audit prompt."""
    return f"""Please review and explain this sealed Placebo Evidence Package:

AUDIT ID: {package.audit_id}
SCHEMA VERSION: {package.schema_version}

HYPOTHESIS:
- Claim: {package.hypothesis.claim_description}
- Metric: {package.hypothesis.metric.name} ({package.hypothesis.metric.column})
- Time Window: {package.hypothesis.time_window.start} to {package.hypothesis.time_window.end}
- Intervention Date: {package.hypothesis.time_window.intervention_date}

SEARCH CONTEXT:
- Total Hypotheses/Queries Explored: {package.search_context.total_hypotheses_tested}

STATISTICAL RESULTS:
- Estimated Effect Size: {package.statistical_result.effect_size}
- Percentage Change: {package.statistical_result.percentage_change}%
- Standard Error: {package.statistical_result.standard_error}
- Raw p-value: {package.statistical_result.raw_p_value}
- Multiple Testing Method: {package.statistical_result.adjustment_method}
- Multiplicity Adjusted p-value: {package.statistical_result.adjusted_p_value}
- 95% Confidence Interval: {package.statistical_result.confidence_interval}
- Total Sample Size: {package.statistical_result.sample_size}
- Test Selected: {package.statistical_result.test_used}

FALSIFICATION BATTERY OUTCOMES:
{json_format_falsifications(package.falsification_results)}

DETERMINISTIC VERDICT:
- Grade: {package.verdict.grade.value}
- Confidence: {package.verdict.confidence.value}
- Summary: {package.verdict.summary}
- Failure Reason: {package.verdict.primary_failure_reason or "None"}
- Recommendation: {package.verdict.recommendation}

Generate the structured JSON explanation following the prompt contract.
"""


def json_format_falsifications(results) -> str:
    lines = []
    for r in results:
        lines.append(f"- [{r.test_type.value}] Status: {r.status.value} -> Details: {r.details}")
    return "\n".join(lines)
