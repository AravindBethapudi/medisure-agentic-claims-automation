# backend/agents/fraud.py
from ..utils.ollama_client import ask_llama
import re

class FraudDetectionAgent:
    def __init__(self):
        print("Hybrid Fraud Agent ready")

    def detect(self, claim_data: dict) -> dict:
        """
        Enhanced fraud detection with multiple rule checks
        """
        amount = claim_data.get("claim_amount", 0)
        diagnosis_codes = claim_data.get("diagnosis_codes", [])
        procedure_codes = claim_data.get("procedure_codes", [])
        provider_name = claim_data.get("provider_name", "")
        service_date = claim_data.get("service_date", "")
        
        risk = 0.0
        flags = []

        # Rule 1: High claim amounts
        if amount > 10000:
            risk += 0.7
            flags.append("Extremely high amount (>$10,000)")
        elif amount > 5000:
            risk += 0.5
            flags.append("Very high amount (>$5,000)")
        elif amount > 2000:
            risk += 0.2
            flags.append("High amount (>$2,000)")

        # Rule 2: Suspicious keywords
        claim_text = str(claim_data).lower()
        suspicious_keywords = ["cash", "urgent", "emergency", "immediate", "rush"]
        for keyword in suspicious_keywords:
            if keyword in claim_text:
                risk += 0.2
                flags.append(f"Suspicious keyword: '{keyword}'")

        # Rule 3: Invalid or missing codes
        if not diagnosis_codes or len(diagnosis_codes) == 0:
            risk += 0.3
            flags.append("Missing diagnosis codes")
        
        if not procedure_codes or len(procedure_codes) == 0:
            risk += 0.3
            flags.append("Missing procedure codes")

        # Rule 4: Duplicate procedure codes
        if len(procedure_codes) != len(set(procedure_codes)):
            risk += 0.4
            flags.append("Duplicate procedure codes detected")

        # Rule 5: Suspicious provider patterns
        if not provider_name or provider_name.lower() == "unknown":
            risk += 0.3
            flags.append("Missing or unknown provider")
        elif "fake" in provider_name.lower():
            risk += 0.8
            flags.append("Suspicious provider name")

        # Rule 6: Invalid diagnosis codes (basic check)
        for code in diagnosis_codes:
            if not re.match(r'^[A-Z]\d{2}\.?\d*$', str(code)):
                risk += 0.2
                flags.append(f"Invalid diagnosis code format: {code}")

        # Rule 7: Invalid procedure codes (should be 5 digits)
        for code in procedure_codes:
            if not re.match(r'^\d{5}$', str(code)):
                risk += 0.2
                flags.append(f"Invalid procedure code format: {code}")

        # Rule 8: Weekend/holiday fraud pattern (optional - simplified)
        if service_date:
            # You can enhance this with actual holiday checking
            pass

        # Rule 9: Round numbers (potential fraud indicator)
        if amount > 0 and amount % 1000 == 0:
            risk += 0.1
            flags.append("Suspiciously round amount")

        # Cap risk at 1.0
        risk = min(risk, 1.0)

        # LLM second opinion if suspicious
        if risk > 0.3:
            messages = [
                {
                    "role": "system",
                    "content": "You are a medical claims fraud expert. Analyze this claim and return ONLY a JSON object with: {\"fraud_likely\": true/false, \"confidence\": 0.0-1.0, \"reasoning\": \"brief explanation\"}"
                },
                {
                    "role": "user",
                    "content": f"""Analyze this claim for fraud:
Amount: ${amount}
Provider: {provider_name}
Diagnosis Codes: {diagnosis_codes}
Procedure Codes: {procedure_codes}
Service Date: {service_date}

Current risk flags: {flags}
Current risk score: {risk}

Is this claim likely fraudulent?"""
                }
            ]
            
            try:
                llm_out = ask_llama(messages)
                # Parse LLM response
                if "true" in llm_out.lower() and "fraud_likely" in llm_out.lower():
                    risk = max(risk, 0.8)
                    flags.append("LLM detected suspicious patterns")
            except:
                pass  # If LLM fails, continue with rule-based result

        # Determine risk level
        if risk >= 0.7:
            level = "HIGH"
        elif risk >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        # Recommendation
        if risk >= 0.6:
            recommendation = "MANUAL_REVIEW"
        elif risk >= 0.4:
            recommendation = "NEEDS_REVIEW"
        else:
            recommendation = "APPROVE"

        return {
            "risk_score": round(risk, 2),
            "risk_level": level,
            "red_flags": flags,
            "recommendation": recommendation
        }