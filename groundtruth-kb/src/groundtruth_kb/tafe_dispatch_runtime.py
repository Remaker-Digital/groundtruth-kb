"""TAFE ``gt flow dispatch tick`` / ``dispatch health`` evaluation runtime (WI-4499).

A read / compute / report layer over the VERIFIED WI-4498 dispatch policy engine
(``groundtruth_kb.tafe_dispatch_policy``). It answers "what *would* be dispatched
for each eligible unclaimed stage" and "how dispatch-ready is the system" without
spawning harnesses, mutating ``stage_leases``, writing the bridge index, or
persisting telemetry. Every report carries ``mutated == False``.

Specification coverage:
- ``SPEC-TAFE-R5`` (need-driven activation): ``evaluate_dispatch_tick`` evaluates
  actual dispatch need from current flow/stage state plus capability snapshots;
  it does not blindly initiate sessions.
- ``SPEC-TAFE-R4`` (policy engine): each eligible stage is routed through
  ``select_dispatch_target`` for hard eligibility gates + calibrated ranking.
- ``SPEC-TAFE-R2`` (single claim): only ``claim_status == 'unclaimed'`` stages are
  dispatch candidates; lease state is read, never mutated.
- ``SPEC-TAFE-R6`` (decision evidence): reports surface per-stage decision evidence
  for later telemetry persistence (not persisted in this slice).

Mapping assumptions (WI-4499; documented for Loyal Opposition verification).
Because the WI-4498 ``DispatchNeed`` / ``DispatchCandidate`` carry fields that are
not first-class columns on the TAFE runtime tables, this slice sources them as
follows, defaulting safely (fail-closed) when absent:

DispatchNeed (per eligible stage instance):
- ``required_role``            <- ``stage_instances.required_role`` (column).
- ``subject_scope``            <- the owning flow instance's ``subject_type``.
- ``required_capabilities``    <- ``stage.metadata['required_capabilities']`` (list), else ``()``.
- ``artifact_author_session_id`` <- ``stage.metadata['artifact_author_session_id']``, else ``None``.
- ``owner_gate_blocked``       <- ``bool(stage.metadata['owner_gate_blocked'])``, else ``False``.
- ``requires_workspace``       <- ``bool(stage.metadata.get('requires_workspace', True))``.
- ``stage_id`` / ``flow_instance_id`` <- columns.

DispatchCandidate (per active capability snapshot):
- ``harness_id`` / ``role`` / ``health_status`` / ``reviewer_precedence`` /
  ``model_identifier`` / ``capabilities`` <- snapshot columns.
- ``subject_scope``           <- ``snapshot.subject_scope`` or ``'all'`` when null.
- ``workspace_available``     <- truthy interpretation of ``snapshot.workspace_availability``.
- ``active_session_id``       <- ``snapshot.metadata['active_session_id']``, else ``None``
  (a ``None`` candidate session fails the review-independence gate closed; candidates
  must advertise an active session in snapshot metadata to be dispatch-eligible).
- ``stage_lease_available``   <- ``True`` for every candidate of an unclaimed stage
  (claimed/terminal stages are excluded before evaluation, per R2).
- ``cost``                    <- ``snapshot.metadata['cost']``, else ``None``.

Source: bridge thread ``gtkb-tafe-dispatch-tick-health`` (GO at ``-004``);
``PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`` / ``WI-4499``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from groundtruth_kb.tafe_dispatch_policy import (
    DispatchCandidate,
    DispatchNeed,
    select_dispatch_target,
)

# Stage statuses that are terminal and therefore never dispatch candidates.
TERMINAL_STAGE_STATUSES = frozenset({"completed", "cancelled", "failed", "skipped"})
# claim_status value that marks a stage as available for dispatch (SPEC-TAFE-R2).
UNCLAIMED_CLAIM_STATUS = "unclaimed"
# Only currently-active capability snapshots are dispatch candidates.
ACTIVE_SNAPSHOT_STATUS = "active"
# Truthy interpretations of the snapshot ``workspace_availability`` text column.
_WORKSPACE_AVAILABLE_TOKENS = frozenset({"available", "yes", "true", "ready", "ok", "1"})


class _FlowService(Protocol):
    """The read-only slice of the TAFE flow service this runtime depends on."""

    def list_stage_instances(
        self, *, flow_instance_id: str | None = ..., status: str | None = ...
    ) -> list[dict[str, Any]]: ...

    def get_flow_instance(self, flow_instance_id: str) -> dict[str, Any] | None: ...

    def list_capability_snapshots(
        self,
        *,
        harness_id: str | None = ...,
        health_status: str | None = ...,
        status: str | None = ...,
    ) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class StageDispatchDecision:
    """The evaluated (non-mutating) dispatch decision for a single stage."""

    stage_instance_id: str
    stage_id: str
    flow_instance_id: str
    required_role: str
    subject_scope: str
    selected_harness_id: str | None
    eligible_candidate_count: int
    ranked_harness_ids: tuple[str, ...]
    owner_gate_blocked: bool
    rationale: str


@dataclass(frozen=True)
class DispatchTickReport:
    """Result of one need-driven dispatch evaluation cycle (no mutation)."""

    subject_scope: str | None
    pending_stage_count: int
    decisions: tuple[StageDispatchDecision, ...]
    mutated: bool = False


@dataclass(frozen=True)
class DispatchHealthReport:
    """Aggregate dispatch-readiness snapshot (no mutation)."""

    subject_scope: str | None
    pending_unclaimed_stage_count: int
    active_candidate_count: int
    candidates_by_role: Mapping[str, int] = field(default_factory=dict)
    dispatchable_stage_count: int = 0
    no_eligible_candidate_stage_count: int = 0
    owner_gated_stage_count: int = 0
    mutated: bool = False


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _as_str_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return ()
        value = parsed
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value if str(item).strip())
    return ()


def _workspace_available(value: Any) -> bool:
    if value is None:
        return True  # Absence is not evidence of unavailability; default open.
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in _WORKSPACE_AVAILABLE_TOKENS


def _stage_is_dispatchable(stage: Mapping[str, Any]) -> bool:
    """SPEC-TAFE-R2: dispatch candidates are unclaimed, non-terminal stages."""
    claim_status = str(stage.get("claim_status") or "").strip().lower()
    status = str(stage.get("status") or "").strip().lower()
    return claim_status == UNCLAIMED_CLAIM_STATUS and status not in TERMINAL_STAGE_STATUSES


def _flow_subject_type(
    service: _FlowService,
    flow_instance_id: str,
    cache: dict[str, str | None],
) -> str | None:
    if flow_instance_id in cache:
        return cache[flow_instance_id]
    flow = service.get_flow_instance(flow_instance_id)
    subject_type = str(flow["subject_type"]) if flow and flow.get("subject_type") else None
    cache[flow_instance_id] = subject_type
    return subject_type


def _stage_to_need(stage: Mapping[str, Any], *, subject_scope: str) -> DispatchNeed:
    metadata = _as_mapping(stage.get("metadata"))
    return DispatchNeed(
        required_role=str(stage["required_role"]),
        subject_scope=subject_scope,
        artifact_author_session_id=(
            str(metadata["artifact_author_session_id"]) if metadata.get("artifact_author_session_id") else None
        ),
        required_capabilities=_as_str_tuple(metadata.get("required_capabilities")),
        owner_gate_blocked=bool(metadata.get("owner_gate_blocked", False)),
        requires_workspace=bool(metadata.get("requires_workspace", True)),
        stage_id=str(stage.get("stage_id")) if stage.get("stage_id") else None,
        flow_instance_id=str(stage.get("flow_instance_id")) if stage.get("flow_instance_id") else None,
    )


def _snapshot_to_candidate(
    snapshot: Mapping[str, Any],
    *,
    stage_lease_available: bool,
) -> DispatchCandidate:
    metadata = _as_mapping(snapshot.get("metadata"))
    precedence = snapshot.get("reviewer_precedence")
    cost = metadata.get("cost")
    return DispatchCandidate(
        harness_id=str(snapshot["harness_id"]),
        role=str(snapshot["role"]),
        subject_scope=str(snapshot.get("subject_scope") or "all"),
        health_status=str(snapshot.get("health_status") or "unknown"),
        reviewer_precedence=int(precedence) if precedence is not None else 0,
        active_session_id=(str(metadata["active_session_id"]) if metadata.get("active_session_id") else None),
        stage_lease_available=stage_lease_available,
        workspace_available=_workspace_available(snapshot.get("workspace_availability")),
        capabilities=_as_mapping(snapshot.get("capabilities")),
        cost=cost if isinstance(cost, (int, float)) else None,
        model_identifier=(str(snapshot["model_identifier"]) if snapshot.get("model_identifier") else None),
    )


def _active_candidates(service: _FlowService) -> tuple[DispatchCandidate, ...]:
    snapshots = service.list_capability_snapshots(status=ACTIVE_SNAPSHOT_STATUS)
    return tuple(_snapshot_to_candidate(snapshot, stage_lease_available=True) for snapshot in snapshots)


def _dispatchable_stages(
    service: _FlowService,
    *,
    subject_scope: str | None,
) -> list[tuple[dict[str, Any], str]]:
    """Return ``(stage, resolved_subject_scope)`` for each dispatchable stage.

    When ``subject_scope`` is provided, only stages whose owning flow's
    ``subject_type`` matches are returned.
    """
    cache: dict[str, str | None] = {}
    result: list[tuple[dict[str, Any], str]] = []
    for stage in service.list_stage_instances():
        if not _stage_is_dispatchable(stage):
            continue
        flow_instance_id = str(stage.get("flow_instance_id") or "")
        resolved = _flow_subject_type(service, flow_instance_id, cache) if flow_instance_id else None
        resolved_scope = resolved or "all"
        if subject_scope is not None and resolved_scope != subject_scope:
            continue
        result.append((dict(stage), resolved_scope))
    return result


def evaluate_dispatch_tick(
    service: _FlowService,
    *,
    subject_scope: str | None = None,
    now: str | None = None,  # noqa: ARG001 - reserved for future as-of evaluation; non-mutating.
) -> DispatchTickReport:
    """Evaluate need-driven dispatch for each eligible unclaimed stage (R5).

    Computes and reports what ``select_dispatch_target`` would choose per stage.
    Performs no claim, spawn, lease write, or telemetry persistence.
    """
    candidates = _active_candidates(service)
    stages = _dispatchable_stages(service, subject_scope=subject_scope)

    decisions: list[StageDispatchDecision] = []
    for stage, resolved_scope in stages:
        need = _stage_to_need(stage, subject_scope=resolved_scope)
        decision = select_dispatch_target(need, candidates)
        eligible_count = sum(1 for result in decision.evaluations if result.eligible)
        decisions.append(
            StageDispatchDecision(
                stage_instance_id=str(stage.get("id") or ""),
                stage_id=str(stage.get("stage_id") or ""),
                flow_instance_id=str(stage.get("flow_instance_id") or ""),
                required_role=str(stage.get("required_role") or ""),
                subject_scope=resolved_scope,
                selected_harness_id=decision.selected,
                eligible_candidate_count=eligible_count,
                ranked_harness_ids=tuple(c.harness_id for c in decision.ranked_candidates),
                owner_gate_blocked=need.owner_gate_blocked,
                rationale=decision.rationale,
            )
        )

    return DispatchTickReport(
        subject_scope=subject_scope,
        pending_stage_count=len(decisions),
        decisions=tuple(decisions),
        mutated=False,
    )


def evaluate_dispatch_health(
    service: _FlowService,
    *,
    subject_scope: str | None = None,
) -> DispatchHealthReport:
    """Aggregate dispatch readiness across pending unclaimed stages (no mutation)."""
    candidates = _active_candidates(service)
    stages = _dispatchable_stages(service, subject_scope=subject_scope)

    candidates_by_role: dict[str, int] = {}
    for candidate in candidates:
        candidates_by_role[candidate.role] = candidates_by_role.get(candidate.role, 0) + 1

    no_eligible = 0
    owner_gated = 0
    for stage, resolved_scope in stages:
        need = _stage_to_need(stage, subject_scope=resolved_scope)
        if need.owner_gate_blocked:
            owner_gated += 1
        decision = select_dispatch_target(need, candidates)
        if decision.selected is None:
            no_eligible += 1

    return DispatchHealthReport(
        subject_scope=subject_scope,
        pending_unclaimed_stage_count=len(stages),
        active_candidate_count=len(candidates),
        candidates_by_role=candidates_by_role,
        dispatchable_stage_count=len(stages),
        no_eligible_candidate_stage_count=no_eligible,
        owner_gated_stage_count=owner_gated,
        mutated=False,
    )


def tick_report_to_payload(report: DispatchTickReport) -> dict[str, Any]:
    """Render a ``DispatchTickReport`` as a JSON-compatible CLI payload."""
    return {
        "command": "flow dispatch tick",
        "phase": "phase-1",
        "status": "phase1_evaluate_only",
        "mutated": report.mutated,
        "subject_scope": report.subject_scope,
        "pending_stage_count": report.pending_stage_count,
        "decisions": [
            {
                "stage_instance_id": decision.stage_instance_id,
                "stage_id": decision.stage_id,
                "flow_instance_id": decision.flow_instance_id,
                "required_role": decision.required_role,
                "subject_scope": decision.subject_scope,
                "selected_harness_id": decision.selected_harness_id,
                "eligible_candidate_count": decision.eligible_candidate_count,
                "ranked_harness_ids": list(decision.ranked_harness_ids),
                "owner_gate_blocked": decision.owner_gate_blocked,
                "rationale": decision.rationale,
            }
            for decision in report.decisions
        ],
        "summary": (
            f"Evaluated {report.pending_stage_count} dispatchable stage(s); "
            f"{sum(1 for d in report.decisions if d.selected_harness_id)} would dispatch. "
            f"No mutation performed."
        ),
    }


def health_report_to_payload(report: DispatchHealthReport) -> dict[str, Any]:
    """Render a ``DispatchHealthReport`` as a JSON-compatible CLI payload."""
    return {
        "command": "flow dispatch health",
        "phase": "phase-1",
        "status": "phase1_evaluate_only",
        "mutated": report.mutated,
        "subject_scope": report.subject_scope,
        "pending_unclaimed_stage_count": report.pending_unclaimed_stage_count,
        "active_candidate_count": report.active_candidate_count,
        "candidates_by_role": dict(report.candidates_by_role),
        "dispatchable_stage_count": report.dispatchable_stage_count,
        "no_eligible_candidate_stage_count": report.no_eligible_candidate_stage_count,
        "owner_gated_stage_count": report.owner_gated_stage_count,
        "summary": (
            f"{report.pending_unclaimed_stage_count} pending unclaimed stage(s), "
            f"{report.active_candidate_count} active candidate(s); "
            f"{report.no_eligible_candidate_stage_count} stage(s) have no eligible candidate. "
            f"No mutation performed."
        ),
    }
