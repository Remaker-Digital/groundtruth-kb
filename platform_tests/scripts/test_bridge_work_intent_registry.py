"""WI-4540 per-session guard-reader tests for the go_implementation claim.

bridge/gtkb-wi4540-per-session-role-marker-context-envelope-003.md (GO at -004).

These tests exercise the WI-4540 change to the WI-4534 role-eligibility guard
(``scripts.bridge_work_intent_registry._interactive_marker_role`` via
``acquire``): an owner-declared interactive Prime session is recognized through
the PER-SESSION marker (``.claude/session/role-<sanitized_session_id>.json``)
keyed under — and validated against — the querying session id. This is the
GO's required demonstration that "the WI-4534 guard's interactive branch now
finds a valid per-session marker written from the same interactive context,
under the canonical id."

Every oracle is the production ``acquire()`` outcome (raise vs. acquired) plus
the persisted claim record. The legacy single-file fallback path is covered by
``platform_tests/scripts/test_work_intent_role_eligibility.py``.
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REGISTRY_PATH = SCRIPTS_DIR / "bridge_work_intent_registry.py"

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


@pytest.fixture
def env(monkeypatch):
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    registry = _registry()
    base = datetime(2026, 6, 14, 0, 0, tzinfo=UTC)
    monkeypatch.setattr(registry, "now_utc", lambda: base)
    return registry


def test_go_impl_allowed_for_uuid_session_with_per_session_prime_marker(tmp_path: Path, env) -> None:
    """F3/b realized via the per-session marker: an owner-declared interactive
    Prime session (raw-UUID id) is accepted when a per-session Prime marker
    keyed+validated under that id exists."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_per_session_marker(tmp_path, "prime-builder", session_id)

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


def test_legacy_fallback_when_no_per_session_marker(tmp_path: Path, env) -> None:
    """Absent a per-session marker, the guard falls back to the legacy single-file
    marker (preserved transition behavior)."""
    _write_registry(tmp_path, {"B": "prime-builder", "D": "loyal-opposition"})
    _write_index(tmp_path, {"go-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_legacy_marker(tmp_path, "prime-builder", session_id=session_id)

    assert env.acquire("go-thread", session_id, project_root=tmp_path) is True
    holder = env.current_holder("go-thread", project_root=tmp_path)
    assert holder is not None
    assert holder["claim_kind"] == env.CLAIM_KIND_GO_IMPLEMENTATION


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

    assert env.acquire(
        "thread-a",
        "2026-06-22T00-00-00Z-prime-builder-B-abc123",
        project_root=tmp_path,
    )
    holder = env.current_holder("thread-a", project_root=tmp_path)
    assert holder is not None
    assert holder["acting_role"] == "prime-builder"
    assert holder["project_id"] == "PROJECT-X"
    assert env.project_id_for_thread("thread-a", project_root=tmp_path) == "PROJECT-X"

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    columns = {row[1] for row in conn.execute("PRAGMA table_info(work_intent_claims)").fetchall()}
    conn.close()
    assert {"acting_role", "project_id"} <= columns


def test_same_role_project_holder_detects_conflicting_same_role_claim(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    holder_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"

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

    assert env.acquire("thread-a", holder_session, project_root=tmp_path)
    assert env.same_role_project_holder("prime-builder", "PROJECT-X", other_session, project_root=tmp_path)
    assert env.acquire("thread-b", other_session, project_root=tmp_path) is True


def test_same_role_project_holder_ignores_expired_or_lapsed_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, env
) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_project_thread(tmp_path, "thread-a", "GO", project_id="PROJECT-X")
    holder_session = "2026-06-22T00-00-00Z-prime-builder-B-abc123"

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

    assert env.acquire(
        "thread-a",
        "2026-06-22T00-00-00Z-prime-builder-B-abc123",
        project_root=tmp_path,
    )

    assert env.same_role_project_holder(None, "PROJECT-X", "other-session", project_root=tmp_path) is None
    assert env.same_role_project_holder("prime-builder", None, "other-session", project_root=tmp_path) is None


# WI-4658 — MalformedBridgeStatusError tests.
# bridge/gtkb-dispatch-malformed-status-token-quarantine-001.md (GO at -002).
#
# Cover the typed permanent-error class that lets the dispatch batch-acquire
# surface (cross_harness_bridge_trigger._acquire_prime_work_intent_batch)
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
    for token in ("NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED", "WITHDRAWN"):
        path = _write_bridge_file(tmp_path, f"slug-{token.lower()}", 1, f"{token}\n\n# Body\n")
        assert env._bridge_file_status(path) == token


def test_bridge_file_status_skips_leading_blank_lines(tmp_path: Path, env) -> None:
    """Pre-existing behavior: blank prefix lines do not trigger malformed-status."""
    path = _write_bridge_file(tmp_path, "blanks", 1, "\n\n   \nGO\n\n# Body\n")
    assert env._bridge_file_status(path) == "GO"


def test_acquire_tolerates_legacy_status_shadowed_thread(tmp_path: Path, env) -> None:
    _write_registry(tmp_path, {"B": "prime-builder"})
    _write_index(tmp_path, {"shadowed-thread": "GO"})
    session_id = "26c2349e-1cd0-4024-acef-f934b35fea4e"
    _write_per_session_marker(tmp_path, "prime-builder", session_id)

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
