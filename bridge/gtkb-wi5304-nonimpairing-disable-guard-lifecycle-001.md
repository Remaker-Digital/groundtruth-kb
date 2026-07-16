NEW

# WI-5304 - Non-impairing dispatcher disable-guard lifecycle repair

bridge_kind: prime_proposal
Document: gtkb-wi5304-nonimpairing-disable-guard-lifecycle
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning configuration

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5304-NONIMPAIRING-GUARD-CLEAR-20260715
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5304

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_disable_guard.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/groundtruth_kb/test_dispatcher_disable_guard.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the dispatcher disable-guard lifecycle without changing harness
eligibility, routing, worker state, or scheduled-task availability. Current CLI
health reports the daemon, supervisor, and watchdog enabled and healthy, with
Codex A, Claude B, and Antigravity C all active and dispatchable. The same
health report also exposes stale guard records as active: one TTL-bounded record
is simultaneously `active=true` and `expired=true`, while an obsolete
window-related owner record remains active even though the watchdog task is
enabled.

Add an audited guard-supersession transition and invoke it only after the
existing governed `enable` operations succeed. Preserve every original disable
field, record who superseded it and why, make a superseded record inactive, and
make explicit TTL expiry authoritative when a record carries both TTL and owner
evidence. Failed enables leave the guard unchanged. A post-enable guard-write
failure is surfaced as a warning but must never disable, suspend, roll back, or
otherwise impair the enabled component.

## Intended Implementation

1. Add a focused `supersede_guarded_disable` API to
   `dispatcher_disable_guard.py`. It resolves only the named task records,
   preserves the original disable evidence, appends supersession audit fields,
   reports absent records as no-ops, and fails closed rather than overwriting an
   unreadable guard document.
2. Update effective status semantics so a superseded record is inactive and a
   record with `expires_at` becomes inactive when that timestamp passes. An
   owner record remains an indefinite guard only when no TTL was supplied.
3. After successful complex, supervisor, and watchdog `enable` operations, call
   the supersession API for exactly the task names that were enabled. Do not call
   it when the underlying enable fails or a complex enable reports `ok=false`.
4. Include the guard-resolution result in JSON output and a concise warning in
   text output when guard persistence fails. The already successful enable
   remains successful and no compensating disable is attempted.
5. Add direct unit coverage for status and audit preservation plus CLI coverage
   for success, enable failure, complex partial failure, and post-enable guard
   persistence failure.

## Pre-start Ownership Boundary

At proposal time `groundtruth-kb/src/groundtruth_kb/cli.py` is already staged by
foreign concurrent work. The other five targets are clean or absent. WI-5304
must record pre-start bytes, edit only its attributable hunks, and use a
hunk-isolated implementation report and eventual VERIFIED finalizer. Whole-file
staging or finalization of `cli.py` is prohibited.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test mutation starts only after independent GO, a matching claim, and implementation-start authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal maps each applicable requirement to deterministic evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5304, its project, and its bounded PAUTH are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must evaluate the mapped tests and non-impairment evidence.
- `GOV-STANDING-BACKLOG-001` - the stale guard lifecycle defect is durably tracked as WI-5304 rather than handled as an untracked runtime workaround.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - the resolution occurs through existing governed `gt bridge dispatch ... enable` commands, never by direct runtime-file editing.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - the implementation does not edit dispatcher configuration or eligibility and exposes no direct-file mutation path.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` - stale or recoverable guard diagnostics must not erase valid per-role dispatch capability.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must preserve all active harness capacity and prove before/after dispatchability.

## Prior Deliberations

- `DELIB-20260715-WINDOW-NOT-A-WITHHOLD-REASON` - establishes that console-window behavior is never a dispatch-eligibility withhold reason and requires a non-impairing containment repair.
- `DELIB-202666332` - authorizes exact independently VERIFIED finalization while forbidding broad capture and reiterates that the console-window repair cannot make a harness non-dispatchable.

## Owner Decisions / Input

The owner explicitly directed that the console-window defect must be fixed
without disabling or withholding any harness. That decision is captured in
`DELIB-20260715-WINDOW-NOT-A-WITHHOLD-REASON` and is the authority for
`PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5304-NONIMPAIRING-GUARD-CLEAR-20260715`.
No dispatcher mutation, routing change, eligibility change, or direct runtime
guard edit is requested by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-DISPATCHER-CONTROL-SURFACE-001` and
`DCL-DISPATCHER-CONFIG-CLI-ONLY-001` require governed CLI state transitions;
`SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` preserves dispatch capability; and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` forbids solving the visibility defect
by reducing harness availability. No new or revised requirement is needed.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: proposal applicability
  and clause preflights report no blocking gaps.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` and
  `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`: CLI tests prove that only successful
  complex/supervisor/watchdog enable commands supersede exact matching guards,
  while failed enables and unrelated task records remain unchanged.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001`: direct guard tests prove there is
  no `active=true`/`expired=true` state, superseded records are inactive, and
  indefinite owner records remain active until explicitly superseded.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`: capture before/after
  `gt bridge dispatch health --json` evidence showing A, B, and C remain active
  and `can_receive_dispatch=true`; supervisor/watchdog stay enabled and healthy;
  no eligibility, weights, caps, rules, role, or routing state changes.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: an independent Loyal
  Opposition reviewer reruns the focused suite and evaluates the live
  non-impairment evidence before VERIFIED.

