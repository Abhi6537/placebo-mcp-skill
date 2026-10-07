# Placebo — System Architecture & Design Specification

## 1. Architectural Philosophy
Placebo enforces three core invariant design principles:
1. **Separation of Computation and Narrative:** All p-values, corrections, and falsification statistics are computed strictly by deterministic Python scientific libraries (`scipy`, `numpy`, `statsmodels`). LLMs never perform calculations.
2. **Dependency Inversion:** The domain layer (`placebo.models`) and interface contracts (`placebo.protocols`) have zero dependencies on Snowflake, FastAPI, or LLM providers.
3. **Evidence Immutability:** Once an analysis is audited, an immutable `EvidencePackage` (Schema v1.0) is sealed and persisted with full query and hypothesis lineage.

## 2. Module Directory Structure
```
d:/placebo/
├── placebo/
│   ├── models/            # Pydantic v2 domain schemas (strict validation)
│   ├── protocols/         # Protocol boundaries (Storage, Falsifier, LLM)
│   ├── statistics/        # Deterministic statistical engines (Scipy/Numpy)
│   ├── timeseries/        # Placebo dates, pre-trend & sensitivity batteries
│   ├── snowflake/         # Snowflake connector, push-down SQL & DDL
│   ├── storage/           # SQLite fallback & cache
│   ├── verdict/           # Pure function deterministic rule engine
│   ├── evidence/          # Builder and Schema v1.0
│   ├── pipeline/          # Orchestration pipeline (runner)
│   ├── cli/               # Typer / Click CLI tool
│   ├── api/               # FastAPI REST endpoints
│   └── llm/               # Gemma / Gemini / Ollama explanation layer & guardrails
├── skill/
│   └── placebo-audit/     # CoCo / Agent custom skill (SKILL.md)
├── web/                   # Investigation UI (Scientific forensic dashboard)
├── docs/                  # Architectural and technical documentation
└── tests/                 # Unit & statistical validation tests
```

## 3. Data Contracts
- `Hypothesis`: Tracks claim, metric definition, dimension filters, and time window.
- `SearchContext`: Records the multiplicity burden (total hypotheses explored in session).
- `StatisticalResult`: Stores raw p-value, adjustment method, adjusted p-value, effect size, and 95% CI.
- `FalsificationResult`: Individual outcome of stress tests (Placebo Dates, Pre-trend, Leave-one-out).
- `VerdictDecision`: Deterministic outcome (`CONFIRMED`, `INCONCLUSIVE`, `REFUTED`).
- `EvidencePackage`: The root JSON contract containing all results and audit metadata.
