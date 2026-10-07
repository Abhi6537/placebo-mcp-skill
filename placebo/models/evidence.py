"""
Pydantic schema for the Evidence Package (Schema v1.0).
This is the immutable contract shared across all modules.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from placebo.models.falsification import FalsificationResult
from placebo.models.hypothesis import Hypothesis, SearchContext
from placebo.models.statistical import StatisticalResult
from placebo.models.verdict import VerdictDecision


class GroundedExplanation(BaseModel):
    provider: str = Field(..., description="LLM provider name, e.g. gemini-2.5-flash or ollama")
    headline: str = Field(..., description="Executive 1-sentence finding")
    what_was_tested: str
    what_was_observed: str
    falsification_checks_summary: str
    verdict_explanation: str
    recommended_action: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    guardrail_passed: bool = True


class EvidencePackage(BaseModel):
    schema_version: str = Field("1.0", description="Strict evidence schema version")
    audit_id: str = Field(..., description="Unique audit package ID, e.g. AUDIT-20261007-001")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    hypothesis: Hypothesis
    search_context: SearchContext
    statistical_result: StatisticalResult
    falsification_results: List[FalsificationResult] = Field(default_factory=list)
    verdict: VerdictDecision
    query_lineage: Optional[Dict[str, Any]] = Field(default_factory=dict)
    explanation: Optional[GroundedExplanation] = None
