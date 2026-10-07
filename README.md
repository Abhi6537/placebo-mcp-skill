# Placebo 🛡️
### The Falsification & Statistical Audit Layer for AI Data Agents

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Snowflake](https://img.shields.io/badge/Snowflake-Certified-29B5E8.svg)](https://www.snowflake.com/)
[![Gemma 4](https://img.shields.io/badge/Gemma_4-Integrated-8E75C2.svg)](https://ai.google.dev/gemma)

Placebo is an open-source **statistical audit and active falsification layer** built for modern AI data agents (such as CoCo).

When autonomous AI agents query cloud data warehouses (Snowflake), they test dozens of dimensions, metrics, and time slices in seconds. This creates severe risk of **multiple testing, p-hacking, and spurious correlations**.

Placebo acts as the automated "senior econometrician" looking over the agent's shoulder:
1. **Hypothesis Ledger:** Silently tracks the search space burden of every query.
2. **Multiplicity Correction:** Automatically applies Benjamini-Hochberg (BH) FDR adjustments.
3. **Active Falsification Battery:** Executes pre-trend drift regressions, in-time placebo dates, and leave-one-out sensitivity tests directly on Snowflake.
4. **Deterministic Verdict Engine:** Pure function decision matrix producing `CONFIRMED`, `INCONCLUSIVE`, or `REFUTED`.
5. **Grounded Narrative Layer:** Uses **Google Gemma 4** to translate the immutable Evidence Package into executive English with **zero mathematical hallucination**.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   CoCo / AI Data Agent                      │
│   "Explores Snowflake, formulates candidate hypotheses"     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 PLACEBO FALSIFICATION LAYER                 │
│                                                             │
│   ┌─────────────────────┐       ┌────────────────────────┐  │
│   │  Hypothesis Ledger  │  ──►  │ Multiplicity (BH / FDR)│  │
│   └─────────────────────┘       └───────────┬────────────┘  │
│                                             ▼               │
│   ┌─────────────────────┐       ┌────────────────────────┐  │
│   │ Deterministic Judge │  ◄──  │ Falsification Battery  │  │
│   │(CONFIRMED | REFUTED)│       │ (Pre-trends, Placebos) │  │
│   └──────────┬──────────┘       └────────────────────────┘  │
│              ▼                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  Google Gemma 4 Translation (Strict Prompt Contract) │  │
│   └──────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Snowflake Data Warehouse                    │
│           "Push-Down SQL Execution on Live Data"            │
└─────────────────────────────────────────────────────────────┘
```

---

## Quickstart

### 1. Installation
```bash
git clone https://github.com/your-username/placebo.git
cd placebo
pip install -e .
```

### 2. Configure Environment
Copy the template and fill in your Snowflake credentials:
```bash
cp .env.example .env
```
*(Your `.env` file is protected by `.gitignore` and is never committed).*

### 3. Run the Automated Tests
```bash
pytest tests/ -v
```

### 4. Start the Web Console & REST API
```bash
uvicorn placebo.api.main:app --reload --port 8000
```
Open your browser to: **`http://localhost:8000`**

---

## CLI Usage
You can run audits directly from the command line:

```bash
# Check version
placebo version

# Initialize local ledger
placebo init

# Run an active audit on a dataset
placebo audit path/to/dataset.csv \
  --metric revenue \
  --date-col order_date \
  --intervention 2026-06-01 \
  --entity customer_id
```

---

## MCP Server (Model Context Protocol)

Placebo can run as an official MCP server for AI data agents (CoCo, Claude Desktop, Cursor):

### Running via Stdio
```bash
python -m placebo.mcp.server
# Or via entrypoint:
placebo-mcp
```

### CoCo / Client MCP Configuration
```json
{
  "mcpServers": {
    "placebo": {
      "command": "python",
      "args": ["-m", "placebo.mcp.server"],
      "env": {
        "SNOWFLAKE_ACCOUNT": "your-account",
        "SNOWFLAKE_USER": "your-user",
        "SNOWFLAKE_PASSWORD": "your-password",
        "GEMINI_API_KEY": "your-key"
      }
    }
  }
}
```

### MCP Tools Provided:
- `placebo_register_hypothesis`: Pre-registers hypotheses to track search-space burden and enforce multiplicity penalties (p-hacking prevention).
- `placebo_audit_claim`: Runs the active falsification battery directly on Snowflake with pre-trend checks, placebo dates, and Gemma 4 explanations.
- `placebo_get_evidence`: Fetches the immutable Evidence Package JSON by Audit ID.

---

## Repository Structure

- `placebo/mcp/` — Model Context Protocol (MCP) server implementation (`server.py`)
- `placebo/models/` — Strict Pydantic v2 domain models and Evidence Package Schema v1.0
- `placebo/protocols/` — Protocol boundaries (`StorageAdapter`, `FalsificationEngine`, `LLMExplainer`)
- `placebo/statistics/` — Deterministic mathematical engines (Welch t-test, Benjamini-Hochberg)
- `placebo/timeseries/` — Falsification battery (Pre-trend OLS, in-time placebos, jackknife)
- `placebo/snowflake/` — Snowflake connector, push-down SQL generators, and DDL scripts
- `placebo/verdict/` — Pure function deterministic decision matrix
- `placebo/llm/` — Gemma 4 explanation client, Prompt Contract, and guardrails
- `placebo/api/` — FastAPI REST endpoints
- `skill/placebo-audit/` — Official custom skill for AI Data Agents (`SKILL.md`)
- `web/` — Forensic scientific audit console (HTML/CSS/JS)

---

## License
Apache-2.0 License.
