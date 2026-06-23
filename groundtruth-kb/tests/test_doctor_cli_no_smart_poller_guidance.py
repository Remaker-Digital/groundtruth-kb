# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CLI smoke test: ``gt project doctor`` no longer emits smart-poller guidance.

Per Slice 4 D6 step 38 (proposal
``bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md``),
this CliRunner-based test invokes ``gt project doctor`` and asserts that:

1. No occurrence of ``verified smart poller``, ``smart-poller liveness``,
   ``Configure the smart poller``, or any pattern from D6 step 32's
   forbidden-pattern set appears in stdout.
2. Cross-harness-trigger or bridge-dispatch wording is present in the
   dispatch-related check messages.
3. The new ``_check_cross_harness_trigger`` reports a status (any of
   PASS / WARN / FAIL is acceptable; this test verifies the check runs and
   emits cross-harness-trigger wording, not a specific result).

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

# Required cross-harness-trigger wording in dispatch-related output.
_REQUIRED_DISPATCH_WORDING = (
    "cross-harness",
    "bridge dispatch",
)


def _scaffold_minimal_dual_agent(target: Path) -> None:
    """Scaffold the minimum surface a doctor smoke test needs.

    The full ``gt project init`` is heavy; for this CLI smoke test we only
    need ``groundtruth.toml`` and the bridge dirs so doctor walks the
    cross-harness-trigger and dispatch-liveness checks.
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
        "doctor output must contain at least one cross-harness-trigger or "
        f"bridge-dispatch reference; got:\n{result.output}"
    )


def test_doctor_cli_runs_cross_harness_trigger_check(tmp_path: Path) -> None:
    """The cross-harness-trigger check must run and emit a status line."""
    _scaffold_minimal_dual_agent(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["project", "doctor", "--dir", str(tmp_path)],
    )
    assert result.exit_code in (0, 1), f"unexpected exit code {result.exit_code}; output:\n{result.output}"

    # The check name "Cross-harness trigger" or similar must appear; the
    # status (PASS/WARN/FAIL) is mechanism-dependent and not asserted.
    output_lower = result.output.lower()
    assert "cross-harness" in output_lower or "cross harness" in output_lower, (
        f"cross-harness-trigger check did not run; output:\n{result.output}"
    )
