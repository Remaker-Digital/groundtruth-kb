"""Focused implementation-start worker-document selector regressions."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_authorization.py"


@pytest.fixture(scope="module")
def auth_module():
    spec = importlib.util.spec_from_file_location("wi5353_implementation_authorization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def _clear_harness_signals(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "GTKB_HARNESS_NAME",
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "GTKB_HARNESS_ID",
        "GTKB_AUTHOR_HARNESS_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDECODE",
        "CODEX_THREAD_ID",
        "CODEX_HOME",
    ):
        monkeypatch.delenv(name, raising=False)


def _write_worker_document(
    project_root: Path,
    harness_name: str,
    session_id: str,
    *,
    role: str,
    document_session_id: str | None = None,
) -> None:
    actual_session_id = document_session_id or session_id
    document = {
        "status": "open",
        "session_id": actual_session_id,
        "harness_id": harness_name[:1].upper(),
        "harness_name": harness_name,
        "role": role,
        "role_asserted": role,
        "role_resolved": role,
        "worker_role_provenance": {
            "schema_version": 1,
            "session_id": actual_session_id,
            "harness_id": harness_name[:1].upper(),
            "harness_name": harness_name,
            "role": role,
            "role_resolution_source": "test-fixture",
            "issued_at": "2026-07-16T20:49:00Z",
            "dispatch_run_id": None,
        },
    }
    path = project_root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def _packet(auth_module, bridge_id: str = "wi5353-fixture") -> dict[str, Any]:
    packet: dict[str, Any] = {
        "schema_version": 2,
        "bridge_id": bridge_id,
        "target_path_globs": ["scripts/implementation_authorization.py"],
    }
    packet["packet_hash"] = auth_module.packet_hash(packet)
    return packet


def _stub_start_dependencies(auth_module, monkeypatch: pytest.MonkeyPatch, *, role: str = "prime-builder") -> None:
    holder = {
        "thread_slug": "wi5353-fixture",
        "session_id": "shared-session",
        "claim_kind": auth_module.bridge_work_intent_registry.CLAIM_KIND_GO_IMPLEMENTATION,
        "acting_role": role,
    }
    monkeypatch.setattr(auth_module, "work_intent_claim_block_reason", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth_module.bridge_work_intent_registry, "current_holder", lambda *_args, **_kwargs: holder)
    monkeypatch.setattr(
        auth_module,
        "validate_packet_project_authorization_operation",
        lambda *_args, **_kwargs: None,
    )


def test_selected_prime_document_wins_over_same_session_lo_document(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_worker_document(tmp_path, "codex", "shared-session", role="prime-builder")
    _write_worker_document(tmp_path, "cursor", "shared-session", role="loyal-opposition")
    _stub_start_dependencies(auth_module, monkeypatch)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")

    finalized = auth_module.finalize_implementation_start_packet(
        tmp_path,
        _packet(auth_module),
        session_id="shared-session",
    )

    provenance = finalized["implementation_start"]["worker_role_provenance"]
    assert provenance["harness_name"] == "codex"
    assert provenance["role"] == "prime-builder"


def test_no_selector_preserves_cross_harness_ambiguity_failure(
    auth_module, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_worker_document(tmp_path, "codex", "shared-session", role="prime-builder")
    _write_worker_document(tmp_path, "cursor", "shared-session", role="loyal-opposition")
    _stub_start_dependencies(auth_module, monkeypatch)

    with pytest.raises(auth_module.AuthorizationError, match="ambiguous across session envelopes"):
        auth_module.finalize_implementation_start_packet(
            tmp_path,
            _packet(auth_module),
            session_id="shared-session",
        )


@pytest.mark.parametrize(
    ("selected_harness", "selected_role", "document_session_id", "error"),
    [
        ("cursor", "loyal-opposition", None, "requires prime-builder worker provenance"),
        ("claude", None, None, "missing for the current session"),
        ("codex", "prime-builder", "different-session", "does not match the current session"),
    ],
)
def test_selected_wrong_missing_or_mismatched_document_fails_closed(
    auth_module,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    selected_harness: str,
    selected_role: str | None,
    document_session_id: str | None,
    error: str,
) -> None:
    if selected_role is not None:
        _write_worker_document(
            tmp_path,
            selected_harness,
            "shared-session",
            role=selected_role,
            document_session_id=document_session_id,
        )
    _stub_start_dependencies(auth_module, monkeypatch)
    monkeypatch.setenv("GTKB_HARNESS_NAME", selected_harness)

    with pytest.raises(auth_module.AuthorizationError, match=error):
        auth_module.finalize_implementation_start_packet(
            tmp_path,
            _packet(auth_module),
            session_id="shared-session",
        )


def test_selector_precedence_and_headless_ambiguity(auth_module, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GTKB_HARNESS_NAME", "cursor")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-session")
    assert auth_module._worker_harness_selector() == "cursor"

    monkeypatch.delenv("GTKB_HARNESS_NAME")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run")
    assert auth_module._worker_harness_selector() is None

    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-session")
    assert auth_module._worker_harness_selector() == "claude"

    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID")
    assert auth_module._worker_harness_selector() == "codex"


def _write_identities(root: Path, mapping: dict[str, str]) -> None:
    """Write a minimal harness identities SoT: harness name -> durable id."""
    harness_state = root / "harness-state"
    harness_state.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "harnesses": {name: {"id": harness_id, "status": "active"} for name, harness_id in mapping.items()},
    }
    (harness_state / "harness-identities.json").write_text(json.dumps(payload), encoding="utf-8")


def test_selector_maps_durable_id_through_registry(auth_module, tmp_path, monkeypatch) -> None:
    """A generic durable harness id resolves to the canonical harness name."""
    _write_identities(tmp_path, {"goose": "G", "codex": "A", "cursor": "E"})
    monkeypatch.setenv("GTKB_HARNESS_ID", "G")
    assert auth_module._worker_harness_selector(tmp_path) == "goose"
    monkeypatch.delenv("GTKB_HARNESS_ID")
    monkeypatch.setenv("GTKB_AUTHOR_HARNESS_ID", "E")
    assert auth_module._worker_harness_selector(tmp_path) == "cursor"


def test_selector_conflicting_durable_ids_fail_closed(auth_module, tmp_path, monkeypatch) -> None:
    """Disagreeing durable-id variables fail closed instead of guessing."""
    _write_identities(tmp_path, {"goose": "G", "codex": "A"})
    monkeypatch.setenv("GTKB_HARNESS_ID", "G")
    monkeypatch.setenv("GTKB_AUTHOR_HARNESS_ID", "A")
    with pytest.raises(ValueError, match="disagree"):
        auth_module._worker_harness_selector(tmp_path)


def test_selector_unknown_durable_id_fails_closed(auth_module, tmp_path, monkeypatch) -> None:
    """An unregistered durable id fails closed (no harness selected)."""
    _write_identities(tmp_path, {"goose": "G"})
    monkeypatch.setenv("GTKB_HARNESS_ID", "ZZZ")
    with pytest.raises(ValueError, match="no registered harness"):
        auth_module._worker_harness_selector(tmp_path)


def test_selector_explicit_name_still_highest_precedence(auth_module, tmp_path, monkeypatch) -> None:
    """GTKB_HARNESS_NAME remains highest precedence over durable-id mapping."""
    _write_identities(tmp_path, {"goose": "G", "codex": "A"})
    monkeypatch.setenv("GTKB_HARNESS_NAME", "cursor")
    monkeypatch.setenv("GTKB_HARNESS_ID", "G")
    assert auth_module._worker_harness_selector(tmp_path) == "cursor"


def test_selector_legacy_markers_and_codex_home_unchanged(auth_module, tmp_path, monkeypatch) -> None:
    """Legacy live markers still select; CODEX_HOME alone selects nothing."""
    _write_identities(tmp_path, {"goose": "G"})
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-session")
    assert auth_module._worker_harness_selector(tmp_path) == "claude"
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-session")
    assert auth_module._worker_harness_selector(tmp_path) == "codex"
    monkeypatch.delenv("CODEX_THREAD_ID")
    monkeypatch.setenv("CODEX_HOME", "C:/Users/test/.codex")
    assert auth_module._worker_harness_selector(tmp_path) is None
