from backend.agents.extraction import ExtractionAgent
from backend.agents.rag import RAGAgent
from backend.agents.validation import ValidationAgent
from backend.agents.fraud import FraudDetectionAgent
from backend.agents.summarization import SummarizationAgent


class ClaimsOrchestrator:

    def __init__(self):
        self.extractor = ExtractionAgent()
        self.rag = RAGAgent()
        self.validation = ValidationAgent()
        self.fraud = FraudDetectionAgent()
        self.summary = SummarizationAgent()

    def process_claim(self, file_bytes, content_type, filename):

        # Step 1 — Extract
        extracted = self.extractor.parse_claim(file_bytes, content_type)

        # Step 2 — RAG
        policies = self.rag.retrieve_policies(extracted, top_k=3)

        # Step 3 — Validation
        validation = self.validation.validate(extracted)

        # Step 4 — Fraud
        fraud = self.fraud.detect(extracted)

        # Step 5 — Final Decision
        final_decision = self.get_final_decision(validation, fraud)

        # Step 6 — Summary (needs final_decision)
        summary = self.summary.summarize(
            extracted_data=extracted,
            validation_result=validation,
            policies=policies,
            final_decision=final_decision
        )

        # Step 7 — Final Output
        return {
            "file_name": filename,
            "extracted": extracted,
            "policies": policies,
            "validation": validation,
            "fraud": fraud,
            "summary": summary,
            "final_decision": final_decision
        }

    def get_final_decision(self, validation, fraud):

        v_decision = validation.get("decision")
        f_level = fraud.get("risk_level", "MINIMAL")

        # High fraud risk → manual review
        if f_level == "HIGH":
            return {
                "decision": "MANUAL_REVIEW",
                "reason": "High fraud risk detected."
            }

        # Validation failure → reject
        if v_decision == "DENIED":
            return {
                "decision": "REJECT",
                "reason": validation.get("message", "Validation failed.")
            }

        # Validation needs review → manual review
        if v_decision == "NEEDS_REVIEW":
            return {
                "decision": "MANUAL_REVIEW",
                "reason": validation.get("message", "Manual review required.")
            }

        # All good
        return {
            "decision": "APPROVE",
            "reason": "All checks passed."
        }
