"""
Failure type taxonomy for root cause categorization.
Each failure type has a description, typical indicators, and severity.
"""

from __future__ import annotations

from app.models import FailureType


FAILURE_TAXONOMY = {
    FailureType.EXTRACTION_HALLUCINATION: {
        "name": "Extraction Hallucination",
        "description": "The extraction step produced entities that do not exist in the source document.",
        "indicators": [
            "Extracted names/dates/amounts not found in original text",
            "Confidence score for extraction is low",
            "Entity source_snippet doesn't match document content",
        ],
        "severity": "high",
        "typical_step": "extraction",
    },
    FailureType.MISCLASSIFICATION: {
        "name": "Misclassification",
        "description": "The document was classified into the wrong category.",
        "indicators": [
            "Classification confidence is low",
            "Alternative types listed have higher relevance",
            "Document keywords strongly suggest a different category",
        ],
        "severity": "high",
        "typical_step": "classification",
    },
    FailureType.PROPAGATION_ERROR: {
        "name": "Propagation Error",
        "description": "A step produced correct output, but the next step misinterpreted or misused it.",
        "indicators": [
            "Previous step output was reasonable",
            "Current step's interpretation of input is incorrect",
            "Information was distorted during handoff between steps",
        ],
        "severity": "medium",
        "typical_step": "any",
    },
    FailureType.PROMPT_FAILURE: {
        "name": "Prompt Failure",
        "description": "The LLM ignored instructions in the prompt.",
        "indicators": [
            "Output format doesn't match requested structure",
            "Required fields are missing from response",
            "Response addresses a different task than prompted",
        ],
        "severity": "medium",
        "typical_step": "any",
    },
    FailureType.CONTEXT_LOSS: {
        "name": "Context Loss",
        "description": "Important information from earlier steps was dropped or ignored.",
        "indicators": [
            "Key entities from extraction are missing in summary",
            "Document type context not reflected in summary format",
            "Critical details present in source but absent from output",
        ],
        "severity": "high",
        "typical_step": "summarization",
    },
}


def get_taxonomy_info(failure_type: FailureType) -> dict:
    """Get the full taxonomy entry for a failure type."""
    return FAILURE_TAXONOMY.get(failure_type, {
        "name": "Unknown",
        "description": "Failure type not categorized.",
        "indicators": [],
        "severity": "unknown",
        "typical_step": "unknown",
    })
