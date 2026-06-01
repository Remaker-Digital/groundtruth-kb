"""Implementation for the governed ``gt backlog authorize-implementation`` command.

Authority: bridge/gtkb-backlog-authorize-implementation-cli-slice-1-003.md
(REVISED), Codex GO at
``bridge/gtkb-backlog-authorize-implementation-cli-slice-1-004.md``.
Source work item: WI-3494. Owner decision: DELIB-2547 (S379 disposition
"Reduce friction, keep gates").

``gt backlog authorize-implementation WI-NNNN`` collapses the multi-call
project-authorization plumbing required before filing a bridge proposal for an
owner-selected work item -- record the owner-decision deliberation, create the
project authorization, then cite it -- into one governed command, per the
Deterministic Services Principle (DELIB-S312).

Governance preservation (NOT an authorization bypass): the command REQUIRES
owner-decision evidence and fails closed without it. It accepts either an
existing owner-authority deliberation (``source_type == 'owner_conversation'``
AND ``outcome == 'owner_decision'``) via ``--owner-decision``, OR fresh AUQ
evidence routed through the already-governed ``gt deliberations record`` path.
It never fabricates owner authorization and it touches no gate logic. The
produced authorization still requires a bridge proposal, Codex GO, an
implementation-start packet, spec-derived tests, a post-implementation report,
and VERIFIED before any implementation lands
(PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import (
    ProjectLifecycleError,
    ProjectLifecycleService,
)

# Owner-authority predicate (NO-GO -002 F2): an existing ``--owner-decision``
# deliberation is accepted as owner authority only when BOTH conditions hold.
# This is the CLI-layer enforcement point because
# ``KnowledgeDB.insert_project_authorization`` validates only that the
# deliberation EXISTS (db.py), not that it carries owner authority.
OWNER_AUTHORITY_SOURCE_TYPE = "owner_conversation"
OWNER_AUTHORITY_OUTCOME = "owner_decision"


class AuthorizeImplementationError(Exception):
    """Raised when ``gt backlog authorize-implementation`` cannot safely proceed."""


@dataclass(frozen=True)
class AuthorizeImplementationRequest:
    """Validated request for one ``gt backlog authorize-implementation`` invocation.

    Exactly one owner-decision authority path must be supplied: an existing
    ``owner_decision`` (an owner-authority deliberation id) XOR fresh AUQ
    evidence (``auq_id`` + ``auq_answer`` + ``decision_content_file``).
    """

    work_item_id: str
    owner_decision: str | None
    auq_id: str | None
    auq_answer: str | None
    decision_content_file: str | None
    decision_title: str | None
    decision_summary: str | None
    project_id: str | None
    include_spec_ids: tuple[str, ...]
    allowed_mutation_classes: tuple[str, ...]
    forbidden_operations: tuple[str, ...]
    authorization_id: str | None
    authorization_name: str | None
    scope_summary: str | None
    change_reason: str
    session_id: str | None
    dry_run: bool


def _active_project_memberships(db: KnowledgeDB, work_item_id: str) -> list[str]:
    rows = (
        db._get_conn()
        .execute(
            "SELECT project_id FROM current_project_work_item_memberships WHERE work_item_id = ? AND status = 'active'",
            (work_item_id,),
        )
        .fetchall()
    )
    return [row[0] for row in rows]


def _resolve_project(db: KnowledgeDB, work_item_id: str, explicit_project: str | None) -> str:
    """Resolve the active project the work item belongs to.

    Fail closed when the work item has no active membership, or when it has more
    than one and ``--project`` was not supplied to disambiguate. When
    ``--project`` is supplied, the work item must be an active member of it (the
    Write-time bridge gate requires active membership, so an authorization on a
    non-member project would be useless).
    """
    memberships = _active_project_memberships(db, work_item_id)
    if explicit_project:
        if explicit_project not in memberships:
            raise AuthorizeImplementationError(
                f"work item {work_item_id} is not an active member of project {explicit_project}; "
                f"active memberships: {memberships or 'none'}"
            )
        return explicit_project
    if not memberships:
        raise AuthorizeImplementationError(
            f"work item {work_item_id} is not an active member of any project; pass --project"
        )
    if len(memberships) > 1:
        raise AuthorizeImplementationError(
            f"work item {work_item_id} is an active member of multiple projects {memberships}; "
            "pass --project to disambiguate"
        )
    return memberships[0]


def _validate_owner_authority(db: KnowledgeDB, deliberation_id: str) -> str:
    """Validate that an existing deliberation carries owner authority (F2)."""
    deliberation = db.get_deliberation(deliberation_id)
    if deliberation is None:
        raise AuthorizeImplementationError(f"owner-decision deliberation {deliberation_id} not found")
    source_type = deliberation.get("source_type")
    outcome = deliberation.get("outcome")
    if source_type != OWNER_AUTHORITY_SOURCE_TYPE or outcome != OWNER_AUTHORITY_OUTCOME:
        raise AuthorizeImplementationError(
            f"deliberation {deliberation_id} is not owner authority "
            f"(source_type={source_type!r}, outcome={outcome!r}); require "
            f"source_type={OWNER_AUTHORITY_SOURCE_TYPE!r} and outcome={OWNER_AUTHORITY_OUTCOME!r}"
        )
    return deliberation_id


def _record_fresh_owner_decision(config: GTConfig, request: AuthorizeImplementationRequest) -> dict[str, Any]:
    """Record a fresh owner-decision deliberation through the governed path."""
    from groundtruth_kb.cli_deliberations_record import (
        DeliberationRecordError,
        DeliberationRecordRequest,
        record_deliberation,
    )

    if not (request.auq_id and request.auq_answer and request.decision_content_file):
        raise AuthorizeImplementationError(
            "fresh owner-decision evidence requires --auq-id, --auq-answer, and --decision-content-file"
        )
    record_request = DeliberationRecordRequest(
        source_type=OWNER_AUTHORITY_SOURCE_TYPE,
        source_ref=request.auq_id,
        title=request.decision_title or f"Owner authorization for {request.work_item_id}",
        summary=request.decision_summary or request.auq_answer,
        content_file=Path(request.decision_content_file),
        change_reason=request.change_reason,
        auq_id=request.auq_id,
        auq_answer=request.auq_answer,
        owner_presented=True,
        approved_by="owner",
        spec_id=None,
        work_item_id=request.work_item_id,
        participants=None,
        outcome=OWNER_AUTHORITY_OUTCOME,
        session_id=request.session_id,
        dry_run=request.dry_run,
    )
    try:
        return record_deliberation(config, record_request)
    except DeliberationRecordError as exc:
        raise AuthorizeImplementationError(str(exc)) from exc


def _validate_request(request: AuthorizeImplementationRequest) -> None:
    if not request.work_item_id or not request.work_item_id.strip():
        raise AuthorizeImplementationError("work_item_id is required")
    if not request.change_reason or not request.change_reason.strip():
        raise AuthorizeImplementationError("--change-reason must be a non-empty string")

    has_existing = bool(request.owner_decision and request.owner_decision.strip())
    has_fresh = bool(request.auq_id or request.auq_answer or request.decision_content_file)
    if has_existing and has_fresh:
        raise AuthorizeImplementationError(
            "supply exactly one owner-decision authority path: either --owner-decision OR fresh "
            "AUQ evidence (--auq-id/--auq-answer/--decision-content-file), not both"
        )
    if not has_existing and not has_fresh:
        raise AuthorizeImplementationError(
            "owner-decision evidence required: pass --owner-decision DELIB-NNNN or fresh AUQ "
            "evidence (--auq-id/--auq-answer/--decision-content-file)"
        )
    if not request.include_spec_ids:
        raise AuthorizeImplementationError(
            "--include-spec is required (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001)"
        )
    if not request.allowed_mutation_classes:
        raise AuthorizeImplementationError("--allowed-mutation is required")


def authorize_implementation(config: GTConfig, request: AuthorizeImplementationRequest) -> dict[str, Any]:
    """Resolve the project, secure owner-decision evidence, and create a bounded
    project authorization for a single work item.

    Fails closed (no authorization written) on missing or invalid owner evidence,
    on an unresolvable/ambiguous project, or on missing spec linkage.
    """
    _validate_request(request)

    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)

    if db.get_work_item(request.work_item_id) is None:
        raise AuthorizeImplementationError(f"work item {request.work_item_id} not found")

    project_id = _resolve_project(db, request.work_item_id, request.project_id)

    has_existing = bool(request.owner_decision and request.owner_decision.strip())
    deliberation_result: dict[str, Any] | None = None
    if has_existing:
        owner_decision_id = _validate_owner_authority(db, request.owner_decision.strip())
    else:
        deliberation_result = _record_fresh_owner_decision(config, request)
        owner_decision_id = deliberation_result["id"]

    proposed_authorization = {
        "id": request.authorization_id,
        "project_id": project_id,
        "included_work_item_ids": [request.work_item_id],
        "included_spec_ids": list(request.include_spec_ids),
        "allowed_mutation_classes": list(request.allowed_mutation_classes),
        "forbidden_operations": list(request.forbidden_operations),
        "owner_decision": owner_decision_id,
    }

    if request.dry_run:
        return {
            "created": False,
            "dry_run": True,
            "work_item_id": request.work_item_id,
            "project_id": project_id,
            "owner_decision": owner_decision_id,
            "proposed_authorization": proposed_authorization,
            "deliberation": deliberation_result,
        }

    service = ProjectLifecycleService(db)
    name = request.authorization_name or f"Authorize {request.work_item_id} implementation"
    scope = request.scope_summary or (
        f"Bounded implementation authorization for {request.work_item_id} per owner decision {owner_decision_id}."
    )
    try:
        authorization = service.authorize_project(
            project_id,
            owner_decision=owner_decision_id,
            name=name,
            scope=scope,
            change_reason=request.change_reason,
            authorization_id=request.authorization_id,
            allowed_mutation_classes=list(request.allowed_mutation_classes) or None,
            forbidden_operations=list(request.forbidden_operations) or None,
            included_work_item_ids=[request.work_item_id],
            included_spec_ids=list(request.include_spec_ids) or None,
        )
    except ProjectLifecycleError as exc:
        raise AuthorizeImplementationError(str(exc)) from exc

    return {
        "created": True,
        "dry_run": False,
        "work_item_id": request.work_item_id,
        "project_id": project_id,
        "owner_decision": owner_decision_id,
        "authorization_id": authorization["id"],
        "authorization": authorization,
        "deliberation": deliberation_result,
    }
