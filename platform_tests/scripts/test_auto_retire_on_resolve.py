"""Work-item status updates preserve the parent and do not finalize its project."""

from __future__ import annotations

from contextlib import closing
from pathlib import Path

import pytest
from groundtruth_kb import cli_backlog_update
from groundtruth_kb.cli_backlog_update import BacklogUpdateRequest, update_backlog_item
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleService


@pytest.mark.parametrize("status", ["resolved", "verified", "retired", "wont_fix", "not_a_defect"])
@pytest.mark.parametrize("authorization", ["authorized", "not authorized"])
def test_last_member_status_does_not_finalize_or_remove_parent(tmp_path: Path, monkeypatch, status, authorization):
    monkeypatch.setattr(cli_backlog_update, "_resolve_changed_by", lambda *_args, **_kwargs: "test")
    config = GTConfig(db_path=tmp_path / "groundtruth.db", project_root=tmp_path)
    with closing(KnowledgeDB(config.db_path)) as db:
        db.insert_project("Complete outcome", "test", "seed", id="PROJECT-X", authorization=authorization)
        for number, initial in [(1, "verified"), (2, "open")]:
            db.insert_work_item(f"WI-{number}", f"Member {number}", "improvement", "platform", initial, "test", "seed")
            db.link_project_work_item("PROJECT-X", f"WI-{number}", "test", "explicit parent", membership_order=number)
        project = db.get_project("PROJECT-X")
        sibling = db.get_work_item("WI-1")
        memberships = [dict(row) for row in db._get_conn().execute("SELECT * FROM project_work_item_memberships")]
        result = update_backlog_item(
            config,
            BacklogUpdateRequest(
                work_item_id="WI-2",
                resolution_status=status,
                stage=None,
                priority=None,
                related_bridge_threads=None,
                status_detail=None,
                owner_approved=False,
                change_reason="Record the work-item result",
                dry_run=False,
            ),
        )
        assert result["updated"] is True
        assert db.get_work_item("WI-2")["resolution_status"] == status
        assert db.get_work_item("WI-1") == sibling
        assert db.get_project("PROJECT-X") == project
        assert [
            dict(row) for row in db._get_conn().execute("SELECT * FROM project_work_item_memberships")
        ] == memberships
        assert len(db.list_project_work_items("PROJECT-X")) == 2


def test_retiring_project_preserves_member_results_and_relationships(tmp_path: Path):
    with closing(KnowledgeDB(tmp_path / "groundtruth.db")) as db:
        db.insert_project("Retired outcome", "test", "seed", id="PROJECT-X")
        db.insert_work_item("WI-1", "Historical result", "improvement", "platform", "resolved", "test", "seed")
        membership = db.link_project_work_item("PROJECT-X", "WI-1", "test", "explicit parent")
        work = db.get_work_item("WI-1")
        ProjectLifecycleService(db).retire_project(
            "PROJECT-X", changed_by="test", change_reason="Retire obsolete scope"
        )
        assert db.get_project("PROJECT-X")["status"] == "retired"
        assert db.get_work_item("WI-1") == work
        assert db.get_project_work_item_membership(membership["id"]) == membership
        assert db.list_project_work_items("PROJECT-X")[0]["work_item_id"] == "WI-1"
