"""
SQLite Storage Adapter.
Implements the StorageAdapter protocol for local caching and zero-dependency operation.
"""

import json
import sqlite3
from typing import List, Optional
from placebo.models.evidence import EvidencePackage
from placebo.models.hypothesis import Hypothesis, QueryLog, SearchContext


class SQLiteStorage:
    """Local SQLite repository implementing StorageAdapter protocol."""

    def __init__(self, db_path: str = "./placebo_ledger.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS hypotheses (
                hypothesis_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                data_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS query_logs (
                query_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                sql_text TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                row_count INTEGER,
                execution_time_ms REAL,
                associated_hypothesis_id TEXT
            );
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_packages (
                audit_id TEXT PRIMARY KEY,
                hypothesis_id TEXT NOT NULL,
                data_json TEXT NOT NULL,
                generated_at TEXT NOT NULL
            );
            """)

    def save_hypothesis(self, hypothesis: Hypothesis) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO hypotheses (hypothesis_id, session_id, data_json, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    hypothesis.hypothesis_id,
                    hypothesis.session_id,
                    hypothesis.model_dump_json(),
                    hypothesis.status.value,
                    hypothesis.created_at.isoformat()
                )
            )

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM hypotheses WHERE hypothesis_id = ?",
                (hypothesis_id,)
            ).fetchone()
            if row:
                return Hypothesis.model_validate_json(row["data_json"])
            return None

    def list_hypotheses(self, session_id: Optional[str] = None) -> List[Hypothesis]:
        with self._get_conn() as conn:
            if session_id:
                rows = conn.execute(
                    "SELECT data_json FROM hypotheses WHERE session_id = ? ORDER BY created_at ASC",
                    (session_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT data_json FROM hypotheses ORDER BY created_at DESC"
                ).fetchall()
            return [Hypothesis.model_validate_json(r["data_json"]) for r in rows]

    def save_query_log(self, query: QueryLog) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO query_logs (query_id, session_id, sql_text, executed_at, row_count, execution_time_ms, associated_hypothesis_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    query.query_id,
                    query.session_id,
                    query.sql_text,
                    query.executed_at.isoformat(),
                    query.row_count,
                    query.execution_time_ms,
                    query.associated_hypothesis_id
                )
            )

    def list_query_logs(self, session_id: str) -> List[QueryLog]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT query_id, session_id, sql_text, executed_at, row_count, execution_time_ms, associated_hypothesis_id FROM query_logs WHERE session_id = ? ORDER BY executed_at ASC",
                (session_id,)
            ).fetchall()
            return [
                QueryLog(
                    query_id=r["query_id"],
                    session_id=r["session_id"],
                    sql_text=r["sql_text"],
                    executed_at=r["executed_at"],
                    row_count=r["row_count"],
                    execution_time_ms=r["execution_time_ms"],
                    associated_hypothesis_id=r["associated_hypothesis_id"]
                )
                for r in rows
            ]

    def get_search_context(self, session_id: str) -> SearchContext:
        hyps = self.list_hypotheses(session_id)
        queries = self.list_query_logs(session_id)
        # Search burden is max(hypotheses count, query count, 1)
        count = max(len(hyps), len(queries), 1)
        return SearchContext(
            session_id=session_id,
            total_hypotheses_tested=count,
            initially_significant=0,
            survived_correction=0,
            dimensions_explored=[]
        )

    def save_evidence_package(self, package: EvidencePackage) -> None:
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO evidence_packages (audit_id, hypothesis_id, data_json, generated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    package.audit_id,
                    package.hypothesis.hypothesis_id,
                    package.model_dump_json(),
                    package.generated_at.isoformat()
                )
            )

    def get_evidence_package(self, audit_id: str) -> Optional[EvidencePackage]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM evidence_packages WHERE audit_id = ?",
                (audit_id,)
            ).fetchone()
            if row:
                return EvidencePackage.model_validate_json(row["data_json"])
            return None
