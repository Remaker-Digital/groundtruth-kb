VERIFIED

# Loyal Opposition Verification - Smart-Poller Verification In Session-Start Orient REVISED-1

Reviewed: 2026-04-29

Subject: `bridge/smart-poller-orient-verification-2026-04-29-009.md`

Verdict: VERIFIED

## Claim

The REVISED-1 implementation in commit `fc98ca87` closes the single P2 finding
from `-008`. `_render_smart_poller_section` now returns `[]` immediately when
the smart-poller doctor raises or cannot be imported, so stale notifications do
not render when the verification layer itself is broken.

## Prior Deliberations

No prior deliberations found for smart-poller orient verification or
session-start orient. Required searches were executed:

- `python -m groundtruth_kb.cli deliberations search "smart poller"` -> no output
- `python -m groundtruth_kb.cli deliberations search "session-start orient"` -> no output

## Finding Closure

### Finding 1 - Doctor-exception path still renders notifications - CLOSED

Evidence:

- `scripts/session_self_initialization.py:3506-3513` catches doctor exceptions
  by setting `health = None`, then immediately returns `[]` before
  notification reading.
- `tests/scripts/test_session_self_initialization.py:1955-1999` adds
  `test_smart_poller_section_silent_on_doctor_exception_with_notification_present`.
  The test plants a PRIME notification, monkeypatches
  `groundtruth_kb.project.doctor._check_smart_bridge_poller` to raise, and
  asserts `_render_smart_poller_section(...) == []`.
- Direct probe matching the `-008` failure mode now returns:
  `section_len=0`, `section=[]`.

Risk / impact:

- The stale-notification edge from `-008` is resolved. When the doctor fails,
  startup stays silent rather than presenting unverified queue state as fresh
  smart-poller evidence.

Recommended action:

- No further action required for this bridge thread.

Owner decision needed: No.

## Verification Commands

- `python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short -k smart_poller_section`
  -> 10 passed, 43 deselected, 1 warning.
- `python -m pytest groundtruth-kb/tests/test_doctor_smart_poller.py -q --tb=short`
  -> 14 passed, 1 warning.
- `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F`
  -> all checks passed.
- `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_smart_poller.py`
  -> all checks passed.

## Matrix Verification

The approved `-001 §3.1` matrix is now implemented:

- doctor `pass` + notification present -> notification renders.
- doctor `pass` + notification absent/empty -> silent.
- doctor `warning` + any notification state -> diagnostic.
- doctor `fail` + any notification state -> diagnostic.
- doctor exception + notification present -> silent.
- doctor exception + notification absent -> silent.

## Scope Verification

- Commit `fc98ca87` modifies only:
  - `scripts/guardrails/assertion-baseline.json`
  - `scripts/session_self_initialization.py`
  - `tests/scripts/test_session_self_initialization.py`
- The prior nine targeted orient tests still pass, and the new tenth test covers
  the exact notification-present doctor-exception regression from `-008`.
- The doctor module and diagnostic renderer behavior are unchanged by this
  revision.
- The pre-existing
  `test_claude_code_startup_discovers_durable_role_without_forced_profile`
  failure remains outside this bridge thread and is being handled through the
  separate session-hygiene drift-triage bridge entry.

## Final Status

VERIFIED.

