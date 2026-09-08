"""Current membership has one parent; historical role labels carry no authority."""

from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.membership_resolver import (
    MembershipResolutionError,
    list_current_memberships,
    resolve_execution_membership,
)


def test_typed_membership_readback(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_project("Execution", "test", "seed", id="PROJECT-EXECUTION")
        db.insert_project("Other", "test", "seed", id="PROJECT-OTHER")
        db.insert_work_item("WI-MEMBER", "Member", "new", "platform", "open", "test", "seed")
        db.link_project_work_item("PROJECT-EXECUTION", "WI-MEMBER", "test", "seed", membership_order=10)
        assert len(list_current_memberships(db, "WI-MEMBER")) == 1
        exact = resolve_execution_membership(db, "WI-MEMBER")
        assert exact.project_id == "PROJECT-EXECUTION"
        assert exact.membership_order == 10
        with pytest.raises(ValueError, match="already belongs"):
            db.link_project_work_item("PROJECT-OTHER", "WI-MEMBER", "test", "invalid duplicate")
        assert resolve_execution_membership(db, "WI-MEMBER") == exact
    finally:
        db.close()


def test_missing_membership_is_reported(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_work_item("WI-ORPHAN", "Missing parent", "new", "platform", "open", "test", "seed")
        with pytest.raises(MembershipResolutionError) as error:
            resolve_execution_membership(db, "WI-ORPHAN")
        assert error.value.code == "project_membership_required"
    finally:
        db.close()
