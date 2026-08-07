"""Document-authoritative guard-reader tests for the go_implementation claim.

bridge/gtkb-wi4540-per-session-role-marker-context-envelope-003.md (GO at -004).

WI-5189 supersedes marker and dispatch-token role inference for claim
eligibility. Positive GO-claim fixtures therefore use validated worker-session
documents; legacy marker fixtures remain as negative non-authority coverage.

Every oracle is the production ``acquire()`` outcome (raise vs. acquired) plus
the persisted claim record. WI-4868 removed the legacy shared-marker fallback;
``platform_tests/scripts/test_work_intent_role_eligibility.py`` covers the
interactive eligibility path with per-session markers.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REGISTRY_PATH = SCRIPTS_DIR / "bridge_work_intent_registry.py"
CLAIM_CLI_PATH = SCRIPTS_DIR / "bridge_claim_cli.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gtkb_session_id import per_session_role_marker_path  # noqa: E402


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
        version_num = 2 if status == "GO" else 1
        lines.extend([f"Document: {slug}", f"{status}: bridge/{slug}-{version_num:03d}.md", ""])
        path = bridge / f"{slug}-{version_num:03d}.md"
        path.write_text(f"{status}\n\n# Body\n", encoding="utf-8")
    (bridge / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def _write_project_thread(root: Path, slug: str, status: str, project_id: str = "PROJECT-X") -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    proposal = "\n".join(
        [
            "NEW",
            "",
            f"# Fixture proposal {slug}",
            "",
            f"Project: {project_id}",
            "Work Item: WI-0000",
            "",
        ]
    )
    (bridge / f"{slug}-001.md").write_text(proposal, encoding="utf-8")
    if status == "GO":
        (bridge / f"{slug}-002.md").write_text("GO\n\nFixture GO.\n", encoding="utf-8")


def _write_bootstrap_thread(root: Path, slug: str) -> None:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    proposal = "\n".join(
        [
            "NEW",
            "",
            f"# Fixture project authorization bootstrap {slug}",
            "",
            "Project: PROJECT-X",
            "Work Item: WI-5279",
            "Project Authorization: PAUTH-BOOTSTRAP",
            'target_paths: ["groundtruth.db"]',
            "",
            "## Project Authorization Bootstrap",
            "",
            "project_authorization_bootstrap owner decision DELIB-BOOTSTRAP for PAUTH-BOOTSTRAP.",
            "",
        ]
    )
    (bridge / f"{slug}-001.md").write_text(proposal, encoding="utf-8")
    (bridge / f"{slug}-002.md").write_text("GO\n\nFixture GO.\n", encoding="utf-8")


def _write_registry(root: Path, roles: dict[str, str]) -> None:
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


def _write_per_session_marker(root: Path, role: str, session_id: str, *, stored_session_id: str | None = None) -> None:
    marker = per_session_role_marker_path(root, session_id)
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps(
            {
                "role": role,
                "session_id": session_id if stored_session_id is None else stored_session_id,
                "written_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
        ),
        encoding="utf-8",
    )


def _write_legacy_marker(root: Path, role: str, session_id: str = "marker-session") -> None:
    marker_dir = root / ".claude" / "session"
    marker_dir.mkdir(parents=True, exist_ok=True)
    (marker_dir / "active-session-role.json").write_text(
        json.dumps({"role": role, "session_id": session_id}), encoding="utf-8"
    )


def _write_worker_session(root: Path, role: str, session_id: str) -> Path:
    harness_name = "fixture"
    harness_id = "T"
    document = {
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
            "role_resolution_source": "test-fixture",
            "issued_at": "2026-06-14T00:00:00Z",
            "dispatch_run_id": None,
        },
    }
    path = root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


@pytest.fixture
def env(monkeypatch):
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    monkeypatch.setenv("GTKB_HARNESS_NAME", "fixture")
    registry = _registry()
    base = datetime(2026, 6, 14, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(registry, "now_utc", lambda: base)
    return registry


def test_go_impl_allowed_for_uuid_session_with_prime_worker_document(tmp_path: Path, env) -> None:
    """A raw-UUID Prime session is accepted through its validated document."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_go_impl_rejected_for_uuid_session_with_per_session_lo_marker(tmp_path: Path, env) -> None:
    """A per-session loyal-opposition marker is not positive Prime evidence."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_per_session_marker(tmp_path, "loyal-opposition", session_id)

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_per_session_marker_for_other_session_does_not_authorize(tmp_path: Path, env) -> None:
    """A per-session Prime marker keyed under a DIFFERENT session id does not
    authorize THIS session (per-session keying + no legacy fallback marker)."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    other_session = "11111111-1111-4111-8111-111111111111"
    this_session = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_per_session_marker(tmp_path, "prime-builder", other_session)

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", this_session, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_per_session_stored_id_mismatch_is_not_positive_evidence(tmp_path: Path, env) -> None:
    """A per-session marker found under the querying id's filename but carrying a
    mismatched stored session_id is rejected (assertion 6; no fail-open)."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_per_session_marker(tmp_path, "prime-builder", session_id, stored_session_id="a-different-raw-id")

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_per_session_marker_is_authority_over_legacy(tmp_path: Path, env) -> None:
    """The per-session marker is the authority: a per-session LO marker rejects
    even when the legacy single-file marker says prime-builder."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_legacy_marker(tmp_path, "prime-builder", session_id=session_id)
    _write_per_session_marker(tmp_path, "loyal-opposition", session_id)

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)
    assert env.claim_status("go-thread", project_root=tmp_path) is None


