# backend/main.py - WITH MONITORING
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from orchestrator.claims_orchestrator import process_claim as orchestrator_process_claim
from utils.monitoring import monitor

app = FastAPI(
    title="MediSure Agentic Claims API",
    version="1.0.0",
    description="Backend service for the MediSure Agentic Claims Automation System with Real-time Monitoring"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Welcome to MediSure Agentic Claims API",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "MediSure Claims API is running"}

@app.post("/process-claim")
async def process_claim_endpoint(file: UploadFile = File(...)):
    """
    Process a claim through the multi-agent pipeline
    """
    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # Process through orchestrator (now with monitoring)
        result = orchestrator_process_claim(file_bytes, file.content_type, file.filename)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/metrics/reset")
def reset_metrics():
    """
    Reset all metrics (useful for testing)
    """
    global monitor
    from utils.monitoring import ClaimsMonitor
    monitor = ClaimsMonitor()
    return {"message": "Metrics reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)