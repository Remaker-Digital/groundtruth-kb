"""Known-debt marking and strict-debt gating for the platform_tests sweep.

WI-6222 Slice 1 (`bridge/gtkb-wi6222-test-debt-triage-slice-1-002.md`, GO).

WHY THIS EXISTS. The first complete ``platform_tests`` sweep measured a large
standing failure population. Before Slice 1 there was no way to run the suite
and get an honest answer: the only options were an ad-hoc ``--ignore`` list per
invocation (which silently hides regressions) or an unfiltered run whose signal
was drowned by known debt. Every implementation report that needed regression
evidence therefore hand-crafted its own exclusions, and no two agreed.

THE CONTRACT. Modules and tests carrying ``@pytest.mark.known_debt`` are
**reported in a distinct count, never silently excluded**. They still run, still
fail, and still appear in the summary — they are simply attributed to the known
population rather than to this change. ``--strict-debt`` then makes the sweep
exit non-zero when, and only when, a failure occurs **outside** that marked set.
That is the form an implementation report can cite without exclusion flags:

    pytest --strict-debt        -> 0 when only known debt fails; non-zero on any new failure

The marker is registered here via ``addinivalue_line`` rather than in
``pyproject.toml``'s ``markers`` list because ``pyproject.toml`` is outside this
work item's authorized ``target_paths``. Registration is required regardless:
``addopts`` carries ``--strict-markers``, so an unregistered marker is an error.

WHAT THIS DOES NOT DO. It does not repair, weaken, or skip any test's substance.
Marking is inventory, not remediation, which keeps Slice 1 inside `GOV-07` /
`GOV-15` (no autonomous fixes of failing tests). Repairs are owner-prioritized
slices seeded by the triage manifest at
``.gtkb-state/test-debt/triage-manifest.json``.

Consistent with the shielding pattern in the root ``conftest.py`` and
``platform_tests/scripts/conftest.py``, this module imports no application code.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import pytest

KNOWN_DEBT_MARKER = "known_debt"

_MARKER_HELP = (
    "known_debt(reason=None): test or module belongs to the measured standing "
    "failure population (WI-6222). Reported in a distinct count and exempt from "
    "--strict-debt gating; never silently excluded from the run."
)

# Outcome buckets accumulated across the session. Keyed by nodeid so a test that
# fails in both call and teardown is counted once.
_KNOWN_DEBT_FAILURES: dict[str, str] = {}
_NEW_FAILURES: dict[str, str] = {}


def pytest_addoption(parser) -> None:
    """Register ``--strict-debt``.

    Default off so existing invocations are byte-for-byte unaffected; the flag
    is opt-in for callers that want the regression-floor semantics.
    """
    group = parser.getgroup("gtkb-test-debt", "GT-KB known-debt gating (WI-6222)")
    group.addoption(
        "--strict-debt",
        action="store_true",
        default=False,
        help=(
            "Exit non-zero only on failures OUTSIDE the known_debt-marked set. "
            "Known debt still runs and is still reported, just not gated on."
        ),
    )


def pytest_configure(config) -> None:
    """Register the ``known_debt`` marker (required under --strict-markers)."""
    config.addinivalue_line("markers", _MARKER_HELP)


def _is_known_debt(report) -> bool:
    """True when the report's test carries the ``known_debt`` marker.

    ``report.keywords`` is the reliable surface at report time: the item itself
    is not attached to the report, and keywords already include markers applied
    at function, class, and module level (``pytestmark``).
    """
    return KNOWN_DEBT_MARKER in getattr(report, "keywords", {})


def pytest_runtest_logreport(report) -> None:
    """Bucket each failure as known debt or new.

    Only genuine failures and errors are bucketed. Skips and xfails are not
    failures and must not gate; counting them would make an environment-gated
    skip look like debt.
    """
    if report.outcome != "failed":
        return
    bucket = _KNOWN_DEBT_FAILURES if _is_known_debt(report) else _NEW_FAILURES
    # First failing phase wins; a later teardown failure does not double-count.
    bucket.setdefault(report.nodeid, report.when or "call")


def pytest_terminal_summary(terminalreporter, exitstatus, config) -> None:
    """Report the two populations distinctly.

    Printed unconditionally — not only under ``--strict-debt`` — because the
    whole point is that known debt is *visible*. A silent exclusion is the
    failure mode this replaces.
    """
    known = len(_KNOWN_DEBT_FAILURES)
    new = len(_NEW_FAILURES)
    if not known and not new:
        return

    terminalreporter.write_sep("=", "GT-KB test-debt summary (WI-6222)")
    terminalreporter.write_line(f"known_debt failures : {known}")
    terminalreporter.write_line(f"new failures        : {new}")

    if new:
        terminalreporter.write_line("")
        terminalreporter.write_line("Failures outside the known_debt set:")
        for nodeid in sorted(_NEW_FAILURES):
            terminalreporter.write_line(f"  - {nodeid}")

    if config.getoption("--strict-debt"):
        verdict = "FAIL" if new else "PASS"
        terminalreporter.write_line("")
        terminalreporter.write_line(f"--strict-debt verdict: {verdict}")
    else:
        terminalreporter.write_line("")
        terminalreporter.write_line("(--strict-debt not set; exit status reflects ALL failures, known debt included)")


def pytest_sessionfinish(session, exitstatus) -> None:
    """Under ``--strict-debt``, gate the exit status on new failures only.

    Two directions, both required:

    - Known debt only -> force success. Otherwise the flag would be pointless,
      since the run would still exit non-zero on the population it exists to
      tolerate.
    - Any new failure -> force ``TESTS_FAILED``. This matters when a new failure
      is somehow not already reflected in ``exitstatus``; the gate must never be
      weaker than an ordinary run.
    """
    if not session.config.getoption("--strict-debt"):
        return

    try:
        from _pytest.config import ExitCode
    except ImportError:  # pragma: no cover - defensive across pytest versions
        return

    # Never override a non-test-failure exit (collection error, internal error,
    # user interrupt, no-tests-collected). Those are real and must surface.
    if exitstatus not in (ExitCode.OK, ExitCode.TESTS_FAILED):
        return

    session.exitstatus = ExitCode.TESTS_FAILED if _NEW_FAILURES else ExitCode.OK


def _harness_marker_env_vars() -> tuple[str, ...]:
    """Every environment variable that can select an acting harness.

    Sourced from ``RUNTIME_HARNESS_MARKERS`` rather than copied, so this cannot
    drift from the resolver it exists to neutralize. Falls back to a literal set
    if the package is not importable during collection.
    """
    names = {"GTKB_HARNESS_NAME", "GTKB_HARNESS_ID", "GTKB_SESSION_ID"}
    try:
        from groundtruth_kb.session.envelope import RUNTIME_HARNESS_MARKERS

        for markers in RUNTIME_HARNESS_MARKERS.values():
            names.update(markers)
    except Exception:  # pragma: no cover - defensive during collection
        names.update(
            {
                "ANTIGRAVITY_SESSION_ID",
                "CLAUDE_CODE_SESSION_ID",
                "CLAUDECODE",
                "CODEX_THREAD_ID",
                "CURSOR_CONVERSATION_ID",
                "GOOSE_SESSION_ID",
            }
        )
    return tuple(sorted(names))


_HARNESS_SESSION_ENV_VARS = _harness_marker_env_vars()


@pytest.fixture(autouse=True)
def _hermetic_harness_environment(monkeypatch):
    """Clear ambient harness session variables before every test.

    WI-7119 replaced the hardcoded ``--harness-name`` default of "codex" with
    resolution from whichever harness-native session variable the host set. Tests
    that intend a specific harness set their own variable, but previously also
    inherited the developer's session variable, so a test intending codex could
    resolve whichever harness the test-runner happened to be running under.

    That inheritance was always latent in these tests; the constant default merely
    hid it. No test asserts on an ambient (unset-by-test) harness variable, so
    clearing them makes each test state its own harness, which is what they
    already intended. Tests still set their own variables in the test body, which
    runs after this fixture.
    """
    for env_var in _HARNESS_SESSION_ENV_VARS:
        monkeypatch.delenv(env_var, raising=False)
