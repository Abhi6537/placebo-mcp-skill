"""
Placebo MCP (Model Context Protocol) Server.
Exposes Placebo's statistical falsification engine as standardized MCP tools and resources for AI Agents (CoCo, Claude, Cursor).
"""

import os
from typing import Optional
from dotenv import load_dotenv

from mcp.server.mcpserver import MCPServer

from placebo.llm.client import PlaceboLLMClient
from placebo.models.hypothesis import (
    Hypothesis,
    MetricDefinition,
    SegmentFilter,
    TimeWindow,
)
from placebo.pipeline.runner import AuditPipeline
from placebo.snowflake.client import SnowflakeClient
from placebo.storage.sqlite import SQLiteStorage

load_dotenv()

# Initialize MCPServer
mcp = MCPServer(
    name="placebo-falsification",
    instructions=(
        "Placebo is an active falsification and statistical audit engine. "
        "Use placebo_register_hypothesis to track queries and prevent p-hacking. "
        "Use placebo_audit_claim to stress-test claims against Snowflake with pre-trend checks, "
        "placebo dates, and Benjamini-Hochberg multiplicity correction before reporting discoveries."
    )
)

storage = SQLiteStorage()
llm_client = PlaceboLLMClient()
pipeline = AuditPipeline(storage=storage, llm_explainer=llm_client)


@mcp.tool()
def placebo_register_hypothesis(
    hypothesis_id: str,
    session_id: str,
    claim_description: str,
    metric_name: str,
    metric_column: str,
    start_date: str,
    end_date: str,
    intervention_date: str,
    dimension: Optional[str] = None,
    dimension_value: Optional[str] = None
) -> str:
    """
    Pre-register a candidate hypothesis in the Placebo ledger to track search space burden.

    Args:
        hypothesis_id: Unique ID (e.g. HYP-0001)
        session_id: Agent session ID
        claim_description: The natural language hypothesis
        metric_name: Business name of the metric (e.g. temperature, revenue)
        metric_column: Underlying SQL column name
        start_date: Analysis window start date (YYYY-MM-DD)
        end_date: Analysis window end date (YYYY-MM-DD)
        intervention_date: Event / launch date (YYYY-MM-DD)
        dimension: Optional dimension filter column (e.g. city_name)
        dimension_value: Optional filter value (e.g. paris)
    """
    segments = []
    if dimension and dimension_value:
        segments.append(SegmentFilter(dimension=dimension, operator="=", value=dimension_value))

    hyp = Hypothesis(
        hypothesis_id=hypothesis_id,
        session_id=session_id,
        claim_description=claim_description,
        metric=MetricDefinition(name=metric_name, column=metric_column, aggregation="mean"),
        segments=segments,
        time_window=TimeWindow(
            start=start_date,
            end=end_date,
            intervention_date=intervention_date
        )
    )

    storage.save_hypothesis(hyp)
    return f"Successfully registered hypothesis {hypothesis_id} in session {session_id}."


