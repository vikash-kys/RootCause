"""
Step 2: Extraction — Use LLM to extract structured entities from cleaned text.
Extracts persons, organizations, dates, amounts, and key terms with confidence scoring.
"""

from __future__ import annotations

import json
from typing import Any

from app.models import ExtractionResult, ExtractedEntity, StepName
from app.llm.provider import LLMProvider
from app.llm.prompts import EXTRACTION_PROMPT
from app.tracing.tracer import traced, TraceContext


class _TracedResult(ExtractionResult):
    """ExtractionResult with trace metadata attached."""
    _trace_meta: dict[str, Any] = {}

    class Config:
        arbitrary_types_allowed = True


@traced(StepName.EXTRACTION)
async def extract_entities(
    cleaned_text: str,
    *,
    ctx: TraceContext,
    provider: LLMProvider,
) -> ExtractionResult:
    """
    Extract structured entities from document text using LLM.
    Returns typed ExtractionResult with confidence scoring.
    """
    prompt = EXTRACTION_PROMPT.format(document_text=cleaned_text[:4000])

    llm_response = await provider.complete(prompt)
    data = llm_response.parse_json()

    # Build entity list
    entities = []
    for ent_data in data.get("entities", []):
        try:
            entities.append(ExtractedEntity(**ent_data))
        except Exception:
            continue

    result = _TracedResult(
        entities=entities,
        persons=data.get("persons", []),
        organizations=data.get("organizations", []),
        dates=data.get("dates", []),
        amounts=data.get("amounts", []),
        key_terms=data.get("key_terms", []),
        extraction_confidence=data.get("extraction_confidence", 3),
    )

    # Attach trace metadata
    result._trace_meta = {
        "prompt": prompt,
        "raw_response": llm_response.raw_response,
        "token_count": llm_response.token_count,
    }

    return result
