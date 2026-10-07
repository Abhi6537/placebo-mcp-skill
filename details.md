# Placebo — The Falsification Layer for AI Data Agents

> **When an AI finds a pattern, Placebo tries to break it before you believe it.**

**Primary Hackathon Track:** Best Open-Source AI Project with Snowflake  
**Secondary Fit:** Best Open-Source AI Project  
**Possible AI Model:** Gemma 4 / another open-weight model  
**Primary Platform:** Snowflake + Cortex Code (CoCo)  
**Project Type:** Open-source statistical audit layer + CoCo Agent Skill + investigation UI

---

# 1. Executive Summary

Placebo is an open-source **falsification and statistical-audit layer for AI-driven data analysis**.

Modern AI data agents can explore large datasets extremely quickly. They can generate SQL, test many hypotheses, compare many segments, search different time windows, and repeatedly modify an analysis until they find something that looks interesting.

That creates a problem:

> An AI agent can accidentally discover a statistically interesting result simply because it searched many possible explanations.

This is closely related to **multiple testing, p-hacking, researcher degrees of freedom, selection bias, and post-hoc hypothesis generation**.

Placebo does not stop an AI agent from exploring.

Instead, it makes the exploration **auditable** and subjects promising findings to deliberate attempts at falsification.

The system:

1. Registers hypotheses before analysis.
2. Records every hypothesis and analysis attempt.
3. Records executed SQL and Snowflake query IDs.
4. Counts the search space.
5. Applies appropriate multiple-testing corrections.
6. Runs time-series-aware falsification tests.
7. Tests fake intervention dates.
8. Checks pre-trends.
9. Tests negative-control outcomes where appropriate.
10. Tests robustness to reasonable analytical choices.
11. Produces a structured evidence package.
12. Uses an open-weight model such as Gemma to explain the evidence.
13. Never asks the LLM to invent statistical evidence.
14. Clearly separates **observed result**, **statistical evidence**, **falsification evidence**, and **interpretation**.

The central principle is:

> **The AI searches for patterns. Placebo searches for reasons not to trust those patterns.**

---

# 2. The Problem

## 2.1 The old data-analysis workflow

A human analyst traditionally:

```text
Question
  ↓
Hypothesis
  ↓
Analysis
  ↓
Result
  ↓
Interpretation
```

The number of analyses a human can manually run is limited.

---

## 2.2 The AI-agent workflow

An AI data agent changes the scale:

```text
Question
  ↓
AI explores data
  ↓
Query 1
Query 2
Query 3
Query 4
...
Query 100
...
Query 500
  ↓
Interesting result
  ↓
Report
```

The agent may honestly find the result.

The problem is that the user may not know:

- how many hypotheses were tested,
- how many alternative windows were tried,
- how many segments were searched,
- how many metrics were examined,
- which results were discarded,
- whether the reported result was selected because it looked best,
- whether similar results appear at fake dates,
- whether the trend already existed before the supposed event.

---

# 3. Simple Explanation of the Statistical Problem

Suppose an AI tests 100 unrelated hypotheses.

If it uses a threshold of:

```text
p < 0.05
```

then, under a simple null model where none of the hypotheses is actually associated, you can expect some apparently significant results by chance.

A simplified intuition is:

```text
1 test
    ↓
5% false-positive threshold

100 tests
    ↓
many opportunities for an apparently significant result
```

This does **not** mean exactly 5 false positives will always occur. The actual behavior depends on dependence between tests, the null distribution, effect sizes, and other assumptions.

The important point is:

> **The probability of seeing at least one apparently interesting result increases when you search many times.**

Placebo therefore records the search process instead of pretending that only the final selected hypothesis existed.

---

# 4. Example

A user asks:

> "Find what caused the Q3 sales increase."

CoCo explores:

```text
H1: Promotion X caused the increase
H2: Region A caused the increase
H3: Weather caused the increase
H4: Product category Y caused the increase
H5: Weekend traffic caused the increase
...
H47: Promotion X in Region A caused the increase
```

Suppose H47 produces:

```text
Effect = +21%
Raw p-value = 0.012
```

A normal system might report:

> Promotion X in Region A significantly increased sales.

Placebo instead records:

```text
47 hypotheses tested
8 initially significant
2 survive selected multiple-testing correction
1 survives falsification tests
```

It then checks:

- fake intervention dates,
- pre-trends,
- negative-control outcomes,
- time-series robustness,
- alternative specifications where appropriate.

If the result fails these checks, Placebo may return:

> **Insufficient evidence**

rather than presenting the original result as established fact.

---

# 5. Product Definition

## 5.1 One-line definition

> **Placebo is a falsification layer that audits AI-generated data findings before they are reported as trustworthy insights.**

## 5.2 What Placebo is

- Statistical audit infrastructure.
- AI-agent instrumentation.
- Hypothesis ledger.
- Falsification engine.
- Evidence generator.
- Open-source CoCo skill.
- Evidence-grounded AI explanation layer.

## 5.3 What Placebo is NOT

Placebo is not:

- a general-purpose BI dashboard,
- a replacement for Snowflake,
- a replacement for CoCo,
- a generic LLM evaluator,
- a generic p-value calculator,
- a causal-inference oracle,
- a system that proves causality automatically,
- a system that guarantees a finding is true,
- an AI that decides statistical significance by itself.

