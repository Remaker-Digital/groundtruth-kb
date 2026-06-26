"""Unit tests for the WI-4790 slice-1 dispatch monitoring detector.

Covers the pure detection core: ``classify_outcome`` taxonomy plus
``compute_snapshot`` per-role distribution, saturation, and stale-live detection.
The read-only gather/``main`` glue is exercised by the module's smoke run, not
unit-tested here (it is filesystem I/O over live dispatch evidence).

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OPS_DIR = _REPO_ROOT / "scripts" / "ops"
if str(_OPS_DIR) not in sys.path:
    sys.path.insert(0, str(_OPS_DIR))

import dispatch_monitor as dm  # noqa: E402

NOW = 1_000_000.0


def _outcome(
    *,
    role: str = "loyal-opposition",
    launched: bool = True,
    exit_code: int | None = 0,
    has_verdict: bool = True,
    stdout_bytes: int = 128,
    error_message: str = "",
    age: float = 10.0,
    pid_alive: bool = False,
) -> dm.DispatchOutcome:
    return dm.DispatchOutcome(
        role=role,
        harness_id="F",
        launched=launched,
        exit_code=exit_code,
        has_verdict=has_verdict,
        stdout_bytes=stdout_bytes,
        error_message=error_message,
        created_epoch=NOW - age,
        pid_alive=pid_alive,
    )


def test_classify_outcome_taxonomy() -> None:
    # success
    assert dm.classify_outcome(_outcome(exit_code=0)) == dm.CLASS_SUCCESS
    # corrupt_output: nonzero exit + zero stdout + no verdict (killed-mid-output signature),
    # for the timeout code, a generic nonzero code, and the abrupt-termination code.
    assert dm.classify_outcome(_outcome(exit_code=124, stdout_bytes=0, has_verdict=False)) == dm.CLASS_CORRUPT_OUTPUT
    assert dm.classify_outcome(_outcome(exit_code=1, stdout_bytes=0, has_verdict=False)) == dm.CLASS_CORRUPT_OUTPUT
    assert (
        dm.classify_outcome(_outcome(exit_code=4294967295, stdout_bytes=0, has_verdict=False))
        == dm.CLASS_CORRUPT_OUTPUT
    )
    # worker_timeout: kill-code exit but produced some output (not the corrupt signature)
    assert dm.classify_outcome(_outcome(exit_code=124, stdout_bytes=500, has_verdict=True)) == dm.CLASS_WORKER_TIMEOUT
    # in_flight: no exit recorded yet
    assert dm.classify_outcome(_outcome(exit_code=None)) == dm.CLASS_IN_FLIGHT
    # nonzero exit WITH output, classified by message
    assert (
        dm.classify_outcome(_outcome(exit_code=1, stdout_bytes=50, has_verdict=True, error_message="provider_failure"))
        == dm.CLASS_PROVIDER_FAILURE
    )
    assert (
        dm.classify_outcome(
            _outcome(exit_code=1, stdout_bytes=50, has_verdict=True, error_message="subprocess_execution_failed")
        )
        == dm.CLASS_SUBPROCESS_FAILED
    )
    assert dm.classify_outcome(_outcome(exit_code=1, stdout_bytes=50, has_verdict=True)) == dm.CLASS_OTHER
    # not-launched: no_active_target / cap_reached from the failure reason
    assert (
        dm.classify_outcome(_outcome(launched=False, exit_code=None, error_message="no active harness for role"))
        == dm.CLASS_NO_ACTIVE_TARGET
    )
    assert (
        dm.classify_outcome(_outcome(launched=False, exit_code=None, error_message="per_role_concurrency_cap_reached"))
        == dm.CLASS_CAP_REACHED
    )


def test_compute_snapshot_per_role_distribution() -> None:
    outcomes = [
        _outcome(exit_code=0),
        _outcome(exit_code=0),
        _outcome(exit_code=124, stdout_bytes=0, has_verdict=False),  # corrupt_output
        _outcome(exit_code=1, stdout_bytes=50, has_verdict=True, error_message="provider_failure"),
    ]
    snap = dm.compute_snapshot(outcomes, caps={"loyal-opposition": 3}, now=NOW)
    role = snap.per_role["loyal-opposition"]
    assert role.total == 4
    assert role.error_class_counts[dm.CLASS_SUCCESS] == 2
    assert role.error_class_counts[dm.CLASS_CORRUPT_OUTPUT] == 1
    assert role.error_class_counts[dm.CLASS_PROVIDER_FAILURE] == 1
    assert role.corrupt_output_count == 1
    assert role.healthy is False  # corrupt-output present
    # purity: identical inputs -> identical snapshot
    snap2 = dm.compute_snapshot(outcomes, caps={"loyal-opposition": 3}, now=NOW)
    assert snap.per_role["loyal-opposition"] == snap2.per_role["loyal-opposition"]
    # window filtering: an old outcome is excluded
    old = [*outcomes, _outcome(exit_code=0, age=dm.DEFAULT_WINDOW_SECONDS + 500)]
    snap3 = dm.compute_snapshot(old, caps={"loyal-opposition": 3}, now=NOW)
    assert snap3.per_role["loyal-opposition"].total == 4


def test_snapshot_flags_saturation_and_stale_live() -> None:
    # Saturation: cap 2, two genuinely-live in-flight workers -> ratio >= 1.0, unhealthy.
    live = [_outcome(exit_code=None, pid_alive=True), _outcome(exit_code=None, pid_alive=True)]
    role = dm.compute_snapshot(live, caps={"loyal-opposition": 2}, now=NOW).per_role["loyal-opposition"]
    assert role.in_flight_count == 2
    assert role.saturation_ratio >= 1.0
    assert role.healthy is False

    # Stale-live: in-flight records whose pid is dead -> stale, excluded from the live count.
    stale = [
        _outcome(exit_code=None, pid_alive=False),  # dead pid -> stale
        _outcome(exit_code=None, pid_alive=False),  # dead pid -> stale
        _outcome(exit_code=None, pid_alive=True),  # genuinely live
    ]
    role2 = dm.compute_snapshot(stale, caps={"loyal-opposition": 3}, now=NOW).per_role["loyal-opposition"]
    assert role2.stale_live_count == 2
    assert role2.saturation_ratio == round(1 / 3, 4)  # live = 3 - 2 stale = 1, cap 3
    assert role2.healthy is False  # stale present even though not saturated

    # Over-lifetime stale: pid "alive" but older than the max-lifetime backstop.
    overage = [_outcome(exit_code=None, pid_alive=True, age=dm.DEFAULT_MAX_LIFETIME_SECONDS + 100)]
    role3 = dm.compute_snapshot(overage, caps={"loyal-opposition": 3}, now=NOW).per_role["loyal-opposition"]
    assert role3.stale_live_count == 1


# --- WI-4790 slice 2: health_response decision -----------------------------


def _role_snap(
    role: str = "loyal-opposition", *, saturation: float = 0.0, corrupt: int = 0, stale: int = 0
) -> dm.RoleMonitorSnapshot:
    return dm.RoleMonitorSnapshot(
        role=role,
        total=1,
        error_class_counts={},
        corrupt_output_count=corrupt,
        in_flight_count=0,
        saturation_ratio=saturation,
        stale_live_count=stale,
        healthy=(saturation < 1.0 and corrupt == 0 and stale == 0),
    )


def _snapshot(*role_snaps: dm.RoleMonitorSnapshot) -> dm.DispatchMonitorSnapshot:
    return dm.DispatchMonitorSnapshot(
        per_role={s.role: s for s in role_snaps},
        generated_at="2026-01-01T00:00:00Z",
        window_seconds=3600,
    )


def test_health_response_holds_on_unhealth() -> None:
    snap = _snapshot(
        _role_snap("loyal-opposition", saturation=1.0),
        _role_snap("prime-builder", corrupt=1),
        _role_snap("ollama", stale=2),
        _role_snap("openrouter"),  # healthy
    )
    resp = dm.health_response(snap)
    assert resp["loyal-opposition"].action == "hold"
    assert resp["prime-builder"].action == "hold"
    assert resp["ollama"].action == "hold"
    assert resp["openrouter"].action == "allow"
    # purity: identical snapshot -> identical response
    assert dm.health_response(snap) == resp


def test_health_response_remediation_hint() -> None:
    resp = dm.health_response(
        _snapshot(
            _role_snap("ollama", stale=2),  # stale-dominated
            _role_snap("loyal-opposition", saturation=1.0),  # saturated, no stale
        )
    )
    assert resp["ollama"].remediation_hint == "reap_stale_dispatch_runs"
    assert resp["loyal-opposition"].remediation_hint == "drain_and_hold"
    # allow -> no remediation hint
    assert dm.health_response(_snapshot(_role_snap("openrouter")))["openrouter"].remediation_hint is None


def test_health_response_escalates_on_severe_corrupt() -> None:
    severe = dm.health_response(_snapshot(_role_snap("openrouter", corrupt=3)))["openrouter"]
    assert severe.action == "escalate"
    assert "severe_corrupt_output_outage" in severe.reasons
    mild = dm.health_response(_snapshot(_role_snap("openrouter", corrupt=1)))["openrouter"]
    assert mild.action == "hold"


# --- WI-4852: watchdog_dormancy pure detection --------------------------------


def test_watchdog_dormancy_detected_when_stale() -> None:
    """Age exceeding threshold → dormant=True, reason='stale'."""
    threshold = dm.DEFAULT_WATCHDOG_DORMANCY_THRESHOLD_SECONDS
    last_epoch = NOW - (threshold + 60)
    verdict = dm.watchdog_dormancy(last_epoch, NOW, threshold)
    assert verdict.dormant is True
    assert verdict.reason == "stale"
    assert verdict.age_seconds > threshold


def test_watchdog_dormancy_not_flagged_when_fresh() -> None:
    """Recent evidence → dormant=False, reason='fresh'."""
    threshold = dm.DEFAULT_WATCHDOG_DORMANCY_THRESHOLD_SECONDS
    last_epoch = NOW - 30  # 30 s old, well inside the threshold
    verdict = dm.watchdog_dormancy(last_epoch, NOW, threshold)
    assert verdict.dormant is False
    assert verdict.reason == "fresh"


def test_watchdog_dormancy_missing_evidence_is_dormant() -> None:
    """Missing or zero last_evidence_epoch → dormant=True, reason='no_evidence'."""
    verdict_zero = dm.watchdog_dormancy(0.0, NOW)
    assert verdict_zero.dormant is True
    assert verdict_zero.reason == "no_evidence"
    assert verdict_zero.age_seconds == float("inf")
