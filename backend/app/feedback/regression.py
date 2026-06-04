"""
Regression tracking — re-runs the accumulated eval dataset against the current
pipeline and tracks whether known failure cases are still failing or have been fixed.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.database import get_db
from app.models import (
    RawDocument, RegressionResult, StepName
)
from app.llm.provider import LLMProvider, get_provider
from app.pipeline.runner import run_pipeline
from app.feedback.loop import get_eval_dataset, mark_eval_case_resolved


async def run_regression(provider: LLMProvider | None = None) -> RegressionResult:
    """
    Re-run all eval cases against the current pipeline.
    Compares new outputs against known bad outputs to detect regressions or fixes.
    """
    if provider is None:
        provider = get_provider()

    eval_cases = await get_eval_dataset()
    
    result = RegressionResult(
        total_cases=len(eval_cases),
    )

    for case in eval_cases:
        original_input = case.get("original_input", "")
        if not original_input:
            continue

        try:
            # Re-run the pipeline
            doc = RawDocument(content=original_input, source="regression_test")
            trace = await run_pipeline(doc, provider)

            # Check if the failing step still fails
            failing_step = case.get("failing_step", "")
            was_resolved = case.get("resolved", 0)

            # Find the relevant span
            step_output = {}
            for span in trace.spans:
                if span.step_name.value == failing_step:
                    step_output = span.output_data
                    break

            # Compare with known bad output
            bad_output = case.get("bad_output", {})
            still_failing = _outputs_similar(step_output, bad_output)

            case_result = {
                "eval_id": case.get("eval_id", ""),
                "trace_id": trace.trace_id,
                "failing_step": failing_step,
                "still_failing": still_failing,
                "new_output": step_output,
                "status": trace.status.value,
            }

            if still_failing:
                result.still_failing += 1
            else:
                result.resolved += 1
                # Auto-mark as resolved if it was unresolved
                if not was_resolved:
                    eval_id = case.get("eval_id")
                    if eval_id:
                        await mark_eval_case_resolved(eval_id)

            result.results.append(case_result)

        except Exception as e:
            result.results.append({
                "eval_id": case.get("eval_id", ""),
                "error": str(e),
                "still_failing": True,
            })
            result.still_failing += 1

    # Store regression run
    db = await get_db()
    try:
        await db.execute(
            """
            INSERT INTO regression_runs
            (run_id, total_cases, still_failing, resolved, new_failures, run_at, results)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.run_id,
                result.total_cases,
                result.still_failing,
                result.resolved,
                result.new_failures,
                result.run_at.isoformat(),
                json.dumps(result.results, default=str),
            ),
        )
        await db.commit()
    finally:
        await db.close()

    return result


def _outputs_similar(output_a: dict, output_b: dict) -> bool:
    """
    Check if two outputs are similar enough to be considered 'the same failure'.
    Uses a simple string comparison heuristic.
    """
    str_a = json.dumps(output_a, sort_keys=True, default=str)
    str_b = json.dumps(output_b, sort_keys=True, default=str)

    if str_a == str_b:
        return True

    # Check for high overlap using character-level comparison
    if not str_a or not str_b:
        return False

    set_a = set(str_a.split())
    set_b = set(str_b.split())
    if not set_a or not set_b:
        return False

    overlap = len(set_a & set_b) / max(len(set_a), len(set_b))
    return overlap > 0.8


async def get_regression_history() -> list[dict[str, Any]]:
    """Get past regression run summaries."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT run_id, total_cases, still_failing, resolved, new_failures, run_at FROM regression_runs ORDER BY run_at DESC LIMIT 20"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()
