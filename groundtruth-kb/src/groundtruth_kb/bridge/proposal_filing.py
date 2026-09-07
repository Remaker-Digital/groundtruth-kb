"""Deterministic filing service for dispatchable bridge implementation proposals."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any

from groundtruth_kb.bridge.proposal_autoload import (
    _dedupe,
    _normalize_rel_path,
    auto_prior_delibs,
    auto_spec_links,
    auto_target_paths_in_root_evidence,
    get_work_item_or_raise,
)
from groundtruth_kb.bridge.taxonomy import BridgeKind
from groundtruth_kb.bridge.versioned_files import status_from_bridge_file
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.governance.project_authorization_operation_time import (
    classify_target,
    evaluator_sha256,
    load_operation_taxonomy,
    normalize_operation,
    normalized_envelope_hash,
)

APPROVED_SPEC_STATUSES = {"active", "specified", "implemented", "verified"}
CHANGED_BY = "prime-builder/codex"
FILING_OPERATION = "bridge_proposal_filing"
NONIMPAIRMENT_REQUIRED_FIELDS = (
    "applicability",
    "provenance",
    "canonical_authority",
    "primary_route",
    "before_behavior",
    "after_behavior",
    "self_descriptive_naming",
    "obsolete_guidance_disposition",
    "history_preservation",
    "baseline",
    "expected_result",
    "rollback",
    "hard_invariants",
    "fail_closed_conditions",
    "essential_context_preservation",
)


#: Artifact-head envelope emitted on every generated implementation proposal.
#: A Prime-authored ``NEW`` proposal is dispatched to Loyal Opposition for review,
#: so line 2 names the RECIPIENT role, not the author's.
#: Authority: ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001,
#: DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001 (WI-7326 defect 2).
PROPOSAL_RECIPIENT_INIT_MARKER = "::init gtkb lo"
PROPOSAL_ACTIVITY_MARKER = "::open build"

#: Knowledge-base filename used to derive ``kb_mutation_in_scope`` (WI-7326 defect 4).
KB_DB_FILENAME = "groundtruth.db"

#: Author audit metadata lines every bridge artifact must carry.
#: Authority: owner emergency audit directive 2026-05-19 (WI-7326 defect 3).
AUTHOR_METADATA_FIELDS: tuple[str, ...] = (
    "author_identity",
    "author_harness_id",
    "author_session_context_id",
    "author_model",
    "author_model_version",
    "author_model_configuration",
)


class ProposalFilingError(RuntimeError):
    """Raised when a dispatchable implementation proposal cannot be filed."""

    def __init__(self, message: str, *, decision: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.decision = decision


@dataclass(frozen=True)
class FilingRequest:
    wi_id: str
    slug: str
    target_paths: tuple[str, ...]
    project_id: str | None = None
    project_authorization_id: str | None = None
    owner_decision: str | None = None
    add_specs: tuple[str, ...] = ()
    scope_lines: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    cross_harness_dispositions: tuple[str, ...] = ()
    simplification: tuple[str, ...] = ()
    summary: str | None = None
    create_missing_state: bool = False
    dry_run: bool = False


@dataclass(frozen=True)
class PreflightResult:
    name: str
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class AuthorizationCandidateRank:
    project_authorization_id: str
    coverage: str
    included_work_item_count: int | None
    specificity_rank: tuple[int, int] | None
    status: str = "active"
    normalized_expiry: str | None = None
    currentness: str = "current"
    supersession_state: str = "current"
    disposition: str = "eligible"
    selected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_authorization_id": self.project_authorization_id,
            "coverage": self.coverage,
            "included_work_item_count": self.included_work_item_count,
            "specificity_rank": list(self.specificity_rank) if self.specificity_rank is not None else None,
            "status": self.status,
            "normalized_expiry": self.normalized_expiry,
            "currentness": self.currentness,
            "supersession_state": self.supersession_state,
            "disposition": self.disposition,
            "selected": self.selected,
        }


@dataclass(frozen=True)
class FilingResult:
    bridge_path: Path | None
    content: str
    project_id: str
    project_authorization_id: str
    project_authorization_candidates: tuple[AuthorizationCandidateRank, ...] = field(default_factory=tuple)
    authorization_decision: dict[str, Any] = field(default_factory=dict)
    preflight_results: tuple[PreflightResult, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class _ProjectState:
    project_id: str
    membership_created: bool


def _require(value: str | None, name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ProposalFilingError(f"{name} is required")
    return normalized


def _active_memberships_for_work_item(db: KnowledgeDB, wi_id: str) -> list[dict[str, Any]]:
    memberships: list[dict[str, Any]] = []
    for project in db.list_projects(include_terminal=True):
        project_id = str(project.get("id") or "")
        for membership in db.list_project_work_items(project_id):
            if membership.get("work_item_id") == wi_id:
                memberships.append(membership)
    return memberships


def _strict_authorization_list(row: dict[str, Any], field: str) -> list[str]:
    parsed_key = f"{field}_parsed"
    if parsed_key in row:
        value = row[parsed_key]
    elif f"_{field}_parsed" in row:
        value = row[f"_{field}_parsed"]
    else:
        value = row.get(field)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{field} is not valid JSON") from exc
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a JSON list of strings")
    return [item.strip() for item in value if item.strip()]


def _normalize_expiry(value: object, *, decision_time: datetime) -> tuple[str | None, str]:
    raw = str(value or "").strip()
    if not raw:
        return None, "current"
    candidate = f"{raw[:-1]}+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None, "malformed"
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None, "malformed"
    normalized = parsed.astimezone(UTC).replace(microsecond=0)
    rendered = normalized.isoformat().replace("+00:00", "Z")
    return rendered, "expired" if normalized <= decision_time else "current"


def _authorization_candidate_rank(
    authorization: dict[str, Any],
    wi_id: str,
    *,
    membership_active: bool,
    decision_time: datetime,
) -> AuthorizationCandidateRank:
    authorization_id = str(authorization.get("id") or "").strip()
    included = tuple(dict.fromkeys(_strict_authorization_list(authorization, "included_work_item_ids")))
    excluded = set(_strict_authorization_list(authorization, "excluded_work_item_ids"))
    if included == (wi_id,):
        coverage = "exact_singleton"
        rank: tuple[int, int] | None = (0, 1)
        included_count: int | None = 1
    elif included and wi_id in included:
        coverage = "explicit_list"
        rank = (1, len(included))
        included_count = len(included)
    elif not included and membership_active:
        coverage = "project_membership_fallback"
        rank = (2, 0)
        included_count = None
    else:
        coverage = "not_covering"
        rank = None
        included_count = len(included) if included else None

    disposition = "eligible" if rank is not None else "not_covering"
    if wi_id in excluded:
        disposition = "work_item_excluded"

    normalized_expiry, currentness = _normalize_expiry(authorization.get("expires_at"), decision_time=decision_time)
    superseded = bool(_strict_authorization_list(authorization, "superseded_by"))
    supersession_state = "superseded" if superseded else "current"
    if str(authorization.get("status") or "").strip().lower() != "active":
        currentness = "inactive"
    elif superseded:
        currentness = "superseded"

    return AuthorizationCandidateRank(
        project_authorization_id=authorization_id,
        coverage=coverage,
        included_work_item_count=included_count,
        specificity_rank=rank,
        status=str(authorization.get("status") or ""),
        normalized_expiry=normalized_expiry,
        currentness=currentness,
        supersession_state=supersession_state,
        disposition=disposition,
    )


def _authorization_envelope(authorization: dict[str, Any]) -> dict[str, Any]:
    envelope = dict(authorization)
    for field_name in (
        "allowed_mutation_classes",
        "forbidden_operations",
        "included_work_item_ids",
        "excluded_work_item_ids",
        "included_spec_ids",
        "excluded_spec_ids",
        "supersedes",
        "superseded_by",
    ):
        envelope[field_name] = _strict_authorization_list(authorization, field_name)
    return envelope


def _resolve_actor_context(project_root: Path) -> dict[str, str]:
    try:
        from scripts.bridge_author_metadata import load_author_metadata

        from groundtruth_kb.session.envelope import resolve_worker_role_provenance

        metadata = load_author_metadata(project_root)
        identity = str(metadata.get("author_identity") or "")
        harness_name = identity.rsplit("/", 1)[-1].strip().lower() if "/" in identity else ""
        session_context_id = str(metadata["author_session_context_id"])
        provenance = resolve_worker_role_provenance(
            project_root,
            current_session_id=session_context_id,
            harness_name=harness_name or None,
        )
    except Exception as exc:  # noqa: BLE001 - absence must fail closed with one stable reason
        raise ProposalFilingError(f"Unable to resolve filing session identity: {exc}") from exc
    role = str(provenance.get("role") or "").strip().lower()
    if role == "acting-prime-builder":
        role = "prime-builder"
    if role != "prime-builder":
        raise ProposalFilingError(
            f"Implementation-proposal filing requires prime-builder role, got {role or '<missing>'}"
        )
    context = {
        "session_context_id": session_context_id,
        "role": role,
    }
    # WI-7326 defect 3: the six audit-metadata values are already resolved here for
    # role validation. Carry them out so ``_build_content`` can emit them instead of
    # re-deriving (or, as before, omitting) them.
    for field_name in AUTHOR_METADATA_FIELDS:
        context[field_name] = str(metadata.get(field_name) or "")
    return context


def _bridge_invalidation_inputs(project_root: Path, slug: str) -> dict[str, Any]:
    pattern = re.compile(rf"^{re.escape(slug)}-(\d{{3}})\.md$")
    versions: list[tuple[int, Path]] = []
    bridge_dir = project_root / "bridge"
    if bridge_dir.is_dir():
        for path in bridge_dir.glob(f"{slug}-*.md"):
            match = pattern.fullmatch(path.name)
            if match is not None:
                versions.append((int(match.group(1)), path))
    if not versions:
        return {
            "bridge_document": slug,
            "latest_bridge_status": "ABSENT",
            "latest_bridge_version": 0,
            "reviewed_proposal_version": 1,
            "planned_bridge_status": "NEW",
            "planned_bridge_version": 1,
        }
    version, path = max(versions, key=lambda item: item[0])
    _status = status_from_bridge_file(path)
    return {
        "bridge_document": slug,
        "latest_bridge_status": _status or "UNREADABLE",
        "latest_bridge_version": version,
        "reviewed_proposal_version": 1,
        "planned_bridge_status": "NEW",
        "planned_bridge_version": 1,
    }


def _decision_payload(
    *,
    project_root: Path,
    request: FilingRequest,
    project_id: str,
    spec_links: list[str],
    actor: dict[str, str],
    invalidation_inputs: dict[str, Any],
    candidates: tuple[AuthorizationCandidateRank, ...],
    best_rank: tuple[int, int] | None,
    authorization: dict[str, Any] | None,
    allowed: bool,
    reason_code: str,
    reason: str,
    recovery: str,
    decision_time: datetime,
    envelope_decision: dict[str, Any] | None = None,
) -> dict[str, Any]:
    taxonomy = load_operation_taxonomy(project_root)
    envelope = _authorization_envelope(authorization) if authorization is not None else {}
    selected_id = str(authorization.get("id") or "") if authorization is not None else None
    payload: dict[str, Any] = {
        "schema_version": 1,
        "selector_mode": "explicit" if request.project_authorization_id else "automatic",
        "requested_project_authorization_id": request.project_authorization_id,
        "selected_project_authorization_id": selected_id,
        "project_authorization_candidates": [candidate.to_dict() for candidate in candidates],
        "fixed_best_rank": list(best_rank) if best_rank is not None else None,
        "fixed_best_cohort_ids": [
            candidate.project_authorization_id
            for candidate in candidates
            if best_rank is not None and candidate.specificity_rank == best_rank
        ],
        "authorization": {
            "id": selected_id,
            "version": authorization.get("version") if authorization is not None else None,
            "status": authorization.get("status") if authorization is not None else None,
            "normalized_expiry": next(
                (
                    candidate.normalized_expiry
                    for candidate in candidates
                    if candidate.project_authorization_id == selected_id
                ),
                None,
            ),
            "supersession_state": next(
                (
                    candidate.supersession_state
                    for candidate in candidates
                    if candidate.project_authorization_id == selected_id
                ),
                None,
            ),
            "owner_decision_deliberation_id": (
                authorization.get("owner_decision_deliberation_id") if authorization is not None else None
            ),
            "owner_decision_snapshot": (
                authorization.get("_owner_decision_snapshot") if authorization is not None else None
            ),
            "normalized_envelope_hash": (
                normalized_envelope_hash(envelope, taxonomy) if authorization is not None else None
            ),
            "included_work_item_ids": envelope.get("included_work_item_ids", []),
            "excluded_work_item_ids": envelope.get("excluded_work_item_ids", []),
            "included_spec_ids": envelope.get("included_spec_ids", []),
            "excluded_spec_ids": envelope.get("excluded_spec_ids", []),
            "allowed_mutation_classes": envelope.get("allowed_mutation_classes", []),
            "forbidden_operations": envelope.get("forbidden_operations", []),
        },
        "actor": actor,
        "request": {
            "project_id": project_id,
            "work_item_id": request.wi_id,
            "bridge_document": request.slug,
            "target_paths": list(request.target_paths),
            "linked_specifications": list(spec_links),
        },
        "invalidation_inputs": invalidation_inputs,
        "normalized_operation": normalize_operation(FILING_OPERATION, taxonomy),
        "classified_targets": [
            {"path": item.path, "mutation_class": item.mutation_class}
            for item in (classify_target(path, taxonomy) for path in request.target_paths)
        ],
        "evaluator_id": taxonomy.evaluator_id,
        "evaluator_version": taxonomy.evaluator_version,
        "evaluator_sha256": evaluator_sha256(),
        "taxonomy_version": taxonomy.taxonomy_version,
        "taxonomy_sha256": taxonomy.source_sha256,
        "decision_time": decision_time.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "allowed": allowed,
        "reason_code": reason_code,
        "reason": reason,
        "recovery": recovery,
    }
    if envelope_decision is not None:
        payload["envelope_decision"] = envelope_decision
    identity_material = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    payload["decision_id"] = "sha256:" + hashlib.sha256(identity_material).hexdigest()
    return payload


def _deny_from_decision(
    decision: dict[str, Any],
    *,
    reason_code: str,
    reason: str,
    recovery: str,
) -> dict[str, Any]:
    payload = json.loads(json.dumps(decision))
    payload.pop("decision_id", None)
    payload.update(
        {
            "allowed": False,
            "reason_code": reason_code,
            "reason": reason,
            "recovery": recovery,
        }
    )
    identity_material = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    payload["decision_id"] = "sha256:" + hashlib.sha256(identity_material).hexdigest()
    return payload


def _decision_invalidation_fingerprint(decision: dict[str, Any]) -> str:
    """Return a stable identity for authorization inputs, excluding evaluation time."""
    payload = json.loads(json.dumps(decision))
    payload.pop("decision_id", None)
    payload.pop("decision_time", None)
    envelope_decision = payload.get("envelope_decision")
    if isinstance(envelope_decision, dict):
        envelope_decision.pop("decision_time", None)
    material = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    return "sha256:" + hashlib.sha256(material).hexdigest()


def _require_owner_decision(db: KnowledgeDB, owner_decision: str | None) -> str:
    delib_id = _require(owner_decision, "owner_decision")
    deliberation = db.get_deliberation(delib_id)
    if deliberation is None:
        raise ProposalFilingError(f"Owner-decision deliberation not found: {delib_id}")
    if deliberation.get("source_type") != "owner_conversation":
        raise ProposalFilingError(f"Owner-decision deliberation is not owner_conversation evidence: {delib_id}")
    return delib_id


def _approved_existing_specs(db: KnowledgeDB, spec_ids: list[str]) -> list[str]:
    approved: list[str] = []
    for spec_id in spec_ids:
        row = db.get_spec(spec_id)
        if row is not None and row.get("status") in APPROVED_SPEC_STATUSES:
            approved.append(spec_id)
    return _dedupe(tuple(approved))


def _resolve_project_state(
    db: KnowledgeDB,
    project_root: Path,
    request: FilingRequest,
    *,
    spec_links: list[str],
    decision_time: datetime,
    allow_state_creation: bool = True,
) -> _ProjectState:
    work_item = get_work_item_or_raise(db, request.wi_id)
    memberships = _active_memberships_for_work_item(db, request.wi_id)

    project_id = request.project_id.strip() if request.project_id else None
    if not project_id and len(memberships) == 1:
        project_id = str(memberships[0].get("project_id") or "")
    elif not project_id and len(memberships) > 1:
        raise ProposalFilingError(f"Work item {request.wi_id} has multiple active project memberships; pass --project.")
    elif not project_id:
        compatibility_project = str(work_item.get("project_name") or "").strip()
        project_id = compatibility_project or None

    project_id = _require(project_id, "project")
    project = db.get_project(project_id)
    if project is None:
        raise ProposalFilingError(f"Project not found: {project_id}")
    membership = next((item for item in memberships if item.get("project_id") == project_id), None)
    actor = _resolve_actor_context(project_root)
    invalidation_inputs = {
        **_bridge_invalidation_inputs(project_root, request.slug),
        "project_version": project.get("version"),
        "project_status": project.get("status"),
        "project_completed_at": project.get("completed_at"),
        "membership_id": membership.get("id") if membership is not None else None,
        "membership_version": membership.get("version") if membership is not None else None,
        "membership_status": membership.get("status") if membership is not None else None,
    }

    def deny_state(code: str, reason: str, recovery: str) -> None:
        decision = _decision_payload(
            project_root=project_root,
            request=request,
            project_id=project_id,
            spec_links=spec_links,
            actor=actor,
            invalidation_inputs=invalidation_inputs,
            candidates=(),
            best_rank=None,
            authorization=None,
            allowed=False,
            reason_code=code,
            reason=reason,
            recovery=recovery,
            decision_time=decision_time,
        )
        raise ProposalFilingError(f"{reason} [{code}]", decision=decision)

    if project.get("status") != "active":
        deny_state(
            "project_not_active",
            f"Project {project_id} is not active",
            "Reactivate the project through the governed append-only lifecycle before filing.",
        )
    if invalidation_inputs["latest_bridge_status"] != "ABSENT":
        deny_state(
            "bridge_preimage_not_absent",
            f"Bridge thread {request.slug} already exists at version "
            f"{invalidation_inputs['latest_bridge_version']} with status "
            f"{invalidation_inputs['latest_bridge_status']}",
            "Choose a fresh bridge slug or continue the existing thread through its role-correct workflow.",
        )

    # WI-7657: no authorization is selected, evaluated, or created here.
    #
    # This block used to rank candidate authorization rows, deny with
    # no_current_covering_authorization when none covered the work item, and --
    # under --create-missing-state -- mint a bounded PAUTH row for the filing.
    # All three are gone. There is no authorization record to select, denying
    # on its absence refused lawful work, and minting one reinstated the object
    # being removed.
    #
    # What survives is the part that was always doing the real work: project
    # membership. Work-item scope IS membership, so an absent membership is
    # still a genuine blocker and is still creatable under owner-decision
    # evidence. Authorization is a field on the project row, set by owner
    # direction through gt projects update --activation-status, and gates
    # dispatch rather than filing.
    membership_created = False
    if membership is None:
        if not request.create_missing_state:
            deny_state(
                "no_active_project_membership",
                f"Work item {request.wi_id} has no active membership in {project_id}",
                "Add the membership with gt projects add-item, or pass --create-missing-state "
                "with owner-decision evidence.",
            )
        try:
            owner_decision = _require_owner_decision(db, request.owner_decision)
        except ProposalFilingError as exc:
            deny_state(
                "owner_decision_unresolvable",
                str(exc),
                "Supply a resolvable owner_conversation deliberation id before creating membership state.",
            )
        if not request.dry_run and allow_state_creation:
            db.link_project_work_item(
                project_id,
                request.wi_id,
                CHANGED_BY,
                f"gt bridge file-implementation-proposal membership creation approved by {owner_decision}",
                source="gt bridge file-implementation-proposal",
            )
            membership_created = True

    return _ProjectState(
        project_id=project_id,
        membership_created=membership_created,
    )


def _validate_target_paths(project_root: Path, target_paths: tuple[str, ...]) -> tuple[str, ...]:
    if not target_paths:
        raise ProposalFilingError("At least one --target-path is required")
    root = project_root.resolve()
    normalized: list[str] = []
    for raw_path in target_paths:
        rel_path = _normalize_rel_path(raw_path)
        if not rel_path:
            raise ProposalFilingError("Empty target path is not allowed")
        candidate = (root / rel_path).resolve()
        if not candidate.is_relative_to(root):
            raise ProposalFilingError(f"Target path is outside the project root: {raw_path}")
        if rel_path == "applications/Agent_Red" or rel_path.startswith("applications/Agent_Red/"):
            raise ProposalFilingError("Agent Red targets are out of scope for this platform bridge filing command.")
        normalized.append(rel_path)
    return tuple(_dedupe(tuple(normalized)))


def _validate_cross_harness_dispositions(entries: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    seen_keys: set[str] = set()
    for entry in entries:
        if "=" not in entry:
            raise ProposalFilingError("--cross-harness-disposition entries must use HARNESS_OR_SURFACE=DISPOSITION")
        key, disposition = (part.strip() for part in entry.split("=", 1))
        if not key or not disposition:
            raise ProposalFilingError(
                "--cross-harness-disposition requires a non-empty harness/surface and disposition"
            )
        if any(character in key or character in disposition for character in "\r\n"):
            raise ProposalFilingError("--cross-harness-disposition entries must be single-line values")
        normalized_key = key.casefold()
        if normalized_key in seen_keys:
            raise ProposalFilingError(f"Duplicate --cross-harness-disposition key: {key}")
        seen_keys.add(normalized_key)
        normalized.append(f"{key}={disposition}")
    return tuple(normalized)


def _format_bullets(values: list[str] | tuple[str, ...], *, empty: str) -> str:
    if not values:
        return f"- {empty}"
    return "\n".join(f"- {value}" for value in values)


def _format_spec_links(spec_ids: list[str]) -> str:
    reasons = {
        "GOV-FILE-BRIDGE-AUTHORITY-001": "preserves role-correct bridge authority and numbered-file filing.",
        "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001": "requires concrete specification links in implementation proposals.",
        "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001": "requires spec-derived verification evidence before VERIFIED.",
        "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001": "requires project authorization, project, work item, and target path metadata.",
        "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001": "governs bounded project implementation authority.",
        "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001": "requires bounded PAUTH envelopes for new authorization state.",
        "ADR-ISOLATION-APPLICATION-PLACEMENT-001": "keeps this platform command out of adopter application scope.",
    }
    return "\n".join(
        f"- `{spec_id}` - {reasons.get(spec_id, 'auto-linked governing or work-item specification.')}"
        for spec_id in spec_ids
    )


def _format_verification_plan(spec_ids: list[str], explicit: tuple[str, ...]) -> str:
    explicit_by_spec: dict[str, str] = {}
    for item in explicit:
        if "=" not in item:
            raise ProposalFilingError("--verification entries must use SPEC_ID=verification text")
        spec_id, verification = item.split("=", 1)
        explicit_by_spec[spec_id.strip()] = verification.strip()

    rows = ["| Spec | Verification |", "| --- | --- |"]
    for spec_id in spec_ids:
        verification = explicit_by_spec.get(
            spec_id,
            "Run candidate and live bridge applicability preflights; implementation report must add targeted tests.",
        )
        rows.append(f"| `{spec_id}` | {verification} |")
    return "\n".join(rows)


def _format_cross_harness_dispositions(entries: tuple[str, ...]) -> str:
    return "\n".join(f"- **{key}**: {disposition}" for key, disposition in (entry.split("=", 1) for entry in entries))


def draft_nonimpairment_disposition() -> dict[str, Any]:
    """Return the complete, deliberately non-fileable draft schema."""
    return {
        "schema_version": 1,
        **{field: "TODO" for field in NONIMPAIRMENT_REQUIRED_FIELDS},
    }


def build_nonimpairment_disposition(
    *,
    wi_id: str,
    project_id: str,
    project_authorization_id: str,
    target_paths: tuple[str, ...],
    summary: str,
    description: str,
    scope_lines: tuple[str, ...],
    acceptance_criteria: tuple[str, ...],
    spec_links: list[str],
) -> dict[str, Any]:
    """Build a concrete request-derived non-impairment disposition."""
    return {
        "schema_version": 1,
        "applicability": "applicable",
        "provenance": f"{wi_id}; {project_authorization_id}; generated by gt bridge file-implementation-proposal",
        "canonical_authority": ("GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators"),
        "primary_route": "gt bridge file-implementation-proposal",
        "before_behavior": description or f"{wi_id} has no implemented behavior yet; this proposal defines the slice.",
        "after_behavior": summary,
        "self_descriptive_naming": (
            "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect."
        ),
        "obsolete_guidance_disposition": (
            "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance."
        ),
        "history_preservation": (
            "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts."
        ),
        "baseline": {
            "work_item": wi_id,
            "project": project_id,
            "target_paths": list(target_paths),
            "linked_specifications": list(spec_links),
        },
        "expected_result": {
            "summary": summary,
            "scope": list(scope_lines),
            "acceptance_criteria": list(acceptance_criteria),
        },
        "rollback": {
            "instructions": "Revert only the approved source and test implementation targets under separate authority.",
            "verification": "Rerun the proposal's specification-derived tests and bridge preflights.",
        },
        "hard_invariants": [
            "Bridge review, implementation-start, and independent verification gates remain mandatory.",
            "Only the declared in-root target paths are attributable to this implementation proposal.",
            "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority.",
        ],
        "fail_closed_conditions": [
            "Project membership or active PAUTH coverage is missing.",
            "Target paths escape the project root or candidate/live preflights fail.",
            "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders.",
        ],
        "essential_context_preservation": (
            "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, "
            "owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
        ),
    }


def render_nonimpairment_disposition(disposition: dict[str, Any]) -> str:
    return (
        "## Intuitiveness / Non-Impairment Disposition\n\n"
        "```json\n"
        f"{json.dumps(disposition, ensure_ascii=True, indent=2)}\n"
        "```"
    )


def _session_scratch_dirname() -> str:
    """Session-scoped scratch subdirectory name per Compact Guidance section 17."""
    for env_var in (
        "GTKB_SESSION_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CODEX_THREAD_ID",
        "CURSOR_CONVERSATION_ID",
        "GOOSE_SESSION_ID",
        "ANTIGRAVITY_SESSION_ID",
    ):
        value = str(os.environ.get(env_var) or "").strip()
        if value:
            return re.sub(r"[^A-Za-z0-9._-]", "-", value)[:120]
    return "proposal-filing-no-session"


def _derive_kb_mutation_in_scope(
    target_paths: tuple[str, ...],
    authorization_decision: dict[str, Any],
) -> bool:
    """Derive ``kb_mutation_in_scope`` from declared targets and cross-check the decision.

    WI-7326 defect 4. The flag was previously hard-coded ``false``. It is now derived
    from ``target_paths`` and cross-checked against the classified mutation targets the
    authorization evaluator already produced; a disagreement fails closed rather than
    emitting a flag the decision does not corroborate.
    """
    kb_targets = tuple(
        path for path in target_paths if PurePosixPath(str(path).replace("\\", "/")).name == KB_DB_FILENAME
    )
    if not kb_targets:
        return False
    classified = {str(entry.get("path")) for entry in (authorization_decision.get("classified_targets") or ())}
    uncorroborated = [path for path in kb_targets if path not in classified]
    if uncorroborated:
        raise ProposalFilingError(
            "kb_mutation_in_scope derivation disagrees with the authorization decision: "
            f"{uncorroborated} declared as targets but absent from classified_targets. "
            "Re-run filing from a fresh authorization snapshot."
        )
    return True


def _compliance_gate_script(project_root: Path) -> Path:
    """Canonical baseline bridge compliance gate. Projections are never invoked here."""
    return project_root / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"


def _run_compliance_gate(project_root: Path, slug: str, content: str) -> PreflightResult:
    """Evaluate the real baseline compliance gate against generated content.

    WI-7326 defect 5. The gate previously ran only inside the bridge writer, so the
    ``--dry-run`` path evaluated strictly fewer gates than the write it previewed and
    reported success for content the write rejected. Both paths now call this, so the
    two verdicts cannot disagree for identical inputs.

    Absence of the baseline gate in ``project_root`` is reported as ``not_evaluated``
    rather than raised. Parity is the contract: where no baseline gate exists, the
    writer path is not gated either, so gating only the preview would make the two
    paths disagree in the opposite direction. This does not modify any gate's deny
    logic; a gate that is present is always evaluated and always fails closed.
    """
    script = _compliance_gate_script(project_root)
    if not script.is_file():
        return PreflightResult(
            name="compliance_gate",
            returncode=0,
            stdout="not_evaluated: no baseline bridge compliance gate in this project root",
            stderr="",
        )
    payload = json.dumps(
        {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(project_root / "bridge" / f"{slug}-001.md"),
                "content": content,
            },
        }
    )
    result = subprocess.run(
        [sys.executable, str(script)],
        input=payload,
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    raw = (result.stdout or "").strip()
    gate_result = PreflightResult(
        name="compliance_gate", returncode=result.returncode, stdout=raw, stderr=result.stderr or ""
    )
    if not raw:
        return gate_result
    try:
        decision = json.loads(raw).get("hookSpecificOutput") or {}
    except json.JSONDecodeError as exc:
        raise ProposalFilingError(f"Bridge compliance gate emitted unparseable output: {raw[:400]}") from exc
    verdict = str(decision.get("permissionDecision") or "").strip().lower()
    if verdict in {"deny", "ask"}:
        raise ProposalFilingError(
            f"Bridge compliance gate returned {verdict}: {decision.get('permissionDecisionReason') or ''}"
        )
    return gate_result


def _build_content(
    db: KnowledgeDB,
    project_root: Path,
    request: FilingRequest,
    project_state: _ProjectState,
    *,
    spec_links: list[str],
) -> str:
    work_item = get_work_item_or_raise(db, request.wi_id)
    title = str(work_item.get("title") or request.wi_id)
    description = str(work_item.get("description") or "").strip()
    target_paths_json = json.dumps(list(request.target_paths), ensure_ascii=True)
    prior_delibs = auto_prior_delibs(db, request.wi_id, request.slug)
    owner_decisions = []
    if request.owner_decision:
        owner_decisions.append(f"`{request.owner_decision}` - owner-decision evidence supplied to this command.")
    owner_decisions.append(
        f"`{project_state.project_authorization_id}` - active project authorization covering `{request.wi_id}`."
    )
    scope_lines = request.scope_lines or (
        f"File a dispatchable NEW implementation proposal for `{request.wi_id}`.",
        "Preserve bridge review and implementation-start gates; this command does not bypass Loyal Opposition.",
        "Fail closed on missing project membership, missing PAUTH coverage, preflight gaps, or invalid target paths.",
    )
    acceptance = request.acceptance_criteria or (
        "A single command writes one `NEW` bridge proposal file through the governed bridge writer path.",
        "The proposal contains project linkage, inline-JSON target paths, concrete spec links, prior deliberations, owner-decision evidence, and a spec-derived verification plan.",
        "Candidate and live bridge preflights pass or no bridge file is written.",
    )
    summary = request.summary or (
        f"File a governed implementation proposal for `{request.wi_id}` using deterministic project, "
        "authorization, target-path, and preflight wiring."
    )
    cross_harness_section = (
        f"## Cross-Harness Disposition\n\n{_format_cross_harness_dispositions(request.cross_harness_dispositions)}\n\n"
        if request.cross_harness_dispositions
        else ""
    )
    nonimpairment_section = render_nonimpairment_disposition(
        build_nonimpairment_disposition(
            wi_id=request.wi_id,
            project_id=project_state.project_id,
            project_authorization_id=project_state.project_authorization_id,
            target_paths=request.target_paths,
            summary=summary,
            description=description,
            scope_lines=scope_lines,
            acceptance_criteria=acceptance,
            spec_links=spec_links,
        )
    )
    actor = _resolve_actor_context(project_root)
    author_metadata_block = chr(10).join(f"{name}: {actor.get(name, '')}" for name in AUTHOR_METADATA_FIELDS)
    kb_mutation_in_scope = _derive_kb_mutation_in_scope(request.target_paths, project_state.authorization_decision)
    simplification = request.simplification or (
        "No net reduction is claimed: this change adds capability without removing "
        "artifacts, lines, state locations, or concepts. Supply `--simplification` to "
        "state what actually gets smaller.",
    )
    date = f"{datetime.now(UTC).date().isoformat()} UTC"
    return f"""NEW
{PROPOSAL_RECIPIENT_INIT_MARKER}
{PROPOSAL_ACTIVITY_MARKER}

