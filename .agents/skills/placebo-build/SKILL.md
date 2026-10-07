---
name: placebo-build
description: >
  Build the Placebo falsification layer for AI data agents. 
  Activate this skill when working on any part of the Placebo project — 
  statistical engine, Snowflake integration, CoCo skill, FastAPI backend, 
  investigation UI, Gemma explanation layer, or demo preparation.
  Triggers: "placebo", "falsification", "hypothesis ledger", "multiple testing",
  "p-hacking", "evidence package", "CoCo skill", "placebo dates", "pre-trend",
  "verdict engine", "investigation UI", "statistical audit".
---

# Placebo Build Skill

## What Is Placebo

Placebo is an open-source falsification and statistical-audit layer for AI data agents.
When an AI agent (like Snowflake CoCo) explores data and finds "interesting" patterns,
Placebo intercepts the workflow to:

1. Log every hypothesis the agent investigates
2. Count the search space
3. Apply multiple-testing corrections
4. Run time-series-aware falsification tests
5. Build a structured evidence package
6. Explain the evidence using Gemma (constrained — never invents statistics)
7. Present an investigation UI with verdicts and audit trails

## Core Principle

> The AI searches for patterns. Placebo searches for reasons not to trust those patterns.

## Spec Reference

The full specification is at `d:\placebo\details.md` (2557 lines, 74 sections).
Always consult it for detailed requirements. Key sections:
- Sections 1-6: Philosophy and problem statement
- Sections 13-16: Core modules (Ledger, Query Tracker, Analysis Registry, Multiple Testing)
- Sections 17-23: Falsification tests (fake dates, pre-trend, negative control, block permutation, circular shift, alternative window)
- Sections 24-28: Robustness, alternatives, verdict, Gemma prompt contract
- Sections 29-38: Architecture, tech stack, structure, data models, API
- Section 39-40: CoCo skill and rules
- Section 57: MVP scope (must-have vs nice-to-have)
- Section 58: Build phases
- Section 76: Definition of done

## Persona Reference

Consult `d:\placebo\persona.md` for the 6 persona system:
1. **Architect** — data models, schemas, protocols
2. **Statistician** — all statistical calculations and tests
3. **Snowflake Engineer** — Snowflake client, CoCo skill, Query History
4. **Backend Engineer** — FastAPI, pipeline orchestration, CLI
5. **Frontend Engineer** — Investigation UI
6. **LLM Integrator** — Gemma explanation layer, guardrails

## Project Structure

```
placebo/
├── README.md
├── LICENSE (Apache-2.0 or MIT)
├── pyproject.toml
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── statistics.md
│   ├── falsification.md
│   ├── snowflake.md
│   └── gemma.md
├── placebo/                    # Python package (core library)
│   ├── __init__.py
│   ├── models/                 # Pydantic data models
│   │   ├── hypothesis.py
│   │   ├── query.py
│   │   ├── result.py
│   │   ├── verdict.py
│   │   └── evidence.py
│   ├── protocols/              # Interface contracts (typing.Protocol)
│   │   ├── storage.py
│   │   └── llm.py
│   ├── statistics/             # Deterministic statistical engine
│   │   ├── effects.py          # Effect size, CI
│   │   ├── multiple_testing.py # BH, Holm, Bonferroni
│   │   └── tests.py            # Test selection + execution
│   ├── timeseries/             # Time-series falsification
│   │   ├── placebo_dates.py    # Fake intervention dates
│   │   ├── pretrend.py         # Pre-trend detection
│   │   ├── block_permutation.py
│   │   └── robustness.py
│   ├── falsification/          # Falsification orchestration
│   │   ├── engine.py
│   │   └── negative_controls.py
│   ├── verdict/                # Deterministic verdict engine
│   │   └── engine.py
│   ├── evidence/               # Evidence package
│   │   ├── builder.py
│   │   ├── schema.py
│   │   ├── schema.json         # JSON Schema (versioned)
│   │   └── validator.py
│   ├── llm/                    # LLM explanation layer
│   │   ├── client.py           # Model-agnostic client
│   │   ├── providers/          # DeepInfra, Vertex, Ollama
│   │   ├── prompts.py
│   │   └── guardrails.py
│   ├── snowflake/              # Snowflake integration
│   │   ├── client.py
│   │   ├── query_history.py
│   │   ├── storage.py
│   │   ├── mapper.py
│   │   └── ddl/
│   ├── storage/                # Storage implementations
│   │   └── sqlite.py           # Local dev fallback
│   ├── pipeline/               # Audit pipeline orchestration
│   │   └── audit.py
│   ├── api/                    # FastAPI application
│   │   ├── app.py
│   │   ├── routes/
│   │   └── dependencies.py
│   └── cli/                    # CLI entry point
│       └── main.py
├── skill/                      # CoCo custom skill
│   └── placebo-audit/
│       └── SKILL.md
├── tests/
│   ├── unit/
│   ├── statistical/
│   ├── timeseries/
│   ├── integration/
│   ├── llm/
│   └── fixtures/               # Synthetic test datasets
├── demo/                       # Demo scenarios
│   ├── scenario_true_positive.py
│   ├── scenario_false_positive.py
│   └── scenario_pretrend.py
└── web/                        # Investigation UI
    ├── index.html
    ├── css/
    └── js/
```

