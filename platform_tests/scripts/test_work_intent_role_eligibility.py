"""Tests for the WI-4534 Slice A role-eligibility guard on go_implementation claims.

Every oracle is the ``acquire()`` outcome (raise vs. acquired) plus the
persisted ``claim_status`` record, exercising the production registry interface.
Authority: GOV-SESSION-ROLE-AUTHORITY-001, DCL-SESSION-ROLE-RESOLUTION-001,
GOV-FILE-BRIDGE-AUTHORITY-001 (the guard adds no canonical INDEX write surface).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REGISTRY_PATH = SCRIPTS_DIR / "bridge_work_intent_registry.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _registry():
    return _load_module(REGISTRY_PATH, "bridge_work_intent_registry")


def _write_index(root: Path, statuses: dict[str, str]) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for slug, status in statuses.items():
        existing = sorted(
            (
                int(path.stem.rsplit("-", 1)[1])
                for path in bridge.glob(f"{slug}-*.md")
                if path.stem.rsplit("-", 1)[-1].isdigit()
            ),
            reverse=True,
        )
        if existing:
            version_number = existing[0] + 1
        else:
            version_number = 2 if status == "GO" else 1
            if status == "GO":
                (bridge / f"{slug}-001.md").write_text("NEW\n", encoding="utf-8")
        version = f"{version_number:03d}"
        (bridge / f"{slug}-{version}.md").write_text(f"{status}\n", encoding="utf-8")
        lines.extend([f"Document: {slug}", f"{status}: bridge/{slug}-{version}.md", ""])
    (bridge / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def _write_registry(root: Path, roles: dict[str, str]) -> None:
    """Write a test harness-registry projection mapping harness id -> role token."""
    harness_dir = root / "harness-state"
    harness_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "schema_version": 1,
        "source_of_truth": "test fixture",
        "harnesses": [
            {"id": harness_id, "harness_name": harness_id.lower(), "role": [role], "status": "active"}
            for harness_id, role in roles.items()
        ],
    }
    (harness_dir / "harness-registry.json").write_text(json.dumps(document), encoding="utf-8")


def _write_per_session_marker(root: Path, role: str, session_id: str) -> None:
    from scripts.gtkb_session_id import per_session_role_marker_path

    marker = per_session_role_marker_path(root, session_id)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"role": role, "session_id": session_id}),
        encoding="utf-8",
    )


def _write_marker(root: Path, role: str, session_id: str = "marker-session") -> None:
    _write_per_session_marker(root, role, session_id)


def _write_shared_marker(root: Path, role: str, session_id: str) -> Path:
    marker = root / ".claude" / "session" / "active-session-role.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"role": role, "session_id": session_id}),
        encoding="utf-8",
    )
    return marker


def _write_worker_session(
    root: Path,
    role: str,
    session_id: str,
    *,
    harness_name: str = "codex",
    harness_id: str = "B",
    status: str = "open",
    document_session_id: str | None = None,
    provenance_session_id: str | None = None,
    provenance_harness_name: str | None = None,
    provenance_harness_id: str | None = None,
    provenance_role: str | None = None,
    provenance_schema_version: int = 1,
) -> Path:
    """Write the minimum valid worker-session document for the canonical resolver."""
    document_session_id = document_session_id or session_id
    document = {
        "status": status,
        "session_id": document_session_id,
        "harness_id": harness_id,
        "harness_name": harness_name,
        "worker_role_provenance": {
            "schema_version": provenance_schema_version,
            "session_id": provenance_session_id or document_session_id,
            "harness_id": provenance_harness_id or harness_id,
            "harness_name": provenance_harness_name or harness_name,
            "role": provenance_role or role,
            "role_resolution_source": "test-fixture",
            "issued_at": "2026-06-13T00:00:00Z",
            "dispatch_run_id": None,
        },
    }
    path = root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


@pytest.fixture
def env(monkeypatch):
    """Pin registry and worker-document resolution to the test fixture."""
    for name in (
        "GTKB_HARNESS_REGISTRY_PATH",
        "GTKB_HARNESS_NAME",
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDECODE",
        "CODEX_THREAD_ID",
        "CODEX_HOME",
    ):
        monkeypatch.delenv(name, raising=False)
    registry = _registry()
    base = datetime(2026, 6, 13, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(registry, "now_utc", lambda: base)
    return registry


def test_go_impl_rejected_for_lo_dispatch_harness(tmp_path: Path, env) -> None:
    """A document-resolved Loyal Opposition worker cannot hold a GO claim."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T20-07-29Z-loyal-opposition-D-20c71a"
    _write_worker_session(tmp_path, "loyal-opposition", session_id, harness_id="D")

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_allowed_for_prime_dispatch_harness(tmp_path: Path, env) -> None:
    """A document-resolved Prime Builder worker may hold a GO claim."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T22-19-33Z-prime-builder-B-6a8e3e"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] == "prime-builder"
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_go_impl_ignores_unknown_dispatch_harness_registry(tmp_path: Path, env) -> None:
    """A valid worker document is sufficient even when the dispatch id is unknown to the registry."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T22-00-00Z-prime-builder-Z-a1b2c3"
    _write_worker_session(tmp_path, "prime-builder", session_id, harness_id="Z")

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] == "prime-builder"


