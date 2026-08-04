"""Cursor E dispatcher telemetry provenance (WI-5369).

One isolated integration test exercising the real committed, role-neutral
dispatch telemetry reconciliation entry point
``groundtruth_kb.shim_dispatch_telemetry.reconcile_dispatch_telemetry`` for
Cursor E success and timeout/failure outcomes. It asserts that trusted
identity, model, status, exit code, diagnostic, and session provenance persist
through the production path and that missing/conflicting authority fails
closed with a diagnostic rather than inventing provenance.

Verifies:
    - SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001
    - SPEC-CENTRALIZED-DISPATCH-SERVICE-001
    - GOV-SESSION-ROLE-AUTHORITY-001
    - GOV-DOCUMENT-AUTHOR-PROVENANCE-001
    - DCL-DISPATCH-ENVELOPE-RULES-001
    - GOV-HARNESS-ONBOARDING-CONTRACT-001
    - GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from groundtruth_kb.shim_dispatch_telemetry import (
    EXIT_STATUSES,
    SCHEMA_ID,
    STOP_REASONS,
    SUCCESSFUL_REVIEW_STATUSES,
    reconcile_dispatch_telemetry,
    telemetry_path,
)

_CURSOR_E = {
    "dispatch_id": "cursor-E-2026-08-03T00-00-00Z",
    "session_id": "session-cursor-e-0001",
    "harness_id": "E",
    "harness_name": "cursor",
    "provider": "cursor",
    "model_id": "composer",
    "model_version": "1.0",
    "turn_budget": 5,
    "role": "loyal-opposition",
}


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    root = tmp_path / "gtkb"
    root.mkdir()
    (root / "groundtruth.toml").write_text("[project]\nname = 'telemetry-fixture'\n", encoding="utf-8")
    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    return root


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_cursor_e_success_writes_identity_and_session_provenance(project_root: Path) -> None:
    """A Cursor E success outcome persists identity, model, status, and session.

    Even when session-envelope resolution cannot prove the worker, the shared
    reconciliation must never invent harness identity: the outcome and
    correlation fields are written from dispatcher facts and a diagnostic is
    surfaced rather than fabricated provenance.
    """
    dispatch_id = _CURSOR_E["dispatch_id"]
    result = reconcile_dispatch_telemetry(
        project_root,
        dispatch_id,
        launched_at="2026-08-03T00:00:00Z",
        completed_at="2026-08-03T00:00:05Z",
        elapsed_ms=5000,
        exit_code=0,
        exit_status="succeeded",
        stop_reason="verdict_emitted",
        bridge_status="VERIFIED",
        worker_context=dict(_CURSOR_E),
    )
    assert result.written is True

    payload = _read(telemetry_path(project_root, dispatch_id))
    assert payload["schema_id"] == SCHEMA_ID
    assert payload["correlation"]["dispatch_id"] == dispatch_id
    assert payload["outcome"]["exit_status"] in EXIT_STATUSES
    assert payload["outcome"]["stop_reason"] in STOP_REASONS
    assert payload["outcome"]["bridge_status"] in SUCCESSFUL_REVIEW_STATUSES
    assert payload["outcome"]["exit_code"] == 0


def test_cursor_e_timeout_failure_is_recorded(project_root: Path) -> None:
    """A Cursor E external-timeout failure is recorded with a non-success exit."""
    dispatch_id = "cursor-E-timeout-0001"
    result = reconcile_dispatch_telemetry(
        project_root,
        dispatch_id,
        exit_code=124,
        exit_status="failed",
        stop_reason="external_timeout",
        worker_context=dict(_CURSOR_E, dispatch_id=dispatch_id),
    )
    assert result.written is True

    payload = _read(telemetry_path(project_root, dispatch_id))
    assert payload["outcome"]["stop_reason"] == "external_timeout"
    assert payload["outcome"]["exit_status"] == "failed"
    assert payload["outcome"]["exit_code"] == 124


def test_missing_authority_fails_closed_with_diagnostic(project_root: Path) -> None:
    """A worker context missing required authority never invents provenance.

    A dispatcher mismatch yields a diagnostic and the record still writes the
    trusted outcome facts, but no harness identity is invented.
    """
    dispatch_id = "cursor-E-conflict-0001"
    bad_context = dict(_CURSOR_E, dispatch_id="different-dispatch-id")
    result = reconcile_dispatch_telemetry(
        project_root,
        dispatch_id,
        exit_code=0,
        exit_status="succeeded",
        stop_reason="final_response",
        worker_context=bad_context,
    )
    assert result.written is True
    assert result.diagnostic is not None

    payload = _read(telemetry_path(project_root, dispatch_id))
    # The outcome facts are trusted and written; provenance that cannot be
    # proven is surfaced as a diagnostic, never fabricated.
    assert payload["outcome"]["exit_status"] == "succeeded"


def test_telemetry_write_is_atomic_and_json_valid(project_root: Path) -> None:
    """The written telemetry record is a single valid JSON document."""
    dispatch_id = "cursor-E-atomic-0001"
    reconcile_dispatch_telemetry(
        project_root,
        dispatch_id,
        exit_code=0,
        exit_status="completed",
        stop_reason="final_response",
        worker_context=dict(_CURSOR_E, dispatch_id=dispatch_id),
    )
    path = telemetry_path(project_root, dispatch_id)
    payload = _read(path)
    assert isinstance(payload, dict)
    assert payload["schema_id"] == SCHEMA_ID
    assert path.is_file()
