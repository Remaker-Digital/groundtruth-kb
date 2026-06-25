NEW

# gtkb-wi4780-strip-storm-watchdog-kill-switch — Strip the storm-watchdog auto-assertion of the cross-harness kill-switch

bridge_kind: prime_proposal
Document: gtkb-wi4780-strip-storm-watchdog-kill-switch
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-25 UTC

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

## Summary

`scripts/ops/harness_storm_watchdog.ps1` (line 64) auto-asserts the
`GTKB_NO_CROSS_HARNESS_TRIGGER` cross-harness dispatch kill-switch at User scope
inside its storm-threshold branch and never clears it — a set-only latch. A
transient ~1-minute process spike therefore silently disables ALL cross-harness
dispatch indefinitely (the recurring "dispatch-dead" incidents of 2026-06-21 and
2026-06-24). This violates the owner directive that the kill-switch is
emergency-only and congestion is not failure (DELIB-20265877), and contradicts
the prior owner decision to run with the watchdog OFF once the concurrency cap
was VERIFIED (DELIB-20260612).

Per `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`, no automated mechanism may
assert the kill-switch on a congestion threshold. The two protections the
watchdog was bridging are now durable elsewhere: storm protection is the VERIFIED
global concurrency cap (WI-4472, default 8), and hung-worker reaping is the
VERIFIED worker-lifetime timeout in `run_with_status.py` (WI-4806, committed). The
watchdog's auto-kill-switch is therefore redundant.

This proposal removes the auto-assertion of `GTKB_NO_CROSS_HARNESS_TRIGGER` (and
the now-redundant storm process-kill block it guards) from the watchdog script,
preserving the heartbeat and log-rotate observability. It reconciles the two
existing tests that assert the kill-switch is present and adds a grep-absent
regression test. It does NOT clear the current live kill-switch, which is serving
the active WI-4670 emergency (cloud LO fleet down); that is cleared separately
when WI-4670 is resolved.

Recommended companion ops action (outside the repo diff, noted for the operator):
re-apply DELIB-20260612 by disabling the `GTKB-HarnessStormWatchdog` scheduled
task. The script edit makes the watchdog safe even if the task remains enabled.

## Specification Links

- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` — the governing requirement; the
  kill-switch is emergency-only and no automated mechanism may assert it on
  congestion. This proposal implements acceptance A.1-A.3.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed and
  versioned per the no-index bridge path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites the
  governing spec and derives its tests from it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project /
  Work Item / Project Authorization metadata present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the verification
  plan maps each spec acceptance clause to a test.
- `GOV-STANDING-BACKLOG-001` — WI-4780 is the governing backlog item; this
  proposal also supersedes WI-4804 (recorded below).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — preserved: spec created,
  tests derived, report + VERIFIED verdict to follow.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — preserved: captured as
  durable artifacts (spec, PAUTH, bridge thread, tests).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — preserved: WI-4780
  transitions backlogged -> resolved on VERIFIED; WI-4804 transitions
  active -> superseded.

## Prior Deliberations

- `DELIB-20265877` — Owner directive: the kill-switch is emergency-only;
  dispatcher must not treat congestion as failure (2026-06-24). The watchdog's
  set-only auto-assertion is the mechanism this directive prohibits.
- `DELIB-20260612-REENABLE-AUTODISPATCH-WATCHDOG-OFF` — Owner decision to
  re-enable auto-dispatch with the watchdog OFF once the storm cap (WI-4472) was
  VERIFIED. The watchdog running today is an unauthorized revert of that
  decision; this proposal re-aligns to it.
- No prior deliberation rejected stripping the auto-kill-switch; this proposal
  does not revisit a previously rejected approach. The scaffold-seeded candidates
  concern dispatch routing/scheduling, not the kill-switch latch, and are not
  relied upon here.

## Owner Decisions / Input

This work is owner-authorized; the relevant durable decisions are:

- `DELIB-20265877` (owner decision) — kill-switch emergency-only.
- `DELIB-20260612` (owner decision) — watchdog OFF after the cap was VERIFIED.
- AUQ 2026-06-25 (this session): owner approved creating
  `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` as written AND confirmed the
  disable/strip direction, which supersedes WI-4804's fix-and-keep approach.

No further owner decision is required to implement. The WI-4804 supersession is
recorded as a backlog disposition (see Risk / Rollback).

## Requirement Sufficiency

Existing requirements sufficient — `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`
(governing) plus the cited bridge-governance specs fully constrain the change. No
new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

Tests live in `platform_tests/scripts/test_harness_storm_watchdog.py` and run
with:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_harness_storm_watchdog.py -q --no-header
```

Spec-acceptance to test mapping (`SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001`):

- A.1 (no auto-assertion of the kill-switch) => new test
  `test_watchdog_does_not_auto_assert_kill_switch`, asserting the script contains
  no `SetEnvironmentVariable('GTKB_NO_CROSS_HARNESS_TRIGGER'` (grep-absent), plus
  reconciliation of the two existing tests that assert its presence.
- A.2 (heartbeat + logrotate preserved) => existing
  `test_watchdog_preserves_heartbeat_and_logrotate`, updated to drop the
  kill-switch-presence assertion while keeping the heartbeat and logrotate
  assertions.
- A.3 (non-regression) => the existing `test_run_with_status.py` worker-lifetime
  timeout tests (WI-4806, already VERIFIED) and the concurrency-cap tests remain
  green; this proposal does not change those protections.

Test reconciliation (these assert the superseded buggy behavior — the script
auto-asserts the kill-switch — and are updated to the new behavior):

- `test_watchdog_has_noncodex_threshold_trip` => drop the
  `GTKB_NO_CROSS_HARNESS_TRIGGER`-presence assertion; keep the threshold-detection
  assertions (the watchdog still DETECTS the population; it just no longer asserts
  the kill-switch).
- `test_watchdog_preserves_heartbeat_and_logrotate` => drop the
  `GTKB_NO_CROSS_HARNESS_TRIGGER`-presence assertion; keep heartbeat + logrotate
  assertions.

Also run on the changed test file:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_harness_storm_watchdog.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_harness_storm_watchdog.py
```

The PowerShell script `harness_storm_watchdog.ps1` is not a Python file; it is
covered by the static-text tests above rather than by ruff.

## Risk / Rollback

Risk surface: the watchdog script's storm-intervention block plus two test
expectations. The change REMOVES an intervention (the auto-kill-switch + the
redundant process-kill), so it cannot newly disable dispatch; the worst case is
the loss of a redundant safety net, which is covered by the VERIFIED concurrency
cap (WI-4472) and the VERIFIED worker-lifetime timeout (WI-4806). Single-commit
rollback: revert the one commit (script + tests bundled).

Backlog disposition: this proposal supersedes WI-4804 ("storm-watchdog dormancy +
stale kill-switch never auto-clears"). WI-4804's set-only-latch concern is
resolved by removing the auto-assertion entirely; its watchdog-liveness /
auto-clear sub-concern is moot because the watchdog no longer asserts the
kill-switch. On VERIFIED, WI-4804 is retired as superseded-by-WI-4780.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge
file for `gtkb-wi4780-strip-storm-watchdog-kill-switch`; append-only. Dispatcher/
TAFE state plus the numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs a set-only-latch defect (the watchdog silently disabling
dispatch); no new capability surface is added.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
