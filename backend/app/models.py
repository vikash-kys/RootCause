"""
Pydantic models for every data structure in the RootCause pipeline.
Every intermediate stage has a typed model, making traces meaningful and serializable.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Enums ────────────────────────────────────────────────────────────────────

class DocumentType(str, Enum):
    CONTRACT = "contract"
    INVOICE = "invoice"
    REPORT = "report"
    CORRESPONDENCE = "correspondence"
    UNKNOWN = "unknown"


class TraceStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DEGRADED = "degraded"
    RUNNING = "running"


class FailureType(str, Enum):
    EXTRACTION_HALLUCINATION = "extraction_hallucination"
    MISCLASSIFICATION = "misclassification"
    PROPAGATION_ERROR = "propagation_error"
    PROMPT_FAILURE = "prompt_failure"
    CONTEXT_LOSS = "context_loss"
    NONE = "none"


class StepName(str, Enum):
    INTAKE = "intake"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"


# ─── Pipeline Data Models ─────────────────────────────────────────────────────

class RawDocument(BaseModel):
    """Input to Step 1 (Intake)."""
    content: str = Field(..., description="Raw document text")
    source: str = Field(default="manual", description="Where this document came from")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntakeResult(BaseModel):
    """Output of Step 1 (Intake)."""
    cleaned_text: str = Field(..., description="Normalized, cleaned text")
    char_count: int = Field(..., description="Character count after cleaning")
    word_count: int = Field(..., description="Word count after cleaning")
    language: str = Field(default="en")
    quality_flags: list[str] = Field(default_factory=list, description="Issues detected during intake")


class ExtractedEntity(BaseModel):
    """A single extracted entity."""
    entity_type: str = Field(..., description="Type: person, organization, date, amount, key_term")
    value: str = Field(..., description="The extracted value")
    confidence: float = Field(default=1.0, ge=0, le=1)
    source_snippet: str = Field(default="", description="Surrounding text where entity was found")


class ExtractionResult(BaseModel):
    """Output of Step 2 (Extraction)."""
    entities: list[ExtractedEntity] = Field(default_factory=list)
    persons: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)
    key_terms: list[str] = Field(default_factory=list)
    extraction_confidence: int = Field(default=3, ge=1, le=5, description="Self-assessed confidence 1-5")


class ClassificationResult(BaseModel):
    """Output of Step 3 (Classification)."""
    document_type: DocumentType = Field(..., description="Classified document type")
    classification_confidence: int = Field(default=3, ge=1, le=5, description="Self-assessed confidence 1-5")
    reasoning: str = Field(default="", description="Why this classification was chosen")
    alternative_types: list[DocumentType] = Field(default_factory=list)


class SummaryResult(BaseModel):
    """Output of Step 4 (Summarization)."""
    summary: str = Field(..., description="Structured summary tailored to document type")
    key_points: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    summarization_confidence: int = Field(default=3, ge=1, le=5, description="Self-assessed confidence 1-5")


# ─── Tracing Models ──────────────────────────────────────────────────────────

class Span(BaseModel):
    """A single traced step in the pipeline."""
    span_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    step_name: StepName
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    prompt_sent: str = Field(default="")
    llm_raw_response: str = Field(default="")
    token_count: int = Field(default=0)
    latency_ms: float = Field(default=0.0)
    confidence_score: int = Field(default=3, ge=1, le=5)
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: str = Field(default="success")


class Trace(BaseModel):
    """A complete pipeline execution trace."""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    spans: list[Span] = Field(default_factory=list)
    status: TraceStatus = Field(default=TraceStatus.RUNNING)
    final_output: Optional[dict[str, Any]] = None
    final_score: Optional[float] = None
    failure_type: FailureType = Field(default=FailureType.NONE)
    input_document: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    flagged: bool = Field(default=False)
    flag_reason: str = Field(default="")


# ─── Analysis Models ─────────────────────────────────────────────────────────

class StepDiagnosis(BaseModel):
    """Diagnosis for a single step."""
    step_name: StepName
    quality_score: float = Field(ge=0, le=1, description="Quality of transformation 0-1")
    is_root_cause: bool = Field(default=False)
    failure_type: FailureType = Field(default=FailureType.NONE)
    explanation: str = Field(default="")
    evidence: str = Field(default="", description="Specific input/output evidence")


class FailureDiagnosis(BaseModel):
    """Complete root cause analysis for a failed trace."""
    trace_id: str
    root_cause_step: Optional[StepName] = None
    failure_type: FailureType = Field(default=FailureType.NONE)
    step_diagnoses: list[StepDiagnosis] = Field(default_factory=list)
    evidence_chain: str = Field(default="", description="Human-readable evidence chain")
    summary: str = Field(default="")
    diagnosed_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Feedback / Eval Models ──────────────────────────────────────────────────

class EvalCase(BaseModel):
    """A test case generated from human feedback."""
    eval_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(..., description="Original trace that generated this case")
    original_input: str = Field(..., description="The input document text")
    failing_step: StepName
    bad_output: dict[str, Any] = Field(default_factory=dict)
    corrected_output: Optional[dict[str, Any]] = None
    failure_type: FailureType
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None


class RegressionResult(BaseModel):
    """Result of running the eval dataset against the current pipeline."""
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    total_cases: int = 0
    still_failing: int = 0
    resolved: int = 0
    new_failures: int = 0
    results: list[dict[str, Any]] = Field(default_factory=list)
    run_at: datetime = Field(default_factory=datetime.utcnow)


# ─── API Request/Response Models ─────────────────────────────────────────────

class RunPipelineRequest(BaseModel):
    content: str
    source: str = "manual"
    metadata: dict[str, Any] = Field(default_factory=dict)


class BatchRunRequest(BaseModel):
    documents: list[RunPipelineRequest]


class FlagTraceRequest(BaseModel):
    reason: str = ""


class ConfirmDiagnosisRequest(BaseModel):
    confirmed: bool = True
    corrected_output: Optional[dict[str, Any]] = None
    override_failure_type: Optional[FailureType] = None
    override_root_cause_step: Optional[StepName] = None


class AnalyticsResponse(BaseModel):
    total_traces: int = 0
    failure_count: int = 0
    success_count: int = 0
    degraded_count: int = 0
    failure_rate: float = 0.0
    failure_by_type: dict[str, int] = Field(default_factory=dict)
    failure_by_step: dict[str, int] = Field(default_factory=dict)
    avg_latency_ms: float = 0.0
    avg_confidence: float = 0.0
    eval_dataset_size: int = 0
    resolved_issues: int = 0


class TrendPoint(BaseModel):
    date: str
    total: int = 0
    failures: int = 0
    failure_rate: float = 0.0


class TrendResponse(BaseModel):
    trends: list[TrendPoint] = Field(default_factory=list)
