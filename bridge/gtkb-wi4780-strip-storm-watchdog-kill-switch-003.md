NEW

# gtkb-wi4780-strip-storm-watchdog-kill-switch — Post-Implementation Report (WI-4780)

bridge_kind: prime_proposal
Document: gtkb-wi4780-strip-storm-watchdog-kill-switch
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-wi4780-strip-storm-watchdog-kill-switch-002.md (GO)

author_identity: claude
author_harness_id: B
author_session_context_id: 0550e08e-1e1f-4820-bfd0-cb80d797d60b
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-WI-4780-STORM-WATCHDOG-KILL-SWITCH-STRIP-001
Project: PROJECT-GTKB-DISPATCHER-COMPLETION
Work Item: WI-4780

target_paths: ["scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_harness_storm_watchdog.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary of Implementation

Implemented the GO'd (-002) kill-switch strip in
`scripts/ops/harness_storm_watchdog.ps1`, per WI-4780 option (a) ("keep
corpse-reaping but stop asserting the global kill-switch") and
`SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`:

- Removed the `[Environment]::SetEnvironmentVariable('GTKB_NO_CROSS_HARNESS_TRIGGER', ...)`
  line from the storm-threshold branch (the set-only latch). Replaced with a
  comment citing WI-4780 / the spec / DELIB-20265877 / DELIB-20260612.
- Updated the STORM log line from `kill-switch=asserted(User)` to
  `kill-switch=not-asserted(emergency-only)` so the audit log stays accurate.
- Updated the header comment block: the watchdog NO LONGER auto-asserts the
  global kill-switch; storm protection is the verified concurrency cap
  (WI-4472); hung-worker reaping is the worker-lifetime timeout (WI-4806).
- Retained the corpse-reaping (`Stop-Process` loops), the heartbeat, and the
  log-rotate observability; the threshold detection is unchanged.

Scope note: I implemented WI-4780 option (a) (retain reaping, strip the latch).
The proposal summary prose also mentioned removing the process-kill block, but
its operational test-reconciliation list expects the threshold-detection
assertions to remain (which requires the storm branch to stay) and is silent on
removing the killing; retaining the now-secondary reaping also preserves the
`test_watchdog_never_kills_claude` safety guarantee. The spec (A.1/A.2) requires
only that the auto-kill-switch be absent and heartbeat/logrotate preserved —
both satisfied.

## Specification Links (carried forward)

- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — governing requirement;
  implemented (A.1 no auto-assert; A.2 heartbeat/logrotate preserved; A.3 cap +
  worker-timeout remain the protections).
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`.
- Advisory: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Prior Deliberations

- `DELIB-20265877` — kill-switch emergency-only directive (the mechanism this
  removes).
- `DELIB-20260612-REENABLE-AUTODISPATCH-WATCHDOG-OFF` — watchdog OFF after the
  cap was VERIFIED.
- Owner AUQ 2026-06-25 — approve spec + disable/strip direction (supersedes
  WI-4804).

## Owner Decisions / Input

Authorized by `PAUTH-WI-4780-STORM-WATCHDOG-KILL-SWITCH-STRIP-001` (owner
decisions `DELIB-20265877` + `DELIB-20260612`) plus the 2026-06-25 AUQs (spec
approval + strip direction). The LO GO (-002) authorized the change to the two
files with three conditions (dispositioned below). A further owner AUQ
2026-06-25 directed filing this report with the pre-existing failure disclosed.

## GO Conditions (from -002) — disposition

1. "Implementation report MUST include the reconciled test output (all tests in
   test_harness_storm_watchdog.py passing)." — Addressed with disclosure: 6 of 7
   pass; the 1 failure is PRE-EXISTING and unrelated (see Verification Evidence).
   Per owner AUQ 2026-06-25, this report is filed with that pre-existing failure
   disclosed rather than expanding WI-4780 scope to fix it.
2. "The grep-absent test MUST assert SetEnvironmentVariable(...kill-switch...)
   does not appear." — DONE: `test_watchdog_does_not_auto_assert_kill_switch`
   asserts exactly that.
3. "The live kill-switch serving WI-4670 MUST NOT be cleared." — HONORED: this
   change edits the script only; it does not clear the live User-scope
   assertion.

## Requirement Sufficiency

Existing requirements sufficient — `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`
governs; no new or revised requirement introduced.

## Spec-to-Test Mapping & Verification Evidence

| Spec acceptance | Test | Result |
|---|---|---|
| A.1 (no auto-assert of the kill-switch) | `test_watchdog_does_not_auto_assert_kill_switch` (grep-absent the SetEnvironmentVariable call; asserts `kill-switch=not-asserted`; asserts reaping retained) | PASS |
| A.2 (heartbeat + logrotate preserved) | reconciled `test_watchdog_preserves_heartbeat_and_logrotate` | PASS |
| A.1 (threshold detection retained without the latch) | reconciled `test_watchdog_has_noncodex_threshold_trip` | PASS |
| A.3 (reaping / never-kills-claude safety retained) | existing `test_watchdog_never_kills_claude` | PASS |

Commands and observed results (repo venv interpreter):

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_harness_storm_watchdog.py -q --no-header
  => 6 passed, 1 failed (the 1 failure is pre-existing + unrelated; see below)

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_harness_storm_watchdog.py
  => All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_harness_storm_watchdog.py
  => 1 file already formatted
```

The PowerShell script `harness_storm_watchdog.ps1` is not a Python file; it is
covered by the static-text tests above, not by ruff.

### Pre-existing unrelated failure (disclosure)

The single failing test is `test_watchdog_covers_registry_lowcost_backends`. It
is PRE-EXISTING and unrelated to this change:

- It derives the expected low-cost harness scripts from the LIVE
  `harness-state/harness-registry.json` and asserts that set equals the hardcoded
  `{"ollama_harness.py", "openrouter_harness.py"}`.
- The registry now also contains `scripts/cursor_harness.py`
  (`harness-state/harness-registry.json` line 167), added when Cursor / harness E
  was registered in commit `f64bf85d8` ("register Cursor harness E ..."), which
  predates this session.
- So `expected_scripts = {cursor, ollama, openrouter} != {ollama, openrouter}` —
  the assertion fails on the registry content, before the watchdog text is even
  checked. This change touches neither the registry nor the watchdog's
  `NONCODEX_HARNESS_SCRIPTS` detection list, so it cannot have caused the failure;
  the test fails on git HEAD too.

This is a separate drift defect (the storm-watchdog + this test do not account
for the Cursor harness; whether the watchdog SHOULD storm-watch the interactive
Cursor harness is an open design question). It is captured as a separate backlog
work item and is NOT in WI-4780 scope (kill-switch latch removal). All WI-4780
spec-derived tests (A.1-A.3) and the reconciled tests PASS.

## Acceptance Criteria Check

- A.1 no auto-assertion of the kill-switch (grep-absent) — ✓
- A.2 heartbeat + logrotate preserved — ✓
- A.3 cap (WI-4472) + worker-timeout (WI-4806) remain the protections; reaping retained — ✓
- GO condition #2 (grep-absent test) — ✓
- GO condition #3 (live kill-switch not cleared) — ✓
- GO condition #1 (all watchdog tests pass) — met for every test EXCEPT the pre-existing unrelated `test_watchdog_covers_registry_lowcost_backends` cursor-drift failure (disclosed; owner-directed to file with disclosure)

## Risk / Rollback

The change REMOVES the set-only kill-switch latch (a defect) plus comment/log
accuracy; it adds no new behavior. Worst case is loss of the now-redundant
auto-latch, covered by the VERIFIED cap (WI-4472) + worker-timeout (WI-4806).
Single-commit rollback = revert the diff (script + test bundled). The current
live kill-switch (WI-4670 emergency) is untouched.

## Recommended Commit Type

`fix` — repairs the set-only-latch defect (watchdog silently disabling
dispatch); reconciles and adds tests; no new capability surface.

## Recommended Companion Ops Action (operator, outside the diff)

Per DELIB-20260612, disable the `GTKB-HarnessStormWatchdog` scheduled task so the
watchdog is OFF (the cap + worker-timeout are the protections). The script edit
makes the watchdog safe even if the task stays enabled.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