def test_go_impl_resolves_from_document_not_registry_or_token(tmp_path: Path, env) -> None:
    """The document denies a claim even when registry and dispatch token say Prime."""
    _write_registry(tmp_path, {"D": "prime-builder"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T22-00-00Z-prime-builder-D-a1b2c3"
    _write_worker_session(tmp_path, "loyal-opposition", session_id, harness_id="D")

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_rejected_for_uuid_session_without_document(tmp_path: Path, env) -> None:
    """A missing worker document denies the claim even when a Prime marker exists."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None

    _write_marker(tmp_path, "prime-builder", session_id=session_id)
    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_document_overrides_conflicting_marker(tmp_path: Path, env) -> None:
    """A Prime document authorizes despite a conflicting Loyal Opposition marker."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_worker_session(tmp_path, "prime-builder", session_id)
    _write_marker(tmp_path, "loyal-opposition", session_id=session_id)

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] == "prime-builder"
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_go_impl_harness_selector_only_selects_document(tmp_path: Path, env, monkeypatch) -> None:
    """A harness selector chooses a document but cannot contribute its role."""
    _write_registry(tmp_path, {"B": "loyal-opposition", "C": "prime-builder"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_worker_session(tmp_path, "prime-builder", session_id, harness_name="codex", harness_id="B")
    _write_worker_session(tmp_path, "loyal-opposition", session_id, harness_name="claude", harness_id="C")
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] == "prime-builder"


def test_go_impl_ignores_shared_and_per_session_markers(tmp_path: Path, env) -> None:
    """Marker changes cannot authorize or revoke a document-authorized claim."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_worker_session(tmp_path, "prime-builder", session_id)
    _write_marker(tmp_path, "loyal-opposition", session_id=session_id)
    _write_shared_marker(tmp_path, "loyal-opposition", session_id)

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] == "prime-builder"
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_go_impl_ignores_unrelated_session_marker_overwrite(tmp_path: Path, env) -> None:
    """A peer marker cannot override the current worker session document."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    current_session = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    peer_session = "f7c20a94-cff7-48e4-87b4-3524f28f42df"
    _write_worker_session(tmp_path, "prime-builder", current_session)
    _write_marker(tmp_path, "loyal-opposition", session_id=peer_session)
    _write_shared_marker(tmp_path, "loyal-opposition", peer_session)

    assert env.acquire("go-thread", current_session, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == current_session
    assert holder["acting_role"] == "prime-builder"
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_go_impl_rejects_invalid_worker_documents_without_claim_record(tmp_path: Path, env) -> None:
    """Missing, malformed, closed, ambiguous, and inconsistent documents fail closed."""
    _write_registry(tmp_path, {"B": "prime-builder", "C": "prime-builder"})
    invalid_cases = (
        "missing",
        "malformed",
        "closed",
        "ambiguous",
        "mismatched-session",
        "inconsistent-harness",
    )
    for index, case in enumerate(invalid_cases):
        slug = f"invalid-worker-document-{index}"
        session_id = f"26c2349e-1cd0-4024-acef-f934b35fea{index:02d}"
        _write_index(tmp_path, {slug: "GO"})
        if case == "malformed":
            path = tmp_path / "harness-state" / "codex" / "session-envelopes" / f"{session_id}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("not-json", encoding="utf-8")
        elif case == "closed":
            _write_worker_session(tmp_path, "prime-builder", session_id, status="closed")
        elif case == "ambiguous":
            _write_worker_session(tmp_path, "prime-builder", session_id, harness_name="codex", harness_id="B")
            _write_worker_session(tmp_path, "prime-builder", session_id, harness_name="claude", harness_id="C")
        elif case == "mismatched-session":
            _write_worker_session(
                tmp_path,
                "prime-builder",
                session_id,
                document_session_id="different-session",
            )
        elif case == "inconsistent-harness":
            _write_worker_session(
                tmp_path,
                "prime-builder",
                session_id,
                provenance_harness_id="different-harness",
            )
        else:
            pass

        with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
            env.acquire(slug, session_id, project_root=tmp_path)
        assert env.claim_status(slug, project_root=tmp_path) is None


def test_draft_claim_unaffected_for_lo_harness_on_non_go_thread(tmp_path: Path, env) -> None:
    """The guard is scoped to go_implementation: an LO harness may draft on a NEW-latest thread."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"draft-thread": "NEW"})
    session_id = "2026-06-13T22-00-00Z-loyal-opposition-D-20c71a"

    assert env.acquire("draft-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("draft-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_DRAFT


def test_go_impl_rejected_for_unsupported_document_role(tmp_path: Path, env) -> None:
    """A legacy acting-prime-builder role cannot replace the document contract."""
    _write_registry(tmp_path, {"B": "prime-builder", "X": "acting-prime-builder"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "2026-06-13T22-00-00Z-acting-prime-builder-X-a1b2c3"
    _write_worker_session(tmp_path, "acting-prime-builder", session_id, harness_id="X")

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_go_impl_preempts_lingering_non_go_draft_claim(tmp_path: Path, env) -> None:
    """WI-4849: a Prime GO implementation claim may replace a stale draft claim."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"handoff-thread": "NEW"})
    draft_session = "2026-06-13T22-00-00Z-loyal-opposition-D-20c71a"
    prime_session = "2026-06-13T22-19-33Z-prime-builder-B-6a8e3e"
    _write_worker_session(tmp_path, "prime-builder", prime_session)

    assert env.acquire("handoff-thread", draft_session, project_root=tmp_path) is True
    draft_holder = env.current_holder("handoff-thread", project_root=tmp_path)
    assert draft_holder is not None
    assert draft_holder["claim_kind"] == env.CLAIM_KIND_DRAFT

    _write_index(tmp_path, {"handoff-thread": "GO"})

    assert env.acquire("handoff-thread", prime_session, project_root=tmp_path) is True
    holder = env.current_holder("handoff-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == prime_session
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_go_impl_does_not_preempt_peer_go_implementation_claim(tmp_path: Path, env) -> None:
    """WI-4849 negative control: an active peer go_implementation holder remains exclusive."""
    _write_registry(tmp_path, {"B": "prime-builder", "C": "prime-builder"})
    _write_index(tmp_path, {"go-thread": "GO"})
    first_session = "2026-06-13T22-19-33Z-prime-builder-B-6a8e3e"
    second_session = "2026-06-13T22-20-33Z-prime-builder-C-a1b2c3"
    _write_worker_session(tmp_path, "prime-builder", first_session, harness_id="B")
    _write_worker_session(tmp_path, "prime-builder", second_session, harness_id="C")

    assert env.acquire("go-thread", first_session, project_root=tmp_path) is True
    assert env.acquire("go-thread", second_session, project_root=tmp_path) is False
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == first_session
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_lo_dispatch_cannot_upgrade_own_draft_after_go(tmp_path: Path, env) -> None:
    """WI-4849 keeps the GO role guard ahead of any draft-preemption path."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"handoff-thread": "NEW"})
    lo_session = "2026-06-13T22-00-00Z-loyal-opposition-D-20c71a"

    assert env.acquire("handoff-thread", lo_session, project_root=tmp_path) is True
    _write_index(tmp_path, {"handoff-thread": "GO"})

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("handoff-thread", lo_session, project_root=tmp_path)
    holder = env.current_holder("handoff-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == lo_session
    assert holder["claim_kind"] == env.CLAIM_KIND_DRAFT
