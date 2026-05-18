"""Deterministic project lifecycle operations over MemBase project records."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.authorization import ACTIVE_PROJECT_AUTHORIZATION_STATUS

PROJECT_TERMINAL_STATUS = "retired"
COMPLETED_PROJECT_AUTHORIZATION_STATUS = "completed"
PROJECTS_CHANGED_BY = "gt-projects"

# Bridge proposal/report metadata line: ``Work Item: WI-1234`` (or a GTKB-/
# WORKLIST- descriptive id), optionally backtick-wrapped.
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)


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

    def _project_membership_work_item_ids(self, project_id: str) -> list[str]:
        """Return the work-item ids linked to ``project_id`` via an active
        project-to-work-item membership link.

        GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 defines the
        completion-gating set as the project's explicitly-linked work items -
        the active project-to-work-item membership links - not the
        authorization envelope's ``included_work_item_ids`` list. The scanner
        (scripts/project_verified_completion_scanner.py) and this service both
        source the gating set from the membership link so the two agree.
        """
        memberships = self.db.list_project_work_items(_require_nonempty(project_id, "project_id"))
        return [
            str(membership["work_item_id"])
            for membership in memberships
            if str(membership.get("membership_status") or "").strip().lower() == "active"
        ]

    def _authorization_completion_ready(
        self, authorization: dict[str, Any], verified_work_items: set[str]
    ) -> bool:
        """True when ``authorization`` is active and every gating work item has
        a VERIFIED bridge thread.

        The gating set is the project's active membership-linked work items
        (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2). An authorization
        whose project has no active membership links is not completion-ready.
        """
        if authorization.get("status") != ACTIVE_PROJECT_AUTHORIZATION_STATUS:
            return False
        project_id = str(authorization.get("project_id") or "")
        if not project_id:
            return False
        included = self._project_membership_work_item_ids(project_id)
        return bool(included) and all(work_item in verified_work_items for work_item in included)

    @staticmethod
    def _verified_work_items(project_root: Path) -> set[str]:
        """Return work-item ids covered by a bridge thread whose latest
        ``bridge/INDEX.md`` status is ``VERIFIED``.

        Mirrors the IP-1 scanner's readiness check using the canonical bridge
        index parser directly. A cross-layer import of the ``scripts/`` scanner
        from package code was rejected as fragile; both call sites delegate to
        the same ``groundtruth_kb.bridge.detector.parse_index`` parser.
        """
        from groundtruth_kb.bridge.detector import BridgeStatus, parse_index

        root = Path(project_root)
        index_path = root / "bridge" / "INDEX.md"
        if not index_path.is_file():
            return set()
        result = parse_index(index_path.read_text(encoding="utf-8"), project_root=root)
        verified: set[str] = set()
        for document in result.documents:
            top = document.current_top
            if top is None or top.status != BridgeStatus.VERIFIED:
                continue
            for version in document.versions:
                file_path = root / version.file_path
                if not file_path.is_file():
                    continue
                text = file_path.read_text(encoding="utf-8", errors="replace")
                for match in _WORK_ITEM_LINE_RE.finditer(text):
                    verified.add(match.group(1).strip())
        return verified

    def _work_item_in_other_active_project(self, work_item_id: str, exclude_project_id: str) -> bool:
        """True when ``work_item_id`` has an active membership link in some
        non-terminal project other than ``exclude_project_id``.

        Used by collective retirement: a work item shared with another
        still-active project is not retired when one of its projects retires;
        only the retiring project's own membership link is retired.
        """
        for project in self.db.list_projects(include_terminal=False):
            other_project_id = str(project.get("id") or "")
            if not other_project_id or other_project_id == exclude_project_id:
                continue
            for membership in self.db.list_project_work_items(other_project_id):
                if str(membership.get("work_item_id") or "") == work_item_id:
                    return True
        return False

    def _retire_project_work_items(
        self,
        project_id: str,
        *,
        completed_authorization_id: str,
        changed_by: str = PROJECTS_CHANGED_BY,
    ) -> list[str]:
        """Collectively retire a retiring project's associated work items.

        GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 makes retirement
        collective: when a project retires, its active project-to-work-item
        membership links are retired, and each membership-linked work item is
        transitioned to ``resolution_status='retired'`` unless that work item
        is still an active member of another non-terminal project (a shared
        work item, left active for the other project).

        Only ``resolution_status`` is changed; the work item's ``stage`` is
        left untouched so the transition does not trip the GOV-15 owner-
        approval gate in ``_validate_stage_transition``. Collective retirement
        is automatic and takes no owner AskUserQuestion.

        Returns the ids of the work items transitioned to ``retired``.
        """
        change_reason = (
            f"Collective retirement: project {project_id} retired on completion of "
            f"authorization {completed_authorization_id} "
            "(GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3 collective-retirement clause)."
        )
        retired_work_items: list[str] = []
        for membership in self.db.list_project_work_items(project_id):
            work_item_id = str(membership.get("work_item_id") or "")
            if not work_item_id:
                continue
            # Retire this project's membership link; "retired" is non-active so
            # the link drops out of the active project-to-work-item set.
            self.db.link_project_work_item(
                project_id,
                work_item_id,
                changed_by,
                change_reason,
                membership_role=membership.get("membership_role") or "member",
                membership_order=membership.get("membership_order"),
                status="retired",
                source=membership.get("membership_source"),
            )
            # A work item shared with another non-terminal project stays active
            # for that project; only the membership link above is retired here.
            if self._work_item_in_other_active_project(work_item_id, project_id):
                continue
            work_item = self.db.get_work_item(work_item_id)
            if work_item is None:
                continue
            if str(work_item.get("resolution_status") or "") == "retired":
                continue
            self.db.update_work_item(
                work_item_id,
                changed_by,
                change_reason,
                resolution_status="retired",
            )
            retired_work_items.append(work_item_id)
        return retired_work_items

    def complete_project_authorization(
        self,
        authorization_id: str,
        *,
        project_root: Path,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
    ) -> dict[str, Any]:
        """Transition an active project authorization to ``completed`` and, when
        it was the project's sole active authorization, retire the project and
        collectively retire its associated work items and membership links.

        ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v2: completion and
        retirement are automatic once every gating work item is VERIFIED. There
        is no owner-confirmation gate - owner AUQ governs project START
        (authorization creation and approval), not completion. The gating set
        is the project's explicitly-linked work items: the active
        project-to-work-item membership links (v2's "explicitly linked"
        definition), not the authorization envelope's ``included_work_item_ids``.
        """
        norm_auth_id = _require_nonempty(authorization_id, "authorization_id")

        # Step 1: load the authorization; it must be active.
        authorization = self.db.get_project_authorization(norm_auth_id)
        if authorization is None:
            raise ProjectLifecycleError(f"Project authorization not found: {norm_auth_id}")
        if authorization.get("status") != ACTIVE_PROJECT_AUTHORIZATION_STATUS:
            raise ProjectLifecycleError(
                f"Project authorization {norm_auth_id} is not active "
                f"(status={authorization.get('status')!r}); cannot complete."
            )
        project_id = str(authorization.get("project_id") or "")

        # Step 2: readiness check - every gating work item must be VERIFIED.
        # The gating set is the project's active membership-linked work items
        # (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 "explicitly linked").
        included = self._project_membership_work_item_ids(project_id)
        if not included:
            raise ProjectLifecycleError(
                f"Project {project_id} has no active membership-linked work items; "
                "completion readiness cannot be established."
            )
        verified = self._verified_work_items(project_root)
        unverified = [wi for wi in included if wi not in verified]
        if unverified:
            raise ProjectLifecycleError(
                f"Project authorization {norm_auth_id} is not completion-ready; work item(s) "
                f"without a VERIFIED bridge thread: {', '.join(unverified)}."
            )

        # Step 3: transition the authorization to completed (status-only change).
        try:
            completed = self.db.update_project_authorization(
                norm_auth_id,
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                status=COMPLETED_PROJECT_AUTHORIZATION_STATUS,
            )
        except ValueError as exc:
            raise ProjectLifecycleError(str(exc)) from exc
        if completed is None:
            raise ProjectLifecycleError("Project authorization completion did not return a current authorization")

        # Step 4: retire the project iff no other active authorization remains,
        # and collectively retire the project's associated work items and
        # membership links (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001:
        # retirement is collective - project, authorization, and associated
        # VERIFIED work items retire together).
        other_active = [
            a
            for a in self.db.list_project_authorizations(project_id, status="active")
            if a.get("id") != norm_auth_id
        ]
        project_retired = False
        retired_work_items: list[str] = []
        if not other_active:
            self.retire_project(
                project_id,
                changed_by=changed_by,
                change_reason=(
                    f"Auto-retired: sole active authorization {norm_auth_id} completed "
                    "(GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3 automatic collective retirement)."
                ),
            )
            project_retired = True
            retired_work_items = self._retire_project_work_items(
                project_id,
                completed_authorization_id=norm_auth_id,
                changed_by=changed_by,
            )

        return {
            "authorization": completed,
            "project_retired": project_retired,
            "retired_work_items": retired_work_items,
        }

    def auto_complete_ready_authorizations(
        self,
        *,
        project_root: Path,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str = (
            "Auto-completed: all membership-linked work items VERIFIED "
            "(GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 automatic completion)."
        ),
    ) -> list[dict[str, Any]]:
        """Scan every active project authorization and auto-complete each one
        whose gating work items all have a VERIFIED bridge thread.

        ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v2: completion and
        retirement are automatic and require no owner confirmation. Idempotent -
        a completed authorization is no longer active, so a re-run does not
        re-process it. Returns one result dict per authorization completed in
        this pass.
        """
        verified = self._verified_work_items(project_root)
        completed: list[dict[str, Any]] = []
        for project in self.db.list_projects(include_terminal=False):
            project_id = str(project.get("id") or "")
            if not project_id:
                continue
            for authorization in self.db.list_project_authorizations(project_id, status="active"):
                if not self._authorization_completion_ready(authorization, verified):
                    continue
                result = self.complete_project_authorization(
                    str(authorization["id"]),
                    project_root=project_root,
                    changed_by=changed_by,
                    change_reason=change_reason,
                )
                completed.append(
                    {
                        "authorization_id": str(authorization["id"]),
                        "project_id": project_id,
                        "project_retired": result["project_retired"],
                        "retired_work_items": result.get("retired_work_items", []),
                    }
                )
        return completed
