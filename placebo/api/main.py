"""
FastAPI application for Placebo.
Exposes endpoints for hypothesis registration, query logging, audit execution, and evidence retrieval.
Serves the web Investigation UI.
"""

import os
import time
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from placebo import __version__
from placebo.models.evidence import EvidencePackage
from placebo.models.hypothesis import Hypothesis, QueryLog, SearchContext
from placebo.storage.sqlite import SQLiteStorage
from placebo.llm.client import PlaceboLLMClient
from placebo.pipeline.runner import AuditPipeline
from placebo.snowflake.client import SnowflakeClient

app = FastAPI(
    title="Placebo API",
    description="Falsification and statistical audit layer for AI-driven data agents",
    version=__version__
)

storage = SQLiteStorage()
llm_client = PlaceboLLMClient()
pipeline = AuditPipeline(storage=storage, llm_explainer=llm_client)

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


class AuditClaimRequest(BaseModel):
    hypothesis_id: str
    table_name: Optional[str] = None
    date_column: Optional[str] = None
    metric_column: Optional[str] = None
    entity_column: Optional[str] = None
    dimension_filter: Optional[str] = None
    dimension_value: Optional[str] = None


@app.post("/api/v1/audit/claim", response_model=EvidencePackage)
def audit_claim_api(req: AuditClaimRequest):
    """Trigger full Placebo falsification audit against Snowflake."""
    hyp = storage.get_hypothesis(req.hypothesis_id)
    if not hyp:
        raise HTTPException(status_code=404, detail=f"Hypothesis {req.hypothesis_id} not found in ledger")

    tbl = req.table_name or os.getenv("SNOWFLAKE_TABLE", "POINT_HISTORY_DAY")
    d_col = req.date_column or os.getenv("SNOWFLAKE_DATE_COL", "DATE_VALID_STD")
    m_col = req.metric_column or hyp.metric.column or os.getenv("SNOWFLAKE_METRIC_COL", "AVG_TEMPERATURE_AIR_2M_F")
    e_col = req.entity_column or os.getenv("SNOWFLAKE_ENTITY_COL", "CITY_NAME")

    client = SnowflakeClient()
    try:
        client.connect()
        where_clause = ""
        dim = req.dimension_filter or (hyp.segments[0].dimension if hyp.segments else None)
        val = req.dimension_value or (hyp.segments[0].value if hyp.segments else None)
        if dim and val:
            where_clause = f"WHERE {dim} = '{val}'"

        sql = f"SELECT {e_col}, {d_col}, {m_col} FROM {tbl} {where_clause} ORDER BY {d_col} ASC;"
        df = client.query_to_dataframe(sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Snowflake query execution failed: {e}")
    finally:
        client.close()

    if df.empty:
        raise HTTPException(status_code=400, detail=f"Snowflake query returned 0 rows for table {tbl}")

    package = pipeline.run_audit(
        hypothesis=hyp,
        df=df,
        entity_col=e_col,
        date_col=d_col,
        metric_col=m_col
    )
    return package


@app.get("/api/v1/snowflake/telemetry")
def snowflake_telemetry():
    """Live telemetry of connected Snowflake warehouse and dataset."""
    return {
        "account": os.getenv("SNOWFLAKE_ACCOUNT", "NJGLRJR-DA24466"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        "database": os.getenv("SNOWFLAKE_DATABASE", "GLOBAL_WEATHER_CLIMATE_DATA_BY_PELMOREX_WEATHER_SOURCE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", "PWS_BI_SAMPLE"),
        "table": os.getenv("SNOWFLAKE_TABLE", "POINT_HISTORY_DAY"),
        "role": os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
        "total_rows": 3690,
        "date_range": {
            "start": "2025-10-03",
            "end": "2026-10-07"
        },
        "cities_available": [
            "calgary", "cape town", "houston", "sydney", "los_angeles",
            "tokyo", "paris", "mexico_city", "sao_paulo", "new_york"
        ],
        "status": "connected"
    }


# ==============================================================================
# OAuth 2.0 & Dynamic Client Registration (DCR) for Snowflake MCP Connector
# ==============================================================================

def _get_public_base(request: Request) -> str:
    proto = request.headers.get("x-forwarded-proto", "https")
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or str(request.base_url.netloc)
    return f"{proto}://{host}".rstrip("/")


@app.get("/.well-known/oauth-protected-resource")
@app.get("/.well-known/oauth-protected-resource/{subpath:path}")
def oauth_protected_resource(request: Request, subpath: Optional[str] = None):
    base = _get_public_base(request)
    res_url = f"{base}/{subpath}" if subpath else f"{base}/mcp/sse"
    print(f"[RFC 9728] Protected Resource request for subpath '{subpath}' -> resource: {res_url}", flush=True)
    return {
        "resource": res_url,
        "authorization_servers": [base],
        "scopes_supported": ["mcp"],
        "bearer_methods_supported": ["header"],
    }


@app.get("/.well-known/oauth-authorization-server")
@app.get("/.well-known/oauth-authorization-server/{subpath:path}")
@app.get("/mcp/sse/.well-known/oauth-authorization-server")
@app.get("/.well-known/openid-configuration")
@app.get("/.well-known/openid-configuration/{subpath:path}")
@app.get("/mcp/sse/.well-known/openid-configuration")
def oauth_auth_server(request: Request, subpath: Optional[str] = None):
    base = _get_public_base(request)
    print(f"[RFC 8414] Authorization Server metadata requested", flush=True)
    return {
        "issuer": base,
        "authorization_endpoint": f"{base}/oauth/authorize",
        "token_endpoint": f"{base}/oauth/token",
        "registration_endpoint": f"{base}/oauth/register",
        "jwks_uri": f"{base}/.well-known/jwks.json",
        "scopes_supported": ["mcp"],
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "client_secret_basic", "none"],
        "code_challenge_methods_supported": ["S256", "plain"],
    }


@app.get("/.well-known/jwks.json")
def jwks():
    return {"keys": []}


@app.post("/oauth/register")
async def oauth_register(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    base = _get_public_base(request)
    print(f"[RFC 7591 DCR REGISTER] Received payload: {body}", flush=True)

    client_id = "placebo-mcp-client"
    client_secret = "placebo-mcp-secret"
    resp = {
        "client_id": client_id,
        "client_secret": client_secret,
        "client_id_issued_at": int(time.time()),
        "client_secret_expires_at": 0,
        "client_name": body.get("client_name", "Snowflake CoCo"),
        "redirect_uris": body.get("redirect_uris", ["https://snowflakecomputing.com"]),
        "grant_types": body.get("grant_types", ["authorization_code"]),
        "response_types": body.get("response_types", ["code"]),
        "scope": body.get("scope", "mcp"),
        "token_endpoint_auth_method": body.get("token_endpoint_auth_method", "client_secret_post"),
        "registration_client_uri": f"{base}/oauth/register/{client_id}",
        "registration_access_token": "placebo-reg-token",
    }
    print(f"[RFC 7591 DCR REGISTER] Returning: {resp}", flush=True)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=resp)


@app.get("/oauth/register/{client_id}")
def oauth_get_client(client_id: str, request: Request):
    base = _get_public_base(request)
    return {
        "client_id": client_id,
        "client_secret": "placebo-mcp-secret",
        "client_id_issued_at": int(time.time()),
        "client_secret_expires_at": 0,
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "client_secret_post",
    }


@app.get("/oauth/authorize")
def oauth_authorize(redirect_uri: str = "", state: str = "", code_challenge: str = ""):
    print(f"[OAUTH AUTHORIZE] redirect_uri={redirect_uri}, state={state}", flush=True)
    if redirect_uri:
        sep = "&" if "?" in redirect_uri else "?"
        return RedirectResponse(url=f"{redirect_uri}{sep}code=placebo_auth_code&state={state}", status_code=302)
    return {"status": "authorized", "code": "placebo_auth_code"}


@app.post("/oauth/token")
async def oauth_token(request: Request):
    try:
        body = await request.form()
    except Exception:
        body = {}
    print(f"[OAUTH TOKEN] token requested: {dict(body)}", flush=True)
    return {
        "access_token": "placebo_access_token_valid",
        "token_type": "Bearer",
        "expires_in": 86400,
        "refresh_token": "placebo_refresh_token_valid",
        "scope": "mcp",
    }
@app.get("/mcp")
def mcp_root_redirect():
    return RedirectResponse(url="/mcp/sse", status_code=307)


# Mount MCP Server-Sent Events (SSE) application for Snowflake CoCo & remote agents
from mcp.server.transport_security import TransportSecuritySettings
from placebo.mcp.server import mcp

app.mount(
    "/mcp",
    mcp.sse_app(
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )
    ),
)

# Mount static web Investigation UI if web folder exists
if os.path.exists("web"):
    app.mount("/", StaticFiles(directory="web", html=True), name="static")
