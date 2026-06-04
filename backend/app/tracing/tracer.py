"""
Tracing decorator and context manager for pipeline steps.
Wraps each step to automatically capture inputs, outputs, prompts, latency, and confidence.
Instrumenting a new step is a single @traced decorator.
"""

from __future__ import annotations

import functools
import time
import json
import traceback
from datetime import datetime
from typing import Any, Callable, Optional

from app.models import Span, StepName, Trace, TraceStatus


class TraceContext:
    """
    Manages the lifecycle of a single pipeline trace.
    Collects spans from each step and produces a complete Trace object.
    """

    def __init__(self, trace: Trace):
        self.trace = trace
        self._current_span: Optional[Span] = None

    def start_span(self, step_name: StepName, input_data: dict[str, Any]) -> Span:
        """Begin a new span for a pipeline step."""
        span = Span(
            step_name=step_name,
            input_data=input_data,
            started_at=datetime.utcnow(),
        )
        self._current_span = span
        return span

    def end_span(
        self,
        span: Span,
        output_data: dict[str, Any],
        prompt: str = "",
        raw_response: str = "",
        token_count: int = 0,
        confidence_score: int = 3,
        error: Optional[str] = None,
    ):
        """Complete a span with its results."""
        span.output_data = output_data
        span.prompt_sent = prompt
        span.llm_raw_response = raw_response
        span.token_count = token_count
        span.confidence_score = confidence_score
        span.ended_at = datetime.utcnow()
        span.latency_ms = (span.ended_at - span.started_at).total_seconds() * 1000
        span.error = error
        span.status = "error" if error else "success"
        self.trace.spans.append(span)
        self._current_span = None

    def complete(self, final_output: dict[str, Any], status: TraceStatus = TraceStatus.SUCCESS):
        """Mark the trace as complete."""
        self.trace.final_output = final_output
        self.trace.status = status
        self.trace.completed_at = datetime.utcnow()

        # Compute final score as average confidence
        if self.trace.spans:
            self.trace.final_score = sum(s.confidence_score for s in self.trace.spans) / len(self.trace.spans)

        # Auto-detect degraded status from low confidence spans
        if status == TraceStatus.SUCCESS and self.trace.spans:
            low_conf = any(s.confidence_score <= 2 for s in self.trace.spans)
            has_error = any(s.error for s in self.trace.spans)
            if has_error:
                self.trace.status = TraceStatus.FAILURE
            elif low_conf:
                self.trace.status = TraceStatus.DEGRADED

    def fail(self, error: str):
        """Mark the trace as failed."""
        self.trace.status = TraceStatus.FAILURE
        self.trace.completed_at = datetime.utcnow()
        if self.trace.spans:
            self.trace.final_score = sum(s.confidence_score for s in self.trace.spans) / len(self.trace.spans)


def traced(step_name: StepName):
    """
    Decorator that instruments a pipeline step with automatic tracing.

    Usage:
        @traced(StepName.EXTRACTION)
        async def extract(text: str, ctx: TraceContext, provider: LLMProvider) -> ExtractionResult:
            ...

    The decorated function must accept `ctx: TraceContext` as a keyword argument.
    The decorator automatically captures inputs, outputs, timing, and errors.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            ctx: TraceContext = kwargs.get("ctx")
            if ctx is None:
                raise ValueError(f"Traced function '{func.__name__}' requires 'ctx' keyword argument")

            # Serialize input for tracing
            input_data = {}
            for i, arg in enumerate(args):
                if hasattr(arg, "model_dump"):
                    input_data[f"arg_{i}"] = arg.model_dump()
                elif isinstance(arg, str):
                    input_data[f"arg_{i}"] = arg[:2000]  # Truncate long strings
                else:
                    try:
                        input_data[f"arg_{i}"] = json.loads(json.dumps(arg, default=str))
                    except (TypeError, ValueError):
                        input_data[f"arg_{i}"] = str(arg)[:2000]

            span = ctx.start_span(step_name, input_data)

            try:
                result = await func(*args, **kwargs)

                # Extract tracing metadata from result
                output_data = {}
                prompt = ""
                raw_response = ""
                token_count = 0
                confidence = 3

                if hasattr(result, "_trace_meta"):
                    meta = result._trace_meta
                    prompt = meta.get("prompt", "")
                    raw_response = meta.get("raw_response", "")
                    token_count = meta.get("token_count", 0)

                if hasattr(result, "model_dump"):
                    output_data = result.model_dump()
                    # Extract confidence from the result model
                    for field in ["extraction_confidence", "classification_confidence", "summarization_confidence"]:
                        if field in output_data:
                            confidence = output_data[field]
                            break
                else:
                    try:
                        output_data = json.loads(json.dumps(result, default=str))
                    except (TypeError, ValueError):
                        output_data = {"result": str(result)[:2000]}

                ctx.end_span(
                    span,
                    output_data=output_data,
                    prompt=prompt,
                    raw_response=raw_response,
                    token_count=token_count,
                    confidence_score=confidence,
                )

                return result

            except Exception as e:
                ctx.end_span(
                    span,
                    output_data={"error": str(e)},
                    error=f"{type(e).__name__}: {str(e)}",
                    confidence_score=1,
                )
                raise

        return wrapper
    return decorator
