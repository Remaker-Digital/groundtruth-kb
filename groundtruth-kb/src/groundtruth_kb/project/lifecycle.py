"""Deterministic project lifecycle operations over MemBase project records."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.authorization import ACTIVE_PROJECT_AUTHORIZATION_STATUS

PROJECT_TERMINAL_STATUS = "retired"
COMPLETED_PROJECT_AUTHORIZATION_STATUS = "completed"
PROJECTS_CHANGED_BY = "gt-projects"
WORK_ITEM_TERMINAL_RESOLUTION_STATUSES = frozenset({"verified", "resolved", "retired", "wont_fix", "not_a_defect"})
LOGGER = logging.getLogger(__name__)

# Bridge proposal/report metadata line: ``Work Item: WI-1234`` (including
# spec-intake ``WI-AUTO-*`` ids, or a GTKB-/WORKLIST- descriptive id),
# optionally backtick-wrapped.
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-AUTO-[A-Z0-9-]+|WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)
_COMPLETION_GUARD_RELATIONSHIP = "plan_incomplete"
_COMPLETION_GUARD_ARTIFACT_TYPES = ("completion_guard", "bridge_thread")


# WI-4737: id-agnostic recognition helpers. A work item whose VERIFIED bridge
# thread carries no regex-parseable ``Work Item:`` line (a non-canonical id, or
# a thread authored before its work item existed) is recognized as
# verified-for-project via its own ``related_bridge_threads`` field instead.
# These two helpers normalize that field and are mirrored byte-for-byte in
# ``scripts/project_verified_completion_scanner.py``.
def _thread_slug_from_ref(ref: object) -> str:
    """Normalize a ``related_bridge_threads`` entry to a bare thread slug.

    Accepts either a bare slug (``gtkb-foo``) or a versioned bridge-file path
    (``bridge/gtkb-foo-003.md``); returns the slug, or ``""`` when empty.
    """
    text = str(ref or "").strip()
    if not text:
        return ""
    base = text.replace("\\", "/").rsplit("/", 1)[-1]
    match = re.match(r"^(?P<slug>.+)-\d{3}\.md$", base)
    if match:
        return match.group("slug")
    if base.endswith(".md"):
        base = base[:-3]
    return base


def _related_thread_slugs(value: object) -> set[str]:
    """Parse a work item's ``related_bridge_threads`` field into a set of slugs.

    The field may be a JSON string, a list, or ``None``; unparseable input
    yields the empty set (defensive — never raises).
    """
    if value is None:
        return set()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (ValueError, TypeError):
            return set()
    if not isinstance(value, (list, tuple)):
        return set()
    return {slug for slug in (_thread_slug_from_ref(item) for item in value) if slug}


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
            str(values["name"]),
            _require_nonempty(changed_by, "changed_by"),
            _require_nonempty(change_reason, "change_reason"),
            id=current["id"],
            status=str(values["status"]),
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

    def remove_project_item(
        self,
        project_id: str,
        work_item_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        status: str = "removed",
    ) -> dict[str, Any]:
        """Detach a work item from a project via an append-only non-active membership version.

        Appends a new ``project_work_item_memberships`` version with a non-active
        ``status`` (default ``"removed"``), carrying forward the current active
        membership's role/order/source. The active-set filter in
        ``list_project_work_items`` excludes non-active statuses, so this detaches
        the membership while preserving the prior active version for audit.

        Non-active-status invariant (WI-4266 NO-GO -004 F2): a command named
        ``remove`` must never append an *active* membership. Empty status or any
        case-insensitive ``"active"`` is rejected. Fails closed when there is no
        active membership to remove.
        """
        normalized_status = str(status or "").strip()
        if not normalized_status or normalized_status.lower() == "active":
            raise ProjectLifecycleError(
                f"remove-item requires a non-active status; got {status!r}. "
                "A removal must not append an active membership version."
            )
        normalized_project_id = _require_nonempty(project_id, "project_id")
        normalized_work_item_id = _require_nonempty(work_item_id, "work_item_id")
        current = next(
            (
                membership
                for membership in self.db.list_project_work_items(normalized_project_id)
                if membership.get("work_item_id") == normalized_work_item_id
            ),
            None,
        )
        if current is None:
            raise ProjectLifecycleError(
                f"No active membership to remove for {normalized_work_item_id} in {normalized_project_id}"
            )
        try:
            membership = self.db.link_project_work_item(
                normalized_project_id,
                normalized_work_item_id,
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                membership_role=current.get("membership_role") or "member",
                membership_order=current.get("membership_order"),
                status=normalized_status,
                source=current.get("membership_source"),
            )
        except ValueError as exc:
            raise ProjectLifecycleError(str(exc)) from exc
        if membership is None:
            raise ProjectLifecycleError("Project membership removal did not return a current membership")
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

    def _project_keep_open_elected(self, project_id: str) -> bool:
        """True when durable project/authorization history preserves keep-open.

        ``complete_project_authorization(..., retire_project=False)`` completes
        the current authorization while intentionally leaving the project active.
        There is no separate keep-open boolean, so the conservative durable
        signal is: current project is active, at least one current authorization
        is completed, and no current authorization remains active.
        """
        normalized_project_id = _require_nonempty(project_id, "project_id")
        project = self.db.get_project(normalized_project_id)
        if project is None or str(project.get("status") or "").strip().lower() != "active":
            return False
        authorizations = self.db.list_project_authorizations(normalized_project_id, include_terminal=True)
        has_completed = any(
            str(authorization.get("status") or "").strip().lower() == COMPLETED_PROJECT_AUTHORIZATION_STATUS
            for authorization in authorizations
        )
        has_active = any(
            str(authorization.get("status") or "").strip().lower() == ACTIVE_PROJECT_AUTHORIZATION_STATUS
            for authorization in authorizations
        )
        return has_completed and not has_active

    def member_completion_status(self, project_id: str) -> dict[str, Any]:
        """Return the v6 member-WI automatic-retirement readiness record.

        ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v6 retires an
        active project automatically only when it has active member WIs, every
        active member WI has a terminal ``resolution_status``, no active
        ``plan_incomplete`` guard exists, and no caller has taken the
        keep-open election.
        """
        normalized_project_id = _require_nonempty(project_id, "project_id")
        project = self.db.get_project(normalized_project_id)
        if project is None:
            raise ProjectLifecycleError(f"Project not found: {normalized_project_id}")
        memberships = self.db.list_project_work_items(normalized_project_id)
        member_ids: list[str] = []
        terminal_ids: list[str] = []
        nonterminal_ids: list[str] = []
        nonterminal_statuses: dict[str, str] = {}
        for membership in memberships:
            work_item_id = str(membership.get("work_item_id") or "")
            if not work_item_id:
                continue
            member_ids.append(work_item_id)
            status = str(membership.get("resolution_status") or "").strip().lower()
            if status in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES:
                terminal_ids.append(work_item_id)
            else:
                nonterminal_ids.append(work_item_id)
                nonterminal_statuses[work_item_id] = status

        guard_refs = self._project_completion_guard_refs(normalized_project_id)
        keep_open_elected = self._project_keep_open_elected(normalized_project_id)
        completion_ready = bool(member_ids) and not nonterminal_ids and not guard_refs and not keep_open_elected
        exclusion_reasons: list[str] = []
        if not member_ids:
            exclusion_reasons.append("zero_active_members")
        if nonterminal_ids:
            exclusion_reasons.append("nonterminal_member_work_items")
        if guard_refs:
            exclusion_reasons.append("plan_incomplete_guard")
        if keep_open_elected:
            exclusion_reasons.append("keep_open_election")

        return {
            "project_id": normalized_project_id,
            "active_member_work_item_ids": member_ids,
            "terminal_work_item_ids": terminal_ids,
            "nonterminal_work_item_ids": nonterminal_ids,
            "nonterminal_work_item_statuses": nonterminal_statuses,
            "completion_guarded": bool(guard_refs),
            "completion_guard_refs": guard_refs,
            "keep_open_elected": keep_open_elected,
            "completion_ready": completion_ready,
            "exclusion_reasons": exclusion_reasons,
        }

    def member_completion_ready(self, project_id: str) -> bool:
        """Return true when a project satisfies the v6 member-WI criterion."""
        return bool(self.member_completion_status(project_id)["completion_ready"])

    def _authorization_completion_ready(
        self,
        authorization: dict[str, Any],
        verified_for_project: set[str],
        guarded_project_ids: set[str] | None = None,
        non_verified_implements_by_project: dict[str, set[str]] | None = None,
    ) -> bool:
        """True when ``authorization`` is active and every gating work item is in
        ``verified_for_project`` and every active addressing thread is VERIFIED.

        ``verified_for_project`` is the PROJECT-SCOPED verified set for this
        authorization's project (per ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001``
        v4): the caller looks it up by ``project_id`` from
        ``_verified_work_items_by_project()``. Passing a project-scoped set
        (not a global one) is the NO-GO -012 F1 fix — coverage from one
        project's implements-linked threads cannot satisfy another project's
        authorization. (The fail-safe diagnostic deliberately passes the global
        v3 baseline instead, to compute "what v3 would have completed".)

        The gating set is the project's active membership-linked work items
        (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001). An authorization
        whose project has no active membership links is not completion-ready.
        """
        if authorization.get("status") != ACTIVE_PROJECT_AUTHORIZATION_STATUS:
            return False
        project_id = str(authorization.get("project_id") or "")
        if not project_id:
            return False
        if guarded_project_ids is not None and project_id in guarded_project_ids:
            return False
        if non_verified_implements_by_project and non_verified_implements_by_project.get(project_id):
            return False
        included = self._project_membership_work_item_ids(project_id)
        return bool(included) and all(work_item in verified_for_project for work_item in included)

    def _completion_guards_by_project(self) -> dict[str, list[dict[str, Any]]]:
        """Return active ``plan_incomplete`` completion guards keyed by project."""
        rows = (
            self.db._get_conn()
            .execute(
                "SELECT project_id, artifact_type, artifact_ref, relationship, notes "
                "FROM current_project_artifact_links "
                "WHERE status = 'active' "
                "AND relationship = ? "
                f"AND artifact_type IN ({', '.join('?' for _ in _COMPLETION_GUARD_ARTIFACT_TYPES)}) "
                "ORDER BY project_id, artifact_type, artifact_ref",
                (_COMPLETION_GUARD_RELATIONSHIP, *_COMPLETION_GUARD_ARTIFACT_TYPES),
            )
            .fetchall()
        )
        guards: dict[str, list[dict[str, Any]]] = {}
        for project_id, artifact_type, artifact_ref, relationship, notes in rows:
            if not project_id:
                continue
            guards.setdefault(str(project_id), []).append(
                {
                    "project_id": str(project_id),
                    "artifact_type": str(artifact_type or ""),
                    "artifact_ref": str(artifact_ref or ""),
                    "relationship": str(relationship or ""),
                    "notes": notes,
                }
            )
        return guards

    def _project_completion_guard_refs(self, project_id: str) -> list[dict[str, Any]]:
        return self._completion_guards_by_project().get(project_id, [])

    def _implements_links_by_project(self) -> dict[str, set[str]]:
        """Return ``{project_id: {bridge_thread_slug}}`` for active implements links.

        v4 PROJECT-SCOPED 'addressing-thread' discriminator per
        ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v4 clause (a):
        coverage from a thread T accrues ONLY to the project(s) that themselves
        hold an active ``project_artifact_links`` row (``artifact_type =
        'bridge_thread'``, ``relationship = 'implements'``, ``status =
        'active'``) for T's slug. A link held by a *different* project does not
        transfer coverage (NO-GO -012 F1 fix). Incidental ``'related'`` /
        ``'implementation_proposal'`` / ``'source_evidence'`` links do not
        contribute. Reads ``current_project_artifact_links`` (latest-version
        view) so superseded rows are excluded.
        """
        rows = (
            self.db._get_conn()
            .execute(
                "SELECT project_id, artifact_ref FROM current_project_artifact_links "
                "WHERE artifact_type = 'bridge_thread' "
                "AND relationship = 'implements' "
                "AND status = 'active'"
            )
            .fetchall()
        )
        by_project: dict[str, set[str]] = {}
        for project_id, slug in rows:
            if project_id and slug:
                by_project.setdefault(str(project_id), set()).add(str(slug))
        return by_project

    @staticmethod
    def _latest_bridge_thread_statuses(project_root: Path) -> dict[str, str | None]:
        """Return ``{bridge_thread_slug: latest_status}`` from versioned bridge files."""
        from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

        root = Path(project_root)
        bridge_dir = root / "bridge"
        if not bridge_dir.is_dir():
            return {}
        grouped: dict[str, list[tuple[int, Path]]] = {}
        bridge_file_re = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")
        for path in bridge_dir.glob("*.md"):
            match = bridge_file_re.match(path.name)
            if match is None:
                continue
            grouped.setdefault(match.group("slug"), []).append((int(match.group("version")), path))
        return {
            slug: status_from_bridge_file(max(versioned_files, key=lambda item: item[0])[1])
            for slug, versioned_files in grouped.items()
        }

    def _non_verified_implements_threads_by_project(self, project_root: Path) -> dict[str, set[str]]:
        """Return active ``implements`` bridge threads whose latest status is not VERIFIED."""
        links_by_project = self._implements_links_by_project()
        statuses_by_thread = self._latest_bridge_thread_statuses(project_root)
        blocked_by_project: dict[str, set[str]] = {}
        for project_id, slugs in links_by_project.items():
            non_verified = {slug for slug in slugs if statuses_by_thread.get(slug) != "VERIFIED"}
            if non_verified:
                blocked_by_project[project_id] = non_verified
        return blocked_by_project

    @staticmethod
    def _verified_thread_work_items(project_root: Path) -> dict[str, set[str]]:
        """Return ``{bridge_thread_slug: {work_item_id}}`` for VERIFIED-topped threads.

        Scans ALL versions of each VERIFIED-topped thread for ``Work Item:``
        metadata (D3 corrected scope).
        """
        from groundtruth_kb.bridge.versioned_files import status_from_bridge_file

        root = Path(project_root)
        bridge_dir = root / "bridge"
        if not bridge_dir.is_dir():
            return {}
        grouped: dict[str, list[tuple[int, Path]]] = {}
        bridge_file_re = re.compile(r"^(?P<slug>.+)-(?P<version>\d{3})\.md$")
        for path in bridge_dir.glob("*.md"):
            match = bridge_file_re.match(path.name)
            if match is None:
                continue
            grouped.setdefault(match.group("slug"), []).append((int(match.group("version")), path))
        by_thread: dict[str, set[str]] = {}
        for slug, versioned_files in grouped.items():
            latest_path = max(versioned_files, key=lambda item: item[0])[1]
            if status_from_bridge_file(latest_path) != "VERIFIED":
                continue
            wis: set[str] = set()
            for _version, file_path in sorted(versioned_files):
                if not file_path.is_file():
                    continue
                text = file_path.read_text(encoding="utf-8", errors="replace")
                for match in _WORK_ITEM_LINE_RE.finditer(text):
                    wis.add(match.group(1).strip())
            if wis:
                by_thread[slug] = wis
        return by_thread

    def _verified_work_items_by_project(self, project_root: Path) -> dict[str, set[str]]:
        """Return ``{project_id: {verified work_item_id}}`` (project-scoped; F1 fix).

        WI-X is VERIFIED *for project P* iff P holds an active
        ``relationship='implements'`` link to a VERIFIED-topped thread that
        either (regex path) cites WI-X in a ``Work Item:`` line, or (WI-4737
        id-agnostic path) is named in WI-X's own ``related_bridge_threads``
        while WI-X is an active member of P. Mirrors the scanner's
        ``verified_work_items_by_project()``. This is the only
        completion-authorizing view; there is no global decision set.
        """
        links_by_project = self._implements_links_by_project()
        wis_by_thread = self._verified_thread_work_items(project_root)
        statuses_by_thread = self._latest_bridge_thread_statuses(project_root)
        verified_by_project: dict[str, set[str]] = {}
        for project_id, slugs in links_by_project.items():
            verified: set[str] = set()
            # Regex path: WIs cited by a ``Work Item:`` line in a VERIFIED thread.
            for slug in slugs:
                verified |= wis_by_thread.get(slug, set())
            # WI-4737 additive path: an active member WI that names a VERIFIED
            # implements-linked thread in its own ``related_bridge_threads``
            # (two-sided guard: the project's implements-link AND the WI's
            # reference must agree). Recognizes work items whose VERIFIED thread
            # carries no regex-parseable ``Work Item:`` line.
            verified_implements_slugs = {s for s in slugs if statuses_by_thread.get(s) == "VERIFIED"}
            if verified_implements_slugs:
                for membership in self.db.list_project_work_items(project_id):
                    if str(membership.get("membership_status") or "").strip().lower() != "active":
                        continue
                    work_item_id = str(membership.get("work_item_id") or "")
                    if not work_item_id or work_item_id in verified:
                        continue
                    work_item = self.db.get_work_item(work_item_id)
                    if work_item is None:
                        continue
                    if _related_thread_slugs(work_item.get("related_bridge_threads")) & verified_implements_slugs:
                        verified.add(work_item_id)
            verified_by_project[project_id] = verified
        return verified_by_project

    def _all_verified_work_items(self, project_root: Path) -> set[str]:
        """Return the GLOBAL union of WIs cited by any VERIFIED-topped thread.

        This is the v3 (over-broad, project-blind) baseline. It is used ONLY by
        the ``include_fail_safe_pauses`` diagnostic in
        ``auto_complete_ready_authorizations()`` to compute "what v3 would have
        completed" — never for a completion authorization decision (which is
        always project-scoped via ``_verified_work_items_by_project()``).
        """
        wis_by_thread = self._verified_thread_work_items(project_root)
        out: set[str] = set()
        for wis in wis_by_thread.values():
            out |= wis
        return out

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
        retire_project: bool = True,
    ) -> dict[str, Any]:
        """Transition an active project authorization to ``completed`` and, when
        elected by the caller and it was the project's sole active authorization,
        retire the project and collectively retire its associated work items and
        membership links.

        ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v5: completion and
        retirement are automatic once every gating work item is VERIFIED. There
        is no owner-confirmation gate - owner AUQ governs project START
        (authorization creation and approval), not completion. The gating set
        is the project's explicitly-linked work items: the active
        project-to-work-item membership links (v2's "explicitly linked"
        definition), not the authorization envelope's ``included_work_item_ids``.
        ``retire_project=False`` is the explicit v5 keep-open caller election;
        the default preserves automatic project retirement.
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
        guard_refs = self._project_completion_guard_refs(project_id)
        if guard_refs:
            refs = ", ".join(
                f"{ref['artifact_type']}:{ref['artifact_ref']} ({ref['relationship']})" for ref in guard_refs
            )
            raise ProjectLifecycleError(
                f"Project {project_id} has an active plan_incomplete completion guard; "
                f"authorization {norm_auth_id} cannot be completed until it is removed or superseded. "
                f"Guard refs: {refs}."
            )
        included = self._project_membership_work_item_ids(project_id)
        if not included:
            raise ProjectLifecycleError(
                f"Project {project_id} has no active membership-linked work items; "
                "completion readiness cannot be established."
            )
        non_verified_implements = sorted(
            self._non_verified_implements_threads_by_project(project_root).get(project_id, set())
        )
        if non_verified_implements:
            raise ProjectLifecycleError(
                f"Project authorization {norm_auth_id} is not completion-ready; active implements "
                f"bridge thread(s) are not VERIFIED: {', '.join(non_verified_implements)}."
            )
        # Project-scoped verified set (v4 F1 fix): only THIS project's own
        # implements-linked VERIFIED threads count toward its completion.
        verified = self._verified_work_items_by_project(project_root).get(project_id, set())
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
            a for a in self.db.list_project_authorizations(project_id, status="active") if a.get("id") != norm_auth_id
        ]
        project_retired = False
        retired_work_items: list[str] = []
        if retire_project and not other_active:
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
            "(GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v4 automatic completion)."
        ),
        include_fail_safe_pauses: bool = False,
    ) -> list[dict[str, Any]]:
        """Scan every active project authorization; auto-complete those whose
        gating work items are all covered by an implements-linked VERIFIED
        bridge thread; optionally emit fail-safe manual-review records for
        those that would have completed under v3 but are paused under v4.

        ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v4: completion and
        retirement are automatic on the implements-linked all-WI-VERIFIED
        condition (clause (a)+(b)+(c)). When a project has gating WIs but no
        implements-linked VERIFIED thread covers them, the auto-completion
        pass does NOT fire and the condition is surfaced as a manual-review
        record (clause (d): the fail-safe direction is "auto-completion
        paused" rather than "spurious retirement").

        The fail-safe surface is opt-in (``include_fail_safe_pauses=True``)
        so existing callers - notably the byte-identical
        ``project-completion-surface`` hooks per ADR-CODEX-HOOK-PARITY-FALLBACK-001
        - receive the historical return shape unchanged. New callers (tests,
        diagnostic surfaces, future hook upgrades) opt in to receive both
        kinds of records, distinguished by the ``outcome`` key.

        Return record shape:
          ``outcome="completed"`` - existing shape + new outcome key:
              ``authorization_id``, ``project_id``, ``project_retired``,
              ``retired_work_items``, ``outcome="completed"``.
          ``outcome="manual_review_required"`` (opt-in only):
              ``authorization_id``, ``project_id``, ``outcome``, ``reason``,
              ``gating_work_items``, ``covered_under_v3``, ``missing_under_v4``.

        Idempotent: a completed authorization is no longer active, so a re-run
        does not re-process it. The fail-safe records are read-only (no
        mutation); a re-run yields the same set until ``implements`` links are
        backfilled (Phase-2).
        """
        # Project-scoped decision map (v4 F1 fix): {project_id: {verified WI}}.
        verified_by_project = self._verified_work_items_by_project(project_root)
        non_verified_implements_by_project = self._non_verified_implements_threads_by_project(project_root)
        guards_by_project = self._completion_guards_by_project()
        guarded_project_ids = set(guards_by_project)
        # Global v3 baseline (over-broad, project-blind) used ONLY for the
        # fail-safe diagnostic — never for a completion decision.
        verified_global_v3: set[str] | None = (
            self._all_verified_work_items(project_root) if include_fail_safe_pauses else None
        )
        records: list[dict[str, Any]] = []
        for project in self.db.list_projects(include_terminal=False):
            project_id = str(project.get("id") or "")
            if not project_id:
                continue
            if project_id in guarded_project_ids:
                continue
            project_verified = verified_by_project.get(project_id, set())
            for authorization in self.db.list_project_authorizations(project_id, status="active"):
                authorization_id = str(authorization["id"])
                if self._authorization_completion_ready(
                    authorization,
                    project_verified,
                    guarded_project_ids,
                    non_verified_implements_by_project,
                ):
                    result = self.complete_project_authorization(
                        authorization_id,
                        project_root=project_root,
                        changed_by=changed_by,
                        change_reason=change_reason,
                    )
                    records.append(
                        {
                            "outcome": "completed",
                            "authorization_id": authorization_id,
                            "project_id": project_id,
                            "project_retired": result["project_retired"],
                            "retired_work_items": result.get("retired_work_items", []),
                        }
                    )
                    continue
                if not include_fail_safe_pauses or verified_global_v3 is None:
                    continue
                # v4 clause (d) fail-safe: emit manual-review record when the
                # authorization would have completed under v3 (over-broad,
                # project-blind, incidental-citation-inclusive) but is correctly
                # held under v4's project-scoped set. This precisely targets the
                # transition-window cases that need Phase-2 backfill: the auths
                # that WOULD have auto-retired under v3 and are now paused for
                # safety. The v3 baseline is the global verified set; the v4
                # decision is the project-scoped set.
                if not self._authorization_completion_ready(
                    authorization,
                    verified_global_v3,
                    guarded_project_ids,
                    non_verified_implements_by_project,
                ):
                    continue
                gating = self._project_membership_work_item_ids(project_id)
                missing_under_v4 = [wi for wi in gating if wi not in project_verified]
                covered_under_v3 = [wi for wi in gating if wi in verified_global_v3]
                records.append(
                    {
                        "outcome": "manual_review_required",
                        "authorization_id": authorization_id,
                        "project_id": project_id,
                        "reason": "no_implements_linked_thread_covers_gating_wis",
                        "gating_work_items": gating,
                        "covered_under_v3": covered_under_v3,
                        "missing_under_v4": missing_under_v4,
                    }
                )
        return records

    def auto_retire_completed_projects(
        self,
        *,
        project_root: Path,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str = (
            "Auto-retired: all active member work items reached terminal resolution "
            "and no keep-open election is present "
            "(GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v6 automatic retirement)."
        ),
    ) -> list[dict[str, Any]]:
        """Retire active projects satisfying the v6 member-WI criterion.

        ``project_root`` is accepted for API symmetry with the existing
        authorization-completion actuator and for call-site traceability; the
        v6 member-WI criterion itself is MemBase-backed. Best-effort behavior
        is per project: lifecycle errors are logged and skipped.
        """
        _ = project_root
        records: list[dict[str, Any]] = []
        for project in self.db.list_projects(include_terminal=False):
            project_id = str(project.get("id") or "")
            if not project_id:
                continue
            try:
                status = self.member_completion_status(project_id)
                if not status["completion_ready"]:
                    continue
                self.retire_project(
                    project_id,
                    changed_by=changed_by,
                    change_reason=change_reason,
                )
                retired_work_items = self._retire_project_work_items(
                    project_id,
                    completed_authorization_id="member-terminal-resolution",
                    changed_by=changed_by,
                )
            except ProjectLifecycleError as exc:
                LOGGER.warning("Skipping automatic project retirement for %s: %s", project_id, exc)
                continue
            records.append(
                {
                    "outcome": "retired",
                    "project_id": project_id,
                    "project_retired": True,
                    "retired_work_items": retired_work_items,
                    "member_completion_status": status,
                }
            )
        return records
