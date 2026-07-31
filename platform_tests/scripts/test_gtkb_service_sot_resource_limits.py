# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for resource-bounded watchdog restore execution (WI-5046)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.watchdog.resource_limits import (  # noqa: E402
    HostLoadSnapshot,
    ProcessTreeLimiter,
    ResourceLimitPlan,
    execute_resource_bounded_restore,
    should_defer_for_load,
)
from groundtruth_kb.watchdog.restore_policy import (  # noqa: E402
    AutoRestoreAction,
    EscalateAction,
)


def _auto_decision() -> AutoRestoreAction:
    return AutoRestoreAction(
        artifact_id="bridge-dispatch-state",
        restore_action="ensure_alive",
        reason_code="safe_auto_restore",
    )


def test_defers_heavy_restore_under_host_load() -> None:
    calls: list[str] = []

    result = execute_resource_bounded_restore(
        _auto_decision(),
        restore=lambda: calls.append("restore") or {"ok": True},
        fresh_probe=lambda: {"status": "FAIL", "detail": "daemon down"},
        success_probe=lambda: {"status": "PASS"},
        load_snapshot=HostLoadSnapshot(cpu_percent=96.0, memory_percent=40.0, detail="cpu saturated"),
    )

    assert result.status == "deferred"
    assert result.reason_code == "host_load_too_high"
    assert calls == []


def test_should_defer_for_load_checks_cpu_and_memory_thresholds() -> None:
    plan = ResourceLimitPlan(max_cpu_percent=80.0, max_memory_percent=85.0)

    assert should_defer_for_load(HostLoadSnapshot(cpu_percent=80.0, memory_percent=10.0), plan)
    assert should_defer_for_load(HostLoadSnapshot(cpu_percent=10.0, memory_percent=85.0), plan)
    assert not should_defer_for_load(HostLoadSnapshot(cpu_percent=79.9, memory_percent=84.9), plan)


def test_fresh_probe_runs_before_restore_and_can_skip() -> None:
    calls: list[str] = []

    result = execute_resource_bounded_restore(
        _auto_decision(),
        restore=lambda: calls.append("restore") or {"ok": True},
        fresh_probe=lambda: calls.append("fresh_probe") or {"status": "PASS", "detail": "already healthy"},
        success_probe=lambda: calls.append("success_probe") or {"status": "PASS"},
    )

    assert result.status == "skipped"
    assert result.reason_code == "fresh_probe_not_failed"
    assert calls == ["fresh_probe"]


def test_required_process_tree_cap_fails_closed_when_unavailable() -> None:
    calls: list[str] = []

    def unavailable_limiter(plan: ResourceLimitPlan) -> ProcessTreeLimiter:
        return ProcessTreeLimiter(plan, available=False)

    result = execute_resource_bounded_restore(
        _auto_decision(),
        restore=lambda: calls.append("restore") or {"ok": True},
        fresh_probe=lambda: {"status": "FAIL"},
        success_probe=lambda: {"status": "PASS"},
        limiter_factory=unavailable_limiter,
    )

    assert result.status == "deferred"
    assert result.reason_code == "process_tree_cap_unavailable"
    assert calls == []


def test_restore_success_is_judged_by_symptom_probe() -> None:
    calls: list[str] = []

    result = execute_resource_bounded_restore(
        _auto_decision(),
        restore=lambda: calls.append("restore") or {"started": True},
        fresh_probe=lambda: calls.append("fresh_probe") or {"status": "FAIL"},
        success_probe=lambda: calls.append("success_probe") or {"status": "PASS"},
    )

    assert result.status == "executed"
    assert result.reason_code == "symptom_probe_passed"
    assert result.process_tree_cap_applied is True
    assert calls == ["fresh_probe", "restore", "success_probe"]


def test_failed_symptom_probe_reports_failed_restore() -> None:
    result = execute_resource_bounded_restore(
        _auto_decision(),
        restore=lambda: {"started": True},
        fresh_probe=lambda: {"status": "FAIL"},
        success_probe=lambda: {"status": "FAIL", "detail": "operation still blocked"},
    )

    assert result.status == "failed"
    assert result.reason_code == "symptom_probe_still_failing"


def test_non_auto_policy_decision_is_not_executed() -> None:
    calls: list[str] = []
    decision = EscalateAction(
        artifact_id="membase-specifications",
        restore_action="membase_export_restore",
        reason_code="canonical_restore_forbidden",
    )

    result = execute_resource_bounded_restore(
        decision,
        restore=lambda: calls.append("restore") or {"ok": True},
        fresh_probe=lambda: calls.append("fresh_probe") or {"status": "FAIL"},
        success_probe=lambda: calls.append("success_probe") or {"status": "PASS"},
    )

    assert result.status == "skipped"
    assert result.reason_code == "policy_not_auto_restore"
    assert calls == []
