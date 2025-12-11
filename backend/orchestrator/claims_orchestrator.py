# backend/orchestrator/claims_orchestrator.py - WITH MONITORING
from typing import TypedDict, Annotated, List, Dict, Any
import operator

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.extraction import ExtractionAgent
from backend.agents.rag import RAGAgent
from backend.agents.validation import ValidationAgent
from backend.agents.fraud import FraudDetectionAgent
from backend.agents.summarization import SummarizationAgent
from backend.utils.monitoring import monitor


# === 1. Define the shared state ===
class ClaimState(TypedDict):
    file_bytes: bytes
    content_type: str
    filename: str
    
    extracted: Dict[str, Any]
    policies: List[Dict[str, Any]]
    validation: Dict[str, Any]
    fraud: Dict[str, Any]
    final_decision: Dict[str, Any]
    summary: Dict[str, Any]
    
    messages: Annotated[List[str], operator.add]
    tracking: Dict[str, Any]  # For monitoring


# === 2. Initialize agents ===
extractor = ExtractionAgent()
rag = RAGAgent()
validator = ValidationAgent()
fraud_detector = FraudDetectionAgent()
summarizer = SummarizationAgent()


# === 3. Define monitored nodes ===
def extract_node(state: ClaimState) -> ClaimState:
    print("Step 1: Extracting claim data...")
    with monitor.track_agent(state["tracking"], "extraction"):
        extracted = extractor.extract(state["file_bytes"], state["content_type"], state["filename"])
    return {"extracted": extracted, "messages": ["Extraction complete"]}

def retrieve_node(state: ClaimState) -> ClaimState:
    print("Step 2: Retrieving relevant policies...")
    with monitor.track_agent(state["tracking"], "rag"):
        policies = rag.retrieve(state["extracted"])
    return {"policies": policies, "messages": ["Policy retrieval complete"]}

def validate_node(state: ClaimState) -> ClaimState:
    print("Step 3: Validating eligibility & coverage...")
    with monitor.track_agent(state["tracking"], "validation"):
        validation = validator.validate(state["extracted"])
    return {"validation": validation, "messages": ["Validation complete"]}

def fraud_node(state: ClaimState) -> ClaimState:
    print("Step 4: Running fraud detection...")
    with monitor.track_agent(state["tracking"], "fraud"):
        fraud = fraud_detector.detect(state["extracted"])
    return {"fraud": fraud, "messages": ["Fraud check complete"]}

def decide_node(state: ClaimState) -> ClaimState:
    print("Step 5: Making final decision...")
    with monitor.track_agent(state["tracking"], "decision"):
        v_decision = state["validation"]["decision"]
        f_level = state["fraud"].get("risk_level", "LOW")

        # Decision logic with validation priority
        if v_decision == "DENIED":
            decision = {"decision": "REJECT", "reason": "Validation failed"}
        elif f_level == "HIGH":
            decision = {"decision": "REJECT", "reason": "High fraud risk - claim rejected"}
        elif f_level == "MEDIUM" or v_decision == "NEEDS_REVIEW":
            decision = {"decision": "MANUAL_REVIEW", "reason": "Requires manual review"}
        else:
            decision = {"decision": "APPROVE", "reason": "All clear"}

    return {"final_decision": decision, "messages": ["Decision made"]}

def summarize_node(state: ClaimState) -> ClaimState:
    print("Step 6: Generating beautiful summary...")
    with monitor.track_agent(state["tracking"], "summary"):
        summary = summarizer.summarize(
            extracted=state["extracted"],
            validation=state["validation"],
            policies=state["policies"],
            fraud=state["fraud"],
            final_decision=state["final_decision"]
        )
    return {"summary": summary, "messages": ["Summary ready"]}


# === 4. Build the workflow ===
workflow = StateGraph(ClaimState)

workflow.add_node("extract", extract_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("validate", validate_node)
workflow.add_node("fraud", fraud_node)
workflow.add_node("decide", decide_node)
workflow.add_node("summarize", summarize_node)

workflow.set_entry_point("extract")
workflow.add_edge("extract", "retrieve")
workflow.add_edge("retrieve", "validate")
workflow.add_edge("validate", "fraud")
workflow.add_edge("fraud", "decide")
workflow.add_edge("decide", "summarize")
workflow.add_edge("summarize", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


# === 5. Main entry point with monitoring ===
def process_claim(file_bytes: bytes, content_type: str, filename: str) -> Dict[str, Any]:
    """
    Process claim with full monitoring
    """
    claim_id = filename  # Use filename as claim ID
    tracking = monitor.start_claim(claim_id)
    
    inputs = {
        "file_bytes": file_bytes,
        "content_type": content_type,
        "filename": filename,
        "tracking": tracking
    }
    
    config = {"configurable": {"thread_id": "default"}}
    
    print("\nSTARTING LANGGRAPH MULTI-AGENT CLAIMS PROCESSING\n")
    
    try:
        result = app.invoke(inputs, config=config)
        
        print("\nLANGGRAPH PIPELINE COMPLETE\n")
        
        output = {
            "file_name": filename,
            "extracted": result["extracted"],
            "policies": result["policies"],
            "validation": result["validation"],
            "fraud": result["fraud"],
            "final_decision": result["final_decision"],
            "summary": result["summary"],
        }
        
        # Log successful completion
        monitor.complete_claim(tracking, output)
        
        return output
        
    except Exception as e:
        print(f"\n❌ ERROR PROCESSING CLAIM: {e}\n")
        # Log error
        monitor.complete_claim(tracking, {}, error=str(e))
        raise