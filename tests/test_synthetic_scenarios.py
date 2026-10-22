"""Regression tests for the three documented synthetic claim scenarios."""

from pathlib import Path

import pytest

from backend.agents import fraud as fraud_module
from backend.orchestrator.claims_orchestrator import process_claim


SCENARIO_DIRECTORY = Path(__file__).parents[1] / "test_claims"


@pytest.mark.parametrize(
    ("filename", "expected_decision", "expected_fraud"),
    [
        ("TEST1.json", "APPROVE", "LOW"),
        ("TEST2.json", "REJECT", "HIGH"),
        ("TEST3.json", "APPROVE", "LOW"),
    ],
)
def test_documented_synthetic_scenario(
    monkeypatch,
    filename: str,
    expected_decision: str,
    expected_fraud: str,
):
    """Each checked-in scenario produces its documented deterministic outcome."""
    monkeypatch.setattr(fraud_module, "ask_llama", lambda *_args, **_kwargs: "{}")
    file_bytes = (SCENARIO_DIRECTORY / filename).read_bytes()

    result = process_claim(file_bytes, "application/json", filename)

    assert result["final_decision"]["decision"] == expected_decision
    assert result["fraud"]["risk_level"] == expected_fraud
