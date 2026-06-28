#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Deterministic STUB dispatch chaos harness for WI-4887.

This harness models daemon-resilience failure handling without starting the
live dispatcher, invoking real harnesses, killing processes, or spending
provider calls. It returns JSON-ready recovery reports for focused regression
tests and future dispatcher health integration.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from enum import StrEnum

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
DISPATCH_CONTROL_OWNER = "central_dispatch_service"
PER_HARNESS_CHAOS_CAP = 1


class FailureMode(StrEnum):
    DAEMON_DEATH = "daemon_death"
    WORKER_HANG = "worker_hang"
    WORKER_CRASH = "worker_crash"
    SPAWN_STORM = "spawn_storm"
    CORRUPT_STATE = "corrupt_state"
    HARNESS_SATURATION = "harness_saturation"
    PROVIDER_OUTAGE = "provider_outage"


class RecoveryAction(StrEnum):
    SUPERVISOR_RESTART = "supervisor_restart"
    REAP_AND_REDISPATCH = "reap_and_redispatch"
    SUPPRESS_SPAWN_STORM = "suppress_spawn_storm"
    CHECKPOINT_OR_SAFE_EMPTY_RESET = "checkpoint_or_safe_empty_reset"
    CAP_BACKOFF = "cap_backoff"
    PROVIDER_CIRCUIT_BREAK = "provider_circuit_break"


class FinalState(StrEnum):
    RECOVERED = "recovered"
    DEGRADED = "degraded"
    SAFE_EMPTY = "safe_empty"


@dataclass(frozen=True)
class ChaosScenario:
    failure_mode: FailureMode
    detected_failure: str
    recovery_action: RecoveryAction
    recovery_cycle_expectation: str
    final_state: FinalState
    degraded_components: tuple[str, ...]
    healthy_components_remaining: tuple[str, ...]
    owner_alert_required: bool
    audit_steps: tuple[str, ...]
    daemon_owner_count: int = 1
    max_workers_by_harness: dict[str, int] | None = None
    redispatched: bool = False


@dataclass(frozen=True)
class ChaosHarnessReport:
    failure_mode: str
    detected_failure: str
    recovery_action: str
    recovery_cycle_expectation: str
    final_state: str
    degraded_components: list[str]
    healthy_components_remaining: list[str]
    owner_alert_required: bool
    audit_events: list[dict[str, object]]
    daemon_owner_count: int
    max_workers_by_harness: dict[str, int]
    redispatched: bool
    dispatch_control_owner: str = DISPATCH_CONTROL_OWNER
    stub_only: bool = True
    real_side_effects: bool = False

    def to_json_dict(self) -> dict[str, object]:
        return {
            "failure_mode": self.failure_mode,
            "detected_failure": self.detected_failure,
            "recovery_action": self.recovery_action,
            "recovery_cycle_expectation": self.recovery_cycle_expectation,
            "final_state": self.final_state,
            "degraded_components": self.degraded_components,
            "healthy_components_remaining": self.healthy_components_remaining,
            "owner_alert_required": self.owner_alert_required,
            "audit_events": self.audit_events,
            "daemon_owner_count": self.daemon_owner_count,
            "max_workers_by_harness": self.max_workers_by_harness,
            "redispatched": self.redispatched,
            "dispatch_control_owner": self.dispatch_control_owner,
            "stub_only": self.stub_only,
            "real_side_effects": self.real_side_effects,
        }


_ONE_WORKER_CAPS = {
    "codex": PER_HARNESS_CHAOS_CAP,
    "cursor": PER_HARNESS_CHAOS_CAP,
    "ollama": PER_HARNESS_CHAOS_CAP,
    "openrouter": PER_HARNESS_CHAOS_CAP,
}

