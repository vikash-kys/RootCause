"""
Pipeline Runner — Orchestrates the 4-step document processing pipeline.
Manages the trace lifecycle: creates a Trace, runs all steps, handles errors,
and saves the complete trace.
"""

from __future__ import annotations

import json
import traceback
from datetime import datetime

from app.models import (
    RawDocument, Trace, TraceStatus, FailureType,
    IntakeResult, ExtractionResult, ClassificationResult, SummaryResult,
)
from app.llm.provider import LLMProvider, get_provider
from app.tracing.tracer import TraceContext
from app.tracing.store import save_trace
from app.pipeline.intake import process_intake
from app.pipeline.extraction import extract_entities
from app.pipeline.classification import classify_document
from app.pipeline.summarization import summarize_document


async def run_pipeline(document: RawDocument, provider: LLMProvider | None = None) -> Trace:
    """
    Execute the full 4-step pipeline on a document.

    Steps:
      1. Intake — clean and normalize text
      2. Extraction — extract structured entities
      3. Classification — classify document type
      4. Summarization — generate tailored summary

    Returns the complete Trace with all spans.
    """
    if provider is None:
        provider = get_provider()

    # Create trace
    trace = Trace(
        input_document=document.model_dump(),
        created_at=datetime.utcnow(),
    )
    ctx = TraceContext(trace)

    try:
        # Step 1: Intake
        intake_result: IntakeResult = await process_intake(
            document.content, ctx=ctx
        )

        # Step 2: Extraction
        extraction_result: ExtractionResult = await extract_entities(
            intake_result.cleaned_text, ctx=ctx, provider=provider
        )

        # Step 3: Classification
        entities_json = json.dumps({
            "persons": extraction_result.persons,
            "organizations": extraction_result.organizations,
            "dates": extraction_result.dates,
            "amounts": extraction_result.amounts,
            "key_terms": extraction_result.key_terms,
        })

        classification_result: ClassificationResult = await classify_document(
            intake_result.cleaned_text, entities_json, ctx=ctx, provider=provider
        )

        # Step 4: Summarization
        summary_result: SummaryResult = await summarize_document(
            intake_result.cleaned_text,
            classification_result.document_type.value,
            entities_json,
            ctx=ctx,
            provider=provider,
        )

        # Complete the trace
        final_output = {
            "intake": intake_result.model_dump(),
            "extraction": extraction_result.model_dump(),
            "classification": classification_result.model_dump(),
            "summary": summary_result.model_dump(),
        }
        ctx.complete(final_output)

    except Exception as e:
        ctx.fail(f"{type(e).__name__}: {str(e)}")
        trace.final_output = {"error": str(e), "traceback": traceback.format_exc()}

    # Save the trace
    await save_trace(trace)

    return trace


async def run_batch(documents: list[RawDocument], provider: LLMProvider | None = None) -> list[Trace]:
    """Run the pipeline on multiple documents sequentially."""
    if provider is None:
        provider = get_provider()

    traces = []
    for doc in documents:
        trace = await run_pipeline(doc, provider)
        traces.append(trace)

    return traces
