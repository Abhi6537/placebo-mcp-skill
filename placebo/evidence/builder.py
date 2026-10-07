"""
Evidence Package Assembly and Validation.
Builds the final immutable EvidencePackage (Schema v1.0).
"""

from datetime import datetime
import uuid
from typing import Any, Dict, List, Optional

from placebo.models.evidence import EvidencePackage, GroundedExplanation
from placebo.models.falsification import FalsificationResult
from placebo.models.hypothesis import Hypothesis, SearchContext
from placebo.models.statistical import StatisticalResult
from placebo.models.verdict import VerdictDecision


def assemble_evidence_package(
    hypothesis: Hypothesis,
    search_context: SearchContext,
    statistical_result: StatisticalResult,
    falsification_results: List[FalsificationResult],
    verdict: VerdictDecision,
    explanation: Optional[GroundedExplanation] = None,
    query_lineage: Optional[Dict[str, Any]] = None
) -> EvidencePackage:
    """Construct, seal, and validate an immutable EvidencePackage."""
    now_str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    audit_id = f"AUDIT-{now_str}-{uuid.uuid4().hex[:6].upper()}"

    package = EvidencePackage(
        schema_version="1.0",
        audit_id=audit_id,
        generated_at=datetime.utcnow(),
        hypothesis=hypothesis,
        search_context=search_context,
        statistical_result=statistical_result,
        falsification_results=falsification_results,
        verdict=verdict,
        query_lineage=query_lineage or {},
        explanation=explanation
    )

    return package
