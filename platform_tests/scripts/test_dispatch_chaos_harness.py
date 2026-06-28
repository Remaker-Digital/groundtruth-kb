"""Tests for the deterministic WI-4887 dispatch chaos harness."""

from __future__ import annotations

import json
import os
import subprocess

import pytest

from scripts.ops import dispatch_chaos_harness as harness


def _report(mode: harness.FailureMode) -> harness.ChaosHarnessReport:
    return harness.run_chaos_harness(mode)


def test_chaos_matrix_covers_resilience_addendum_failure_modes() -> None:
    reports = harness.run_chaos_matrix()

    assert {report.failure_mode for report in reports} == {mode.value for mode in harness.FailureMode}
    assert len(reports) == 7


def test_each_failure_mode_has_bounded_recovery_action() -> None:
    for report in harness.run_chaos_matrix():
        assert report.detected_failure
        assert report.recovery_action
        assert report.recovery_cycle_expectation.endswith(("cycle", "expiry", "reached", "sweep"))
        assert report.final_state in {state.value for state in harness.FinalState}
        assert report.audit_events
        assert report.dispatch_control_owner == harness.DISPATCH_CONTROL_OWNER
        assert report.stub_only is True
        assert report.real_side_effects is False


def test_provider_outage_circuit_breaks_one_component_and_keeps_healthy_fleet() -> None:
    report = _report(harness.FailureMode.PROVIDER_OUTAGE)

    assert report.recovery_action == harness.RecoveryAction.PROVIDER_CIRCUIT_BREAK.value
    assert report.degraded_components == ["openrouter_provider"]
    assert set(report.healthy_components_remaining) == {"codex", "ollama"}
    assert report.final_state == harness.FinalState.DEGRADED.value


def test_daemon_death_recovery_preserves_single_owner() -> None:
    report = _report(harness.FailureMode.DAEMON_DEATH)

    assert report.daemon_owner_count == 1
    assert "single_owner_preserved" in {event["event"] for event in report.audit_events}
    assert report.final_state == harness.FinalState.RECOVERED.value


def test_daemon_death_uses_supervisor_restart_not_dispatch_directly() -> None:
    report = _report(harness.FailureMode.DAEMON_DEATH)

    assert report.recovery_action == harness.RecoveryAction.SUPERVISOR_RESTART.value
    assert report.recovery_cycle_expectation == "supervisor_ensure_alive_cycle"
    assert "work_redispatched" not in {event["event"] for event in report.audit_events}


def test_worker_hang_and_crash_are_reaped_and_redispatched() -> None:
    for mode in (harness.FailureMode.WORKER_HANG, harness.FailureMode.WORKER_CRASH):
        report = _report(mode)

        assert report.recovery_action == harness.RecoveryAction.REAP_AND_REDISPATCH.value
        assert report.redispatched is True
        assert {"claim_released", "work_redispatched"} <= {event["event"] for event in report.audit_events}


def test_spawn_storm_and_saturation_respect_one_worker_caps() -> None:
    for mode in (harness.FailureMode.SPAWN_STORM, harness.FailureMode.HARNESS_SATURATION):
        report = _report(mode)

        assert report.max_workers_by_harness
        assert max(report.max_workers_by_harness.values()) == harness.PER_HARNESS_CHAOS_CAP
        assert report.owner_alert_required is True


def test_corrupt_state_recovers_to_checkpoint_or_safe_empty_state() -> None:
    report = _report(harness.FailureMode.CORRUPT_STATE)

    assert report.recovery_action == harness.RecoveryAction.CHECKPOINT_OR_SAFE_EMPTY_RESET.value
    assert report.final_state == harness.FinalState.SAFE_EMPTY.value
    assert "state_audit_recorded" in {event["event"] for event in report.audit_events}


def test_recovery_report_contains_centralized_audit_events() -> None:
    report = _report(harness.FailureMode.WORKER_CRASH)
    payload = report.to_json_dict()

    assert payload["dispatch_control_owner"] == harness.DISPATCH_CONTROL_OWNER
    assert all(event["source"] == harness.DISPATCH_CONTROL_OWNER for event in report.audit_events)
    json.dumps(payload)


def test_cli_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = harness.main(["--scenario", "provider_outage", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["scenario"] == "provider_outage"
    assert payload["reports"][0]["failure_mode"] == "provider_outage"
    assert payload["reports"][0]["recovery_action"] == "provider_circuit_break"


def test_cli_help_mentions_stub_only_behavior(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        harness.main(["--help"])

    assert excinfo.value.code == 0
    assert "STUB-only" in capsys.readouterr().out


def test_chaos_harness_does_not_spawn_or_kill_real_processes(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_spawn(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("chaos harness must not touch real process surfaces")

    monkeypatch.setattr(subprocess, "Popen", fail_spawn)
    monkeypatch.setattr(subprocess, "run", fail_spawn)
    monkeypatch.setattr(os, "kill", fail_spawn)

    reports = harness.run_chaos_matrix()

    assert len(reports) == 7
    assert all(report.real_side_effects is False for report in reports)
