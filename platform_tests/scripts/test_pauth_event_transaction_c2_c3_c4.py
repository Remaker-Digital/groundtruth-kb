# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-6617: membership mutation is the authorization transaction (C2/C3/C4)."""

from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleError, ProjectLifecycleService


def _seed(db: KnowledgeDB, *, project_id: str, work_item_id: str, spec_id: str, delib_id: str) -> None:
    db.insert_deliberation(
        delib_id,
        "owner_conversation",
        "Owner approved bounded project implementation",
        "Owner approved the test project for implementation.",
        "{}",
        "test",
        "seed owner decision",
        outcome="owner_decision",
    )
    db.insert_spec(spec_id, "Scoped spec", "specified", "test", "seed spec")
    db.insert_work_item(
        work_item_id,
        "Project authorization work item",
        "new",
        "platform",
        "open",
        "test",
        "seed work item",
        stage="backlogged",
    )
    db.insert_project("Authorization Event Project", "test", "create project", id=project_id, status="active")


def _authorize(
    service: ProjectLifecycleService, *, project_id: str, authorization_id: str, delib_id: str, spec_id: str
) -> dict:
    return service.authorize_project(
        project_id,
        owner_decision=delib_id,
        name="Project implementation approval",
        scope="Implement the authorized project membership.",
        changed_by="test",
        change_reason="authorize implementation project",
        authorization_id=authorization_id,
        allowed_mutation_classes=["source", "test"],
        included_spec_ids=[spec_id],
    )


