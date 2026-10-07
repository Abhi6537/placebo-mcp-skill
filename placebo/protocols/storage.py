"""
Protocols defining storage abstraction boundaries.
Core logic must never depend directly on a concrete storage engine.
"""

from typing import List, Optional, Protocol, runtime_checkable
from placebo.models.hypothesis import Hypothesis, QueryLog, SearchContext
from placebo.models.evidence import EvidencePackage


@runtime_checkable
class StorageAdapter(Protocol):
    """Protocol for persisting and retrieving hypotheses, query logs, and evidence packages."""

    def save_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Persist a hypothesis."""
        ...

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """Retrieve a hypothesis by ID."""
        ...

    def list_hypotheses(self, session_id: Optional[str] = None) -> List[Hypothesis]:
        """List hypotheses, optionally filtered by session."""
        ...

    def save_query_log(self, query: QueryLog) -> None:
        """Log an executed query."""
        ...

    def list_query_logs(self, session_id: str) -> List[QueryLog]:
        """Retrieve all queries executed in a session."""
        ...

    def get_search_context(self, session_id: str) -> SearchContext:
        """Compute or retrieve search context for a session."""
        ...

    def save_evidence_package(self, package: EvidencePackage) -> None:
        """Persist an audited evidence package."""
        ...

    def get_evidence_package(self, audit_id: str) -> Optional[EvidencePackage]:
        """Retrieve an evidence package by audit ID."""
        ...
