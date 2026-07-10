"""Specification-derived tests for document-authoritative backlog attribution."""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
ARCHIVE_HELPERS = sorted(SCRIPTS_DIR.glob("_archive_delib_s32*.py"))

sys.path.insert(0, str(PROJECT_ROOT))

from groundtruth_kb.session.envelope import worker_session_envelope_path  # noqa: E402

import scripts._kb_attribution as kb  # noqa: E402


def _write_worker_document(
    root: Path,
    *,
    harness_name: str,
    session_id: str,
    role: str,
    harness_id: str = "A",
) -> None:
    path = worker_session_envelope_path(root, harness_name, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "open",
                "session_id": session_id,
                "harness_id": harness_id,
                "harness_name": harness_name,
                "worker_role_provenance": {
                    "schema_version": 1,
                    "session_id": session_id,
                    "harness_id": harness_id,
                    "harness_name": harness_name,
                    "role": role,
                    "role_resolution_source": "dispatcher_composition",
                    "dispatch_run_id": session_id,
                    "issued_at": "2026-07-10T18:00:00Z",
                },
            }
        ),
        encoding="utf-8",
    )


@pytest.fixture
def worker_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, str]:
    session_id = "session-5171"
    monkeypatch.setattr(kb, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(kb, "_current_session_id", lambda: session_id)
    monkeypatch.delenv(kb.ENV_VAR_HARNESS_NAME, raising=False)
    for env_var in ("CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "CODEX_HOME", "CODEX_THREAD_ID"):
        monkeypatch.delenv(env_var, raising=False)
    return tmp_path, session_id


@pytest.mark.parametrize(
    ("harness_name", "role"),
    [("codex", "prime-builder"), ("claude", "loyal-opposition")],
)
def test_role_dcl_a10_document_provenance_semantics_are_harness_independent(
    worker_session: tuple[Path, str], harness_name: str, role: str
) -> None:
    root, session_id = worker_session
    _write_worker_document(root, harness_name=harness_name, session_id=session_id, role=role)

    assert kb.resolve_changed_by(harness_name=harness_name) == f"{role}/{harness_name}"


def test_role_dcl_a2_canonical_writer_delegates_only_to_document_provenance(worker_session: tuple[Path, str]) -> None:
    """The writer consumes document provenance and has no dispatcher-role path."""
    root, session_id = worker_session
    _write_worker_document(root, harness_name="codex", session_id=session_id, role="prime-builder")

    resolver_source = inspect.getsource(kb.resolve_changed_by)
    assert "resolve_worker_role_provenance" in resolver_source
    assert "read_roles" not in resolver_source
    assert "harness-registry" not in resolver_source
    assert "dispatcher" not in resolver_source
    assert kb.resolve_changed_by(harness_name="codex") == "prime-builder/codex"


def test_harness_environment_selects_a_document_but_never_supplies_a_role(
    worker_session: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, session_id = worker_session
    _write_worker_document(root, harness_name="claude", session_id=session_id, role="loyal-opposition", harness_id="B")
    monkeypatch.setenv(kb.ENV_VAR_HARNESS_NAME, "claude")

    assert kb.resolve_changed_by() == "loyal-opposition/claude"


def test_vendor_signal_without_a_worker_document_fails_closed(
    worker_session: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CODEX_THREAD_ID", "untrusted-selector-only")

    with pytest.raises(RuntimeError, match="provenance is missing"):
        kb.resolve_changed_by()
    assert kb.resolve_changed_by_or_none() is None


def test_stale_explicit_document_fails_closed(worker_session: tuple[Path, str]) -> None:
    root, _ = worker_session
    _write_worker_document(root, harness_name="codex", session_id="older-session", role="prime-builder")

    with pytest.raises(RuntimeError, match="session id does not match"):
        kb.resolve_changed_by(harness_name="codex")


def test_role_dcl_a8_a9_shared_marker_and_registry_cannot_supply_behavior_role(
    worker_session: tuple[Path, str],
) -> None:
    root, session_id = worker_session
    _write_worker_document(root, harness_name="codex", session_id=session_id, role="loyal-opposition")
    state = root / "harness-state"
    (state / "harness-registry.json").write_text(
        json.dumps({"harnesses": [{"harness_name": "codex", "role": ["prime-builder"]}]}),
        encoding="utf-8",
    )
    marker = root / ".claude" / "session" / "active-session-role.json"
    marker.parent.mkdir(parents=True)
    marker.write_text(json.dumps({"role": "prime-builder", "session_id": session_id}), encoding="utf-8")

    assert kb.resolve_changed_by(harness_name="codex") == "loyal-opposition/codex"


@pytest.mark.parametrize("helper_path", ARCHIVE_HELPERS, ids=lambda path: path.name)
def test_archive_helpers_use_the_fail_closed_attribution_helper(helper_path: Path) -> None:
    text = helper_path.read_text(encoding="utf-8")
    assert "prime-builder/claude-code" not in text
    assert "changed_by=resolve_changed_by(" in text
    assert "resolve_changed_by_or_none" not in text
