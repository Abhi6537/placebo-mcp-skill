"""
Model-agnostic LLM Client for Placebo.
Dispatches to configured provider (Gemini, Ollama, or deterministic fallback).
"""

import os
from typing import Optional
from placebo.models.evidence import EvidencePackage, GroundedExplanation
from placebo.protocols.llm import LLMExplainer
from placebo.llm.providers.gemini import GeminiProvider
from placebo.llm.providers.ollama import OllamaProvider


class PlaceboLLMClient:
    """Unified LLM client implementing LLMExplainer protocol."""

    def __init__(self, provider: Optional[str] = None):
        self.provider_choice = provider or os.getenv("LLM_PROVIDER", "gemini").lower()
        self.gemini = GeminiProvider()
        self.ollama = OllamaProvider()

    def explain(self, package: EvidencePackage) -> GroundedExplanation:
        """Selects provider and executes explanation with automatic graceful fallback."""
        if self.provider_choice == "gemini" and self.gemini.is_available():
            return self.gemini.explain(package)
        elif self.provider_choice == "ollama" and self.ollama.is_available():
            return self.ollama.explain(package)
        elif self.gemini.is_available():
            return self.gemini.explain(package)
        elif self.ollama.is_available():
            return self.ollama.explain(package)

        # Deterministic Fallback if no LLM API is configured or reachable
        return GroundedExplanation(
            provider="deterministic_engine [no_llm_configured]",
            headline=f"Audited Verdict: {package.verdict.grade.value}",
            what_was_tested=package.hypothesis.claim_description,
            what_was_observed=(
                f"Effect Size: {package.statistical_result.effect_size} "
                f"(Raw p: {package.statistical_result.raw_p_value}, "
                f"Adjusted p: {package.statistical_result.adjusted_p_value})"
            ),
            falsification_checks_summary=(
                f"Completed {len(package.falsification_results)} stress tests "
                f"across placebo dates, pre-trends, and cluster sensitivity."
            ),
            verdict_explanation=package.verdict.summary,
            recommended_action=package.verdict.recommendation,
            guardrail_passed=True
        )