---

# 6. Core Product Philosophy

## Principle 1 — Record the search

Do not only save the final result.

Save:

```text
Hypothesis
↓
Analysis
↓
Query
↓
Result
↓
Decision
```

---

## Principle 2 — Statistics are deterministic

The LLM should not calculate:

- p-values,
- confidence intervals,
- effect sizes,
- corrected p-values,
- test statistics.

Those should be calculated by trusted statistical libraries and deterministic code.

---

## Principle 3 — The LLM explains evidence

The open-weight model receives a structured evidence package and explains it.

It must not create new evidence.

---

## Principle 4 — Falsification comes before confidence

The question is not:

> "Can we make this finding look significant?"

The question is:

> "What would make this finding look less convincing?"

---

## Principle 5 — Never claim more than the evidence supports

Placebo should use language such as:

- "consistent with",
- "insufficient evidence",
- "evidence is weakened by",
- "robust to tested placebo dates",
- "finding did not survive correction",
- "possible alternative explanation".

Avoid:

- "proved",
- "caused" unless a valid causal design supports that claim,
- "guaranteed",
- "certain",
- "scientifically proven".

---

# 7. Primary Track

## Best Open-Source AI Project with Snowflake

This is the strongest track.

The project naturally combines all required components.

### Required element 1 — Snowflake CoCo

CoCo acts as the AI data-analysis agent.

Example:

```text
User:
"Find unusual changes in monthly sales after promotions."
```

CoCo investigates the Snowflake data.

---

### Required element 2 — Freely accessible Snowflake dataset

Use a public/free Snowflake dataset suitable for temporal analysis.

The final implementation should document:

- dataset name,
- source,
- Snowflake listing/location,
- access terms,
- tables used,
- columns used,
- time range,
- known limitations.

The exact dataset should be confirmed against the current Snowflake Marketplace/sample-data availability before final submission.

---

### Required element 3 — Open-source/open-weight AI

Use Gemma or another eligible open-weight model.

Gemma's role:

- evidence summarization,
- alternative explanation generation,
- natural-language verdict,
- analyst-facing explanation.

It should not replace the deterministic statistical engine.

---

# 8. Secondary Track

## Best Open-Source AI Project

Placebo can also be submitted as:

> **An open-source statistical-falsification skill and library for AI data agents.**

Open-source deliverables:

```text
placebo/
├── core/
├── statistical/
├── time_series/
├── instrumentation/
├── integrations/
├── gemma/
├── skill/
├── cli/
├── tests/
└── docs/
```

Possible artifact:

```text
placebo-snowflake-skill/
└── SKILL.md
```

---

# 9. Why Not the Cybersecurity Track?

The core problem is not cybersecurity.

Do not force Placebo into cybersecurity simply to fit another sponsor.

The strongest and most natural fit is Snowflake.

---

# 10. Why Not Primarily the Gemma Track?

Gemma is useful, but Placebo does not inherently need multimodal input.

Gemma is an important component because it provides evidence-grounded explanation, but the main technical novelty is the **falsification system**.

Therefore:

```text
Primary:
Snowflake + CoCo

AI:
Gemma

Core innovation:
Falsification
```

---

# 11. Main User Personas

## Persona 1 — Data Analyst

Wants to know:

> "Is this pattern actually trustworthy?"

---

## Persona 2 — Data Scientist

Wants:

- experiment history,
- multiple-testing correction,
- robustness checks,
- reproducibility.

---

## Persona 3 — Researcher

Wants:

- preregistered hypotheses,
- audit trails,
- falsification,
- alternative explanations.

---

## Persona 4 — AI Data-Agent Developer

Wants:

> "I don't want my agent to report a cherry-picked result."

---

## Persona 5 — Business Decision Maker

Wants:

> "Can I safely make a decision from this AI-generated insight?"

---

# 12. End-to-End User Flow

## Step 1 — Connect data

User connects a Snowflake database/schema.

---

## Step 2 — Ask a natural-language question

Example:

> "Find what explains the sales spike in Q3."

---

## Step 3 — CoCo starts analysis

CoCo explores the data.

Placebo intercepts/records the analysis workflow.

---

## Step 4 — Register hypothesis

Before the analysis is executed, Placebo creates:

```text
Hypothesis ID:
HYP-0042

Statement:
"Campaign X increased sales."

Outcome:
daily_sales

Treatment:
campaign_x

Time window:
2026-01-01 → 2026-09-30
```

---

## Step 5 — Execute analysis

CoCo executes SQL.

Placebo records:

- SQL,
- timestamp,
- query ID,
- hypothesis ID,
- dataset,
- result.

---

## Step 6 — Discover additional hypotheses

Every additional hypothesis gets its own record.

Example:

```text
HYP-0042
HYP-0043
HYP-0044
...
HYP-0088
```

---

## Step 7 — Candidate finding

Suppose HYP-0042 looks interesting.

Placebo marks:

```text
CANDIDATE_FINDING
```

It does not immediately report it as trustworthy.

---

## Step 8 — Multiple-testing correction

Placebo considers the relevant family of tests and applies an appropriate correction.