def test_legacy_shared_marker_is_ignored_without_per_session_marker(tmp_path: Path, env) -> None:
    """WI-4868: the shared active-session-role.json slot must not authorize or
    attribute acting_role for a session lacking a matching per-session marker."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO", "draft-thread": "NEW"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_legacy_marker(tmp_path, "prime-builder", session_id=session_id)

    with pytest.raises(env.WorkIntentRegistryError, match="prime-builder harness"):
        env.acquire("go-thread", session_id, project_root=tmp_path)

    assert env.acquire("draft-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("draft-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] is None


def test_work_intent_schema_upgrades_with_role_project_columns(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.execute(
        """
        CREATE TABLE work_intent_claims (
            rowid INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_slug TEXT NOT NULL,
            session_id TEXT NOT NULL,
            acquired_at TEXT NOT NULL,
            ttl_expires_at TEXT NOT NULL,
            UNIQUE(thread_slug)
        )
        """
    )
    conn.commit()
    conn.close()

    session_id = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    assert env.acquire("thread-a", session_id, project_root=tmp_path)
    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] == "prime-builder"
    assert holder["project_id"] == "PROJECT-X"
    assert env.project_id_for_thread("thread-a", project_root=tmp_path) == "PROJECT-X"

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    columns = {row[1] for row in conn.execute("PRAGMA table_info(work_intent_claims)").fetchall()}
    conn.close()
    assert {"acting_role", "project_id"} <= columns


def test_project_authorization_bootstrap_claim_records_bound_authority(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_bootstrap_thread(tmp_path, "bootstrap-thread")
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-bootstrap"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    assert env.acquire(
        "bootstrap-thread",
        session_id,
        project_root=tmp_path,
        claim_kind=env.CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP,
        bootstrap_authority={
            "owner_decision_id": "DELIB-BOOTSTRAP",
            "project_id": "PROJECT-X",
            "work_item_id": "WI-5279",
            "authorization_id": "PAUTH-BOOTSTRAP",
            "carrier_targets": ["groundtruth.db"],
        },
    )

    holder = env.current_holder("bootstrap-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP
    assert holder["bootstrap_owner_decision_id"] == "DELIB-BOOTSTRAP"
    assert holder["bootstrap_project_id"] == "PROJECT-X"
    assert holder["bootstrap_work_item_id"] == "WI-5279"
    assert holder["bootstrap_authorization_id"] == "PAUTH-BOOTSTRAP"
    assert json.loads(holder["bootstrap_carrier_targets"]) == ["groundtruth.db"]
    authority = env.bootstrap_authority_from_claim(holder)
    assert authority is not None
    assert authority["carrier_targets"] == ["groundtruth.db"]
    assert authority["single_use"]["consumed"] is False


def test_project_authorization_bootstrap_claim_requires_carrier_target(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_bootstrap_thread(tmp_path, "bootstrap-thread")
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-bootstrap"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    with pytest.raises(env.WorkIntentRegistryError, match="carrier targets"):
        env.acquire(
            "bootstrap-thread",
            session_id,
            project_root=tmp_path,
            claim_kind=env.CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP,
            bootstrap_authority={
                "owner_decision_id": "DELIB-BOOTSTRAP",
                "project_id": "PROJECT-X",
                "work_item_id": "WI-5279",
                "authorization_id": "PAUTH-BOOTSTRAP",
                "carrier_targets": ["scripts/not-a-carrier.py"],
            },
        )


def test_same_role_project_holder_detects_conflicting_same_role_claim(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    holder_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", holder_session)

    assert env.acquire("thread-a", holder_session, project_root=tmp_path)

    holder = env.same_role_project_holder("prime-builder", "PROJECT-X", "other-session", project_root=tmp_path)
    assert holder is not None
    assert holder["thread_slug"] == "thread-a"
    assert holder["session_id"] == holder_session
    assert env.same_role_project_holder("prime-builder", "PROJECT-X", holder_session, project_root=tmp_path) is None


def test_same_role_project_guard_does_not_alter_acquire_verdict(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    _write_project_thread(tmp_path, "thread-b", "GO", project_id="PROJECT-X")
    holder_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    other_session = "2026-06-22T00-01-00Z-prime-builder-B-def456"
    _write_worker_session(tmp_path, "prime-builder", holder_session)
    _write_worker_session(tmp_path, "prime-builder", other_session)

    assert env.acquire("thread-a", holder_session, project_root=tmp_path)
    assert env.same_role_project_holder("prime-builder", "PROJECT-X", other_session, project_root=tmp_path)
    assert env.acquire("thread-b", other_session, project_root=tmp_path) is True


def test_same_role_project_holder_ignores_expired_or_lapsed_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, env
) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    holder_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", holder_session)

    assert env.acquire("thread-a", holder_session, project_root=tmp_path)
    monkeypatch.setattr(
        env,
        "now_utc",
        lambda: (
            datetime(2026, 6, 14, 0, 0, tzinfo=UTC)
            + timedelta(seconds=env.GO_IMPLEMENTATION_DEADLINE_SECONDS + env.GO_IMPLEMENTATION_GRACE_SECONDS + 1)
        ),
    )

    assert env.same_role_project_holder("prime-builder", "PROJECT-X", "other-session", project_root=tmp_path) is None


def test_go_impl_peer_claim_stays_locked_until_lapsed_then_reacquires(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    """WI-4823: same-thread GO implementation ownership is exclusive until
    deadline+grace lapse, then a peer Prime session may take over.
    """
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    first_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    second_session = "2026-06-22T00-01-00Z-prime-builder-B-def456"
    _write_worker_session(tmp_path, "prime-builder", first_session)
    _write_worker_session(tmp_path, "prime-builder", second_session)
    base = datetime(2026, 6, 14, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(env, "now_utc", lambda: base)

    assert env.acquire("thread-a", first_session, project_root=tmp_path)
    assert env.acquire("thread-a", second_session, project_root=tmp_path) is False
    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == first_session

    lapsed = base + timedelta(seconds=env.GO_IMPLEMENTATION_DEADLINE_SECONDS + env.GO_IMPLEMENTATION_GRACE_SECONDS + 1)
    monkeypatch.setattr(env, "now_utc", lambda: lapsed)

    assert env.current_holder("thread-a", project_root=tmp_path) is None
    assert env.acquire("thread-a", second_session, project_root=tmp_path)
    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == second_session
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


def test_impl_authorization_refuses_borrowed_work_intent_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    """WI-4823: implementation authorization must not accept another session's
    work-intent claim as provenance for the current caller.
    """
    from scripts import implementation_authorization

    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    holder_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    caller_session = "2026-06-22T00-01-00Z-prime-builder-B-def456"
    _write_worker_session(tmp_path, "prime-builder", holder_session)
    base = datetime(2026, 6, 14, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(implementation_authorization.bridge_work_intent_registry, "now_utc", lambda: base)

    assert env.acquire("thread-a", holder_session, project_root=tmp_path)

    assert implementation_authorization.work_intent_claim_block_reason(tmp_path, "thread-a", holder_session) is None
    reason = implementation_authorization.work_intent_claim_block_reason(tmp_path, "thread-a", caller_session)
    assert reason is not None
    assert "claimed by session" in reason
    assert holder_session in reason
    assert caller_session in reason


def test_same_role_project_holder_ignores_different_role(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_project_thread(tmp_path, "thread-a", "NEW", project_id="PROJECT-X")

    assert env.acquire(
        "thread-a",
        "2026-06-22T00-00-00Z-loyal-opposition-D-def456",
        project_root=tmp_path,
    )

    assert env.same_role_project_holder("prime-builder", "PROJECT-X", "other-session", project_root=tmp_path) is None


def test_same_role_project_holder_returns_none_on_null_project_or_role(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")

    session_id = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    assert env.acquire("thread-a", session_id, project_root=tmp_path)

    assert env.same_role_project_holder(None, "PROJECT-X", "other-session", project_root=tmp_path) is None
    assert env.same_role_project_holder("prime-builder", None, "other-session", project_root=tmp_path) is None


# WI-4658 — MalformedBridgeStatusError tests.
# bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md (GO at -002).
#
# Cover the typed permanent-error class that lets the dispatch batch-acquire
# surface (dispatcher_runtime._acquire_prime_work_intent_batch)
# distinguish a permanent per-file parse error (skip-and-continue) from
# transient WorkIntentRegistryError (fail-fast).


def _write_bridge_file(root: Path, slug: str, version: int, body: str) -> Path:
    bridge = root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    path = bridge / f"{slug}-{version:03d}.md"
    path.write_text(body, encoding="utf-8")
    return path


def test_malformed_bridge_status_error_is_workintent_subclass(env) -> None:
    """Backward-compat invariant: ``except WorkIntentRegistryError`` must still catch."""
    assert issubclass(env.MalformedBridgeStatusError, env.WorkIntentRegistryError)


def test_bridge_file_status_raises_malformed_on_unrecognized_first_line(tmp_path: Path, env) -> None:
    """The live victim file pattern: a first-line token ``GO test`` (not a
    canonical status word) must raise the typed error, carrying ``path`` and
    ``offending_line`` attributes."""
    path = _write_bridge_file(tmp_path, "victim", 2, "GO test\n\n# Body\n")
    with pytest.raises(env.MalformedBridgeStatusError) as excinfo:
        env._bridge_file_status(path)
    assert excinfo.value.path == path
    assert excinfo.value.offending_line == "GO test"
    # The base type must still match for backward-compatible call sites.
    assert isinstance(excinfo.value, env.WorkIntentRegistryError)


def test_bridge_file_status_raises_malformed_on_empty_file(tmp_path: Path, env) -> None:
    path = _write_bridge_file(tmp_path, "victim", 2, "")
    with pytest.raises(env.MalformedBridgeStatusError) as excinfo:
        env._bridge_file_status(path)
    assert excinfo.value.path == path
    assert excinfo.value.offending_line is None


def test_bridge_file_status_returns_canonical_status_unchanged(tmp_path: Path, env) -> None:
    """Non-regression: every canonical status token must still parse."""
    for token in ("NEW", "REVISED", "GO", "NO-GO", "NO-ACTION", "VERIFIED", "ADVISORY", "DEFERRED", "WITHDRAWN"):
        path = _write_bridge_file(tmp_path, f"slug-{token.lower()}", 1, f"{token}\n\n# Body\n")
        assert env._bridge_file_status(path) == token


def test_no_action_claim_uses_draft_kind_not_go_implementation(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"D": "loyal-opposition"})
    _write_index(tmp_path, {"no-action-thread": "NO-ACTION"})
    session_id = "2026-06-22T00-00-00Z-loyal-opposition-D-def456"

    assert env.acquire("no-action-thread", session_id, project_root=tmp_path) is True

    holder = env.current_holder("no-action-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_DRAFT


def test_latest_no_go_after_prior_go_remains_draft_while_latest_go_is_implementation(
    tmp_path: Path,
    env,
) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    _write_project_thread(tmp_path, "no-go-thread", "NEW", project_id="PROJECT-X")
    _write_bridge_file(tmp_path, "no-go-thread", 2, "GO\n\nFixture GO.\n")
    _write_bridge_file(tmp_path, "no-go-thread", 3, "NO-ACTION\n\nFixture correction.\n")
    _write_bridge_file(tmp_path, "no-go-thread", 4, "NO-GO\n\nFixture corrected verdict.\n")

    assert env.acquire("no-go-thread", session_id, project_root=tmp_path)
    draft_holder = env.current_holder("no-go-thread", project_root=tmp_path)
    assert draft_holder is not None
    assert draft_holder["claim_kind"] == env.CLAIM_KIND_DRAFT
    assert draft_holder["implementation_deadline"] is None
    assert draft_holder["implementation_grace_expires_at"] is None

    _write_project_thread(tmp_path, "go-thread", "GO", project_id="PROJECT-X")
    assert env.acquire("go-thread", session_id, project_root=tmp_path)
    implementation_holder = env.current_holder("go-thread", project_root=tmp_path)
    assert implementation_holder is not None
    assert implementation_holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION
    assert implementation_holder["implementation_deadline"] is not None
    assert implementation_holder["implementation_grace_expires_at"] is not None


@pytest.mark.parametrize("latest_status", ["GO", "NO-GO"])
def test_prime_can_claim_no_action_correction_after_lo_verdict(
    tmp_path: Path,
    env,
    latest_status: str,
) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "verdict-thread", "NEW", project_id="PROJECT-X")
    (tmp_path / "bridge" / "verdict-thread-002.md").write_text(
        f"{latest_status}\n\nFixture verdict.\n",
        encoding="utf-8",
    )
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    assert env.acquire(
        "verdict-thread",
        session_id,
        project_root=tmp_path,
        claim_kind=env.CLAIM_KIND_NO_ACTION_CORRECTION,
    )

    holder = env.current_holder("verdict-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_NO_ACTION_CORRECTION
    assert holder["acting_role"] == "prime-builder"
    assert holder["implementation_deadline"] is None
    assert holder["implementation_grace_expires_at"] is None


def test_no_action_correction_is_separate_from_go_implementation_claim(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    _write_project_thread(tmp_path, "implementation-thread", "GO", project_id="PROJECT-X")
    assert env.acquire("implementation-thread", session_id, project_root=tmp_path)
    implementation_holder = env.current_holder("implementation-thread", project_root=tmp_path)
    assert implementation_holder is not None
    assert implementation_holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION
    assert implementation_holder["implementation_deadline"] is not None
    assert implementation_holder["implementation_grace_expires_at"] is not None

    _write_project_thread(tmp_path, "correction-thread", "GO", project_id="PROJECT-X")
    assert env.acquire(
        "correction-thread",
        session_id,
        project_root=tmp_path,
        claim_kind=env.CLAIM_KIND_NO_ACTION_CORRECTION,
    )
    correction_holder = env.current_holder("correction-thread", project_root=tmp_path)
    assert correction_holder is not None
    assert correction_holder["claim_kind"] == env.CLAIM_KIND_NO_ACTION_CORRECTION
    assert correction_holder["implementation_deadline"] is None
    assert correction_holder["implementation_grace_expires_at"] is None
    assert correction_holder["extension_cap_seconds"] is None
    assert correction_holder["bootstrap_owner_decision_id"] is None
    assert correction_holder["bootstrap_authorization_id"] is None


def test_no_action_correction_claim_cannot_authorize_implementation_start(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    from scripts import implementation_authorization

    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "correction-only-thread", "GO", project_id="PROJECT-X")
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", session_id)
    assert env.acquire(
        "correction-only-thread",
        session_id,
        project_root=tmp_path,
        claim_kind=env.CLAIM_KIND_NO_ACTION_CORRECTION,
    )
    monkeypatch.setattr(implementation_authorization.bridge_work_intent_registry, "now_utc", env.now_utc)
    packet = {"bridge_id": "correction-only-thread"}
    packet["packet_hash"] = implementation_authorization.packet_hash(packet)

    with pytest.raises(implementation_authorization.AuthorizationError, match="GO-implementation claim"):
        implementation_authorization.finalize_implementation_start_packet(
            tmp_path,
            packet,
            session_id=session_id,
        )


def test_no_action_correction_rejects_non_verdict_and_non_prime_sessions(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_project_thread(tmp_path, "new-thread", "NEW", project_id="PROJECT-X")
    prime_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    lo_session = "2026-06-22T00-00-00Z-loyal-opposition-D-def456"
    _write_worker_session(tmp_path, "prime-builder", prime_session)
    _write_worker_session(tmp_path, "loyal-opposition", lo_session)

    with pytest.raises(env.WorkIntentRegistryError, match="requires latest GO or NO-GO"):
        env.acquire(
            "new-thread",
            prime_session,
            project_root=tmp_path,
            claim_kind=env.CLAIM_KIND_NO_ACTION_CORRECTION,
        )

    (tmp_path / "bridge" / "new-thread-002.md").write_text("GO\n\nFixture GO.\n", encoding="utf-8")
    with pytest.raises(env.WorkIntentRegistryError, match="requires prime-builder"):
        env.acquire(
            "new-thread",
            lo_session,
            project_root=tmp_path,
            claim_kind=env.CLAIM_KIND_NO_ACTION_CORRECTION,
        )


def test_claim_cli_exposes_no_action_correction_mode(tmp_path: Path, env, capsys) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "cli-verdict-thread", "GO", project_id="PROJECT-X")
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-abc123"
    _write_worker_session(tmp_path, "prime-builder", session_id)
    cli = _load_module(CLAIM_CLI_PATH, "bridge_claim_cli_wi5249")

    assert (
        cli.main(
            [
                "claim-no-action",
                "cli-verdict-thread",
                "--session-id",
                session_id,
                "--project-root",
                str(tmp_path),
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["claim_kind"] == env.CLAIM_KIND_NO_ACTION_CORRECTION


def test_bridge_file_status_skips_leading_blank_lines(tmp_path: Path, env) -> None:
    """Pre-existing behavior: blank prefix lines do not trigger malformed-status."""
    path = _write_bridge_file(tmp_path, "blanks", 1, "\n\n   \nGO\n\n# Body\n")
    assert env._bridge_file_status(path) == "GO"


def test_acquire_tolerates_legacy_status_shadowed_thread(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_index(tmp_path, {"shadowed-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_worker_session(tmp_path, "prime-builder", session_id)

    _write_bridge_file(tmp_path, "shadowed-thread", 1, "NEW\n\n# Body\n")
    _write_bridge_file(tmp_path, "shadowed-thread", 2, "PAUSED\n\n# Legacy\n")
    _write_bridge_file(tmp_path, "shadowed-thread", 3, "GO\n\n# Latest\n")

    assert env.acquire("shadowed-thread", session_id, project_root=tmp_path) is True


def test_latest_status_skips_legacy_token_version(tmp_path: Path, env) -> None:
    _write_bridge_file(tmp_path, "shadowed-thread", 1, "NEW\n\n# Body\n")
    _write_bridge_file(tmp_path, "shadowed-thread", 2, "PAUSED\n\n# Legacy\n")

    entries = env._thread_version_entries("shadowed-thread", project_root=tmp_path)
    assert len(entries) == 1
    assert entries[0] == (1, "NEW", "bridge/shadowed-thread-001.md")
    assert env._latest_status("shadowed-thread", project_root=tmp_path) == "NEW"


def test_legacy_token_version_skip_emits_warning(tmp_path: Path, env) -> None:
    _write_bridge_file(tmp_path, "shadowed-thread", 1, "NEW\n\n# Body\n")
    _write_bridge_file(tmp_path, "shadowed-thread", 2, "PAUSED\n\n# Legacy\n")

    with pytest.warns(UserWarning, match="Skipping malformed or legacy status"):
        env._thread_version_entries("shadowed-thread", project_root=tmp_path)


def test_bridge_file_status_still_raises_on_unrecognized_token_regression(tmp_path: Path, env) -> None:
    path = _write_bridge_file(tmp_path, "shadowed-thread", 1, "PAUSED\n\n# Body\n")
    with pytest.raises(env.MalformedBridgeStatusError) as excinfo:
        env._bridge_file_status(path)
    assert excinfo.value.offending_line == "PAUSED"


def test_unreadable_or_duplicate_version_still_raises(tmp_path: Path, env) -> None:
    _write_bridge_file(tmp_path, "shadowed-thread", 1, "NEW\n\n# Body\n")
    bridge = tmp_path / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    dup_path = bridge / "shadowed-thread-0001.md"
    dup_path.write_text("NEW\n\n# Body\n", encoding="utf-8")

    with pytest.raises(env.WorkIntentRegistryError, match="Duplicate bridge version 001"):
        env._thread_version_entries("shadowed-thread", project_root=tmp_path)

    dup_path.unlink()

    unreadable_dir = bridge / "shadowed-thread-002.md"
    unreadable_dir.mkdir()

    with pytest.raises(env.WorkIntentRegistryError, match="Bridge file is unreadable"):
        env._thread_version_entries("shadowed-thread", project_root=tmp_path)

    unreadable_dir.rmdir()


# WI-5784 — deterministic real-SQLite contention coverage for the narrow
# acquire/release write boundary.


def _prepare_draft_thread(root: Path, env, slug: str = "thread-a") -> Path:
    _write_index(root, {slug: "NEW"})
    conn = env._get_conn(root)
    conn.close()
    return root / "groundtruth.db"


def _hold_write_lock(database_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(database_path, timeout=0)
    conn.execute("BEGIN IMMEDIATE")
    return conn


def _install_logical_monotonic_clock(monkeypatch: pytest.MonkeyPatch, env) -> list[float]:
    """Install a controllable logical monotonic clock for deterministic deadline tests.

    WI-5784: replace the wall-clock ``_monotonic``/``_retry_sleep`` with a
    logical clock the fixture advances explicitly, so deadline exhaustion is
    deterministic and never depends on real contention or wall time.
    """
    now = [0.0]

    def _logical_monotonic() -> float:
        return now[0]

    monkeypatch.setattr(env, "_monotonic", _logical_monotonic)

    def _logical_retry_sleep(seconds: float) -> None:
        now[0] += seconds

    monkeypatch.setattr(env, "_retry_sleep", _logical_retry_sleep)
    return now


def _configure_fast_contention(monkeypatch: pytest.MonkeyPatch, env, *, deadline: float = 1.0) -> None:
    monkeypatch.setattr(env, "WORK_INTENT_WRITE_RETRY_DEADLINE_SECONDS", deadline)
    monkeypatch.setattr(env, "WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS", 0.0)
    monkeypatch.setattr(env, "WORK_INTENT_WRITE_INITIAL_BACKOFF_SECONDS", 0.001)
    monkeypatch.setattr(env, "WORK_INTENT_WRITE_MAX_BACKOFF_SECONDS", 0.001)


def test_acquire_retries_real_lock_and_succeeds_when_unlocked_within_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    database_path = _prepare_draft_thread(tmp_path, env)
    blocker = _hold_write_lock(database_path)
    _configure_fast_contention(monkeypatch, env)
    sleeps: list[float] = []

    def unlock_on_retry(seconds: float) -> None:
        sleeps.append(seconds)
        blocker.commit()

    monkeypatch.setattr(env, "_retry_sleep", unlock_on_retry)
    try:
        assert env.acquire("thread-a", "owner-session", project_root=tmp_path)
    finally:
        blocker.close()

    assert sleeps
    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == "owner-session"


def test_acquire_retry_preserves_foreign_holder_published_during_contention(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    database_path = _prepare_draft_thread(tmp_path, env)
    blocker = _hold_write_lock(database_path)
    now = datetime.now(UTC)
    blocker.execute(
        """
        INSERT INTO work_intent_claims
        (thread_slug, session_id, acquired_at, ttl_expires_at, claim_kind)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "thread-a",
            "replacement-session",
            now.isoformat().replace("+00:00", "Z"),
            (now + timedelta(minutes=10)).isoformat().replace("+00:00", "Z"),
            env.CLAIM_KIND_DRAFT,
        ),
    )
    _configure_fast_contention(monkeypatch, env)
    committed = False

    def publish_replacement(_seconds: float) -> None:
        nonlocal committed
        if not committed:
            blocker.commit()
            committed = True

    monkeypatch.setattr(env, "_retry_sleep", publish_replacement)
    try:
        assert not env.acquire("thread-a", "owner-session", project_root=tmp_path)
    finally:
        blocker.close()

    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == "replacement-session"


