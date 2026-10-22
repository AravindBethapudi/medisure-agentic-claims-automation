# MediSure Agentic Claims Automation

MediSure is a portfolio prototype that processes synthetic medical-claim files
through a traceable, multi-step decision workflow. It demonstrates how document
extraction, policy retrieval, validation, fraud-risk screening, decision routing,
summarization, and operational monitoring can be composed behind an API.

> **Synthetic data only.** This repository is not a production claims system,
> does not provide medical or coverage advice, and must not be used with real
> patient information or protected health information (PHI).

## What It Demonstrates

- A FastAPI service for JSON, XML, and text-based PDF claim uploads
- Rule-first field extraction with an optional local Ollama fallback
- Keyword-based retrieval from synthetic policy documents
- Eligibility, coverage, authorization, and business-rule checks
- Explainable fraud-risk flags and manual-review routing
- A LangGraph workflow that coordinates each processing stage
- A Streamlit dashboard for inspecting workflow results
- Aggregate processing metrics without logging raw claim content

## Processing Flow

```text
Synthetic JSON, XML, or PDF claim
  -> upload type and size validation
  -> structured field extraction
  -> synthetic policy retrieval
  -> eligibility and coverage validation
  -> fraud-risk screening
  -> approve, reject, or manual-review routing
  -> human-readable summary
  -> aggregate operational metrics
```

The current policy retrieval is keyword-based. The word "agent" refers to a
workflow component with one responsibility; it does not imply that every step
uses a large language model.

## Architecture

| Area | Responsibility |
| --- | --- |
| `backend/main.py` | HTTP boundary, upload validation, health, and metrics routes |
| `backend/orchestrator/` | LangGraph workflow and decision routing |
| `backend/agents/` | Extraction, retrieval, validation, fraud, and summary stages |
| `backend/utils/` | Local Ollama client, code descriptions, and safe monitoring |
| `streamlit_app/` | Interactive prototype dashboard |
| `tests/` | API, contract, privacy, and workflow-isolation checks |

## Technology

- Python
- FastAPI and Pydantic
- LangGraph
- Streamlit
- Ollama with `llama3.2:1b` for optional local inference
- Pytest
- Docker and Render configuration

## Run Locally

Python 3.11 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Start Ollama if you want to exercise the optional LLM fallback:

```bash
ollama serve
ollama pull llama3.2:1b
```

The rule-based path still works when Ollama is unavailable.

Start the API from the repository root:

```bash
uvicorn backend.main:app --reload --port 8000
```

Start the dashboard in another terminal:

```bash
BACKEND_URL=http://localhost:8000 streamlit run streamlit_app/app.py \
  --server.maxUploadSize 2
```

Then open `http://localhost:8501`. FastAPI documentation is available at
`http://localhost:8000/docs`.

## API Example

Use only a synthetic file from `test_claims/` or create your own fictional
example.

```bash
curl -X POST http://localhost:8000/process-claim \
  -F "file=@test_claims/TEST1.json;type=application/json"
```

Uploads are limited to 2 MB and must have a matching JSON, XML, or PDF media type
and extension. Unexpected processing failures return a generic message instead
of exposing document content or internal exception details.

## Tests

```bash
pytest
```

The tests cover:

- accepted synthetic JSON uploads
- empty, unsupported, and oversized upload rejection
- sanitized API failures
- removal of client-supplied path components
- frontend/backend response-field compatibility
- exclusion of raw input previews from extracted results
- isolated workflow identifiers for concurrent requests

The checked-in `accuracy_report.json` records three synthetic scenarios that
passed when the report was generated. It is a small functional smoke test, not
evidence of production accuracy or clinical validity.

## Live Status

- [API health](https://medisure-agentic-claims-automation.onrender.com/health)
- [Interactive API documentation](https://medisure-agentic-claims-automation.onrender.com/docs)

The public dashboard is not currently published. The API deployment may run
without a local Ollama process, in which case the deterministic rule-based path
continues and the optional LLM fallback is skipped.

## Security And Privacy Boundaries

Implemented prototype controls:

- explicit upload media types and extensions
- 2 MB request limit
- normalized filenames
- generic server-error responses
- explicit CORS origins rather than a wildcard
- generated monitoring IDs instead of uploaded filenames
- error-type logging without exception text
- no raw-text preview in API extraction results

Not yet implemented:

- authentication and authorization
- encryption and production secret management
- tenant isolation
- durable audit storage and retention controls
- malware scanning or OCR sandboxing
- production-grade policy and fraud models
- independent evaluation on a representative dataset
- compliance review for regulated use

These limitations are why the project accepts synthetic data only.

## Portfolio Summary

MediSure demonstrates a production-minded Python workflow for synthetic claims:
API design, multi-stage orchestration, deterministic controls, optional local
model integration, human-review routing, monitoring, deployment configuration,
and tests for unsafe input and failure paths.
