"""Resolve a work item's single current parent project."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class MembershipResolutionError(RuntimeError):
    def __init__(self, code: str, message: str, *, memberships: list[dict[str, Any]] | None = None):
        super().__init__(message)
        self.code = code
        self.memberships = memberships or []


@dataclass(frozen=True)
class ExecutionMembership:
    id: str
    version: int
    project_id: str
    work_item_id: str
    membership_role: str
    membership_order: int | None
    status: str
    source: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def list_current_memberships(db: Any, work_item_id: str) -> list[ExecutionMembership]:
    rows = (
        db._get_conn()
        .execute(
            """SELECT id,version,project_id,work_item_id,membership_role,membership_order,status,source
           FROM current_project_work_item_memberships
           WHERE work_item_id=? ORDER BY project_id,id""",
            (work_item_id,),
        )
        .fetchall()
    )
    return [ExecutionMembership(**dict(row)) for row in rows]


def resolve_execution_membership(db: Any, work_item_id: str) -> ExecutionMembership:
    all_memberships = list_current_memberships(db, work_item_id)
    executable = [row for row in all_memberships if row.status == "active"]
    if not executable:
        raise MembershipResolutionError(
            "project_membership_required",
            f"work item {work_item_id} has no active parent project",
            memberships=[row.to_dict() for row in all_memberships],
        )
    if len(executable) != 1:
        raise MembershipResolutionError(
            "project_membership_ambiguous",
            f"work item {work_item_id} has {len(executable)} active project memberships; reconcile to one parent",
            memberships=[row.to_dict() for row in executable],
        )
    project = db.get_project(executable[0].project_id)
    if project is None or project["kind"] != "project":
        raise MembershipResolutionError(
            "invalid_parent_project",
            f"work item {work_item_id} must belong to an execution project, not a program or missing record",
            memberships=[row.to_dict() for row in executable],
        )
    return executable[0]
