"""
Feedback Loop — Auto-generates eval cases from flagged traces.
When a human confirms a root cause diagnosis, the system creates a new test case
that gets added to a growing evaluation dataset.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

import aiosqlite

from app.database import get_db
from app.models import (
    EvalCase, FailureDiagnosis, FailureType, StepName, Trace
)
from app.tracing.store import load_trace


async def create_eval_case(
    trace_id: str,
    diagnosis: FailureDiagnosis,
    corrected_output: Optional[dict[str, Any]] = None,
    override_failure_type: Optional[FailureType] = None,
    override_step: Optional[StepName] = None,
) -> EvalCase:
    """
    Create a new eval case from a flagged trace and its diagnosis.
    
    This is triggered when a human:
    1. Flags a trace as "bad output"
    2. Reviews the automated diagnosis
    3. Confirms or overrides the root cause
    """
    trace = await load_trace(trace_id)
    if not trace:
        raise ValueError(f"Trace {trace_id} not found")

    failing_step = override_step or diagnosis.root_cause_step or StepName.SUMMARIZATION
    failure_type = override_failure_type or diagnosis.failure_type

    # Get the bad output from the failing step's span
    bad_output = {}
    for span in trace.spans:
        if span.step_name == failing_step:
            bad_output = span.output_data
            break

    original_input = ""
    if trace.input_document:
        original_input = trace.input_document.get("content", "")

    eval_case = EvalCase(
        trace_id=trace_id,
        original_input=original_input,
        failing_step=failing_step,
        bad_output=bad_output,
        corrected_output=corrected_output,
        failure_type=failure_type,
    )

    # Store in SQLite
    db = await get_db()
    try:
        await db.execute(
            """
            INSERT INTO eval_cases
            (eval_id, trace_id, failing_step, failure_type, original_input,
             bad_output, corrected_output, created_at, resolved, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eval_case.eval_id,
                eval_case.trace_id,
                eval_case.failing_step.value,
                eval_case.failure_type.value,
                eval_case.original_input[:5000],
                json.dumps(eval_case.bad_output, default=str),
                json.dumps(eval_case.corrected_output, default=str) if eval_case.corrected_output else None,
                eval_case.created_at.isoformat(),
                0,
                None,
            ),
        )
        await db.commit()
    finally:
        await db.close()

    return eval_case


async def get_eval_dataset() -> list[dict[str, Any]]:
    """Retrieve the complete eval dataset."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM eval_cases ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        cases = []
        for row in rows:
            case = dict(row)
            # Parse JSON fields
            try:
                case["bad_output"] = json.loads(case.get("bad_output", "{}"))
            except (json.JSONDecodeError, TypeError):
                case["bad_output"] = {}
            try:
                case["corrected_output"] = json.loads(case.get("corrected_output", "null"))
            except (json.JSONDecodeError, TypeError):
                case["corrected_output"] = None
            cases.append(case)
        return cases
    finally:
        await db.close()


async def mark_eval_case_resolved(eval_id: str) -> bool:
    """Mark an eval case as resolved."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE eval_cases SET resolved = 1, resolved_at = ? WHERE eval_id = ?",
            (datetime.utcnow().isoformat(), eval_id),
        )
        await db.commit()
        return True
    finally:
        await db.close()


async def get_eval_stats() -> dict[str, Any]:
    """Get eval dataset statistics."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT COUNT(*) FROM eval_cases")
        total = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT COUNT(*) FROM eval_cases WHERE resolved = 1")
        resolved = (await cursor.fetchone())[0]

        cursor = await db.execute(
            "SELECT failure_type, COUNT(*) FROM eval_cases GROUP BY failure_type"
        )
        by_type = dict(await cursor.fetchall())

        cursor = await db.execute(
            "SELECT failing_step, COUNT(*) FROM eval_cases GROUP BY failing_step"
        )
        by_step = dict(await cursor.fetchall())

        return {
            "total": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "by_failure_type": by_type,
            "by_failing_step": by_step,
        }
    finally:
        await db.close()
