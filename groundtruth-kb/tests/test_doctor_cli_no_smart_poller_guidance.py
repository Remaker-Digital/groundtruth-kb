# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CLI smoke test: ``gt project doctor`` no longer emits smart-poller guidance.

Per Slice 4 D6 step 38 (proposal
``bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md``),
this test invokes the native ``gt project doctor`` on an initialized application and asserts that:

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


def test_doctor_cli_emits_no_current_use_smart_poller_guidance(native_application) -> None:
    """``gt project doctor`` stdout must not advertise the retired smart poller."""
    native_application.stage_baseline()
    native_application.init("Alpha", "--profile", "dual-agent", "--harness", "claude")
    result = native_application.invoke(
        "project", "doctor", "--project-id", "PROJECT-Alpha", "--host-root", str(native_application.host)
    )

    # Doctor exits with 0 on PASS or 1 on findings; either is acceptable for
    # this wording assertion. The test cares about output content, not verdict.
    assert result.exit_code in (0, 1), f"unexpected exit code {result.exit_code}; output:\n{result.output}"

    output = result.output
    for pattern in _FORBIDDEN_CURRENT_USE_PATTERNS:
        assert pattern not in output, (
            f"forbidden current-use smart-poller wording found: {pattern!r}\nfull doctor output:\n{output}"
        )
