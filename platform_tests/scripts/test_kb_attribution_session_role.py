"""Validation coverage for document-authoritative worker-role provenance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.session.envelope import (
    EnvelopeError,
    resolve_worker_role_provenance,
    worker_session_envelope_path,
)


def _write_envelope(
    root: Path,
    *,
    harness_name: str = "codex",
    session_id: str = "session-5171",
    role: str = "prime-builder",
    provenance_session_id: str | None = None,
    provenance_role: str | None = None,
    status: str = "open",
) -> None:
    harness_id = "A" if harness_name == "codex" else "B"
    path = worker_session_envelope_path(root, harness_name, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": status,
                "session_id": session_id,
                "harness_id": harness_id,
                "harness_name": harness_name,
                "worker_role_provenance": {
                    "schema_version": 1,
                    "session_id": provenance_session_id or session_id,
                    "harness_id": harness_id,
                    "harness_name": harness_name,
                    "role": provenance_role or role,
                    "role_resolution_source": "dispatcher_composition",
                    "dispatch_run_id": session_id,
                    "issued_at": "2026-07-10T18:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )


def test_valid_document_provenance_is_returned(tmp_path: Path) -> None:
    _write_envelope(tmp_path, harness_name="claude", role="loyal-opposition")

    result = resolve_worker_role_provenance(tmp_path, current_session_id="session-5171", harness_name="claude")

    assert result["role"] == "loyal-opposition"
    assert result["dispatch_run_id"] == "session-5171"


def test_role_dcl_a5_rejects_missing_or_malformed_explicit_document(tmp_path: Path) -> None:
    with pytest.raises(EnvelopeError, match="missing"):
        resolve_worker_role_provenance(tmp_path, current_session_id="session-5171", harness_name="codex")

    path = worker_session_envelope_path(tmp_path, "codex", "session-5171")
    path.parent.mkdir(parents=True)
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(EnvelopeError, match="malformed"):
        resolve_worker_role_provenance(tmp_path, current_session_id="session-5171", harness_name="codex")


def test_role_dcl_a5_rejects_stale_session_and_conflicting_provenance(tmp_path: Path) -> None:
    _write_envelope(tmp_path, session_id="stale-session")
    with pytest.raises(EnvelopeError, match="session id does not match"):
        resolve_worker_role_provenance(tmp_path, current_session_id="session-5171", harness_name="codex")

    _write_envelope(tmp_path, provenance_session_id="other-session")
    with pytest.raises(EnvelopeError, match="conflicts with its session envelope"):
        resolve_worker_role_provenance(tmp_path, current_session_id="session-5171", harness_name="codex")


def test_worker_document_role_is_independent_of_dispatch_audit_metadata(tmp_path: Path) -> None:
    _write_envelope(tmp_path, role="prime-builder")

    result = resolve_worker_role_provenance(
        tmp_path,
        current_session_id="session-5171",
        harness_name="codex",
    )

    assert result["role"] == "prime-builder"


def test_ambiguous_documents_fail_closed(tmp_path: Path) -> None:
    _write_envelope(tmp_path, harness_name="codex")
    _write_envelope(tmp_path, harness_name="claude")

    with pytest.raises(EnvelopeError, match="ambiguous"):
        resolve_worker_role_provenance(tmp_path, current_session_id="session-5171")
