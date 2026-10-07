"""
Pydantic schemas for Falsification tests (Placebo dates, Pre-trends, Sensitivity).
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    __test__ = False
    PASSED = "PASSED"
    FAILED = "FAILED"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FalsificationTestType(str, Enum):
    PLACEBO_DATES = "placebo_dates"
    PRETREND = "pretrend"
    LEAVE_ONE_OUT = "leave_one_out"
    PLACEBO_COHORT = "placebo_cohort"


class PlaceboDatesDetail(BaseModel):
    fake_dates: List[str] = Field(default_factory=list)
    placebo_effects: List[float] = Field(default_factory=list)
    real_effect: float
    dates_failed: int = Field(0, description="Count of fake dates showing statistically significant effect")
    total_dates_tested: int = Field(0)
    failure_ratio: float = Field(0.0, description="Ratio of failed placebo dates")


class PreTrendDetail(BaseModel):
    pre_period_slope: float = Field(..., description="Estimated slope in pre-intervention period")
    pre_period_p_value: float = Field(..., description="p-value testing H0: slope == 0")
    has_pre_trend: bool = Field(..., description="True if pre-trend is statistically significant (falsification fails)")
    observations_in_pre_period: int = Field(..., ge=0)


class LeaveOneOutDetail(BaseModel):
    baseline_effect: float
    min_effect: float
    max_effect: float
    max_percentage_drop: float
    is_fragile: bool = Field(..., description="True if dropping a single entity/cluster collapses the effect")
    influential_entities: List[str] = Field(default_factory=list)


class FalsificationResult(BaseModel):
    test_type: FalsificationTestType
    status: TestStatus
    details: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    placebo_dates_detail: Optional[PlaceboDatesDetail] = None
    pretrend_detail: Optional[PreTrendDetail] = None
    leave_one_out_detail: Optional[LeaveOneOutDetail] = None
