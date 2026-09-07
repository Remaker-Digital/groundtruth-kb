"""Typed resolution of exact execution-authority project membership."""

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
    executable = [
        row for row in all_memberships if row.status == "active" and row.membership_role == "execution_authority"
    ]
    if not executable:
        raise MembershipResolutionError(
            "execution_authority_membership_required",
            f"work item {work_item_id} has no active execution_authority membership",
            memberships=[row.to_dict() for row in all_memberships],
        )
    if len(executable) != 1:
        raise MembershipResolutionError(
            "execution_authority_membership_ambiguous",
            f"work item {work_item_id} has {len(executable)} active execution_authority memberships",
            memberships=[row.to_dict() for row in executable],
        )
    return executable[0]
