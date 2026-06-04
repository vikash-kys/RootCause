"""
SQLite database initialization and connection management.
Stores trace metadata for fast querying; full traces live in JSON files.
"""

import aiosqlite
import os
from pathlib import Path

DATABASE_DIR = Path(__file__).parent.parent / "data"
DATABASE_PATH = DATABASE_DIR / "failure_forensics.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS traces (
    trace_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'running',
    final_score REAL,
    failure_type TEXT DEFAULT 'none',
    input_preview TEXT DEFAULT '',
    created_at TEXT NOT NULL,
    completed_at TEXT,
    flagged INTEGER DEFAULT 0,
    flag_reason TEXT DEFAULT '',
    total_latency_ms REAL DEFAULT 0,
    avg_confidence REAL DEFAULT 0,
    step_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS eval_cases (
    eval_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    failing_step TEXT NOT NULL,
    failure_type TEXT NOT NULL,
    original_input TEXT NOT NULL,
    bad_output TEXT DEFAULT '{}',
    corrected_output TEXT,
    created_at TEXT NOT NULL,
    resolved INTEGER DEFAULT 0,
    resolved_at TEXT,
    FOREIGN KEY (trace_id) REFERENCES traces (trace_id)
);

CREATE TABLE IF NOT EXISTS regression_runs (
    run_id TEXT PRIMARY KEY,
    total_cases INTEGER DEFAULT 0,
    still_failing INTEGER DEFAULT 0,
    resolved INTEGER DEFAULT 0,
    new_failures INTEGER DEFAULT 0,
    run_at TEXT NOT NULL,
    results TEXT DEFAULT '[]'
);

CREATE INDEX IF NOT EXISTS idx_traces_status ON traces(status);
CREATE INDEX IF NOT EXISTS idx_traces_created ON traces(created_at);
CREATE INDEX IF NOT EXISTS idx_traces_flagged ON traces(flagged);
CREATE INDEX IF NOT EXISTS idx_traces_failure_type ON traces(failure_type);
CREATE INDEX IF NOT EXISTS idx_eval_cases_trace ON eval_cases(trace_id);
CREATE INDEX IF NOT EXISTS idx_eval_cases_step ON eval_cases(failing_step);
"""


async def get_db() -> aiosqlite.Connection:
    """Get a database connection. Creates the database and tables if they don't exist."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(DATABASE_PATH))
    db.row_factory = aiosqlite.Row
    await db.executescript(SCHEMA)
    await db.commit()
    return db


async def init_db():
    """Initialize the database on startup."""
    db = await get_db()
    await db.close()