def test_add_item_to_authorized_project_increments_pauth_version(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(
            db,
            project_id="PROJECT-C3-A",
            work_item_id="WI-C3-1",
            spec_id="SPEC-C3-A",
            delib_id="DELIB-C3-A",
        )
        db.insert_work_item("WI-C3-2", "Second member", "new", "platform", "open", "test", "seed")
        service = ProjectLifecycleService(db)
        auth = _authorize(
            service,
            project_id="PROJECT-C3-A",
            authorization_id="PAUTH-C3-A",
            delib_id="DELIB-C3-A",
            spec_id="SPEC-C3-A",
        )
        assert auth["version"] == 1
        service.add_project_item("PROJECT-C3-A", "WI-C3-1", change_reason="link first")
        assert db.get_project_authorization("PAUTH-C3-A")["version"] == 2
        service.add_project_item("PROJECT-C3-A", "WI-C3-2", change_reason="link second")
        current = db.get_project_authorization("PAUTH-C3-A")
        assert current is not None
        assert current["version"] == 3
        members = {row["work_item_id"] for row in db.list_project_work_items("PROJECT-C3-A")}
        assert members == {"WI-C3-1", "WI-C3-2"}
        assert not current.get("included_work_item_ids_parsed")
    finally:
        db.close()


def test_auth_append_failure_rolls_back_membership(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(
            db,
            project_id="PROJECT-C3-FAIL",
            work_item_id="WI-C3-FAIL",
            spec_id="SPEC-C3-FAIL",
            delib_id="DELIB-C3-FAIL",
        )
        service = ProjectLifecycleService(db)
        _authorize(
            service,
            project_id="PROJECT-C3-FAIL",
            authorization_id="PAUTH-C3-FAIL",
            delib_id="DELIB-C3-FAIL",
            spec_id="SPEC-C3-FAIL",
        )
        original = db.insert_project_authorization

        def boom(*args, **kwargs):
            raise ValueError("forced auth-append failure")

        monkeypatch.setattr(db, "insert_project_authorization", boom)
        with pytest.raises(ProjectLifecycleError, match="forced auth-append failure"):
            service.add_project_item("PROJECT-C3-FAIL", "WI-C3-FAIL", change_reason="should roll back")
        monkeypatch.setattr(db, "insert_project_authorization", original)
        assert db.list_project_work_items("PROJECT-C3-FAIL") == []
        current = db.get_project_authorization("PAUTH-C3-FAIL")
        assert current is not None
        assert current["version"] == 1
    finally:
        db.close()


def test_move_between_authorized_projects_appends_both(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(
            db,
            project_id="PROJECT-C3-FROM",
            work_item_id="WI-C3-MOVE",
            spec_id="SPEC-C3-FROM",
            delib_id="DELIB-C3-FROM",
        )
        db.insert_deliberation(
            "DELIB-C3-TO",
            "owner_conversation",
            "Owner approved destination project",
            "Owner approved the destination project.",
            "{}",
            "test",
            "seed owner decision",
            outcome="owner_decision",
        )
        db.insert_spec("SPEC-C3-TO", "Destination spec", "specified", "test", "seed spec")
        db.insert_project("Destination Project", "test", "create project", id="PROJECT-C3-TO", status="active")
        service = ProjectLifecycleService(db)
        _authorize(
            service,
            project_id="PROJECT-C3-FROM",
            authorization_id="PAUTH-C3-FROM",
            delib_id="DELIB-C3-FROM",
            spec_id="SPEC-C3-FROM",
        )
        _authorize(
            service,
            project_id="PROJECT-C3-TO",
            authorization_id="PAUTH-C3-TO",
            delib_id="DELIB-C3-TO",
            spec_id="SPEC-C3-TO",
        )
        service.add_project_item("PROJECT-C3-FROM", "WI-C3-MOVE", change_reason="start on from")
        assert db.get_project_authorization("PAUTH-C3-FROM")["version"] == 2
        service.remove_project_item("PROJECT-C3-FROM", "WI-C3-MOVE", change_reason="leave from")
        service.add_project_item("PROJECT-C3-TO", "WI-C3-MOVE", change_reason="join to")
        assert db.get_project_authorization("PAUTH-C3-FROM")["version"] == 3
        assert db.get_project_authorization("PAUTH-C3-TO")["version"] == 2
        assert db.list_project_work_items("PROJECT-C3-FROM") == []
        assert [row["work_item_id"] for row in db.list_project_work_items("PROJECT-C3-TO")] == ["WI-C3-MOVE"]
    finally:
        db.close()


def test_add_item_to_unauthorized_project_does_not_create_pauth(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(
            db,
            project_id="PROJECT-C3-UNAUTH",
            work_item_id="WI-C3-UNAUTH",
            spec_id="SPEC-C3-UNAUTH",
            delib_id="DELIB-C3-UNAUTH",
        )
        service = ProjectLifecycleService(db)
        service.add_project_item("PROJECT-C3-UNAUTH", "WI-C3-UNAUTH", change_reason="membership only")
        assert db.list_project_authorizations("PROJECT-C3-UNAUTH") == []
        assert [row["work_item_id"] for row in db.list_project_work_items("PROJECT-C3-UNAUTH")] == ["WI-C3-UNAUTH"]
    finally:
        db.close()


def test_insert_rejects_enumerated_work_item_ids(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(
            db,
            project_id="PROJECT-C4",
            work_item_id="WI-C4-1",
            spec_id="SPEC-C4",
            delib_id="DELIB-C4",
        )
        with pytest.raises(ValueError, match="must not enumerate included or excluded work-item IDs"):
            db.insert_project_authorization(
                "PROJECT-C4",
                "List envelope",
                "DELIB-C4",
                "Implement the authorized project membership.",
                "test",
                "authorize with include list",
                id="PAUTH-C4",
                included_work_item_ids=["WI-C4-1"],
                included_spec_ids=["SPEC-C4"],
            )
        assert db.get_project_authorization("PAUTH-C4") is None
    finally:
        db.close()


def test_insert_rejects_work_item_scoped_identity(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(
            db,
            project_id="PROJECT-C2",
            work_item_id="WI-3396",
            spec_id="SPEC-C2",
            delib_id="DELIB-C2",
        )
        with pytest.raises(ValueError, match="designates an individual work item"):
            db.insert_project_authorization(
                "PROJECT-C2",
                "Per-item approval",
                "DELIB-C2",
                "Implement the authorized project membership.",
                "test",
                "authorize work-item identity",
                id="PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001",
                included_spec_ids=["SPEC-C2"],
            )
        assert db.get_project_authorization("PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001") is None
    finally:
        db.close()


def test_amend_authorization_fails_closed_and_leaves_version(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(
            db,
            project_id="PROJECT-AMEND",
            work_item_id="WI-AMEND-1",
            spec_id="SPEC-AMEND",
            delib_id="DELIB-AMEND",
        )
        service = ProjectLifecycleService(db)
        auth = _authorize(
            service,
            project_id="PROJECT-AMEND",
            authorization_id="PAUTH-AMEND",
            delib_id="DELIB-AMEND",
            spec_id="SPEC-AMEND",
        )
        assert auth["version"] == 1
        with pytest.raises(ProjectLifecycleError, match="not an authorization path"):
            service.amend_authorization(
                "PAUTH-AMEND",
                owner_decision="DELIB-AMEND",
                change_reason="delta include list",
                add_work_items=["WI-AMEND-1"],
            )
        current = db.get_project_authorization("PAUTH-AMEND")
        assert current is not None
        assert current["version"] == 1
    finally:
        db.close()
