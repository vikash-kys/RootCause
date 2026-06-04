"""
Step 1: Intake — Accept raw document text, normalize, and detect quality issues.
This step runs without an LLM call; it's pure text processing.
"""

from __future__ import annotations

import re
import unicodedata

from app.models import IntakeResult, StepName
from app.tracing.tracer import traced, TraceContext


@traced(StepName.INTAKE)
async def process_intake(raw_text: str, *, ctx: TraceContext) -> IntakeResult:
    """
    Clean and normalize raw document text.
    Detects quality issues like encoding problems, excessive whitespace, or very short content.
    """
    cleaned = raw_text

    # Normalize unicode
    cleaned = unicodedata.normalize("NFKC", cleaned)

    # Fix common encoding artifacts
    replacements = {
        "\u2018": "'", "\u2019": "'",   # Smart quotes
        "\u201c": '"', "\u201d": '"',   # Smart double quotes
        "\u2013": "-", "\u2014": "--",  # En/em dashes
        "\u2026": "...",                # Ellipsis
        "\u00a0": " ",                  # Non-breaking space
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)

    # Normalize whitespace (preserve paragraph breaks)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)         # Collapse spaces/tabs
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)      # Max 2 newlines
    cleaned = cleaned.strip()

    # Detect quality issues
    quality_flags = []
    if len(cleaned) < 50:
        quality_flags.append("very_short_document")
    if len(cleaned) > 50000:
        quality_flags.append("very_long_document")
    if re.search(r'[^\x00-\x7F]', cleaned):
        quality_flags.append("contains_non_ascii")
    if not re.search(r'[.!?]', cleaned):
        quality_flags.append("no_sentence_endings")
    if re.search(r'(.)\1{5,}', cleaned):
        quality_flags.append("repeated_characters")

    words = cleaned.split()

    result = IntakeResult(
        cleaned_text=cleaned,
        char_count=len(cleaned),
        word_count=len(words),
        language="en",
        quality_flags=quality_flags,
    )

    return result