Possible methods:

- Bonferroni
- Holm
- Benjamini-Hochberg/FDR

The exact method should depend on the analysis goal.

Do not blindly apply one correction to every possible analysis.

---

## Step 9 — Falsification

Placebo selects applicable tests.

Examples:

```text
Fake intervention dates
Pre-trend check
Negative-control outcome
Time-series block permutation
Circular shift
Alternative window
```

Not every test is appropriate for every dataset.

---

## Step 10 — Verdict

Possible verdicts:

```text
ROBUST TO TESTED CHECKS
WEAK EVIDENCE
FALSIFICATION FAILED
INSUFFICIENT EVIDENCE
INCONCLUSIVE
```

---

## Step 11 — Evidence package

Create a machine-readable package:

```json
{
  "hypothesis": "...",
  "observed_effect": 0.21,
  "raw_p_value": 0.012,
  "adjusted_p_value": 0.31,
  "hypotheses_tested": 47,
  "pretrend_detected": true,
  "placebo_tests_passed": 1,
  "placebo_tests_failed": 4
}
```

---

## Step 12 — Gemma explanation

Gemma receives only the evidence package.

It generates a concise explanation.

---

## Step 13 — User sees final result

The UI shows:

```text
Finding:
Campaign X and increased sales

Verdict:
INSUFFICIENT EVIDENCE

Why:
• 47 hypotheses were tested.
• The initial p-value did not survive the selected correction.
• Similar effects appeared at placebo dates.
• Sales were already increasing before the campaign.
```

---

# 13. Core Modules

## Module 1 — Hypothesis Ledger

Purpose:

> Record every hypothesis the AI investigates.

Responsibilities:

- create hypothesis ID,
- store hypothesis text,
- store variables,
- store time range,
- store dataset,
- timestamp creation,
- track status.

Statuses:

```text
REGISTERED
RUNNING
CANDIDATE
FALSIFYING
PASSED
FAILED
INCONCLUSIVE
REPORTED
```

---

# 14. Module 2 — Query Tracker

Records executed queries.

Fields:

```text
placebo_query_id
hypothesis_id
snowflake_query_id
sql
timestamp
status
duration
warehouse
database
schema
```

The Snowflake query ID should be retained as the external reference.

---

# 15. Module 3 — Analysis Registry

Stores what statistical operation was performed.

Example:

```text
test_type:
difference_in_means

outcome:
sales

treatment:
campaign

population:
all stores

window:
30 days

effect:
+21%

raw_p:
0.012
```

---

# 16. Module 4 — Multiple-Testing Engine

Purpose:

> Account for the fact that many analyses were attempted.

Potential methods:

### Bonferroni

Very conservative.

Conceptually:

```text
adjusted threshold = alpha / number_of_tests
```

---

### Holm

Step-down family-wise error control.

---

### Benjamini-Hochberg

Controls false discovery rate and can be more appropriate when screening many candidate findings.

---

## Important implementation rule

Do not claim:

> "Benjamini-Hochberg solves p-hacking."

It does not.

It addresses one part of the multiple-testing problem.

---

# 17. Module 5 — Time-Series Falsification Engine

This is a major differentiator.

Time-series data cannot always be randomly shuffled because observations often have:

- temporal dependence,
- seasonality,
- trend,
- autocorrelation.

Therefore Placebo should offer time-aware falsification tests.

---

# 18. Falsification Test A — Fake Intervention Date

Suppose:

```text
Real event:
June 15
```

Placebo tests:

```text
May 15
May 29
June 01
June 08
June 22
June 29
```

The exact placebo dates must follow rules that avoid invalid leakage and should be documented.

If many fake dates produce similar effects:

```text
SUSPICIOUS
```

---

# 19. Falsification Test B — Pre-Trend

If an event supposedly caused a change:

```text
Before event:
No effect expected

After event:
Effect expected
```

If the same trend existed before the event:

```text
Possible alternative explanation
```

This does not automatically disprove an effect, but it weakens simple before/after causal interpretation.

---

# 20. Falsification Test C — Negative Control

Choose an outcome that should not plausibly be affected by the treatment.

Example:

```text
Campaign X
      ↓
Expected:
sales ↑

Negative control:
unrelated operational metric
```

If the same effect appears in the unrelated outcome, the result may be driven by a common trend or confounder.

Negative controls require domain knowledge. Placebo should not invent arbitrary negative controls and call them valid.

---

# 21. Falsification Test D — Block Permutation

For time-series data, preserve local temporal structure by permuting blocks rather than individual rows.

Example:

```text
Week 1
Week 2
Week 3
Week 4
```

may be treated as blocks rather than randomly shuffling individual days.

The exact implementation should depend on the time scale and dependence structure.

---

# 22. Falsification Test E — Circular Shift

For compatible time-series analyses:

```text
Series A:
A A A A A A

Series B:
B B B B B B
```

Shift one series relative to the other while preserving its internal structure.

If strong relationships appear under many shifts:

```text
Observed relationship becomes less convincing.
```

This test must be used carefully because it assumes the shift preserves an appropriate null structure.

---

# 23. Falsification Test F — Alternative Time Window

Original:

```text
30 days after event
```

Test:

```text
7 days
14 days
30 days
60 days
90 days
```

