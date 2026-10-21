"""Pure helpers for keeping the Streamlit UI aligned with the API contract."""

from typing import Any, Dict


def normalize_claim_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return canonical response fields while accepting older prototype aliases."""
    if not isinstance(payload, dict):
        raise ValueError("Claim response must be a JSON object.")

    normalized = dict(payload)
    aliases = {
        "extracted": "extracted_data",
        "validation": "validation_result",
        "fraud": "fraud_analysis",
    }
    for canonical, legacy in aliases.items():
        value = payload.get(canonical, payload.get(legacy, {}))
        normalized[canonical] = value if isinstance(value, dict) else {}

    normalized.setdefault("policies", [])
    normalized.setdefault("final_decision", {})
    normalized.setdefault("summary", {})
    return normalized
