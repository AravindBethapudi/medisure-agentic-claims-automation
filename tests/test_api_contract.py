"""Unit tests for the frontend/backend response contract."""

import pytest

from streamlit_app.utils.api_contract import normalize_claim_result


def test_normalize_claim_result_preserves_current_backend_fields():
    """The current API keys remain available to every Streamlit page."""
    payload = {
        "extracted": {"claim_id": "SYNTHETIC-1"},
        "validation": {"decision": "APPROVED"},
        "fraud": {"risk_level": "LOW"},
    }

    normalized = normalize_claim_result(payload)

    assert normalized["extracted"]["claim_id"] == "SYNTHETIC-1"
    assert normalized["validation"]["decision"] == "APPROVED"
    assert normalized["fraud"]["risk_level"] == "LOW"


def test_normalize_claim_result_accepts_legacy_aliases():
    """Older demo responses still map to the canonical field names."""
    normalized = normalize_claim_result(
        {
            "extracted_data": {"claim_id": "LEGACY-1"},
            "validation_result": {"decision": "NEEDS_REVIEW"},
            "fraud_analysis": {"risk_level": "MEDIUM"},
        }
    )

    assert normalized["extracted"]["claim_id"] == "LEGACY-1"
    assert normalized["validation"]["decision"] == "NEEDS_REVIEW"
    assert normalized["fraud"]["risk_level"] == "MEDIUM"


def test_normalize_claim_result_rejects_non_object_payloads():
    """Malformed API responses fail clearly before corrupting UI state."""
    with pytest.raises(ValueError, match="JSON object"):
        normalize_claim_result([])
