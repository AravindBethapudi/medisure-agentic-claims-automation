from typing import Dict, Any, List
import json
import os
from datetime import datetime
from pathlib import Path


class FraudDetectionAgent:
    """
    Detects potential fraud patterns in claims.
    Uses configurable rules + mock historical data.
    """

    def __init__(self, rules_file: str | None = None):
        print("🔧 Initializing Fraud Detection Agent...")

        # ------------------------------------------------------------------
        # Resolve data/fraud_rules.json relative to backend/ directory
        # ------------------------------------------------------------------
        backend_dir = Path(__file__).resolve().parents[1]   # .../backend
        data_dir = backend_dir / "data"

        if rules_file is None:
            rules_path = data_dir / "fraud_rules.json"
        else:
            rules_path = Path(rules_file)

        # Load fraud rules
        if rules_path.exists():
            with open(rules_path, "r") as f:
                rules = json.load(f)
                self.thresholds = rules.get("risk_thresholds", {})
                self.red_flags = rules.get("red_flags", {})
                self.high_risk_providers = rules.get("high_risk_providers", [])
                self.suspicious_combos = rules.get(
                    "suspicious_procedure_combinations", []
                )
            print(f"✅ Loaded fraud rules from {rules_path}")
        else:
            print(f"⚠️ Fraud rules file not found: {rules_path}")
            self.thresholds = {"low": 0.3, "medium": 0.7, "high": 0.9}
            self.red_flags = {}
            self.high_risk_providers = []
            self.suspicious_combos = []

        # Mock historical claims database
        self.historical_claims = self._load_mock_history()
        print("✅ Fraud Detection Agent ready")

    # ------------------------------------------------------------------
    # MOCK HISTORY
    # ------------------------------------------------------------------
    def _load_mock_history(self) -> List[Dict[str, Any]]:
        """Mock historical claims (used for duplicate + pattern checks)."""
        return [
            {
                "claim_id": "CLM-OLD-001",
                "member_id": "M12345678",
                "procedure_codes": ["99213"],
                "total_amount": 150.0,
                "date_of_service": "2025-09-15",
                "provider_id": "PRV-9001",
            },
            {
                "claim_id": "CLM-OLD-002",
                "member_id": "M12345678",
                "procedure_codes": ["99213"],
                "total_amount": 155.0,
                "date_of_service": "2025-10-01",
                "provider_id": "PRV-9001",
            },
        ]

    # ------------------------------------------------------------------
    # MAIN FRAUD DETECTION ENTRY POINT
    # ------------------------------------------------------------------
    def detect(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Master fraud detection function.
        Runs all checks and produces a final risk score + decision.
        """

        fraud_checks = {
            "duplicate_check": self._check_duplicates(claim_data),
            "amount_check": self._check_unusual_amount(claim_data),
            "provider_check": self._check_high_risk_provider(claim_data),
            "pattern_check": self._check_suspicious_patterns(claim_data),
            "volume_check": self._check_claim_volume(claim_data),
        }

        # Combine risk contributions
        risk_score = self._calculate_risk_score(fraud_checks)
        risk_level = self._risk_level_from_score(risk_score)

        return {
            "risk_score": round(risk_score, 3),
            "risk_level": risk_level,
            "fraud_checks": fraud_checks,
            "red_flags": self._collect_red_flags(fraud_checks),
            "recommendation": self._recommendation_from_risk(risk_level),
        }

    # ------------------------------------------------------------------
    # INDIVIDUAL FRAUD CHECKS
    # ------------------------------------------------------------------
    def _check_duplicates(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential duplicate claims."""
        member_id = claim_data.get("patient", {}).get("member_id")
        procedures = claim_data.get("procedure_codes", [])
        date_service = claim_data.get("date_of_service")

        if not member_id or not date_service:
            return {"status": "SKIPPED", "reason": "Missing member ID or date"}

        duplicate_days = self.red_flags.get("duplicate_claim_within_days", 30)
        duplicates = []

        try:
            current = datetime.strptime(date_service, "%Y-%m-%d")
        except Exception:
            return {"status": "SKIPPED", "reason": "Invalid date format"}

        for old in self.historical_claims:
            if old["member_id"] == member_id and old["procedure_codes"] == procedures:
                old_date = datetime.strptime(old["date_of_service"], "%Y-%m-%d")
                diff = abs((current - old_date).days)

                if diff <= duplicate_days:
                    duplicates.append(
                        {"claim_id": old["claim_id"], "days_diff": diff}
                    )

        if duplicates:
            return {
                "status": "FLAGGED",
                "reason": f"Duplicate claim found within {duplicate_days} days",
                "duplicate_claims": duplicates,
                "risk_contribution": 0.4,
            }

        return {"status": "PASSED", "risk_contribution": 0.0}

    def _check_unusual_amount(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for suspicious increases in billed amount."""
        amount = claim_data.get("total_amount", 0)
        member_id = claim_data.get("patient", {}).get("member_id")

        previous_claims = [
            c for c in self.historical_claims if c["member_id"] == member_id
        ]

        if not previous_claims:
            return {
                "status": "PASSED",
                "reason": "No history",
                "risk_contribution": 0.0,
            }

        avg = sum(c["total_amount"] for c in previous_claims) / len(previous_claims)
        deviation = amount / avg if avg else 1
        max_dev = self.red_flags.get("max_amount_deviation", 3.0)

        if deviation > max_dev:
            return {
                "status": "FLAGGED",
                "reason": f"Amount is {deviation:.1f}x higher than historical avg",
                "deviation": deviation,
                "risk_contribution": 0.3,
            }

        return {"status": "PASSED", "risk_contribution": 0.0}

    def _check_high_risk_provider(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect providers previously involved in fraud cases."""
        provider_id = claim_data.get("provider", {}).get("id")

        if not provider_id:
            return {"status": "SKIPPED", "reason": "No provider ID"}

        if provider_id in self.high_risk_providers:
            return {
                "status": "FLAGGED",
                "reason": f"Provider {provider_id} has fraud history",
                "risk_contribution": 0.5,
            }

        return {"status": "PASSED", "risk_contribution": 0.0}

    def _check_suspicious_patterns(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check suspicious combinations (upcoding, bundling)."""
        procs = claim_data.get("procedure_codes", [])

        max_procs = self.red_flags.get("max_procedures_per_claim", 10)
        if len(procs) > max_procs:
            return {
                "status": "FLAGGED",
                "reason": "Too many procedures",
                "risk_contribution": 0.2,
            }

        for combo in self.suspicious_combos:
            if all(c in procs for c in combo):
                return {
                    "status": "FLAGGED",
                    "reason": f"Suspicious combination: {', '.join(combo)}",
                    "risk_contribution": 0.2,
                }

        return {"status": "PASSED", "risk_contribution": 0.0}

    def _check_claim_volume(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if member is filing too many claims."""
        member_id = claim_data.get("patient", {}).get("member_id")
        date_service = claim_data.get("date_of_service")

        if not date_service:
            return {"status": "SKIPPED", "reason": "Missing service date"}

        try:
            current = datetime.strptime(date_service, "%Y-%m-%d")
        except Exception:
            return {"status": "SKIPPED", "reason": "Invalid date format"}

        recent = 0
        for old in self.historical_claims:
            if old["member_id"] == member_id:
                old_date = datetime.strptime(old["date_of_service"], "%Y-%m-%d")
                days = (current - old_date).days
                if 0 <= days <= 30:
                    recent += 1

        if recent > 5:
            return {
                "status": "FLAGGED",
                "reason": f"{recent} claims in last 30 days",
                "risk_contribution": 0.2,
            }

        return {"status": "PASSED", "risk_contribution": 0.0}

    # ------------------------------------------------------------------
    # RISK SCORING + DECISIONING
    # ------------------------------------------------------------------
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        score = 0.0
        for result in checks.values():
            score += result.get("risk_contribution", 0.0)
        return min(1.0, score)

    def _risk_level_from_score(self, score: float) -> str:
        if score >= self.thresholds.get("high", 0.9):
            return "HIGH"
        if score >= self.thresholds.get("medium", 0.7):
            return "MEDIUM"
        if score >= self.thresholds.get("low", 0.3):
            return "LOW"
        return "MINIMAL"

    def _collect_red_flags(self, checks: Dict[str, Any]) -> List[str]:
        flags = []
        for result in checks.values():
            if result.get("status") == "FLAGGED":
                flags.append(result.get("reason", "Unknown issue"))
        return flags

    def _recommendation_from_risk(self, risk: str) -> str:
        mapping = {
            "MINIMAL": "Clear - proceed with payment.",
            "LOW": "Minor indicators - normal review.",
            "MEDIUM": "Moderate indicators - enhanced review advised.",
            "HIGH": "High fraud risk - immediate investigation required.",
        }
        return mapping.get(risk, "Unknown risk level")
