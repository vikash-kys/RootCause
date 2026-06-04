"""
REST API routes for the RootCause platform.
All endpoints for pipeline execution, trace viewing, flagging, analysis, and feedback.
"""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import (
    RawDocument, RunPipelineRequest, BatchRunRequest,
    FlagTraceRequest, ConfirmDiagnosisRequest,
    AnalyticsResponse, TrendResponse,
)
from app.llm.provider import get_provider
from app.pipeline.runner import run_pipeline, run_batch
from app.tracing.store import (
    load_trace, list_traces, save_trace,
    update_trace_flag, get_analytics_data, get_trend_data,
)
from app.analysis.analyzer import analyze_trace
from app.analysis.taxonomy import FAILURE_TAXONOMY
from app.feedback.loop import (
    create_eval_case, get_eval_dataset, get_eval_stats,
)
from app.feedback.regression import run_regression, get_regression_history
from app.demo.documents import get_demo_documents

router = APIRouter(prefix="/api")


# ─── Pipeline Execution ──────────────────────────────────────────────────────

@router.post("/pipeline/run")
async def api_run_pipeline(request: RunPipelineRequest):
    """Execute the 4-step pipeline on a single document."""
    provider = get_provider()
    document = RawDocument(
        content=request.content,
        source=request.source,
        metadata=request.metadata,
    )
    trace = await run_pipeline(document, provider)
    return trace.model_dump(mode="json")


@router.post("/pipeline/run-batch")
async def api_run_batch(request: BatchRunRequest):
    """Execute the pipeline on multiple documents."""
    provider = get_provider()
    documents = [
        RawDocument(content=d.content, source=d.source, metadata=d.metadata)
        for d in request.documents
    ]
    traces = await run_batch(documents, provider)
    return {
        "total": len(traces),
        "traces": [t.model_dump(mode="json") for t in traces],
    }


@router.post("/pipeline/run-demo")
async def api_run_demo():
    """Run the pipeline on all 50 demo documents."""
    provider = get_provider()
    documents = get_demo_documents()
    traces = await run_batch(documents, provider)
    return {
        "total": len(traces),
        "success": sum(1 for t in traces if t.status.value == "success"),
        "degraded": sum(1 for t in traces if t.status.value == "degraded"),
        "failure": sum(1 for t in traces if t.status.value == "failure"),
        "traces": [
            {
                "trace_id": t.trace_id,
                "status": t.status.value,
                "final_score": t.final_score,
                "source": t.input_document.get("source", "") if t.input_document else "",
            }
            for t in traces
        ],
    }


# ─── Trace Viewing ───────────────────────────────────────────────────────────

@router.get("/traces")
async def api_list_traces(
    status: Optional[str] = Query(None, description="Filter by status"),
    flagged: Optional[bool] = Query(None, description="Filter by flagged status"),
    failure_type: Optional[str] = Query(None, description="Filter by failure type"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List all traces with optional filtering."""
    traces = await list_traces(
        status=status,
        flagged=flagged,
        failure_type=failure_type,
        limit=limit,
        offset=offset,
    )
    return {"traces": traces, "count": len(traces)}


@router.get("/traces/{trace_id}")
async def api_get_trace(trace_id: str):
    """Get full trace details including all spans."""
    trace = await load_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace.model_dump(mode="json")


# ─── Flagging & Diagnosis ────────────────────────────────────────────────────

@router.post("/traces/{trace_id}/flag")
async def api_flag_trace(trace_id: str, request: FlagTraceRequest):
    """Flag a trace as having bad output."""
    success = await update_trace_flag(trace_id, True, request.reason)
    if not success:
        raise HTTPException(status_code=404, detail="Trace not found")

    # Automatically run diagnosis
    provider = get_provider()
    diagnosis = await analyze_trace(trace_id, provider)

    return {
        "flagged": True,
        "diagnosis": diagnosis.model_dump(mode="json"),
    }


@router.get("/traces/{trace_id}/diagnosis")
async def api_get_diagnosis(trace_id: str):
    """Get or compute root cause analysis for a trace."""
    trace = await load_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    provider = get_provider()
    diagnosis = await analyze_trace(trace_id, provider)
    return diagnosis.model_dump(mode="json")


@router.post("/traces/{trace_id}/confirm")
async def api_confirm_diagnosis(trace_id: str, request: ConfirmDiagnosisRequest):
    """
    Confirm or override a diagnosis and create an eval case.
    This is the key action that feeds the feedback-to-eval loop.
    """
    trace = await load_trace(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    # Get diagnosis
    provider = get_provider()
    diagnosis = await analyze_trace(trace_id, provider)

    # Create eval case
    eval_case = await create_eval_case(
        trace_id=trace_id,
        diagnosis=diagnosis,
        corrected_output=request.corrected_output,
        override_failure_type=request.override_failure_type,
        override_step=request.override_root_cause_step,
    )

    return {
        "eval_case": eval_case.model_dump(mode="json"),
        "message": "Eval case created successfully. The evaluation dataset has grown.",
    }


# ─── Eval Dataset ────────────────────────────────────────────────────────────

@router.get("/eval/dataset")
async def api_get_eval_dataset():
    """Get the complete eval dataset."""
    dataset = await get_eval_dataset()
    stats = await get_eval_stats()
    return {
        "cases": dataset,
        "stats": stats,
    }


@router.post("/eval/run")
async def api_run_regression():
    """Run regression tests against the eval dataset."""
    provider = get_provider()
    result = await run_regression(provider)
    return result.model_dump(mode="json")


@router.get("/eval/history")
async def api_get_regression_history():
    """Get history of regression runs."""
    history = await get_regression_history()
    return {"runs": history}


# ─── Analytics ────────────────────────────────────────────────────────────────

@router.get("/analytics")
async def api_get_analytics():
    """Get failure analytics dashboard data."""
    data = await get_analytics_data()
    return data


@router.get("/analytics/trends")
async def api_get_trends(days: int = Query(30, ge=1, le=365)):
    """Get failure rate trend data."""
    trends = await get_trend_data(days)
    return {"trends": trends}


@router.get("/analytics/taxonomy")
async def api_get_taxonomy():
    """Get the failure type taxonomy."""
    taxonomy = {}
    for ft, info in FAILURE_TAXONOMY.items():
        taxonomy[ft.value] = info
    return {"taxonomy": taxonomy}
