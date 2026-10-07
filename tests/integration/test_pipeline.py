"""
End-to-end integration test for Placebo pipeline.
Tests Hypothesis -> AuditPipeline -> Falsification Battery -> Verdict -> Sealed Evidence Package.
"""

import os
import numpy as np
import pandas as pd
import pytest

from placebo.models.hypothesis import Hypothesis, MetricDefinition, TimeWindow
from placebo.models.verdict import VerdictGrade
from placebo.pipeline.runner import AuditPipeline
from placebo.storage.sqlite import SQLiteStorage


def test_full_pipeline_confirmed_scenario(tmp_path):
    """Test a clean treatment effect scenario that correctly confirms."""
    db_file = str(tmp_path / "test_ledger.db")
    storage = SQLiteStorage(db_path=db_file)
    pipeline = AuditPipeline(storage=storage)

    # Generate synthetic clean experiment: 30 days pre, 15 days post
    np.random.seed(42)
    pre_dates = pd.date_range("2026-01-01", "2026-01-30", freq="D")
    post_dates = pd.date_range("2026-01-31", "2026-02-14", freq="D")

    rows = []
    # Pre-period: mean 10.0
    for d in pre_dates:
        for u in range(1, 20):
            rows.append({
                "event_date": d,
                "user_id": f"user_{u}",
                "conversion_rate": float(np.random.normal(10.0, 1.0))
            })
    # Post-period: mean 15.0 (+5.0 lift, clean jump)
    for d in post_dates:
        for u in range(1, 20):
            rows.append({
                "event_date": d,
                "user_id": f"user_{u}",
                "conversion_rate": float(np.random.normal(15.0, 1.0))
            })

    df = pd.DataFrame(rows)

    hyp = Hypothesis(
        hypothesis_id="HYP-INT-001",
        session_id="test_session",
        claim_description="Feature launch increased conversion rate",
        metric=MetricDefinition(name="conversion_rate", column="conversion_rate"),
        time_window=TimeWindow(
            start="2026-01-01",
            end="2026-02-14",
            intervention_date="2026-01-31"
        )
    )

    storage.save_hypothesis(hyp)

    package = pipeline.run_audit(
        hypothesis=hyp,
        df=df,
        entity_col="user_id",
        date_col="event_date",
        metric_col="conversion_rate"
    )

    assert package.schema_version == "1.0"
    assert package.audit_id.startswith("AUDIT-")
    assert package.verdict.grade == VerdictGrade.CONFIRMED
    assert package.statistical_result.effect_size > 4.0
    assert len(package.falsification_results) >= 2

    # Verify persisted in SQLite
    retrieved = storage.get_evidence_package(package.audit_id)
    assert retrieved is not None
    assert retrieved.audit_id == package.audit_id
    assert retrieved.verdict.grade == VerdictGrade.CONFIRMED
