"""Deterministic project lifecycle operations over MemBase project records."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.authorization import ACTIVE_PROJECT_AUTHORIZATION_STATUS

PROJECT_TERMINAL_STATUS = "retired"
PROJECTS_CHANGED_BY = "gt-projects"


class ProjectLifecycleError(ValueError):
    """Raised when a project lifecycle request is invalid."""


class ProjectAuthorizationSpecLinkageError(ProjectLifecycleError):
    """Raised when authorize_project() rejects an active authorization that
    cites no approved specification
    (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 / WI-3312).

    A typed subclass of ProjectLifecycleError so the CLI can surface a
    user-facing usage error distinct from generic lifecycle failures.
    """


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_nonempty(value: str, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ProjectLifecycleError(f"{field_name} is required")
    return normalized


class ProjectLifecycleService:
    """Thin service layer for first-class project lifecycle commands."""

    def __init__(self, db: KnowledgeDB) -> None:
        self.db = db

    def create_project(
        self,
        name: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        project_id: str | None = None,
        status: str = "active",
        rank: int | None = None,
        parent_project_id: str | None = None,
        purpose: str | None = None,
        target_outcome: str | None = None,
        scope_note: str | None = None,
        start_date: str | None = None,
        target_date: str | None = None,
        notes: str | None = None,
        source_project_name: str | None = None,
        source_subproject_name: str | None = None,
    ) -> dict[str, Any]:
        project = self.db.insert_project(
            _require_nonempty(name, "name"),
            _require_nonempty(changed_by, "changed_by"),
            _require_nonempty(change_reason, "change_reason"),
            id=project_id.strip() if project_id else None,
            status=status,
            rank=rank,
            parent_project_id=parent_project_id,
            purpose=purpose,
            target_outcome=target_outcome,
            scope_note=scope_note,
            start_date=start_date,
            target_date=target_date,
            notes=notes,
            source_project_name=source_project_name,
            source_subproject_name=source_subproject_name,
        )
        if project is None:
            raise ProjectLifecycleError("Project insert did not return a current project")
        return project

    def list_projects(self, *, include_terminal: bool = False, status: str | None = None) -> list[dict[str, Any]]:
        return self.db.list_projects(include_terminal=include_terminal, status=status)

    def show_project(self, project_id: str) -> dict[str, Any]:
        project = self.db.get_project(_require_nonempty(project_id, "project_id"))
        if project is None:
            raise ProjectLifecycleError(f"Project not found: {project_id}")
        return {
            "project": project,
            "work_items": self.db.list_project_work_items(project["id"]),
            "dependencies": self.db.list_project_dependencies(project["id"]),
            "artifact_links": self.db.list_project_artifact_links(project["id"]),
            "authorizations": self.db.list_project_authorizations(project["id"]),
        }

    def update_project(
        self,
        project_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        **fields: Any,
    ) -> dict[str, Any]:
        current = self.db.get_project(_require_nonempty(project_id, "project_id"))
        if current is None:
            raise ProjectLifecycleError(f"Project not found: {project_id}")

        allowed_fields = {
            "name",
            "status",
            "rank",
            "parent_project_id",
            "purpose",
            "target_outcome",
            "scope_note",
            "start_date",
            "target_date",
            "completed_at",
            "notes",
            "source_project_name",
            "source_subproject_name",
        }
        unknown = sorted(set(fields) - allowed_fields)
        if unknown:
            raise ProjectLifecycleError(f"Unsupported project fields: {', '.join(unknown)}")

        values = {field: fields.get(field, current.get(field)) for field in allowed_fields}
        project = self.db.insert_project(
            values["name"],
            _require_nonempty(changed_by, "changed_by"),
            _require_nonempty(change_reason, "change_reason"),
            id=current["id"],
            status=values["status"],
            rank=values["rank"],
            parent_project_id=values["parent_project_id"],
            purpose=values["purpose"],
            target_outcome=values["target_outcome"],
            scope_note=values["scope_note"],
            start_date=values["start_date"],
            target_date=values["target_date"],
            completed_at=values["completed_at"],
            notes=values["notes"],
            source_project_name=values["source_project_name"],
            source_subproject_name=values["source_subproject_name"],
        )
        if project is None:
            raise ProjectLifecycleError("Project update did not return a current project")
        return project

    def add_project_item(
        self,
        project_id: str,
        work_item_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        membership_role: str = "member",
        membership_order: int | None = None,
        source: str | None = "gt projects add-item",
    ) -> dict[str, Any]:
        try:
            membership = self.db.link_project_work_item(
                _require_nonempty(project_id, "project_id"),
                _require_nonempty(work_item_id, "work_item_id"),
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                membership_role=membership_role,
                membership_order=membership_order,
                source=source,
            )
        except ValueError as exc:
            raise ProjectLifecycleError(str(exc)) from exc
        if membership is None:
            raise ProjectLifecycleError("Project membership insert did not return a current membership")
        return membership

    def reorder_project_items(
        self,
        project_id: str,
        ordered_work_item_ids: list[str],
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        start_at: int = 1,
    ) -> list[dict[str, Any]]:
        normalized_project_id = _require_nonempty(project_id, "project_id")
        if self.db.get_project(normalized_project_id) is None:
            raise ProjectLifecycleError(f"Project not found: {normalized_project_id}")
        if start_at < 0:
            raise ProjectLifecycleError("start_at must be zero or greater")

        ordered_ids = [_require_nonempty(item_id, "work_item_id") for item_id in ordered_work_item_ids]
        if len(ordered_ids) != len(set(ordered_ids)):
            raise ProjectLifecycleError("reorder requires each work item id exactly once")

        current_memberships = self.db.list_project_work_items(normalized_project_id)
        current_by_work_item = {item["work_item_id"]: item for item in current_memberships}
        current_ids = set(current_by_work_item)
        requested_ids = set(ordered_ids)
        missing = sorted(current_ids - requested_ids)
        extra = sorted(requested_ids - current_ids)
        if missing or extra:
            parts = []
            if missing:
                parts.append(f"missing existing item(s): {', '.join(missing)}")
            if extra:
                parts.append(f"not in project: {', '.join(extra)}")
            raise ProjectLifecycleError("reorder must name the active membership set exactly; " + "; ".join(parts))

        reordered: list[dict[str, Any]] = []
        for offset, work_item_id in enumerate(ordered_ids):
            current = current_by_work_item[work_item_id]
            try:
                membership = self.db.link_project_work_item(
                    normalized_project_id,
                    work_item_id,
                    _require_nonempty(changed_by, "changed_by"),
                    _require_nonempty(change_reason, "change_reason"),
                    membership_role=current.get("membership_role") or "member",
                    membership_order=start_at + offset,
                    status=current.get("membership_status") or "active",
                    source=current.get("membership_source"),
                )
            except ValueError as exc:
                raise ProjectLifecycleError(str(exc)) from exc
            if membership is None:
                raise ProjectLifecycleError(f"Reorder did not return membership for {work_item_id}")
            reordered.append(membership)
        return reordered

    def retire_project(
        self,
        project_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        completed_at: str | None = None,
    ) -> dict[str, Any]:
        return self.update_project(
            project_id,
            changed_by=changed_by,
            change_reason=change_reason,
            status=PROJECT_TERMINAL_STATUS,
            completed_at=completed_at or _utc_now(),
        )

    def link_bridge_thread(
        self,
        project_id: str,
        bridge_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        relationship: str = "related",
        notes: str | None = None,
    ) -> dict[str, Any]:
        try:
            link = self.db.add_project_artifact_link(
                _require_nonempty(project_id, "project_id"),
                "bridge_thread",
                _require_nonempty(bridge_id, "bridge_id"),
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                relationship=relationship,
                notes=notes,
            )
        except ValueError as exc:
            raise ProjectLifecycleError(str(exc)) from exc
        if link is None:
            raise ProjectLifecycleError("Project artifact link insert did not return a current link")
        return link

    def authorize_project(
        self,
        project_id: str,
        *,
        owner_decision: str,
        name: str,
        scope: str,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        authorization_id: str | None = None,
        allowed_mutation_classes: list[str] | None = None,
        forbidden_operations: list[str] | None = None,
        included_work_item_ids: list[str] | None = None,
        excluded_work_item_ids: list[str] | None = None,
        included_spec_ids: list[str] | None = None,
        excluded_spec_ids: list[str] | None = None,
        expires_at: str | None = None,
    ) -> dict[str, Any]:
        try:
            authorization = self.db.insert_project_authorization(
                _require_nonempty(project_id, "project_id"),
                _require_nonempty(name, "name"),
                _require_nonempty(owner_decision, "owner_decision"),
                _require_nonempty(scope, "scope"),
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                id=authorization_id,
                status=ACTIVE_PROJECT_AUTHORIZATION_STATUS,
                allowed_mutation_classes=allowed_mutation_classes,
                forbidden_operations=forbidden_operations,
                included_work_item_ids=included_work_item_ids,
                excluded_work_item_ids=excluded_work_item_ids,
                included_spec_ids=included_spec_ids,
                excluded_spec_ids=excluded_spec_ids,
                expires_at=expires_at,
            )
        except ValueError as exc:
            message = str(exc)
            # WI-3312: the spec-linkage validator's ValueError cites the source
            # spec; re-raise it as the typed subclass so the CLI can map it to a
            # usage error. All other ValueErrors stay generic lifecycle errors.
            if "GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001" in message:
                raise ProjectAuthorizationSpecLinkageError(message) from exc
            raise ProjectLifecycleError(message) from exc
        if authorization is None:
            raise ProjectLifecycleError("Project authorization insert did not return a current authorization")
        return authorization

    def list_project_authorizations(
        self,
        project_id: str,
        *,
        include_terminal: bool = False,
    ) -> list[dict[str, Any]]:
        normalized_project_id = _require_nonempty(project_id, "project_id")
        if self.db.get_project(normalized_project_id) is None:
            raise ProjectLifecycleError(f"Project not found: {normalized_project_id}")
        return self.db.list_project_authorizations(normalized_project_id, include_terminal=include_terminal)

    def revoke_project_authorization(
        self,
        authorization_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
    ) -> dict[str, Any]:
        try:
            authorization = self.db.update_project_authorization(
                _require_nonempty(authorization_id, "authorization_id"),
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                status="revoked",
            )
        except ValueError as exc:
            raise ProjectLifecycleError(str(exc)) from exc
        if authorization is None:
            raise ProjectLifecycleError("Project authorization update did not return a current authorization")
        return authorization
