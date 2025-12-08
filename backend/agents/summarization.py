# backend/agents/summarization.py
from utils.ollama_client import ask_llama

class SummarizationAgent:
    def summarize(self, extracted, validation, policies, fraud, final_decision):
        prompt = f"""
Create a warm, professional patient letter.

Patient: {extracted.get('patient_name', 'Valued Member')}
Amount: ${extracted.get('claim_amount', 0):.2f}
Decision: {final_decision['decision']}
Fraud Risk: {fraud['risk_level']}

Write a compassionate 4-5 sentence letter.
"""
        messages = [
            {"role": "system", "content": "You are a caring insurance agent."},
            {"role": "user", "content": prompt}
        ]
        letter = ask_llama(messages)
        return {
            "patient_letter": letter,
            "executive_summary": f"Claim {final_decision['decision'].lower()} — amount ${extracted.get('claim_amount', 0):.2f}"
        }