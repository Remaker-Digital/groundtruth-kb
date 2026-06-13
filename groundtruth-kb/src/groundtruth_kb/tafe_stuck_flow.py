"""Read-only TAFE stuck-flow detection and self-diagnosis (WI-4505).

A pure read / compute / report layer (SPEC-TAFE-R3) over the VERIFIED TAFE
runtime substrate. ``detect_stuck_flows`` reads current flow / stage / stage-lease
state plus the WI-4504 per-stage-attempt telemetry (SPEC-TAFE-R6) and classifies,
for each active flow, why each non-terminal stage is stuck. It attaches a
self-diagnosis derived from the recorded ``outcome`` / ``failure_class`` /
``cleanup_result`` / ``recovery_actions`` telemetry.

This module is **read-only**. It performs no recovery actuation -- no lease
release / expiry, re-dispatch, stage or flow mutation, session spawn, subprocess,
bridge index write, or MemBase write. Every report carries ``mutated == False``.
Lease recovery is WI-4494; dispatch is WI-4498/4499; this slice only detects and
diagnoses.

Relationship to WI-4499 (``tafe_dispatch_runtime``): WI-4499 surfaces *aggregate
dispatch-readiness* counts for the R5 need-evaluation path. WI-4505 is the
canonical *per-flow structured stuck detector + R3 self-diagnosis*. They are
non-overlapping; a later slice may have the WI-4499 tick consume
``detect_stuck_flows`` as its stuck-input primitive (out of scope here).

Telemetry dependence degrades gracefully: when no telemetry exists the
``failed_unrecovered`` facet simply produces no findings, so the lease / stall /
owner-gate facets work on the already-VERIFIED runtime + lease substrate.

Source: bridge thread ``gtkb-tafe-stuck-flow-detection`` (GO at ``-002``);
``PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`` / ``WI-4505``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Any, Protocol

# Stuck-condition reason tokens (SPEC-TAFE-R3).
REASON_EXPIRED_LEASE = "expired_lease"
REASON_STALLED_PENDING = "stalled_pending"
REASON_OWNER_GATE_STALLED = "owner_gate_stalled"
REASON_FAILED_UNRECOVERED = "failed_unrecovered"

# A flow in one of these statuses is terminal and never evaluated for stuck-ness.
TERMINAL_FLOW_STATUSES = frozenset({"completed", "cancelled", "failed", "archived", "superseded", "closed"})
# A stage in one of these statuses is terminal and never evaluated.
TERMINAL_STAGE_STATUSES = frozenset({"completed", "cancelled", "failed", "skipped"})
# claim_status that marks a stage as awaiting a claim (SPEC-TAFE-R2 context).
UNCLAIMED_CLAIM_STATUS = "unclaimed"
# lease_status that marks a stage lease as currently held.
ACTIVE_LEASE_STATUS = "active"
# Telemetry outcome tokens treated as a failed attempt.
_FAILED_OUTCOMES = frozenset({"failure", "failed", "error", "errored"})


@dataclass(frozen=True)
class StuckThresholds:
    """Configurable staleness thresholds for stuck classification (seconds)."""

    stalled_seconds: int = 3600
    owner_gate_stalled_seconds: int = 86400
    lease_expiry_grace_seconds: int = 0


@dataclass(frozen=True)
class StuckFlowFinding:
    """One structured stuck-condition finding for a single stage (read-only)."""

    flow_instance_id: str
    stage_instance_id: str
    stage_id: str
    required_role: str
    reason: str
    diagnosis: str = ""
    age_seconds: int | None = None
    lease_id: str | None = None
    last_outcome: str | None = None
    failure_class: str | None = None
    cleanup_result: str | None = None
    expires_at: str | None = None
    last_activity_at: str | None = None


@dataclass(frozen=True)
class StuckFlowReport:
    """Result of one read-only stuck-flow detection pass (no mutation)."""

    subject_scope: str | None
    active_flow_count: int
    findings: tuple[StuckFlowFinding, ...]
    counts_by_reason: Mapping[str, int] = field(default_factory=dict)
    mutated: bool = False


class _FlowService(Protocol):
    """The read-only slice of the TAFE flow service this detector depends on."""

    def list_flow_instances(
        self,
        *,
        flow_definition_id: str | None = ...,
        flow_type: str | None = ...,
        status: str | None = ...,
    ) -> list[dict[str, Any]]: ...

    def list_stage_instances(
        self, *, flow_instance_id: str | None = ..., status: str | None = ...
    ) -> list[dict[str, Any]]: ...

    def list_stage_leases(
        self,
        *,
        stage_instance_id: str | None = ...,
        lease_status: str | None = ...,
        holder_harness_id: str | None = ...,
    ) -> list[dict[str, Any]]: ...

    def list_stage_attempt_telemetry(
        self,
        *,
        flow_instance_id: str | None = ...,
        stage_instance_id: str | None = ...,
        outcome: str | None = ...,
        failure_class: str | None = ...,
    ) -> list[dict[str, Any]]: ...


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _normalized(value: object) -> str:
    return str(value or "").strip().lower()


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return _normalized(value) in {"true", "yes", "1", "blocked", "on"}


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


def _as_list(value: Any) -> tuple[Any, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return ()
        if isinstance(parsed, (list, tuple)):
            return tuple(parsed)
    return ()


def _int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _parse_iso(text: Any) -> datetime | None:
    """Parse an ISO-8601 timestamp to an aware UTC datetime, or None.

    Accepts both ``...Z`` and ``...+00:00`` forms (the runtime writes the latter
    via ``datetime.isoformat``; telemetry fixtures use the former). A naive value
    is interpreted as UTC. Unparseable input returns None so age-based facets
    fail open -- a value we cannot prove is stale is never flagged.
    """
    if not isinstance(text, str) or not text.strip():
        return None
    candidate = text.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _coerce_now(now: str | datetime | None) -> datetime:
    if isinstance(now, datetime):
        return now if now.tzinfo is not None else now.replace(tzinfo=UTC)
    parsed = _parse_iso(now)
    if parsed is not None:
        return parsed
    return datetime.now(UTC)


def _recovery_actions(row: Mapping[str, Any]) -> tuple[Any, ...]:
    if "recovery_actions_parsed" in row:
        return _as_list(row.get("recovery_actions_parsed"))
    return _as_list(row.get("recovery_actions"))


def _latest_telemetry(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    latest = max(
        rows,
        key=lambda r: (_int_or_zero(r.get("attempt_number")), str(r.get("changed_at") or "")),
    )
    return dict(latest)


def _last_activity(
    stage: Mapping[str, Any],
    telemetry: Sequence[Mapping[str, Any]],
) -> tuple[datetime | None, str | None]:
    """Most recent observable activity timestamp for a stage (stage + telemetry)."""
    candidates: list[str] = []
    for key in ("changed_at", "started_at"):
        value = stage.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(value)
    for row in telemetry:
        for key in ("changed_at", "completed_at", "started_at"):
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value)
    best_dt: datetime | None = None
    best_text: str | None = None
    for text in candidates:
        parsed = _parse_iso(text)
        if parsed is None:
            continue
        if best_dt is None or parsed > best_dt:
            best_dt = parsed
            best_text = text
    return best_dt, best_text


def _active_lease(service: _FlowService, stage_instance_id: str) -> dict[str, Any] | None:
    leases = service.list_stage_leases(stage_instance_id=stage_instance_id, lease_status=ACTIVE_LEASE_STATUS)
    if not leases:
        return None
    # list_stage_leases orders ascending by changed_at; the last row is most recent.
    return dict(leases[-1])


def _is_failed_unrecovered(latest: Mapping[str, Any] | None) -> bool:
    """SPEC-TAFE-R3/R6: latest attempt failed with a failure_class and no recovery."""
    if latest is None:
        return False
    if _normalized(latest.get("outcome")) not in _FAILED_OUTCOMES:
        return False
    if not str(latest.get("failure_class") or "").strip():
        return False
    # Recorded recovery_actions on the failed attempt means recovery was attempted.
    return not _recovery_actions(latest)


def _is_terminal_flow(flow: Mapping[str, Any]) -> bool:
    return _normalized(flow.get("status")) in TERMINAL_FLOW_STATUSES


def _is_terminal_stage(stage: Mapping[str, Any]) -> bool:
    return _normalized(stage.get("status")) in TERMINAL_STAGE_STATUSES


# ---------------------------------------------------------------------------
# Diagnosis (SPEC-TAFE-R3 self-diagnosis over SPEC-TAFE-R6 telemetry)
# ---------------------------------------------------------------------------


def diagnose_stuck_flow(
    finding: StuckFlowFinding,
    telemetry_rows: Sequence[Mapping[str, Any]] = (),
) -> str:
    """Return an advisory self-diagnosis string for a stuck finding (text only).

    The hint is advisory: it is never actuated. Recovery is WI-4494; dispatch is
    WI-4498/4499. ``telemetry_rows`` (SPEC-TAFE-R6) enriches the failed-attempt
    diagnosis with the latest attempt number.
    """
    reason = finding.reason
    if reason == REASON_EXPIRED_LEASE:
        return (
            f"Stage {finding.stage_instance_id} holds active lease "
            f"{finding.lease_id or '<unknown>'} expired at {finding.expires_at} "
            f"({finding.age_seconds}s past expiry). Read-only detection; "
            f"lease recovery is WI-4494 (not actuated here)."
        )
    if reason == REASON_OWNER_GATE_STALLED:
        return (
            f"Stage {finding.stage_instance_id} blocked on an owner gate for "
            f"{finding.age_seconds}s. Awaiting owner decision; advisory only."
        )
    if reason == REASON_STALLED_PENDING:
        return (
            f"Stage {finding.stage_instance_id} unclaimed with no progress for "
            f"{finding.age_seconds}s. Dispatch is WI-4498/4499; not actuated here."
        )
    if reason == REASON_FAILED_UNRECOVERED:
        latest = _latest_telemetry(telemetry_rows)
        attempt = _int_or_zero(latest.get("attempt_number")) if latest else 0
        cls = finding.failure_class or "<unset>"
        return (
            f"Latest attempt (#{attempt}) failed (outcome={finding.last_outcome!r}, "
            f"failure_class={cls!r}, cleanup_result={finding.cleanup_result!r}); "
            f"no recovery_actions recorded. Advisory: investigate {cls}; "
            f"recovery is WI-4494 (not actuated here)."
        )
    return f"Stuck condition {reason!r} detected on stage {finding.stage_instance_id}; advisory only."


def _finalize(finding: StuckFlowFinding, telemetry: Sequence[Mapping[str, Any]]) -> StuckFlowFinding:
    return replace(finding, diagnosis=diagnose_stuck_flow(finding, telemetry))


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _classify_stage(
    service: _FlowService,
    flow: Mapping[str, Any],
    stage: Mapping[str, Any],
    *,
    now_dt: datetime,
    thresholds: StuckThresholds,
) -> list[StuckFlowFinding]:
    flow_id = str(flow.get("id") or "")
    stage_instance_id = str(stage.get("id") or "")
    telemetry = service.list_stage_attempt_telemetry(stage_instance_id=stage_instance_id)
    latest = _latest_telemetry(telemetry)
    active_lease = _active_lease(service, stage_instance_id)
    metadata = _as_mapping(stage.get("metadata"))
    last_activity_dt, last_activity_at = _last_activity(stage, telemetry)

    base = {
        "flow_instance_id": flow_id,
        "stage_instance_id": stage_instance_id,
        "stage_id": str(stage.get("stage_id") or ""),
        "required_role": str(stage.get("required_role") or ""),
    }
    findings: list[StuckFlowFinding] = []

    # Structural facet: a held lease vs an unclaimed/owner-gated stall are mutually
    # exclusive (a leased stage is not "stalled_pending").
    if active_lease is not None:
        expires_dt = _parse_iso(active_lease.get("expires_at"))
        if expires_dt is not None and now_dt >= expires_dt:
            age = int((now_dt - expires_dt).total_seconds())
            if age >= thresholds.lease_expiry_grace_seconds:
                findings.append(
                    _finalize(
                        StuckFlowFinding(
                            **base,
                            reason=REASON_EXPIRED_LEASE,
                            age_seconds=age,
                            lease_id=str(active_lease.get("id") or "") or None,
                            expires_at=str(active_lease.get("expires_at") or "") or None,
                        ),
                        telemetry,
                    )
                )
    else:
        owner_gate_blocked = _truthy(metadata.get("owner_gate_blocked"))
        age = int((now_dt - last_activity_dt).total_seconds()) if last_activity_dt is not None else None
        if owner_gate_blocked and age is not None and age >= thresholds.owner_gate_stalled_seconds:
            findings.append(
                _finalize(
                    StuckFlowFinding(
                        **base,
                        reason=REASON_OWNER_GATE_STALLED,
                        age_seconds=age,
                        last_activity_at=last_activity_at,
                    ),
                    telemetry,
                )
            )
        elif (
            not owner_gate_blocked
            and age is not None
            and age >= thresholds.stalled_seconds
            and _normalized(stage.get("claim_status")) == UNCLAIMED_CLAIM_STATUS
        ):
            findings.append(
                _finalize(
                    StuckFlowFinding(
                        **base,
                        reason=REASON_STALLED_PENDING,
                        age_seconds=age,
                        last_activity_at=last_activity_at,
                    ),
                    telemetry,
                )
            )

    # Telemetry facet (SPEC-TAFE-R6): orthogonal; can co-occur with a structural reason.
    if _is_failed_unrecovered(latest):
        findings.append(
            _finalize(
                StuckFlowFinding(
                    **base,
                    reason=REASON_FAILED_UNRECOVERED,
                    last_outcome=str(latest.get("outcome") or "") or None,
                    failure_class=str(latest.get("failure_class") or "") or None,
                    cleanup_result=str(latest.get("cleanup_result") or "") or None,
                    last_activity_at=last_activity_at,
                ),
                telemetry,
            )
        )

    return findings


def detect_stuck_flows(
    service: _FlowService,
    *,
    now: str | datetime | None = None,
    thresholds: StuckThresholds = StuckThresholds(),
    subject_scope: str | None = None,
) -> StuckFlowReport:
    """Detect and self-diagnose stuck conditions across active flows (read-only).

    Reads current flow / stage / stage-lease / telemetry rows and classifies each
    non-terminal stage of each active (non-terminal) flow. Performs no mutation:
    the returned report always carries ``mutated == False``.
    """
    now_dt = _coerce_now(now)
    flows = [flow for flow in service.list_flow_instances() if not _is_terminal_flow(flow)]
    if subject_scope is not None:
        flows = [flow for flow in flows if str(flow.get("subject_type") or "") == subject_scope]

    findings: list[StuckFlowFinding] = []
    for flow in flows:
        flow_id = str(flow.get("id") or "")
        if not flow_id:
            continue
        for stage in service.list_stage_instances(flow_instance_id=flow_id):
            if _is_terminal_stage(stage):
                continue
            findings.extend(_classify_stage(service, flow, stage, now_dt=now_dt, thresholds=thresholds))

    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.reason] = counts.get(finding.reason, 0) + 1

    return StuckFlowReport(
        subject_scope=subject_scope,
        active_flow_count=len(flows),
        findings=tuple(findings),
        counts_by_reason=counts,
        mutated=False,
    )


def stuck_report_to_payload(report: StuckFlowReport) -> dict[str, Any]:
    """Render a ``StuckFlowReport`` as a JSON-compatible CLI payload."""
    return {
        "command": "flow stuck",
        "phase": "phase-1",
        "status": "phase1_detect_only",
        "mutated": report.mutated,
        "subject_scope": report.subject_scope,
        "active_flow_count": report.active_flow_count,
        "counts": dict(report.counts_by_reason),
        "findings": [
            {
                "flow_instance_id": finding.flow_instance_id,
                "stage_instance_id": finding.stage_instance_id,
                "stage_id": finding.stage_id,
                "required_role": finding.required_role,
                "reason": finding.reason,
                "diagnosis": finding.diagnosis,
                "age_seconds": finding.age_seconds,
                "lease_id": finding.lease_id,
                "last_outcome": finding.last_outcome,
                "failure_class": finding.failure_class,
                "cleanup_result": finding.cleanup_result,
                "expires_at": finding.expires_at,
                "last_activity_at": finding.last_activity_at,
            }
            for finding in report.findings
        ],
        "summary": (
            f"{len(report.findings)} stuck finding(s) across "
            f"{report.active_flow_count} active flow(s). No mutation performed."
        ),
    }


__all__ = [
    "REASON_EXPIRED_LEASE",
    "REASON_FAILED_UNRECOVERED",
    "REASON_OWNER_GATE_STALLED",
    "REASON_STALLED_PENDING",
    "StuckFlowFinding",
    "StuckFlowReport",
    "StuckThresholds",
    "detect_stuck_flows",
    "diagnose_stuck_flow",
    "stuck_report_to_payload",
]
