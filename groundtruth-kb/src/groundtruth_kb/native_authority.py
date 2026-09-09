"""Typed native knowledge and work-planning services.

The service owns PostgreSQL connections. Clients send domain operations, never
SQL, table names, storage paths, or database credentials. A domain mutation and
its resulting current-state/history changes commit together.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Annotated, Any, Literal
from uuid import uuid4

from psycopg import sql
from pydantic import BaseModel, ConfigDict, Field

from groundtruth_kb.postgres_kernel import (
    TABLE_SPECS,
    PostgresKernel,
    PostgresKernelError,
    PostgresTransaction,
    dependency_shape,
    validate_project_dependencies,
    validate_work_item_dependencies,
)

Identifier = Annotated[str, Field(min_length=1, max_length=256, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]
Text = Annotated[str, Field(min_length=1)]
Version = Annotated[int, Field(ge=0, lt=2_147_483_647)]
Scope = Literal["gtkb_platform", "agent_red_application"]


class Request(BaseModel):
    """Reject unknown fields and coercion at the domain boundary."""

    model_config = ConfigDict(extra="forbid", strict=True)


class Mutation(Request):
    expected_version: Version
    actor: Text
    reason: Text


class SpecFields(Request):
    title: Text | None = None
    description: str | None = None
    status: Text | None = None
    type: Text | None = None
    priority: str | None = None
    scope: str | None = None
    section: str | None = None
    handle: str | None = None
    tags: list[str] | None = None
    assertions: list[dict[str, Any]] | None = None
    authority: str | None = None
    provisional_until: Identifier | None = None
    constraints: dict[str, Any] | list[Any] | None = None
    affected_by: list[Identifier] | None = None
    testability: Literal["automatable", "observable", "structural", "untestable"] | None = None
    source_paths: list[str] | None = None
    parent: Identifier | None = None
    application_scope: Scope | None = None


class SpecMutation(Mutation):
    fields: SpecFields


class TestFields(Request):
    title: Text | None = None
    description: str | None = None
    test_type: Text | None = None
    spec_id: Identifier | None = None
    test_file: str | None = None
    test_class: str | None = None
    test_function: str | None = None
    expected_outcome: Text | None = None
    application_scope: Scope | None = None


class TestMutation(Mutation):
    fields: TestFields


class TestPlanFields(Request):
    title: Text | None = None
    description: str | None = None
    status: Text | None = None


class TestPlanMutation(Mutation):
    fields: TestPlanFields


class TestPhaseFields(Request):
    plan_id: Identifier | None = None
    phase_order: int | None = None
    title: Text | None = None
    description: str | None = None
    gate_criteria: Text | None = None
    test_ids: list[Identifier] | None = None


class TestPhaseMutation(Mutation):
    fields: TestPhaseFields


class ProjectFields(Request):
    name: Text | None = None
    parent_project_id: Identifier | None = None
    rank: int | None = None
    purpose: str | None = None
    target_outcome: str | None = None
    scope_note: str | None = None
    start_date: str | None = None
    target_date: str | None = None
    notes: str | None = None


class ProjectMutation(Mutation):
    kind: Literal["program", "project"] | None = None
    fields: ProjectFields


class DependencyFields(Request):
    dependent_project_id: Identifier | None = None
    prerequisite_project_id: Identifier | None = None
    dependency_kind: Literal["requires_project_state"] | None = None
    required_prerequisite_state: Literal["active", "verified", "retired", "cancelled"] | None = None
    affected_gate: Literal["readiness", "closure"] | None = None
    rationale: Text | None = None
    provenance: Text | None = None
    related_work_item_id: Identifier | None = None
    status: Literal["active", "retired"] | None = None


class DependencyMutation(Mutation):
    fields: DependencyFields


class WorkItemFields(Request):
    title: Text | None = None
    description: str | None = None
    component: Text | None = None
    origin: Text | None = None
    source_spec_id: Identifier | None = None
    source_test_id: Identifier | None = None
    priority: Literal["P0", "P1", "P2", "P3"] | None = None
    acceptance_summary: str | None = None
    implementation_order: int | None = None
    depends_on_work_items: list[Identifier] | None = None
    status_detail: str | None = None


class WorkItemMutation(Mutation):
    project_id: Identifier | None = None
    fields: WorkItemFields


class MembershipMove(Mutation):
    source_project_id: Identifier
    destination_project_id: Identifier
    membership_order: int | None = None


DOMAINS = {
    "specifications": "specifications",
    "tests": "tests",
    "projects": "projects",
    "work-items": "work_items",
    "test-plans": "test_plans",
    "test-phases": "test_plan_phases",
    "project-dependencies": "project_dependencies",
}
FILTERS = {
    "specifications": {"status", "type", "priority", "authority", "testability", "application_scope"},
    "tests": {"test_type", "spec_id", "application_scope"},
    "projects": {"kind", "status", "parent_project_id"},
    "work-items": {"resolution_status", "priority", "component", "source_spec_id"},
    "test-plans": {"status"},
    "test-phases": {"plan_id"},
    "project-dependencies": {"status", "dependent_project_id", "prerequisite_project_id", "affected_gate"},
}


def _error(code: str, message: str, **details: Any) -> None:
    raise PostgresKernelError(code, message, details=details)


def _required(tx: PostgresTransaction, table: str, record_id: str, *, lock: bool = False) -> dict[str, Any]:
    record = tx.get(table, {"id": record_id}, lock=lock)
    if record is None:
        _error("not_found", "Canonical record does not exist", domain=table, id=record_id)
    return record


def _related(tx: PostgresTransaction, table: str, **filters: Any) -> list[dict[str, Any]]:
    """Read all matching relationships without silently truncating a closure."""
    result: list[dict[str, Any]] = []
    after = None
    while True:
        page = tx.list(table, filters=filters, after=after, limit=1000)
        result.extend(page)
        if len(page) < 1000:
            return result
        after = page[-1]["id"]


def _current_parent(tx: PostgresTransaction, work_item_id: str) -> dict[str, Any]:
    memberships = _related(tx, "project_work_item_memberships", work_item_id=work_item_id, status="active")
    if len(memberships) != 1:
        _error("invalid_membership", "A work item requires exactly one current project", work_item_id=work_item_id)
    return memberships[0]


def _work_evidence(tx: PostgresTransaction, state: dict[str, Any]) -> None:
    """Recheck current executable evidence at intake and proposal publication."""
    for field, table in (("source_spec_id", "specifications"), ("source_test_id", "tests")):
        if not state.get(field):
            _error("work_evidence_required", "Implementation work requires a specification and executable test")
        evidence = _required(tx, table, state[field])
        if table == "specifications" and evidence["status"] in {"retired", "superseded"}:
            _error("inactive_evidence", "Work must refer to current evidence", id=evidence["id"])
        if table == "tests" and not evidence.get("test_file"):
            _error("executable_test_required", "The linked test must identify executable work")
    tx.cursor.execute(
        sql.SQL(
            "SELECT 1 FROM {}.test_plan_phases phase JOIN {}.test_plans plan ON plan.id=phase.plan_id "
            "WHERE phase.test_ids @> jsonb_build_array(%s::text) AND plan.status='active' LIMIT 1"
        ).format(sql.Identifier(tx.schema), sql.Identifier(tx.schema)),
        (state["source_test_id"],),
    )
    if tx.cursor.fetchone() is None:
        _error("test_phase_required", "The executable test must belong to an active test plan phase")


def _execution_project(tx: PostgresTransaction, project_id: str) -> dict[str, Any]:
    project = _required(tx, "projects", project_id, lock=True)
    if project["kind"] != "project":
        _error("program_cannot_contain_work", "Programs sequence projects and cannot contain work items")
    if project["status"] != "active":
        _error("project_closed", "Membership cannot change in a closed project")
    return project


def _project_commit(tx: PostgresTransaction, project_id: str) -> str | None:
    links = _related(
        tx,
        "project_artifact_links",
        project_id=project_id,
        artifact_type="git_commit",
        relationship="activation",
        status="active",
    )
    commit = links[0]["artifact_ref"] if len(links) == 1 else None
    return commit if isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", commit) else None


def _project_dependency_readiness(
    tx: PostgresTransaction, project_id: str, gate: str, *, lock: bool = False
) -> dict[str, Any]:
    if gate not in {"readiness", "closure"}:
        _error("invalid_dependency_gate", "Dependencies affect readiness or project closure")
    project = _required(tx, "projects", project_id, lock=lock)
    if project["kind"] != "project":
        _error("program_has_no_readiness", "Readiness applies to the execution projects sequenced by a program")
    results = []
    for record in _related(tx, "project_dependencies", dependent_project_id=project_id, status="active"):
        if dependency_shape(record) and record["affected_gate"] != gate:
            continue
        prerequisite = tx.get("projects", {"id": record["prerequisite_project_id"]}, lock=lock)
        current = prerequisite["status"] if prerequisite else None
        reason = None
        if not dependency_shape(record):
            reason = "invalid_dependency_contract"
        elif not prerequisite or prerequisite["kind"] != "project":
            reason = "invalid_prerequisite_project"
        elif current != record["required_prerequisite_state"]:
            reason = "prerequisite_state_not_reached"
        elif current == "verified" and not _project_commit(tx, prerequisite["id"]):
            reason = "prerequisite_commit_missing"
        results.append(
            {
                "dependency_id": record["id"],
                "prerequisite_project_id": record["prerequisite_project_id"],
                "required_state": record["required_prerequisite_state"],
                "current_state": current,
                "satisfied": reason is None,
                "reason": reason,
            }
        )
    return {
        "project_id": project_id,
        "gate": gate,
        "ready": all(row["satisfied"] for row in results),
        "dependencies": results,
    }


def _require_project_dependencies(
    tx: PostgresTransaction, project_id: str, gate: str = "readiness", *, lock: bool = False
) -> None:
    result = _project_dependency_readiness(tx, project_id, gate, lock=lock)
    if not result["ready"]:
        _error(
            "project_dependencies_unsatisfied",
            "Required predecessor results are not available; read project readiness",
            **result,
        )


def _write(
    tx: PostgresTransaction,
    table: str,
    record_id: str,
    fields: dict[str, Any],
    request: Mutation,
    *,
    defaults: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = tx.get(table, {"id": record_id}, lock=True)
    actual = current["version"] if current else 0
    if actual != request.expected_version:
        _error(
            "cas_conflict",
            "Read the current record before applying this change",
            expected=request.expected_version,
            actual=actual,
            id=record_id,
        )
    state = current or {column: None for column in TABLE_SPECS[table].columns}
    if not current:
        state.update(defaults or {})
    state.update(fields)
    state.update(
        id=record_id,
        version=actual,
        changed_by=request.actor,
        changed_at=datetime.now(UTC).isoformat(),
        change_reason=request.reason,
    )
    return tx.mutate(
        table=table,
        identity={"id": record_id},
        expected_version=actual,
        new_state=state,
        actor=request.actor,
        reason=request.reason,
    )["record"]


class AuthorityService:
    """Knowledge, planning, and task-context operations over native PostgreSQL."""

    def __init__(self, kernel: PostgresKernel) -> None:
        self.kernel = kernel

    def list_records(
        self,
        domain: str,
        *,
        filters: dict[str, Any] | None = None,
        after: str | None = None,
        limit: int = 200,
        search: str | None = None,
    ) -> dict[str, Any]:
        if domain not in DOMAINS or set(filters or {}) - FILTERS[domain]:
            _error("invalid_query", "Unknown domain or unsupported filter")
        with self.kernel.transaction(read_only=True) as tx:
            records = tx.list(DOMAINS[domain], filters=filters, after=after, limit=limit, search=search)
        return {"records": records, "next_after": records[-1]["id"] if len(records) == limit else None}

    def show(self, domain: str, record_id: str) -> dict[str, Any]:
        if domain not in DOMAINS:
            _error("invalid_query", "Unknown knowledge domain")
        with self.kernel.transaction(read_only=True) as tx:
            row = _required(tx, DOMAINS[domain], record_id)
            if domain == "projects":
                return {
                    "project": row,
                    "projects": _related(tx, "projects", parent_project_id=record_id),
                    "memberships": _related(tx, "project_work_item_memberships", project_id=record_id, status="active"),
                    "dependencies": _related(
                        tx, "project_dependencies", dependent_project_id=record_id, status="active"
                    ),
                    "artifact_links": _related(tx, "project_artifact_links", project_id=record_id, status="active"),
                }
            if domain == "work-items":
                return {"work_item": row, "membership": _current_parent(tx, record_id)}
            return row

    def amend_specification(self, record_id: str, request: SpecMutation) -> dict[str, Any]:
        fields = request.fields.model_dump(exclude_unset=True)
        with self.kernel.transaction() as tx:
            for reference in [
                fields.get("parent"),
                fields.get("provisional_until"),
                *(fields.get("affected_by") or []),
            ]:
                if reference:
                    _required(tx, "specifications", reference)
            # A retirement time is an observed event, not client-invented metadata.
            if fields.get("status") == "retired":
                fields["retired_at"] = datetime.now(UTC).isoformat()
            return _write(tx, "specifications", record_id, fields, request, defaults={"status": "specified"})

    def amend_test(self, record_id: str, request: TestMutation) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            return _write(tx, "tests", record_id, request.fields.model_dump(exclude_unset=True), request)

    def amend_test_plan(self, record_id: str, request: TestPlanMutation) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            return _write(
                tx,
                "test_plans",
                record_id,
                request.fields.model_dump(exclude_unset=True),
                request,
                defaults={"status": "active"},
            )

    def amend_test_phase(self, record_id: str, request: TestPhaseMutation) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            fields = request.fields.model_dump(exclude_unset=True)
            for test_id in fields.get("test_ids") or []:
                _required(tx, "tests", test_id)
            return _write(tx, "test_plan_phases", record_id, fields, request)

    def amend_project(self, record_id: str, request: ProjectMutation) -> dict[str, Any]:
        fields = request.fields.model_dump(exclude_unset=True)
        with self.kernel.transaction() as tx:
            current = tx.get("projects", {"id": record_id}, lock=True)
            kind = request.kind or (current["kind"] if current else "project")
            if current and (kind != current["kind"] or current["status"] != "active"):
                _error("project_structure_frozen", "Kind changes and closed project changes require reconciliation")
            parent = fields.get("parent_project_id", current["parent_project_id"] if current else None)
            if parent:
                program = _required(tx, "projects", parent, lock=True)
                if kind != "project" or program["kind"] != "program" or program["status"] != "active":
                    _error("invalid_program_parent", "An execution project may have one active program parent")
            fields["kind"] = kind
            defaults = {"status": "active", "authorization": None if kind == "program" else "authorized"}
            if record_id == "PROJECT-GTKB-NEW-WORK-INTAKE":
                defaults["authorization"] = "not authorized"
            return _write(tx, "projects", record_id, fields, request, defaults=defaults)

    def amend_dependency(self, record_id: str, request: DependencyMutation) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            current = tx.get("project_dependencies", {"id": record_id}, lock=True)
            actual = current["version"] if current else 0
            if actual != request.expected_version:
                _error(
                    "cas_conflict",
                    "Read the current dependency before changing it",
                    id=record_id,
                    expected=request.expected_version,
                    actual=actual,
                )
            fields = request.fields.model_dump(exclude_unset=True)
            candidate = {
                **(current or {"id": record_id, "status": "active", "dependency_kind": "requires_project_state"}),
                **fields,
            }
            if not current and fields.get("status", "active") != "active":
                _error("invalid_dependency_transition", "A new dependency starts active")
            for key in ("dependent_project_id", "prerequisite_project_id"):
                if not candidate.get(key):
                    _error("dependency_endpoint_required", "A dependency names both execution projects")
                _required(tx, "projects", candidate[key])
            # Publication and finalization hold this same project row before
            # reading its edges. New or changed prerequisites cannot cross an effect.
            affected = {candidate["dependent_project_id"]}
            if current:
                affected.add(current["dependent_project_id"])
            for project_id in sorted(affected):
                project = _required(tx, "projects", project_id, lock=True)
                if project["kind"] != "project":
                    _error("invalid_dependency_endpoint", "Dependencies sequence execution projects")
                if candidate["status"] == "active" and project["status"] != "active":
                    _error("closed_dependent_project", "A closed project cannot acquire or change an active dependency")
            prerequisite = _required(tx, "projects", candidate["prerequisite_project_id"])
            if (
                candidate["status"] == "active"
                and prerequisite["status"] in {"retired", "cancelled", "verified"}
                and prerequisite["status"] != candidate.get("required_prerequisite_state")
            ):
                _error("unreachable_dependency", "The closed prerequisite cannot reach the requested state")
            if candidate.get("related_work_item_id"):
                _required(tx, "work_items", candidate["related_work_item_id"])
            graph = [row for row in _related(tx, "project_dependencies", status="active") if row["id"] != record_id]
            projects = {row["id"]: row for row in _related(tx, "projects")}
            validate_project_dependencies(graph + [candidate], projects)
            return _write(
                tx,
                "project_dependencies",
                record_id,
                fields,
                request,
                defaults={
                    "status": "active",
                    "dependency_kind": "requires_project_state",
                    "registry_version": 1,
                    "provenance": request.actor,
                    "blocking_status": "open",
                },
            )

    def project_readiness(self, project_id: str, gate: str = "readiness") -> dict[str, Any]:
        with self.kernel.transaction(read_only=True) as tx:
            return _project_dependency_readiness(tx, project_id, gate)

    def amend_work_item(self, record_id: str, request: WorkItemMutation) -> dict[str, Any]:
        fields = request.fields.model_dump(exclude_unset=True)
        with self.kernel.transaction() as tx:
            current = tx.get("work_items", {"id": record_id}, lock=True)
            if current:
                membership = _current_parent(tx, record_id)
                project = _execution_project(tx, membership["project_id"])
                if request.project_id and request.project_id != project["id"]:
                    _error("membership_move_required", "Use the atomic membership move operation")
                if current["resolution_status"] != "open":
                    _error("work_item_frozen", "Reviewed or closed work cannot be amended through ordinary intake")
            else:
                if not request.project_id:
                    _error("project_required", "New work requires an existing execution project")
                project = _execution_project(tx, request.project_id)
            state = {**(current or {}), **fields}
            _work_evidence(tx, state)
            self._check_dependencies(tx, record_id, state.get("depends_on_work_items") or [])
            row = _write(
                tx,
                "work_items",
                record_id,
                fields,
                request,
                defaults={"origin": "manual", "component": "gtkb", "resolution_status": "open", "stage": "created"},
            )
            if not current:
                _write(
                    tx,
                    "project_work_item_memberships",
                    f"PWM-{uuid4().hex}",
                    {
                        "project_id": project["id"],
                        "work_item_id": record_id,
                        "status": "active",
                        "membership_order": row.get("implementation_order"),
                        "source": "domain_service",
                    },
                    Mutation(expected_version=0, actor=request.actor, reason=request.reason),
                )
            return {"work_item": row, "membership": _current_parent(tx, record_id)}

    @staticmethod
    def _check_dependencies(tx: PostgresTransaction, record_id: str, dependencies: list[str]) -> None:
        tx.cursor.execute(
            sql.SQL("SELECT id,depends_on_work_items FROM {}.work_items WHERE id<>%s").format(
                sql.Identifier(tx.schema)
            ),
            (record_id,),
        )
        rows = [dict(row) for row in tx.cursor.fetchall()]
        validate_work_item_dependencies(rows + [{"id": record_id, "depends_on_work_items": dependencies}])

    def move_work_item(self, record_id: str, request: MembershipMove) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            row = _required(tx, "work_items", record_id, lock=True)
            if row["resolution_status"] != "open":
                _error("work_item_frozen", "Reviewed or closed membership requires reconciliation")
            current = _current_parent(tx, record_id)
            if current["project_id"] != request.source_project_id or current["version"] != request.expected_version:
                _error("cas_conflict", "Read the current membership before moving work")
            for project_id in sorted({request.source_project_id, request.destination_project_id}):
                _execution_project(tx, project_id)
            if request.source_project_id == request.destination_project_id:
                _error("invalid_membership", "A move requires two distinct projects")
            _write(tx, "project_work_item_memberships", current["id"], {"status": "removed"}, request)
            old_destination = _related(
                tx, "project_work_item_memberships", project_id=request.destination_project_id, work_item_id=record_id
            )
            destination = old_destination[0] if old_destination else None
            updated = _write(
                tx,
                "project_work_item_memberships",
                destination["id"] if destination else f"PWM-{uuid4().hex}",
                {
                    "project_id": request.destination_project_id,
                    "work_item_id": record_id,
                    "status": "active",
                    "membership_order": request.membership_order,
                    "source": "domain_service",
                },
                Mutation(
                    expected_version=destination["version"] if destination else 0,
                    actor=request.actor,
                    reason=request.reason,
                ),
            )
            return {"work_item_id": record_id, "membership": updated}

    def task_context(self, record_id: str, *, predecessor_readiness=None) -> dict[str, Any]:
        """Load linked current facts without another context's memory or state."""
        with self.kernel.transaction(read_only=True) as tx:
            work = _required(tx, "work_items", record_id)
            membership = _current_parent(tx, record_id)
            project = _required(tx, "projects", membership["project_id"])
            program = _required(tx, "projects", project["parent_project_id"]) if project["parent_project_id"] else None
            links = _related(tx, "project_artifact_links", project_id=project["id"], status="active")
            formal_ids = {link["artifact_ref"] for link in links if link["artifact_type"] == "spec"}
            formal_ids.update(work.get("related_spec_ids_at_creation") or [])
            if work.get("source_spec_id"):
                formal_ids.add(work["source_spec_id"])
            formals = [_required(tx, "specifications", key) for key in sorted(formal_ids)]
            stale = [formal["id"] for formal in formals if formal["status"] in {"retired", "superseded"}]
            if stale:
                _error(
                    "inactive_context_source", "Task links require reconciliation to current formal sources", ids=stale
                )
            return {
                "work_item": work,
                "membership": membership,
                "project": project,
                "program": program,
                "specifications": formals,
                "test": _required(tx, "tests", work["source_test_id"]) if work.get("source_test_id") else None,
                "predecessors": [_required(tx, "work_items", key) for key in work.get("depends_on_work_items") or []],
                "readiness": _project_dependency_readiness(tx, project["id"], "readiness"),
                **({"work_item_readiness": predecessor_readiness(tx, record_id)} if predecessor_readiness else {}),
                "project_dependencies": _related(
                    tx, "project_dependencies", dependent_project_id=project["id"], status="active"
                ),
            }
