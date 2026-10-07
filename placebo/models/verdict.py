"""
Pydantic schemas for deterministic Verdict results and rules.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class VerdictGrade(str, Enum):
    CONFIRMED = "CONFIRMED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REFUTED = "REFUTED"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RuleEvaluation(BaseModel):
    rule_id: str
    rule_name: str
    passed: bool
    description: str
    observed_value: Optional[str] = None
    threshold: Optional[str] = None


class VerdictDecision(BaseModel):
    grade: VerdictGrade
    confidence: ConfidenceLevel
    summary: str
    primary_failure_reason: Optional[str] = None
    rules_evaluated: List[RuleEvaluation] = Field(default_factory=list)
    recommendation: str