SCENARIO_CATALOG: dict[FailureMode, ChaosScenario] = {
    FailureMode.DAEMON_DEATH: ChaosScenario(
        failure_mode=FailureMode.DAEMON_DEATH,
        detected_failure="daemon heartbeat missing",
        recovery_action=RecoveryAction.SUPERVISOR_RESTART,
        recovery_cycle_expectation="supervisor_ensure_alive_cycle",
        final_state=FinalState.RECOVERED,
        degraded_components=(),
        healthy_components_remaining=("dispatcher_queue", "bridge_state"),
        owner_alert_required=False,
        audit_steps=(
            "failure_detected",
            "supervisor_restart_requested",
            "single_owner_preserved",
            "daemon_ready",
        ),
    ),
    FailureMode.WORKER_HANG: ChaosScenario(
        failure_mode=FailureMode.WORKER_HANG,
        detected_failure="worker lifetime cap exceeded",
        recovery_action=RecoveryAction.REAP_AND_REDISPATCH,
        recovery_cycle_expectation="worker_lifetime_cap_expiry",
        final_state=FinalState.RECOVERED,
        degraded_components=("hung_worker",),
        healthy_components_remaining=("codex", "ollama", "openrouter"),
        owner_alert_required=False,
        audit_steps=("failure_detected", "hung_worker_reaped", "claim_released", "work_redispatched"),
        redispatched=True,
    ),
    FailureMode.WORKER_CRASH: ChaosScenario(
        failure_mode=FailureMode.WORKER_CRASH,
        detected_failure="worker exited non-zero",
        recovery_action=RecoveryAction.REAP_AND_REDISPATCH,
        recovery_cycle_expectation="watchdog_recovery_cycle",
        final_state=FinalState.RECOVERED,
        degraded_components=("crashed_worker",),
        healthy_components_remaining=("codex", "ollama", "openrouter"),
        owner_alert_required=False,
        audit_steps=("failure_detected", "crashed_worker_reaped", "claim_released", "work_redispatched"),
        redispatched=True,
    ),
    FailureMode.SPAWN_STORM: ChaosScenario(
        failure_mode=FailureMode.SPAWN_STORM,
        detected_failure="spawn attempts exceeded per-harness cap",
        recovery_action=RecoveryAction.SUPPRESS_SPAWN_STORM,
        recovery_cycle_expectation="storm_watchdog_cycle",
        final_state=FinalState.DEGRADED,
        degraded_components=("storming_harness",),
        healthy_components_remaining=("non_storming_harnesses",),
        owner_alert_required=True,
        audit_steps=("failure_detected", "spawn_cap_enforced", "storm_suppressed", "owner_alert_marked"),
        max_workers_by_harness=_ONE_WORKER_CAPS,
    ),
    FailureMode.CORRUPT_STATE: ChaosScenario(
        failure_mode=FailureMode.CORRUPT_STATE,
        detected_failure="daemon state checksum mismatch",
        recovery_action=RecoveryAction.CHECKPOINT_OR_SAFE_EMPTY_RESET,
        recovery_cycle_expectation="daemon_lifecycle_sweep",
        final_state=FinalState.SAFE_EMPTY,
        degraded_components=("daemon_state_cache",),
        healthy_components_remaining=("bridge_files", "harness_registry"),
        owner_alert_required=True,
        audit_steps=(
            "failure_detected",
            "checkpoint_restore_attempted",
            "safe_empty_reset_selected",
            "state_audit_recorded",
        ),
    ),
    FailureMode.HARNESS_SATURATION: ChaosScenario(
        failure_mode=FailureMode.HARNESS_SATURATION,
        detected_failure="eligible harness fleet saturated",
        recovery_action=RecoveryAction.CAP_BACKOFF,
        recovery_cycle_expectation="fleet_saturation_backoff_cycle",
        final_state=FinalState.DEGRADED,
        degraded_components=("saturated_harness_pool",),
        healthy_components_remaining=("queue_intake", "degraded_status_surface"),
        owner_alert_required=True,
        audit_steps=("failure_detected", "worker_cap_enforced", "backoff_selected", "degraded_status_recorded"),
        max_workers_by_harness=_ONE_WORKER_CAPS,
    ),
    FailureMode.PROVIDER_OUTAGE: ChaosScenario(
        failure_mode=FailureMode.PROVIDER_OUTAGE,
        detected_failure="provider route unavailable",
        recovery_action=RecoveryAction.PROVIDER_CIRCUIT_BREAK,
        recovery_cycle_expectation="provider_failure_threshold_reached",
        final_state=FinalState.DEGRADED,
        degraded_components=("openrouter_provider",),
        healthy_components_remaining=("codex", "ollama"),
        owner_alert_required=True,
        audit_steps=("failure_detected", "provider_circuit_break_opened", "healthy_fleet_reroute_recorded"),
    ),
}


def _audit_events(scenario: ChaosScenario) -> list[dict[str, object]]:
    return [
        {
            "event": step,
            "sequence": index + 1,
            "failure_mode": scenario.failure_mode.value,
            "source": DISPATCH_CONTROL_OWNER,
        }
        for index, step in enumerate(scenario.audit_steps)
    ]


def run_chaos_harness(failure_mode: FailureMode | str) -> ChaosHarnessReport:
    """Run one deterministic STUB chaos scenario."""
    mode = FailureMode(failure_mode)
    scenario = SCENARIO_CATALOG[mode]
    max_workers = scenario.max_workers_by_harness or {
        "codex": PER_HARNESS_CHAOS_CAP,
        "ollama": PER_HARNESS_CHAOS_CAP,
    }
    return ChaosHarnessReport(
        failure_mode=scenario.failure_mode.value,
        detected_failure=scenario.detected_failure,
        recovery_action=scenario.recovery_action.value,
        recovery_cycle_expectation=scenario.recovery_cycle_expectation,
        final_state=scenario.final_state.value,
        degraded_components=list(scenario.degraded_components),
        healthy_components_remaining=list(scenario.healthy_components_remaining),
        owner_alert_required=scenario.owner_alert_required,
        audit_events=_audit_events(scenario),
        daemon_owner_count=scenario.daemon_owner_count,
        max_workers_by_harness=dict(max_workers),
        redispatched=scenario.redispatched,
    )


def run_chaos_matrix() -> list[ChaosHarnessReport]:
    """Run all deterministic STUB chaos scenarios."""
    return [run_chaos_harness(mode) for mode in FailureMode]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run deterministic STUB-only dispatcher chaos scenarios for WI-4887.")
    parser.add_argument(
        "--scenario",
        choices=[mode.value for mode in FailureMode] + ["all"],
        default="all",
        help="Failure mode to model, or all scenarios.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    reports = run_chaos_matrix() if args.scenario == "all" else [run_chaos_harness(args.scenario)]
    payload: dict[str, object] = {
        "scenario": args.scenario,
        "reports": [report.to_json_dict() for report in reports],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for report in reports:
            print(
                "{failure_mode}: {recovery_action} -> {final_state}".format(
                    **report.to_json_dict(),
                )
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
