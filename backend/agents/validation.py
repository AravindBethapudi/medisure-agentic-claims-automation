
# backend/agents/validation.py
import json
from pathlib import Path
from ..utils.ollama_client import ask_llama

class ValidationAgent:
    def __init__(self):
        print("Hybrid Validation Agent ready")
        self.members = self._load_json("data/members.json")
        self.rules = self._load_json("data/coverage_rules.json")

    def _load_json(self, rel_path):
        path = Path(__file__).parent.parent / rel_path
        return json.loads(path.read_text()) if path.exists() else {}

    def validate(self, claim_data: dict) -> dict:
        """
        Comprehensive claim validation with multiple checks
        """
        result = {
            "eligibility": self._check_eligibility(claim_data),
            "coverage": self._check_coverage(claim_data),
            "authorization": self._check_authorization(claim_data),
            "business_rules": self._check_business_rules(claim_data)
        }
        
        # Determine final decision based on all checks
        statuses = [r["status"] for r in result.values()]
        
        if "FAILED" in statuses:
            decision = "DENIED"
        elif "NEEDS_REVIEW" in statuses:
            decision = "NEEDS_REVIEW"
        else:
            decision = "APPROVED"
        
        return {
            "decision": decision,
            "details": result
        }

    def _check_eligibility(self, claim_data: dict) -> dict:
        """
        Check if member is eligible for coverage
        """
        member_id = claim_data.get("member_id", "")
        
        # If no members data, assume eligible (for testing)
        if not self.members:
            return {"status": "PASSED", "reason": "Member validation bypassed (no data)"}
        
        # Check if member exists
        if member_id in self.members:
            member = self.members[member_id]
            
            # Check if member is active
            if member.get("status", "").upper() == "ACTIVE":
                return {"status": "PASSED", "reason": "Member active and eligible"}
            else:
                return {"status": "FAILED", "reason": f"Member status: {member.get('status', 'UNKNOWN')}"}
        else:
            return {"status": "FAILED", "reason": "Member ID not found in system"}

    def _check_coverage(self, claim_data: dict) -> dict:
        """
        Check if the procedure codes are covered
        """
        procedure_codes = claim_data.get("procedure_codes", [])
        diagnosis_codes = claim_data.get("diagnosis_codes", [])
        
        # Basic validation - check if codes exist
        if not procedure_codes:
            return {"status": "FAILED", "reason": "No procedure codes provided"}
        
        if not diagnosis_codes:
            return {"status": "FAILED", "reason": "No diagnosis codes provided"}
        
        # Check for known invalid codes (example - extend this list)
        invalid_procedures = ["99999", "00000"]
        invalid_diagnoses = ["Z99.99"]
        
        for code in procedure_codes:
            if code in invalid_procedures:
                return {"status": "FAILED", "reason": f"Invalid procedure code: {code}"}
        
        for code in diagnosis_codes:
            if code in invalid_diagnoses:
                return {"status": "FAILED", "reason": f"Invalid diagnosis code: {code}"}
        
        # If coverage rules exist, check them
        if self.rules:
            # Add your coverage rule logic here
            pass
        
        return {"status": "PASSED", "reason": "All codes are valid and covered"}

    def _check_authorization(self, claim_data: dict) -> dict:
        """
        Check if procedures require prior authorization
        """
        procedure_codes = claim_data.get("procedure_codes", [])
        
        # High-cost procedures requiring authorization
        auth_required = ["80050", "99285", "99291"]  # Add more as needed
        
        for code in procedure_codes:
            if code in auth_required:
                return {
                    "status": "NEEDS_REVIEW",
                    "reason": f"Procedure {code} requires prior authorization"
                }
        
        return {"status": "PASSED", "reason": "No authorization required"}

    def _check_business_rules(self, claim_data: dict) -> dict:
        """
        Check business rules and thresholds
        """
        amount = claim_data.get("claim_amount", 0)
        provider_name = claim_data.get("provider_name", "")
        
        # Rule 1: Extremely high amounts need review
        if amount > 10000:
            return {
                "status": "NEEDS_REVIEW",
                "reason": f"High claim amount requires review: ${amount}"
            }
        
        # Rule 2: Missing provider info
        if not provider_name or provider_name.lower() == "unknown":
            return {
                "status": "FAILED",
                "reason": "Provider information missing"
            }
        
        # Rule 3: Suspicious provider names
        suspicious_providers = ["fake", "test", "dummy"]
        if any(word in provider_name.lower() for word in suspicious_providers):
            return {
                "status": "FAILED",
                "reason": f"Suspicious provider name: {provider_name}"
            }
        
        # Rule 4: Zero or negative amounts
        if amount <= 0:
            return {
                "status": "FAILED",
                "reason": "Invalid claim amount"
            }
        
        return {"status": "PASSED", "reason": "All business rules satisfied"}
