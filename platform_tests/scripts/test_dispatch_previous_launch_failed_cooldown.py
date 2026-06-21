# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""WI-4662: cooldown-gated previous_launch_failed re-log + lo_failover_exhausted.

Spec-to-test mapping (proposal
``bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-001.md``):

- GOV-AUTOMATION-VALUE-VS-COST-001 — the durable re-log is throttled to one row
  per cooldown window, while the in-memory health annotation is set every cycle.
- Recovery clears the cooldown stamp so a re-failed target re-logs immediately.
- The exhausted ranked-LO failover is a bounded terminal record, not a re-log;
  multi-active / non-failure exhaustion does NOT become lo_failover_exhausted.

The cooldown core (``_should_relog_previous_launch_failure``), the failover-
exhaustion decision (``_is_lo_failover_exhausted``), the durable re-log throttle
at a real record site (``_provider_failure_backoff_skip``), and the recovery
clear (``_process_pending_exit_codes`` success branch) are exercised directly.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "cross_harness_bridge_trigger.py"


def _load_trigger() -> ModuleType:
    module_name = "cross_harness_bridge_trigger"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _iso(moment: datetime) -> str:
    return moment.isoformat().replace("+00:00", "Z")


def _read_failure_rows(failures_path: Path) -> list[dict]:
    if not failures_path.is_file():
        return []
    return [json.loads(line) for line in failures_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _previous_launch_failed_rows(failures_path: Path) -> list[dict]:
    return [row for row in _read_failure_rows(failures_path) if row.get("reason") == "previous_launch_failed"]


# --- _should_relog_previous_launch_failure (cooldown core) -------------------


def test_should_relog_true_when_no_stamp() -> None:
    trigger = _load_trigger()
    assert trigger._should_relog_previous_launch_failure({}) is True


def test_should_relog_respects_cooldown_window(monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.setenv("GTKB_DISPATCH_RETRY_DELAY_SECONDS", "300")
    now = datetime(2026, 6, 21, 12, 0, 0, tzinfo=UTC)
    state = {"previous_launch_failed_logged_at": _iso(now)}
    # Fresh + within window -> suppressed.
    assert trigger._should_relog_previous_launch_failure(state, now=now) is False
    assert trigger._should_relog_previous_launch_failure(state, now=now + timedelta(seconds=299)) is False
    # At/after the window -> re-log allowed again.
    assert trigger._should_relog_previous_launch_failure(state, now=now + timedelta(seconds=300)) is True
    assert trigger._should_relog_previous_launch_failure(state, now=now + timedelta(seconds=400)) is True


def test_should_relog_true_when_stamp_unparseable() -> None:
    trigger = _load_trigger()
    # Fail-open to re-log (never silently suppress) on a malformed stamp.
    assert trigger._should_relog_previous_launch_failure({"previous_launch_failed_logged_at": "not-a-time"}) is True


# --- durable re-log throttle at a real record site ---------------------------


def test_backoff_skip_throttles_relog_and_keeps_annotation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    trigger = _load_trigger()
    monkeypatch.setenv("GTKB_DISPATCH_RETRY_DELAY_SECONDS", "300")
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    failures = state_dir / trigger.DISPATCH_FAILURES_FILENAME

    # A prior with a non-zero exit code is detected as a previous launch failure;
    # non_retryable_failure forces the deterministic record branch.
    prior: dict = {
        "last_launch": {"launched": True, "exit_code": 1, "dispatch_id": "d1"},
        "non_retryable_failure": True,
    }

    skip1 = trigger._provider_failure_backoff_skip(
        prior=prior, recipient="loyal-opposition:A", signature="sig1", state_dir=state_dir
    )
    assert skip1 is not None
    assert skip1["reason"] == "provider_failure_backoff_active"
    assert "previous_launch_failed" in skip1  # in-memory annotation present
    assert "previous_launch_failed_logged_at" in prior  # cooldown stamp set on emit
    assert len(_previous_launch_failed_rows(failures)) == 1

    # Second cycle within the cooldown window: NO new durable row, annotation kept.
    skip2 = trigger._provider_failure_backoff_skip(
        prior=prior, recipient="loyal-opposition:A", signature="sig1", state_dir=state_dir
    )
    assert skip2 is not None
    assert "previous_launch_failed" in skip2  # annotation set every cycle
    assert len(_previous_launch_failed_rows(failures)) == 1  # throttled

    # Advance the stamp past the cooldown -> re-log resumes.
    prior["previous_launch_failed_logged_at"] = _iso(datetime.now(UTC) - timedelta(seconds=301))
    trigger._provider_failure_backoff_skip(
        prior=prior, recipient="loyal-opposition:A", signature="sig1", state_dir=state_dir
    )
    assert len(_previous_launch_failed_rows(failures)) == 2


# --- recovery clears the cooldown stamp --------------------------------------


def test_recovery_clears_previous_launch_failed_stamp(tmp_path: Path) -> None:
    trigger = _load_trigger()
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    runs_dir = state_dir / trigger.DISPATCH_RUNS_SUBDIR
    runs_dir.mkdir(parents=True)
    (runs_dir / "d1.exit_code").write_text("0", encoding="utf-8")

    recipients_state: dict = {
        "prime-builder:B": {
            "last_launch": {
                "launched": True,
                "dispatch_id": "d1",
                "signature": "sig",
                "needed_role_label": "prime-builder",
            },
            "previous_launch_failed_logged_at": "2026-06-21T00:00:00Z",
            "previous_launch_failed": {"reason": "previous_launch_failed"},
            "failure_count": 3,
            "circuit_breaker_tripped": True,
        }
    }

    trigger._process_pending_exit_codes(recipients_state, state_dir, tmp_path)

    state = recipients_state["prime-builder:B"]
    # WI-4662: the recovery branch clears the cooldown stamp + annotation.
    assert "previous_launch_failed_logged_at" not in state
    assert "previous_launch_failed" not in state
    # Existing recovery behavior is preserved.
    assert state["failure_count"] == 0
    assert state["circuit_breaker_tripped"] is False


# --- lo_failover_exhausted decision (terminal vs re-log) ----------------------


def test_lo_failover_exhausted_true_for_lo_with_failure_skip() -> None:
    trigger = _load_trigger()
    for skipped in (
        {"reason": "provider_failure_backoff_active", "backoff_source": "non_retryable_worker_failure"},
        {"reason": "previous_launch_failed"},
    ):
        skipped["recipient"] = "loyal-opposition:D"
        assert trigger._is_lo_failover_exhausted("no_ready_target_for_role", "loyal-opposition", [skipped]) is True, (
            skipped
        )


def test_lo_failover_exhausted_false_for_non_failure_or_non_lo() -> None:
    trigger = _load_trigger()
    backoff = [{"reason": "provider_failure_backoff_active"}]
    # A target was selected (no failure_reason) -> not exhausted (WI-4484 path).
    assert trigger._is_lo_failover_exhausted(None, "loyal-opposition", backoff) is False
    # Prime-builder lane is out of scope for the LO-specific terminal.
    assert trigger._is_lo_failover_exhausted("no_ready_target_for_role", "prime-builder", backoff) is False
    # Exhaustion with only a not-ready (non-failure) skip stays no_ready_target_for_role.
    not_ready = [{"reason": "codex_dispatch_not_ready"}]
    assert trigger._is_lo_failover_exhausted("no_ready_target_for_role", "loyal-opposition", not_ready) is False
    retry_delay = [{"reason": "provider_failure_backoff_active", "backoff_source": "retry_delay_enforced"}]
    assert trigger._is_lo_failover_exhausted("no_ready_target_for_role", "loyal-opposition", retry_delay) is False
    # No skipped candidates at all.
    assert trigger._is_lo_failover_exhausted("no_ready_target_for_role", "loyal-opposition", []) is False
    assert trigger._is_lo_failover_exhausted("no_ready_target_for_role", "loyal-opposition", None) is False


def test_lo_provider_backoff_hold_reason_preserves_retry_delay() -> None:
    trigger = _load_trigger()
    skipped = [{"reason": "provider_failure_backoff_active", "backoff_source": "retry_delay_enforced"}]
    assert (
        trigger._lo_provider_backoff_hold_reason("no_ready_target_for_role", "loyal-opposition", skipped)
        == "retry_delay_enforced"
    )


# --- end-to-end run_trigger integration ---------------------------------------

_CODEX_INVOCATION_SURFACES = {"headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}}
_CLAUDE_INVOCATION_SURFACES = {
    "headless": {"argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]}
}


def _make_failover_project(root: Path) -> Path:
    """Minimal synthetic GT-KB project for sole-active-LO failover test."""
    (root / "groundtruth.toml").write_text(
        '[project]\nproject_name = "TestSynthetic"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (root / "bridge").mkdir(exist_ok=True)
    hs = root / "harness-state"
    hs.mkdir(exist_ok=True)
    (hs / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"claude": {"id": "B"}, "codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (hs / "role-assignments.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    "B": {"role": "prime-builder", "harness_type": "claude"},
                    "A": {"role": "loyal-opposition", "harness_type": "codex"},
                },
            }
        ),
        encoding="utf-8",
    )
    (hs / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["loyal-opposition"],
                        "invocation_surfaces": _CODEX_INVOCATION_SURFACES,
                    },
                    {
                        "id": "B",
                        "harness_name": "claude",
                        "harness_type": "claude",
                        "status": "active",
                        "event_driven_hooks": True,
                        "role": ["prime-builder"],
                        "invocation_surfaces": _CLAUDE_INVOCATION_SURFACES,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return root


def test_sole_active_lo_in_backoff_produces_lo_failover_exhausted_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """run_trigger with sole active LO in non_retryable backoff must emit lo_failover_exhausted.

    Regression for WI-4662: the `if target_index < len(targets) - 1` guard prevented
    _provider_failure_backoff_skip from running on the sole/last target, so the
    lo_failover_exhausted path was unreachable with a single active LO target.
    """
    trigger = _load_trigger()
    # Bypass conftest autouse fixture that overrides GTKB_HARNESS_REGISTRY_PATH.
    monkeypatch.delenv("GTKB_HARNESS_REGISTRY_PATH", raising=False)
    # Ensure loop prevention is off.
    monkeypatch.delenv(trigger.LOOP_PREVENTION_ENV_VAR, raising=False)

    root = tmp_path / "proj"
    root.mkdir()
    _make_failover_project(root)

    state_dir = tmp_path / "state"
    state_dir.mkdir()

    # Pre-seed a non-retryable failure for the sole LO target (harness A).
    (state_dir / trigger.DISPATCH_STATE_FILENAME).write_text(
        json.dumps(
            {
                "recipients": {
                    "loyal-opposition:A": {
                        "last_launch": {"launched": True, "exit_code": 1, "dispatch_id": "seed-d1"},
                        "non_retryable_failure": True,
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    # Write a NEW (LO-actionable) bridge entry so there is actionable work.
    bridge_file = root / "bridge" / "failover-test-001.md"
    bridge_file.write_text(
        "NEW\n\nauthor_session_context_id: fixture-author-session\n",
        encoding="utf-8",
    )
    (root / "bridge" / "INDEX.md").write_text(
        "# bridge index\n\nDocument: failover-test\nNEW: bridge/failover-test-001.md\n",
        encoding="utf-8",
    )

    summary = trigger.run_trigger(project_root=root, state_dir=state_dir, dry_run=True)

    assert not summary.get("skipped"), f"run_trigger skipped unexpectedly: {summary.get('reason')}"

    recipients = summary.get("dispatch_state", {}).get("recipients", {})
    lo_state = recipients.get("loyal-opposition", {})
    assert lo_state.get("last_result") == "lo_failover_exhausted", (
        f"expected lo_failover_exhausted, got {lo_state.get('last_result')!r}"
    )

    results = summary.get("results", {})
    lo_result = results.get("loyal-opposition", {})
    assert lo_result.get("launched") is False
    assert lo_result.get("reason") == "lo_failover_exhausted"

    # Exactly one lo_failover_exhausted row in the cooldown window.
    failures_path = state_dir / trigger.DISPATCH_FAILURES_FILENAME
    rows = _read_failure_rows(failures_path)
    lo_exhausted = [r for r in rows if r.get("reason") == "lo_failover_exhausted"]
    assert len(lo_exhausted) == 1, f"expected 1 lo_failover_exhausted row, got {len(lo_exhausted)}: {rows}"
