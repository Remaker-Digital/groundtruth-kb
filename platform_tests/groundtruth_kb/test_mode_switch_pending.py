"""Tests for groundtruth_kb.mode_switch.pending.

Covers SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001 acceptance criterion #6:
next-session-effectiveness via the pending-transaction queue.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.mode_switch.pending import (
    apply_pending,
    defer_role_switch,
    list_pending,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _seed_workspace(root: Path) -> None:
    _write(
        root / "harness-state" / "role-assignments.json",
        json.dumps(
            {
                "harnesses": {
                    "A": {"role": ["loyal-opposition"], "name": "codex"},
                    "B": {"role": ["prime-builder"], "name": "claude"},
                }
            }
        ),
    )
    _write(
        root / "bridge" / "INDEX.md",
        "Document: foo\nVERIFIED: bridge/foo-001.md\n",
    )


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
    pending_path = defer_role_switch(
        project_root, "claude", "loyal-opposition", change_reason="drain test"
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
    defer_role_switch(
        project_root, "claude", "loyal-opposition", change_reason="next-session test"
    )
    apply_pending(project_root)
    role_map = json.loads(
        (project_root / "harness-state" / "role-assignments.json").read_text(
            encoding="utf-8"
        )
    )
    assert role_map["harnesses"]["B"]["role"] == ["loyal-opposition"]
