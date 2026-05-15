"""Deterministic project lifecycle operations over MemBase project records."""

from __future__ import annotations

import json
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

    @staticmethod
    def _authorization_work_item_ids(authorization: dict[str, Any]) -> list[str]:
        """Decode an authorization's ``included_work_item_ids`` to a list."""
        parsed = authorization.get("included_work_item_ids_parsed")
        if isinstance(parsed, list):
            return [str(value) for value in parsed]
        raw = authorization.get("included_work_item_ids")
        if not raw:
            return []
        try:
            decoded = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []
        return [str(value) for value in decoded] if isinstance(decoded, list) else []

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

    def complete_project_authorization(
        self,
        authorization_id: str,
        owner_decision_deliberation_id: str,
        *,
        project_root: Path,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
    ) -> dict[str, Any]:
        """Transition an active project authorization to ``completed`` and, when
        it was the project's sole active authorization, retire the project.

        IP-3 of WI-3316 (``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001``).
        Owner confirmation is mandatory and auto-transition is prohibited:
        ``owner_decision_deliberation_id`` must resolve to a genuine
        owner-decision deliberation (``source_type='owner_conversation'`` AND
        ``outcome='owner_decision'``) whose text records the completion context
        for THIS project or authorization. An LO-review, informational, or
        no-go deliberation, or an owner decision recorded for a different
        project, is rejected.
        """
        norm_auth_id = _require_nonempty(authorization_id, "authorization_id")
        norm_delib_id = _require_nonempty(owner_decision_deliberation_id, "owner_decision_deliberation_id")

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

        # Step 2: owner-confirmation gate (existence is insufficient).
        deliberation = self.db.get_deliberation(norm_delib_id)
        if deliberation is None:
            raise ProjectLifecycleError(
                f"Owner-decision deliberation not found: {norm_delib_id}. "
                "Auto-transition is prohibited; an owner-decision deliberation is required."
            )
        if deliberation.get("source_type") != "owner_conversation":
            raise ProjectLifecycleError(
                f"Deliberation {norm_delib_id} is not an owner conversation "
                f"(source_type={deliberation.get('source_type')!r}); completion requires "
                "a genuine owner decision."
            )
        if deliberation.get("outcome") != "owner_decision":
            raise ProjectLifecycleError(
                f"Deliberation {norm_delib_id} is not an owner decision "
                f"(outcome={deliberation.get('outcome')!r}); an LO-review, informational, "
                "or no-go deliberation cannot confirm completion."
            )
        context_text = " ".join(
            str(deliberation.get(field) or "")
            for field in ("content", "source_ref", "change_reason", "title", "summary")
        )
        if project_id not in context_text and norm_auth_id not in context_text:
            raise ProjectLifecycleError(
                f"Deliberation {norm_delib_id} does not record the completion context for "
                f"project {project_id} / authorization {norm_auth_id}; the owner decision "
                "must reference this project or authorization."
            )

        # Step 3: re-run the IP-1 readiness check for this authorization.
        included = self._authorization_work_item_ids(authorization)
        if not included:
            raise ProjectLifecycleError(
                f"Project authorization {norm_auth_id} lists no work items; "
                "completion readiness cannot be established."
            )
        verified = self._verified_work_items(project_root)
        unverified = [wi for wi in included if wi not in verified]
        if unverified:
            raise ProjectLifecycleError(
                f"Project authorization {norm_auth_id} is not completion-ready; work item(s) "
                f"without a VERIFIED bridge thread: {', '.join(unverified)}."
            )

        # Step 4: transition the authorization to completed (status-only change).
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

        # Step 5: retire the project iff no other active authorization remains.
        other_active = [
            a
            for a in self.db.list_project_authorizations(project_id, status="active")
            if a.get("id") != norm_auth_id
        ]
        project_retired = False
        if not other_active:
            self.retire_project(
                project_id,
                changed_by=changed_by,
                change_reason=(
                    f"Auto-retired: sole active authorization {norm_auth_id} completed "
                    f"per owner decision {norm_delib_id}."
                ),
            )
            project_retired = True

        return {"authorization": completed, "project_retired": project_retired}