# Implementation Proposal - {title}

bridge_kind: {BridgeKind.PRIME_PROPOSAL.value}
Document: {request.slug}
Version: 001
Date: {date}

{author_metadata_block}

Project Authorization: {project_state.project_authorization_id}
Project Authorization Candidates: {json.dumps([candidate.to_dict() for candidate in project_state.project_authorization_candidates], ensure_ascii=True, separators=(",", ":"))}
Project Authorization Decision: {json.dumps(project_state.authorization_decision, ensure_ascii=True, separators=(",", ":"), sort_keys=True)}
Project: {project_state.project_id}
Work Item: {request.wi_id}
Latest Bridge Status: {project_state.authorization_decision["invalidation_inputs"]["latest_bridge_status"]}
Reviewed Proposal Version: {project_state.authorization_decision["invalidation_inputs"]["reviewed_proposal_version"]}

target_paths: {target_paths_json}

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: {str(kb_mutation_in_scope).lower()}

## Summary

{summary}

Work item description: {description or "_No work item description supplied._"}

## Claim

Prime Builder proposes a bounded implementation slice for `{request.wi_id}` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

{auto_target_paths_in_root_evidence(project_root, request.target_paths)}

## Specification Links

{_format_spec_links(spec_links)}

## Prior Deliberations

