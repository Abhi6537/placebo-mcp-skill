"""
Protocol defining LLM explanation boundaries.
"""

from typing import Protocol, runtime_checkable
from placebo.models.evidence import EvidencePackage, GroundedExplanation


@runtime_checkable
class LLMExplainer(Protocol):
    """Protocol for generating plain-language explanations from Evidence Packages."""

    def explain(self, evidence: EvidencePackage) -> GroundedExplanation:
        """Translate structured evidence into an executive narrative with zero hallucinations."""
        ...
