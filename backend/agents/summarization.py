from typing import Dict, Any

class SummarizationAgent:
    """
    Generates human-readable summaries of claim processing results.
    """
    
    def __init__(self):
        print("🔧 Initializing Summarization Agent...")
        
        # Decision emojis for visual clarity
        self.decision_icons = {
            "APPROVE": "✅",
            "APPROVED": "✅",
            "DENIED": "❌",
            "REJECT": "❌",
            "NEEDS_REVIEW": "⚠️",
            "MANUAL_REVIEW": "⚠️"
        }
        
        print("✅ Summarization Agent ready")
    
    def summarize(self, 
                  extracted_data: Dict[str, Any],
                  validation_result: Dict[str, Any],
                  policies: list,
                  final_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive summary of claim processing.
        Uses FINAL orchestrator decision instead of validation-only decision.
        """
        
        executive = self._generate_executive_summary(
            extracted_data,
            validation_result,
            final_decision
        )
        
        detailed = self._generate_detailed_summary(
            extracted_data,
            validation_result,
            policies,
            final_decision
        )

        action = self._generate_action_items(final_decision)

        return {
            "executive_summary": executive,
            "detailed_summary": detailed,
            "action_required": action,
            "summary_generated_at": self._get_timestamp()
        }
    
    def _generate_executive_summary(self, 
                                   extracted_data: Dict[str, Any],
                                   validation_result: Dict[str, Any],
                                   final_decision: Dict[str, Any]) -> str:
        """
        One-paragraph summary for quick review.
        Now uses FINAL decision (validation + fraud).
        """
        claim_id = extracted_data.get("claim_id", "N/A")
        patient = extracted_data.get("patient", {})
        patient_name = patient.get("name", "Unknown")
        member_id = patient.get("member_id", "N/A")
        
        amount = extracted_data.get("total_amount", 0)
        
        # FINAL decision replaces validation decision
        decision = final_decision.get("decision", "UNKNOWN")
        icon = self.decision_icons.get(decision, "❓")
        
        # Member plan
        eligibility = validation_result.get("validation_results", {}).get("eligibility", {})
        plan = eligibility.get("plan", "Unknown")

        message = final_decision.get("reason", validation_result.get("message", ""))

        summary = f"""
{icon} CLAIM {claim_id} — {decision}

Patient: {patient_name} (Member ID: {member_id})
Plan: {plan}
Total Amount: ${amount:.2f}

Decision: {decision}
{message}
        """.strip()
        
        return summary
    
    def _generate_detailed_summary(self,
                                  extracted_data: Dict[str, Any],
                                  validation_result: Dict[str, Any],
                                  policies: list,
                                  final_decision: Dict[str, Any]) -> str:
        """
        Detailed breakdown with all relevant information.
        Final decision replaces validation-only decision in summary footer.
        """
        claim_id = extracted_data.get("claim_id", "N/A")
        patient = extracted_data.get("patient", {})
        procedures = extracted_data.get("procedure_codes", [])
        diagnosis = extracted_data.get("diagnosis_codes", [])
        date_of_service = extracted_data.get("date_of_service", "N/A")
        
        validation_results = validation_result.get("validation_results", {})
        
        sections = []
        
        # Header
        sections.append("=" * 60)
        sections.append(f"DETAILED CLAIM SUMMARY - {claim_id}")
        sections.append("=" * 60)
        sections.append("")
        
        # Patient Information
        sections.append("PATIENT INFORMATION:")
        sections.append(f"  Name: {patient.get('name', 'N/A')}")
        sections.append(f"  Member ID: {patient.get('member_id', 'N/A')}")
        sections.append(f"  Service Date: {date_of_service}")
        sections.append("")
        
        # Clinical Information
        sections.append("CLINICAL INFORMATION:")
        sections.append(f"  Diagnosis Codes: {', '.join(diagnosis) if diagnosis else 'None'}")
        sections.append(f"  Procedure Codes: {', '.join(procedures) if procedures else 'None'}")
        sections.append(f"  Total Amount: ${extracted_data.get('total_amount', 0):.2f}")
        sections.append("")
        
        # Validation Results
        sections.append("VALIDATION RESULTS:")
        sections.append("")
        
        # Eligibility
        eligibility = validation_results.get("eligibility", {})
        status_icon = "✅" if eligibility.get("status") == "PASSED" else "❌"
        sections.append(f"  {status_icon} Eligibility: {eligibility.get('status', 'UNKNOWN')}")
        if eligibility.get("plan"):
            sections.append(f"     Plan: {eligibility['plan']}")
        if eligibility.get("reason"):
            sections.append(f"     Reason: {eligibility['reason']}")
        sections.append("")
        
        # Coverage
        coverage = validation_results.get("coverage", {})
        status_icon = "✅" if coverage.get("status") == "PASSED" else "❌"
        sections.append(f"  {status_icon} Coverage: {coverage.get('status', 'UNKNOWN')}")
        if coverage.get("reason"):
            sections.append(f"     Reason: {coverage['reason']}")
        if coverage.get("uncovered_procedures"):
            sections.append(f"     Uncovered: {', '.join(coverage['uncovered_procedures'])}")
        sections.append("")
        
        # Authorization
        auth = validation_results.get("authorization", {})
        status_icon = "⚠️" if auth.get("status") == "NEEDS_REVIEW" else "✅"
        sections.append(f"  {status_icon} Authorization: {auth.get('status', 'UNKNOWN')}")
        if auth.get("reason"):
            sections.append(f"     {auth['reason']}")
        if auth.get("procedures_needing_auth"):
            sections.append(f"     Requires Auth: {', '.join(auth['procedures_needing_auth'])}")
        sections.append("")
        
        # Business Rules
        rules = validation_results.get("business_rules", {})
        status_icon = "⚠️" if rules.get("status") == "NEEDS_REVIEW" else "✅"
        sections.append(f"  {status_icon} Business Rules: {rules.get('status', 'UNKNOWN')}")
        sections.append(f"     {rules.get('reason', 'N/A')}")
        sections.append("")
        
        # Policy References
        sections.append("RELEVANT POLICY DOCUMENTS:")
        for i, policy in enumerate(policies[:3], 1):
            sections.append(f"  {i}. {policy.get('source', 'Unknown')} (Relevance: {policy.get('relevance_score', 0):.0%})")
        sections.append("")
        
        # Final Decision (updated)
        decision = final_decision.get("decision", "UNKNOWN")
        icon = self.decision_icons.get(decision, "❓")
        sections.append("=" * 60)
        sections.append(f"FINAL DECISION: {icon} {decision}")
        sections.append("=" * 60)
        
        return "\n".join(sections)
    
    def _generate_action_items(self, final_decision: Dict[str, Any]) -> str:
        """
        Action items are now based on FINAL decision, not validation-only decision.
        """
        decision = final_decision.get("decision", "UNKNOWN")
        actions = []
        
        if decision in ["APPROVE", "APPROVED"]:
            actions.append("✅ No action required - Claim can be processed automatically.")
            actions.append("✅ Payment can be issued immediately.")
        
        elif decision in ["REJECT", "DENIED"]:
            actions.append("❌ Claim REJECTED.")
            actions.append(f"❌ Reason: {final_decision.get('reason', 'No reason provided')}")
        
        elif decision == "MANUAL_REVIEW":
            actions.append("⚠️ MANUAL REVIEW REQUIRED")
            actions.append(f"⚠️ Reason: {final_decision.get('reason', 'Review required')}")
            actions.append("")
            actions.append("Expected Review Time: 24–48 hours")
            actions.append("Assign to: Claims Review Team")
        
        return "\n".join(actions)
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