If the effect only appears under one unusually convenient window:

```text
Potential specification sensitivity
```

This should be counted as researcher/agent degrees of freedom when relevant.

---

# 24. Module 6 — Robustness Engine

Tests whether a finding changes substantially under reasonable analytical choices.

Possible dimensions:

```text
Time window
Population
Outlier handling
Aggregation level
Model specification
Control variables
```

Important:

> Do not automatically search thousands of specifications and then report the best one.

The purpose of the robustness engine is to **expose sensitivity**, not create another p-hacking machine.

---

# 25. Module 7 — Alternative Explanation Generator

Gemma can suggest alternative explanations.

Example:

Finding:

> Sales increased after Campaign X.

Gemma may produce:

```text
Possible alternatives supported by supplied evidence:

1. Existing upward sales trend.
2. Holiday effect.
3. Concurrent discount campaign.
4. Region-specific seasonal change.
```

It must only use variables/evidence provided in the evidence package.

---

# 26. Module 8 — Verdict Engine

The verdict engine is deterministic.

It should not simply ask Gemma:

> "Is this significant?"

Instead it combines structured evidence.

Example:

```text
Raw result:
positive

Multiple-testing:
failed

Pre-trend:
failed

Placebo dates:
failed

Negative control:
passed

Final:
WEAK / INSUFFICIENT EVIDENCE
```

The exact decision policy must be transparent and documented.

---

# 27. Module 9 — Gemma Explanation Layer

Gemma gets:

```text
Evidence package
```

not the raw warehouse.

This reduces hallucination risk and keeps the model's role constrained.

---

# 28. Gemma Prompt Contract

Conceptual system instruction:

```text
You are the explanation layer for Placebo.

You may only use facts present in the supplied evidence package.

Do not calculate statistics.

Do not invent evidence.

Do not introduce external facts.

Do not claim causality unless the evidence package explicitly supports the applicable design.

Explain:
1. What was tested.
2. What was observed.
3. What falsification checks were performed.
4. What failed or passed.
5. What alternative explanations remain.
6. What conclusion is justified.

If evidence is insufficient, say so.
```

---

# 29. Architecture

```text
                         USER
                           |
                           v
                    +-------------+
                    |    CoCo     |
                    | AI Analyst  |
                    +------+------+
                           |
                           v
                    +-------------+
                    | Placebo     |
                    | Skill       |
                    +------+------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
     +---------------+          +----------------+
     | Hypothesis    |          | Snowflake      |
     | Ledger        |          | Warehouse      |
     +-------+-------+          +--------+-------+
             |                           |
             |                           v
             |                    Query History
             |                           |
             +-------------+-------------+
                           |
                           v
                  +-------------------+
                  | Analysis Registry |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  | Statistical      |
                  | Engine            |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  | Falsification     |
                  | Engine            |
                  +---------+---------+
                            |
                 +----------+----------+
                 |          |          |
                 v          v          v
             Pretrend   Placebo    Negative
                        Dates      Controls
                 |          |          |
                 +----------+----------+
                            |
                            v
                  +-------------------+
                  | Verdict Engine    |
                  +---------+---------+
                            |
                            v
                  +-------------------+
                  | Evidence Package  |
                  +---------+---------+
                            |
                            v
                      +-----------+
                      |   Gemma   |
                      +-----+-----+
                            |
                            v
                  +-------------------+
                  | Investigation UI  |
                  +-------------------+
```

---

# 30. High-Level Technology Stack

## Data

- Snowflake
- Snowflake public/free dataset
- Snowflake Query History

## AI Agent

- Snowflake Cortex Code / CoCo
- Custom CoCo Skill

## Open-weight model

- Gemma 4 or another eligible open-weight model

## Statistical engine

- Python
- NumPy
- SciPy
- statsmodels
- pandas or Polars
- scikit-learn where appropriate

## Backend

- FastAPI
- Python

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- Recharts
- React Flow if an investigation graph is required

## Storage

Primary:

- Snowflake tables for experiment/audit data

Optional local development:

- SQLite

## Testing

- pytest
- synthetic datasets
- deterministic fixtures
- statistical validation tests

## Packaging

- Python package
- CLI
- CoCo Skill
- Docker optional

---

# 31. Recommended Repository Structure

```text
placebo/
│
├── README.md
├── LICENSE
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── statistics.md
│   ├── falsification.md
│   ├── snowflake.md
│   ├── coco.md
│   ├── gemma.md
│   └── limitations.md
│
├── placebo/
│   ├── __init__.py
│   │
│   ├── ledger/
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── service.py
│   │
│   ├── snowflake/
│   │   ├── client.py
│   │   ├── query_history.py
│   │   └── mapper.py
│   │
│   ├── statistics/
│   │   ├── multiple_testing.py
│   │   ├── effects.py
│   │   ├── confidence.py
│   │   └── assumptions.py
│   │
│   ├── timeseries/
│   │   ├── placebo_dates.py
│   │   ├── pretrend.py
│   │   ├── block_permutation.py
│   │   ├── circular_shift.py
│   │   └── robustness.py
│   │
│   ├── falsification/
│   │   ├── engine.py
│   │   ├── negative_controls.py
│   │   └── verdict.py
│   │
│   ├── evidence/
│   │   ├── builder.py
│   │   ├── schema.py
│   │   └── validator.py
│   │
│   ├── gemma/
│   │   ├── client.py
│   │   ├── prompts.py
│   │   └── guardrails.py
│   │
│   └── cli/
│       └── main.py
│
├── skill/
│   └── placebo-audit/
│       └── SKILL.md
│
├── tests/
│   ├── unit/
│   ├── statistical/
│   ├── timeseries/
│   ├── integration/
│   └── fixtures/
│
└── web/
    ├── app/
    ├── components/
    ├── lib/
    └── types/
```

