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

from groundtruth_kb.session.attestation import (  # noqa: E402
    bind_exact_init,
)
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
def exact_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, str]:
    session_id = "session-5171"
    monkeypatch.setattr(kb, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(kb, "_current_session_id", lambda: session_id)
    monkeypatch.delenv(kb.ENV_VAR_HARNESS_NAME, raising=False)
    for env_var in (
        "CLAUDECODE",
        "CLAUDE_CODE_SESSION_ID",
        "CODEX_HOME",
        "CODEX_THREAD_ID",
    ):
        monkeypatch.delenv(env_var, raising=False)
    identities = tmp_path / "harness-state" / "harness-identities.json"
    identities.parent.mkdir(parents=True, exist_ok=True)
    identities.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "codex": {"id": "A"},
                    "claude": {"id": "B"},
                },
            }
        ),
        encoding="utf-8",
    )
    return tmp_path, session_id


def _bind_exact_role(root: Path, session_id: str, role: str) -> object:
    token = "pb" if role == "prime-builder" else "lo"
    return bind_exact_init(
        root / "groundtruth.db",
        native_context_id=session_id,
        init_command=f"::init gtkb {token}",
    )


@pytest.mark.parametrize(
    ("harness_name", "role"),
    [("codex", "prime-builder"), ("claude", "loyal-opposition")],
)
def test_exact_init_attribution_is_harness_independent(
    exact_session: tuple[Path, str], harness_name: str, role: str
) -> None:
    root, session_id = exact_session
    _bind_exact_role(root, session_id, role)
    opposite = "loyal-opposition" if role == "prime-builder" else "prime-builder"
    _write_worker_document(root, harness_name=harness_name, session_id=session_id, role=opposite)

    assert kb.resolve_changed_by(harness_name=harness_name) == f"{role}/{harness_name}"


def test_canonical_writer_delegates_only_to_exact_init_authority(
    exact_session: tuple[Path, str],
) -> None:
    root, session_id = exact_session
    _bind_exact_role(root, session_id, "prime-builder")

    resolver_source = inspect.getsource(kb.resolve_changed_by)
    assert "binding_for_context" in resolver_source
    assert "resolve_worker_role_provenance" not in resolver_source
    assert "read_roles" not in resolver_source
    assert "harness-registry" not in resolver_source
    assert kb.resolve_changed_by(harness_name="codex") == "prime-builder/codex"


def test_harness_environment_supplies_identity_but_never_role(
    exact_session: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, session_id = exact_session
    _bind_exact_role(root, session_id, "loyal-opposition")
    monkeypatch.setenv(kb.ENV_VAR_HARNESS_NAME, "claude")
    monkeypatch.setenv("GTKB_ROLE", "prime-builder")

    assert kb.resolve_changed_by() == "loyal-opposition/claude"


def test_vendor_signal_without_exact_init_binding_fails_closed(
    exact_session: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CODEX_THREAD_ID", "untrusted-selector-only")

    with pytest.raises(RuntimeError, match="no session-init binding exists"):
        kb.resolve_changed_by()
    assert kb.resolve_changed_by_or_none() is None


def test_worker_document_cannot_supply_changed_by_role(
    exact_session: tuple[Path, str],
) -> None:
    root, session_id = exact_session
    _write_worker_document(root, harness_name="codex", session_id=session_id, role="prime-builder")

    with pytest.raises(RuntimeError, match="no session-init binding exists"):
        kb.resolve_changed_by(harness_name="codex")


def test_shared_marker_and_registry_cannot_override_exact_init_role(
    exact_session: tuple[Path, str],
) -> None:
    root, session_id = exact_session
    _bind_exact_role(root, session_id, "loyal-opposition")
    state = root / "harness-state"
    (state / "harness-registry.json").write_text(
        json.dumps({"harnesses": [{"harness_name": "codex", "role": ["prime-builder"]}]}),
        encoding="utf-8",
    )
    marker = root / ".claude" / "session" / "active-session-role.json"
    marker.parent.mkdir(parents=True)
    marker.write_text(
        json.dumps({"role": "prime-builder", "session_id": session_id}),
        encoding="utf-8",
    )

    assert kb.resolve_changed_by(harness_name="codex") == "loyal-opposition/codex"


def test_no_role_change_surface_exists_to_override_changed_by_authority(
    exact_session: tuple[Path, str],
) -> None:
    """Role immutability is structural, not a check that can be bypassed.

    The predecessor of this test appended an ``owner_role_change`` attestation
    and asserted ``resolve_changed_by`` refused it. Under
    ``DCL-SESSION-ROLE-RESOLUTION-001`` v9 role is a column on the immutable
    binding row and no role-change operation exists, so the stronger assertion
    is that the service exposes no such surface at all.
    """
    root, session_id = exact_session
    _bind_exact_role(root, session_id, "prime-builder")

    import groundtruth_kb.session.attestation as attestation_pkg

    for retired in ("attest_role_change", "resolve_effective_role", "Attestation"):
        assert not hasattr(attestation_pkg, retired), (
            f"{retired} is part of the retired ADR-SESSION-ROLE-ATTESTATION-SERVICE-001 design "
            "whose retirement forbids retaining a separate attestation log or role-change path"
        )

    assert kb.resolve_changed_by(harness_name="codex") == "prime-builder/codex"


@pytest.mark.parametrize("helper_path", ARCHIVE_HELPERS, ids=lambda path: path.name)
def test_archive_helpers_use_the_fail_closed_attribution_helper(
    helper_path: Path,
) -> None:
    text = helper_path.read_text(encoding="utf-8")
    assert "prime-builder/claude-code" not in text
    assert "changed_by=resolve_changed_by(" in text
    assert "resolve_changed_by_or_none" not in text
