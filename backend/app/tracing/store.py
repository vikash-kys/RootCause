"""
Trace storage: writes complete traces as JSON files and indexes metadata in SQLite.
Provides both human-readable trace files and queryable metadata.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import aiosqlite

from app.database import get_db, DATABASE_DIR
from app.models import Trace, TraceStatus, FailureType

TRACES_DIR = DATABASE_DIR / "traces"


async def save_trace(trace: Trace) -> str:
    """
    Save a complete trace to both JSON file and SQLite index.
    Returns the trace_id.
    """
    TRACES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Write JSON file
    trace_data = trace.model_dump(mode="json")
    trace_file = TRACES_DIR / f"{trace.trace_id}.json"
    with open(trace_file, "w", encoding="utf-8") as f:
        json.dump(trace_data, f, indent=2, default=str)

    # 2. Index in SQLite
    db = await get_db()
    try:
        # Compute aggregates
        total_latency = sum(s.latency_ms for s in trace.spans)
        avg_confidence = (
            sum(s.confidence_score for s in trace.spans) / len(trace.spans)
            if trace.spans else 0
        )
        input_preview = ""
        if trace.input_document:
            content = trace.input_document.get("content", "")
            input_preview = content[:200] if content else ""

        await db.execute(
            """
            INSERT OR REPLACE INTO traces
            (trace_id, status, final_score, failure_type, input_preview,
             created_at, completed_at, flagged, flag_reason,
             total_latency_ms, avg_confidence, step_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace.trace_id,
                trace.status.value,
                trace.final_score,
                trace.failure_type.value,
                input_preview,
                trace.created_at.isoformat(),
                trace.completed_at.isoformat() if trace.completed_at else None,
                1 if trace.flagged else 0,
                trace.flag_reason,
                total_latency,
                avg_confidence,
                len(trace.spans),
            ),
        )
        await db.commit()
    finally:
        await db.close()

    return trace.trace_id


async def load_trace(trace_id: str) -> Optional[Trace]:
    """Load a complete trace from its JSON file."""
    trace_file = TRACES_DIR / f"{trace_id}.json"
    if not trace_file.exists():
        return None

    with open(trace_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return Trace.model_validate(data)


async def update_trace_flag(trace_id: str, flagged: bool, reason: str = "") -> bool:
    """Update the flagged status of a trace."""
    # Update JSON file
    trace = await load_trace(trace_id)
    if not trace:
        return False

    trace.flagged = flagged
    trace.flag_reason = reason
    await save_trace(trace)
    return True


async def update_trace_failure_type(trace_id: str, failure_type: FailureType) -> bool:
    """Update the failure type of a trace."""
    trace = await load_trace(trace_id)
    if not trace:
        return False

    trace.failure_type = failure_type
    await save_trace(trace)
    return True


async def list_traces(
    status: Optional[str] = None,
    flagged: Optional[bool] = None,
    failure_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List traces from the SQLite index with optional filters."""
    db = await get_db()
    try:
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        if flagged is not None:
            conditions.append("flagged = ?")
            params.append(1 if flagged else 0)
        if failure_type:
            conditions.append("failure_type = ?")
            params.append(failure_type)

        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT * FROM traces{where} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def get_trace_count(
    status: Optional[str] = None,
    flagged: Optional[bool] = None,
) -> int:
    """Get count of traces matching filters."""
    db = await get_db()
    try:
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        if flagged is not None:
            conditions.append("flagged = ?")
            params.append(1 if flagged else 0)

        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT COUNT(*) FROM traces{where}"

        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
        return row[0] if row else 0
    finally:
        await db.close()


async def get_analytics_data() -> dict[str, Any]:
    """Get aggregated analytics from the traces database."""
    db = await get_db()
    try:
        # Total counts by status
        cursor = await db.execute("SELECT status, COUNT(*) FROM traces GROUP BY status")
        status_counts = dict(await cursor.fetchall())

        total = sum(status_counts.values())
        failures = status_counts.get("failure", 0)
        successes = status_counts.get("success", 0)
        degraded = status_counts.get("degraded", 0)

        # Failure by type
        cursor = await db.execute(
            "SELECT failure_type, COUNT(*) FROM traces WHERE failure_type != 'none' GROUP BY failure_type"
        )
        failure_by_type = dict(await cursor.fetchall())

        # Average latency and confidence
        cursor = await db.execute(
            "SELECT AVG(total_latency_ms), AVG(avg_confidence) FROM traces WHERE status != 'running'"
        )
        row = await cursor.fetchone()
        avg_latency = row[0] or 0
        avg_confidence = row[1] or 0

        # Eval dataset size
        cursor = await db.execute("SELECT COUNT(*) FROM eval_cases")
        eval_size = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM eval_cases WHERE resolved = 1")
        resolved = (await cursor.fetchone())[0]

        return {
            "total_traces": total,
            "failure_count": failures,
            "success_count": successes,
            "degraded_count": degraded,
            "failure_rate": failures / total if total > 0 else 0,
            "failure_by_type": failure_by_type,
            "failure_by_step": {},  # Will be populated from trace files
            "avg_latency_ms": round(avg_latency, 2),
            "avg_confidence": round(avg_confidence, 2),
            "eval_dataset_size": eval_size,
            "resolved_issues": resolved,
        }
    finally:
        await db.close()


async def get_trend_data(days: int = 30) -> list[dict[str, Any]]:
    """Get daily trend data for failure rates."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT
                DATE(created_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) as failures
            FROM traces
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT ?
            """,
            (days,)
        )
        rows = await cursor.fetchall()
        trends = []
        for row in rows:
            total = row[1]
            failures = row[2]
            trends.append({
                "date": row[0],
                "total": total,
                "failures": failures,
                "failure_rate": failures / total if total > 0 else 0,
            })
        return list(reversed(trends))
    finally:
        await db.close()
