"""
Step 3: Classification — Use LLM to classify the document type.
Classifies into: contract, invoice, report, or correspondence.
"""

from __future__ import annotations

import json
from typing import Any

from app.models import ClassificationResult, DocumentType, StepName
from app.llm.provider import LLMProvider
from app.llm.prompts import CLASSIFICATION_PROMPT
from app.tracing.tracer import traced, TraceContext


class _TracedResult(ClassificationResult):
    """ClassificationResult with trace metadata attached."""
    _trace_meta: dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


@traced(StepName.CLASSIFICATION)
async def classify_document(
    cleaned_text: str,
    entities_json: str,
    *,
    ctx: TraceContext,
    provider: LLMProvider,
) -> ClassificationResult:
    """
    Classify document type using LLM.
    Takes both the cleaned text and extracted entities for better classification.
    """
    prompt = CLASSIFICATION_PROMPT.format(
        document_text=cleaned_text[:4000],
        entities_json=entities_json[:2000],
    )

    llm_response = await provider.complete(prompt)
    data = llm_response.parse_json()

    # Parse document type safely
    doc_type_str = data.get("document_type", "unknown")
    try:
        doc_type = DocumentType(doc_type_str)
    except ValueError:
        doc_type = DocumentType.UNKNOWN

    # Parse alternative types
    alt_types = []
    for alt in data.get("alternative_types", []):
        try:
            alt_types.append(DocumentType(alt))
        except ValueError:
            continue

    result = _TracedResult(
        document_type=doc_type,
        classification_confidence=data.get("classification_confidence", 3),
        reasoning=data.get("reasoning", ""),
        alternative_types=alt_types,
    )

    result._trace_meta = {
        "prompt": prompt,
        "raw_response": llm_response.raw_response,
        "token_count": llm_response.token_count,
    }

    return result