{_format_bullets(prior_delibs, empty="_No prior deliberations auto-loaded; author must confirm before review._")}

## Owner Decisions / Input

{_format_bullets(owner_decisions, empty="_No owner-decision evidence required for existing active authorization reuse._")}

## Simplification Accounting

{_format_bullets(simplification, empty="_No simplification accounting supplied._")}

## Proposed Scope

{_format_bullets(scope_lines, empty="_No proposed scope supplied._")}

{cross_harness_section}{nonimpairment_section}

## Specification-Derived Verification Plan

{_format_verification_plan(spec_links, request.verification)}

## Acceptance Criteria

{_format_bullets(acceptance, empty="_No acceptance criteria supplied._")}

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

{_format_bullets([f"`{path}`" for path in request.target_paths], empty="_No files supplied._")}

## Recommended Commit Type

`feat`
"""


def _project_root_from_module() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_bridge_writer(project_root: Path) -> ModuleType:
    candidates = [
        project_root / ".claude" / "skills" / "gtkb-bridge-propose" / "helpers" / "write_bridge.py",
        _project_root_from_module() / ".claude" / "skills" / "gtkb-bridge-propose" / "helpers" / "write_bridge.py",
        project_root / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py",
        _project_root_from_module() / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py",
    ]
    helper_path = next((path for path in candidates if path.is_file()), None)
    if helper_path is None:
        raise ProposalFilingError("Governed bridge writer helper not found")
    spec = importlib.util.spec_from_file_location("gtkb_bridge_proposal_writer", helper_path)
    if spec is None or spec.loader is None:
        raise ProposalFilingError(f"Unable to load bridge writer helper: {helper_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _run_preflight_command(
    project_root: Path,
    *,
    name: str,
    content_file: Path | None = None,
    bridge_id: str | None = None,
) -> PreflightResult:
    script = {
        "applicability": project_root / "scripts" / "bridge_applicability_preflight.py",
        "adr_dcl": project_root / "scripts" / "adr_dcl_clause_preflight.py",
    }[name]
    argv = [sys.executable, str(script)]
    if content_file is not None:
        argv.extend(["--content-file", str(content_file)])
    if bridge_id is not None:
        argv.extend(["--bridge-id", bridge_id])
    result = subprocess.run(argv, cwd=project_root, capture_output=True, text=True, check=False)
    preflight = PreflightResult(name=name, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    if result.returncode != 0:
        raise ProposalFilingError(
            f"{name} preflight failed with exit {result.returncode}: {result.stdout}{result.stderr}"
        )
    return preflight


def _run_candidate_preflights(project_root: Path, content: str) -> tuple[PreflightResult, ...]:
    # WI-7326 defect 6: ``.gtkb-state`` is a forbidden directory. Candidate-preflight
    # scratch belongs in the canonical in-root scratchpad, in a session-scoped subdirectory.
    scratch_root = project_root / "scratchpad" / _session_scratch_dirname() / "proposal-filing-preflight"
    scratch_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="candidate-", dir=scratch_root) as tmp:
        content_file = Path(tmp) / "proposal.md"
        content_file.write_text(content, encoding="utf-8")
        return (
            _run_preflight_command(project_root, name="applicability", content_file=content_file),
            _run_preflight_command(project_root, name="adr_dcl", content_file=content_file),
        )


def _run_live_preflights(project_root: Path, bridge_id: str) -> tuple[PreflightResult, ...]:
    return (
        _run_preflight_command(project_root, name="applicability", bridge_id=bridge_id),
        _run_preflight_command(project_root, name="adr_dcl", bridge_id=bridge_id),
    )


def file_implementation_proposal(
    db: KnowledgeDB,
    project_root: Path,
    request: FilingRequest,
    *,
    writer: Any | None = None,
    run_candidate_preflights: bool = True,
    run_live_preflights: bool = True,
) -> FilingResult:
    """File a dispatchable ``NEW`` implementation proposal through the bridge writer."""
    normalized_targets = _validate_target_paths(project_root, request.target_paths)
    normalized_dispositions = _validate_cross_harness_dispositions(request.cross_harness_dispositions)
    request = FilingRequest(
        **{
            **request.__dict__,
            "wi_id": _require(request.wi_id, "wi"),
            "slug": _require(request.slug, "slug"),
            "target_paths": normalized_targets,
            "cross_harness_dispositions": normalized_dispositions,
        }
    )
    spec_links = auto_spec_links(
        db,
        project_root,
        request.wi_id,
        "implementation",
        request.target_paths,
        request.add_specs,
    )
    decision_time = datetime.now(UTC).replace(microsecond=0)
    project_state = _resolve_project_state(
        db,
        project_root,
        request,
        spec_links=spec_links,
        decision_time=decision_time,
    )
    content = _build_content(db, project_root, request, project_state, spec_links=spec_links)

    preflight_results: list[PreflightResult] = []
    if run_candidate_preflights:
        preflight_results.extend(_run_candidate_preflights(project_root, content))
    revalidation_time = datetime.now(UTC).replace(microsecond=0)
    revalidated_state = _resolve_project_state(
        db,
        project_root,
        request,
        spec_links=spec_links,
        decision_time=revalidation_time,
        allow_state_creation=False,
    )
    initial_fingerprint = _decision_invalidation_fingerprint(project_state.authorization_decision)
    revalidated_fingerprint = _decision_invalidation_fingerprint(revalidated_state.authorization_decision)
    if initial_fingerprint != revalidated_fingerprint:
        denied = _deny_from_decision(
            revalidated_state.authorization_decision,
            reason_code="authorization_inputs_changed_before_filing",
            reason="Project authorization or bridge invalidation inputs changed after candidate preflight",
            recovery="Restart proposal filing from a fresh snapshot; do not reuse the stale authorization decision.",
        )
        raise ProposalFilingError("Authorization inputs changed before bridge filing", decision=denied)
    # WI-7326 defect 5: evaluate the same gate the writer evaluates, on both paths, so a
    # dry-run verdict and a write verdict cannot disagree for identical inputs.
    preflight_results.append(_run_compliance_gate(project_root, request.slug, content))
    if request.dry_run:
        return FilingResult(
            bridge_path=None,
            content=content,
            project_id=project_state.project_id,
            project_authorization_id=project_state.project_authorization_id,
            project_authorization_candidates=project_state.project_authorization_candidates,
            authorization_decision=project_state.authorization_decision,
            preflight_results=tuple(preflight_results),
        )

    bridge_writer = writer or _load_bridge_writer(project_root)
    try:
        bridge_path = bridge_writer.propose_bridge_codex_non_bypass(
            request.slug,
            content,
            version=1,
            status="NEW",
            bridge_dir=project_root / "bridge",
            pre_populate_prior_deliberations=False,
        )
    except Exception as exc:  # noqa: BLE001 - normalize helper exceptions for CLI callers
        raise ProposalFilingError(str(exc)) from exc

    if run_live_preflights:
        preflight_results.extend(_run_live_preflights(project_root, request.slug))
    return FilingResult(
        bridge_path=Path(bridge_path),
        content=content,
        project_id=project_state.project_id,
        project_authorization_id=project_state.project_authorization_id,
        project_authorization_candidates=project_state.project_authorization_candidates,
        authorization_decision=project_state.authorization_decision,
        preflight_results=tuple(preflight_results),
    )