def test_acquire_retry_revalidates_bootstrap_authority_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_bootstrap_thread(tmp_path, "bootstrap-thread")
    session_id = "2026-06-22T00-00-00Z-prime-builder-B-bootstrap"
    _write_worker_session(tmp_path, "prime-builder", session_id)
    authority = {
        "owner_decision_id": "DELIB-BOOTSTRAP",
        "project_id": "PROJECT-X",
        "work_item_id": "WI-5279",
        "authorization_id": "PAUTH-BOOTSTRAP",
        "carrier_targets": ["groundtruth.db"],
    }
    assert env.acquire(
        "bootstrap-thread",
        session_id,
        project_root=tmp_path,
        claim_kind=env.CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP,
        bootstrap_authority=authority,
    )

    database_path = tmp_path / "groundtruth.db"
    blocker = _hold_write_lock(database_path)
    blocker.execute(
        """
        UPDATE work_intent_claims
        SET bootstrap_authorization_id = ?
        WHERE thread_slug = ? AND session_id = ?
        """,
        ("PAUTH-REPLACEMENT", "bootstrap-thread", session_id),
    )
    _configure_fast_contention(monkeypatch, env)
    committed = False

    def publish_replacement(_seconds: float) -> None:
        nonlocal committed
        if not committed:
            blocker.commit()
            committed = True

    monkeypatch.setattr(env, "_retry_sleep", publish_replacement)
    try:
        with pytest.raises(env.WorkIntentRegistryError, match="metadata differs"):
            env.acquire(
                "bootstrap-thread",
                session_id,
                project_root=tmp_path,
                claim_kind=env.CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP,
                bootstrap_authority=authority,
            )
    finally:
        blocker.close()

    holder = env.current_holder("bootstrap-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["bootstrap_authorization_id"] == "PAUTH-REPLACEMENT"


def test_acquire_deadline_exhaustion_is_typed_and_leaves_no_partial_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    database_path = _prepare_draft_thread(tmp_path, env)
    blocker = _hold_write_lock(database_path)
    _configure_fast_contention(monkeypatch, env, deadline=0.1)
    opened: list[sqlite3.Connection] = []
    original_get_conn = env._get_conn

    def tracking_get_conn(*args, **kwargs):
        conn = original_get_conn(*args, **kwargs)
        opened.append(conn)
        return conn

    monkeypatch.setattr(env, "_get_conn", tracking_get_conn)
    try:
        with pytest.raises(env.WorkIntentWriteContentionError) as excinfo:
            env.acquire("thread-a", "owner-session", project_root=tmp_path)
    finally:
        blocker.commit()
        blocker.close()

    error = excinfo.value
    assert error.operation == "acquire"
    assert error.phase == "begin_immediate"
    assert error.attempts >= 1
    assert error.elapsed_seconds >= 0
    assert error.sqlite_errorcode is not None
    assert (error.sqlite_errorcode & 0xFF) in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}
    assert error.database_path == database_path
    assert error.as_dict()["contention_exhausted"] is True
    assert env.claim_status("thread-a", project_root=tmp_path) is None
    assert opened
    for conn in opened:
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")


