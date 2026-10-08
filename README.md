# Placebo: An Active Falsification Layer for Snowflake AI Data Agents

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Snowflake](https://img.shields.io/badge/Snowflake-Marketplace_Certified-29B5E8.svg)](https://www.snowflake.com/)
[![Open--Weight AI](https://img.shields.io/badge/Open--Weight_AI-Gemma-8E75C2.svg)](https://ai.google.dev/gemma)
[![arXiv](https://img.shields.io/badge/arXiv-2606.27687-B31B1B.svg)](https://arxiv.org/abs/2606.27687)

---

## Executive Overview

Placebo is an open-source statistical audit and active falsification layer designed to sit between autonomous AI data agents (such as Snowflake Cortex Code) and enterprise decision-makers.

When an autonomous AI agent explores enterprise databases, it operates with superhuman speed: an agent can execute dozens of SQL queries across arbitrary dimensional cuts in seconds. However, this velocity introduces a critical econometric failure mode: **automated p-hacking, multiple testing bias, and spurious correlations**. Across noisy time-series datasets, testing enough arbitrary segmentations guarantees finding correlations with nominal p < 0.05.

Placebo serves as an impartial scientific peer reviewer. Rather than accepting correlations at face value, Placebo intercepts candidate findings, logs them in an append-only ledger, and subjects them to an active battery of econometric stress tests—pre-trend drift detection, synthetic in-time placebo dates, leave-one-out sensitivity checks, and Benjamini-Hochberg False Discovery Rate (FDR) adjustments—before producing a verifiable verdict.

---

## Theoretical Foundation & Research Grounding

This project implements the foundational methodology introduced in:

> **Mitigating LLM-based p-Hacking by Preregistering for the Next LLM**  
> *arXiv:2606.27687 [cs.AI / stat.ME]*  
> Link: [https://arxiv.org/abs/2606.27687](https://arxiv.org/abs/2606.27687)

### Core Insight
The research establishes that when large language models are tasked with exploratory data analysis, they systematically engage in data dredging: iteratively altering regression specifications, adjusting subsets, and selectively reporting only nominal positive results without accounting for the expanded search space.

Placebo directly operationalizes the paper's framework through three architectural primitives:
1. **Pre-Registration Ledger:** The exploratory agent must formally pre-register its target metric, dimension filters, and analysis window prior to inspecting outcome data.
2. **Search Space Multiplicity Burden:** Placebo maintains a persistent search-space denominator $k$ across the entire exploratory session, forcing multiple-testing adjustments that scale with exploratory breadth.
3. **Separation of Discovery and Adjudication:** An exploratory agent (Snowflake CoCo) proposes candidate findings, but an independent, deterministic falsification engine adjudicates them, eliminating self-serving confirmation bias.

---

## Architecture

```
+-----------------------------------------------------------------------------------+
|                        Autonomous Snowflake CoCo Agent                           |
|        Translates user queries into SQL; executes exploratory scans               |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                          PLACEBO FALSIFICATION LAYER                              |
|                                                                                   |
|  +---------------------------+              +----------------------------------+  |
|  |  Hypothesis Ledger (k)    | -----------> | Multiplicity Correction (BH-FDR) |  |
|  |  (Append-only SQLite)     |              +-----------------+----------------+  |
|  +---------------------------+                                |                   |
|                                                               v                   |
|  +---------------------------+              +----------------------------------+  |
|  | Deterministic Decision    | <----------- | Falsification Battery Engine     |  |
|  | Engine (CONFIRMED/REFUTED)|              | - Pre-Trend OLS Invariance       |  |
|  +-------------+-------------+              | - Synthetic In-Time Placebo Dates|  |
|                |                            | - Leave-One-Out Cluster Jackknife|  |
|                v                            +----------------------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  | Open-Weight Gemma Synthesis (Strict Prompt Contract, Zero Hallucination)    |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                   Live Snowflake Cloud Warehouse (PELMOREX_WEATHER)               |
|      Table: POINT_HISTORY_DAY (3,690 rows across 10 global cities: Paris, etc.)    |
+-----------------------------------------------------------------------------------+
```

---

## Key Capabilities

### 1. Invariant Scientific Protocol (The 10 Rules)
Defined in `skill/placebo-audit/SKILL.md`, Placebo binds AI agents to strict scientific conduct:
- **Mandatory Pre-Registration:** Hypotheses must be logged before outcome evaluation.
- **Query Lineage Tracking:** Every executed SQL query ID and execution timestamp is logged.
- **Anti-Cherry-Picking:** Reporting isolated significant subsets while ignoring flat aggregate effects is rejected.
- **Pre-Treatment Parallel Trend Invariance:** Rejects any claim where the metric was already drifting prior to the event date.
- **Counterfactual Placebo Date Robustness:** Injects 5 historical pseudo-intervention dates prior to treatment; if random baseline dates replicate the effect, the claim is falsified.
- **Deterministic Ruling:** Final verdicts are computed by mathematical rule matrix, preventing language models from altering statistical results.

### 2. Live Snowflake Marketplace Dataset Integration
Placebo connects directly to real-world cloud telemetry:
- **Dataset:** Global Weather & Climate Data for BI
- **Provider:** Pelmorex Weather Networks (Snowflake Marketplace)
- **Database / Schema:** `PELMOREX_WEATHER.PUBLIC` (or `GLOBAL_WEATHER_CLIMATE_DATA_BY_PELMOREX_WEATHER_SOURCE.PWS_BI_SAMPLE`)
- **Table:** `POINT_HISTORY_DAY`
- **Volume:** 3,690 daily records across 10 international locations (Paris, Tokyo, New York, Calgary, Houston, Sydney, Los Angeles, Cape Town, Mexico City, Sao Paulo).
- **Observed Metrics:** `AVG_TEMPERATURE_AIR_2M_F`, `AVG_PRESSURE_MEAN_SEA_LEVEL_MB`, `AVG_HUMIDITY_RELATIVE_2M_PCT`.

### 3. Open-Weight AI Architecture (Gemma)
- **Model Family:** Open-weight Google Gemma models (`gemma-2-9b-it`, `gemma2:27b` via local Ollama and the Gemini developer API).
- **Role in Solution:** Once Placebo computes mathematical statistics (Welch's t-test, OLS pre-trend regressions, and Benjamini-Hochberg critical values), Gemma synthesizes the plain-English executive summary.
- **Strict Guardrail Contract:** Gemma receives only the sealed Evidence Package JSON. It is programmatically constrained from modifying p-values, recalculating slopes, or overriding the deterministic verdict.

### 4. Standardized Model Context Protocol (MCP) Server
Placebo exposes native MCP tools for direct integration with external developer agents (Claude Desktop, Cursor, and Snowflake CoCo CLI):
- `placebo_register_hypothesis`: Pre-registers hypotheses into the session ledger.
- `placebo_audit_claim`: Runs the full falsification pipeline against live Snowflake tables.
- Implements RFC 9728 and RFC 7591 OAuth Dynamic Client Registration (DCR) for agent discovery.

---

## Live Case Studies

| Scenario | Target Entity & Metric | Pre-Trend Test | Placebo Dates | Final Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Paris Winter Warming (P-Hacked Trap)** | Paris: Air Temperature (`+11.49 deg F`) | **FAILED** (Slope: `-0.2160 deg F/day`, `p=0.0000`) | **FAILED** (5 of 5 fake dates significant) | **REFUTED** |
| **Sydney Atmospheric Shift (Authentic)** | Sydney: Sea-Level Pressure (`+9.77 mb`) | **PASSED** (Flat stationary baseline) | **PASSED** (0 of 5 fake dates significant) | **CONFIRMED** |
| **Cape Town Humidity Stabilization** | Cape Town: Relative Humidity (`+2.03%`) | **PASSED** (Stable pre-treatment window) | **PASSED** (0 of 5 fake dates significant) | **CONFIRMED** |
| **New York Summer Pressure Variance** | New York: Sea-Level Pressure (`-1.63 mb`) | **PASSED** | **PASSED** | **CONFIRMED** |

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Node.js 18.x or higher
- Snowflake account with access to Pelmorex Weather data (or standard Snowflake credentials)

### 1. Clone the Repository
```bash
git clone https://github.com/Abhi6537/placebo-mcp-skill.git
cd placebo-mcp-skill
```

### 2. Backend Setup (FastAPI & Statistical Engine)
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies in editable mode
pip install -e .
```

### 3. Configure Environment Variables
Create a `.env` file in the repository root:
```ini
# Snowflake Credentials
SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=GLOBAL_WEATHER_CLIMATE_DATA_BY_PELMOREX_WEATHER_SOURCE
SNOWFLAKE_SCHEMA=PWS_BI_SAMPLE
SNOWFLAKE_TABLE=POINT_HISTORY_DAY
SNOWFLAKE_ROLE=ACCOUNTADMIN

# LLM Explanation Layer (Open-Weight Gemma / Gemini API)
LLM_PROVIDER=gemini  # Options: gemini, ollama
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash

# Local Ollama Fallback (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:27b
```

### 4. Frontend Setup (Next.js Interactive Studio)
```bash
cd frontend1
npm install
```

Configure `frontend1/.env.local`:
```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
ENABLE_AUTH=false
ENABLE_GUEST_CHAT=true
```

---

## Running the Application

### 1. Launch the Backend API & MCP Server
```bash
# From repository root
uvicorn placebo.api.main:app --host 0.0.0.0 --port 8000 --reload
```
The FastAPI backend and MCP SSE endpoint will be live at `http://localhost:8000`.

### 2. Launch the Interactive Studio
```bash
# In a separate terminal
cd frontend1
npm run dev
```
Open your browser to `http://localhost:3000/studio` to explore the live investigation console.

### 3. Run the Automated Test Suite
```bash
# Run unit and econometric validation tests
pytest tests/ -v
```

---

## Command-Line Interface (CLI)

Placebo includes a full command-line interface for headless automation:

```bash
# Display version and engine status
placebo version

# Initialize local hypothesis database
placebo init

# Register a candidate hypothesis
placebo hypothesis register \
  --statement "Paris average temperature increased after Jan 1, 2026" \
  --metric AVG_TEMPERATURE_AIR_2M_F \
  --intervention 2026-01-01

# Execute active falsification audit
placebo audit HYP-LIVE-001

# Inspect full Evidence Package report
placebo report HYP-LIVE-001
```

---

## Codebase Organization

```
placebo-mcp-skill/
├── placebo/                         # Core Python package
│   ├── api/                         # FastAPI routes and SSE MCP streaming
│   ├── evidence/                    # Immutable Evidence Package assembler
│   ├── llm/                         # Open-weight Gemma integrations & guardrails
│   ├── mcp/                         # Model Context Protocol server implementation
│   ├── models/                      # Pydantic schemas (hypotheses, tests, verdicts)
│   ├── pipeline/                    # Audit pipeline orchestrator
│   ├── snowflake/                   # Snowflake client, connection pool, SQL pushdown
│   ├── statistics/                  # Welch's t-test, Cohen's d, Benjamini-Hochberg FDR
│   ├── storage/                     # SQLite persistence for hypothesis ledgers
│   ├── timeseries/                  # Pre-trend OLS, placebo dates, jackknife tests
│   └── verdict/                     # Deterministic decision matrix engine
├── frontend1/                       # Next.js 16 interactive studio
│   ├── app/                         # App router (studio, snowflake telemetry, mcp hub)
│   ├── components/                  # Site navigation, telemetry cards, audit gauges
│   └── public/                      # Static assets
├── skill/                           # Agent skill specifications
│   └── placebo-audit/SKILL.md       # 10 Invariant Rules protocol for CoCo agents
├── tests/                           # Pytest test suite (unit, integration, MCP)
├── pyproject.toml                   # Python package specification
└── README.md                        # Documentation
```

---

## Technologies and Frameworks

- **Backend Runtime:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Econometric Computation:** NumPy, SciPy, Statsmodels, Pandas
- **Data Warehouse:** Snowflake, `snowflake-connector-python`
- **Agent Interoperability:** Model Context Protocol (MCP) SDK, Server-Sent Events (SSE)
- **Language Models:** Open-weight Google Gemma (Gemma 2, Gemma 4 via Ollama & Gemini API)
- **Frontend Architecture:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Tabler Icons

---

## Limitations and Dependencies

1. **Pre-Intervention Duration:** Pre-trend OLS regression requires a minimum of 5 historical pre-treatment observations. In-time placebo dates testing requires at least 19 historical days to construct valid pseudo-windows.
2. **Cluster Analysis:** Leave-one-out sensitivity testing requires at least 2 distinct entities or clusters within the segment slice.
3. **Snowflake Permissions:** Running live queries requires an active Snowflake user with access to the specified database warehouse and table (`PELMOREX_WEATHER.PUBLIC.POINT_HISTORY_DAY` or equivalent).
4. **LLM Explanations:** The explanation layer is purely descriptive; it summarizes the deterministic evidence package and cannot alter or override statistical grades.

---

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.