## Technology Stack

| Layer | Technology | Version Guidance |
|-------|-----------|-----------------|
| Language | Python 3.11+ | Use type hints throughout |
| Data Models | Pydantic v2 | BaseModel with strict validation |
| Statistics | SciPy, statsmodels, NumPy | Use `statsmodels.stats.multitest.multipletests` for corrections |
| Data | pandas or Polars | For time-series manipulation |
| Backend | FastAPI | With Uvicorn |
| CLI | typer or click | |
| Snowflake | snowflake-connector-python | Use env vars for credentials |
| LLM | OpenAI-compatible API (DeepInfra/Vertex/Ollama) | For Gemma 4 |
| Frontend | HTML/CSS/JS | Vanilla or lightweight — no Next.js for MVP |
| Charts | Chart.js or Recharts (if React) | Time-series visualization |
| Testing | pytest | With synthetic fixtures |
| Storage | SQLite (dev), Snowflake (prod) | Both implement the same Protocol |

## Critical Rules — ALWAYS Follow These

### Statistical Integrity
```
1. The LLM NEVER calculates, modifies, or invents statistical results.
2. All statistics are computed by deterministic Python code using SciPy/statsmodels.
3. The verdict engine is a PURE FUNCTION: evidence -> verdict. No LLM involvement.
4. Every statistical function must have unit tests with known expected outputs.
5. If a test's assumptions are violated, return TEST_NOT_APPLICABLE — never a fake result.
6. Do not claim BH "solves p-hacking" — it addresses one part of the multiple-testing problem.
```

### LLM Safety
```
7. The LLM receives ONLY the evidence package — never raw data, credentials, or app state.
8. The LLM prompt must follow the Prompt Contract (spec Section 28).
9. Never send PII or credentials in prompts.
10. If the LLM is unavailable, still produce the verdict + evidence package (skip explanation).
```

### Security
```
11. NEVER commit Snowflake credentials. Use .env / environment variables.
12. Use SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE, SNOWFLAKE_WAREHOUSE.
13. Never log credentials or include them in error messages.
14. Prefer key-pair/OAuth authentication where possible.
```

### Language and Claims
```
15. Use: "consistent with", "insufficient evidence", "evidence is weakened by", "robust to tested checks".
16. NEVER use: "proved", "caused" (without valid causal design), "guaranteed", "certain", "scientifically proven".
17. Placebo is a "falsification and audit layer" — NOT a "causal-proof engine".
```

### Architecture
```
18. The core library (placebo/) must be importable WITHOUT FastAPI, Snowflake, or LLM dependencies.
19. Use Protocols (typing.Protocol) for all module boundaries.
20. Use dependency injection for external services.
21. The CoCo skill is ONE integration — Placebo must also work via CLI and API without CoCo.
```

## Verdict Decision Matrix

Use these deterministic rules for the verdict engine:

| Condition | Verdict |
|-----------|---------|
| Survives multiple-testing correction AND all applicable falsification tests pass | `ROBUST_TO_TESTED_CHECKS` |
| Survives correction AND some falsification tests fail | `WEAK_EVIDENCE` |
| Does not survive multiple-testing correction | `INSUFFICIENT_EVIDENCE` |
| >= 50% of placebo dates show similar effect size | `FALSIFICATION_WARNING` |
| Pre-trend detected AND no correction survival | `INSUFFICIENT_EVIDENCE` |
| Pre-trend detected AND correction survives | `WEAK_EVIDENCE` |
| Not enough data to run any test | `INSUFFICIENT_DATA` |
| Test assumptions violated | `TEST_NOT_APPLICABLE` (for that specific test) |
| Falsification results conflict with each other | `INCONCLUSIVE` |
| No hypothesis survives any check | `NO_ROBUST_FINDING` |

## Evidence Package Schema (v1.0)

