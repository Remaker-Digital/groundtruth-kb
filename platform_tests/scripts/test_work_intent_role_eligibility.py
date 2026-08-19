"""Spec-derived GO-claim role-attestation tests.

Authority:
- GOV-ROLE-DETERMINATION-INIT-LINE-ONLY-001
- DCL-INIT-BOUND-SESSION-IDENTITY-001
- DCL-SESSION-ROLE-RESOLUTION-001 v8
- SPEC-INTERACTIVE-GO-IMPLEMENTATION-CLAIM-DOCUMENT-AUTHORITY-001 v2

The production oracle is acquire() plus the persisted claim row. Harness
identity, registry role, worker-session documents, markers, and environment
values are deliberately only contradictory noise.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
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
    for slug, status in statuses.items():
        existing = sorted(
            int(path.stem.rsplit("-", 1)[1])
            for path in bridge.glob(f"{slug}-*.md")
            if path.stem.rsplit("-", 1)[-1].isdigit()
        )
        version = (existing[-1] + 1) if existing else (2 if status == "GO" else 1)
        if status == "GO" and not existing:
            (bridge / f"{slug}-001.md").write_text("NEW\n", encoding="utf-8")
        (bridge / f"{slug}-{version:03d}.md").write_text(
            f"{status}\n", encoding="utf-8"
        )


def _bind(root: Path, session_id: str, role: str):
    from groundtruth_kb.session.attestation.service import bind_exact_init

    token = {"prime-builder": "pb", "loyal-opposition": "lo"}[role]
    return bind_exact_init(
        root / "groundtruth.db",
        invoking_context=session_id,
        init_command=f"::init gtkb {token}",
        issuer="test/exact-init",
    )


def _write_obsolete_role_noise(root: Path, session_id: str, role: str) -> None:
    harness_dir = root / "harness-state"
    harness_dir.mkdir(parents=True, exist_ok=True)
    (harness_dir / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "B",
                        "harness_name": "codex",
                        "role": [role],
                        "status": "active",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    worker = harness_dir / "codex" / "session-envelopes" / f"{session_id}.json"
    worker.parent.mkdir(parents=True, exist_ok=True)
    worker.write_text(
        json.dumps(
            {
                "status": "open",
                "session_id": session_id,
                "harness_id": "B",
                "harness_name": "codex",
                "worker_role_provenance": {
                    "schema_version": 1,
                    "session_id": session_id,
                    "harness_id": "B",
                    "harness_name": "codex",
                    "role": role,
                    "role_resolution_source": "obsolete-test-noise",
                    "issued_at": "2026-08-16T00:00:00Z",
                    "dispatch_run_id": None,
                },
            }
        ),
        encoding="utf-8",
    )
    marker = root / ".claude" / "session" / "active-session-role.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"role": role, "session_id": session_id}), encoding="utf-8"
    )


@pytest.fixture
def env(monkeypatch):
    for name in (
        "GTKB_HARNESS_REGISTRY_PATH",
        "GTKB_HARNESS_NAME",
        "GTKB_HARNESS_ID",
        "GTKB_AUTHOR_HARNESS_ID",
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDECODE",
        "CODEX_THREAD_ID",
        "CODEX_HOME",
    ):
        monkeypatch.delenv(name, raising=False)
    return _registry()


def test_prime_attestation_allows_and_is_persisted(tmp_path: Path, env) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "pb-session"
    binding, attestation = _bind(tmp_path, session_id, "prime-builder")

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION
    assert holder["acting_role"] == "prime-builder"
    assert holder["session_envelope_id"] == binding.envelope_id
    assert holder["acting_role_attestation"] == attestation.evidence_reference


def test_lo_attestation_denies_even_when_every_obsolete_surface_says_prime(
    tmp_path: Path,
    env,
    monkeypatch,
) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "lo-session"
    _bind(tmp_path, session_id, "loyal-opposition")
    _write_obsolete_role_noise(tmp_path, session_id, "prime-builder")
    monkeypatch.setenv("GTKB_HARNESS_NAME", "codex")
    monkeypatch.setenv("GTKB_HARNESS_ID", "B")
    monkeypatch.setenv("CODEX_THREAD_ID", "thread-1")

    with pytest.raises(
        env.WorkIntentRegistryError, match="Prime Builder role attestation"
    ):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_prime_attestation_allows_when_obsolete_surfaces_say_lo(
    tmp_path: Path, env, monkeypatch
) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "pb-session"
    _bind(tmp_path, session_id, "prime-builder")
    _write_obsolete_role_noise(tmp_path, session_id, "loyal-opposition")
    monkeypatch.setenv("GTKB_HARNESS_NAME", "claude")
    monkeypatch.setenv("GTKB_HARNESS_ID", "D")

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    assert (
        env.current_holder("go-thread", project_root=tmp_path)["acting_role"]
        == "prime-builder"
    )


def test_missing_binding_denies_without_claim_mutation(tmp_path: Path, env) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})

    with pytest.raises(env.WorkIntentRegistryError, match="no_session_binding"):
        env.acquire("go-thread", "missing-session", project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_missing_role_attestation_denies_without_claim_mutation(
    tmp_path: Path, env
) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "missing-attestation"
    binding, _ = _bind(tmp_path, session_id, "prime-builder")
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "DELETE FROM session_role_attestations WHERE envelope_id = ?",
            (binding.envelope_id,),
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(env.WorkIntentRegistryError, match="no_role_attestation"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_unsupported_attested_role_denies_without_claim_mutation(
    tmp_path: Path, env
) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "unsupported-role"
    binding, _ = _bind(tmp_path, session_id, "prime-builder")
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "UPDATE session_role_attestations SET role = 'acting-prime-builder' WHERE envelope_id = ?",
            (binding.envelope_id,),
        )
        conn.commit()
    finally:
        conn.close()

    with pytest.raises(env.WorkIntentRegistryError, match="unsupported attested role"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_draft_claim_does_not_require_or_infer_role(tmp_path: Path, env) -> None:
    _write_index(tmp_path, {"draft-thread": "NEW"})
    _write_obsolete_role_noise(tmp_path, "draft-session", "prime-builder")

    assert env.acquire("draft-thread", "draft-session", project_root=tmp_path) is True
    holder = env.current_holder("draft-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_DRAFT
    assert holder["acting_role"] is None
    assert holder["session_envelope_id"] is None
    assert holder["acting_role_attestation"] is None


def test_prime_go_claim_preempts_lingering_draft(tmp_path: Path, env) -> None:
    _write_index(tmp_path, {"handoff-thread": "NEW"})
    assert env.acquire("handoff-thread", "draft-session", project_root=tmp_path) is True
    _write_index(tmp_path, {"handoff-thread": "GO"})
    _bind(tmp_path, "pb-session", "prime-builder")

    assert env.acquire("handoff-thread", "pb-session", project_root=tmp_path) is True
    holder = env.current_holder("handoff-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == "pb-session"
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_peer_go_claim_remains_exclusive(tmp_path: Path, env) -> None:
    _write_index(tmp_path, {"go-thread": "GO"})
    _bind(tmp_path, "pb-one", "prime-builder")
    _bind(tmp_path, "pb-two", "prime-builder")

    assert env.acquire("go-thread", "pb-one", project_root=tmp_path) is True
    assert env.acquire("go-thread", "pb-two", project_root=tmp_path) is False
    assert (
        env.current_holder("go-thread", project_root=tmp_path)["session_id"] == "pb-one"
    )


def test_lo_cannot_upgrade_own_draft_after_go(tmp_path: Path, env) -> None:
    _write_index(tmp_path, {"handoff-thread": "NEW"})
    _bind(tmp_path, "lo-session", "loyal-opposition")
    assert env.acquire("handoff-thread", "lo-session", project_root=tmp_path) is True
    _write_index(tmp_path, {"handoff-thread": "GO"})

    with pytest.raises(
        env.WorkIntentRegistryError, match="Prime Builder role attestation"
    ):
        env.acquire("handoff-thread", "lo-session", project_root=tmp_path)
    holder = env.current_holder("handoff-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == "lo-session"
    assert holder["claim_kind"] == env.CLAIM_KIND_DRAFT


def test_role_evidence_columns_are_additively_migrated(tmp_path: Path, env) -> None:
    _write_index(tmp_path, {"draft-thread": "NEW"})
    assert env.acquire("draft-thread", "draft-session", project_root=tmp_path) is True

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(work_intent_claims)")
        }
    finally:
        conn.close()
    assert {"session_envelope_id", "acting_role_attestation"} <= columns
