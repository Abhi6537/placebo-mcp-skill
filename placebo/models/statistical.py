"""
Pydantic schemas for statistical results, tests, and effect sizes.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StatisticalResult(BaseModel):
    effect_size: float = Field(..., description="Estimated treatment effect (difference in means)")
    percentage_change: Optional[float] = Field(None, description="Relative percentage change (%)")
    standard_error: float = Field(..., ge=0.0, description="Standard error of the effect estimate")
    raw_p_value: float = Field(..., ge=0.0, le=1.0, description="Unadjusted p-value")
    adjustment_method: str = Field("benjamini_hochberg", description="Multiple testing correction applied")
    adjusted_p_value: float = Field(..., ge=0.0, le=1.0, description="Adjusted p-value after multiplicity correction")
    confidence_interval: List[float] = Field(..., min_length=2, max_length=2, description="[lower_95, upper_95] CI")
    sample_size: int = Field(..., ge=0, description="Total sample observations")
    treatment_sample_size: Optional[int] = Field(None, ge=0)
    control_sample_size: Optional[int] = Field(None, ge=0)
    test_used: str = Field("welch_t_test", description="Statistical test executed")
    degrees_of_freedom: Optional[float] = Field(None)
    assumptions_met: bool = Field(True, description="Whether statistical test assumptions were satisfied")
    assumption_notes: Optional[str] = Field(None)


class SampleSummary(BaseModel):
    count: int
    mean: float
    std: float
    min_val: float
    max_val: float
    median: float
