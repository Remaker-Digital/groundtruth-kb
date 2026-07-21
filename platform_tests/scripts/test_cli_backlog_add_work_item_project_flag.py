"""Tests for gt backlog add-work-item --project flag (GFR Slice C Finding 2.6).

Work item: WI-5647 (TEST-11692).
Governing: DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001,
DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-FILE-BRIDGE-AUTHORITY-001.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB


def _make_db(tmp_path: Path) -> tuple[Path, GTConfig]:
    """Create a fully-initialized KnowledgeDB with test data."""
    db_path = tmp_path / "groundtruth.db"
    chroma_path = tmp_path / "chroma"
    config = GTConfig(db_path=db_path, project_root=tmp_path, chroma_path=chroma_path)
    db = KnowledgeDB(db_path=db_path, chroma_path=chroma_path)

    # Insert projects to link to
    db.insert_project("Test Project", "test", "test setup", id="PROJECT-TEST")
    db.insert_project("Other Project", "test", "test setup", id="PROJECT-OTHER")

    # Insert a spec for test linkage
    db.insert_spec("SPEC-TEST-001", "Test Spec", "active", "test", "test setup")

    # Insert a test plan + phase
    db.insert_test_plan("PLAN-001", "Test Plan", "active", "test", "test setup")
    db.insert_test_plan_phase(
        "PHASE-001",
        plan_id="PLAN-001",
        phase_order=1,
        title="Initial",
        gate_criteria="pass",
        changed_by="test",
        change_reason="test setup",
        test_ids=[],
    )

    db.close()
    return db_path, config


class TestProjectFlag:
    """Finding 2.6: --project flag creates project_members row atomically."""

    def test_project_flag_creates_membership(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--project creates a project_work_item_memberships row."""
        db_path, config = _make_db(tmp_path)

        monkeypatch.setattr(
            "groundtruth_kb.cli_backlog_add_work_item._resolve_changed_by",
            lambda project_root: "test-session",
        )

        from groundtruth_kb.cli_backlog_add_work_item import AddWorkItemRequest, add_work_item_with_test

        request = AddWorkItemRequest(
            title="Test WI",
            origin="new",
            component="cli",
            priority="P1",
            project_name=None,
            subproject_name=None,
            description="Test",
            source_owner_directive=None,
            source_spec_id="SPEC-TEST-001",
            project_id="PROJECT-TEST",
            change_reason="Test creation",
            test_title="Test linked test",
            test_type="unit",
            test_expected_outcome="Pass",
            test_spec_id="SPEC-TEST-001",
            test_plan_phase="PHASE-001",
            dry_run=False,
        )
        result = add_work_item_with_test(config, request)
        assert result["created"] is True
        assert result["project_membership"] is not None

        # Verify membership row was created
        db = KnowledgeDB(db_path=db_path, chroma_path=tmp_path / "chroma")
        rows = (
            db._get_conn()
            .execute(
                "SELECT project_id, work_item_id FROM project_work_item_memberships WHERE work_item_id = ?",
                (result["work_item_id"],),
            )
            .fetchall()
        )
        db.close()
        assert len(rows) == 1
        assert rows[0][0] == "PROJECT-TEST"
        assert rows[0][1] == result["work_item_id"]

    def test_no_project_flag_no_membership(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without --project, no project_work_item_memberships row is created."""
        db_path, config = _make_db(tmp_path)

        monkeypatch.setattr(
            "groundtruth_kb.cli_backlog_add_work_item._resolve_changed_by",
            lambda project_root: "test-session",
        )

        from groundtruth_kb.cli_backlog_add_work_item import AddWorkItemRequest, add_work_item_with_test

        request = AddWorkItemRequest(
            title="Test WI no project",
            origin="new",
            component="cli",
            priority="P1",
            project_name=None,
            subproject_name=None,
            description="Test",
            source_owner_directive=None,
            source_spec_id="SPEC-TEST-001",
            project_id=None,
            change_reason="Test creation",
            test_title="Test linked test",
            test_type="unit",
            test_expected_outcome="Pass",
            test_spec_id="SPEC-TEST-001",
            test_plan_phase="PHASE-001",
            dry_run=False,
        )
        result = add_work_item_with_test(config, request)
        assert result["created"] is True
        assert result.get("project_membership") is None

        db = KnowledgeDB(db_path=db_path, chroma_path=tmp_path / "chroma")
        rows = (
            db._get_conn()
            .execute(
                "SELECT project_id FROM project_work_item_memberships WHERE work_item_id = ?",
                (result["work_item_id"],),
            )
            .fetchall()
        )
        db.close()
        assert len(rows) == 0

    def test_project_flag_invalid_project_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--project with invalid project id raises error after WI creation."""
        db_path, config = _make_db(tmp_path)

        monkeypatch.setattr(
            "groundtruth_kb.cli_backlog_add_work_item._resolve_changed_by",
            lambda project_root: "test-session",
        )

        from groundtruth_kb.cli_backlog_add_work_item import (
            AddWorkItemError,
            AddWorkItemRequest,
            add_work_item_with_test,
        )

        request = AddWorkItemRequest(
            title="Test WI invalid project",
            origin="new",
            component="cli",
            priority="P1",
            project_name=None,
            subproject_name=None,
            description="Test",
            source_owner_directive=None,
            source_spec_id="SPEC-TEST-001",
            project_id="PROJECT-NONEXISTENT",
            change_reason="Test creation",
            test_title="Test linked test",
            test_type="unit",
            test_expected_outcome="Pass",
            test_spec_id="SPEC-TEST-001",
            test_plan_phase="PHASE-001",
            dry_run=False,
        )
        with pytest.raises(AddWorkItemError) as exc_info:
            add_work_item_with_test(config, request)
        assert "PROJECT-NONEXISTENT" in str(exc_info.value)

        # WI should still exist even though linkage failed
        db = KnowledgeDB(db_path=db_path, chroma_path=tmp_path / "chroma")
        wi_rows = (
            db._get_conn().execute("SELECT id FROM work_items WHERE title = ?", ("Test WI invalid project",)).fetchall()
        )
        db.close()
        assert len(wi_rows) == 1
