"""Typed native knowledge and work-planning services.

The service owns PostgreSQL connections. Clients send domain operations, never
SQL, table names, storage paths, or database credentials. A domain mutation and
its resulting current-state/history changes commit together.
"""

from __future__ import annotations

import hashlib
import io
import os
import re
import subprocess
import tomllib
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Annotated, Any, Literal, NoReturn
from uuid import uuid4

from psycopg import sql
from pydantic import BaseModel, ConfigDict, Field, field_validator

from groundtruth_kb.isolation.registry_check import (
    ApplicationRegistryError,
    resolve_project_repository,
    validate_application_scope,
)
from groundtruth_kb.postgres_kernel import (
    TABLE_SPECS,
    PostgresKernel,
    PostgresKernelError,
    PostgresTransaction,
    canonical_json_bytes,
    dependency_shape,
    validate_project_dependencies,
    validate_work_item_dependencies,
)
from groundtruth_kb.project.sot_registry import registry_path_observations

Identifier = Annotated[str, Field(min_length=1, max_length=256, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]
# Imported obsolete project relationships carry historical identities that
# concatenated untruncated components; several exceed the ordinary length. The
# formal-link addresses keep the same lexical rule without that cap so every
# existing row can be read, retired status-only and read back. Request fields
# and every other domain keep the ordinary identifier.
FormalLinkIdentifier = Annotated[str, Field(min_length=1, pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")]
Text = Annotated[str, Field(min_length=1)]
Version = Annotated[int, Field(ge=0, lt=2_147_483_647)]
Scope = Annotated[str, Field(pattern=r"^(gtkb_platform|application:[A-Za-z][A-Za-z0-9_-]*)$")]


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
    status: Literal["active", "superseded", "retired"] = "active"
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
    # `true` asserts that the implementation is verified now (the service stamps the time; a client
    # timestamp is refused by this contract, as retired_at is); `null` clears the marker.
    implementation_verified_at: bool | None = None

    @field_validator("implementation_verified_at")
    @classmethod
    def _assertion_or_clear(cls, value: bool | None) -> bool | None:
        if value is False:
            raise ValueError("implementation_verified_at accepts true (assert now) or null (clear)")
        return value


class SpecMutation(Mutation):
    fields: SpecFields


class TermFields(Request):
    canonical_term: Text | None = None
    definition: Text | None = None
    authority_level: Literal["platform_core", "adopter_extension", "project_local"] | None = None
    scope: Text | None = None
    accepted_synonyms: list[Text] | None = None
    discouraged_synonyms: list[Text] | None = None
    linked_artifacts: list[Text] | None = None
    linked_services: list[Text] | None = None
    usage_examples: list[Text] | None = None
    forbidden_uses: list[Text] | None = None
    lifecycle_status: Literal["candidate", "active", "deprecated", "retired"] | None = None
    source_authority: Text | None = None


class TermMutation(Mutation):
    fields: TermFields


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


class HarnessFields(Request):
    harness_name: Text | None = None
    harness_type: Text | None = None
    status: Literal["registered", "active", "suspended", "retired"] | None = None
    invocation_surfaces: dict[str, Any] | None = None
    capabilities_ref: str | None = None


class HarnessMutation(Mutation):
    fields: HarnessFields


class ProjectFields(Request):
    name: Text | None = None
    repository_ref: Annotated[str, Field(pattern=r"^(platform|application:[A-Za-z][A-Za-z0-9_-]*)$")] | None = None
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


class ProjectAuthorizationChange(Mutation):
    authorization: Literal["authorized", "not authorized"]


class ProjectRetirement(Mutation):
    """Status-only retirement of one active program or execution project; nothing else can travel with it."""


class ProjectFormalLinkFields(Request):
    project_id: Identifier | None = None
    artifact_ref: Identifier | None = None
    status: Literal["active", "retired"] | None = None
    notes: str | None = None


class ProjectFormalLinkMutation(Mutation):
    fields: ProjectFormalLinkFields


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
    resolution_status: Literal["open", "verified", "retired"] | None = None
    # Existing storage column: exact historical Git evidence or an explicit inspected false-completion clear.
    completion_evidence: str | None = None


class WorkItemMutation(Mutation):
    project_id: Identifier | None = None
    fields: WorkItemFields


class WorkItemRetirement(Mutation):
    """Status-only retirement of one open work item; nothing else can travel with it."""


class MembershipMove(Mutation):
    source_project_id: Identifier
    destination_project_id: Identifier
    membership_order: int | None = None


DOMAINS = {
    "harnesses": "harnesses",
    "terms": "canonical_terms",
    "specifications": "specifications",
    "tests": "tests",
    "projects": "projects",
    "work-items": "work_items",
    "test-plans": "test_plans",
    "test-phases": "test_plan_phases",
    "project-dependencies": "project_dependencies",
    "project-formal-links": "project_artifact_links",
    # Historical reasoning records: readable, never amended through this service (SPEC-2098 v2).
    "deliberations": "deliberations",
}
FILTERS = {
    "harnesses": {"status"},
    "terms": {"scope", "authority_level", "lifecycle_status"},
    "specifications": {"status", "type", "priority", "authority", "testability", "application_scope", "scope"},
    "tests": {"test_type", "spec_id", "application_scope"},
    "projects": {"kind", "status", "parent_project_id", "repository_ref"},
    "work-items": {"resolution_status", "priority", "component", "source_spec_id"},
    "test-plans": {"status"},
    "test-phases": {"plan_id"},
    "project-dependencies": {"status", "dependent_project_id", "prerequisite_project_id", "affected_gate"},
    "project-formal-links": {"status", "project_id", "artifact_type"},
    "deliberations": {"source_type", "spec_id", "work_item_id"},
}


def _error(code: str, message: str, **details: Any) -> NoReturn:
    raise PostgresKernelError(code, message, details=details)


def _refuse_role_bearing_surfaces(record_id: str, surfaces: dict[str, Any]) -> None:
    """Refuse invocation surfaces that name a role or a placeholder outside the contract (c123; batch design WP2 2.1).

    Roles bind to contexts through the init line; a registration that carried one in a dispatch tag, a role key or a
    ``--skill`` argument let a launch argument stand in for the binding. Nothing is written when this refuses.
    """
    from groundtruth_kb.harness_invocation import PLACEHOLDERS, ROLE_FINDINGS, surface_findings

    findings = surface_findings(surfaces)
    if not findings:
        return
    listed = [{"code": finding.code, "path": finding.path, "value": finding.value} for finding in findings]
    if any(finding.code in ROLE_FINDINGS for finding in findings):
        _error(
            "harness_surface_names_role",
            "A harness registration names no role: roles bind to contexts through the init line, never through a "
            "dispatch tag, a role key, an init marker or a --skill argument",
            id=record_id,
            findings=listed,
        )
    _error(
        "unknown_invocation_placeholder",
        f"A harness invocation uses only the contract's placeholders: {', '.join(sorted(PLACEHOLDERS))}",
        id=record_id,
        findings=listed,
    )


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


def _membership_facts(tx: PostgresTransaction, work: dict[str, Any]) -> dict[str, Any]:
    """Recorded membership facts for a read.

    An open work item has exactly one active parent project; reading an open item with any other
    history is refused like every mutation, move and readiness check. Closed work keeps its recorded
    membership rows exactly as history (the migration preserves zero or several active memberships
    on the owner's decision), so a read returns those rows and ``membership`` only when exactly one is
    active. Nothing is repaired or invented on the read path.
    """
    memberships = _related(tx, "project_work_item_memberships", work_item_id=work["id"])
    active = [row for row in memberships if row["status"] == "active"]
    if work["resolution_status"] == "open":
        if len(active) != 1:
            _error("invalid_membership", "A work item requires exactly one current project", work_item_id=work["id"])
        return {"membership": active[0], "memberships": memberships}
    return {"membership": active[0] if len(active) == 1 else None, "memberships": memberships}


def _work_formal_roots(
    tx: PostgresTransaction, work: dict[str, Any], project_id: str, *, lock: bool = False
) -> dict[str, Any]:
    """Read canonical relationship inputs independently of supplementary citations."""
    work_sources = set(work.get("related_spec_ids_at_creation") or [])
    if work.get("source_spec_id"):
        work_sources.add(work["source_spec_id"])
    test_id = work.get("source_test_id")
    return {
        "work": sorted(work_sources),
        "test": {test_id: _required(tx, "tests", test_id, lock=lock)["spec_id"]} if test_id else {},
        "project": {
            link["id"]: link["artifact_ref"]
            for link in _related(tx, "project_artifact_links", project_id=project_id, status="active")
            if link["artifact_type"] == "spec"
        },
    }


def _work_formal_sources(
    tx: PostgresTransaction,
    work: dict[str, Any],
    project_id: str,
    *,
    additional_ids: list[str] | None = None,
    lock: bool = False,
) -> list[dict[str, Any]]:
    """Read the declared formal closure in the caller's domain transaction.

    This is the explicit relationship floor, not a claim of complete semantic
    applicability. Context loading and bridge effects use the same facts.
    Cyclic cross-references are visited once, without dropping their records.
    """
    roots = _work_formal_roots(tx, work, project_id, lock=lock)
    pending = (
        set(additional_ids or []) | set(roots["work"]) | set(roots["test"].values()) | set(roots["project"].values())
    )
    records: dict[str, dict[str, Any]] = {}
    while pending:
        for key in sorted(pending):
            record = tx.get("specifications", {"id": key}, lock=lock)
            if record is None:
                _error(
                    "not_found",
                    "A required formal source is missing; reconcile its canonical relationship",
                    domain="specifications",
                    id=key,
                    recovery_route=f"gt context work-item {work['id']}",
                )
            records[key] = record
        pending = {
            reference
            for record in records.values()
            for reference in [record.get("parent"), record.get("provisional_until"), *(record.get("affected_by") or [])]
            if reference and reference not in records
        }
    return [records[key] for key in sorted(records)]


def _test_phases(tx: PostgresTransaction, test_id: str) -> list[dict[str, Any]]:
    tx.cursor.execute(
        sql.SQL(
            "SELECT phase.id FROM {}.test_plan_phases phase JOIN {}.test_plans plan ON plan.id=phase.plan_id "
            "WHERE phase.test_ids @> jsonb_build_array(%s::text) AND plan.status='active' "
            "ORDER BY phase.plan_id,phase.phase_order,phase.id"
        ).format(sql.Identifier(tx.schema), sql.Identifier(tx.schema)),
        (test_id,),
    )
    return [_required(tx, "test_plan_phases", row["id"]) for row in tx.cursor.fetchall()]


def _work_evidence(tx: PostgresTransaction, state: dict[str, Any]) -> None:
    """Require current evidence at creation, link replacement and proposal publication."""
    for field, table in (("source_spec_id", "specifications"), ("source_test_id", "tests")):
        if not state.get(field):
            _error("work_evidence_required", "Implementation work requires a specification and executable test")
        evidence = _required(tx, table, state[field])
        if table == "specifications" and evidence["status"] in {"retired", "superseded"}:
            _error("inactive_evidence", "Work must refer to current evidence", id=evidence["id"])
        if table == "tests" and not evidence.get("test_file"):
            _error("executable_test_required", "The linked test must identify executable work")
    if not _test_phases(tx, state["source_test_id"]):
        _error("test_phase_required", "The executable test must belong to an active test plan phase")


def _verification_evidence(tx: PostgresTransaction, spec_id: str) -> list[str]:
    """Executable tests of one specification that sit in a phase of an active test plan.

    The `_work_evidence` rule mirrored for implementation verification (owner ruling D17, WI-7861):
    a test counts when its ``spec_id`` is this specification, it identifies executable work
    (``test_file``) and an active plan phase lists it.
    """
    return [
        test["id"]
        for test in _related(tx, "tests", spec_id=spec_id)
        if test.get("test_file") and _test_phases(tx, test["id"])
    ]


def _execution_project(tx: PostgresTransaction, project_id: str) -> dict[str, Any]:
    project = _required(tx, "projects", project_id, lock=True)
    if project["kind"] != "project":
        _error("program_cannot_contain_work", "Programs sequence projects and cannot contain work items")
    if project["status"] != "active":
        _error("project_closed", "Membership cannot change in a closed project")
    return project


def _open_dependants(tx: PostgresTransaction, work_item_id: str) -> list[str]:
    """Open work items whose ``depends_on_work_items`` names this one, in code-point id order.

    ``depends_on_work_items`` is the sole writable predecessor list (DCL-STANDING-BACKLOG-DB-SCHEMA-001);
    ``blocks_work_items`` is imported legacy data with no native writer, reader or derived view and is not
    consulted. Closed dependants (any resolution other than ``open``) never block, and a legacy non-array
    JSONB value simply does not match.
    """
    tx.cursor.execute(
        sql.SQL(
            "SELECT id FROM {}.work_items WHERE id<>%s AND resolution_status='open' "
            "AND depends_on_work_items @> jsonb_build_array(%s::text)"
        ).format(sql.Identifier(tx.schema)),
        (work_item_id, work_item_id),
    )
    return sorted(row["id"] for row in tx.cursor.fetchall())


def _active_attempts(
    tx: PostgresTransaction,
    *,
    work_item_id: str | None = None,
    project_id: str | None = None,
    reviewed_only: bool = False,
) -> list[str]:
    """Identifiers of the active bridge attempts on one work item or on one project, in code-point id order.

    The bridge's own predicate (``disposition='active'``). A VERIFIED member keeps its attempt active until
    the project commit, so an active attempt marks reviewed-but-uncommitted work as well as work in progress.
    Ordinary planning/membership mutations filter to reviewed heads, whose work remains frozen.
    """
    named = {
        column: value
        for column, value in (("work_item_id", work_item_id), ("project_id", project_id))
        if value is not None
    }
    if len(named) != 1:
        _error("invalid_query", "Active attempts are selected by exactly one work item or one project")
    ((column, value),) = named.items()
    tx.cursor.execute(
        sql.SQL("SELECT id FROM {}.bridge_attempts WHERE {}=%s AND disposition='active'").format(
            sql.Identifier(tx.schema), sql.Identifier(column)
        )
        + (sql.SQL(" AND head_status='VERIFIED'") if reviewed_only else sql.SQL("")),
        (value,),
    )
    return sorted(row["id"] for row in tx.cursor.fetchall())


def _open_members(tx: PostgresTransaction, project: dict[str, Any]) -> dict[str, list[str]]:
    """Members that keep a project or program open: open work with an active membership, active child projects.

    A closed member's active membership is its preserved current parent (GOV-WORK-ITEM-TERMINAL-STATE-001,
    GOV-STANDING-BACKLOG-001) and never blocks. A program has no memberships and an execution project has
    no children, so one of the two lists is empty by construction.
    """
    memberships = _related(tx, "project_work_item_memberships", project_id=project["id"], status="active")
    return {
        "work_item_ids": sorted(
            row["work_item_id"]
            for row in memberships
            if _required(tx, "work_items", row["work_item_id"])["resolution_status"] == "open"
        ),
        "project_ids": sorted(
            row["id"] for row in _related(tx, "projects", parent_project_id=project["id"], status="active")
        ),
    }


def _active_dependants(tx: PostgresTransaction, project_id: str) -> list[dict[str, Any]]:
    """Active dependencies of active projects that require this prerequisite to reach a state other than retired.

    The ``unreachable_dependency`` rule of amend_dependency seen from the prerequisite's side: a retired
    prerequisite can never reach ``active`` or ``verified``. A dependency that requires ``retired`` is met by
    the retirement, and a closed dependent project no longer waits.
    """
    return [
        row
        for row in _related(tx, "project_dependencies", prerequisite_project_id=project_id, status="active")
        if row["required_prerequisite_state"] != "retired"
        and _required(tx, "projects", row["dependent_project_id"])["status"] == "active"
    ]


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
    result = tx.mutate(
        table=table,
        identity={"id": record_id},
        expected_version=actual,
        new_state=state,
        actor=request.actor,
        reason=request.reason,
    )
    record = result.get("record")
    if not isinstance(record, dict):
        _error("mutation_readback_mismatch", "Native mutation did not return a current record")
    return record


def _historical_git(root: Path, *arguments: str) -> bytes:
    """Bounded, read-only Git evidence in the registered repository, without ambient Git redirection."""
    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "--literal-pathspecs", "-C", str(root), *arguments],
            env={key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")},
            capture_output=True,
            timeout=15,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise PostgresKernelError(
            "historical_git_unavailable", "The historical Git object could not be inspected"
        ) from error
    if result.returncode:
        if result.returncode == 1 and arguments[:2] == ("merge-base", "--is-ancestor"):
            _error(
                "historical_git_not_current",
                "The exact historical commit is not an ancestor of the registered repository's current HEAD",
            )
        _error(
            "historical_git_unavailable",
            "The historical Git object could not be inspected in its registered repository",
        )
    return result.stdout


def _historical_product_path(path: str, *, historical_skills: bool = False) -> bool:
    """Ignore coordination carriers and generated output when establishing a physical product change."""
    parts = PurePosixPath(path).parts
    if not parts or parts[0].casefold() in {"bridge", "memory", ".groundtruth"}:
        return False
    ignored = {
        ".git",
        ".gtkb-state",
        "harness-state",
        "scratchpad",
        ".worktrees",
        ".agent",
        ".antigravity",
        ".api-harness",
        ".claude",
        ".codex",
        ".cursor",
        ".goose",
    }
    if any(part.casefold() in ignored for part in parts):
        return False
    return not any(
        part.casefold() == ".agents"
        and not (historical_skills and index == 0 and len(parts) >= 3 and parts[1].casefold() == "skills")
        for index, part in enumerate(parts)
    )


def _confirm_historical_commit(project_root: Path | None, project: dict[str, Any], evidence: str) -> str:
    """Confirm physical Git facts; these checks do not prove completion of the work item's semantic scope.

    The caller's substantive inspected acceptance and remaining scope belong in the ordinary mutation reason/history.
    A commit citation or a changed product file alone is not proof that the complete intended behavior was delivered.
    """
    match = re.fullmatch(r"git:([0-9a-f]{40}(?:[0-9a-f]{24})?)", evidence)
    if match is None:
        _error("invalid_completion_evidence", "Historical completion requires git:<exact full lowercase commit ID>")
    if project_root is None:
        _error("repository_host_required", "Historical Git inspection requires the authority service's configured host")
    reference = project.get("repository_ref")
    if project["kind"] != "project" or reference is None:
        _error("project_repository_required", "Establish the historical work item's explicit execution repository")
    try:
        repository = resolve_project_repository(project_root, reference)
    except ApplicationRegistryError as error:
        raise PostgresKernelError("invalid_repository_ref", str(error)) from error
    commit = match.group(1)
    try:
        observed = (
            _historical_git(repository, "rev-parse", "--verify", "--end-of-options", commit + "^{commit}")
            .decode("ascii")
            .strip()
        )
        if observed != commit:
            _error("historical_commit_mismatch", "The inspected object is not the exact supplied commit")
        # Object survival after a rewrite is not activation. A legitimate forward change retains this ancestry.
        _historical_git(repository, "merge-base", "--is-ancestor", commit, "HEAD")
        parents = _historical_git(repository, "show", "-s", "--format=%P", commit).decode("ascii").split()
        # A merge's first-parent difference is what that merge introduced to its integration history.
        arguments = ("diff-tree", "--no-commit-id", "-r", "--name-only", "-z")
        changes = (
            _historical_git(repository, *arguments, parents[0], commit)
            if parents
            else _historical_git(repository, *arguments, "--root", commit)
        )
        changed_paths = changes.decode("utf-8").split("\0")
    except UnicodeError as error:
        raise PostgresKernelError(
            "historical_git_unavailable", "Historical Git evidence has an unreadable identity or path"
        ) from error
    product_change = any(path and _historical_product_path(path) for path in changed_paths)
    if not product_change and any(path.startswith(".agents/skills/") for path in changed_paths):
        # A real former source commit remains product evidence. Current generated
        # catalog bytes do not: inspect the exact commit's tracked declaration,
        # never a current compatibility alias or an assumed historical cutoff.
        declaration = "scripts/harness_projection/profiles.toml"
        if _historical_git(repository, "ls-tree", "-z", commit, "--", declaration):
            try:
                historical_profiles = tomllib.loads(
                    _historical_git(repository, "show", commit + ":" + declaration).decode("utf-8")
                )
            except (UnicodeError, tomllib.TOMLDecodeError) as error:
                raise PostgresKernelError(
                    "historical_git_unavailable", "The exact historical Skills source declaration is unreadable"
                ) from error
            declared_baseline = historical_profiles.get("baseline")
            authored_skills = (
                isinstance(declared_baseline, dict) and declared_baseline.get("skills_root") == ".agents/skills"
            )
            product_change = authored_skills and any(
                path and _historical_product_path(path, historical_skills=True) for path in changed_paths
            )
    if not product_change:
        _error(
            "historical_product_change_required",
            "The exact commit has no substantive changed product outside coordination carriers",
        )
    return "git:" + commit


_CONTEXT_SAD_SECTIONS = {
    "1.1": "Platform purpose",
    "1.2": "Intended outcomes and evidence",
    "1.3": "Architectural invariants",
    "1.4": "Component responsibilities",
    "1.5": "Correction and successor sequence",
    "2.1": "Current authority and historical rationale",
    "2.2": "Source roles and precedence",
    "2.3": "Component and source map",
    "2.4": "Project authorization and membership",
    "2.5": "Owner choices in current records",
    "3.1": "Architecture reference role",
    "3.2": "Planned context composition",
    "3.3": "Semantic closure review",
    "4.1": "Separate implementation and review contexts",
    "4.2": "Independent test selection",
    "4.3": "Verification and project finalization",
    "5.1": "Authored headers and routing",
    "5.2": "Twelve status lifecycle",
    "6.1": "Immutable native session binding",
    "6.2": "Transient activity and bounded operations",
    "6.3": "Ephemeral scratch space",
    "7.1": "Planned coordination responsibilities",
    "7.2": "Intended selection order",
    "7.3": "Exact artifact claims and planned recovery",
    "8.1": "Claimed target scope",
    "8.2": "Exact edits and encoding",
    "8.3": "Native CLI command families",
    "9.1": "Supported assertions",
    "9.2": "Distinct evidence levels",
    "9.3": "Release and document checks",
    "10.1": "Role neutral registration",
    "10.2": "Measured resource behavior",
    "11.1": "Migration history and source refresh",
    "11.2": "Defect status and required work",
}
_CONTEXT_SHARED_SECTIONS = {"2.1", "2.2", "3.1", "4.1", "5.1", "5.2", "6.1"}
_CONTEXT_ACTIVITY_SECTIONS = {
    "build": {"8.1", "8.2"},
    "test": {"4.2", "4.3", "9.1", "9.2"},
    "spec": {"2.1", "2.2", "8.2"},
    "deliberation": {"2.5"},
    "project": {"2.4", "4.3"},
    "ops": {"6.2", "8.3"},
}
_CONTEXT_BASELINE_PATHS = (
    ".harness-baseline-configuration/rules/session-bootstrap.md",
    ".harness-baseline-configuration/rules/operating-model.md",
)
_CONTEXT_FORMAL_ID = re.compile(r"\b(?:ADR|DCL|GOV|PB|REQ|SPEC)-[A-Za-z0-9][A-Za-z0-9_.:-]*")
_CONTEXT_ROW_VERSION = re.compile(
    r"(?P<id>(?:ADR|DCL|GOV|PB|REQ|SPEC)-[A-Za-z0-9][A-Za-z0-9_.:-]*) "
    r"(?:is )?active at row version (?P<version>[0-9]+)"
)


def _context_selection(
    record_id: str,
    recipient_role: str | None,
    activity: str | None,
    critical_sections: list[str] | None,
    critical_specs: list[str] | None,
) -> dict[str, Any] | None:
    """Explicit successor selectors, never a role binding or an effect grant."""
    sections, specs = critical_sections or [], critical_specs or []
    if recipient_role is None and activity is None and not sections and not specs:
        return None
    missing = [
        name
        for name, value in (("work_item", record_id), ("recipient_role", recipient_role), ("activity", activity))
        if not value
    ]
    if missing:
        _error(
            "context_inputs_required",
            "Supply the explicit successor context inputs",
            missing=missing,
            recovery_route="gt context work-item <WI-ID> --recipient-role <pb|lo> --activity <activity>",
        )
    if recipient_role not in {"pb", "lo"} or activity not in _CONTEXT_ACTIVITY_SECTIONS:
        _error(
            "invalid_context_selector",
            "Use a supported literal receiving role and activity",
            recipient_role=recipient_role,
            activity=activity,
            supported_roles=["pb", "lo"],
            supported_activities=sorted(_CONTEXT_ACTIVITY_SECTIONS),
        )
    for name, values in (("critical_sections", sections), ("critical_specs", specs)):
        if any(not isinstance(value, str) for value in values) or len(values) > 32 or len(values) != len(set(values)):
            _error("invalid_context_selector", "Selections must be unique and contain at most 32 values", selector=name)
    unknown = sorted(set(sections) - _CONTEXT_SAD_SECTIONS.keys())
    invalid = [
        value
        for value in specs
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}", value)
    ]
    if unknown or invalid:
        _error(
            "invalid_context_selector",
            "Select literal SAD section IDs and canonical formal IDs",
            unsupported_sections=unknown,
            invalid_formal_ids=invalid,
            supported_sections=sorted(_CONTEXT_SAD_SECTIONS),
        )
    selected = _CONTEXT_SHARED_SECTIONS | _CONTEXT_ACTIVITY_SECTIONS[activity] | set(sections)
    if recipient_role == "lo":
        selected |= {"4.2", "4.3"}
    return {
        "recipient_role": recipient_role,
        "activity": activity,
        "sections": sorted(selected, key=lambda key: tuple(map(int, key.split(".")))),
        "critical_sections": sorted(sections),
        "critical_specs": sorted(specs),
    }


def _context_file(root: Path, relative: str, limit: int) -> bytes:
    """Read only the named authored source in the configured service root."""
    path = root / relative
    try:
        if path.resolve(strict=True) != path or not path.is_file():
            raise ValueError("The selected source is redirected or not a regular file")
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError(f"The selected source exceeds {limit} bytes")
        return data
    except (OSError, ValueError) as error:
        _error(
            "context_source_unavailable",
            "Reconcile the named authored context source",
            path=relative,
            reason=str(error),
            recovery_route="Correct the named source in the authority service's configured project root",
        )


def _context_authored_sources(root: Path, selection: dict[str, Any]) -> dict[str, Any]:
    """Bounded excerpts from the existing SAD; no graph compiler or source store."""
    relative = "GT-KB_System_Architecture_Document_Target_EndState.docx"
    data = _context_file(root, relative, 2_097_152)
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = [entry for entry in archive.infolist() if entry.filename == "word/document.xml"]
            if len(entries) != 1 or entries[0].file_size > 2_097_152:
                raise ValueError("The SAD requires one bounded word/document.xml")
            document = ET.fromstring(archive.read(entries[0]))
        body = document.find(f"{{{namespace}}}body")
        if body is None:
            raise ValueError("The SAD has no Word document body")
        paragraphs = []

        def text_of(paragraph: ET.Element) -> str:
            return "".join(
                node.text or ""
                if node.tag == f"{{{namespace}}}t"
                else "\n"
                if node.tag in {f"{{{namespace}}}br", f"{{{namespace}}}cr"}
                else "\t"
                if node.tag == f"{{{namespace}}}tab"
                else ""
                for node in paragraph.iter()
            )

        for block in body:
            if block.tag == f"{{{namespace}}}p":
                paragraphs.append(text_of(block))
            elif block.tag == f"{{{namespace}}}tbl":
                for row in block.findall(f"{{{namespace}}}tr"):
                    cells = [
                        " / ".join(
                            text_of(paragraph).replace("\n", " / ") for paragraph in cell.iter(f"{{{namespace}}}p")
                        )
                        for cell in row.findall(f"{{{namespace}}}tc")
                    ]
                    paragraphs.append("| " + " | ".join(cells) + " |")
    except (
        OSError,
        ValueError,
        RuntimeError,
        NotImplementedError,
        EOFError,
        zipfile.BadZipFile,
        ET.ParseError,
    ) as error:
        _error(
            "context_source_unavailable",
            "The existing SAD cannot be read as bounded Word XML",
            path=relative,
            reason=str(error),
            recovery_route="Correct the existing SAD source; no alternate document is selected",
        )
    boundaries: list[tuple[int, str, str]] = []
    for index, paragraph in enumerate(paragraphs):
        match = re.fullmatch(r"([1-9][0-9]*)\s+([1-9][0-9]*)\s+(.+)", paragraph.strip())
        if match:
            boundaries.append((index, f"{match[1]}.{match[2]}", match[3]))
    sections = []
    for key in selection["sections"]:
        matches = [boundary for boundary in boundaries if boundary[1] == key]
        if len(matches) != 1 or matches[0][2] != _CONTEXT_SAD_SECTIONS[key]:
            _error(
                "context_section_unavailable",
                "A selected named SAD boundary is missing, duplicated or renamed",
                path=relative,
                section=key,
                expected_title=_CONTEXT_SAD_SECTIONS[key],
                matches=len(matches),
                recovery_route="Correct the named boundary in the existing SAD; no full-document fallback is selected",
            )
        start = matches[0][0]
        end = next((boundary[0] for boundary in boundaries if boundary[0] > start), len(paragraphs))
        sections.append({"id": key, "title": matches[0][2], "content": "\n".join(paragraphs[start:end]).strip()})
    baseline = []
    for path in _CONTEXT_BASELINE_PATHS:
        raw = _context_file(root, path, 65_536)
        try:
            content = raw.decode("utf-8-sig")
        except UnicodeError:
            _error(
                "context_source_unavailable",
                "The named authored baseline is not UTF-8",
                path=path,
                recovery_route="Correct the named authored baseline in the configured project root",
            )
        baseline.append({"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "content": content})
    text = "\n".join([*(section["content"] for section in sections), *(source["content"] for source in baseline)])
    declared_versions: dict[str, int] = {}
    for match in _CONTEXT_ROW_VERSION.finditer(text):
        key, version = match["id"], int(match["version"])
        if key in declared_versions and declared_versions[key] != version:
            _error(
                "conflicting_context_source",
                "Selected authored sources disagree on a current formal row version",
                id=key,
                versions=sorted({version, declared_versions[key]}),
                recovery_route=(
                    f"gt spec show {key} --json; correct the conflicting current-version claims "
                    "in the named authored context sources"
                ),
            )
        declared_versions[key] = version
    return {
        "sad": {"path": relative, "sha256": hashlib.sha256(data).hexdigest(), "sections": sections},
        "baseline": baseline,
        "formal_ids": sorted({match.rstrip(".:") for match in _CONTEXT_FORMAL_ID.findall(text)}),
        "declared_versions": declared_versions,
    }


def _context_message(context: dict[str, Any], selection: dict[str, Any], authored: dict[str, Any]) -> dict[str, Any]:
    """Informative inline body text; each excerpt is quoted against envelope parsing."""
    formals = {
        formal["id"]: formal for formal in [*context.get("authored_formal_references", []), *context["specifications"]]
    }
    for key, version in authored["declared_versions"].items():
        if key not in formals or formals[key]["version"] != version or formals[key].get("status") != "active":
            _error(
                "stale_context_source",
                "A selected authored source claims a stale current formal row version",
                id=key,
                declared_version=version,
                current_version=formals.get(key, {}).get("version"),
                current_status=formals.get(key, {}).get("status"),
                recovery_route=(
                    f"gt spec show {key} --json; correct that current-version claim "
                    "in the named authored context source"
                ),
            )
    lines = [
        (
            f"Informative context for successor {selection['recipient_role']}/{selection['activity']}, "
            f"work {context['work_item']['id']}."
        ),
        (
            "This selection is a message-context floor, not complete applicability, a new test result, "
            "an effect grant or a recall certificate."
        ),
        (
            "The recipient independently investigates current requirements and re-reads canonical facts "
            "before protected effects."
        ),
        "Canonical facts below share one read snapshot; authored SAD/baseline bytes were read separately.",
        (
            "Inactive authored-source references are historical information, "
            "never applicable normative sources or permission."
        ),
        "Current linked work, project, test, prerequisites and formal facts:",
        "> " + canonical_json_bytes(context).decode("utf-8").strip(),
        f"Informative SAD source: {authored['sad']['path']} sha256={authored['sad']['sha256']}",
    ]
    for section in authored["sad"]["sections"]:
        lines.append(f"SAD section {section['id']}: {section['title']}")
        lines.extend("> " + line for line in section["content"].splitlines())
    for baseline in authored["baseline"]:
        lines.append(f"Authored baseline: {baseline['path']} sha256={baseline['sha256']}")
        lines.extend("> " + line for line in baseline["content"].splitlines())
    return {
        "recipient_role": selection["recipient_role"],
        "activity": selection["activity"],
        "selected_sections": selection["sections"],
        "sender_critical_sections": selection["critical_sections"],
        "sender_critical_specs": selection["critical_specs"],
        "sad": authored["sad"],
        "baseline": authored["baseline"],
        "text": "\n".join(lines) + "\n",
    }


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
        if domain == "project-formal-links":
            requested = (filters or {}).get("artifact_type", "spec")
            if requested not in {"spec", "bridge_thread", "completion_guard"}:
                _error(
                    "invalid_query",
                    "Formal links are listed by spec, bridge_thread or completion_guard",
                    artifact_type=requested,
                )
            filters = {**(filters or {}), "artifact_type": requested}
        with self.kernel.transaction(read_only=True) as tx:
            records = tx.list(DOMAINS[domain], filters=filters, after=after, limit=limit, search=search)
        return {"records": records, "next_after": records[-1]["id"] if len(records) == limit else None}

    def show(self, domain: str, record_id: str) -> dict[str, Any]:
        if domain not in DOMAINS:
            _error("invalid_query", "Unknown knowledge domain")
        with self.kernel.transaction(read_only=True) as tx:
            row = _required(tx, DOMAINS[domain], record_id)
            if domain == "project-formal-links" and row["artifact_type"] not in {
                "spec",
                "bridge_thread",
                "completion_guard",
            }:
                _error(
                    "not_found", "The record is not a formal source or an obsolete project relationship", id=record_id
                )
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
                return {"work_item": row, **_membership_facts(tx, row)}
            return row

    def history(self, domain: str, record_id: str) -> dict[str, Any]:
        """The current record and its complete version chain; a missing record is not found, never empty history."""
        if domain not in DOMAINS:
            _error("invalid_query", "Unknown knowledge domain")
        with self.kernel.transaction(read_only=True) as tx:
            current = _required(tx, DOMAINS[domain], record_id)
            rows = tx.history(DOMAINS[domain], {"id": record_id})
        history = [
            {
                "version": row["new_version"],
                "prior_version": row["prior_version"],
                "actor": row["actor"],
                "changed_at": row["changed_at"],
                "reason": row["reason"],
                "state": row["new_state"],
            }
            for row in rows
        ]
        return {"current": current, "history": history}

    def specification_snapshot(self) -> dict[str, Any]:
        """Read the whole active formal corpus in one repeatable-read transaction."""
        with self.kernel.transaction(read_only=True) as tx:
            records = _related(tx, "specifications", status="active")
        return {"records": records, "consistency": "single_read_transaction"}

    @staticmethod
    def _term_source_issue(tx: PostgresTransaction, record: dict[str, Any]) -> dict[str, Any] | None:
        source = tx.get("specifications", {"id": record["source_authority"]})
        if source is None or source["status"] != "active":
            return {
                "id": record["id"],
                "source_authority": record["source_authority"],
                "status": source["status"] if source else "missing",
            }
        return None

    def resolve_authority(self, subject: str, *, scope: str | None = None) -> dict[str, Any]:
        from groundtruth_kb.authority import AuthorityResolutionError, resolve_term

        with self.kernel.transaction(read_only=True) as tx:
            try:
                result = resolve_term(subject, records=_related(tx, "canonical_terms"), scope=scope)
            except AuthorityResolutionError as error:
                _error("invalid_terminology", str(error))
            if result["status"] == "resolved":
                issue = self._term_source_issue(tx, result["record"])
                if issue:
                    _error("invalid_term_source", "The term's formal source requires reconciliation", **issue)
            return result

    def authority_status(self, *, scope: str | None = None) -> dict[str, Any]:
        from groundtruth_kb.authority import compact_status

        with self.kernel.transaction(read_only=True) as tx:
            records = _related(tx, "canonical_terms", **({"scope": scope} if scope is not None else {}))
            result = compact_status(records=records, scope=scope)
            issues = [
                issue
                for row in records
                if row["lifecycle_status"] == "active"
                if (issue := self._term_source_issue(tx, row)) is not None
            ]
            result["source_issues"] = issues
            if issues:
                result["status"] = "fail"
            return result

    def amend_term(self, record_id: str, request: TermMutation) -> dict[str, Any]:
        from groundtruth_kb.authority import compact_status

        with self.kernel.transaction() as tx:
            fields = request.fields.model_dump(exclude_unset=True)
            row = _write(tx, "canonical_terms", record_id, fields, request, defaults={"lifecycle_status": "candidate"})
            validation = compact_status(records=[{**row, "lifecycle_status": "active"}])
            if validation["validation_issues"]:
                _error("invalid_terminology", "Term names require correction", issues=validation["validation_issues"])
            if row["lifecycle_status"] == "active":
                issue = self._term_source_issue(tx, row)
                if issue:
                    _error("invalid_term_source", "An active term requires a current formal source", **issue)
            return row

    def registry_path_observations(self) -> list[dict[str, str]]:
        """Read the complete typed path inventory from one current snapshot."""
        with self.kernel.transaction(read_only=True) as tx:
            try:
                return registry_path_observations(
                    specifications=_related(tx, "specifications"),
                    tests=_related(tx, "tests"),
                    documents=_related(tx, "documents"),
                    project_artifact_links=_related(tx, "project_artifact_links", status="active"),
                )
            except ValueError as exc:
                _error("invalid_registry_path_source", str(exc))

    def amend_harness(self, record_id: str, request: HarnessMutation) -> dict[str, Any]:
        """Create or amend one harness installation record; roles never live here (they bind to contexts)."""
        from groundtruth_kb.harness_lifecycle import STATUS_ACTIVE, STATUS_REGISTERED, validate_transition

        fields = request.fields.model_dump(exclude_unset=True)
        if fields.get("invocation_surfaces") is not None:
            _refuse_role_bearing_surfaces(record_id, fields["invocation_surfaces"])
        with self.kernel.transaction() as tx:
            current = tx.get("harnesses", {"id": record_id}, lock=True)
            if current is None:
                for required in ("harness_name", "harness_type"):
                    if not fields.get(required):
                        _error(
                            "harness_fields_required", "A new harness needs harness_name and harness_type", id=record_id
                        )
                if fields.get("status") not in (None, STATUS_REGISTERED):
                    _error(
                        "invalid_harness_transition",
                        "A new harness starts as registered",
                        id=record_id,
                        status=fields["status"],
                    )
            elif "status" in fields and fields["status"] != current["status"]:
                try:
                    validate_transition(current["status"], fields["status"])
                except ValueError as exc:
                    _error("invalid_harness_transition", str(exc), id=record_id)
                if current["status"] == STATUS_ACTIVE:
                    others = [row for row in _related(tx, "harnesses", status=STATUS_ACTIVE) if row["id"] != record_id]
                    if not others:
                        _error(
                            "last_active_harness",
                            "The last active harness cannot be suspended or retired",
                            id=record_id,
                        )
            return _write(tx, "harnesses", record_id, fields, request, defaults={"status": STATUS_REGISTERED})

    def amend_specification(
        self, record_id: str, request: SpecMutation, *, project_root: Path | None = None
    ) -> dict[str, Any]:
        """Create or amend one specification; ``retired_at`` and ``implementation_verified_at`` are service-stamped.

        ``implementation_verified_at: true`` asserts that the implementation is verified now. The service
        refuses it with ``verification_evidence_required`` unless at least one test of this specification
        has a ``test_file`` and sits in an active test-plan phase (the ``_work_evidence`` mirror, owner
        ruling D17); with evidence it stamps its own clock, so the response differs from the request by
        design. ``null`` clears the marker without evidence. R26 (``gt kb reconcile --provisionals``) reads
        the stamped column.
        """
        fields = request.fields.model_dump(exclude_unset=True)
        with self.kernel.transaction() as tx:
            current = tx.get("specifications", {"id": record_id}, lock=True)
            scope = fields.get("application_scope", current.get("application_scope") if current else None)
            try:
                validate_application_scope(project_root, scope)
            except ApplicationRegistryError as error:
                _error("invalid_application_scope", str(error), id=record_id, application_scope=scope)
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
            # So is a verification time: the request asserts it, the evidence rule admits it, the service stamps it.
            if fields.get("implementation_verified_at") is True:
                if not _verification_evidence(tx, record_id):
                    _error(
                        "verification_evidence_required",
                        "Implementation verification requires an executable test of this specification "
                        "in an active test plan phase",
                        id=record_id,
                    )
                fields["implementation_verified_at"] = datetime.now(UTC).isoformat()
            return _write(tx, "specifications", record_id, fields, request, defaults={"status": "active"})

    def amend_test(self, record_id: str, request: TestMutation, *, project_root: Path | None = None) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            fields = request.fields.model_dump(exclude_unset=True)
            current = tx.get("tests", {"id": record_id}, lock=True)
            # Execution belongs to the previous selector, scope and acceptance definition.
            # The existing kernel history preserves that prior row; authors cannot forge results.
            definition_fields = (
                "test_file",
                "test_class",
                "test_function",
                "test_type",
                "expected_outcome",
                "spec_id",
                "application_scope",
            )
            if current and any(key in fields and fields[key] != current.get(key) for key in definition_fields):
                fields.update(last_result=None, last_executed_at=None, last_executed_on=None)
            scope = fields.get("application_scope", current.get("application_scope") if current else None)
            try:
                validate_application_scope(project_root, scope)
            except ApplicationRegistryError as error:
                _error("invalid_application_scope", str(error), id=record_id, application_scope=scope)
            return _write(tx, "tests", record_id, fields, request)

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
            current = tx.get("test_plan_phases", {"id": record_id}, lock=True)
            if current and "test_ids" in fields and set(fields["test_ids"] or []) != set(current["test_ids"] or []):
                # Stored execution evidence belongs to the previous membership.
                # Native amendments cannot supply a replacement execution result.
                fields.update(last_result=None, last_executed_at=None, last_executed_on=None)
            for test_id in fields.get("test_ids") or []:
                _required(tx, "tests", test_id)
            return _write(tx, "test_plan_phases", record_id, fields, request)

    def amend_project(
        self, record_id: str, request: ProjectMutation, *, project_root: Path | None = None
    ) -> dict[str, Any]:
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
            repository_ref = fields.get("repository_ref", current.get("repository_ref") if current else None)
            if kind == "program":
                if repository_ref is not None:
                    _error("program_has_no_repository", "Programs sequence outcomes and do not select a Git repository")
            else:
                if repository_ref is None:
                    _error("project_repository_required", "Set the execution project's explicit repository_ref")
                if project_root is None:
                    _error(
                        "repository_host_required",
                        "Project repository validation requires the configured platform host",
                    )
                try:
                    resolve_project_repository(project_root, repository_ref)
                except ApplicationRegistryError as error:
                    _error("invalid_repository_ref", str(error), repository_ref=repository_ref)
                if current and repository_ref != current.get("repository_ref"):
                    tx.cursor.execute(
                        sql.SQL(
                            "SELECT 1 FROM {}.bridge_attempts WHERE project_id=%s AND disposition='active' LIMIT 1"
                        ).format(sql.Identifier(tx.schema)),
                        (record_id,),
                    )
                    if tx.cursor.fetchone() or _project_commit(tx, record_id):
                        _error(
                            "project_repository_frozen",
                            "Repository reassignment cannot move active attempts or committed work",
                        )
            fields["kind"] = kind
            defaults = {"status": "active", "authorization": None if kind == "program" else "authorized"}
            if record_id == "PROJECT-GTKB-NEW-WORK-INTAKE":
                defaults["authorization"] = "not authorized"
            return _write(tx, "projects", record_id, fields, request, defaults=defaults)

    def set_project_authorization(self, record_id: str, request: ProjectAuthorizationChange) -> dict[str, Any]:
        """Apply owner-directed ordering to the existing project row.

        This operation neither changes membership nor revokes initiated
        attempts.

        c123 (owner decision E1): the service does not authenticate its
        callers, so the actor is attribution, not proof of permission. For
        agent harnesses, project authorization, membership moves
        (move_work_item) and execution-project creation (amend_project at
        version 0) are guarded at the effect gate as owner operations, which
        the owner runs in their own terminal
        (GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001). A caller the gate does
        not read, such as a program run inside a claim, is not refused here.
        """
        with self.kernel.transaction() as tx:
            current = _required(tx, "projects", record_id, lock=True)
            if current["version"] != request.expected_version:
                _error(
                    "cas_conflict",
                    "Read the current project before changing authorization",
                    id=record_id,
                    expected=request.expected_version,
                    actual=current["version"],
                )
            if current["kind"] != "project":
                _error("program_not_authorizable", "Programs have no execution authorization")
            if current["status"] != "active":
                _error("project_closed", "A closed project cannot change execution ordering")
            if record_id == "PROJECT-GTKB-NEW-WORK-INTAKE" and request.authorization != "not authorized":
                _error("intake_not_authorizable", "Move intake work to its execution project before dispatch")
            if current["authorization"] == request.authorization:
                return current
            return _write(tx, "projects", record_id, {"authorization": request.authorization}, request)

    def retire_project(self, record_id: str, request: ProjectRetirement) -> dict[str, Any]:
        """Retire one active program or execution project by status only, with history (owner ruling D32).

        Exactly one field changes (``status`` -> ``retired``) at version+1 with one history row carrying the
        actor and reason. Kind, authorization, parent, dates, ``completed_at`` (the commit date of a verified
        project only), every membership row (a closed member's active membership is its preserved parent),
        every formal link, every dependency row and every child project are untouched: retiring a project
        never erases a parent or collectively rewrites sibling results (GOV-WORK-ITEM-TERMINAL-STATE-001,
        GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001). Open members are refused, not retired with it, and
        retirement is not implementation verification (GOV-STANDING-BACKLOG-001). An already-closed project
        is refused rather than re-closed. Programs are retirable; a retired program keeps its children and
        cannot acquire new ones (amend_project refuses a non-active program parent).
        """
        with self.kernel.transaction() as tx:
            current = _required(tx, "projects", record_id, lock=True)
            if current["version"] != request.expected_version:
                _error(
                    "cas_conflict",
                    "Read the current project before retiring it",
                    id=record_id,
                    expected=request.expected_version,
                    actual=current["version"],
                )
            if current["status"] != "active":
                _error(
                    "project_closed",
                    "A closed project keeps its terminal state; retirement is not a second closure",
                    id=record_id,
                    status=current["status"],
                )
            if record_id == "PROJECT-GTKB-NEW-WORK-INTAKE":
                _error("project_structure_frozen", "The standing intake project is not retirable", id=record_id)
            members = _open_members(tx, current)
            if members["work_item_ids"] or members["project_ids"]:
                _error(
                    "members_open",
                    "Retire or re-home the open members first; retirement never closes them collectively",
                    id=record_id,
                    **members,
                )
            attempts = _active_attempts(tx, project_id=record_id)
            if attempts:
                _error(
                    "attempt_active",
                    "An active bridge attempt holds reviewed or in-progress work of this project",
                    id=record_id,
                    attempt_ids=attempts,
                )
            dependants = _active_dependants(tx, record_id)
            if dependants:
                _error(
                    "dependants_open",
                    "Active projects still require this prerequisite to reach a state a retired project cannot",
                    id=record_id,
                    dependency_ids=sorted(row["id"] for row in dependants),
                    dependent_project_ids=sorted({row["dependent_project_id"] for row in dependants}),
                )
            return _write(tx, "projects", record_id, {"status": "retired"}, request)

    def amend_project_formal_link(self, record_id: str, request: ProjectFormalLinkMutation) -> dict[str, Any]:
        """Amend formal roots or retire obsolete links without changing authorization."""
        with self.kernel.transaction() as tx:
            current = tx.get("project_artifact_links", {"id": record_id}, lock=True)
            actual = current["version"] if current else 0
            if actual != request.expected_version:
                _error("cas_conflict", "Read the current formal link before changing it", actual=actual, id=record_id)
            fields = request.fields.model_dump(exclude_unset=True)
            if current and current["artifact_type"] != "spec":
                # Imported bridge references and completion guards are obsolete
                # relationships. Retire their status without rewriting identity,
                # creating a substitute, or touching Git activation evidence.
                if (
                    current["artifact_type"] not in {"bridge_thread", "completion_guard"}
                    or current["status"] != "active"
                    or fields != {"status": "retired"}
                ):
                    _error("invalid_formal_link", "Only status-only retirement of an obsolete relationship is allowed")
                _execution_project(tx, current["project_id"])
                return _write(tx, "project_artifact_links", record_id, fields, request)
            candidate = {**(current or {"status": "active"}), **fields}
            if not candidate.get("project_id") or not candidate.get("artifact_ref"):
                _error("formal_link_endpoint_required", "A formal link names an execution project and formal record")
            if current and any(candidate[key] != current[key] for key in ("project_id", "artifact_ref")):
                _error("formal_link_identity_frozen", "Retire the old relationship and create the intended new one")
            if candidate["status"] not in {"active", "retired"}:
                _error("invalid_formal_link_transition", "A formal relationship is active or retired")
            if not current and candidate["status"] != "active":
                _error("invalid_formal_link_transition", "A new formal relationship starts active")
            # Bridge effects and finalization hold the same project row. A root
            # change cannot cross an effect, and later operations re-read roots.
            _execution_project(tx, candidate["project_id"])
            if candidate["status"] == "active":
                source = _required(tx, "specifications", candidate["artifact_ref"], lock=True)
                if source["status"] != "active":
                    _error("inactive_formal_source", "An active formal link requires a current active formal record")
                duplicates = _related(
                    tx,
                    "project_artifact_links",
                    project_id=candidate["project_id"],
                    artifact_type="spec",
                    artifact_ref=candidate["artifact_ref"],
                    status="active",
                )
                if any(row["id"] != record_id for row in duplicates):
                    _error("duplicate_formal_link", "This project already has an active relationship to the source")
            return _write(
                tx,
                "project_artifact_links",
                record_id,
                fields,
                request,
                defaults={"artifact_type": "spec", "relationship": "governed_by", "status": "active"},
            )

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

    def _reconcile_work_item_resolution(
        self,
        tx: PostgresTransaction,
        current: dict[str, Any],
        request: WorkItemMutation,
        *,
        project_root: Path | None = None,
    ) -> dict[str, Any]:
        """Correct imported resolution through the existing writer, without reopening committed work.

        The caller supplies the owner's inspected final disposition. Missing canonical commit facts
        never establish that historical physical work was uncommitted; Git-shaped evidence requires
        inspection instead. This branch does not move an ordinary valid single-parent work item.
        """
        if current["version"] != request.expected_version:
            _error("cas_conflict", "Read the current work item before correcting its resolution", id=current["id"])
        target = request.fields.resolution_status
        supplied_evidence = "completion_evidence" in request.fields.model_fields_set
        clear_rejected_evidence = (
            supplied_evidence
            and target == "open"
            and current["resolution_status"] in {"verified", "implemented", "resolved"}
            and request.fields.completion_evidence == ""
        )
        if supplied_evidence and (
            not clear_rejected_evidence
            and (
                target != "verified"
                or current["resolution_status"] not in {"verified", "implemented", "resolved"}
                or request.fields.completion_evidence is None
            )
        ):
            _error(
                "invalid_completion_evidence",
                "Historical correction accepts exact completion evidence to verified "
                "or an explicit empty clear to open",
            )
        if target == current["resolution_status"] and not supplied_evidence:
            if request.project_id and _current_parent(tx, current["id"])["project_id"] != request.project_id:
                _error("membership_move_required", "Use the atomic membership move operation")
            return {"work_item": current, **_membership_facts(tx, current)}
        if current["resolution_status"] == "open":
            _error(
                "work_item_frozen",
                "Ordinary work cannot set verified; project commit confirms it. Use the retirement route for retired",
            )
        legacy = {
            "implemented": "verified",
            "resolved": "verified",
            "not yet implemented": "open",
            "not_yet_implemented": "open",
            "wont_fix": "retired",
            "not_a_defect": "retired",
            "deferred": "retired",
            "drop": "retired",
        }
        false_completion = current["resolution_status"] in {"verified", "implemented", "resolved"} and target == "open"
        if (
            legacy.get(current["resolution_status"]) != target
            and not false_completion
            and not (current["resolution_status"] == target == "verified" and supplied_evidence)
        ):
            _error("work_item_frozen", "The requested postimage is not a lawful legacy resolution correction")
        if target != "open" and request.project_id:
            _error("membership_move_required", "Status-only normalization preserves recorded memberships")
        memberships = _related(tx, "project_work_item_memberships", work_item_id=current["id"])
        active = [member for member in memberships if member["status"] == "active"]
        parents = {member["project_id"] for member in active}
        project_ids = parents | ({request.project_id} if request.project_id else set())
        projects = {project_id: _required(tx, "projects", project_id, lock=True) for project_id in sorted(project_ids)}
        tx.cursor.execute(
            sql.SQL(
                "SELECT id,disposition,terminal_commit FROM {}.bridge_attempts WHERE work_item_id=%s FOR UPDATE"
            ).format(sql.Identifier(tx.schema)),
            (current["id"],),
        )
        attempts = tx.cursor.fetchall()
        live = [attempt["id"] for attempt in attempts if attempt["disposition"] == "active"]
        if live:
            _error(
                "attempt_active",
                "Conclude or reconcile the active attempt before correcting resolution",
                attempt_ids=live,
            )
        terminal = [
            attempt for attempt in attempts if attempt["disposition"] == "committed" or attempt["terminal_commit"]
        ]
        commits = {attempt["terminal_commit"] for attempt in terminal if attempt["terminal_commit"]}
        for parent in sorted(parents):
            links = _related(
                tx,
                "project_artifact_links",
                project_id=parent,
                artifact_type="git_commit",
                relationship="activation",
                status="active",
            )
            terminal.extend(links)
            commits.update(link["artifact_ref"] for link in links)
        if terminal and target != "verified":
            _error(
                "work_item_frozen",
                "Canonical committed terminal facts cannot be reopened or re-homed",
                id=current["id"],
            )
        evidence = current.get("completion_evidence") or ""
        if target == "verified":
            evidence = request.fields.completion_evidence if supplied_evidence else evidence
            if not isinstance(evidence, str):
                _error("invalid_completion_evidence", "Historical completion requires exact Git evidence")
            if terminal and (not commits or commits != {evidence.removeprefix("git:")}):
                _error(
                    "terminal_commit_mismatch",
                    "Historical correction cannot conflict with existing canonical terminal commit facts",
                    id=current["id"],
                )
            if len(active) != 1:
                _error(
                    "invalid_membership",
                    "Historical completion requires one established execution project",
                    work_item_id=current["id"],
                )
            evidence = _confirm_historical_commit(project_root, projects[active[0]["project_id"]], evidence)
        elif not clear_rejected_evidence and (
            re.search(r"\bgit:", evidence, re.IGNORECASE)
            or re.fullmatch(r"[0-9a-fA-F]{7,64}", evidence.strip())
            or re.search(r"\bcommit(?:ted)?(?:\s+as)?[:=\s]+[0-9a-fA-F]{7,64}\b", evidence, re.IGNORECASE)
        ):
            _error(
                "git_reconciliation_required",
                "Inspect the historical Git-shaped completion evidence; missing canonical facts do not prove no commit",
                id=current["id"],
            )
        if target == "open":
            sole = projects[active[0]["project_id"]] if len(active) == 1 else None
            if sole is not None and sole["kind"] == "project" and sole["status"] == "active":
                if request.project_id and request.project_id != sole["id"]:
                    _error(
                        "membership_move_required",
                        "Return under the current parent, then use the atomic move operation",
                    )
                destination = sole
            elif request.project_id:
                destination = _execution_project(tx, request.project_id)
            else:
                _error(
                    "project_required",
                    "Choose one active execution project for missing, multiple or closed parents",
                )
            changed_parents = parents ^ {destination["id"]}
            for member in sorted(active, key=lambda item: item["id"]):
                if member["project_id"] != destination["id"]:
                    _write(
                        tx,
                        "project_work_item_memberships",
                        member["id"],
                        {"status": "removed"},
                        Mutation(expected_version=member["version"], actor=request.actor, reason=request.reason),
                    )
            existing = next((member for member in memberships if member["project_id"] == destination["id"]), None)
            if existing is None or existing["status"] != "active":
                _write(
                    tx,
                    "project_work_item_memberships",
                    existing["id"] if existing else f"PWM-{uuid4().hex}",
                    {
                        "project_id": destination["id"],
                        "work_item_id": current["id"],
                        "status": "active",
                        "membership_order": (
                            existing["membership_order"] if existing else current.get("implementation_order")
                        ),
                        "source": "domain_service",
                    },
                    Mutation(
                        expected_version=existing["version"] if existing else 0,
                        actor=request.actor,
                        reason=request.reason,
                    ),
                )
            for project_id in sorted(changed_parents):
                project = projects[project_id]
                if project["kind"] == "project" and project["authorization"] != "not authorized":
                    _write(
                        tx,
                        "projects",
                        project_id,
                        {"authorization": "not authorized"},
                        Mutation(expected_version=project["version"], actor=request.actor, reason=request.reason),
                    )
        fields: dict[str, Any] = {"resolution_status": target}
        if target == "verified":
            fields["completion_evidence"] = evidence
            if all(current.get(key) == value for key, value in fields.items()) and (
                current.get("changed_by") == request.actor and current.get("change_reason") == request.reason
            ):
                return {"work_item": current, **_membership_facts(tx, current)}
        elif clear_rejected_evidence:
            # The caller records substantive scope inspection in the existing reason. Physical Git checks alone
            # cannot prove full semantic completion. Native history retains the rejected text in its prior state;
            # an omitted evidence field preserves it, and all terminal/attempt/membership guards above still apply.
            fields["completion_evidence"] = ""
        row = _write(tx, "work_items", current["id"], fields, request)
        return {"work_item": row, **_membership_facts(tx, row)}

    def amend_work_item(
        self, record_id: str, request: WorkItemMutation, *, project_root: Path | None = None
    ) -> dict[str, Any]:
        fields = request.fields.model_dump(exclude_unset=True)
        with self.kernel.transaction() as tx:
            current = tx.get("work_items", {"id": record_id}, lock=True)
            if "resolution_status" in fields:
                if fields["resolution_status"] is None:
                    _error("invalid_request", "Resolution status cannot be null")
                if current:
                    if set(fields) - {"resolution_status", "completion_evidence"}:
                        _error("invalid_request", "Resolution correction cannot also amend ordinary work fields")
                    return self._reconcile_work_item_resolution(tx, current, request, project_root=project_root)
                if fields["resolution_status"] != "open":
                    _error("work_item_frozen", "New work starts open; only confirmed project commit sets verified")
            if "completion_evidence" in fields:
                _error("invalid_completion_evidence", "Ordinary work cannot author terminal completion evidence")
            if current:
                membership = _current_parent(tx, record_id)
                project = _execution_project(tx, membership["project_id"])
                if request.project_id and request.project_id != project["id"]:
                    _error("membership_move_required", "Use the atomic membership move operation")
                if current["resolution_status"] != "open" or _active_attempts(
                    tx, work_item_id=record_id, reviewed_only=True
                ):
                    _error("work_item_frozen", "Reviewed or closed work cannot be amended through ordinary intake")
            else:
                if not request.project_id:
                    _error("project_required", "New work requires an existing execution project")
                project = _execution_project(tx, request.project_id)
            state = {**(current or {}), **fields}
            # Planning amendments preserve visible evidence gaps in existing work.
            # Creation and changed evidence links still require a complete pair;
            # proposal publication independently rechecks the current evidence.
            if current is None or any(
                state.get(key) != current.get(key) for key in ("source_spec_id", "source_test_id")
            ):
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
                if project["authorization"] != "not authorized":
                    _write(
                        tx,
                        "projects",
                        project["id"],
                        {"authorization": "not authorized"},
                        Mutation(
                            expected_version=project["version"],
                            actor=request.actor,
                            reason=request.reason,
                        ),
                    )
            return {"work_item": row, **_membership_facts(tx, row)}

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
            if row["resolution_status"] != "open" or _active_attempts(tx, work_item_id=record_id, reviewed_only=True):
                _error("work_item_frozen", "Reviewed or closed membership requires reconciliation")
            current = _current_parent(tx, record_id)
            if current["project_id"] != request.source_project_id or current["version"] != request.expected_version:
                _error("cas_conflict", "Read the current membership before moving work")
            projects = [
                _execution_project(tx, project_id)
                for project_id in sorted({request.source_project_id, request.destination_project_id})
            ]
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
            for project in projects:
                if project["authorization"] != "not authorized":
                    _write(
                        tx,
                        "projects",
                        project["id"],
                        {"authorization": "not authorized"},
                        Mutation(
                            expected_version=project["version"],
                            actor=request.actor,
                            reason=request.reason,
                        ),
                    )
            return {"work_item_id": record_id, "membership": updated}

    def retire_work_item(self, record_id: str, request: WorkItemRetirement) -> dict[str, Any]:
        """Retire one open work item by status only, with history (owner ruling D32).

        Exactly one field changes (``resolution_status`` -> ``retired``) at version+1 with one history row
        carrying the actor and reason. Stage, title, evidence links (an evidence gap stays visible), the
        predecessor list, notes, the active parent membership and every sibling are untouched: active
        membership describes the current parent, including for closed work, and siblings are never retired
        collectively (GOV-WORK-ITEM-TERMINAL-STATE-001). Already-terminal work is refused rather than
        re-closed; open dependants are refused rather than re-pointed; an active bridge attempt is refused
        because its later project finalization would conflict with retirement. Retirement is not
        implementation verification (GOV-STANDING-BACKLOG-001). The response is the work-item read shape.
        """
        with self.kernel.transaction() as tx:
            current = _required(tx, "work_items", record_id, lock=True)
            if current["version"] != request.expected_version:
                _error(
                    "cas_conflict",
                    "Read the current work item before retiring it",
                    id=record_id,
                    expected=request.expected_version,
                    actual=current["version"],
                )
            if current["resolution_status"] != "open":
                _error(
                    "work_item_frozen",
                    "Reviewed or closed work keeps its terminal state; retirement is not a reopen or a second closure",
                    id=record_id,
                    resolution_status=current["resolution_status"],
                )
            membership = _current_parent(tx, record_id)
            # Same lock order as the bridge (work, then project): effects and finalization serialize with this.
            _execution_project(tx, membership["project_id"])
            attempts = _active_attempts(tx, work_item_id=record_id)
            if attempts:
                _error(
                    "attempt_active",
                    "An active bridge attempt holds this work; conclude or abandon it before retirement",
                    id=record_id,
                    attempt_ids=attempts,
                )
            dependants = _open_dependants(tx, record_id)
            if dependants:
                _error(
                    "dependants_open",
                    "Open work still depends on this item; retire or re-point the dependants first",
                    id=record_id,
                    dependant_work_item_ids=dependants,
                )
            row = _write(tx, "work_items", record_id, {"resolution_status": "retired"}, request)
            return {"work_item": row, **_membership_facts(tx, row)}

    def task_context(
        self,
        record_id: str,
        *,
        predecessor_readiness: Callable[[PostgresTransaction, str], dict[str, Any]] | None = None,
        recipient_role: str | None = None,
        activity: str | None = None,
        critical_sections: list[str] | None = None,
        critical_specs: list[str] | None = None,
        project_root: Path | None = None,
    ) -> dict[str, Any]:
        """Load linked current facts without another context's memory or state."""
        selection = _context_selection(record_id, recipient_role, activity, critical_sections, critical_specs)
        authored: dict[str, Any] = {}
        if selection is not None:
            if project_root is None:
                _error(
                    "context_source_unavailable",
                    "Composition requires the service's configured project root",
                    recovery_route="Configure the existing authority service's project root",
                )
            authored = _context_authored_sources(project_root, selection)
        with self.kernel.transaction(read_only=True) as tx:
            work = _required(tx, "work_items", record_id)
            membership = _current_parent(tx, record_id)
            project = _required(tx, "projects", membership["project_id"])
            program = _required(tx, "projects", project["parent_project_id"]) if project["parent_project_id"] else None
            authored_references = []
            if selection:
                for key in authored["formal_ids"]:
                    source = tx.get("specifications", {"id": key})
                    if source is None:
                        _error(
                            "context_source_unavailable",
                            "A selected authored context formal reference is missing",
                            id=key,
                            recovery_route=(
                                f"gt spec show {key} --json; correct the reference in the named SAD or baseline source"
                            ),
                        )
                    if source.get("status") not in {"active", "retired", "superseded"}:
                        _error(
                            "context_source_unavailable",
                            "A selected authored context formal reference has malformed lifecycle state",
                            id=key,
                            recovery_route=f"gt spec show {key} --json",
                        )
                    authored_references.append(source)
            additional = (
                sorted(
                    set(
                        selection["critical_specs"]
                        + [row["id"] for row in authored_references if row["status"] == "active"]
                    )
                )
                if selection
                else None
            )
            formals = _work_formal_sources(tx, work, project["id"], additional_ids=additional)
            stale = [formal["id"] for formal in formals if formal["status"] != "active"]
            if stale:
                _error(
                    "inactive_context_source",
                    "Task links require reconciliation to active formal sources",
                    ids=stale,
                    recovery_route=f"gt context work-item {record_id}",
                )
            test = _required(tx, "tests", work["source_test_id"]) if work.get("source_test_id") else None
            phases = _test_phases(tx, test["id"]) if test else []
            if test and not phases:
                _error(
                    "test_phase_required",
                    "The linked test has no active test-plan phase; reconcile current test instructions",
                    id=test["id"],
                    recovery_route=f"gt context work-item {record_id}",
                )
            result = {
                "work_item": work,
                "membership": membership,
                "project": project,
                "program": program,
                "specifications": formals,
                "test": test,
                "test_phases": phases,
                "test_plans": [
                    _required(tx, "test_plans", key) for key in sorted({phase["plan_id"] for phase in phases})
                ],
                "predecessors": [_required(tx, "work_items", key) for key in work.get("depends_on_work_items") or []],
                "readiness": _project_dependency_readiness(tx, project["id"], "readiness"),
                **({"work_item_readiness": predecessor_readiness(tx, record_id)} if predecessor_readiness else {}),
                "project_dependencies": _related(
                    tx, "project_dependencies", dependent_project_id=project["id"], status="active"
                ),
            }
            if selection is not None:
                result["authored_formal_references"] = authored_references
                result["message_context"] = _context_message(result, selection, authored)
            return result
