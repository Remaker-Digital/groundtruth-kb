"""Tests for `gt projects remove-item` (WI-4266).

Covers the spec-derived verification plan from
`bridge/gtkb-projects-remove-item-cli-slice-1-005.md`:

- removal detaches the active membership (append-only non-active version) (GOV-08)
- prior active version preserved in history
- fail-closed when no active membership exists
- F2 non-active-status invariant (service + CLI): empty / case-insensitive
  `active` is rejected
- role/order carry-forward
- active -> removed -> active round-trip (DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001)
- CLI wiring

All tests use a temporary KnowledgeDB; none mutate the live groundtruth.db.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleError, ProjectLifecycleService

PROJECT_ID = "PROJECT-REMOVE-ITEM-TEST"
WORK_ITEM_ID = "WI-REMOVE-TEST-1"


def _seed(
    db_path: Path,
    *,
    membership_role: str = "member",
    membership_order: int | None = 1,
) -> None:
    """Create a project + work item + one active membership."""
    db = KnowledgeDB(db_path=str(db_path))
    try:
        db.insert_project("Remove Item Test Project", "test", "test setup", id=PROJECT_ID)
        db.insert_work_item(
            WORK_ITEM_ID,
            "Remove-item test work item",
            "new",
            "test",
            "open",
            "test",
            "test setup",
        )
        db.link_project_work_item(
            PROJECT_ID,
            WORK_ITEM_ID,
            "test",
            "seed active membership",
            membership_role=membership_role,
            membership_order=membership_order,
            status="active",
            source="seed",
        )
    finally:
        db.close()


def _service(db_path: Path) -> tuple[KnowledgeDB, ProjectLifecycleService]:
    db = KnowledgeDB(db_path=str(db_path))
    return db, ProjectLifecycleService(db)


def _active_work_item_ids(db: KnowledgeDB, project_id: str) -> list[str]:
    return [m["work_item_id"] for m in db.list_project_work_items(project_id)]


# --------------------------------------------------------------------------
# Service-level behavior
# --------------------------------------------------------------------------


def test_remove_project_item_detaches_active_membership(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path)
    db, service = _service(db_path)
    try:
        assert WORK_ITEM_ID in _active_work_item_ids(db, PROJECT_ID)
        membership = service.remove_project_item(PROJECT_ID, WORK_ITEM_ID, change_reason="detach test")
        assert membership["status"] == "removed"
        # No longer in the active set...
        assert WORK_ITEM_ID not in _active_work_item_ids(db, PROJECT_ID)
        # ...but still present when inactive memberships are included.
        all_ids = [m["work_item_id"] for m in db.list_project_work_items(PROJECT_ID, include_inactive=True)]
        assert WORK_ITEM_ID in all_ids
    finally:
        db.close()


def test_remove_appends_version_preserves_history(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path)
    db, service = _service(db_path)
    try:
        before = db.list_project_work_items(PROJECT_ID, include_inactive=True)
        membership_id = before[0]["membership_id"]
        service.remove_project_item(PROJECT_ID, WORK_ITEM_ID, change_reason="detach test")
        # The membership id is stable; the current version is now 'removed'.
        current = db.get_project_work_item_membership(membership_id)
        assert current is not None
        assert current["status"] == "removed"
    finally:
        db.close()


def test_remove_nonexistent_membership_raises(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    # Project + WI exist, but no membership linked.
    db = KnowledgeDB(db_path=str(db_path))
    try:
        db.insert_project("Remove Item Test Project", "test", "test setup", id=PROJECT_ID)
        db.insert_work_item(WORK_ITEM_ID, "wi", "new", "test", "open", "test", "setup")
    finally:
        db.close()
    db, service = _service(db_path)
    try:
        with pytest.raises(ProjectLifecycleError, match="No active membership"):
            service.remove_project_item(PROJECT_ID, WORK_ITEM_ID, change_reason="detach test")
    finally:
        db.close()


@pytest.mark.parametrize("bad_status", ["active", "Active", "ACTIVE", "  active  ", "", "   "])
def test_remove_rejects_active_status(tmp_path: Path, bad_status: str) -> None:
    """F2: a remove must never append an active (or empty) membership status."""
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path)
    db, service = _service(db_path)
    try:
        with pytest.raises(ProjectLifecycleError):
            service.remove_project_item(PROJECT_ID, WORK_ITEM_ID, change_reason="bad status", status=bad_status)
        # The active membership is untouched.
        assert WORK_ITEM_ID in _active_work_item_ids(db, PROJECT_ID)
    finally:
        db.close()


def test_remove_carries_forward_role_and_order(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path, membership_role="reviewer", membership_order=5)
    db, service = _service(db_path)
    try:
        membership = service.remove_project_item(PROJECT_ID, WORK_ITEM_ID, change_reason="detach test")
        assert membership["membership_role"] == "reviewer"
        assert membership["membership_order"] == 5
        assert membership["source"] == "seed"
    finally:
        db.close()


def test_remove_then_readd_cycle(tmp_path: Path) -> None:
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path)
    db, service = _service(db_path)
    try:
        service.remove_project_item(PROJECT_ID, WORK_ITEM_ID, change_reason="detach")
        assert WORK_ITEM_ID not in _active_work_item_ids(db, PROJECT_ID)
        service.add_project_item(PROJECT_ID, WORK_ITEM_ID, change_reason="re-add")
        assert WORK_ITEM_ID in _active_work_item_ids(db, PROJECT_ID)
    finally:
        db.close()


# --------------------------------------------------------------------------
# CLI wiring
# --------------------------------------------------------------------------


def test_cli_remove_item_invokes_service(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        main,
        ["projects", "remove-item", PROJECT_ID, WORK_ITEM_ID, "--change-reason", "cli detach"],
    )
    assert result.exit_code == 0, result.output
    assert WORK_ITEM_ID in result.output
    db = KnowledgeDB(db_path=str(db_path))
    try:
        assert WORK_ITEM_ID not in _active_work_item_ids(db, PROJECT_ID)
    finally:
        db.close()


def test_cli_remove_item_rejects_active_status(tmp_path: Path, monkeypatch) -> None:
    """F2 (CLI): `--status active` is surfaced as a non-zero ClickException."""
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            "projects",
            "remove-item",
            PROJECT_ID,
            WORK_ITEM_ID,
            "--status",
            "active",
            "--change-reason",
            "should fail",
        ],
    )
    assert result.exit_code != 0
    # The active membership is untouched.
    db = KnowledgeDB(db_path=str(db_path))
    try:
        assert WORK_ITEM_ID in _active_work_item_ids(db, PROJECT_ID)
    finally:
        db.close()


@pytest.mark.parametrize("bad_status", ["", " ", "   ", "\t"])
def test_cli_remove_item_rejects_empty_status(tmp_path: Path, monkeypatch, bad_status: str) -> None:
    """F1 -007 (CLI): empty or whitespace `--status` is surfaced as a non-zero ClickException.

    Closes the F1 finding from `bridge/gtkb-projects-remove-item-cli-slice-1-007.md`:
    CLI-level verification must cover empty/whitespace `--status` in addition to
    case-insensitive `active`. The service-level `test_remove_rejects_active_status`
    parametrization covers the service path; this CLI-surface test pins the
    public-command behavior so a regression in CLI argument handling cannot
    silently bypass the F2 non-active-status invariant.
    """
    db_path = tmp_path / "groundtruth.db"
    _seed(db_path)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        main,
        [
            "projects",
            "remove-item",
            PROJECT_ID,
            WORK_ITEM_ID,
            "--status",
            bad_status,
            "--change-reason",
            "should fail",
        ],
    )
    assert result.exit_code != 0
    # The active membership is untouched.
    db = KnowledgeDB(db_path=str(db_path))
    try:
        assert WORK_ITEM_ID in _active_work_item_ids(db, PROJECT_ID)
    finally:
        db.close()