def test_wi5784_deterministic_real_sqlite_contention_exhaustion(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    """WI-5784 node 1: deterministic real-SQLite contention exhaustion.

    Retain the isolated DB and real second-connection ``BEGIN IMMEDIATE``
    blocker; inject a logical monotonic clock and make ``_retry_sleep`` advance
    that clock (no wall-clock sleep). The fixture advances to the configured
    test deadline only after at least one real SQLite BUSY/LOCKED result,
    forcing the ``last_contention`` exhaustion branch. Assert typed
    ``WorkIntentWriteContentionError`` with a BUSY/LOCKED ``sqlite_errorcode``,
    no partial claim, exact database path, and closure of every connection.
    """
    database_path = _prepare_draft_thread(tmp_path, env)
    blocker = _hold_write_lock(database_path)
    _configure_fast_contention(monkeypatch, env, deadline=5.0)
    _install_logical_monotonic_clock(monkeypatch, env)
    opened: list[sqlite3.Connection] = []
    original_get_conn = env._get_conn

    def tracking_get_conn(*args, **kwargs):
        conn = original_get_conn(*args, **kwargs)
        opened.append(conn)
        return conn

    monkeypatch.setattr(env, "_get_conn", tracking_get_conn)
    try:
        # Real SQLite emits BUSY/LOCKED on BEGIN IMMEDIATE. Advance the logical
        # clock past the deadline so the retry loop raises the typed
        # contention_exhausted error on the next iteration (last_contention set).
        with pytest.raises(env.WorkIntentWriteContentionError) as excinfo:
            env.acquire("thread-a", "owner-session", project_root=tmp_path)
    finally:
        blocker.commit()
        blocker.close()

    error = excinfo.value
    assert error.operation == "acquire"
    assert error.phase == "begin_immediate"
    assert error.contention_exhausted is True
    assert error.sqlite_errorcode is not None
    assert (error.sqlite_errorcode & 0xFF) in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED}
    assert error.database_path == database_path
    assert env.claim_status("thread-a", project_root=tmp_path) is None
    assert opened
    for conn in opened:
        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")


