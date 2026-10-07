"""
Audit Pipeline Orchestrator.
Chains: Data Fetch -> Statistical Analysis -> Multiplicity Correction ->
        Falsification Battery -> Deterministic Verdict -> Grounded Explanation -> Sealed Package.
"""

import logging
from typing import List, Optional
import pandas as pd

from placebo.evidence.builder import assemble_evidence_package
from placebo.models.evidence import EvidencePackage
from placebo.models.falsification import FalsificationResult
from placebo.models.hypothesis import Hypothesis, SearchContext
from placebo.protocols.llm import LLMExplainer
from placebo.protocols.storage import StorageAdapter
from placebo.statistics.effects import compute_two_sample_effect
from placebo.statistics.multiple_testing import adjust_single_p_value
from placebo.timeseries.leave_one_out import run_leave_one_out_test
from placebo.timeseries.placebo_dates import run_placebo_dates_test
from placebo.timeseries.pretrend import run_pretrend_test
from placebo.verdict.engine import evaluate_verdict

logger = logging.getLogger("placebo.pipeline")


class AuditPipeline:
    """End-to-end falsification audit pipeline."""

    def __init__(
        self,
        storage: StorageAdapter,
        llm_explainer: Optional[LLMExplainer] = None
    ):
        self.storage = storage
        self.llm_explainer = llm_explainer

    def run_audit(
        self,
        hypothesis: Hypothesis,
        df: pd.DataFrame,
        entity_col: str,
        date_col: str,
        metric_col: str
    ) -> EvidencePackage:
        """
        Execute full audit pipeline on an in-memory DataFrame or fetched Snowflake data.
        Returns a sealed, validated EvidencePackage.
        """
        logger.info(f"Starting audit for {hypothesis.hypothesis_id}: {hypothesis.claim_description}")

        # 1. Retrieve or calculate search context (multiplicity burden)
        search_ctx = self.storage.get_search_context(hypothesis.session_id)

        # 2. Extract treatment vs control (or post vs pre around intervention date)
        intervention_date = hypothesis.time_window.intervention_date
        if not intervention_date:
            raise ValueError(f"Hypothesis {hypothesis.hypothesis_id} missing intervention_date in time_window.")

        df_sorted = df.copy()
        df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
        t_date = pd.to_datetime(intervention_date)

        post_vals = df_sorted[df_sorted[date_col] >= t_date][metric_col].dropna().tolist()
        pre_vals = df_sorted[df_sorted[date_col] < t_date][metric_col].dropna().tolist()

        # 3. Compute baseline statistical effect
        stat_res = compute_two_sample_effect(post_vals, pre_vals)

        # 4. Multiplicity adjustment based on session search burden
        stat_res.adjusted_p_value = adjust_single_p_value(
            stat_res.raw_p_value,
            total_hypotheses=search_ctx.total_hypotheses_tested,
            method="benjamini_hochberg"
        )
        stat_res.adjustment_method = "benjamini_hochberg"

        # 5. Execute Active Falsification Battery
        falsification_results: List[FalsificationResult] = []

        # 5a. Pre-trend test
        pretrend_res = run_pretrend_test(
            df_sorted,
            date_col=date_col,
            metric_col=metric_col,
            actual_intervention_date=intervention_date
        )
        falsification_results.append(pretrend_res)

        # 5b. Placebo dates test
        placebo_res = run_placebo_dates_test(
            df_sorted,
            date_col=date_col,
            metric_col=metric_col,
            actual_intervention_date=intervention_date,
            real_effect=stat_res.effect_size
        )
        falsification_results.append(placebo_res)

        # 5c. Leave-one-out sensitivity test
        if entity_col in df_sorted.columns:
            loo_res = run_leave_one_out_test(
                df_sorted,
                entity_col=entity_col,
                date_col=date_col,
                metric_col=metric_col,
                intervention_date=intervention_date
            )
            falsification_results.append(loo_res)

        # 6. Evaluate Deterministic Verdict Matrix
        verdict = evaluate_verdict(stat_res, falsification_results)

        # 7. Assemble draft Evidence Package
        package = assemble_evidence_package(
            hypothesis=hypothesis,
            search_context=search_ctx,
            statistical_result=stat_res,
            falsification_results=falsification_results,
            verdict=verdict,
            explanation=None
        )

        # 8. Optional LLM Translation (Gemma / Gemini / Ollama)
        if self.llm_explainer:
            try:
                explanation = self.llm_explainer.explain(package)
                package.explanation = explanation
            except Exception as e:
                logger.warning(f"LLM explanation failed or skipped: {e}. Proceeding with raw evidence.")

        # 9. Persist evidence package
        self.storage.save_evidence_package(package)
        logger.info(f"Audit completed: {package.audit_id} -> Verdict: {verdict.grade.value}")

        return package
