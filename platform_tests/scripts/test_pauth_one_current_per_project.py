# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-6618: one current project authorization per project."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.authorization_collapse import (
    COLLAPSE_OWNER_DECISION,
    census_active_authorizations,
    collapse_all,
    collapse_project,
    union_granted_envelope,
)
from groundtruth_kb.project.lifecycle import ProjectLifecycleService


def _seed(db: KnowledgeDB) -> None:
    db.insert_deliberation(
        COLLAPSE_OWNER_DECISION,
        "owner_conversation",
        "Owner approved one current authorization per project",
        "Owner approved the WI-6618 collapse.",
        "{}",
        "test",
        "seed owner decision",
        outcome="owner_decision",
    )
    db.insert_deliberation(
        "DELIB-C1-OTHER",
        "owner_conversation",
        "Other owner decision",
        "Other owner decision.",
        "{}",
        "test",
        "seed owner decision",
        outcome="owner_decision",
    )
    db.insert_spec("SPEC-C1-A", "Spec A", "specified", "test", "seed spec")
    db.insert_spec("SPEC-C1-B", "Spec B", "specified", "test", "seed spec")
    db.insert_work_item("WI-C1-1", "One", "new", "platform", "open", "test", "seed")
    db.insert_work_item("WI-C1-2", "Two", "new", "platform", "open", "test", "seed")
    db.insert_project("Collapse A", "test", "create", id="PROJECT-C1-A", status="active")
    db.insert_project("Collapse B", "test", "create", id="PROJECT-C1-B", status="active")


def _encode(values: list[str] | None) -> str | None:
    if values is None:
        return None
    return json.dumps([str(item).strip() for item in values if str(item).strip()])


