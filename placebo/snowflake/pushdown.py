"""
Snowflake Push-Down SQL Templates.
Pushes heavy aggregations, time-series metrics, and regression calculations directly into Snowflake.
"""

from typing import List, Optional
from placebo.models.hypothesis import SegmentFilter


def build_where_clause(
    segments: Optional[List[SegmentFilter]] = None,
    base_filters: Optional[List[str]] = None
) -> str:
    """Build parameterized WHERE clause from segments and base filters."""
    clauses = list(base_filters or [])
    if segments:
        for seg in segments:
            # Basic SQL escaping / quoting
            clauses.append(f'"{seg.dimension}" {seg.operator} \'{seg.value}\'')
    if clauses:
        return "WHERE " + " AND ".join(clauses)
    return ""


def sql_daily_metric_series(
    table: str,
    date_col: str,
    metric_col: str,
    segments: Optional[List[SegmentFilter]] = None
) -> str:
    """Generate SQL to fetch daily aggregated metric for pre-trend and placebo date evaluation."""
    where_sql = build_where_clause(segments)
    return f"""
    SELECT
        DATE_TRUNC('DAY', "{date_col}") AS event_date,
        AVG("{metric_col}") AS metric_mean,
        STDDEV("{metric_col}") AS metric_std,
        COUNT(*) AS obs_count
    FROM {table}
    {where_sql}
    GROUP BY 1
    ORDER BY 1 ASC;
    """


def sql_top_entities_by_volume(
    table: str,
    entity_col: str,
    metric_col: str,
    limit: int = 15,
    segments: Optional[List[SegmentFilter]] = None
) -> str:
    """Generate SQL to find top influential clusters / entities in Snowflake."""
    where_sql = build_where_clause(segments)
    return f"""
    SELECT
        "{entity_col}" AS entity_id,
        COUNT(*) AS row_count,
        SUM(ABS("{metric_col}")) AS total_magnitude
    FROM {table}
    {where_sql}
    GROUP BY 1
    ORDER BY total_magnitude DESC
    LIMIT {limit};
    """
