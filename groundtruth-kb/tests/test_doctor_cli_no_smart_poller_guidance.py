# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CLI smoke test: ``gt project doctor`` no longer emits smart-poller guidance.

Per Slice 4 D6 step 38 (proposal
``bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md``),
this CliRunner-based test invokes ``gt project doctor`` and asserts that:

1. No occurrence of ``verified smart poller``, ``smart-poller liveness``,
   ``Configure the smart poller``, or any pattern from D6 step 32's
   forbidden-pattern set appears in stdout.
2. Dispatcher-daemon or bridge-dispatch wording is present in the
   dispatch-related check messages.
3. The dispatcher-daemon substrate check reports a status (any of PASS / WARN /
   FAIL is acceptable; this test verifies the check runs and emits current
   dispatch wording, not a specific result).

Maps to T-4-doctor-cli-no-smart-poller-guidance.
"""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from groundtruth_kb.cli import main

# Forbidden patterns (current-use smart-poller wording, post-retirement).
# Aligned with D6 step 32 forbidden-pattern set.
_FORBIDDEN_CURRENT_USE_PATTERNS = (
    "verified smart poller",
    "smart-poller liveness",
    "Configure the smart poller",
    "configure the smart poller",
    "smart poller is unavailable",
)

_REQUIRED_DISPATCH_WORDING = (
    "dispatcher daemon",
    "bridge dispatch",
)


def _scaffold_minimal_dual_agent(target: Path) -> None:
    """Scaffold the minimum surface a doctor smoke test needs.

    The full ``gt project init`` is heavy; for this CLI smoke test we only
    need ``groundtruth.toml`` and the bridge dirs so doctor walks the
    dispatcher-daemon and dispatch-liveness checks.
    """
    (target / "groundtruth.toml").write_text(
        '[project]\nname = "_test_smoke_doctor"\nprofile = "dual-agent"\n',
        encoding="utf-8",
    )
    (target / "bridge").mkdir(parents=True, exist_ok=True)
    (target / "bridge" / "INDEX.md").write_text("# bridge index\n", encoding="utf-8")
    (target / ".gtkb-state" / "bridge-poller").mkdir(parents=True, exist_ok=True)


def test_doctor_cli_emits_no_current_use_smart_poller_guidance(tmp_path: Path) -> None:
    """``gt project doctor`` stdout must not advertise the retired smart poller."""
    _scaffold_minimal_dual_agent(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["project", "doctor", "--dir", str(tmp_path)],
    )

    # Doctor exits with 0 on PASS or 1 on findings; either is acceptable for
    # this wording assertion. The test cares about output content, not verdict.
    assert result.exit_code in (0, 1), f"unexpected exit code {result.exit_code}; output:\n{result.output}"

    output = result.output
    for pattern in _FORBIDDEN_CURRENT_USE_PATTERNS:
        assert pattern not in output, (
            f"forbidden current-use smart-poller wording found: {pattern!r}\nfull doctor output:\n{output}"
        )


def test_doctor_cli_emits_cross_harness_or_dispatch_wording(tmp_path: Path) -> None:
    """Dispatch-related check messages must reference the new mechanism."""
    _scaffold_minimal_dual_agent(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["project", "doctor", "--dir", str(tmp_path)],
    )
    assert result.exit_code in (0, 1), f"unexpected exit code {result.exit_code}; output:\n{result.output}"

    output = result.output.lower()
    assert any(needle in output for needle in _REQUIRED_DISPATCH_WORDING), (
        f"doctor output must contain at least one dispatcher-daemon or bridge-dispatch reference; got:\n{result.output}"
    )


def test_doctor_cli_runs_dispatcher_daemon_check(tmp_path: Path) -> None:
    """The dispatcher-daemon check must run and emit a status line."""
    _scaffold_minimal_dual_agent(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["project", "doctor", "--dir", str(tmp_path)],
    )
    assert result.exit_code in (0, 1), f"unexpected exit code {result.exit_code}; output:\n{result.output}"

    output_lower = result.output.lower()
    assert "dispatcher daemon" in output_lower or "dispatcher-daemon" in output_lower, (
        f"dispatcher-daemon check did not run; output:\n{result.output}"
    )
