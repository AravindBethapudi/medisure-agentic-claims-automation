"""Integration tests for the FastAPI upload boundary."""

import logging

from fastapi.testclient import TestClient

from backend import main


client = TestClient(main.app)


def synthetic_result(filename: str) -> dict:
    """Build a minimal response shaped like the claims orchestrator output."""
    return {
        "file_name": filename,
        "extracted": {"claim_id": "SYNTHETIC-1"},
        "policies": [],
        "validation": {"decision": "APPROVED", "details": {}},
        "fraud": {"risk_level": "LOW", "risk_score": 0.0},
        "final_decision": {"decision": "APPROVE", "reason": "All clear"},
        "summary": {},
    }


def test_process_claim_accepts_a_synthetic_json_file(monkeypatch):
    """A valid synthetic JSON upload reaches the orchestrator with a safe name."""
    captured = {}

    def fake_process(file_bytes: bytes, content_type: str, filename: str) -> dict:
        captured.update(
            file_bytes=file_bytes,
            content_type=content_type,
            filename=filename,
        )
        return synthetic_result(filename)

    monkeypatch.setattr(main, "orchestrator_process_claim", fake_process)
    response = client.post(
        "/process-claim",
        files={"file": ("../../synthetic.json", b'{"claim_id":"SYNTHETIC-1"}', "application/json")},
    )

    assert response.status_code == 200
    assert response.json()["file_name"] == "synthetic.json"
    assert captured == {
        "file_bytes": b'{"claim_id":"SYNTHETIC-1"}',
        "content_type": "application/json",
        "filename": "synthetic.json",
    }


def test_process_claim_rejects_an_empty_file():
    """An empty upload is a client error and is not converted into a server error."""
    response = client.post(
        "/process-claim",
        files={"file": ("synthetic.json", b"", "application/json")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty."


def test_process_claim_rejects_an_unsupported_type():
    """Executable and unrelated file types never reach document processing."""
    response = client.post(
        "/process-claim",
        files={"file": ("unsafe.exe", b"not a claim", "application/octet-stream")},
    )

    assert response.status_code == 415


def test_process_claim_rejects_an_oversized_file():
    """The API stops reading after the prototype's bounded upload size."""
    response = client.post(
        "/process-claim",
        files={
            "file": (
                "synthetic.json",
                b"x" * (main.MAX_UPLOAD_BYTES + 1),
                "application/json",
            )
        },
    )

    assert response.status_code == 413


def test_process_claim_sanitizes_unexpected_failures(monkeypatch, caplog):
    """Internal errors do not disclose exception text or claim content."""
    def fail_processing(*_args, **_kwargs):
        raise RuntimeError("private patient detail")

    monkeypatch.setattr(main, "orchestrator_process_claim", fail_processing)
    with caplog.at_level(logging.ERROR):
        response = client.post(
            "/process-claim",
            files={"file": ("synthetic.json", b"{}", "application/json")},
        )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Claim processing failed without exposing document content."
    )
    assert "private patient detail" not in response.text
    assert "private patient detail" not in caplog.text
    assert "RuntimeError" in caplog.text


def test_root_exposes_the_synthetic_data_policy():
    """The API communicates its safe-use boundary to callers."""
    response = client.get("/")

    assert response.status_code == 200
    assert "Synthetic claim data only" in response.json()["data_policy"]


def test_metrics_cannot_be_reset_through_a_public_route():
    """The public prototype does not expose an unauthenticated reset operation."""
    response = client.post("/metrics/reset")

    assert response.status_code == 404
