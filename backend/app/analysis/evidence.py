"""
Evidence chain builder — produces structured explanations of failure root causes.
Creates human-readable evidence chains with specific input/output pairs.
"""

from __future__ import annotations

from app.models import StepDiagnosis, FailureType, Span, StepName
from app.analysis.taxonomy import get_taxonomy_info


def build_evidence_chain(
    step_diagnoses: list[StepDiagnosis],
    original_text: str,
) -> str:
    """
    Build a human-readable evidence chain from step diagnoses.

    Example output:
    "Step 2 (Extraction) hallucinated the entity 'John Smith' which does not
    appear in the source document. This propagated to Step 4, which included
    it in the summary."
    """
    root_cause = None
    affected_steps = []

    for diag in step_diagnoses:
        if diag.is_root_cause:
            root_cause = diag
        elif diag.quality_score < 0.7:
            affected_steps.append(diag)

    if not root_cause:
        return "No root cause identified. All steps appear to have produced reasonable outputs."

    step_number = {
        StepName.INTAKE: 1,
        StepName.EXTRACTION: 2,
        StepName.CLASSIFICATION: 3,
        StepName.SUMMARIZATION: 4,
    }

    taxonomy = get_taxonomy_info(root_cause.failure_type)

    # Build the chain
    parts = []

    # Root cause description
    num = step_number.get(root_cause.step_name, "?")
    parts.append(
        f"**Root Cause: Step {num} ({root_cause.step_name.value.title()})**\n"
        f"Failure Type: {taxonomy['name']} (Severity: {taxonomy['severity']})\n"
        f"{root_cause.explanation}"
    )

    if root_cause.evidence:
        parts.append(f"\n**Evidence:** {root_cause.evidence}")

    # Propagation effects
    if affected_steps:
        parts.append("\n**Propagation Effects:**")
        for step in affected_steps:
            snum = step_number.get(step.step_name, "?")
            parts.append(
                f"- Step {snum} ({step.step_name.value.title()}): "
                f"Quality dropped to {step.quality_score:.0%}. {step.explanation}"
            )

    return "\n".join(parts)


def format_span_evidence(span: Span) -> dict:
    """Format a span's input/output as structured evidence."""
    return {
        "step": span.step_name.value,
        "input_preview": _truncate(str(span.input_data), 500),
        "output_preview": _truncate(str(span.output_data), 500),
        "prompt_preview": _truncate(span.prompt_sent, 500),
        "confidence": span.confidence_score,
        "latency_ms": span.latency_ms,
        "error": span.error,
    }


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."