---

# 32. Hypothesis Data Model

Example:

```json
{
  "id": "HYP-0042",
  "experiment_id": "EXP-001",
  "statement": "Campaign X increased daily sales",
  "outcome": "daily_sales",
  "treatment": "campaign_x",
  "population": "all_stores",
  "start_date": "2026-01-01",
  "end_date": "2026-09-30",
  "created_at": "2026-10-07T12:00:00Z",
  "status": "CANDIDATE"
}
```

---

# 33. Query Data Model

```json
{
  "id": "Q-9001",
  "hypothesis_id": "HYP-0042",
  "snowflake_query_id": "01abc...",
  "sql_hash": "sha256...",
  "query_text": "...",
  "status": "SUCCESS",
  "started_at": "...",
  "finished_at": "..."
}
```

Potentially store the full SQL depending on privacy/security requirements.

---

# 34. Statistical Result Data Model

```json
{
  "hypothesis_id": "HYP-0042",
  "effect_size": 0.21,
  "standard_error": 0.04,
  "raw_p_value": 0.012,
  "adjustment_method": "BH",
  "adjusted_p_value": 0.31,
  "confidence_interval": [0.04, 0.38],
  "sample_size": 12000
}
```

The actual statistical fields depend on the test.

---

# 35. Falsification Result Data Model

```json
{
  "hypothesis_id": "HYP-0042",
  "tests": [
    {
      "type": "placebo_date",
      "status": "FAILED",
      "details": "Similar effect found at 4 placebo dates"
    },
    {
      "type": "pretrend",
      "status": "FAILED",
      "details": "Positive trend detected before treatment"
    },
    {
      "type": "negative_control",
      "status": "PASSED"
    }
  ]
}
```

---

# 36. Verdict Schema

Example:

```json
{
  "hypothesis_id": "HYP-0042",
  "verdict": "INSUFFICIENT_EVIDENCE",
  "reasons": [
    "Multiple-testing adjustment weakened the result",
    "Placebo-date tests produced similar effects",
    "Pre-treatment trend was detected"
  ],
  "confidence": "LOW"
}
```

Do not let the model invent this verdict.

---

# 37. API Design

## POST `/experiments`

Create an experiment.

---

## POST `/hypotheses`

Register a hypothesis.

---

## POST `/queries`

Record a query.

---

## GET `/experiments/{id}`

Return experiment details.

---

## GET `/experiments/{id}/hypotheses`

Return all hypotheses.

---

## POST `/hypotheses/{id}/audit`

Run the falsification pipeline.

---

## GET `/hypotheses/{id}/verdict`

Return the structured verdict.

---

## POST `/hypotheses/{id}/explain`

Generate Gemma explanation from the evidence package.

---

# 38. CLI

Potential interface:

```bash
placebo init
```

Initialize a project.

```bash
placebo hypothesis register \
  --statement "Campaign X increased sales"
```

Register a hypothesis.

```bash
placebo audit HYP-0042
```

Run falsification.

```bash
placebo explain HYP-0042
```

Generate evidence-grounded explanation.

```bash
placebo report EXP-001
```

Generate the full report.

---

# 39. CoCo Skill

The skill should enforce an analysis protocol.

Conceptual flow:

```text
User asks analytical question
        ↓
Identify candidate hypothesis
        ↓
REGISTER hypothesis
        ↓
Run analysis
        ↓
Record Snowflake query ID
        ↓
If additional hypothesis:
REGISTER again
        ↓
Never silently discard analysis
        ↓
Candidate finding
        ↓
Invoke Placebo audit
        ↓
Return verdict
```

---

# 40. Skill Rules

The skill should tell CoCo:

```text
RULE 1
Every testable hypothesis must be registered.

RULE 2
Do not report only the best result.

RULE 3
Record all materially different tested specifications.

RULE 4
Record Snowflake query IDs.

RULE 5
Do not claim causality from correlation alone.

RULE 6
Use time-series-aware falsification for temporal data.

RULE 7
Do not fabricate negative controls.

RULE 8
Do not use a placebo test when its assumptions are invalid.

RULE 9
Provide a structured evidence package.

RULE 10
The final language model explanation may only use that evidence package.
```

---

# 41. Query History Integration

Snowflake Query History is useful as an external audit source.

It can provide information about executed SQL and query metadata.

Use it to:

- verify execution,
- obtain query IDs,
- obtain timestamps,
- retrieve query text where permitted,
- cross-check Placebo's internal ledger.

Important limitation:

> Query History does not represent every internal thought or unexecuted hypothesis of an AI agent.

Therefore:

