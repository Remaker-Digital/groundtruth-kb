"""Deterministic project lifecycle operations over MemBase project records."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.db import KnowledgeDB

PROJECT_TERMINAL_STATUS = "retired"
PROJECT_TERMINAL_STATUSES = frozenset({"completed", "retired", "cancelled"})
PROJECTS_CHANGED_BY = "gt-projects"
WORK_ITEM_TERMINAL_RESOLUTION_STATUSES = frozenset({"verified", "resolved", "retired", "wont_fix", "not_a_defect"})
LOGGER = logging.getLogger(__name__)

PROJECT_DEPENDENCY_KIND_REGISTRY_VERSION = 1
PROJECT_DEPENDENCY_KIND_REGISTRY: dict[str, dict[str, Any]] = {
    "requires_project_state": {
        "supported_required_states": ("active", "completed", "retired", "cancelled"),
        "satisfying_states": {
            "active": ("active",),
            "completed": ("completed", "retired"),
            "retired": ("retired",),
            "cancelled": ("cancelled",),
        },
        "supported_affected_gates": ("readiness", "authorization", "promotion", "closure"),
        "hard_dependency": True,
        "recovery_command": "gt projects dependencies recover <dependency-id>",
    }
}

# Bridge proposal/report metadata line: ``Work Item: WI-1234`` (including
# spec-intake ``WI-AUTO-*`` ids, or a GTKB-/WORKLIST- descriptive id),
# optionally backtick-wrapped.
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-AUTO-[A-Z0-9-]+|WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)
_PROJECT_LINE_RE = re.compile(r"^Project:\s*`?([^`\r\n]+)`?\s*$", re.MULTILINE)
_COMPLETION_GUARD_RELATIONSHIP = "plan_incomplete"
_COMPLETION_KEEP_OPEN_ARTIFACT_TYPE = "completion_guard"
_COMPLETION_BLOCKING_ARTIFACT_TYPE = "bridge_thread"
_COMPLETION_GUARD_ARTIFACT_TYPES = (_COMPLETION_KEEP_OPEN_ARTIFACT_TYPE, _COMPLETION_BLOCKING_ARTIFACT_TYPE)
_RETIRE_ITEM_DISALLOWED_STATUSES = frozenset({"", "active", "removed"})


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
        authorization: str | None = None,
        kind: str = "project",
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
            authorization=authorization,
            kind=kind,
        )
        if project is None:
            raise ProjectLifecycleError("Project insert did not return a current project")
        return project

    def list_projects(
        self, *, include_terminal: bool = False, status: str | None = None, kind: str | None = None
    ) -> list[dict[str, Any]]:
        return self.db.list_projects(include_terminal=include_terminal, status=status, kind=kind)

    def show_project(self, project_id: str) -> dict[str, Any]:
        project = self.db.get_project(_require_nonempty(project_id, "project_id"))
        if project is None:
            raise ProjectLifecycleError(f"Project not found: {project_id}")
        return {
            "project": project,
            "projects": [
                child
                for child in self.db.list_projects(include_terminal=True)
                if child.get("parent_project_id") == project_id
            ]
            if project["kind"] == "program"
            else [],
            "work_items": self.db.list_project_work_items(project["id"]),
            "dependencies": self.list_project_dependencies(project["id"]),
            "artifact_links": self.db.list_project_artifact_links(project["id"]),
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

        if "authorization" in fields:
            from groundtruth_kb.db import _VALID_AUTHORIZATION_VALUES

            candidate = str(fields["authorization"] or "").strip()
            if candidate not in _VALID_AUTHORIZATION_VALUES:
                raise ProjectLifecycleError(
                    f"authorization must be one of {sorted(_VALID_AUTHORIZATION_VALUES)}; got {candidate!r}"
                )
            fields["authorization"] = candidate

        allowed_fields = {
            "kind",
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
            # WI-7657: authorization is a field on the project row, and this is
            # the governed path that sets it. Before this, WI-7611 added the
            # column but shipped no writer other than its own one-time
            # migration, so the value the model calls authoritative could not be
            # changed by the owner at all.
            "authorization",
        }
        unknown = sorted(set(fields) - allowed_fields)
        if unknown:
            raise ProjectLifecycleError(f"Unsupported project fields: {', '.join(unknown)}")

        values = {field: fields.get(field, current.get(field)) for field in allowed_fields}
        if values["kind"] == "program":
            if "authorization" in fields:
                raise ProjectLifecycleError("Programs have no authorization field")
            values["authorization"] = None
        current_status = str(current.get("status") or "").strip().lower()
        requested_status = str(values.get("status") or "").strip().lower()
        if current_status not in PROJECT_TERMINAL_STATUSES and requested_status in PROJECT_TERMINAL_STATUSES:
            self._require_project_dependency_gate_ready(current["id"], "closure")
            active_dependencies = self.db.list_project_dependencies(current["id"])
            blocking_dependencies: list[str] = []
            for dependency in active_dependencies:
                if dependency.get("dependent_project_id") == current["id"]:
                    blocking_dependencies.append(str(dependency["id"]))
                    continue
                definition = PROJECT_DEPENDENCY_KIND_REGISTRY.get(str(dependency.get("dependency_kind") or ""))
                required_state = str(dependency.get("required_prerequisite_state") or "")
                satisfying_states = (
                    tuple(definition["satisfying_states"].get(required_state, ())) if definition is not None else ()
                )
                if requested_status not in satisfying_states:
                    blocking_dependencies.append(str(dependency["id"]))
            if blocking_dependencies:
                dependency_ids = ", ".join(sorted(blocking_dependencies))
                raise ProjectLifecycleError(
                    "Project cannot enter the requested terminal state while active dependency edges would "
                    "become invalid; "
                    f"retire these dependencies first: {dependency_ids}"
                )
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
            authorization=values["authorization"],
            kind=values["kind"],
        )
        if project is None:
            raise ProjectLifecycleError("Project update did not return a current project")
        return project

    def _append_membership(
        self,
        *,
        project_id: str,
        changed_by: str,
        change_reason: str,
        link,
        missing_message: str,
    ) -> dict[str, Any]:
        conn = self.db._get_conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            membership = link()
            if membership is None:
                raise ProjectLifecycleError(missing_message)
            # WI-7657: the same-transaction reauthorization is gone. A membership
            # change appended a new project_authorizations version as a side
            # effect, which both wrote to a retired table and had an agent
            # setting authorization -- something only owner direction does.
            # Membership is now recorded on its own, and the project's
            # authorization is untouched by it.
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return membership

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
        normalized_project_id = _require_nonempty(project_id, "project_id")
        normalized_changed_by = _require_nonempty(changed_by, "changed_by")
        normalized_change_reason = _require_nonempty(change_reason, "change_reason")

        def _link() -> dict[str, Any] | None:
            try:
                return self.db.link_project_work_item(
                    normalized_project_id,
                    _require_nonempty(work_item_id, "work_item_id"),
                    normalized_changed_by,
                    normalized_change_reason,
                    membership_role=membership_role,
                    membership_order=membership_order,
                    source=source,
                    commit=False,
                )
            except ValueError as exc:
                raise ProjectLifecycleError(str(exc)) from exc

        return self._append_membership(
            project_id=normalized_project_id,
            changed_by=normalized_changed_by,
            change_reason=normalized_change_reason,
            link=_link,
            missing_message="Project membership insert did not return a current membership",
        )

    def move_project_item(
        self,
        work_item_id: str,
        source_project_id: str,
        target_project_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        membership_order: int | None = None,
    ) -> dict[str, Any]:
        """Move a single-parent item atomically; neither project's authorization changes."""
        from groundtruth_kb.project.membership_resolver import resolve_execution_membership

        work_item_id = _require_nonempty(work_item_id, "work_item_id")
        source_project_id = _require_nonempty(source_project_id, "source_project_id")
        target_project_id = _require_nonempty(target_project_id, "target_project_id")
        changed_by = _require_nonempty(changed_by, "changed_by")
        change_reason = _require_nonempty(change_reason, "change_reason")
        if source_project_id == target_project_id:
            raise ProjectLifecycleError("A membership move requires different source and target projects")
        conn = self.db._get_conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            current = resolve_execution_membership(self.db, work_item_id)
            if current.project_id != source_project_id:
                raise ProjectLifecycleError(
                    f"Work item {work_item_id} belongs to {current.project_id}, not {source_project_id}"
                )
            self.db.link_project_work_item(
                source_project_id,
                work_item_id,
                changed_by,
                change_reason,
                id=current.id,
                status="removed",
                membership_order=current.membership_order,
                source=current.source,
                commit=False,
            )
            self.db.link_project_work_item(
                target_project_id,
                work_item_id,
                changed_by,
                change_reason,
                membership_order=membership_order,
                source="gt projects move-item",
                commit=False,
            )
            result = resolve_execution_membership(self.db, work_item_id).to_dict()
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise

    @staticmethod
    def dependency_kind_registry() -> dict[str, Any]:
        """Return the versioned governed dependency-kind registry."""
        return {
            "version": PROJECT_DEPENDENCY_KIND_REGISTRY_VERSION,
            "kinds": PROJECT_DEPENDENCY_KIND_REGISTRY,
        }

    @staticmethod
    def _canonical_dependency_record(record: dict[str, Any]) -> dict[str, Any]:
        hidden_compatibility_fields = {
            "from_project_id",
            "to_project_id",
            "dependency_type",
            "blocking_status",
        }
        return {key: value for key, value in record.items() if key not in hidden_compatibility_fields}

    @staticmethod
    def _dependency_semantic_key(record: dict[str, Any]) -> tuple[str, ...]:
        return (
            str(record.get("dependent_project_id") or ""),
            str(record.get("prerequisite_project_id") or ""),
            str(record.get("dependency_kind") or ""),
            str(record.get("required_prerequisite_state") or ""),
            str(record.get("affected_gate") or ""),
        )

    def _dependency_validation_errors(self, records: list[dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        active_records = [record for record in records if record.get("status") == "active"]
        semantic_keys: dict[tuple[str, ...], str] = {}
        adjacency: dict[str, set[str]] = {}

        for record in active_records:
            dependency_id = str(record.get("id") or "<missing-id>")
            dependent = str(record.get("dependent_project_id") or "")
            prerequisite = str(record.get("prerequisite_project_id") or "")
            kind = str(record.get("dependency_kind") or "")
            required_state = str(record.get("required_prerequisite_state") or "")
            affected_gate = str(record.get("affected_gate") or "")
            provenance = str(record.get("provenance") or "").strip()
            rationale = str(record.get("rationale") or "").strip()

            if not dependent or not prerequisite:
                errors.append(f"{dependency_id}: dependency endpoint is missing")
                continue
            if dependent == prerequisite:
                errors.append(f"{dependency_id}: self-dependency is prohibited")

            dependent_project = self.db.get_project(dependent)
            prerequisite_project = self.db.get_project(prerequisite)
            if dependent_project is None or prerequisite_project is None:
                missing = dependent if dependent_project is None else prerequisite
                errors.append(f"{dependency_id}: unknown-endpoint {missing}")

            definition = PROJECT_DEPENDENCY_KIND_REGISTRY.get(kind)
            if definition is None:
                errors.append(f"{dependency_id}: unknown dependency kind {kind!r}")
            else:
                if required_state not in definition["supported_required_states"]:
                    errors.append(f"{dependency_id}: unknown required state {required_state!r}")
                if affected_gate not in definition["supported_affected_gates"]:
                    errors.append(f"{dependency_id}: unsupported affected gate {affected_gate!r}")
                dependent_status = str((dependent_project or {}).get("status") or "").lower()
                if dependent_status in PROJECT_TERMINAL_STATUSES:
                    errors.append(f"{dependency_id}: retired-endpoint {dependent}")
                prerequisite_status = str((prerequisite_project or {}).get("status") or "").lower()
                satisfying_states = tuple(definition["satisfying_states"].get(required_state, ()))
                if prerequisite_status in PROJECT_TERMINAL_STATUSES and prerequisite_status not in satisfying_states:
                    errors.append(f"{dependency_id}: retired-endpoint {prerequisite}")
            if not rationale:
                errors.append(f"{dependency_id}: rationale is required")
            if not provenance:
                errors.append(f"{dependency_id}: provenance is required")

            semantic_key = self._dependency_semantic_key(record)
            prior_id = semantic_keys.get(semantic_key)
            if prior_id is not None:
                errors.append(f"{dependency_id}: duplicate-active-edge of {prior_id}")
            else:
                semantic_keys[semantic_key] = dependency_id
            adjacency.setdefault(dependent, set()).add(prerequisite)
            adjacency.setdefault(prerequisite, set())

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(project_id: str) -> bool:
            if project_id in visiting:
                return True
            if project_id in visited:
                return False
            visiting.add(project_id)
            if any(visit(prerequisite) for prerequisite in adjacency.get(project_id, ())):
                return True
            visiting.remove(project_id)
            visited.add(project_id)
            return False

        if any(visit(project_id) for project_id in tuple(adjacency) if project_id not in visited):
            errors.append("cycle detected across active project dependencies")
        return sorted(set(errors))

    def _require_valid_dependency_graph(self, records: list[dict[str, Any]]) -> None:
        errors = self._dependency_validation_errors(records)
        if errors:
            raise ProjectLifecycleError("Project dependency validation failed: " + "; ".join(errors))

    def _dependency_readiness(self, record: dict[str, Any]) -> dict[str, Any]:
        prerequisite_id = str(record["prerequisite_project_id"])
        prerequisite = self.db.get_project(prerequisite_id)
        current_state = str((prerequisite or {}).get("status") or "missing")
        required_state = str(record["required_prerequisite_state"])
        definition = PROJECT_DEPENDENCY_KIND_REGISTRY.get(str(record["dependency_kind"]))
        satisfying_states = (
            tuple(definition["satisfying_states"].get(required_state, ())) if definition is not None else ()
        )
        satisfied = current_state in satisfying_states
        affected_gate = str(record["affected_gate"])
        dependency_id = str(record["id"])
        return {
            "dependency_id": dependency_id,
            "dependent_project_id": record["dependent_project_id"],
            "prerequisite_project_id": prerequisite_id,
            "current_prerequisite_state": current_state,
            "required_prerequisite_state": required_state,
            "satisfying_states": list(satisfying_states),
            "satisfied": satisfied,
            "affected_gate": affected_gate,
            "blocked_gate": None if satisfied else affected_gate,
            "provenance": record["provenance"],
            "recovery_route": (
                f"Advance {prerequisite_id} to {required_state}, or retire {dependency_id} with "
                f"`gt projects dependencies retire {dependency_id} --change-reason <reason>`."
            ),
            "grants_implementation_authority": False,
        }

    def project_dependency_gate_readiness(self, project_id: str, gate: str) -> dict[str, Any]:
        """Explain whether one project's declared dependency gate is ready."""
        normalized_project_id = _require_nonempty(project_id, "project_id")
        normalized_gate = _require_nonempty(gate, "gate")
        if self.db.get_project(normalized_project_id) is None:
            raise ProjectLifecycleError(f"Project not found: {normalized_project_id}")
        supported_gates = {
            supported_gate
            for definition in PROJECT_DEPENDENCY_KIND_REGISTRY.values()
            for supported_gate in definition["supported_affected_gates"]
        }
        if normalized_gate not in supported_gates:
            raise ProjectLifecycleError(f"Unsupported project dependency gate: {normalized_gate}")

        dependencies = self.list_project_dependencies(
            normalized_project_id,
            dependent_project_id=normalized_project_id,
        )
        readiness = [
            dependency["readiness"]
            for dependency in dependencies
            if dependency["affected_gate"] == normalized_gate and dependency.get("readiness") is not None
        ]
        blockers = [row for row in readiness if not row["satisfied"]]
        return {
            "project_id": normalized_project_id,
            "gate": normalized_gate,
            "ready": not blockers,
            "dependency_count": len(readiness),
            "blocking_dependency_ids": [row["dependency_id"] for row in blockers],
            "readiness": readiness,
        }

    def _require_project_dependency_gate_ready(self, project_id: str, gate: str) -> None:
        result = self.project_dependency_gate_readiness(project_id, gate)
        if result["ready"]:
            return
        dependency_ids = ", ".join(result["blocking_dependency_ids"])
        raise ProjectLifecycleError(
            f"Project {result['project_id']} {result['gate']} gate is blocked by unsatisfied "
            f"project dependency edge(s): {dependency_ids}"
        )

    def show_project_dependency(self, dependency_id: str) -> dict[str, Any]:
        record = self.db.get_project_dependency(_require_nonempty(dependency_id, "dependency_id"))
        if record is None:
            raise ProjectLifecycleError(f"Project dependency not found: {dependency_id}")
        canonical = self._canonical_dependency_record(record)
        canonical["readiness"] = self._dependency_readiness(canonical) if canonical.get("status") == "active" else None
        return canonical

    def list_project_dependencies(
        self,
        project_id: str | None = None,
        *,
        dependent_project_id: str | None = None,
        prerequisite_project_id: str | None = None,
        include_inactive: bool = False,
    ) -> list[dict[str, Any]]:
        records = self.db.list_project_dependencies(project_id, include_inactive=include_inactive)
        canonical_records: list[dict[str, Any]] = []
        for raw_record in records:
            record = self._canonical_dependency_record(raw_record)
            if dependent_project_id and record.get("dependent_project_id") != dependent_project_id:
                continue
            if prerequisite_project_id and record.get("prerequisite_project_id") != prerequisite_project_id:
                continue
            record["readiness"] = self._dependency_readiness(record) if record.get("status") == "active" else None
            canonical_records.append(record)
        return canonical_records

    def validate_project_dependencies(self, project_id: str | None = None) -> dict[str, Any]:
        records = self.db.list_project_dependencies(None, include_inactive=True)
        errors = self._dependency_validation_errors(records)
        active = [record for record in records if record.get("status") == "active"]
        if project_id is not None:
            active = [
                record
                for record in active
                if project_id in {record.get("dependent_project_id"), record.get("prerequisite_project_id")}
            ]
        readiness = [self._dependency_readiness(self._canonical_dependency_record(record)) for record in active]
        return {
            "valid": not errors,
            "errors": errors,
            "active_dependency_count": len(active),
            "registry": self.dependency_kind_registry(),
            "readiness": readiness,
        }

    def add_project_dependency(
        self,
        dependent_project_id: str,
        prerequisite_project_id: str,
        *,
        dependency_kind: str = "requires_project_state",
        required_prerequisite_state: str,
        affected_gate: str,
        rationale: str,
        provenance: str,
        related_work_item_id: str | None = None,
        dependency_id: str | None = None,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
    ) -> dict[str, Any]:
        dependent = _require_nonempty(dependent_project_id, "dependent_project_id")
        prerequisite = _require_nonempty(prerequisite_project_id, "prerequisite_project_id")
        candidate = {
            "id": dependency_id or "<pending>",
            "dependent_project_id": dependent,
            "prerequisite_project_id": prerequisite,
            "dependency_kind": _require_nonempty(dependency_kind, "dependency_kind"),
            "required_prerequisite_state": _require_nonempty(
                required_prerequisite_state, "required_prerequisite_state"
            ),
            "affected_gate": _require_nonempty(affected_gate, "affected_gate"),
            "rationale": _require_nonempty(rationale, "rationale"),
            "provenance": _require_nonempty(provenance, "provenance"),
            "status": "active",
        }
        current_records = self.db.list_project_dependencies(None, include_inactive=True)
        candidate_key = self._dependency_semantic_key(candidate)
        for current in current_records:
            if self._dependency_semantic_key(current) != candidate_key:
                continue
            if current.get("status") == "active":
                raise ProjectLifecycleError(f"duplicate-active-edge: {current['id']}")
            raise ProjectLifecycleError(
                f"Dependency {current['id']} is inactive; use `gt projects dependencies recover`"
            )
        self._require_valid_dependency_graph([*current_records, candidate])

        conn = self.db._get_conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            transaction_records = self.db.list_project_dependencies(None, include_inactive=True)
            for current in transaction_records:
                if self._dependency_semantic_key(current) != candidate_key:
                    continue
                if current.get("status") == "active":
                    raise ProjectLifecycleError(f"duplicate-active-edge: {current['id']}")
                raise ProjectLifecycleError(
                    f"Dependency {current['id']} is inactive; use `gt projects dependencies recover`"
                )
            self._require_valid_dependency_graph([*transaction_records, candidate])
            dependency = self.db.add_project_dependency(
                dependent,
                prerequisite,
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                dependency_type="depends_on",
                rationale=candidate["rationale"],
                blocking_status=candidate["required_prerequisite_state"],
                related_work_item_id=related_work_item_id,
                status="active",
                id=dependency_id,
                dependent_project_id=dependent,
                prerequisite_project_id=prerequisite,
                dependency_kind=candidate["dependency_kind"],
                required_prerequisite_state=candidate["required_prerequisite_state"],
                affected_gate=candidate["affected_gate"],
                provenance=candidate["provenance"],
                registry_version=PROJECT_DEPENDENCY_KIND_REGISTRY_VERSION,
                commit=False,
            )
            if dependency is None:
                raise ProjectLifecycleError("Project dependency insert did not return a current record")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.show_project_dependency(str(dependency["id"]))

    def retire_project_dependency(
        self,
        dependency_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
    ) -> dict[str, Any]:
        current = self.db.get_project_dependency(_require_nonempty(dependency_id, "dependency_id"))
        if current is None:
            raise ProjectLifecycleError(f"Project dependency not found: {dependency_id}")
        if current.get("status") != "active":
            raise ProjectLifecycleError(f"invalid-transition: dependency {dependency_id} is not active")
        return self._append_dependency_lifecycle_version(
            current,
            status="retired",
            changed_by=changed_by,
            change_reason=change_reason,
        )

    def recover_project_dependency(
        self,
        dependency_id: str,
        *,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
    ) -> dict[str, Any]:
        current = self.db.get_project_dependency(_require_nonempty(dependency_id, "dependency_id"))
        if current is None:
            raise ProjectLifecycleError(f"Project dependency not found: {dependency_id}")
        if current.get("status") != "retired":
            raise ProjectLifecycleError(f"invalid-transition: dependency {dependency_id} is not retired")
        candidate = {**current, "status": "active"}
        other_records = [
            record
            for record in self.db.list_project_dependencies(None, include_inactive=True)
            if record["id"] != dependency_id
        ]
        self._require_valid_dependency_graph([*other_records, candidate])
        return self._append_dependency_lifecycle_version(
            current,
            status="active",
            changed_by=changed_by,
            change_reason=change_reason,
        )

    def _append_dependency_lifecycle_version(
        self,
        current: dict[str, Any],
        *,
        status: str,
        changed_by: str,
        change_reason: str,
    ) -> dict[str, Any]:
        conn = self.db._get_conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            transaction_current = self.db.get_project_dependency(str(current["id"]))
            if transaction_current is None:
                raise ProjectLifecycleError(f"Project dependency not found: {current['id']}")
            if transaction_current.get("version") != current.get("version") or transaction_current.get(
                "status"
            ) != current.get("status"):
                raise ProjectLifecycleError(
                    f"Project dependency {current['id']} changed during lifecycle validation; retry"
                )
            if status == "active":
                other_records = [
                    record
                    for record in self.db.list_project_dependencies(None, include_inactive=True)
                    if record["id"] != current["id"]
                ]
                self._require_valid_dependency_graph([*other_records, {**transaction_current, "status": "active"}])
            dependency = self.db.add_project_dependency(
                str(transaction_current["dependent_project_id"]),
                str(transaction_current["prerequisite_project_id"]),
                _require_nonempty(changed_by, "changed_by"),
                _require_nonempty(change_reason, "change_reason"),
                dependency_type="depends_on",
                rationale=transaction_current.get("rationale"),
                blocking_status=str(transaction_current["required_prerequisite_state"]),
                related_work_item_id=transaction_current.get("related_work_item_id"),
                status=status,
                id=str(transaction_current["id"]),
                dependent_project_id=str(transaction_current["dependent_project_id"]),
                prerequisite_project_id=str(transaction_current["prerequisite_project_id"]),
                dependency_kind=str(transaction_current["dependency_kind"]),
                required_prerequisite_state=str(transaction_current["required_prerequisite_state"]),
                affected_gate=str(transaction_current["affected_gate"]),
                provenance=str(transaction_current["provenance"]),
                registry_version=PROJECT_DEPENDENCY_KIND_REGISTRY_VERSION,
                commit=False,
            )
            if dependency is None:
                raise ProjectLifecycleError("Dependency lifecycle append did not return a current record")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return self.show_project_dependency(str(current["id"]))

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
        normalized_changed_by = _require_nonempty(changed_by, "changed_by")
        normalized_change_reason = _require_nonempty(change_reason, "change_reason")

        def _link() -> dict[str, Any] | None:
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
            active_count = (
                self.db._get_conn()
                .execute(
                    "SELECT COUNT(*) FROM current_project_work_item_memberships "
                    "WHERE work_item_id=? AND status='active'",
                    (normalized_work_item_id,),
                )
                .fetchone()[0]
            )
            if active_count <= 1:
                raise ProjectLifecycleError("A work item must retain one parent project; use gt projects move-item")
            try:
                return self.db.link_project_work_item(
                    normalized_project_id,
                    normalized_work_item_id,
                    normalized_changed_by,
                    normalized_change_reason,
                    id=current["membership_id"],
                    membership_role="member",
                    membership_order=current.get("membership_order"),
                    status=normalized_status,
                    source=current.get("membership_source"),
                    commit=False,
                )
            except ValueError as exc:
                raise ProjectLifecycleError(str(exc)) from exc

        return self._append_membership(
            project_id=normalized_project_id,
            changed_by=normalized_changed_by,
            change_reason=normalized_change_reason,
            link=_link,
            missing_message="Project membership removal did not return a current membership",
        )

    def retire_project_work_item(
        self,
        project_id: str,
        work_item_id: str,
        *,
        project_root: Path,
        changed_by: str = PROJECTS_CHANGED_BY,
        change_reason: str,
        status: str = "retired",
    ) -> dict[str, Any]:
        """Append a governed non-active membership version for one work item.

        Unlike ``remove_project_item()``, this lifecycle transition is governed
        by explicit owner approval evidence. The cited packet must resolve
        inside ``project_root`` and bind to this exact project, work item,
        lifecycle action, and requested non-active status.
        """
        normalized_status = str(status or "").strip()
        if normalized_status.casefold() in _RETIRE_ITEM_DISALLOWED_STATUSES:
            raise ProjectLifecycleError(
                f"retire-item requires a non-active lifecycle status distinct from 'removed'; got {status!r}."
            )
        normalized_project_id = _require_nonempty(project_id, "project_id")
        normalized_work_item_id = _require_nonempty(work_item_id, "work_item_id")
        normalized_change_reason = _require_nonempty(change_reason, "change_reason")

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
                f"No active membership to retire for {normalized_work_item_id} in {normalized_project_id}"
            )
        normalized_changed_by = _require_nonempty(changed_by, "changed_by")

        def _link() -> dict[str, Any] | None:
            try:
                return self.db.link_project_work_item(
                    normalized_project_id,
                    normalized_work_item_id,
                    normalized_changed_by,
                    normalized_change_reason,
                    membership_role="member",
                    membership_order=current.get("membership_order"),
                    status=normalized_status,
                    source=current.get("membership_source"),
                    commit=False,
                )
            except ValueError as exc:
                raise ProjectLifecycleError(str(exc)) from exc

        return self._append_membership(
            project_id=normalized_project_id,
            changed_by=normalized_changed_by,
            change_reason=normalized_change_reason,
            link=_link,
            missing_message="Project membership retirement did not return a current membership",
        )

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
        conn = self.db._get_conn()
        try:
            conn.execute("BEGIN IMMEDIATE")
            transaction_memberships = self.db.list_project_work_items(normalized_project_id)
            transaction_by_work_item = {item["work_item_id"]: item for item in transaction_memberships}
            if set(transaction_by_work_item) != current_ids:
                raise ProjectLifecycleError(
                    "Project membership changed during reorder validation; retry with the exact active set"
                )
            for work_item_id, current in current_by_work_item.items():
                transaction_current = transaction_by_work_item[work_item_id]
                if (
                    transaction_current.get("membership_id") != current.get("membership_id")
                    or transaction_current.get("membership_version") != current.get("membership_version")
                    or transaction_current.get("membership_status") != current.get("membership_status")
                ):
                    raise ProjectLifecycleError(
                        "Project membership changed during reorder validation; retry with the exact active set"
                    )
            for offset, work_item_id in enumerate(ordered_ids):
                current = transaction_by_work_item[work_item_id]
                membership = self.db.link_project_work_item(
                    normalized_project_id,
                    work_item_id,
                    _require_nonempty(changed_by, "changed_by"),
                    _require_nonempty(change_reason, "change_reason"),
                    membership_role="member",
                    membership_order=start_at + offset,
                    status=current.get("membership_status") or "active",
                    source=current.get("membership_source"),
                    commit=False,
                )
                if membership is None:
                    raise ProjectLifecycleError(f"Reorder did not return membership for {work_item_id}")
                reordered.append(membership)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
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
        # WI-7657: no keep-open election can exist any more, so this is False.
        #
        # The election was never stored directly. It was INFERRED from
        # authorization state: a project was "kept open" when at least one of
        # its authorizations was completed and none remained active, which is
        # what completing an authorization with retire_project=False produced.
        # Both the authorization records and the method that produced that
        # shape are gone, so the inference has no inputs. Returning False is
        # the honest answer rather than a guess: with no way to elect keep-open,
        # no project has elected it.
        _require_nonempty(project_id, "project_id")
        return False

    def member_completion_status(self, project_id: str, *, project_root: Path | None = None) -> dict[str, Any]:
        """Return the v6 member-WI automatic-retirement readiness record.

        ``GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`` v6 retires an
        active project automatically only when it has active member WIs, every
        active member WI has a terminal ``resolution_status``, no active
        ``plan_incomplete`` guard exists, no caller has taken the keep-open
        election, and every closure dependency is satisfied. ``project_root``
        remains an ignored compatibility argument for existing callers.
        """
        _ = project_root
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
        closure_dependency_gate = self.project_dependency_gate_readiness(normalized_project_id, "closure")
        completion_ready = (
            bool(member_ids)
            and not nonterminal_ids
            and not guard_refs
            and not keep_open_elected
            and closure_dependency_gate["ready"]
        )
        exclusion_reasons: list[str] = []
        if not member_ids:
            exclusion_reasons.append("zero_active_members")
        if nonterminal_ids:
            exclusion_reasons.append("nonterminal_member_work_items")
        if guard_refs:
            exclusion_reasons.append("plan_incomplete_guard")
        if keep_open_elected:
            exclusion_reasons.append("keep_open_election")
        if not closure_dependency_gate["ready"]:
            exclusion_reasons.append("unsatisfied_project_dependencies")

        return {
            "project_id": normalized_project_id,
            "active_member_work_item_ids": member_ids,
            "terminal_work_item_ids": terminal_ids,
            "nonterminal_work_item_ids": nonterminal_ids,
            "nonterminal_work_item_statuses": nonterminal_statuses,
            "completion_guarded": bool(guard_refs),
            "completion_guard_refs": guard_refs,
            "keep_open_elected": keep_open_elected,
            "closure_dependency_gate": closure_dependency_gate,
            "completion_ready": completion_ready,
            "exclusion_reasons": exclusion_reasons,
        }

    def member_completion_ready(self, project_id: str, *, project_root: Path | None = None) -> bool:
        """Return true when a project satisfies the v6 member-WI criterion."""
        return bool(self.member_completion_status(project_id, project_root=project_root)["completion_ready"])

    def _completion_guards_by_project(
        self,
        artifact_types: tuple[str, ...] = _COMPLETION_GUARD_ARTIFACT_TYPES,
    ) -> dict[str, list[dict[str, Any]]]:
        """Return active ``plan_incomplete`` completion guards keyed by project."""
        if not artifact_types:
            return {}
        rows = (
            self.db._get_conn()
            .execute(
                "SELECT id, project_id, artifact_type, artifact_ref, relationship, notes "
                "FROM current_project_artifact_links "
                "WHERE status = 'active' "
                "AND relationship = ? "
                f"AND artifact_type IN ({', '.join('?' for _ in artifact_types)}) "
                "ORDER BY project_id, artifact_type, artifact_ref",
                (_COMPLETION_GUARD_RELATIONSHIP, *artifact_types),
            )
            .fetchall()
        )
        guards: dict[str, list[dict[str, Any]]] = {}
        for link_id, project_id, artifact_type, artifact_ref, relationship, notes in rows:
            if not project_id:
                continue
            guards.setdefault(str(project_id), []).append(
                {
                    "id": str(link_id or ""),
                    "project_id": str(project_id),
                    "artifact_type": str(artifact_type or ""),
                    "artifact_ref": str(artifact_ref or ""),
                    "relationship": str(relationship or ""),
                    "notes": notes,
                }
            )
        return guards

    def _project_completion_guard_refs(
        self,
        project_id: str,
        artifact_types: tuple[str, ...] = _COMPLETION_GUARD_ARTIFACT_TYPES,
    ) -> list[dict[str, Any]]:
        return self._completion_guards_by_project(artifact_types).get(project_id, [])

    def _project_completion_blocker_refs(self, project_id: str) -> list[dict[str, Any]]:
        return self._project_completion_guard_refs(project_id, (_COMPLETION_BLOCKING_ARTIFACT_TYPE,))

    def _deactivate_completion_guard_refs(
        self,
        guard_refs: list[dict[str, Any]],
        *,
        changed_by: str,
        change_reason: str,
    ) -> list[dict[str, Any]]:
        deactivated: list[dict[str, Any]] = []
        for ref in guard_refs:
            link = self.db.add_project_artifact_link(
                str(ref["project_id"]),
                str(ref["artifact_type"]),
                str(ref["artifact_ref"]),
                changed_by,
                change_reason,
                relationship=str(ref["relationship"]),
                status="inactive",
                notes=ref.get("notes"),
                id=str(ref.get("id") or "") or None,
            )
            if link is not None:
                deactivated.append(link)
        return deactivated

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
