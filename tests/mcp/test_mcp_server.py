"""
Unit tests for Placebo MCP Server.
"""

import pytest
import asyncio
from placebo.mcp.server import mcp, storage


def test_mcp_tools_registered():
    """Verify all required Placebo MCP tools are registered."""
    tools = asyncio.run(mcp.list_tools())
    tool_names = [t.name for t in tools]
    assert "placebo_register_hypothesis" in tool_names
    assert "placebo_audit_claim" in tool_names
    assert "placebo_get_evidence" in tool_names


def test_mcp_register_hypothesis():
    """Verify hypothesis registration tool stores hypothesis in ledger."""
    res = asyncio.run(mcp.call_tool(
        "placebo_register_hypothesis",
        {
            "hypothesis_id": "TEST-MCP-HYP",
            "session_id": "TEST-SESSION",
            "claim_description": "MCP Test Claim",
            "metric_name": "temperature",
            "metric_column": "temp_col",
            "start_date": "2026-01-01",
            "end_date": "2026-06-01",
            "intervention_date": "2026-03-01",
            "dimension": "city",
            "dimension_value": "paris",
        }
    ))
    assert "Successfully registered hypothesis TEST-MCP-HYP" in res.content[0].text
    saved = storage.get_hypothesis("TEST-MCP-HYP")
    assert saved is not None
    assert saved.claim_description == "MCP Test Claim"
