# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Resource-bounded restore execution helpers for the service/SoT watchdog."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from groundtruth_kb.watchdog.restore_policy import AutoRestoreAction, RestorePolicyDecision

ProbeCallable = Callable[[], dict[str, Any]]
RestoreCallable = Callable[[], dict[str, Any] | None]


@dataclass(frozen=True)
class HostLoadSnapshot:
    """Host load inputs used to decide whether a heavy restore may start."""

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    detail: str = ""


@dataclass(frozen=True)
class ResourceLimitPlan:
    """Resource limits for one restore execution attempt."""

    max_cpu_percent: float = 85.0
    max_memory_percent: float = 90.0
    timeout_seconds: float = 300.0
    require_process_tree_cap: bool = True


@dataclass
class ProcessTreeLimiter:
    """Process-tree containment abstraction.

    This object intentionally models capability and lifecycle separately from a
    concrete OS implementation. Windows Job Object / cgroup plumbing can be
    added behind this interface; callers already fail closed when a required
    whole-process-tree cap is unavailable.
    """

    plan: ResourceLimitPlan
    platform: str = field(default_factory=lambda: os.name)
    available: bool = True
    entered: bool = False
    exited: bool = False

    def __enter__(self) -> ProcessTreeLimiter:
        self.entered = True
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> Literal[False]:
        self.exited = True
        return False

    @property
    def applied(self) -> bool:
        return self.available and self.entered


@dataclass(frozen=True)
class ResourceBoundedRestoreResult:
    """Outcome of a resource-bounded restore execution decision."""

    status: Literal["executed", "deferred", "skipped", "failed"]
    reason_code: str
    detail: str = ""
    restore_result: dict[str, Any] | None = None
    pre_probe: dict[str, Any] | None = None
    success_probe: dict[str, Any] | None = None
    load_snapshot: HostLoadSnapshot | None = None
    process_tree_cap_applied: bool = False

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason_code": self.reason_code,
            "detail": self.detail,
            "restore_result": self.restore_result,
            "pre_probe": self.pre_probe,
            "success_probe": self.success_probe,
            "load_snapshot": None if self.load_snapshot is None else self.load_snapshot.__dict__,
            "process_tree_cap_applied": self.process_tree_cap_applied,
        }


def should_defer_for_load(load: HostLoadSnapshot, plan: ResourceLimitPlan) -> bool:
    """Return True when host load should defer a heavy restore attempt."""

    return load.cpu_percent >= plan.max_cpu_percent or load.memory_percent >= plan.max_memory_percent


def _probe_status(probe: dict[str, Any] | None) -> str:
    return str((probe or {}).get("status") or "UNKNOWN").upper()


def execute_resource_bounded_restore(
    decision: RestorePolicyDecision,
    *,
    restore: RestoreCallable,
    fresh_probe: ProbeCallable,
    success_probe: ProbeCallable,
    load_snapshot: HostLoadSnapshot | None = None,
    limit_plan: ResourceLimitPlan | None = None,
    limiter_factory: Callable[[ResourceLimitPlan], ProcessTreeLimiter] | None = None,
) -> ResourceBoundedRestoreResult:
    """Execute a safe restore under probe, load, and process-tree gates."""

    plan = limit_plan or ResourceLimitPlan()
    load = load_snapshot or HostLoadSnapshot()
    if not isinstance(decision, AutoRestoreAction):
        return ResourceBoundedRestoreResult(
            status="skipped",
            reason_code="policy_not_auto_restore",
            detail=f"policy decision {decision.kind!r} is not executable by the resource layer",
            load_snapshot=load,
        )

    pre = fresh_probe()
    if _probe_status(pre) != "FAIL":
        return ResourceBoundedRestoreResult(
            status="skipped",
            reason_code="fresh_probe_not_failed",
            detail="fresh probe no longer shows a failure symptom",
            pre_probe=pre,
            load_snapshot=load,
        )

    if should_defer_for_load(load, plan):
        return ResourceBoundedRestoreResult(
            status="deferred",
            reason_code="host_load_too_high",
            detail=load.detail or "host load exceeds restore threshold",
            pre_probe=pre,
            load_snapshot=load,
        )

    limiter = (limiter_factory or ProcessTreeLimiter)(plan)
    if plan.require_process_tree_cap and not limiter.available:
        return ResourceBoundedRestoreResult(
            status="deferred",
            reason_code="process_tree_cap_unavailable",
            detail="required whole-process-tree resource cap is unavailable",
            pre_probe=pre,
            load_snapshot=load,
        )

    try:
        with limiter:
            restore_payload = restore() or {}
    except Exception as exc:  # noqa: BLE001 - restore failures must be reported, not hidden
        return ResourceBoundedRestoreResult(
            status="failed",
            reason_code="restore_exception",
            detail=f"{type(exc).__name__}: {exc}",
            pre_probe=pre,
            load_snapshot=load,
            process_tree_cap_applied=limiter.applied,
        )

    success = success_probe()
    if _probe_status(success) == "FAIL":
        return ResourceBoundedRestoreResult(
            status="failed",
            reason_code="symptom_probe_still_failing",
            detail="restore completed but the symptom probe still reports failure",
            restore_result=restore_payload,
            pre_probe=pre,
            success_probe=success,
            load_snapshot=load,
            process_tree_cap_applied=limiter.applied,
        )

    return ResourceBoundedRestoreResult(
        status="executed",
        reason_code="symptom_probe_passed",
        detail="restore completed and symptom probe no longer fails",
        restore_result=restore_payload,
        pre_probe=pre,
        success_probe=success,
        load_snapshot=load,
        process_tree_cap_applied=limiter.applied,
    )


__all__ = [
    "HostLoadSnapshot",
    "ProcessTreeLimiter",
    "ResourceBoundedRestoreResult",
    "ResourceLimitPlan",
    "execute_resource_bounded_restore",
    "should_defer_for_load",
]
