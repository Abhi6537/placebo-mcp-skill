"""
Pydantic schemas for Hypotheses, Queries, and Session Search Context.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class HypothesisStatus(str, Enum):
    REGISTERED = "REGISTERED"
    EVALUATING = "EVALUATING"
    CONFIRMED = "CONFIRMED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REFUTED = "REFUTED"


class TimeWindow(BaseModel):
    start: str = Field(..., description="Start date (YYYY-MM-DD)")
    end: str = Field(..., description="End date (YYYY-MM-DD)")
    intervention_date: Optional[str] = Field(None, description="Actual intervention/event date (YYYY-MM-DD)")


class MetricDefinition(BaseModel):
    name: str = Field(..., description="Business metric name, e.g. conversion_rate, revenue")
    column: str = Field(..., description="Underlying database column name")
    aggregation: str = Field("mean", description="Aggregation function: mean, sum, count, ratio")


class SegmentFilter(BaseModel):
    dimension: str = Field(..., description="Dimension column name, e.g. country, platform")
    operator: str = Field("=", description="Comparison operator: =, !=, IN, >, <")
    value: str = Field(..., description="Filter value, e.g. FR, iOS")


class QueryLog(BaseModel):
    query_id: str = Field(..., description="Unique query execution identifier or Snowflake Query ID")
    session_id: str = Field(..., description="Data exploration session ID")
    sql_text: str = Field(..., description="Raw SQL query executed")
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    row_count: Optional[int] = Field(None, description="Rows returned")
    execution_time_ms: Optional[float] = Field(None, description="Query execution duration in milliseconds")
    associated_hypothesis_id: Optional[str] = Field(None, description="Hypothesis ID linked to this query")


class SearchContext(BaseModel):
    session_id: str = Field(..., description="Agent session ID")
    total_hypotheses_tested: int = Field(1, ge=1, description="Total hypotheses explored in this session")
    initially_significant: int = Field(0, ge=0, description="Hypotheses with raw p < 0.05")
    survived_correction: int = Field(0, ge=0, description="Hypotheses surviving multiplicity adjustment")
    dimensions_explored: List[str] = Field(default_factory=list, description="List of dimensions sliced")


class Hypothesis(BaseModel):
    hypothesis_id: str = Field(..., description="Unique identifier e.g. HYP-0001")
    session_id: str = Field(..., description="Data exploration session ID")
    claim_description: str = Field(..., description="Natural language claim made by agent")
    metric: MetricDefinition
    segments: List[SegmentFilter] = Field(default_factory=list)
    time_window: TimeWindow
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: HypothesisStatus = Field(default=HypothesisStatus.REGISTERED)
