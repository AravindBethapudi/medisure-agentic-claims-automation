from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.orchestrator.claims_orchestrator import ClaimsOrchestrator


app = FastAPI(
    title="MediSure Agentic Claims API",
    version="1.0.0",
    description="Backend service for the MediSure Agentic Claims Automation System"
)

# Initialize Orchestrator (handles all agents)
orchestrator = ClaimsOrchestrator()

@app.get("/")
def root():
    return {
        "message": "Welcome to MediSure Agentic Claims API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "MediSure Claims API is running"}

@app.post("/process-claim")
async def process_claim(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        # 🔥 Single orchestrator call
        result = orchestrator.process_claim(file_bytes, file.content_type, file.filename)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
