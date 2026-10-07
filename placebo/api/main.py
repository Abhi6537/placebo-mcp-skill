"""
FastAPI application for Placebo.
Exposes endpoints for hypothesis registration, query logging, audit execution, and evidence retrieval.
Serves the web Investigation UI.
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from placebo import __version__
from placebo.models.evidence import EvidencePackage
from placebo.models.hypothesis import Hypothesis, QueryLog, SearchContext
from placebo.storage.sqlite import SQLiteStorage

app = FastAPI(
    title="Placebo API",
    description="Falsification and statistical audit layer for AI-driven data agents",
    version=__version__
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = SQLiteStorage()


class HealthResponse(BaseModel):
    status: str
    version: str


@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    """Health status endpoint."""
    return HealthResponse(status="healthy", version=__version__)


@app.post("/api/v1/hypotheses", response_model=Hypothesis, status_code=status.HTTP_201_CREATED)
def register_hypothesis(hyp: Hypothesis):
    """Register a new hypothesis in the ledger."""
    storage.save_hypothesis(hyp)
    return hyp


@app.get("/api/v1/hypotheses", response_model=List[Hypothesis])
def list_hypotheses(session_id: Optional[str] = None):
    """List all registered hypotheses."""
    return storage.list_hypotheses(session_id=session_id)


@app.get("/api/v1/hypotheses/{hypothesis_id}", response_model=Hypothesis)
def get_hypothesis(hypothesis_id: str):
    """Retrieve hypothesis by ID."""
    hyp = storage.get_hypothesis(hypothesis_id)
    if not hyp:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return hyp


@app.post("/api/v1/queries", response_model=QueryLog, status_code=status.HTTP_201_CREATED)
def log_query(query: QueryLog):
    """Log an executed query in the session."""
    storage.save_query_log(query)
    return query


@app.get("/api/v1/queries", response_model=List[QueryLog])
def list_queries(session_id: str):
    """List queries executed in a session."""
    return storage.list_query_logs(session_id)


@app.get("/api/v1/search_context/{session_id}", response_model=SearchContext)
def get_search_context(session_id: str):
    """Get the multiplicity search context for a session."""
    return storage.get_search_context(session_id)


@app.get("/api/v1/evidence/{audit_id}", response_model=EvidencePackage)
def get_evidence(audit_id: str):
    """Retrieve audited Evidence Package."""
    pkg = storage.get_evidence_package(audit_id)
    if not pkg:
        raise HTTPException(status_code=404, detail="Evidence Package not found")
    return pkg


# Mount static web Investigation UI if web folder exists
if os.path.exists("web"):
    app.mount("/", StaticFiles(directory="web", html=True), name="static")
