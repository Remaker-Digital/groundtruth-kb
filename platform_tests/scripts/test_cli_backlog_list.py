"""Tests for governed ``gt backlog list`` query filters.

Authority: bridge/gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority-002.md
Work item: WI-AUTO-SPEC-INTAKE-C2C7FF / SPEC-INTAKE-c2c7ff.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from groundtruth_kb.backlog.query import (  # noqa: E402
    BacklogListQuery,
    ProjectListQuery,
    SortKey,
    filter_projects,
    filter_work_items,
)
from groundtruth_kb.db import KnowledgeDB  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text(
        '[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n',
        encoding="utf-8",
    )
    return root, config


def _seed_backlog(db_path: Path) -> None:
    db = KnowledgeDB(db_path=db_path)
    try:
        db.insert_project(
            id="PROJECT-ALPHA",
            name="Alpha",
            status="active",
            changed_by="test",
            change_reason="seed project alpha",
        )
        db.insert_work_item(
            id="WI-1001",
            title="Scanner cleanup alpha",
            origin="defect",
            component="backlog",
            resolution_status="open",
            priority="P1",
            stage="open",
            approval_state="unapproved",
            changed_by="test",
            change_reason="seed wi-1001",
            description="Exact description for alpha",
            project_name="Alpha",
            source_owner_directive="DELIB-ALPHA",
            implementation_order=2,
        )
        db.insert_work_item(
            id="WI-1002",
            title="Bridge authorized beta",
            origin="enhancement",
            component="bridge",
            resolution_status="open",
            priority="P2",
            stage="review",
            approval_state="bridge_authorized",
            changed_by="test",
            change_reason="seed wi-1002",
            project_name="Beta",
            implementation_order=5,
        )
        db.insert_work_item(
            id="WI-1003",
            title="Resolved gamma",
            origin="defect",
            component="backlog",
            resolution_status="resolved",
            priority="P3",
            stage="resolved",
            approval_state="implementation_authorized",
            changed_by="test",
            change_reason="seed wi-1003",
            project_name="Gamma",
            implementation_order=10,
        )
        db.link_project_work_item(
            project_id="PROJECT-ALPHA",
            work_item_id="WI-1001",
            changed_by="test",
            change_reason="seed membership",
            membership_role="member",
            membership_order=1,
        )
    finally:
        db.close()


def test_filter_work_items_exact_and_approval_state():
    rows = [
        {"id": "WI-A", "approval_state": "unapproved", "priority": "P1"},
        {"id": "WI-B", "approval_state": "bridge_authorized", "priority": "P2"},
    ]
    query = BacklogListQuery(approval_states=("bridge_authorized",))
    filtered = filter_work_items(rows, query, contains_fields=("id",))
    assert [row["id"] for row in filtered] == ["WI-B"]


def test_filter_work_items_pattern_range_and_sort():
    rows = [
        {"id": "WI-1001", "title": "Scanner cleanup", "priority": "P1", "implementation_order": 2},
        {"id": "WI-1002", "title": "Other work", "priority": "P2", "implementation_order": 5},
        {"id": "WI-1003", "title": "Scanner follow-up", "priority": "P3", "implementation_order": 10},
    ]
    query = BacklogListQuery(
        match_specs=("title:*scanner*",),
        range_specs=("priority:P1..P2",),
        sort_keys=(SortKey("implementation_order"),),
    )
    filtered = filter_work_items(rows, query, contains_fields=("title",))
    assert [row["id"] for row in filtered] == ["WI-1001"]


def test_filter_work_items_generic_exact_field():
    rows = [
        {"id": "WI-1001", "source_owner_directive": "DELIB-ALPHA"},
        {"id": "WI-1002", "source_owner_directive": "DELIB-BETA"},
    ]
    query = BacklogListQuery(exact_specs=("source_owner_directive:DELIB-BETA",))
    filtered = filter_work_items(rows, query, contains_fields=("id",))
    assert [row["id"] for row in filtered] == ["WI-1002"]


def test_filter_work_items_member_of_project():
    rows = [
        {"id": "WI-1001", "title": "Alpha"},
        {"id": "WI-1002", "title": "Beta"},
    ]
    query = BacklogListQuery(member_of_project_ids=("PROJECT-ALPHA",))
    filtered = filter_work_items(
        rows,
        query,
        contains_fields=("title",),
        project_membership_ids={"PROJECT-ALPHA": {"WI-1001"}},
    )
    assert [row["id"] for row in filtered] == ["WI-1001"]


def test_filter_projects_pattern_exact_and_sort():
    rows = [
        {"id": "PROJECT-BETA", "name": "Beta", "status": "active", "rank": 3},
        {"id": "PROJECT-ALPHA", "name": "Alpha", "status": "active", "rank": 1},
        {"id": "PROJECT-GAMMA", "name": "Gamma", "status": "retired", "rank": 2},
    ]
    query = ProjectListQuery(
        exact_specs=("status:active",),
        match_specs=("name:*a*",),
        sort_keys=(SortKey("rank"),),
    )
    filtered = filter_projects(rows, query, contains_fields=("id", "name"))
    assert [row["id"] for row in filtered] == ["PROJECT-ALPHA", "PROJECT-BETA"]
