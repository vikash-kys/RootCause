"""
Backward Trace Analyzer — walks backward through pipeline spans to identify
the root cause of failures using LLM-as-judge scoring.

For each step, asks: "Is this step's output a reasonable transformation of its input?"
The first step with a significant quality drop is identified as the root cause.
"""

from __future__ import annotations

import json
from typing import Optional

from app.models import (
    Trace, FailureDiagnosis, StepDiagnosis, FailureType, StepName, Span
)
from app.llm.provider import LLMProvider, get_provider
from app.llm.prompts import JUDGE_PROMPT
from app.analysis.taxonomy import get_taxonomy_info
from app.analysis.evidence import build_evidence_chain
from app.tracing.store import load_trace, update_trace_failure_type


async def analyze_trace(trace_id: str, provider: LLMProvider | None = None) -> FailureDiagnosis:
    """
    Perform backward trace analysis to identify the root cause of a failure.

    Algorithm:
    1. Load the complete trace
    2. Walk backward through spans (step 4 → step 1)
    3. For each step, use LLM-as-judge to score output quality
    4. Identify the first step with a significant quality drop
    5. Categorize the failure type
    6. Build an evidence chain
    """
    if provider is None:
        provider = get_provider()

    trace = await load_trace(trace_id)
    if not trace:
        return FailureDiagnosis(
            trace_id=trace_id,
            summary="Trace not found.",
        )

    # Get original document text
    original_doc = ""
    if trace.input_document:
        original_doc = trace.input_document.get("content", "")

    # Walk backward through spans
    step_diagnoses: list[StepDiagnosis] = []
    root_cause_step: Optional[StepName] = None
    root_cause_type = FailureType.NONE

    # Process spans in reverse order (summarization → classification → extraction → intake)
    reversed_spans = list(reversed(trace.spans))

    for span in reversed_spans:
        diagnosis = await _judge_step(span, original_doc, provider)
        step_diagnoses.append(diagnosis)

        # Check for significant quality drop
        if diagnosis.quality_score < 0.5 and root_cause_step is None:
            root_cause_step = span.step_name
            root_cause_type = diagnosis.failure_type
            diagnosis.is_root_cause = True

    # If no clear root cause found, check for low-confidence steps
    if root_cause_step is None:
        for diag in step_diagnoses:
            if diag.quality_score < 0.7:
                diag.is_root_cause = True
                root_cause_step = diag.step_name
                root_cause_type = diag.failure_type
                break

    # Re-order diagnoses in pipeline order
    step_order = {StepName.INTAKE: 0, StepName.EXTRACTION: 1, StepName.CLASSIFICATION: 2, StepName.SUMMARIZATION: 3}
    step_diagnoses.sort(key=lambda d: step_order.get(d.step_name, 99))

    # Build evidence chain
    evidence_chain = build_evidence_chain(step_diagnoses, original_doc)

    # Create summary
    if root_cause_step:
        taxonomy = get_taxonomy_info(root_cause_type)
        summary = (
            f"Root cause identified at {root_cause_step.value.title()} step. "
            f"Failure type: {taxonomy['name']}. "
            f"Severity: {taxonomy['severity']}."
        )
    else:
        summary = "No clear root cause identified. All steps produced reasonable outputs."

    # Update trace failure type in storage
    if root_cause_type != FailureType.NONE:
        await update_trace_failure_type(trace_id, root_cause_type)

    return FailureDiagnosis(
        trace_id=trace_id,
        root_cause_step=root_cause_step,
        failure_type=root_cause_type,
        step_diagnoses=step_diagnoses,
        evidence_chain=evidence_chain,
        summary=summary,
    )


async def _judge_step(span: Span, original_doc: str, provider: LLMProvider) -> StepDiagnosis:
    """Use LLM-as-judge to evaluate a single step's quality."""

    # Skip intake step — it's deterministic, not LLM-powered
    if span.step_name == StepName.INTAKE:
        return StepDiagnosis(
            step_name=span.step_name,
            quality_score=1.0 if not span.error else 0.0,
            failure_type=FailureType.NONE,
            explanation="Intake is a deterministic text processing step.",
        )

    # Prepare judge prompt
    prompt = JUDGE_PROMPT.format(
        step_name=span.step_name.value,
        step_input=json.dumps(span.input_data, default=str)[:2000],
        step_output=json.dumps(span.output_data, default=str)[:2000],
        original_document=original_doc[:3000],
    )

    try:
        response = await provider.complete(prompt)
        data = response.parse_json()

        quality_score = float(data.get("quality_score", 0.9))
        failure_type_str = data.get("failure_type", "none")

        try:
            failure_type = FailureType(failure_type_str)
        except ValueError:
            failure_type = FailureType.NONE

        return StepDiagnosis(
            step_name=span.step_name,
            quality_score=quality_score,
            failure_type=failure_type if quality_score < 0.7 else FailureType.NONE,
            explanation=data.get("explanation", ""),
            evidence=data.get("evidence", ""),
        )

    except Exception as e:
        # If judge fails, use confidence score as a fallback
        conf_score = span.confidence_score / 5.0
        return StepDiagnosis(
            step_name=span.step_name,
            quality_score=conf_score,
            failure_type=FailureType.NONE,
            explanation=f"Judge evaluation failed: {str(e)}. Using confidence fallback.",
        )