def _seed_pre_cutover_authorization(
    db: KnowledgeDB,
    *,
    project_id: str,
    authorization_id: str,
    name: str,
    owner_decision: str,
    included_spec_ids: list[str],
    allowed_mutation_classes: list[str] | None = None,
) -> None:
    """Write a pre-WI-6618 current row without the C1/C2 creation gates."""
    conn = db._get_conn()
    conn.execute(
        """INSERT INTO project_authorizations
           (id, version, project_id, status, authorization_name, owner_decision_deliberation_id,
            scope_summary, allowed_mutation_classes, forbidden_operations, included_work_item_ids,
            excluded_work_item_ids, included_spec_ids, excluded_spec_ids, expires_at, supersedes,
            superseded_by, changed_by, changed_at, change_reason)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            authorization_id,
            1,
            project_id,
            "active",
            name,
            owner_decision,
            "Implement the authorized project membership.",
            _encode(allowed_mutation_classes),
            None,
            None,
            None,
            _encode(included_spec_ids),
            None,
            None,
            None,
            None,
            "test",
            datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pre-cutover seed",
        ),
    )
    conn.commit()


def test_union_does_not_drop_grants_or_invent_classes(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(db)
        rows = [
            {
                "id": "PAUTH-WI-1001-A",
                "authorization_name": "A",
                "allowed_mutation_classes_parsed": ["source"],
                "forbidden_operations_parsed": ["production_deployment", "git_push"],
                "included_spec_ids_parsed": ["SPEC-C1-A"],
                "excluded_spec_ids_parsed": ["SPEC-C1-B"],
                "expires_at": "2026-12-01T00:00:00Z",
            },
            {
                "id": "PAUTH-PROJECT-C1-A",
                "authorization_name": "B",
                "allowed_mutation_classes_parsed": ["test"],
                "forbidden_operations_parsed": ["production_deployment"],
                "included_spec_ids_parsed": ["SPEC-C1-B"],
                "excluded_spec_ids_parsed": [],
                "expires_at": None,
            },
        ]
        envelope = union_granted_envelope(rows, db=db)
        assert envelope["allowed_mutation_classes"] == ["source", "test"]
        assert envelope["forbidden_operations"] == ["production_deployment"]
        assert envelope["included_spec_ids"] == ["SPEC-C1-A", "SPEC-C1-B"]
        assert envelope["excluded_spec_ids"] is None
        assert envelope["expires_at"] is None
        assert envelope["supersedes"] == ["PAUTH-WI-1001-A", "PAUTH-PROJECT-C1-A"]
    finally:
        db.close()


def test_collapse_one_current_per_project_and_preserves_history(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(db)
        _seed_pre_cutover_authorization(
            db,
            project_id="PROJECT-C1-A",
            authorization_id="PAUTH-C1-A-BATCH",
            name="Per-item A",
            owner_decision=COLLAPSE_OWNER_DECISION,
            included_spec_ids=["SPEC-C1-A"],
            allowed_mutation_classes=["source"],
        )
        _seed_pre_cutover_authorization(
            db,
            project_id="PROJECT-C1-A",
            authorization_id="PAUTH-C1-A-OTHER",
            name="Per-item leftover",
            owner_decision="DELIB-C1-OTHER",
            included_spec_ids=["SPEC-C1-B"],
            allowed_mutation_classes=["test"],
        )
        _seed_pre_cutover_authorization(
            db,
            project_id="PROJECT-C1-B",
            authorization_id="PAUTH-C1-B-ONLY",
            name="Already one",
            owner_decision=COLLAPSE_OWNER_DECISION,
            included_spec_ids=["SPEC-C1-A"],
            allowed_mutation_classes=["source"],
        )
        before = census_active_authorizations(db)
        assert before["projects_with_multiple_current_ids"] == 1
        assert before["active_current_rows"] == 3
        result = collapse_all(db, changed_by="test", dry_run=False)
        assert result["errors"] == []
        after = census_active_authorizations(db)
        assert after["active_current_rows"] == 2
        assert after["projects_with_multiple_current_ids"] == 0
        assert after["wi_scoped_current_ids"] == 0
        current_a = db.list_project_authorizations("PROJECT-C1-A")
        assert len(current_a) == 1
        assert current_a[0]["allowed_mutation_classes_parsed"] == ["source", "test"]
        superseded_a = db.get_project_authorization("PAUTH-C1-A-BATCH")
        assert superseded_a is not None
        assert superseded_a["status"] == "superseded"
        superseded_other = db.get_project_authorization("PAUTH-C1-A-OTHER")
        assert superseded_other is not None
        assert superseded_other["status"] == "superseded"
        assert (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM project_authorizations WHERE id IN (?, ?)",
                ("PAUTH-C1-A-BATCH", "PAUTH-C1-A-OTHER"),
            )
            .fetchone()[0]
            >= 4
        )
        current_b = db.list_project_authorizations("PROJECT-C1-B")
        assert len(current_b) == 1
        assert current_b[0]["id"] != "PAUTH-C1-B-ONLY" or current_b[0]["status"] == "active"
        assert result["c1_fail_closed"] is True
        assert result["c2_fail_closed"] is True
    finally:
        db.close()


def test_c1_rejects_second_current_identity_after_collapse(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(db)
        db.insert_project_authorization(
            "PROJECT-C1-A",
            "Only",
            COLLAPSE_OWNER_DECISION,
            "Implement the authorized project membership.",
            "test",
            "seed",
            id="PAUTH-C1-A-ONLY",
            included_spec_ids=["SPEC-C1-A"],
        )
        collapse_project(db, "PROJECT-C1-A", changed_by="test", dry_run=False)
        with pytest.raises(ValueError, match="second current identity is prohibited"):
            db.insert_project_authorization(
                "PROJECT-C1-A",
                "Second",
                COLLAPSE_OWNER_DECISION,
                "Implement the authorized project membership.",
                "test",
                "seed",
                id="PAUTH-C1-A-SECOND",
                included_spec_ids=["SPEC-C1-A"],
            )
    finally:
        db.close()


def test_c2_rejects_active_wi_scoped_identity(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(db)
        with pytest.raises(ValueError, match="designates an individual work item"):
            db.insert_project_authorization(
                "PROJECT-C1-A",
                "Per-item",
                COLLAPSE_OWNER_DECISION,
                "Implement the authorized project membership.",
                "test",
                "seed",
                id="PAUTH-WI-3396-PRIORITY-CANONICAL-MIGRATION-001",
                included_spec_ids=["SPEC-C1-A"],
            )
    finally:
        db.close()


def test_membership_after_collapse_does_not_mint_second_identity(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(db)
        db.insert_project_authorization(
            "PROJECT-C1-A",
            "Only",
            COLLAPSE_OWNER_DECISION,
            "Implement the authorized project membership.",
            "test",
            "seed",
            id="PAUTH-C1-A-ONLY",
            included_spec_ids=["SPEC-C1-A"],
        )
        collapse_project(db, "PROJECT-C1-A", changed_by="test", dry_run=False)
        service = ProjectLifecycleService(db)
        service.add_project_item("PROJECT-C1-A", "WI-C1-1", change_reason="post-collapse membership")
        after = census_active_authorizations(db)
        assert after["active_current_rows"] == 1
        assert after["projects_with_multiple_current_ids"] == 0
    finally:
        db.close()


def test_collapse_leaves_project_unauthorized_when_no_approved_spec_remains(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _seed(db)
        db.insert_spec("SPEC-C1-DEAD", "Retired later", "specified", "test", "seed spec")
        db.insert_project("Collapse dead specs", "test", "create", id="PROJECT-C1-DEAD", status="active")
        db.insert_project_authorization(
            "PROJECT-C1-DEAD",
            "Was granted",
            COLLAPSE_OWNER_DECISION,
            "Implement the authorized project membership.",
            "test",
            "seed",
            id="PAUTH-C1-DEAD",
            included_spec_ids=["SPEC-C1-DEAD"],
        )
        db.insert_spec("SPEC-C1-DEAD", "Retired later", "retired", "test", "retire spec")
        result = collapse_project(db, "PROJECT-C1-DEAD", changed_by="test", dry_run=False)
        assert result["left_unauthorized"] is True
        assert result["new_id"] is None
        assert db.list_project_authorizations("PROJECT-C1-DEAD") == []
        superseded = db.get_project_authorization("PAUTH-C1-DEAD")
        assert superseded is not None
        assert superseded["status"] == "superseded"
        assert (
            db._get_conn()
            .execute(
                "SELECT COUNT(*) FROM project_authorizations WHERE id = ?",
                ("PAUTH-C1-DEAD",),
            )
            .fetchone()[0]
            >= 2
        )
    finally:
        db.close()
