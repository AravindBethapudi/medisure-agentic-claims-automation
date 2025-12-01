from typing import Dict, Any
import json
import os
from pathlib import Path

class ValidationAgent:
    """
    Validates claims against eligibility, coverage, and business rules.
    Now loads data from JSON files instead of hardcoded values.
    """
    
    def __init__(self, members_file=None, rules_file=None):
        print("🔧 Initializing Validation Agent...")

        BASE_DIR = os.path.dirname(os.path.dirname(__file__))

        if members_file is None:
            members_file = os.path.join(BASE_DIR, "data", "members.json")

        if rules_file is None:
            rules_file = os.path.join(BASE_DIR, "data", "coverage_rules.json")

        # Load members database
        if os.path.exists(members_file):
            with open(members_file, 'r') as f:
                self.members = json.load(f)
            print(f"✅ Loaded {len(self.members)} members from {members_file}")
        else:
            print(f"⚠️ Members file not found: {members_file}")
            self.members = {}

        # Load coverage rules
        if os.path.exists(rules_file):
            with open(rules_file, 'r') as f:
                rules = json.load(f)
                self.plans = rules.get("plans", {})
                self.requires_auth = rules.get("authorization_required", [])
                self.global_rules = rules.get("global_rules", {})
            print(f"✅ Loaded coverage rules from {rules_file}")
        else:
            print(f"⚠️ Rules file not found: {rules_file}")
            self.plans = {}
            self.requires_auth = []
            self.global_rules = {}

        print("✅ Validation Agent ready")

    
    def validate(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation function.
        Returns validation results with decision.
        """
        validation_results = {
            "eligibility": self._check_eligibility(claim_data),
            "coverage": self._check_coverage(claim_data),
            "authorization": self._check_authorization(claim_data),
            "business_rules": self._check_business_rules(claim_data)
        }
        
        # Make final decision
        decision = self._make_decision(validation_results)
        
        return {
            "decision": decision,
            "validation_results": validation_results,
            "message": self._generate_message(decision, validation_results)
        }
    
    def _check_eligibility(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if member is eligible."""
        patient = claim_data.get("patient", {})
        member_id = patient.get("member_id")
        
        if not member_id:
            return {
                "status": "FAILED",
                "reason": "Missing member ID"
            }
        
        member = self.members.get(member_id)
        
        if not member:
            return {
                "status": "FAILED",
                "reason": f"Member {member_id} not found in system"
            }
        
        if member["status"] != "active":
            return {
                "status": "FAILED",
                "reason": f"Member status is {member['status']}, must be active"
            }
        
        return {
            "status": "PASSED",
            "member_name": member.get("name"),
            "member_status": member["status"],
            "plan": member["plan"]
        }
    
    def _check_coverage(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if procedures are covered under member's plan."""
        # First get member's plan
        eligibility = self._check_eligibility(claim_data)
        if eligibility["status"] == "FAILED":
            return {
                "status": "FAILED",
                "reason": "Cannot check coverage - eligibility failed"
            }
        
        plan = eligibility["plan"]
        procedure_codes = claim_data.get("procedure_codes", [])
        
        if not procedure_codes:
            return {
                "status": "FAILED",
                "reason": "No procedure codes provided"
            }
        
        # Get covered procedures for this plan
        plan_info = self.plans.get(plan, {})
        covered_procs = plan_info.get("covered_procedures", [])
        
        uncovered = []
        for proc in procedure_codes:
            if proc not in covered_procs:
                uncovered.append(proc)
        
        if uncovered:
            return {
                "status": "FAILED",
                "reason": f"Procedures not covered under {plan} plan: {', '.join(uncovered)}",
                "uncovered_procedures": uncovered
            }
        
        return {
            "status": "PASSED",
            "plan": plan,
            "covered_procedures": procedure_codes,
            "copay": plan_info.get("copay", 0)
        }
    
    def _check_authorization(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if procedures require prior authorization."""
        procedure_codes = claim_data.get("procedure_codes", [])
        
        needs_auth = []
        for proc in procedure_codes:
            if proc in self.requires_auth:
                needs_auth.append(proc)
        
        if needs_auth:
            return {
                "status": "NEEDS_REVIEW",
                "reason": f"Procedures require prior authorization: {', '.join(needs_auth)}",
                "procedures_needing_auth": needs_auth
            }
        
        return {
            "status": "PASSED",
            "reason": "No prior authorization required"
        }
    
    def _check_business_rules(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules (amount thresholds, etc.)."""
        total_amount = claim_data.get("total_amount", 0)
        max_auto_approve = self.global_rules.get("max_amount_auto_approve", 1000.0)
        
        if total_amount > max_auto_approve:
            return {
                "status": "NEEDS_REVIEW",
                "reason": f"Amount ${total_amount} exceeds auto-approval threshold of ${max_auto_approve}"
            }
        
        return {
            "status": "PASSED",
            "reason": "All business rules passed"
        }
    
    def _make_decision(self, validation_results: Dict[str, Any]) -> str:
        """
        Make final decision based on all validation checks.
        
        Logic:
        - If any check FAILED → DENIED
        - If any check NEEDS_REVIEW → NEEDS_REVIEW
        - If all checks PASSED → APPROVED
        """
        statuses = [
            validation_results["eligibility"]["status"],
            validation_results["coverage"]["status"],
            validation_results["authorization"]["status"],
            validation_results["business_rules"]["status"]
        ]
        
        if "FAILED" in statuses:
            return "DENIED"
        
        if "NEEDS_REVIEW" in statuses:
            return "NEEDS_REVIEW"
        
        return "APPROVED"
    
    def _generate_message(self, decision: str, validation_results: Dict[str, Any]) -> str:
        """Generate human-readable message."""
        if decision == "APPROVED":
            return "Claim approved. All validation checks passed."
        
        if decision == "DENIED":
            reasons = []
            for check, result in validation_results.items():
                if result["status"] == "FAILED":
                    reasons.append(result["reason"])
            return f"Claim denied. Reasons: {'; '.join(reasons)}"
        
        if decision == "NEEDS_REVIEW":
            reasons = []
            for check, result in validation_results.items():
                if result["status"] == "NEEDS_REVIEW":
                    reasons.append(result["reason"])
            return f"Claim requires manual review. Reasons: {'; '.join(reasons)}"
        
        return "Unknown decision"


# Test the agent
if __name__ == "__main__":
    print("\n🚀 Testing Validation Agent (with JSON data)...\n")
    
    agent = ValidationAgent()
    
    # Test Case 1: Valid claim
    print("=" * 50)
    print("TEST 1: Valid Claim (PREMIUM member)")
    print("=" * 50)
    test_claim_1 = {
        "claim_id": "CLM-001",
        "patient": {"member_id": "M12345678"},
        "procedure_codes": ["99213"],
        "diagnosis_codes": ["J10.1"],
        "total_amount": 150.0
    }
    
    result = agent.validate(test_claim_1)
    print(f"Decision: {result['decision']}")
    print(f"Message: {result['message']}")
    print(f"Eligibility: {result['validation_results']['eligibility']}\n")
    
    # Test Case 2: Inactive member
    print("=" * 50)
    print("TEST 2: Inactive Member")
    print("=" * 50)
    test_claim_2 = {
        "patient": {"member_id": "M98765432"},
        "procedure_codes": ["99213"],
        "total_amount": 150.0
    }
    
    result = agent.validate(test_claim_2)
    print(f"Decision: {result['decision']}")
    print(f"Message: {result['message']}\n")
    
    # Test Case 3: Needs authorization
    print("=" * 50)
    print("TEST 3: Requires Prior Authorization")
    print("=" * 50)
    test_claim_3 = {
        "patient": {"member_id": "M12345678"},
        "procedure_codes": ["99213", "80050"],
        "total_amount": 430.0
    }
    
    result = agent.validate(test_claim_3)
    print(f"Decision: {result['decision']}")
    print(f"Message: {result['message']}\n")
    
    # Test Case 4: BASIC plan, uncovered procedure
    print("=" * 50)
    print("TEST 4: Uncovered Procedure (BASIC plan)")
    print("=" * 50)
    test_claim_4 = {
        "patient": {"member_id": "M11111111"},
        "procedure_codes": ["99213", "80050"],
        "total_amount": 300.0
    }
    
    result = agent.validate(test_claim_4)
    print(f"Decision: {result['decision']}")
    print(f"Message: {result['message']}\n")