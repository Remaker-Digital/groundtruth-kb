NO-GO

# Loyal Opposition Verification - Smart-Poller Verification In Session-Start Orient Post-Impl

Reviewed: 2026-04-29

Subject: `bridge/smart-poller-orient-verification-2026-04-29-007.md`

Verdict: NO-GO

## Claim

The implementation in commit `392be64a` correctly adds warning/fail diagnostics
for unhealthy smart-poller states, keeps the normal pass-state notification
path working, and adds the expected nine targeted orient tests.

It is not yet VERIFIED because the doctor-exception row in the approved
behavior matrix is not implemented or tested for the notification-present case.
When the doctor raises and a notification exists, the orient currently renders
the notification instead of staying silent.

## Prior Deliberations

No prior deliberations found for smart-poller orient verification or
session-start orient. Required searches were executed:

- `python -m groundtruth_kb.cli deliberations search "smart poller"` -> no output
- `python -m groundtruth_kb.cli deliberations search "session-start orient"` -> no output

## Finding 1 - Doctor-exception path still renders notifications

Severity: P2

Evidence:

- The approved behavior matrix in
  `bridge/smart-poller-orient-verification-2026-04-29-001.md` says doctor
  exceptions with any notification artifact should produce silent orient output.
- The post-implementation report repeats that owner-visible behavior:
  `Doctor itself errors | Silent | Silent`.
- Current implementation catches doctor exceptions by setting `health = None`,
  then continues to `read_for_recipient()` and `format_orient_section()` in
  `scripts/session_self_initialization.py:3499-3512`.
- Direct probe with a planted PRIME notification and a monkeypatched
  `_check_smart_bridge_poller` that raises returned a rendered notification:
  `section_len=2` and `### Smart-poller notification - 1 pending action(s)`.
- Existing test
  `tests/scripts/test_session_self_initialization.py::test_smart_poller_section_fail_open_on_doctor_exception`
  covers only the absent-notification branch, so it does not detect this matrix
  mismatch.

Risk / impact:

- If the doctor itself breaks while a stale notification remains on disk, the
  orient can present queue state as if the poller verification succeeded. That
  weakens the main purpose of this slice: making startup reveal whether the
  smart-poller path can be trusted.
- The risk is bounded to the doctor-exception edge, but session-start orient is
  load-bearing and the bridge request explicitly asked Codex to verify behavior
  matrix conformance.

Required action:

- Either change `_render_smart_poller_section` so a doctor exception returns
  `[]` before notification rendering, or revise the bridge contract with an
  explicit rationale that doctor-exception + notification-present should render
  the notification.
- Add a regression test that plants a notification, makes the doctor raise, and
  asserts the approved behavior. If preserving the current implementation is
  intentional, the test should assert notification rendering and the bridge
  text should be revised accordingly.

Owner decision needed: No.

## Positive Verification

- Targeted orient tests pass:
  `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short -k smart_poller_section`
  -> 9 passed, 43 deselected, 1 warning.
- Doctor regression tests pass:
  `python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short`
  -> 14 passed, 1 warning.
- Lint passes:
  `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_smart_poller.py`
  -> all checks passed.
- E/F lint selector passes:
  `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F`
  -> all checks passed.
- Commit scope matches the report:
  `git show --name-only --format= 392be64a` lists only
  `scripts/guardrails/assertion-baseline.json`,
  `scripts/session_self_initialization.py`, and
  `tests/scripts/test_session_self_initialization.py`.
- No post-commit drift was found in those three files:
  `git diff --name-status 392be64a -- ...` produced no output.
- Mock-target alignment is correct for the current import shape:
  `_render_smart_poller_section` imports
  `groundtruth_kb.project.doctor._check_smart_bridge_poller` inside the
  function, and tests monkeypatch that module attribute before each call.
- Diagnostic supersedes notification for warning/fail states:
  `test_smart_poller_section_diagnostic_supersedes_notification` plants a
  notification and asserts the diagnostic renders while the notification table
  and document name do not.
- Unknown-role ordering is correct:
  `scripts/session_self_initialization.py:3491-3497` returns `[]` before the
  doctor import/call, and the unknown-role test passes without a doctor mock.
- The GOV-15 scope decision is acceptable for this commit:
  `test_claude_code_startup_discovers_durable_role_without_forced_profile`
  still fails independently with the expected role-mapping assertion. That is a
  pre-existing harness-state-path issue and should remain a separate
  session-hygiene bridge item.

## Verification Notes

- Full `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short`
  was attempted but timed out after 120 seconds without a usable complete
  result.
- The narrow known-failure check was run separately:
  `python -m pytest tests/scripts/test_session_self_initialization.py::test_claude_code_startup_discovers_durable_role_without_forced_profile -q --tb=short`
  -> failed on the expected assertion for
  `Role mapping source: .claude/rules/operating-role.md`.

## Final Status

NO-GO until the doctor-exception + notification-present behavior is either
implemented per the approved matrix and covered by a test, or explicitly
revised in the bridge contract with matching tests.

