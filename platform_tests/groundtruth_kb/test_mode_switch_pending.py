"""Tests for groundtruth_kb.mode_switch.pending.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criterion #6:
next-session-effectiveness via the pending-transaction queue.

WI-3342 IP-6: ``apply_pending`` drains queued transactions through
``apply_role_switch``, which was migrated to read the harness role map from the
DB-backed registry projection ``harness-state/harness-registry.json`` and to
persist the post-switch role map through the DB ``harnesses`` table +
projection regeneration (the transitional ``role-assignments.json`` write was
removed). The fixtures seed a real ``groundtruth.db`` + generated projection;
post-write assertions read the regenerated projection.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import (  # noqa: E402
    generate_harness_projection,
)
from groundtruth_kb.mode_switch.pending import (  # noqa: E402
    apply_pending,
    defer_role_switch,
    list_pending,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_workspace(root: Path) -> None:
    """Seed a real ``groundtruth.db`` registry + generated projection + INDEX.

    A real DB is required: ``apply_pending`` -> ``apply_role_switch`` persists
    the post-switch role map through the DB ``harnesses`` table and regenerates
    the projection — the surface post-write assertions read. Harness A (codex)
    starts loyal-opposition, harness B (claude) prime-builder.
    """
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    for harness_id, harness_name, role_set in (
        ("A", "codex", ["loyal-opposition"]),
        ("B", "claude", ["prime-builder"]),
    ):
        db.insert_harness(
            id=harness_id,
            harness_name=harness_name,
            harness_type=harness_name,
            role=role_set,
            changed_by="test",
            change_reason="WI-3342 IP-6 mode-switch pending fixture",
            status="active",
        )
    generate_harness_projection(db, root)
    _write(
        root / "bridge" / "INDEX.md",
        "Document: foo\nVERIFIED: bridge/foo-001.md\n",
    )


def _read_role_map(root: Path) -> dict[str, Any]:
    """Return ``{harness_id: role_set}`` from the regenerated registry projection."""
    projection = json.loads(
        (root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8")
    )
    return {
        str(record["id"]): record.get("role")
        for record in projection.get("harnesses", [])
        if isinstance(record, dict) and record.get("id")
    }


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


def test_defer_role_switch_writes_pending_file(project_root: Path) -> None:
    _seed_workspace(project_root)
    path = defer_role_switch(
        project_root, "claude", "loyal-opposition", change_reason="defer test"
    )
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["harness_id_or_name"] == "claude"
    assert data["role"] == "loyal-opposition"


def test_list_pending_returns_empty_when_no_queue(project_root: Path) -> None:
    assert list_pending(project_root) == []


def test_apply_pending_idempotent_on_empty_queue(project_root: Path) -> None:
    _seed_workspace(project_root)
    assert apply_pending(project_root) == []


def test_apply_pending_drains_and_archives(project_root: Path) -> None:
    _seed_workspace(project_root)
    # WI-3342 IP-6: target harness B (claude) by its durable id — apply_role_switch
    # resolves the registry projection by harness id (records carry harness_name,
    # not the legacy ``name`` key).
    pending_path = defer_role_switch(
        project_root, "B", "loyal-opposition", change_reason="drain test"
    )
    results = apply_pending(project_root)
    assert len(results) == 1
    assert results[0].applied is True
    assert not pending_path.exists()
    applied_dir = project_root / ".gtkb-state" / "mode-switches" / "applied"
    assert applied_dir.is_dir()
    assert any(applied_dir.iterdir())


def test_apply_pending_leaves_failed_in_pending_with_logged_error(project_root: Path) -> None:
    """Failed pending entries stay in pending/ with an error captured."""
    _seed_workspace(project_root)
    # Defer with an invalid role; apply will fail validation.
    pending_path = defer_role_switch(
        project_root, "claude", "no-such-role", change_reason="fail test"
    )
    results = apply_pending(project_root)
    assert len(results) == 1
    assert results[0].applied is False
    assert results[0].error is not None
    assert pending_path.exists()  # still in pending/


def test_next_session_initialization_applies_pending_and_state_matches_deferred_request(
    project_root: Path,
) -> None:
    """Acceptance criterion #6: deferred request becomes effective at next session start."""
    _seed_workspace(project_root)
    # WI-3342 IP-6: target harness B (claude) by its durable id.
    defer_role_switch(
        project_root, "B", "loyal-opposition", change_reason="next-session test"
    )
    apply_pending(project_root)
    # WI-3342 IP-6: the post-switch role surface is the regenerated registry
    # projection, not the retired role-assignments.json.
    role_map = _read_role_map(project_root)
    assert role_map["B"] == ["loyal-opposition"]
