# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the WI-4703 non-transient dispatch fast-trip behavior.

Source: ``bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-003.md``
(Loyal Opposition GO at ``-004``). Spec-to-test mapping derives from
``GOV-AUTOMATION-VALUE-VS-COST-001``: the dispatcher must gate the expensive
re-spawn behind a cheap deterministic failure-class check, fast-tripping the
half-open circuit breaker after a SINGLE non-transient worker failure (a 401
auth failure, a worker crash/exhaustion, or a provider/guard denial) instead of
spending up to ``DEFAULT_DISPATCH_MAX_RETRIES`` expensive spawns first.

These are deliberately UNIT-level: they drive ``_process_pending_exit_codes``
and ``_matched_worker_output_markers`` directly with synthetic dispatch-run
artifacts, NOT the ``run_trigger`` integration path, so they isolate the
breaker-sensitivity behavior under test.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"

# A worker stdout result line mirroring the real headless-Claude 401 failure
# captured in .gtkb-state/bridge-poller/dispatch-runs/*.stdout.log. It contains
# BOTH fast-trip auth markers ("Invalid authentication credentials" and
# "API Error: 401").
_CLAUDE_401_RESULT_JSON = (
    '{"type":"result","subtype":"success","is_error":true,"api_error_status":401,'
    '"result":"Failed to authenticate. API Error: 401 Invalid authentication credentials",'
    '"num_turns":1}'
)


def _load_trigger() -> ModuleType:
    """Load scripts/cross_harness_bridge_trigger.py with sys.modules registration."""
    assert _SCRIPT_PATH.is_file(), f"Expected trigger at {_SCRIPT_PATH}"
    module_name = "cross_harness_bridge_trigger"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _process_one_exit_code(
    trigger: ModuleType,
    tmp_path: Path,
    *,
    recipient: str = "prime-builder:B",
    exit_code: int,
    stdout_text: str = "",
    stderr_text: str = "",
    initial_failure_count: int = 0,
    initial_breaker_tripped: bool = False,
    needed_role_label: str = "prime-builder",
) -> dict[str, Any]:
    """Drive ``_process_pending_exit_codes`` for one synthetic dispatch run.

    Builds a ``dispatch-runs`` artifact set (exit_code + stdout/stderr logs) plus
    a single-recipient state whose ``last_launch`` references it, processes it,
    and returns the post-processing recipient_state.
    """
    state_dir = tmp_path / "state"
    runs_dir = state_dir / trigger.DISPATCH_RUNS_SUBDIR
    runs_dir.mkdir(parents=True, exist_ok=True)

    dispatch_id = "fast-trip-test-dispatch"
    stdout_path = runs_dir / f"{dispatch_id}.stdout.log"
    stderr_path = runs_dir / f"{dispatch_id}.stderr.log"
    stdout_path.write_text(stdout_text, encoding="utf-8")
    stderr_path.write_text(stderr_text, encoding="utf-8")
    (runs_dir / f"{dispatch_id}.exit_code").write_text(str(exit_code), encoding="utf-8")

    recipient_state: dict[str, Any] = {
        "failure_count": initial_failure_count,
        "circuit_breaker_tripped": initial_breaker_tripped,
        "last_result": "launched",
        "last_launch": {
            "dispatch_id": dispatch_id,
            "recipient": recipient,
            "launched": True,
            "launched_at": "2026-06-20T22:00:00+00:00",
            "signature": "sig-under-test",
            "needed_role_label": needed_role_label,
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
        },
    }
    recipients_state = {recipient: recipient_state}
    trigger._process_pending_exit_codes(recipients_state, state_dir, project_root=tmp_path)
    return recipients_state[recipient]


def test_401_output_is_classified_as_auth_failure(tmp_path: Path) -> None:
    """GOV-AUTOMATION-VALUE-VS-COST-001: a headless-Claude 401 result is
    classified as the non-transient ``auth_failure`` class by the worker-output
    marker scanner (covers both stdout and stderr)."""
    trigger = _load_trigger()
    runs_dir = tmp_path / "dispatch-runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = runs_dir / "d.stdout.log"
    stdout_path.write_text(_CLAUDE_401_RESULT_JSON, encoding="utf-8")

    launch = {"stdout_path": str(stdout_path), "stderr_path": ""}
    matched, _inspected = trigger._matched_worker_output_markers(launch)

    assert matched, "expected the 401 result to match a fatal worker-output marker"
    assert {m["label"] for m in matched} == {"auth_failure"}
    assert "auth_failure" in trigger.FAST_TRIP_FAILURE_CLASSES