@mcp.tool()
def placebo_audit_claim(
    hypothesis_id: str,
    table_name: Optional[str] = None,
    date_column: Optional[str] = None,
    metric_column: Optional[str] = None,
    entity_column: Optional[str] = None,
    dimension_filter: Optional[str] = None,
    dimension_value: Optional[str] = None
) -> str:
    """
    Execute active falsification stress tests on Snowflake for a candidate claim.
    Runs pre-trend tests, in-time placebo dates, and multiplicity correction.
    Produces a deterministic verdict (CONFIRMED, INCONCLUSIVE, REFUTED) and Gemma explanation.

    Args:
        hypothesis_id: The registered hypothesis ID to audit
        table_name: Snowflake table/view (defaults to SNOWFLAKE_TABLE in .env)
        date_column: Date/timestamp column (defaults to SNOWFLAKE_DATE_COL in .env)
        metric_column: Metric column (defaults to SNOWFLAKE_METRIC_COL in .env)
        entity_column: Entity/grouping column (defaults to SNOWFLAKE_ENTITY_COL in .env)
        dimension_filter: Optional column filter (e.g. CITY_NAME)
        dimension_value: Optional value filter (e.g. paris)
    """
    hyp = storage.get_hypothesis(hypothesis_id)
    if not hyp:
        return f"Error: Hypothesis {hypothesis_id} not found in ledger. Call placebo_register_hypothesis first."

    tbl = table_name or os.getenv("SNOWFLAKE_TABLE", "POINT_HISTORY_DAY")
    d_col = date_column or os.getenv("SNOWFLAKE_DATE_COL", "DATE_VALID_STD")
    m_col = metric_column or hyp.metric.column or os.getenv("SNOWFLAKE_METRIC_COL", "AVG_TEMPERATURE_AIR_2M_F")
    e_col = entity_column or os.getenv("SNOWFLAKE_ENTITY_COL", "CITY_NAME")

    # Connect to Snowflake and fetch series
    client = SnowflakeClient()
    try:
        client.connect()
        where_clause = ""
        dim = dimension_filter or (hyp.segments[0].dimension if hyp.segments else None)
        val = dimension_value or (hyp.segments[0].value if hyp.segments else None)
        if dim and val:
            where_clause = f"WHERE {dim} = '{val}'"

        sql = f"SELECT {e_col}, {d_col}, {m_col} FROM {tbl} {where_clause} ORDER BY {d_col} ASC;"
        df = client.query_to_dataframe(sql)
    except Exception as e:
        return f"Snowflake query execution failed: {e}"
    finally:
        client.close()

    if df.empty:
        return f"Error: Snowflake query returned 0 rows for table {tbl}."

    # Execute full Placebo Audit Pipeline
    package = pipeline.run_audit(
        hypothesis=hyp,
        df=df,
        entity_col=e_col,
        date_col=d_col,
        metric_col=m_col
    )

    falsifications_summary = []
    for f in package.falsification_results:
        falsifications_summary.append(f"• [{f.test_type.value}] {f.status.value}: {f.details}")

    explanation_text = package.explanation.headline if package.explanation else package.verdict.summary

    output = f"""=== PLACEBO FALSIFICATION AUDIT REPORT ===
Audit ID:    {package.audit_id}
Hypothesis:  {hyp.claim_description}
Verdict:     {package.verdict.grade.value} (Confidence: {package.verdict.confidence.value})

Statistical Results:
• Effect Size:      {package.statistical_result.effect_size}
• Raw p-value:      {package.statistical_result.raw_p_value}
• Adjusted p-value: {package.statistical_result.adjusted_p_value} (Benjamini-Hochberg)

Falsification Battery:
{chr(10).join(falsifications_summary)}

Gemma 4 Executive Narrative:
{explanation_text}

Recommendation:
{package.verdict.recommendation}
"""
    return output


@mcp.tool()
def placebo_get_evidence(audit_id: str) -> str:
    """Retrieve full immutable Evidence Package JSON by Audit ID."""
    pkg = storage.get_evidence_package(audit_id)
    if not pkg:
        return f"Audit ID {audit_id} not found."
    return pkg.model_dump_json(indent=2)


@mcp.resource("placebo://evidence/{audit_id}")
def get_evidence_resource(audit_id: str) -> str:
    """Read full Evidence Package JSON as an MCP Resource."""
    pkg = storage.get_evidence_package(audit_id)
    if not pkg:
        return f'{{"error": "Evidence Package {audit_id} not found"}}'
    return pkg.model_dump_json(indent=2)


@mcp.prompt()
def scientific_auditor() -> str:
    """System prompt persona for AI data agents following Placebo scientific rules."""
    return (
        "You are an AI data analyst equipped with the Placebo falsification engine. "
        "Before querying data, register your hypotheses. "
        "Before reporting any significant finding, call placebo_audit_claim. "
        "Respect all falsification verdicts and never invent statistical numbers."
    )


def main():
    """Run MCP server over standard I/O (stdio)."""
    mcp.run()


if __name__ == "__main__":
    main()