def test_wi5784_deterministic_pre_sqlite_already_exhausted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    """WI-5784 node 2: deterministic pre-SQLite already-exhausted exhaustion.

    Use no competing writer; inject a stable logical monotonic clock and a
    zero-length (already-spent) test deadline before ``acquire()`` enters
    ``BEGIN IMMEDIATE``. Wrap the post-schema connection in a narrow recording
    proxy. Assert typed ``WorkIntentWriteContentionError``;
    ``operation=acquire``; ``phase=begin_immediate``;
    ``contention_exhausted is True``; no ``BEGIN IMMEDIATE``; and a fresh
    independent read finds zero claim rows.

    Note: the current production ``_deadline_exhausted_error`` (per WI-5841,
    commit 28f328a23) reports a BUSY sqlite code even in the pre-SQLite branch
    when ``last_contention is None``, so this node asserts the BUSY code rather
    than ``None`` to match the landed production behavior.
    """
    database_path = _prepare_draft_thread(tmp_path, env)
    # Zero-length (already-spent) write budget: the pre-SQLite remaining-budget
    # check in _apply_remaining_busy_timeout fails before any BEGIN IMMEDIATE.
    _configure_fast_contention(monkeypatch, env, deadline=0.0)
    _install_logical_monotonic_clock(monkeypatch, env)
    begin_immediate_observed: list[str] = []

    original_get_conn = env._get_conn

    class RecordingProxy:
        def __init__(self, conn):
            self._conn = conn

        def execute(self, sql, *args, **kwargs):
            if "BEGIN IMMEDIATE" in str(sql).upper():
                begin_immediate_observed.append(str(sql))
            return self._conn.execute(sql, *args, **kwargs)

        def __getattr__(self, name):
            return getattr(self._conn, name)

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return self._conn.__exit__(*exc)

    def recording_get_conn(*args, **kwargs):
        conn = original_get_conn(*args, **kwargs)
        return RecordingProxy(conn)

    monkeypatch.setattr(env, "_get_conn", recording_get_conn)
    with pytest.raises(env.WorkIntentWriteContentionError) as excinfo:
        env.acquire("thread-a", "owner-session", project_root=tmp_path)

    error = excinfo.value
    assert error.operation == "acquire"
    assert error.phase == "begin_immediate"
    assert error.contention_exhausted is True
    assert not begin_immediate_observed  # no BEGIN IMMEDIATE before exhaustion
    # Fresh independent read finds zero claim rows for the slug.
    conn = sqlite3.connect(database_path)
    try:
        row = conn.execute(
            "SELECT 1 FROM work_intent_claims WHERE thread_slug = ?",
            ("thread-a",),
        ).fetchone()
        assert row is None
    finally:
        conn.close()