```text
Placebo Hypothesis Ledger
+
Snowflake Query History
```

must be used together.

---

# 42. Audit Matching

Placebo can compare:

```text
Internal record:
HYP-0042
    ↓
Query IDs:
Q1, Q2, Q3

Snowflake:
Q1 exists
Q2 exists
Q3 exists
```

Then:

```text
Audit Integrity:
PASS
```

If a query exists in Snowflake but is not associated with a hypothesis:

```text
UNACCOUNTED ANALYSIS
```

This is an important feature.

---

# 43. Unaccounted Analysis

Suppose the user runs:

```sql
SELECT ...
```

outside Placebo.

Snowflake Query History sees it.

Placebo cannot automatically assume it was part of CoCo's analysis.

Instead, the system can mark:

```text
UNASSOCIATED QUERY
```

and optionally allow the user to attach it to an experiment.

Do not falsely claim that every Snowflake query is generated by CoCo.

---

# 44. Privacy and Security

This project may inspect sensitive analytical data.

Therefore:

- never send raw warehouse data to Gemma unnecessarily,
- send aggregated/statistical evidence to the model,
- avoid including PII in prompts,
- redact secrets,
- never log credentials,
- use environment variables for Snowflake credentials,
- use least-privilege Snowflake roles,
- separate query execution permissions from metadata permissions where practical.

---

# 45. Gemma Data Boundary

Preferred:

```text
Snowflake raw data
       ↓
Statistical engine
       ↓
Aggregated evidence
       ↓
Gemma
```

Avoid:

```text
Snowflake raw customer data
       ↓
Gemma
```

unless explicitly necessary and properly authorized.

---

# 46. Evidence Contract

Gemma should receive:

```text
Hypothesis
Observed effect
Sample size
Statistical test
Raw p-value
Adjusted p-value
Confidence interval
Tests attempted
Tests passed
Tests failed
Alternative evidence
Limitations
```

Gemma should NOT receive arbitrary hidden application state and be asked to infer the conclusion.

---

# 47. Failure Handling

If there is not enough data:

```text
INSUFFICIENT_DATA
```

If assumptions are violated:

```text
TEST_NOT_APPLICABLE
```

If statistical results conflict:

```text
INCONCLUSIVE
```

If placebo test fails:

```text
FALSIFICATION_WARNING
```

If no hypothesis survives:

```text
NO_ROBUST_FINDING
```

This is better than forcing every run to produce an insight.

---

# 48. Important Statistical Limitations

Placebo is not magic.

It cannot prove that a hypothesis is true.

It cannot eliminate all confounding.

It cannot guarantee causal identification.

It cannot detect every form of p-hacking.

It cannot automatically know which negative control is scientifically valid.

It cannot automatically determine the correct causal design for every problem.

It should therefore describe itself as:

> **A falsification and audit layer, not a causal-proof engine.**

---

# 49. Important Time-Series Limitations

Time-series methods have assumptions.

Before using:

- block permutation,
- circular shifts,
- fake dates,
- pre-trend checks,

the system should inspect:

- sampling frequency,
- seasonality,
- missing values,
- autocorrelation,
- treatment timing,
- number of events,
- available pre-period,
- available post-period.

If a test is not appropriate:

```text
NOT APPLICABLE
```

is better than a fake result.

---







# 55. Novelty Positioning

Do not claim:

> "Nobody has ever built statistical falsification."

That would be incorrect.

Existing work includes:

- econometric specification auditing,
- notebook statistical linting,
- LLM p-hacking research,
- preregistration approaches,
- causal inference tooling,
- multiple-testing libraries.

The differentiation is:

> **Placebo operationalizes falsification as a first-class middleware layer around an AI data agent and maintains an auditable hypothesis ledger across warehouse exploration.**

---

# 56. Research Foundation

The 2026 paper:

> **Mitigating LLM-based p-Hacking by Preregistering for the Next LLM**

motivates the broader concern that LLM-driven research can create new p-hacking opportunities and explores preregistration as a mitigation. Use this as motivation, not as proof that Placebo's exact system is novel.

Reference:

https://arxiv.org/abs/2606.27687

Snowflake documentation should be used to verify:

- CoCo capabilities,
- custom skills,
- query history,
- current public datasets.

Do not make unsupported claims about CoCo's internal reasoning.

---

# 57. MVP Scope

Do not try to build every statistical test.

The first version should implement:

### Must have

- Snowflake connection.
- CoCo Skill.
- Hypothesis ledger.
- Query ID tracking.
- Multiple hypothesis tracking.
- One multiple-testing correction.
- Fake intervention dates.
- Pre-trend check.
- Evidence package.
- Gemma explanation.
- Investigation UI.

### Nice to have

- Negative controls.
- Block permutation.
- Circular shifts.
- Robustness analysis.
- Query-history reconciliation.
- CLI.

### Future

- More causal designs.
- More warehouses.
- Jupyter integration.
- Databricks integration.
- BigQuery integration.
- Agent framework integrations.
- Research preregistration workflows.

---

# 58. Recommended MVP Sequence

## Phase 1 — Data

Set up Snowflake dataset.

Verify:

- schema,
- time range,
- data quality,
- missing values.

---

## Phase 2 — Hypothesis Ledger

