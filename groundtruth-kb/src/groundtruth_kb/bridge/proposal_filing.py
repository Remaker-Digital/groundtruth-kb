"""Deterministic filing service for dispatchable bridge implementation proposals."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Any

from groundtruth_kb.bridge.proposal_autoload import (
    _dedupe,
    _normalize_rel_path,
    auto_spec_links,
    auto_target_paths_in_root_evidence,
    get_work_item_or_raise,
)
from groundtruth_kb.bridge.taxonomy import BridgeKind
from groundtruth_kb.bridge.versioned_files import status_from_bridge_file
from groundtruth_kb.db import KnowledgeDB

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


@dataclass(frozen=True)
class FilingRequest:
    wi_id: str
    slug: str
    target_paths: tuple[str, ...]
    project_id: str | None = None
    add_specs: tuple[str, ...] = ()
    scope_lines: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    simplification: tuple[str, ...] = ()
    summary: str | None = None
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
    preflight_results: tuple[PreflightResult, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class _ProjectState:
    project_id: str
    inputs: dict[str, Any]


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


def _resolve_project_state(
    db: KnowledgeDB,
    project_root: Path,
    request: FilingRequest,
) -> _ProjectState:
    """Read existing membership and project authorization without creating state."""
    work_item = get_work_item_or_raise(db, request.wi_id)
    if work_item.get("resolution_status") in {"resolved", "retired", "wont_fix", "not_a_defect", "verified"}:
        raise ProposalFilingError(f"Work item {request.wi_id} is complete or awaiting finalization; cannot start NEW")
    memberships = _active_memberships_for_work_item(db, request.wi_id)
    if len(memberships) != 1:
        raise ProposalFilingError(
            f"Work item {request.wi_id} requires exactly one active project membership; "
            f"found {len(memberships)}. Reconcile membership before filing."
        )
    membership = memberships[0]
    project_id = _require(membership.get("project_id"), "membership project")
    if request.project_id and request.project_id.strip() != project_id:
        raise ProposalFilingError(f"Work item {request.wi_id} belongs to {project_id}, not {request.project_id}")
    project = db.get_project(project_id)
    if project is None or project.get("status") != "active" or project.get("completed_at"):
        raise ProposalFilingError(f"Project {project_id} is missing, inactive, or complete")
    if project.get("authorization") != "authorized":
        raise ProposalFilingError(
            f"Project {project_id} authorization is {project.get('authorization')!r}; "
            "NEW proposal filing requires 'authorized'. The owner must change the project field."
        )
    test_id = str(work_item.get("source_test_id") or "").strip()
    test = db.get_test(test_id) if test_id else None
    if test is None or not str(test.get("test_file") or "").strip():
        raise ProposalFilingError(f"Work item {request.wi_id} requires a linked executable test before filing")
    bridge_inputs = _bridge_invalidation_inputs(project_root, request.slug)
    if bridge_inputs["latest_bridge_status"] != "ABSENT":
        raise ProposalFilingError(f"Bridge thread {request.slug} already exists; continue its existing chain")
    return _ProjectState(
        project_id=project_id,
        inputs=deepcopy(
            {
                "project": project,
                "membership": membership,
                "work_item": work_item,
                "bridge": bridge_inputs,
                "test": test,
            }
        ),
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
        "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001": "requires project, work item, and target path metadata.",
        "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001": "governs bounded project implementation authority.",
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
        "provenance": f"{wi_id}; {project_id}; generated by gt bridge file-implementation-proposal",
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
        "history_preservation": ("Git and formal history are preserved; bridge messages are disposable coordination."),
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
            "Independent proposal review and implementation verification remain mandatory.",
            "Only the declared in-root target paths are attributable to this implementation proposal.",
            "Credential, deployment, release, and unrelated work remain outside the proposed scope.",
        ],
        "fail_closed_conditions": [
            "Exactly one project membership and an authorized parent project are required for a NEW proposal.",
            "Target paths escape the project root or candidate/live preflights fail.",
            "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders.",
        ],
        "essential_context_preservation": (
            "The generated proposal retains project, work item, targets, specifications, "
            "scope, verification, acceptance, risk, rollback, and expected file changes."
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


def _derive_kb_mutation_in_scope(target_paths: tuple[str, ...]) -> bool:
    """Derive database mutation scope directly from the declared paths."""
    return any(PurePosixPath(path.replace("\\", "/")).name == KB_DB_FILENAME for path in target_paths)


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
    if result.returncode != 0:
        raise ProposalFilingError(f"Bridge compliance gate failed with exit {result.returncode}: {result.stderr}")
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
    scope_lines = request.scope_lines or (
        f"File a dispatchable NEW implementation proposal for `{request.wi_id}`.",
        "Preserve independent proposal review and implementation verification.",
        "Require one project membership, project authorization, valid targets, and passing preflights.",
    )
    acceptance = request.acceptance_criteria or (
        "A single command writes one `NEW` bridge proposal file through the governed bridge writer path.",
        "The proposal contains project linkage, inline-JSON target paths, concrete spec links and a spec-derived verification plan.",
        "Candidate and live bridge preflights pass or no bridge file is written.",
    )
    summary = request.summary or (
        f"File a governed implementation proposal for `{request.wi_id}` using deterministic project, "
        "authorization, target-path, and preflight wiring."
    )
    nonimpairment_section = render_nonimpairment_disposition(
        build_nonimpairment_disposition(
            wi_id=request.wi_id,
            project_id=project_state.project_id,
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
    kb_mutation_in_scope = _derive_kb_mutation_in_scope(request.target_paths)
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

recipient_role: loyal-opposition
Project: {project_state.project_id}
Work Item: {request.wi_id}

target_paths: {target_paths_json}
test_artifact_targets: {json.dumps([project_state.inputs["test"]["id"]])}

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: {str(kb_mutation_in_scope).lower()}

## Summary

{summary}

Work item description: {description or "_No work item description supplied._"}

## Claim

Prime Builder proposes a bounded implementation slice for `{request.wi_id}` and requests independent proposal review before implementation.

## Requirement Sufficiency

Existing requirements sufficient for the proposed scope, subject to independent review. The linked specifications and proposed target paths define the change. Membership and the parent project authorization field are read from existing database state. Review must establish requirement sufficiency; filing does not establish it.

## In-Root Placement Evidence

{auto_target_paths_in_root_evidence(project_root, request.target_paths)}

## Specification Links

{_format_spec_links(spec_links)}

## Simplification Accounting

{_format_bullets(simplification, empty="_No simplification accounting supplied._")}

## Proposed Scope

{_format_bullets(scope_lines, empty="_No proposed scope supplied._")}

{nonimpairment_section}

## Specification-Derived Verification Plan

{_format_verification_plan(spec_links, request.verification)}

## Acceptance Criteria

{_format_bullets(acceptance, empty="_No acceptance criteria supplied._")}

## Risks / Rollback

The proposal requires independent review before implementation. Filing checks project state, target paths, bridge slug collisions, author metadata, and preflight failures.

Reversal of committed source and test changes is forward work. Bridge messages are ephemeral coordination and are excluded from work-product commits.

## Files Expected To Change

{_format_bullets([f"`{path}`" for path in request.target_paths], empty="_No files supplied._")}

## Recommended Commit Type

`feat`
"""