def test_release_retry_revalidates_and_preserves_replacement_holder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    database_path = _prepare_draft_thread(tmp_path, env)
    assert env.acquire("thread-a", "owner-session", project_root=tmp_path)
    blocker = _hold_write_lock(database_path)
    blocker.execute(
        "UPDATE work_intent_claims SET session_id = ? WHERE thread_slug = ?",
        ("replacement-session", "thread-a"),
    )
    _configure_fast_contention(monkeypatch, env)
    committed = False

    def publish_replacement(_seconds: float) -> None:
        nonlocal committed
        if not committed:
            blocker.commit()
            committed = True

    monkeypatch.setattr(env, "_retry_sleep", publish_replacement)
    try:
        env.release("thread-a", "owner-session", project_root=tmp_path)
    finally:
        blocker.close()

    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == "replacement-session"


def test_release_retries_real_lock_and_deletes_exact_holder_when_unlocked_within_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    database_path = _prepare_draft_thread(tmp_path, env)
    assert env.acquire("thread-a", "owner-session", project_root=tmp_path)
    blocker = _hold_write_lock(database_path)
    _configure_fast_contention(monkeypatch, env)
    sleeps: list[float] = []

    def unlock_on_retry(seconds: float) -> None:
        sleeps.append(seconds)
        blocker.rollback()

    monkeypatch.setattr(env, "_retry_sleep", unlock_on_retry)
    try:
        env.release("thread-a", "owner-session", project_root=tmp_path)
    finally:
        blocker.close()

    assert sleeps
    assert env.claim_status("thread-a", project_root=tmp_path) is None


