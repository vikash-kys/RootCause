"""
Step 4: Summarization — Generate a structured summary tailored to the document type.
The summary format adapts based on whether the document is a contract, invoice, report, or correspondence.
"""

from __future__ import annotations

import json
from typing import Any

from app.models import SummaryResult, StepName
from app.llm.provider import LLMProvider
from app.llm.prompts import SUMMARIZATION_PROMPT
from app.tracing.tracer import traced, TraceContext


class _TracedResult(SummaryResult):
    """SummaryResult with trace metadata attached."""
    _trace_meta: dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


@traced(StepName.SUMMARIZATION)
async def summarize_document(
    cleaned_text: str,
    document_type: str,
    entities_json: str,
    *,
    ctx: TraceContext,
    provider: LLMProvider,
) -> SummaryResult:
    """
    Generate a structured summary tailored to the document type.
    Uses document type context to produce relevant key points and action items.
    """
    prompt = SUMMARIZATION_PROMPT.format(
        document_text=cleaned_text[:4000],
        document_type=document_type,
        entities_json=entities_json[:2000],
    )

    llm_response = await provider.complete(prompt)
    data = llm_response.parse_json()

    result = _TracedResult(
        summary=data.get("summary", "Unable to generate summary."),
        key_points=data.get("key_points", []),
        action_items=data.get("action_items", []),
        summarization_confidence=data.get("summarization_confidence", 3),
    )

    result._trace_meta = {
        "prompt": prompt,
        "raw_response": llm_response.raw_response,
        "token_count": llm_response.token_count,
    }

    return result