def _project_root_from_module() -> Path:
    return Path(__file__).resolve().parents[4]


def _load_bridge_writer(project_root: Path) -> ModuleType:
    candidates = [
        project_root
        / ".harness-baseline-configuration"
        / "skills"
        / "gtkb-bridge-propose"
        / "helpers"
        / "write_bridge.py",
        _project_root_from_module()
        / ".harness-baseline-configuration"
        / "skills"
        / "gtkb-bridge-propose"
        / "helpers"
        / "write_bridge.py",
        project_root / ".harness-baseline-configuration" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py",
        _project_root_from_module()
        / ".harness-baseline-configuration"
        / "skills"
        / "bridge-propose"
        / "helpers"
        / "write_bridge.py",
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
    request = FilingRequest(
        **{
            **request.__dict__,
            "wi_id": _require(request.wi_id, "wi"),
            "slug": _require(request.slug, "slug"),
            "target_paths": normalized_targets,
        }
    )
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", request.slug):
        raise ProposalFilingError("Bridge slug must be lowercase kebab-case")
    spec_links = auto_spec_links(
        db,
        project_root,
        request.wi_id,
        "implementation",
        request.target_paths,
        request.add_specs,
    )
    project_state = _resolve_project_state(db, project_root, request)
    content = _build_content(db, project_root, request, project_state, spec_links=spec_links)

    preflight_results: list[PreflightResult] = []
    if run_candidate_preflights:
        preflight_results.extend(_run_candidate_preflights(project_root, content))
    preflight_results.append(_run_compliance_gate(project_root, request.slug, content))
    revalidated_state = _resolve_project_state(db, project_root, request)
    if project_state != revalidated_state:
        raise ProposalFilingError("Project, membership, work item, or bridge inputs changed before filing; retry")
    if request.dry_run:
        return FilingResult(
            bridge_path=None,
            content=content,
            project_id=project_state.project_id,
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
        preflight_results=tuple(preflight_results),
    )
