from __future__ import annotations

from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.membership_resolver import (
    MembershipResolutionError,
    list_current_memberships,
    resolve_execution_membership,
)


def test_typed_membership_readback_and_execution_authority(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_project("Execution", "test", "seed", id="PROJECT-EXECUTION")
        db.insert_project("Planning", "test", "seed", id="PROJECT-PLANNING")
        db.insert_work_item("WI-MEMBER", "Member", "new", "platform", "open", "test", "seed")
        db.link_project_work_item("PROJECT-PLANNING", "WI-MEMBER", "test", "plan", membership_role="planning")
        db.link_project_work_item(
            "PROJECT-EXECUTION",
            "WI-MEMBER",
            "test",
            "execute",
            membership_role="execution_authority",
            membership_order=10,
        )
        rows = list_current_memberships(db, "WI-MEMBER")
        assert len(rows) == 2
        exact = resolve_execution_membership(db, "WI-MEMBER")
        assert exact.project_id == "PROJECT-EXECUTION"
        assert exact.membership_order == 10

        db.link_project_work_item(
            "PROJECT-PLANNING",
            "WI-MEMBER",
            "test",
            "invalid duplicate",
            membership_role="execution_authority",
            membership_order=20,
        )
        with pytest.raises(MembershipResolutionError) as exc_info:
            resolve_execution_membership(db, "WI-MEMBER")
        assert exc_info.value.code == "execution_authority_membership_ambiguous"
    finally:
        db.close()


def test_execution_authority_resolution_fails_closed_on_zero_memberships(tmp_path: Path) -> None:
    """The zero case must fail as loudly as the ambiguous case.

    WI-6990 verification expectation 3 requires the readback to fail when a work
    item holds *zero or more than one* active ``execution_authority`` membership.
    The ambiguous branch was already exercised above; this covers the zero branch,
    which is the population-scale condition: as measured 2026-08-26, 1330 of 1402
    open work items hold no execution authority at all, so this is the branch that
    fires for the overwhelming majority of real work items.
    """
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_project("Planning", "test", "seed", id="PROJECT-PLANNING")
        db.insert_work_item("WI-NOEXEC", "No exec", "new", "platform", "open", "test", "seed")

        # No membership at all.
        with pytest.raises(MembershipResolutionError) as exc_info:
            resolve_execution_membership(db, "WI-NOEXEC")
        assert exc_info.value.code == "execution_authority_membership_required"

        # A non-execution membership must not satisfy the requirement either:
        # holding *a* membership is not the same as holding execution authority.
        db.link_project_work_item("PROJECT-PLANNING", "WI-NOEXEC", "test", "plan", membership_role="planning")
        assert len(list_current_memberships(db, "WI-NOEXEC")) == 1
        with pytest.raises(MembershipResolutionError) as exc_info:
            resolve_execution_membership(db, "WI-NOEXEC")
        assert exc_info.value.code == "execution_authority_membership_required"
    finally:
        db.close()
