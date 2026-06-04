# Failure Forensics

**AI Pipeline Observability Tool** — Trace, diagnose, and learn from AI pipeline failures.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License: All Rights Reserved](https://img.shields.io/badge/License-All_Rights_Reserved-red?style=flat-square)](LICENSE)

---

## In Simple Words

### The Problem It Solves

Imagine you have an AI system that processes a document in **4 steps**:

`Raw Document → Clean It → Extract Key Info → Classify It → Summarize It`

When the final summary comes out **wrong**, you're stuck asking: *"Which step messed up?"*

Was it the extraction that hallucinated a name? Was the document classified as an invoice when it's actually a contract? Did the summary drop important details? **Nobody knows.** In most teams, someone manually reads every intermediate output trying to find the bug. This takes hours.

### What This Tool Does

Failure Forensics is like a **flight recorder (black box) for AI pipelines**. It:

1. **Records everything** — Every step logs what went in, what came out, what prompt was sent to the LLM, how confident the LLM was, and how long it took. This is called a **trace**.
2. **Finds the culprit automatically** — When output is bad, instead of you debugging manually, it walks **backward** through the steps and asks an LLM judge: *"Does this step's output make sense given its input?"* The first step where quality drops significantly is flagged as the **root cause**.
3. **Labels the failure** — It doesn't just say "step 2 broke." It tells you *how* it broke: Did it hallucinate data? Misclassify the document? Lose context? These categories help you know what to fix.
4. **Learns from mistakes** — Every time you confirm a failure, it saves that case as a **test**. Over time, you build a growing test suite of known failures. You can re-run these tests anytime to check if your pipeline is getting better or worse.

### The Goal

**Reduce debugging time from hours to seconds.**

Instead of manually inspecting every step, you click a button, and the tool tells you: *"Step 2 (Extraction) hallucinated the entity 'John Smith' which doesn't appear in the source document. This propagated to Step 4, which included it in the summary."*

### Why It Matters

This demonstrates that you understand:
- **AI systems break in non-obvious ways** — and you know how to make them observable
- **Observability tooling** — this is what companies like LangSmith, Braintrust, and Arize do
- **Production ML thinking** — not just building models, but building the infrastructure to monitor, debug, and improve them over time

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  Dashboard │ Trace Explorer │ Analytics │ Eval Dataset   │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────┴──────────────────────────────────┐
│                   FastAPI Backend                        │
│                                                          │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐  │
│  │ Pipeline  │  │  Tracing  │  │ Backward Trace       │  │
│  │ Engine    │──│  Layer    │──│ Analyzer (LLM Judge)  │  │
│  │ (4 steps) │  │ (@traced) │  │                      │  │
│  └──────────┘  └───────────┘  └──────────────────────┘  │
│                                                          │
│  ┌──────────────────────┐  ┌─────────────────────────┐  │
│  │ Feedback Loop        │  │ Regression Tracking     │  │
│  │ (eval case gen)      │  │ (automated re-runs)     │  │
│  └──────────────────────┘  └─────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │   SQLite + JSON Traces      │
        └─────────────────────────────┘
```

### Pipeline Steps

| Step | Name | Input | Output | LLM? |
|------|------|-------|--------|------|
| 1 | **Intake** | Raw text | Cleaned, normalized text | No |
| 2 | **Extraction** | Cleaned text | Persons, orgs, dates, amounts, key terms | Yes |
| 3 | **Classification** | Text + entities | Document type + confidence | Yes |
| 4 | **Summarization** | Text + type + entities | Structured summary + action items | Yes |

---

## How This System Is Designed for Integration

### The Core Pattern: A Decorator-Based Instrumentation Layer

The entire system is built around **one key idea** — you should be able to add observability to any pipeline step with **a single line of code**. Here's how:

### Step 1: You Have an Existing Pipeline

Say a client has their own AI pipeline — maybe it's a customer support bot, a document processor, a RAG system, whatever. It looks something like this:

```python
# Their existing code — no observability
async def extract(text):
    response = await llm.call("Extract entities from: " + text)
    return response

async def classify(text, entities):
    response = await llm.call("Classify this: " + text)
    return response
```

### Step 2: Wrap Each Step With `@traced`

To integrate Failure Forensics, they add our decorator — that's it:

```python
from app.tracing.tracer import traced, TraceContext
from app.models import StepName

@traced(StepName.EXTRACTION)        # ← this one line does everything
async def extract(text, *, ctx: TraceContext):
    response = await llm.call("Extract entities from: " + text)
    return response
```

The `@traced` decorator is a **context manager** that automatically:
- Starts a timer when the function is called
- Serializes the input arguments and output
- Captures the LLM prompt and raw response
- Records token count and confidence score
- Catches any exceptions
- Packages all of this into a **Span** object

The client **never writes tracing logic manually**. The decorator handles everything.

### Step 3: Use the Runner to Orchestrate

Instead of calling steps directly, the client uses our orchestrator which manages the **Trace lifecycle**:

```python
from app.pipeline.runner import run_pipeline
from app.models import RawDocument

# One call — runs all steps, traces everything, saves to DB
trace = await run_pipeline(RawDocument(content="some document text"))
```

### Step 4: The REST API Is the Integration Point

For clients who don't want to embed Python code, everything is exposed via a **REST API**. They can:

```
POST /api/pipeline/run          →  "Here's a document, process it"
GET  /api/traces                →  "Show me all pipeline runs"
GET  /api/traces/{id}           →  "Show me full details of this run"
POST /api/traces/{id}/flag      →  "This output was bad" → auto-diagnoses
POST /api/traces/{id}/confirm   →  "Your diagnosis is correct" → creates test case
GET  /api/analytics             →  "What's my overall failure picture?"
```

So a client could integrate this into their **existing dashboard**, their **Slack bot**, their **CI/CD pipeline** — anything that can make HTTP calls.

### Step 5: The Frontend Is Optional But Powerful

The React UI is a **standalone tool** the client's team uses to:
- Browse traces when things go wrong
- Click through the visual pipeline to inspect each step
- Flag bad outputs and review automated root cause analysis
- Build their eval dataset over time without writing test cases manually

### In Summary
The system is designed as a **drop-in instrumentation layer**. You define your pipeline steps as normal Python functions, add a `@traced` decorator to each one, and the system automatically captures full observability data. The REST API lets you integrate with existing tools. The frontend gives your team a visual debugger. And the feedback loop means every bug your team finds automatically becomes a regression test — so you get smarter over time without extra work.

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/failure-forensics.git
cd failure-forensics

# Start the full stack
docker-compose up --build

# Open http://localhost:8080
```

### Option 2: Manual Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Option 3: With Real API Key (OpenAI, Claude, Gemini, DeepSeek, etc.)

```bash
# Create .env from template
cp .env.example .env
# Edit .env and add your preferred provider's API key (e.g., OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.)

# Then run with Docker or manually
docker-compose up --build
```

---

## Demo Walkthrough

1. **Open the dashboard** at `http://localhost:8080`
2. **Click "Run Demo (50 docs)"** to process all sample documents
3. **Browse traces** — notice ~10 have degraded/failed status
4. **Click a failed trace** — see the animated pipeline visualization
5. **Click "Diagnose"** — watch the backward trace analyzer identify the root cause
6. **Click "Flag as Bad"** — triggers automatic root cause analysis
7. **Confirm the diagnosis** — creates an eval case in the growing test suite
8. **Check Analytics** — see failure type breakdown, step failure rates, trends
9. **Run Regression** — re-test known failures against the current pipeline

---

## Key Features

### Trace Explorer
Every pipeline execution is captured as a structured trace with full span details — inputs, outputs, LLM prompts, raw responses, token counts, latency, and self-assessed confidence scores.

### Backward Root Cause Analysis
When a trace is flagged, the system walks backward through spans using an LLM-as-judge to score each step's output quality. The first step with a significant quality drop is identified as the root cause.

### Failure Taxonomy
Failures are automatically categorized:
- **Extraction Hallucination** — entities that don't exist in the source
- **Misclassification** — wrong document type
- **Propagation Error** — correct output misinterpreted by next step
- **Prompt Failure** — LLM ignored instructions
- **Context Loss** — important information dropped

### Feedback-to-Eval Loop
Every confirmed diagnosis becomes a test case in a growing evaluation dataset. Run regression tests to track whether known failures are fixed or still present.

### Failure Analytics
Dashboard showing failure rates, most common failure types, which pipeline step fails most, and trends over time.

---

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Language | Python 3.11+ | Standard for ML tooling |
| API Framework | FastAPI | Async, typed, auto-documented |
| LLM Provider | Mock (default) / LiteLLM | Zero-config demo + universal API support (OpenAI, Claude, Gemini, DeepSeek, etc.) |
| Tracing | Custom `@traced` decorator | Single-line instrumentation |
| Storage | SQLite + JSON files | Inspectable, git-friendly |
| Frontend | React 18 + Vite | Fast, modern SPA |
| Styling | Vanilla CSS (dark theme) | Full control, no dependencies |
| Containerization | Docker + Compose | One-command deployment |

---

## Project Structure

```
failure-forensics/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes
│   │   ├── analysis/       # Backward trace analyzer + taxonomy
│   │   ├── demo/           # 50 sample documents
│   │   ├── feedback/       # Eval loop + regression tracking
│   │   ├── llm/            # Mock + Universal LiteLLM providers
│   │   ├── pipeline/       # 4-step processing pipeline
│   │   ├── tracing/        # @traced decorator + storage
│   │   ├── database.py     # SQLite setup
│   │   ├── main.py         # FastAPI entry point
│   │   └── models.py       # All Pydantic models
│   ├── data/               # Generated traces + eval dataset
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Shared UI components
│   │   ├── pages/          # Route pages
│   │   ├── api.js          # Backend API client
│   │   ├── App.jsx         # Root component + routing
│   │   └── index.css       # Design system
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

---

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Key Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/pipeline/run` | Process a single document |
| POST | `/api/pipeline/run-demo` | Process all 50 demo documents |
| GET | `/api/traces` | List traces with filtering |
| GET | `/api/traces/{id}` | Get full trace with spans |
| POST | `/api/traces/{id}/flag` | Flag + auto-diagnose |
| POST | `/api/traces/{id}/confirm` | Confirm diagnosis → create eval case |
| GET | `/api/analytics` | Failure analytics dashboard data |
| POST | `/api/eval/run` | Run regression tests |

---

## Design Decisions

1. **Mock LLM by default** — The project runs without any API key. A deterministic mock provider generates realistic responses with controlled failure injection. Same input always produces same output for reproducibility.

2. **Typed everything with Pydantic** — Every pipeline stage has a typed model. This makes traces meaningful and serializable, not spaghetti.

3. **`@traced` decorator pattern** — Instrumenting a new pipeline step is one line of code. The decorator automatically captures inputs, outputs, prompts, latency, and confidence.

4. **Backward analysis with LLM-as-judge** — Rather than just flagging the final output, the system walks backward to find the *first* step that went wrong. This is the key insight that makes debugging tractable.

5. **Feedback loop is automatic** — Confirming a diagnosis automatically creates a test case. No manual data entry required. The eval dataset grows organically from real failures.

---

## License

All Rights Reserved. This project is proprietary.
