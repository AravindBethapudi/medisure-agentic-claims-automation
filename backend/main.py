"""FastAPI entry point for the synthetic MediSure claims prototype."""

import logging
import os
from pathlib import Path
import sys
from typing import Final, Optional

# Fix Python path for deployment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

# Try both import styles (works everywhere)
try:
    # For deployment (Render, etc.)
    from backend.orchestrator.claims_orchestrator import process_claim as orchestrator_process_claim
    from backend.utils.monitoring import monitor
except ImportError:
    # For local development
    from .orchestrator.claims_orchestrator import process_claim as orchestrator_process_claim
    from .utils.monitoring import monitor

app = FastAPI(
    title="MediSure Agentic Claims API",
    version="1.0.0",
    description=(
        "Portfolio prototype for processing synthetic medical-claim files. "
        "Do not submit real protected health information."
    ),
)

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES: Final = 2 * 1024 * 1024
ALLOWED_UPLOADS: Final = {
    "application/json": {".json"},
    "application/pdf": {".pdf"},
    "application/xml": {".xml"},
    "text/xml": {".xml"},
}


def configured_cors_origins() -> list[str]:
    """Return explicitly configured browser origins instead of a wildcard."""
    configured = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8501,http://127.0.0.1:8501",
    )
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


def safe_filename(filename: Optional[str]) -> str:
    """Strip client-supplied path components before using a filename."""
    normalized = (filename or "uploaded-claim").replace("\\", "/")
    return Path(normalized.rsplit("/", 1)[-1]).name[:255] or "uploaded-claim"


async def read_validated_upload(file: UploadFile) -> tuple[bytes, str]:
    """Validate an upload's declared type, extension, and size before processing."""
    filename = safe_filename(file.filename)
    content_type = (file.content_type or "").split(";", 1)[0].lower()
    allowed_extensions = ALLOWED_UPLOADS.get(content_type)

    if not allowed_extensions or Path(filename).suffix.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a JSON, XML, or PDF synthetic claim file.",
        )

    file_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="Uploaded file exceeds the 2 MB prototype limit.",
        )

    return file_bytes, filename


app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

@app.get("/")
def root():
    """Describe the prototype and its safe-use boundary."""
    return {
        "message": "Welcome to MediSure Agentic Claims API",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "version": "1.0.0",
        "data_policy": "Synthetic claim data only; do not submit real PHI.",
    }

@app.get("/health")
def health_check():
    """Report whether the API process is available."""
    return {"status": "ok", "message": "MediSure Claims API is running"}

@app.post("/process-claim")
async def process_claim_endpoint(file: UploadFile = File(...)):
    """Validate and process one synthetic claim through the workflow."""
    try:
        file_bytes, filename = await read_validated_upload(file)
        return orchestrator_process_claim(file_bytes, file.content_type or "", filename)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Synthetic claim processing failed: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Claim processing failed without exposing document content.",
        ) from None

@app.get("/metrics")
def get_metrics():
    """
    Get comprehensive system metrics
    """
    return monitor.get_metrics()

@app.get("/metrics/prometheus", response_class=PlainTextResponse)
def get_prometheus_metrics():
    """
    Get metrics in Prometheus format for monitoring tools
    """
    return monitor.get_prometheus_metrics()

@app.get("/metrics/summary")
def get_metrics_summary():
    """
    Get quick summary of key metrics
    """
    metrics = monitor.get_metrics()
    summary = metrics.get("summary", {})
    
    return {
        "total_claims": summary.get("total_claims", 0),
        "approval_rate": summary.get("approval_rate", 0),
        "avg_processing_time": summary.get("avg_processing_time", 0),
        "errors": summary.get("errors", 0)
    }

@app.get("/metrics/agents")
def get_agent_performance():
    """
    Get detailed agent performance metrics
    """
    metrics = monitor.get_metrics()
    return {
        "agent_performance": metrics.get("agent_performance", {}),
        "message": "Average processing time per agent in seconds"
    }

@app.get("/metrics/recent")
def get_recent_claims():
    """
    Get last 10 processed claims with timing details
    """
    metrics = monitor.get_metrics()
    return {
        "recent_claims": metrics.get("recent_claims", []),
        "count": len(metrics.get("recent_claims", []))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
