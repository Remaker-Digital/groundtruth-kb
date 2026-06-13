"""Pure TAFE dispatch-policy decisions.

This module implements the WI-4498 R4 policy engine as in-memory logic only.
It does not gather live context, perform dispatch, persist telemetry, or touch
MemBase. Callers provide the dispatch need and candidate runtime context.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

_UNIVERSAL_SUBJECT_SCOPES = {"*", "all", "both"}
_GATE_ORDER = (
    "role",
    "capability",
    "subject",
    "review_independence",
    "health",
    "stage_lease_availability",
    "owner_gate",
    "workspace_availability",
)


@dataclass(frozen=True)
class DispatchNeed:
    """Caller-supplied description of the dispatch work to be routed."""

    required_role: str
    subject_scope: str
    artifact_author_session_id: str | None
    required_capabilities: Sequence[str] = ()
    owner_gate_blocked: bool = False
    requires_workspace: bool = True
    stage_id: str | None = None
    flow_instance_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required_capabilities",
            tuple(capability for capability in self.required_capabilities if str(capability).strip()),
        )


@dataclass(frozen=True)
class DispatchCandidate:
    """Caller-supplied capability snapshot plus runtime availability context."""

    harness_id: str
    role: str
    subject_scope: str
    health_status: str
    reviewer_precedence: int
    active_session_id: str | None
    stage_lease_available: bool
    workspace_available: bool
    capabilities: Mapping[str, Any] = field(default_factory=dict)
    cost: float | int | None = None
    model_identifier: str | None = None


@dataclass(frozen=True)
class GateResult:
    """Eligibility result for one hard gate."""

    name: str
    passed: bool
    reason: str


@dataclass(frozen=True)
class EligibilityResult:
    """Per-candidate eligibility breakdown."""

    candidate: DispatchCandidate
    gates: tuple[GateResult, ...]

    @property
    def candidate_harness_id(self) -> str:
        return self.candidate.harness_id

    @property
    def eligible(self) -> bool:
        return all(gate.passed for gate in self.gates)

    @property
    def failed_reasons(self) -> tuple[str, ...]:
        return tuple(gate.reason for gate in self.gates if not gate.passed)


@dataclass(frozen=True)
class DispatchDecision:
    """Deterministic dispatch-policy decision."""

    selected: str | None
    selected_candidate: DispatchCandidate | None
    ranked_candidates: tuple[DispatchCandidate, ...]
    evaluations: tuple[EligibilityResult, ...]
    rationale: str


def evaluate_eligibility(need: DispatchNeed, candidate: DispatchCandidate) -> EligibilityResult:
    """Evaluate SPEC-TAFE-R4 hard eligibility gates for one candidate."""

    gates = tuple(_evaluate_gate(name, need, candidate) for name in _GATE_ORDER)
    return EligibilityResult(candidate=candidate, gates=gates)


def select_dispatch_target(
    need: DispatchNeed,
    candidates: Sequence[DispatchCandidate],
) -> DispatchDecision:
    """Return the selected harness and full eligibility/ranking evidence."""

    evaluations = tuple(evaluate_eligibility(need, candidate) for candidate in candidates)
    eligible_candidates = tuple(
        sorted(
            (result.candidate for result in evaluations if result.eligible),
            key=_candidate_rank_key,
        )
    )
    selected_candidate = eligible_candidates[0] if eligible_candidates else None
    selected = selected_candidate.harness_id if selected_candidate else None
    rationale = _decision_rationale(selected_candidate, evaluations)
    return DispatchDecision(
        selected=selected,
        selected_candidate=selected_candidate,
        ranked_candidates=eligible_candidates,
        evaluations=evaluations,
        rationale=rationale,
    )


def _evaluate_gate(name: str, need: DispatchNeed, candidate: DispatchCandidate) -> GateResult:
    if name == "role":
        return _role_gate(need, candidate)
    if name == "capability":
        return _capability_gate(need, candidate)
    if name == "subject":
        return _subject_gate(need, candidate)
    if name == "review_independence":
        return _review_independence_gate(need, candidate)
    if name == "health":
        return _health_gate(candidate)
    if name == "stage_lease_availability":
        return _stage_lease_gate(candidate)
    if name == "owner_gate":
        return _owner_gate(need)
    if name == "workspace_availability":
        return _workspace_gate(need, candidate)
    raise ValueError(f"unknown eligibility gate: {name}")


def _role_gate(need: DispatchNeed, candidate: DispatchCandidate) -> GateResult:
    required = _normalized(need.required_role)
    candidate_role = _normalized(candidate.role)
    passed = bool(required and candidate_role and required == candidate_role)
    reason = (
        f"candidate role {candidate.role!r} matches required role {need.required_role!r}"
        if passed
        else f"candidate role {candidate.role!r} does not match required role {need.required_role!r}"
    )
    return GateResult("role", passed, reason)


def _capability_gate(need: DispatchNeed, candidate: DispatchCandidate) -> GateResult:
    required = tuple(_normalized(capability) for capability in need.required_capabilities)
    capabilities = {_normalized(key): value for key, value in (candidate.capabilities or {}).items()}
    missing = tuple(capability for capability in required if not capabilities.get(capability))
    passed = not missing
    reason = (
        "candidate satisfies all required capabilities"
        if passed
        else f"candidate is missing required capabilities: {', '.join(missing)}"
    )
    return GateResult("capability", passed, reason)


def _subject_gate(need: DispatchNeed, candidate: DispatchCandidate) -> GateResult:
    need_scope = _normalized(need.subject_scope)
    candidate_scope = _normalized(candidate.subject_scope)
    passed = bool(
        need_scope
        and candidate_scope
        and (candidate_scope == need_scope or candidate_scope in _UNIVERSAL_SUBJECT_SCOPES)
    )
    reason = (
        f"candidate subject scope {candidate.subject_scope!r} covers {need.subject_scope!r}"
        if passed
        else f"candidate subject scope {candidate.subject_scope!r} does not cover {need.subject_scope!r}"
    )
    return GateResult("subject", passed, reason)


def _review_independence_gate(need: DispatchNeed, candidate: DispatchCandidate) -> GateResult:
    author_session = _normalized(need.artifact_author_session_id)
    candidate_session = _normalized(candidate.active_session_id)
    passed = bool(author_session and candidate_session and author_session != candidate_session)
    if passed:
        reason = "candidate active session is independent from artifact author session"
    elif not candidate_session:
        reason = "candidate active session is missing; review independence fails closed"
    elif not author_session:
        reason = "artifact author session is missing; review independence fails closed"
    else:
        reason = "candidate active session matches artifact author session"
    return GateResult("review_independence", passed, reason)


def _health_gate(candidate: DispatchCandidate) -> GateResult:
    passed = _normalized(candidate.health_status) == "active"
    reason = "candidate health is active" if passed else f"candidate health {candidate.health_status!r} is not active"
    return GateResult("health", passed, reason)


def _stage_lease_gate(candidate: DispatchCandidate) -> GateResult:
    passed = candidate.stage_lease_available is True
    reason = "candidate has an available stage lease" if passed else "candidate does not have an available stage lease"
    return GateResult("stage_lease_availability", passed, reason)


def _owner_gate(need: DispatchNeed) -> GateResult:
    passed = need.owner_gate_blocked is False
    reason = "owner gate is open" if passed else "owner gate is blocked"
    return GateResult("owner_gate", passed, reason)


def _workspace_gate(need: DispatchNeed, candidate: DispatchCandidate) -> GateResult:
    if not need.requires_workspace:
        return GateResult(
            "workspace_availability",
            True,
            "dispatch need does not require workspace availability",
        )
    passed = candidate.workspace_available is True
    reason = "candidate workspace is available" if passed else "candidate workspace is unavailable"
    return GateResult("workspace_availability", passed, reason)


def _candidate_rank_key(candidate: DispatchCandidate) -> tuple[int, float, str]:
    return (
        int(candidate.reviewer_precedence),
        _cost_for_ranking(candidate.cost),
        candidate.harness_id,
    )


def _cost_for_ranking(cost: float | int | None) -> float:
    if cost is None:
        return 0.0
    return float(cost)


def _decision_rationale(
    selected_candidate: DispatchCandidate | None,
    evaluations: Sequence[EligibilityResult],
) -> str:
    if selected_candidate is not None:
        return (
            f"Selected {selected_candidate.harness_id!r}: passed all hard eligibility gates and ranked first "
            "by reviewer_precedence, cost, and harness_id."
        )
    rejected = "; ".join(
        f"{result.candidate.harness_id or '<unknown>'}: {', '.join(result.failed_reasons)}" for result in evaluations
    )
    return f"No eligible dispatch target. Rejections: {rejected}" if rejected else "No candidates supplied."


def _normalized(value: object) -> str:
    return str(value or "").strip().lower()


__all__ = [
    "DispatchCandidate",
    "DispatchDecision",
    "DispatchNeed",
    "EligibilityResult",
    "GateResult",
    "evaluate_eligibility",
    "select_dispatch_target",
]