Build:

```text
Experiment
Hypothesis
Query
Result
```

---

## Phase 3 — CoCo Skill

Create `SKILL.md`.

Force hypothesis registration.

---

## Phase 4 — Statistics

Implement:

- effect size,
- p-value,
- one multiple-testing method,
- confidence interval where applicable.

---

## Phase 5 — Falsification

Implement:

1. placebo dates,
2. pre-trend,
3. one time-series robustness test.

---

## Phase 6 — Evidence Package

Build strict JSON schema.

---

## Phase 7 — Gemma

Build constrained explanation prompt.

---

## Phase 8 — UI

Build investigation screen.

---

## Phase 9 — Audit

Compare internal records with Snowflake Query History.

---

## Phase 10 — Demo

Prepare synthetic true/false cases.

---

# 59. UI Screens

## Screen 1 — Home

```text
PLACEBO

Falsification layer for AI data agents

[Start Investigation]
```

---

## Screen 2 — Investigation

```text
Question:
What caused the Q3 sales increase?

Agent:
CoCo

Status:
Investigating

Hypotheses:
47

Queries:
132

Candidates:
8
```

---

## Screen 3 — Hypothesis Explorer

```text
HYP-0042

Campaign X increased sales

Status:
FALSIFICATION RUNNING

Evidence:
+21%

Raw p:
0.012
```

---

## Screen 4 — Falsification

```text
MULTIPLE TESTING       ✓
PLACEBO DATES          ✗
PRE-TREND              ✗
NEGATIVE CONTROL       ✓
ROBUSTNESS             ⚠
```

---

## Screen 5 — Verdict

```text
INSUFFICIENT EVIDENCE

The observed increase is real,
but the available evidence does
not strongly support attributing
it to Campaign X.
```

---

## Screen 6 — Full Audit Trail

```text
47 hypotheses
132 SQL queries
8 candidate findings
2 corrected candidates
1 final candidate
```

This screen proves that Placebo is not simply a chatbot.

---

# 60. Visual Design Direction

Avoid generic AI dashboard styling.

Do not use:

- excessive gradients,
- glowing cards,
- robot illustrations,
- "AI magic" graphics,
- huge chatbot UI.

The visual metaphor should be:

## Scientific investigation / forensic audit.

Use:

- evidence cards,
- timeline,
- hypothesis IDs,
- pass/fail checks,
- experiment graphs,
- query trail,
- clear typography,
- restrained colors,
- strong hierarchy.

Suggested visual states:

```text
GREEN  = survived test
RED    = falsified / failed
AMBER  = uncertainty
GRAY   = not applicable
BLUE   = neutral evidence
```

---


# 62. Evaluation Metrics for Placebo

The project itself should be tested.

## Metric 1 — False discovery reduction

On synthetic datasets with known null relationships:

Compare:

```text
CoCo without Placebo
vs
CoCo + Placebo
```

Measure how often false findings are reported.

---

## Metric 2 — True positive retention

Ensure Placebo does not reject genuine effects excessively.

---

## Metric 3 — Audit completeness

Percentage of executed analytical queries linked to a hypothesis.

---

## Metric 4 — Explanation faithfulness

Check whether Gemma mentions only evidence present in the evidence package.

---

## Metric 5 — Reproducibility

Same data + same hypothesis + same configuration should produce reproducible statistical results.

---

# 63. Important Engineering Rules

## Rule 1

Never store secrets in Git.

---

## Rule 2

Use `.env`.

---

## Rule 3

Use typed schemas.

---

## Rule 4

Keep statistical calculations deterministic.

---

## Rule 5

Write tests for every statistical function.

---

## Rule 6

Do not let the LLM directly mutate verdicts.

---

## Rule 7

Every verdict should have machine-readable reasons.

---

## Rule 8

Every result should link back to its evidence.

---

## Rule 9

Every SQL query used in an analysis should have a traceable query ID where possible.

---

## Rule 10

Never silently discard a materially different hypothesis/specification.

---

# 64. Security Rules

Snowflake credentials:

```text
Never commit
Never display
Never send to Gemma
```

Use:

```text
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_PASSWORD
SNOWFLAKE_ROLE
SNOWFLAKE_WAREHOUSE
```

Prefer key-pair/OAuth authentication where appropriate for the deployment.

Use least privilege.

---

# 65. AI Safety Rules

Gemma must not:

- access raw credentials,
- invent statistical results,
- change p-values,
- change verdicts,
- claim causal certainty,
- create fake evidence,
- hide failed tests.

Gemma may:

- summarize,
- explain,
- identify evidence-supported alternatives,
- communicate uncertainty,
- produce human-readable reports.

---


# 67. What Makes the Project Technically Impressive

The project combines:

```text
AI agents
+
warehouse observability
+
hypothesis tracking
+
multiple testing
+
time-series statistics
+
falsification
+
open-weight AI
+
evidence-grounded generation
```

Each component has a clear purpose.

---

# 68. What Makes the Project Judge-Friendly

A judge can understand the entire story in 30 seconds:

> "We gave an AI access to data and asked it to find something interesting."

Then:

> "It found a significant result."

Then:

> "But it tried 47 hypotheses."

Then:

