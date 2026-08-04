"""Validation coverage for document-authoritative worker-role provenance."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.session.envelope import (
    EnvelopeError,
    resolve_acting_harness_identity,
    resolve_worker_role_provenance,
    same_session_envelope_collisions,
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


def _write_identities(root: Path, **identities: str) -> None:
    path = root / "harness-state" / "harness-identities.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"schema_version": 1, "harnesses": {name: {"id": value} for name, value in identities.items()}}),
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


def test_acting_harness_selector_uses_host_family_and_durable_identity(tmp_path: Path) -> None:
    _write_identities(tmp_path, codex="A", claude="B")

    assert resolve_acting_harness_identity(
        tmp_path,
        environ={"CODEX_THREAD_ID": "session-5171", "GTKB_ROLE": "loyal-opposition"},
    ) == ("codex", "A")

    with pytest.raises(EnvelopeError, match="Conflicting runtime-specific"):
        resolve_acting_harness_identity(
            tmp_path,
            environ={"CODEX_THREAD_ID": "session-5171", "CLAUDE_CODE_SESSION_ID": "session-5171"},
        )
    with pytest.raises(EnvelopeError, match="does not match persisted id"):
        resolve_acting_harness_identity(
            tmp_path,
            environ={"GTKB_HARNESS_NAME": "codex", "GTKB_HARNESS_ID": "B"},
        )
    with pytest.raises(EnvelopeError, match="Could not resolve harness identity"):
        resolve_acting_harness_identity(
            tmp_path,
            environ={"GTKB_HARNESS_NAME": "unknown-host", "GTKB_HARNESS_ID": "Z"},
        )


def test_empty_environ_does_not_fall_back_to_ambient_markers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # WI-5580 IP-R1/R2: an explicit empty environ must fail closed, never inherit
    # the process ambient host-family markers (here a live Codex marker).
    _write_identities(tmp_path, codex="A", claude="B")
    monkeypatch.setenv("CODEX_THREAD_ID", "ambient-codex-session")

    with pytest.raises(EnvelopeError, match="Acting harness identity is unavailable"):
        resolve_acting_harness_identity(tmp_path, environ={})


def test_explicit_producer_beats_ambient_marker(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # WI-5580 IP-R1/R2: an explicit harness name/id resolves to the explicit producer
    # even when an ambient host-family marker (Codex) is present in os.environ.
    _write_identities(tmp_path, codex="A", claude="B")
    monkeypatch.setenv("CODEX_THREAD_ID", "ambient-codex-session")

    assert resolve_acting_harness_identity(
        tmp_path,
        environ={},
        harness_name="claude",
        harness_id="B",
    ) == ("claude", "B")


def test_same_session_collision_diagnostics_are_sorted_and_non_mutating(tmp_path: Path) -> None:
    _write_envelope(tmp_path, harness_name="codex")
    _write_envelope(tmp_path, harness_name="claude")
    _write_envelope(tmp_path, harness_name="cursor")
    state_root = tmp_path / "harness-state"
    before = {path: path.read_bytes() for path in state_root.glob("*/session-envelopes/*.json")}

    collisions = same_session_envelope_collisions(
        tmp_path,
        current_session_id="session-5171",
        selected_harness_name="codex",
    )

    assert collisions == [
        "harness-state/claude/session-envelopes/session-5171.json",
        "harness-state/cursor/session-envelopes/session-5171.json",
    ]
    assert {path: path.read_bytes() for path in before} == before