```json
{
  "schema_version": "1.0",
  "experiment_id": "EXP-001",
  "hypothesis": {
    "id": "HYP-0042",
    "statement": "Campaign X increased daily sales",
    "outcome": "daily_sales",
    "treatment": "campaign_x",
    "population": "all_stores",
    "time_window": {
      "start": "2026-01-01",
      "end": "2026-09-30"
    }
  },
  "search_context": {
    "total_hypotheses_tested": 47,
    "initially_significant": 8,
    "survived_correction": 2
  },
  "statistical_result": {
    "effect_size": 0.21,
    "standard_error": 0.04,
    "raw_p_value": 0.012,
    "adjustment_method": "benjamini_hochberg",
    "adjusted_p_value": 0.31,
    "confidence_interval": [0.04, 0.38],
    "sample_size": 12000,
    "test_used": "welch_t_test"
  },
  "falsification_results": [
    {
      "test_type": "placebo_dates",
      "status": "FAILED",
      "details": "Similar effect found at 4 of 6 placebo dates",
      "placebo_effects": [0.18, 0.15, 0.22, 0.19, 0.03, 0.01],
      "real_effect": 0.21
    },
    {
      "test_type": "pretrend",
      "status": "FAILED",
      "details": "Positive trend detected in 30-day pre-treatment window",
      "pretrend_slope": 0.003,
      "pretrend_p_value": 0.02
    },
    {
      "test_type": "negative_control",
      "status": "PASSED",
      "details": "No effect detected on unrelated metric"
    }
  ],
  "verdict": {
    "conclusion": "INSUFFICIENT_EVIDENCE",
    "confidence": "LOW",
    "reasons": [
      "Adjusted p-value (0.31) does not survive BH correction at alpha=0.05",
      "Similar effects appear at 4 of 6 placebo dates",
      "Pre-existing upward trend detected before treatment"
    ]
  },
  "limitations": [
    "Block permutation test was not applicable (insufficient pre-period length)",
    "Negative control was user-supplied and not independently validated"
  ]
}
```

## CoCo Skill Rules (for skill/placebo-audit/SKILL.md)

The CoCo skill must enforce these 10 rules:

```
RULE 1: Every testable hypothesis must be registered before analysis.
RULE 2: Do not report only the best result — record ALL tested hypotheses.
RULE 3: Record all materially different tested specifications.
RULE 4: Record Snowflake query IDs for every analytical query.
RULE 5: Do not claim causality from correlation alone.
RULE 6: Use time-series-aware falsification for temporal data.
RULE 7: Do not fabricate negative controls.
RULE 8: Do not use a placebo test when its assumptions are invalid.
RULE 9: Provide a structured evidence package for every candidate finding.
RULE 10: The final language model explanation may only use that evidence package.
```

## MVP Priority

### P0 — Must Ship
- [ ] Hypothesis Ledger (Pydantic models + SQLite storage)
- [ ] Statistical Engine (effect size, p-value, Benjamini-Hochberg correction)
- [ ] Falsification: Fake intervention dates test
- [ ] Falsification: Pre-trend detection
- [ ] Evidence Package (strict JSON schema with validation)
- [ ] Model Explanation (Gemma via API, constrained prompt, guardrails)
- [ ] Verdict Engine (deterministic decision matrix)
- [ ] FastAPI backend with core endpoints
- [ ] Investigation UI (3 key screens: investigation, hypothesis, verdict)
- [ ] Demo scenarios (true positive, false positive, pre-trend trap)

### P1 — Should Ship
- [ ] CoCo SKILL.md
- [ ] Snowflake Query ID tracking
- [ ] Query History reconciliation
- [ ] CLI (`placebo audit`, `placebo explain`)

### P2 — Nice to Have
- [ ] Negative controls
- [ ] Block permutation
- [ ] Circular shifts
- [ ] Robustness analysis (multi-window sensitivity)
- [ ] Docker packaging

## Demo Scenarios

### Scenario 1 — True Positive
Inject a real +15% effect after a specific date. Run 5 hypotheses (4 null + 1 real).
Expected: The real hypothesis survives correction, passes placebo dates, passes pre-trend.
Verdict: `ROBUST_TO_TESTED_CHECKS`.

### Scenario 2 — False Positive (Multiple Testing Trap)
Generate 50 null hypotheses (no real effect). One will have raw p < 0.05 by chance.
Expected: Raw p-value looks significant, but BH correction makes adjusted p > 0.05.
Verdict: `INSUFFICIENT_EVIDENCE`.

### Scenario 3 — Pre-Trend Trap
Inject a pre-existing upward trend that starts before the "treatment date".
Expected: Raw analysis shows an "effect", but pre-trend detection catches it.
Verdict: `WEAK_EVIDENCE` or `INSUFFICIENT_EVIDENCE`.

## Common Mistakes to Avoid

1. **Do NOT let the LLM generate p-values** — this is the #1 anti-pattern
2. **Do NOT hardcode Snowflake credentials** — always use env vars
3. **Do NOT use Next.js for the MVP frontend** — plain HTML/CSS/JS is sufficient
4. **Do NOT skip tests for statistical functions** — these are the trust foundation
5. **Do NOT claim Placebo "proves" anything** — it falsifies and audits
6. **Do NOT build all 6 falsification tests for MVP** — placebo dates + pre-trend is enough
7. **Do NOT make the verdict engine call the LLM** — verdicts are deterministic
8. **Do NOT send raw warehouse data to Gemma** — only send the evidence package
9. **Do NOT ignore the evidence package schema version** — always include `schema_version`
10. **Do NOT couple the core library to Snowflake** — use Protocols for storage abstraction