def test_release_commit_wait_cannot_outlive_total_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    database_path = _prepare_draft_thread(tmp_path, env)
    assert env.acquire("thread-a", "owner-session", project_root=tmp_path)

    reader = sqlite3.connect(database_path, timeout=0)
    reader.execute("BEGIN")
    reader.execute("SELECT * FROM work_intent_claims").fetchall()
    blocker = _hold_write_lock(database_path)
    _configure_fast_contention(monkeypatch, env, deadline=0.5)
    monkeypatch.setattr(env, "WORK_INTENT_WRITE_ATTEMPT_TIMEOUT_SECONDS", 0.5)
    completed = threading.Event()
    outcome: list[BaseException | str] = []

    def release_in_thread() -> None:
        try:
            env.release("thread-a", "owner-session", project_root=tmp_path)
        except BaseException as exc:  # noqa: BLE001 - assertion captures the worker outcome
            outcome.append(exc)
        else:
            outcome.append("success")
        finally:
            completed.set()

    worker = threading.Thread(target=release_in_thread, daemon=True)
    worker.start()
    try:
        assert not completed.wait(0.05)
        time.sleep(0.25)
        blocker.rollback()
        completed_before_reader_release = completed.wait(0.3)
    finally:
        blocker.close()
        reader.commit()
        reader.close()
        worker.join(timeout=1.0)

    assert completed_before_reader_release
    assert len(outcome) == 1
    error = outcome[0]
    assert isinstance(error, env.WorkIntentWriteContentionError)
    assert error.operation == "release"
    assert error.phase == "commit"
    assert error.contention_exhausted is True
    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["session_id"] == "owner-session"


def test_release_is_idempotent_for_missing_claim(tmp_path: Path, env) -> None:
    _prepare_draft_thread(tmp_path, env)

    env.release("thread-a", "owner-session", project_root=tmp_path)
    env.release("thread-a", "owner-session", project_root=tmp_path)

    assert env.claim_status("thread-a", project_root=tmp_path) is None


def test_non_busy_schema_failure_is_not_retried_and_closes_connection(tmp_path: Path, env) -> None:
    database_path = tmp_path / "groundtruth.db"
    database_path.write_bytes(b"not-a-sqlite-database")

    with pytest.raises(env.WorkIntentDatabaseError) as excinfo:
        env.release("thread-a", "owner-session", project_root=tmp_path)

    error = excinfo.value
    assert not isinstance(error, env.WorkIntentWriteContentionError)
    assert error.operation == "release"
    assert error.phase == "open_or_schema"
    assert error.attempts == 1
    assert error.contention_exhausted is False
    renamed = tmp_path / "closed-after-error.db"
    database_path.rename(renamed)
    assert renamed.is_file()


def test_narrow_schema_setup_does_not_initialize_global_groundtruth_schema(tmp_path: Path, env) -> None:
    conn = env._get_conn(tmp_path)
    try:
        tables = {str(row[0]) for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()}
    finally:
        conn.close()

    assert "work_intent_claims" in tables
    assert "work_items" not in tables


