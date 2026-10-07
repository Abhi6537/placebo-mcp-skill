"""
Protocol defining falsification engine boundaries.
"""

from typing import List, Protocol, runtime_checkable
import pandas as pd
from placebo.models.falsification import FalsificationResult
from placebo.models.hypothesis import Hypothesis


@runtime_checkable
class FalsificationEngine(Protocol):
    """Protocol for executing active falsification batteries on data."""

    def run_battery(
        self,
        hypothesis: Hypothesis,
        time_series_data: pd.DataFrame,
        entity_col: str,
        date_col: str,
        metric_col: str
    ) -> List[FalsificationResult]:
        """Execute active falsification tests and return individual results."""
        ...
