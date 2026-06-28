"""Deterministic filing service for dispatchable bridge implementation proposals."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

from groundtruth_kb.bridge.proposal_autoload import (
    _dedupe,
    _normalize_rel_path,
    _parsed_list,
    auto_prior_delibs,
    auto_spec_links,
    auto_target_paths_in_root_evidence,
    get_work_item_or_raise,
)
from groundtruth_kb.bridge.taxonomy import BridgeKind
from groundtruth_kb.db import KnowledgeDB

APPROVED_SPEC_STATUSES = {"specified", "implemented", "verified"}
CHANGED_BY = "prime-builder/codex"


class ProposalFilingError(RuntimeError):
    """Raised when a dispatchable implementation proposal cannot be filed."""


@dataclass(frozen=True)
class FilingRequest:
    wi_id: str
    slug: str
    target_paths: tuple[str, ...]
    project_id: str | None = None
    owner_decision: str | None = None
    add_specs: tuple[str, ...] = ()
    scope_lines: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
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
class FilingResult:
    bridge_path: Path | None
    content: str
    project_id: str
    project_authorization_id: str
    preflight_results: tuple[PreflightResult, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class _ProjectState:
    project_id: str
    project_authorization_id: str
    membership_created: bool
    authorization_created: bool


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


def _authorization_covers_work_item(authorization: dict[str, Any], wi_id: str) -> bool:
    included = _parsed_list(authorization, "included_work_item_ids")
    excluded = _parsed_list(authorization, "excluded_work_item_ids")
    return wi_id not in excluded and (not included or wi_id in included)


def _active_authorization_for_work_item(
    db: KnowledgeDB,
    *,
    project_id: str,
    wi_id: str,
) -> dict[str, Any] | None:
    for authorization in db.list_project_authorizations(project_id, status="active"):
        if _authorization_covers_work_item(authorization, wi_id):
            return authorization
    return None


def _require_owner_decision(db: KnowledgeDB, owner_decision: str | None) -> str:
    delib_id = _require(owner_decision, "owner_decision")
    if db.get_deliberation(delib_id) is None:
        raise ProposalFilingError(f"Owner-decision deliberation not found: {delib_id}")
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
    request: FilingRequest,
    *,
    spec_links: list[str],
) -> _ProjectState:
    work_item = get_work_item_or_raise(db, request.wi_id)
    memberships = _active_memberships_for_work_item(db, request.wi_id)

    project_id = request.project_id.strip() if request.project_id else None
    if project_id:
        if db.get_project(project_id) is None:
            raise ProposalFilingError(f"Project not found: {project_id}")
    elif len(memberships) == 1:
        project_id = str(memberships[0].get("project_id") or "")
    elif len(memberships) > 1:
        raise ProposalFilingError(f"Work item {request.wi_id} has multiple active project memberships; pass --project.")
    else:
        compatibility_project = str(work_item.get("project_name") or "").strip()
        project_id = compatibility_project or None

    project_id = _require(project_id, "project")
    membership = next((item for item in memberships if item.get("project_id") == project_id), None)
    membership_created = False
    if membership is None:
        if not request.create_missing_state:
            raise ProposalFilingError(
                f"Work item {request.wi_id} has no active membership in {project_id}; "
                "pass --create-missing-state with --owner-decision to create it."
            )
        owner_decision = _require_owner_decision(db, request.owner_decision)
        db.link_project_work_item(
            project_id,
            request.wi_id,
            CHANGED_BY,
            f"gt bridge file-implementation-proposal membership creation approved by {owner_decision}",
            source="gt bridge file-implementation-proposal",
        )
        membership_created = True

    authorization = _active_authorization_for_work_item(db, project_id=project_id, wi_id=request.wi_id)
    authorization_created = False
    if authorization is None:
        if not request.create_missing_state:
            raise ProposalFilingError(
                f"No active project authorization covers {request.wi_id} in {project_id}; "
                "pass --create-missing-state with --owner-decision to create a bounded PAUTH."
            )
        owner_decision = _require_owner_decision(db, request.owner_decision)
        approved_specs = _approved_existing_specs(db, spec_links)
        if not approved_specs:
            raise ProposalFilingError(
                "Cannot create an active project authorization: no auto-linked or added specs "
                "resolve to an approved specification."
            )
        authorization = db.insert_project_authorization(
            project_id,
            f"{request.wi_id} implementation proposal filing",
            owner_decision,
            f"Bounded implementation-proposal filing authorization for {request.wi_id}.",
            CHANGED_BY,
            f"gt bridge file-implementation-proposal PAUTH creation approved by {owner_decision}",
            included_work_item_ids=[request.wi_id],
            included_spec_ids=approved_specs,
            allowed_mutation_classes=["bridge", "metadata"],
        )
        authorization_created = True

    if authorization is None:
        raise ProposalFilingError("Project authorization insert did not return a current row")

    return _ProjectState(
        project_id=project_id,
        project_authorization_id=str(authorization.get("id") or ""),
        membership_created=membership_created,
        authorization_created=authorization_created,
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
    date = f"{datetime.now(UTC).date().isoformat()} UTC"
    return f"""NEW

# Implementation Proposal - {title}

bridge_kind: {BridgeKind.PRIME_PROPOSAL.value}
Document: {request.slug}
Version: 001
Date: {date}

Project Authorization: {project_state.project_authorization_id}
Project: {project_state.project_id}
Work Item: {request.wi_id}

target_paths: {target_paths_json}

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

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

## Proposed Scope

{_format_bullets(scope_lines, empty="_No proposed scope supplied._")}

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
    scratch_root = project_root / ".gtkb-state" / "proposal-filing-preflight"
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
    request = FilingRequest(
        **{
            **request.__dict__,
            "wi_id": _require(request.wi_id, "wi"),
            "slug": _require(request.slug, "slug"),
            "target_paths": normalized_targets,
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
    project_state = _resolve_project_state(db, request, spec_links=spec_links)
    content = _build_content(db, project_root, request, project_state, spec_links=spec_links)

    preflight_results: list[PreflightResult] = []
    if run_candidate_preflights:
        preflight_results.extend(_run_candidate_preflights(project_root, content))
    if request.dry_run:
        return FilingResult(
            bridge_path=None,
            content=content,
            project_id=project_state.project_id,
            project_authorization_id=project_state.project_authorization_id,
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
        preflight_results=tuple(preflight_results),
    )