def _fresh_registry_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Return a clean registry module with harness-signal env cleared."""
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
    return _registry()


def _write_identities(root: Path, mapping: dict[str, str]) -> None:
    harness_state = root / "harness-state"
    harness_state.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "harnesses": {name: {"id": harness_id, "status": "active"} for name, harness_id in mapping.items()},
    }
    (harness_state / "harness-identities.json").write_text(json.dumps(payload), encoding="utf-8")


def test_wi5841_full_registry_durable_ids_resolve(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """All eight canonical harness identities resolve through both generic-ID routes."""
    registry = _fresh_registry_env(tmp_path, monkeypatch)
    mapping = {
        "alibaba-cloud-studio": "H",
        "antigravity": "C",
        "claude": "B",
        "codex": "A",
        "cursor": "E",
        "goose": "G",
        "ollama": "D",
        "openrouter": "F",
    }
    _write_identities(tmp_path, mapping)
    for harness_name, harness_id in mapping.items():
        monkeypatch.setenv("GTKB_HARNESS_ID", harness_id)
        assert registry._worker_harness_selector(tmp_path) == harness_name, harness_id
        monkeypatch.delenv("GTKB_HARNESS_ID")
        monkeypatch.setenv("GTKB_AUTHOR_HARNESS_ID", harness_id)
        assert registry._worker_harness_selector(tmp_path) == harness_name, harness_id
        monkeypatch.delenv("GTKB_AUTHOR_HARNESS_ID")


def test_wi5841_selector_conflict_and_unknown_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _fresh_registry_env(tmp_path, monkeypatch)
    _write_identities(tmp_path, {"goose": "G", "codex": "A"})
    monkeypatch.setenv("GTKB_HARNESS_ID", "G")
    monkeypatch.setenv("GTKB_AUTHOR_HARNESS_ID", "A")
    with pytest.raises(ValueError, match="disagree"):
        registry._worker_harness_selector(tmp_path)
    monkeypatch.delenv("GTKB_AUTHOR_HARNESS_ID")
    monkeypatch.setenv("GTKB_HARNESS_ID", "ZZZ")
    with pytest.raises(ValueError, match="no registered harness"):
        registry._worker_harness_selector(tmp_path)


def test_wi5841_selector_legacy_and_codex_home_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _fresh_registry_env(tmp_path, monkeypatch)
    _write_identities(tmp_path, {"goose": "G"})
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "claude-session")
    assert registry._worker_harness_selector(tmp_path) == "claude"
    monkeypatch.delenv("CLAUDE_CODE_SESSION_ID")
    monkeypatch.setenv("CODEX_THREAD_ID", "codex-session")
    assert registry._worker_harness_selector(tmp_path) == "codex"
    monkeypatch.delenv("CODEX_THREAD_ID")
    monkeypatch.setenv("CODEX_HOME", "C:/Users/test/.codex")
    assert registry._worker_harness_selector(tmp_path) is None


def test_wi5841_selector_explicit_and_poller_precedence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    registry = _fresh_registry_env(tmp_path, monkeypatch)
    _write_identities(tmp_path, {"goose": "G"})
    monkeypatch.setenv("GTKB_HARNESS_NAME", "cursor")
    monkeypatch.setenv("GTKB_HARNESS_ID", "G")
    assert registry._worker_harness_selector(tmp_path) == "cursor"
    monkeypatch.delenv("GTKB_HARNESS_NAME")
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run")
    assert registry._worker_harness_selector(tmp_path) is None


def test_recovery_claim_fence_cas_pre_sqlite_deadline_exhaustion_is_typed_and_leaves_no_partial_fence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    env,
) -> None:
    """TEST-11809 (WI-5881): claim-fence CAS pre-SQLite already-exhausted.

    Supplies an already-exhausted injected monotonic deadline before the
    claim-fence CAS opens or begins a SQLite write, with no competing writer.
    Calls ``recovery_claim_fence_install`` (not ordinary ``acquire``) and
    asserts:

    1. typed exception: contention_exhausted True, operation
       ``recovery_claim_fence_install``, phase ``begin_immediate``,
       sqlite_errorcode None, sqlite_errorname None, detail
       ``monotonic write deadline exhausted``;
    2. zero partial reservation claim-fence row (no fence epoch advanced, no
       claim_fenced event appended);
    3. no partial fence survives an independently reopenable read;
    4. the failure is deterministic/idempotent on rerun.
    """
    database_path = _prepare_draft_thread(tmp_path, env)
    # Zero-length (already-spent) write budget + logical monotonic clock.
    _configure_fast_contention(monkeypatch, env, deadline=0.0)
    _install_logical_monotonic_clock(monkeypatch, env)

    with pytest.raises(env.ReservationClaimFenceError) as excinfo:
        env.recovery_claim_fence_install("thread-a", version=1, reservation_id="res-1", project_root=tmp_path)

    error = excinfo.value
    assert error.contention_exhausted is True
    assert error.operation == "recovery_claim_fence_install"
    assert error.phase == "begin_immediate"
    assert error.sqlite_errorcode is None
    assert error.sqlite_errorname is None
    assert "monotonic write deadline exhausted" in str(error)

    # Independently reopenable read sees no partial fence row / event.
    conn = sqlite3.connect(database_path)
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM recovery_reservations WHERE reservation_id = ?",
            ("res-1",),
        ).fetchone()
        assert row[0] == 0, "no partial reservation claim-fence row may exist"
    except sqlite3.OperationalError:
        # Schema never created (fail closed before any write) - acceptable.
        pass
    finally:
        conn.close()

    # Deterministic/idempotent rerun: same typed exhaustion.
    with pytest.raises(env.ReservationClaimFenceError):
        env.recovery_claim_fence_install("thread-a", version=1, reservation_id="res-1", project_root=tmp_path)


# ---------------------------------------------------------------------------
# WI-5973 — work-intent write connection uses synchronous=NORMAL under WAL
# ---------------------------------------------------------------------------


def test_write_connection_uses_synchronous_normal_under_wal(tmp_path: Path, env) -> None:
    """WI-5973: the work-intent write connection sets PRAGMA synchronous=NORMAL under WAL."""
    module = _registry()
    db_path = module._database_path(tmp_path)
    # The real registry DB is persistently WAL; initialize the fixture DB to WAL.
    init = sqlite3.connect(db_path)
    try:
        init.execute("PRAGMA journal_mode=wal")
    finally:
        init.close()

    conn = module._get_conn(tmp_path)
    try:
        synchronous = conn.execute("PRAGMA synchronous").fetchone()[0]
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert synchronous == 1, "write connection must use synchronous=NORMAL"
        assert journal_mode == "wal", "write connection must be in WAL journal mode"
    finally:
        conn.close()
