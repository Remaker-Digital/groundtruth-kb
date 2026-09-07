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
    starts loyal-opposition, harness B (claude) loyal-opposition so a deferred
    B -> prime-builder request creates a valid candidate without rewriting A.
    """
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    for harness_id, harness_name, role_set in (
        ("A", "codex", ["loyal-opposition"]),
        ("B", "claude", ["loyal-opposition"]),
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
    _write(
        root / "bridge" / "foo-001.md",
        "VERIFIED\n",
    )


def _read_role_map(root: Path) -> dict[str, Any]:
    """Return ``{harness_id: role_set}`` from the regenerated registry projection."""
    projection = json.loads((root / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    return {
        str(record["id"]): record.get("role")
        for record in projection.get("harnesses", [])
        if isinstance(record, dict) and record.get("id")
    }


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    return tmp_path


def test_list_pending_returns_empty_when_no_queue(project_root: Path) -> None:
    assert list_pending(project_root) == []


def test_apply_pending_idempotent_on_empty_queue(project_root: Path) -> None:
    _seed_workspace(project_root)
    assert apply_pending(project_root) == []


def test_apply_pending_refuses_a_role_axis_entry(project_root: Path) -> None:
    """WI-7823: the queue carries no role axis and fails closed on one.

    No writer can create a role entry any more, so this seeds the file directly to
    prove the applier refuses it rather than silently applying a session role. An
    entry with no ``axis`` key defaults to ``role`` and must be refused the same way.
    """
    _seed_workspace(project_root)
    pending_dir = project_root / ".gtkb-state" / "mode-switches" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    pending_path = pending_dir / "20260907T000000Z-legacyrole.json"
    pending_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "record_id": "legacyrole",
                "harness_id_or_name": "B",
                "role": "prime-builder",
                "change_reason": "legacy role entry",
                "scheduled_at": "2026-09-07T00:00:00Z",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    results = apply_pending(project_root)
    assert len(results) == 1
    assert results[0].applied is False
    assert results[0].error is not None
    assert "role" in results[0].error
    assert pending_path.exists()  # refused entries stay in pending/
