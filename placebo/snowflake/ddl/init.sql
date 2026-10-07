-- =============================================================================
-- Placebo Ledger Tables DDL for Snowflake
-- =============================================================================

CREATE TABLE IF NOT EXISTS PLACEBO_HYPOTHESIS_LEDGER (
    hypothesis_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    claim_description TEXT NOT NULL,
    metric_name VARCHAR(128) NOT NULL,
    metric_column VARCHAR(128) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    intervention_date DATE,
    segments VARIANT,
    status VARCHAR(32) DEFAULT 'REGISTERED',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS PLACEBO_QUERY_LOG (
    query_id VARCHAR(64) PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    sql_text TEXT NOT NULL,
    executed_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    row_count INT,
    execution_time_ms FLOAT,
    associated_hypothesis_id VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS PLACEBO_AUDIT_RESULTS (
    audit_id VARCHAR(64) PRIMARY KEY,
    hypothesis_id VARCHAR(64) REFERENCES PLACEBO_HYPOTHESIS_LEDGER(hypothesis_id),
    verdict_grade VARCHAR(32) NOT NULL,
    confidence VARCHAR(16) NOT NULL,
    raw_p_value FLOAT,
    adjusted_p_value FLOAT,
    effect_size FLOAT,
    evidence_package VARIANT NOT NULL,
    audited_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
