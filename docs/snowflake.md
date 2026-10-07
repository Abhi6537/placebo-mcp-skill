# Placebo — Snowflake Integration Guide

## 1. Credentials & Configuration
Placebo requires the following environment variables (stored in `.env`):
```ini
SNOWFLAKE_ACCOUNT=org-account_locator
SNOWFLAKE_USER=placebo_agent_user
SNOWFLAKE_PASSWORD=secure_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=PROD_DB
SNOWFLAKE_SCHEMA=ANALYTICS
SNOWFLAKE_ROLE=ANALYST_ROLE
```

## 2. Least Privilege Role Setup
Execute in Snowflake Worksheet as `SECURITYADMIN`:
```sql
CREATE ROLE IF NOT EXISTS PLACEBO_AUDITOR_ROLE;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE PLACEBO_AUDITOR_ROLE;
GRANT USAGE ON DATABASE PROD_DB TO ROLE PLACEBO_AUDITOR_ROLE;
GRANT USAGE ON SCHEMA PROD_DB.ANALYTICS TO ROLE PLACEBO_AUDITOR_ROLE;
GRANT SELECT ON ALL TABLES IN SCHEMA PROD_DB.ANALYTICS TO ROLE PLACEBO_AUDITOR_ROLE;
GRANT ROLE PLACEBO_AUDITOR_ROLE TO USER placebo_agent_user;
```

## 3. Query Execution Pattern
Placebo uses push-down aggregation queries via `placebo.snowflake.pushdown` to avoid transferring massive raw datasets over the network.
- Daily time series calculations (`AVG`, `STDDEV`, `COUNT`) are computed directly by Snowflake virtual warehouses.
- Only aggregated series rows (hundreds of rows, not millions) are fetched into Python memory for Welch's t-test and OLS regression.
