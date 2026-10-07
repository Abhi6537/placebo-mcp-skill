---
name: placebo-audit
description: >
  Falsification and statistical audit protocol for CoCo AI data agents.
  Forces active registration of hypotheses, multiplicity tracking, and
  pre-reporting falsification stress testing on Snowflake queries.
---

# Placebo Statistical Audit Skill for CoCo Agents

## Overview
As an AI Data Agent exploring Snowflake databases, you possess the capacity to execute dozens of queries across multiple dimension splits in seconds. This speed introduces severe risk of **multiple testing, p-hacking, and false discoveries**.

This skill establishes your scientific protocol when analyzing metrics, causal events, and A/B test results.

---

## The 10 Invariant Skill Rules

1. **Pre-Register Hypotheses:** Before querying Snowflake for exploratory comparisons, call `placebo_register_hypothesis` with your target metric, time window, and dimension segments.
2. **Log All Executed SQL:** Ensure every query run against Snowflake is recorded with its `session_id`.
3. **No Uncorrected Significance Claims:** Never report $p < 0.05$ as a "discovery" without Benjamini-Hochberg adjustment reflecting all queries tested in the session.
4. **Mandatory Pre-Trend Verification:** Never claim an event or feature caused a change without verifying that the metric was flat in the pre-intervention period.
5. **Mandatory Placebo Date Checks:** Run in-time placebo tests at historical dates before the event to prove the effect does not spontaneously appear without treatment.
6. **Trigger the Audit Pipeline:** When you believe you have discovered a meaningful finding, call `placebo_audit_claim` before drafting your final answer to the user.
7. **Disclose Full Search Context:** Always disclose the denominator: *"Tested across 34 candidate slices, 3 initially looked significant, 1 survived correction."*
8. **Anti-Cherry-Picking:** If a feature had no effect overall, you are strictly forbidden from reporting a random sub-segment as a win without severe multiplicity penalty.
9. **Respect the Deterministic Verdict:** If Placebo returns `REFUTED` or `INCONCLUSIVE`, you must communicate that result to the user. You must never invent excuses or override the statistical verdict.
10. **Ground Final Output in the Evidence Package:** Embed the Placebo Audit ID and Investigation UI link in your response to the user.

---

## Tool API Reference

### 1. Register Hypothesis
**HTTP Endpoint:** `POST http://localhost:8000/api/v1/hypotheses`  
**Headers:** `Content-Type: application/json`

```json
{
  "hypothesis_id": "HYP-0001",
  "session_id": "sess_1234",
  "claim_description": "Checkout redesign boosted conversion rate in France",
  "metric": {
    "name": "conversion_rate",
    "column": "is_converted",
    "aggregation": "mean"
  },
  "segments": [
    {"dimension": "country", "operator": "=", "value": "FR"}
  ],
  "time_window": {
    "start": "2026-01-01",
    "end": "2026-03-31",
    "intervention_date": "2026-02-15"
  }
}
```

### 2. Audit Candidate Claim
**HTTP Endpoint:** `POST http://localhost:8000/api/v1/audit`  
**Headers:** `Content-Type: application/json`

```json
{
  "hypothesis_id": "HYP-0001",
  "table_name": "PROD_DB.ANALYTICS.ORDERS",
  "entity_column": "user_id",
  "date_column": "order_date",
  "metric_column": "is_converted",
  "intervention_date": "2026-02-15"
}
```