Expected focused commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_disable_guard.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/dispatcher_disable_guard.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/groundtruth_kb/test_dispatcher_disable_guard.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/dispatcher_disable_guard.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/groundtruth_kb/test_dispatcher_disable_guard.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health --json
```

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260715-WINDOW-NOT-A-WITHHOLD-REASON",
  "canonical_authority": "SPEC-DISPATCHER-CONTROL-SURFACE-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "gt bridge dispatch complex enable, gt bridge dispatch daemon supervisor enable, and gt bridge dispatch daemon watchdog enable",
  "before_behavior": "Successful enable operations leave old disable records active or contradictory even while every component and harness remains available.",
  "after_behavior": "A successful governed enable supersedes only the matching disable record, preserves its audit evidence, and never changes harness dispatchability or routing.",
  "self_descriptive_naming": "supersede_guarded_disable and superseded_at fields identify the exact lifecycle transition.",
  "obsolete_guidance_disposition": "The obsolete window-based disable rationale remains historical evidence but is inactive after an explicit successful enable.",
  "history_preservation": "Original reason, actor, owner evidence, creation time, expiry, and TTL remain in the record alongside supersession metadata.",
  "baseline": {
    "dispatchable_harnesses": ["A", "B", "C"],
    "components_enabled": ["dispatcher-daemon", "dispatcher-supervisor", "storm-watchdog"],
    "stale_guard_symptoms": ["active=true and expired=true", "enabled watchdog with obsolete active window guard"]
  },
  "expected_result": {
    "dispatchable_harnesses": ["A", "B", "C"],
    "components_enabled": ["dispatcher-daemon", "dispatcher-supervisor", "storm-watchdog"],
    "guard_state": "matching successfully enabled task records are superseded and inactive"
  },
  "rollback": {
    "instructions": "Revert only the eventual WI-5304 implementation commit; do not invoke disable, change eligibility, or edit live guard state.",
    "test": "Focused guard and CLI suites plus gt bridge dispatch health --json"
  },
  "hard_invariants": [
    "A, B, and C remain active and can_receive_dispatch=true",
    "No eligibility, weight, cap, rule, role, or routing mutation",
    "Failed enable operations do not supersede guard records",
    "Guard persistence failure never triggers a compensating disable",
    "Foreign staged cli.py bytes are not captured"
  ],
  "fail_closed_conditions": [
    "missing independent GO or implementation-start authority",
    "unreadable guard document",
    "target path ownership collision",
    "missing before/after dispatch health evidence"
  ],
  "essential_context_preservation": "The CLI output retains guard-resolution status and the durable record retains original and supersession evidence."
}
```

## Risk / Rollback

Primary risks are clearing a legitimate active guard before an enable succeeds,
losing historical disable evidence, corrupting the shared guard document, or
mistaking a guard persistence failure for a reason to undo availability. The
ordering, exact-task filtering, audit-preserving supersession fields,
unreadable-document refusal, and negative tests address those risks. Rollback is
an exact revert of the eventual WI-5304 commit after independent verification;
the rollback must not touch live eligibility or invoke any disable operation.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5304-nonimpairing-disable-guard-lifecycle`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - correct stale disable-guard lifecycle and status semantics without
changing dispatcher policy or harness availability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
