"""Unit tests for extraction output privacy."""

from backend.agents.extraction import ExtractionAgent


def test_json_extraction_does_not_return_a_raw_text_preview():
    """Structured extraction must not echo the complete source payload."""
    agent = ExtractionAgent()

    result = agent.extract(
        b'{"claim_id":"SYNTHETIC-1","patient_name":"Example Person","claim_amount":25}',
        "application/json",
        "synthetic.json",
    )

    assert result["claim_id"] == "SYNTHETIC-1"
    assert result["extraction_method"] == "json_parse"
    assert "raw_text_preview" not in result