> "Our system audits all 47 and tries to falsify the winner."

Then:

> "The winner fails the placebo test."

Then:

> "Gemma explains why."

This is the core demo.

---

# 69. Final Pitch

## 30-second version

> **AI data agents can explore thousands of possibilities in seconds. That makes them incredibly powerful—but it also creates a statistical problem: if you search enough, you'll eventually find something that looks significant. Placebo is an open-source falsification layer for AI data agents. It records every hypothesis, corrects for the full search, runs time-series-aware placebo and robustness tests, and gives the final evidence to Gemma for a constrained explanation. CoCo finds the pattern. Placebo tries to break it before you believe it.**

---

# 70. 60-second version

> **Today, an AI analyst can query a warehouse hundreds of times, try different metrics, segments and time windows, and eventually discover a pattern that looks statistically significant. The problem is that the user may only see the winning result—not the dozens of analyses that were discarded. That's a modern form of the multiple-testing and p-hacking problem.**
>
> **Placebo solves this by becoming an adversarial layer around the AI analyst. Every hypothesis is registered. Every relevant analysis is logged. Placebo accounts for the number of tests, then tries to falsify promising findings using time-aware placebo dates, pre-trend checks, negative controls and robustness tests.**
>
> **The statistical engine produces the evidence; Gemma does not calculate or invent the statistics. It only explains the verified evidence package. With Snowflake and CoCo, we can demonstrate this directly inside a real warehouse workflow.**

---

# 71. Winning Positioning

Do not say:

> "We built an AI statistical checker."

Say:

> **"We built a falsification layer for autonomous data analysis."**

Do not say:

> "Gemma analyzes the data."

Say:

> **"Gemma explains an evidence package produced by deterministic statistical checks."**

Do not say:

> "CoCo is monitored."

Say:

> **"Every analytical hypothesis becomes an auditable experiment."**

Do not say:

> "We detect p-hacking."

Say:

> **"We make the AI's analytical search space visible and test whether its selected findings survive falsification."**

---

# 72. Final Architecture Summary

```text
                    ┌─────────────┐
                    │    USER     │
                    └──────┬──────┘
                           ↓
                    ┌─────────────┐
                    │    CoCo     │
                    └──────┬──────┘
                           ↓
                    ┌─────────────┐
                    │   PLACEBO   │
                    │    SKILL    │
                    └──────┬──────┘
                           ↓
                ┌─────────────────────┐
                │ Hypothesis Ledger   │
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │ Snowflake Analysis  │
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │ Query History Audit │
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │ Statistical Engine  │
                └──────────┬──────────┘
                           ↓
              ┌────────────┼────────────┐
              ↓            ↓            ↓
          Correction    Placebo      Pre-trend
              ↓            ↓            ↓
              └────────────┼────────────┘
                           ↓
                ┌─────────────────────┐
                │ Falsification Engine│
                └──────────┬──────────┘
                           ↓
                ┌─────────────────────┐
                │  Evidence Package   │
                └──────────┬──────────┘
                           ↓
                    ┌─────────────┐
                    │    Gemma    │
                    │ Explanation │
                    └──────┬──────┘
                           ↓
                ┌─────────────────────┐
                │ Investigation UI    │
                └─────────────────────┘
```

---

# 73. Final Product Definition

## PLACEBO

### The falsification layer for AI data agents.

```text
CoCo:
"Look for something interesting."

Placebo:
"Show me everything you tried."

CoCo:
"I found a significant result."

Placebo:
"Let's try to break it."

Statistics:
"Here is the evidence."

Gemma:
"Here is what the evidence actually supports."

User:
"Now I know how much I should trust it."
```

---

# 74. The Core Insight

The project is not about stopping AI from doing analysis.

It is about changing the workflow from:

```text
AI finds pattern
      ↓
AI reports pattern
```

to:

```text
AI finds pattern
      ↓
Record search
      ↓
Account for alternatives
      ↓
Try to falsify
      ↓
Check robustness
      ↓
Build evidence package
      ↓
Explain uncertainty
      ↓
Report
```

That is the complete Placebo philosophy.

---

# 76. Definition of Done

Placebo is ready for submission when:

- [ ] Public GitHub repository exists.
- [ ] Open-source license is present.
- [ ] CoCo skill is included.
- [ ] Snowflake dataset is documented.
- [ ] Snowflake integration works.
- [ ] Hypothesis ledger works.
- [ ] Every major analysis receives a hypothesis ID.
- [ ] SQL/query IDs are captured where possible.
- [ ] Query History reconciliation works.
- [ ] Multiple-testing correction works.
- [ ] At least one time-series placebo test works.
- [ ] Pre-trend analysis works.
- [ ] Evidence package has a strict schema.
- [ ] Gemma receives only evidence package data.
- [ ] Gemma cannot modify statistical results.
- [ ] Synthetic ground-truth dataset exists.
- [ ] True-positive scenario works.
- [ ] False-positive scenario works.
- [ ] Multiple-testing trap scenario works.
- [ ] Demo can be completed in under 5 minutes.
- [ ] README explains architecture.
- [ ] README explains limitations.
- [ ] Tests cover statistical core.
- [ ] No credentials are committed.
- [ ] No unsupported claims are made in the presentation.
