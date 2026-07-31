# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Stateless restoration policy for the service/SoT watchdog."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from groundtruth_kb.bridge.disposition import STATUS_ADVISORY
from groundtruth_kb.project.sot_registry import SoTArtifact

SAFE_AUTO_RESTORE_ACTIONS = frozenset({"ensure_alive", "regenerate_from_source"})
CANONICAL_RESTORE_ACTIONS = frozenset({"git_restore", "membase_export_restore"})
NO_RESTORE_ACTIONS = frozenset({"visibility_only", "noop"})
MANUAL_RESTORE_ACTIONS = frozenset({"manual"})
RESTORABLE_PROBE_STATUSES = frozenset({"WARN", "FAIL"})

RestoreTier = Literal["safe", "canonical", "visibility_only", "manual", "noop", "unknown"]


@dataclass(frozen=True)
class AutoRestoreAction:
    """A safe/idempotent restore action may be executed by a later executor."""

    artifact_id: str
    restore_action: str
    reason_code: str
    detail: str = ""
    retry_attempts: int = 0
    max_attempts: int = 3
    fresh_probe_required: bool = True
    kind: Literal["auto_restore"] = field(default="auto_restore", init=False)

    def to_json_dict(self) -> dict[str, Any]:
        return _decision_to_json_dict(self)


@dataclass(frozen=True)
class EscalateAction:
    """A restore action must become visible instead of auto-mutating state."""

    artifact_id: str
    restore_action: str
    reason_code: str
    detail: str = ""
    retry_attempts: int = 0
    max_attempts: int = 3
    retry_exhausted: bool = False
    advisory_required: bool = True
    flagged_state_required: bool = True
    escalation_status: str = STATUS_ADVISORY
    kind: Literal["escalate"] = field(default="escalate", init=False)

    def to_json_dict(self) -> dict[str, Any]:
        return _decision_to_json_dict(self)


@dataclass(frozen=True)
class NoRestoreAction:
    """No automatic restore is allowed or needed for the target."""

    artifact_id: str
    restore_action: str
    reason_code: str
    detail: str = ""
    retry_attempts: int = 0
    max_attempts: int = 3
    advisory_required: bool = False
    flagged_state_required: bool = False
    kind: Literal["no_restore"] = field(default="no_restore", init=False)

    def to_json_dict(self) -> dict[str, Any]:
        return _decision_to_json_dict(self)


RestorePolicyDecision = AutoRestoreAction | EscalateAction | NoRestoreAction


def normalize_restore_action(restore_action: str | None) -> str:
    """Normalize registry restore-action values for policy matching."""
    return str(restore_action or "manual").strip().lower().replace("-", "_")


def restore_action_tier(restore_action: str | None) -> RestoreTier:
    """Return the safety tier for a registry restore-action value."""
    action = normalize_restore_action(restore_action)
    if action in SAFE_AUTO_RESTORE_ACTIONS:
        return "safe"
    if action in CANONICAL_RESTORE_ACTIONS:
        return "canonical"
    if action == "visibility_only":
        return "visibility_only"
    if action in MANUAL_RESTORE_ACTIONS:
        return "manual"
    if action == "noop":
        return "noop"
    return "unknown"


