"""Tests for the pre-work dispatch/document role-consistency check."""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.session.envelope import worker_session_envelope_path

from scripts.check_dispatched_role_bootstrap import evaluate


def _write_document(root: Path, *, role: str, session_id: str = "run-5171") -> None:
    path = worker_session_envelope_path(root, "codex", session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "open",
                "session_id": session_id,
                "harness_id": "A",
                "harness_name": "codex",
                "worker_role_provenance": {
                    "schema_version": 1,
                    "session_id": session_id,
                    "harness_id": "A",
                    "harness_name": "codex",
                    "role": role,
                    "role_resolution_source": "dispatcher_composition",
                    "dispatch_run_id": session_id,
                    "issued_at": "2026-07-10T18:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )


def test_dispatch_role_bootstrap_accepts_matching_document(tmp_path: Path) -> None:
    _write_document(tmp_path, role="prime-builder")

    result = evaluate(
        tmp_path,
        session_id="run-5171",
        harness_name="codex",
        dispatch_role="prime-builder",
    )

    assert result == {
        "ok": True,
        "role": "prime-builder",
        "harness_name": "codex",
        "dispatch_audit": {
            "status": "match",
            "dispatch_role": "prime-builder",
            "worker_role": "prime-builder",
        },
    }


def test_dispatch_role_bootstrap_reports_mismatch_without_substituting_worker_role(tmp_path: Path) -> None:
    _write_document(tmp_path, role="loyal-opposition")

    result = evaluate(
        tmp_path,
        session_id="run-5171",
        harness_name="codex",
        dispatch_role="prime-builder",
    )

    assert result["ok"] is True
    assert result["role"] == "loyal-opposition"
    assert result["dispatch_audit"] == {
        "status": "warning",
        "dispatch_role": "prime-builder",
        "worker_role": "loyal-opposition",
    }