def test_auth_failure_fast_trips_breaker_at_first_failure(tmp_path: Path) -> None:
    """A single ``auth_failure`` (401) failure trips the circuit breaker after
    ONE failure — the expensive re-spawn is braked immediately rather than after
    DEFAULT_DISPATCH_MAX_RETRIES."""
    trigger = _load_trigger()
    state = _process_one_exit_code(
        trigger,
        tmp_path,
        exit_code=1,
        stdout_text=_CLAUDE_401_RESULT_JSON,
    )
    assert state["failure_count"] == 1
    assert state["circuit_breaker_tripped"] is True
    assert state["last_failure_reason"] == "auth_failure"


def test_max_turn_exhaustion_fast_trips_breaker(tmp_path: Path) -> None:
    """A single ``max_turn_exhaustion`` worker failure fast-trips the breaker
    after one failure (it fails identically on re-spawn)."""
    trigger = _load_trigger()
    state = _process_one_exit_code(
        trigger,
        tmp_path,
        exit_code=1,
        stderr_text="ollama_harness: max-turn exhaustion before final assistant text\n",
    )
    assert state["failure_count"] == 1
    assert state["circuit_breaker_tripped"] is True
    assert state["last_failure_reason"] == "max_turn_exhaustion"


def test_generic_failure_does_not_fast_trip_and_trips_at_normal_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A generic ``subprocess_execution_failed`` (no fatal marker) is NOT
    fast-trip class: it does not trip at failure_count 1 and still trips only at
    the normal DEFAULT_DISPATCH_MAX_RETRIES threshold."""
    trigger = _load_trigger()
    monkeypatch.setattr(trigger, "_dispatch_max_retries", lambda: 3)

    # First generic failure (no marker, empty logs): failure_count 1, NOT tripped.
    state_first = _process_one_exit_code(trigger, tmp_path / "a", exit_code=1)
    assert state_first["failure_count"] == 1
    assert state_first["circuit_breaker_tripped"] is False
    assert state_first["last_failure_reason"] == "subprocess_execution_failed"

    # Reaching the normal threshold (failure_count 2 -> 3) DOES trip it.
    state_third = _process_one_exit_code(trigger, tmp_path / "b", exit_code=1, initial_failure_count=2)
    assert state_third["failure_count"] == 3
    assert state_third["circuit_breaker_tripped"] is True


def test_success_resets_failure_count_and_breaker_after_fast_trip(tmp_path: Path) -> None:
    """Half-open recovery / success-reset is unchanged: a successful dispatch
    (exit 0, no fatal marker) on a previously fast-tripped recipient clears the
    failure_count and the breaker, so dispatch self-heals once the cause is
    fixed."""
    trigger = _load_trigger()
    state = _process_one_exit_code(
        trigger,
        tmp_path,
        exit_code=0,
        initial_failure_count=5,
        initial_breaker_tripped=True,
        needed_role_label="prime-builder",
    )
    assert state["failure_count"] == 0
    assert state["circuit_breaker_tripped"] is False
    assert "circuit_breaker_tripped_at" not in state


def test_fast_trip_does_not_set_non_retryable_failure(tmp_path: Path) -> None:
    """The fast-trip uses the half-open circuit breaker, NOT the permanent
    ``non_retryable_failure`` path: an ``auth_failure`` trips the breaker but
    must NOT mark the recipient non-retryable (which would permanently disable
    it until reset)."""
    trigger = _load_trigger()
    state = _process_one_exit_code(
        trigger,
        tmp_path,
        exit_code=1,
        stdout_text=_CLAUDE_401_RESULT_JSON,
    )
    assert state["circuit_breaker_tripped"] is True
    assert state.get("non_retryable_failure") is not True
    assert "auth_failure" not in trigger.NON_RETRYABLE_WORKER_FAILURE_CLASSES
