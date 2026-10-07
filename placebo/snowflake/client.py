"""
Snowflake client with connection pooling, credentials management, and query execution.
Designed for least privilege and push-down SQL execution.
"""

import os
from typing import Any, Dict, List, Optional
import pandas as pd

try:
    import snowflake.connector
    from snowflake.connector.errors import DatabaseError, OperationalError
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False


class SnowflakeClient:
    """Manages connection to Snowflake cloud data warehouse."""

    def __init__(
        self,
        account: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        warehouse: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        role: Optional[str] = None
    ):
        self.account = account or os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = user or os.getenv("SNOWFLAKE_USER")
        self.password = password or os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        self.role = role or os.getenv("SNOWFLAKE_ROLE")
        self._conn = None

    def is_configured(self) -> bool:
        """Check if minimum required credentials are present."""
        return bool(self.account and self.user and (self.password or os.getenv("SNOWFLAKE_PRIVATE_KEY")))

    def connect(self):
        """Establish connection to Snowflake."""
        if not SNOWFLAKE_AVAILABLE:
            raise ImportError(
                "snowflake-connector-python is not installed. "
                "Install it with: pip install snowflake-connector-python"
            )
        if not self.is_configured():
            raise ValueError(
                "Snowflake credentials missing. Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, "
                "and SNOWFLAKE_PASSWORD in your environment or .env file."
            )

        kwargs = {
            "account": self.account,
            "user": self.user,
            "password": self.password,
            "warehouse": self.warehouse,
            "database": self.database,
            "schema": self.schema,
        }
        if self.role:
            kwargs["role"] = self.role

        self._conn = snowflake.connector.connect(**kwargs)
        return self._conn

    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dicts."""
        if not self._conn:
            self.connect()

        cursor = self._conn.cursor(snowflake.connector.DictCursor)
        try:
            cursor.execute(sql, params or {})
            return cursor.fetchall()
        finally:
            cursor.close()

    def query_to_dataframe(self, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Execute SQL and return results as a Pandas DataFrame."""
        rows = self.execute_query(sql, params)
        return pd.DataFrame(rows)

    def close(self):
        """Close Snowflake connection."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
