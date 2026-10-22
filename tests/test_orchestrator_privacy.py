"""Unit tests for workflow state isolation and audit-safe identifiers."""

import re

from backend.orchestrator import claims_orchestrator


def test_process_claim_uses_a_generated_monitoring_and_thread_id(monkeypatch):
    """A filename never becomes a monitoring ID or shared checkpoint key."""
    observed = {}

    def fake_start_claim(processing_id: str) -> dict:
        observed["processing_id"] = processing_id
        return {"claim_id": processing_id, "start_time": 0.0, "agent_times": {}}

    def fake_invoke(inputs: dict, config: dict) -> dict:
        observed["config"] = config
        return {
            "extracted": {},
            "policies": [],
            "validation": {"decision": "APPROVED"},
            "fraud": {"risk_level": "LOW"},
            "final_decision": {"decision": "APPROVE"},
            "summary": {},
        }

    monkeypatch.setattr(claims_orchestrator.monitor, "start_claim", fake_start_claim)
    monkeypatch.setattr(claims_orchestrator.monitor, "complete_claim", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(claims_orchestrator.app, "invoke", fake_invoke)

    result = claims_orchestrator.process_claim(
        b"{}",
        "application/json",
        "person-name.json",
    )

    processing_id = observed["processing_id"]
    assert re.fullmatch(r"[0-9a-f]{12}", processing_id)
    assert processing_id != "person-name.json"
    assert observed["config"]["configurable"]["thread_id"] == processing_id
    assert result["file_name"] == "person-name.json"