def decide_restore_action(
    *,
    artifact_id: str,
    restore_action: str | None,
    probe_status: str,
    fresh_probe: bool,
    retry_attempts: int = 0,
    max_attempts: int = 3,
    detail: str = "",
    visibility_only_artifact_ids: Iterable[str] = (),
) -> RestorePolicyDecision:
    """Decide the next restoration action from fresh probe output and registry metadata."""
    if retry_attempts < 0:
        raise ValueError("retry_attempts must be non-negative")
    if max_attempts < 0:
        raise ValueError("max_attempts must be non-negative")

    target_id = str(artifact_id)
    action = normalize_restore_action(restore_action)
    status = str(probe_status or "UNKNOWN").strip().upper()
    tier = restore_action_tier(action)
    retry_exhausted = retry_attempts >= max_attempts
    visibility_only_ids = {str(item) for item in visibility_only_artifact_ids}

    if status not in RESTORABLE_PROBE_STATUSES:
        return NoRestoreAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="probe_not_failed",
            detail=detail or f"probe status {status!r} does not require restoration",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
        )
    if not fresh_probe:
        return NoRestoreAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="stale_probe",
            detail=detail or "restore requires a fresh failure probe",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
            flagged_state_required=True,
        )
    if tier == "visibility_only" or target_id in visibility_only_ids:
        return NoRestoreAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="visibility_only",
            detail=detail or "target is configured for visibility only; automatic restore is forbidden",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
            flagged_state_required=True,
        )
    if retry_exhausted:
        return EscalateAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="retry_exhausted",
            detail=detail or f"restore retries exhausted ({retry_attempts}/{max_attempts})",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
            retry_exhausted=True,
        )
    if tier == "canonical":
        return EscalateAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="canonical_restore_forbidden",
            detail=detail or "canonical-tier restore must fail loud instead of auto-mutating authoritative state",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
        )
    if tier == "manual":
        return EscalateAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="manual_restore_required",
            detail=detail or "manual restore action requires visible escalation",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
        )
    if tier == "noop":
        return NoRestoreAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="noop_restore_action",
            detail=detail or "registry declares no restore action for this target",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
            flagged_state_required=True,
        )
    if tier == "safe":
        return AutoRestoreAction(
            artifact_id=target_id,
            restore_action=action,
            reason_code="safe_auto_restore",
            detail=detail or "safe/idempotent restore is eligible for execution",
            retry_attempts=retry_attempts,
            max_attempts=max_attempts,
        )
    return EscalateAction(
        artifact_id=target_id,
        restore_action=action,
        reason_code="unknown_restore_action",
        detail=detail or f"restore action {action!r} is not classified by policy",
        retry_attempts=retry_attempts,
        max_attempts=max_attempts,
    )


def decide_artifact_restoration(
    artifact: SoTArtifact,
    probe: Mapping[str, Any],
    *,
    retry_attempts: int = 0,
    max_attempts: int = 3,
    fresh_probe: bool | None = None,
    visibility_only_artifact_ids: Iterable[str] = (),
) -> RestorePolicyDecision:
    """Decide restoration for one SoT artifact probe result."""
    probe_fresh = bool(probe.get("fresh", True)) if fresh_probe is None else fresh_probe
    return decide_restore_action(
        artifact_id=artifact.id,
        restore_action=artifact.restore_action,
        probe_status=str(probe.get("status", "UNKNOWN")),
        fresh_probe=probe_fresh,
        retry_attempts=retry_attempts,
        max_attempts=max_attempts,
        detail=str(probe.get("detail") or ""),
        visibility_only_artifact_ids=visibility_only_artifact_ids,
    )


def _decision_to_json_dict(decision: RestorePolicyDecision) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "kind": decision.kind,
        "artifact_id": decision.artifact_id,
        "restore_action": decision.restore_action,
        "reason_code": decision.reason_code,
        "detail": decision.detail,
        "retry_attempts": decision.retry_attempts,
        "max_attempts": decision.max_attempts,
    }
    if isinstance(decision, AutoRestoreAction):
        payload["fresh_probe_required"] = decision.fresh_probe_required
    if isinstance(decision, EscalateAction):
        payload.update(
            {
                "retry_exhausted": decision.retry_exhausted,
                "advisory_required": decision.advisory_required,
                "flagged_state_required": decision.flagged_state_required,
                "escalation_status": decision.escalation_status,
            }
        )
    if isinstance(decision, NoRestoreAction):
        payload.update(
            {
                "advisory_required": decision.advisory_required,
                "flagged_state_required": decision.flagged_state_required,
            }
        )
    return payload


__all__ = [
    "AutoRestoreAction",
    "CANONICAL_RESTORE_ACTIONS",
    "EscalateAction",
    "NO_RESTORE_ACTIONS",
    "NoRestoreAction",
    "RestorePolicyDecision",
    "SAFE_AUTO_RESTORE_ACTIONS",
    "decide_artifact_restoration",
    "decide_restore_action",
    "normalize_restore_action",
    "restore_action_tier",
]
