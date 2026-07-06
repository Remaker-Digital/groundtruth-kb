NEW

# WI-4725 - Stale Failure Health Current-State Disposition

bridge_kind: prime_proposal
Document: gtkb-wi4725-stale-failure-health-disposition
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-06T00:14:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4725-BATCH-B-20260705
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4725

target_paths: ["groundtruth.db", "scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: governance, dispatcher-health-state-disposition
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4725 captured a real stale-health failure mode from 2026-06-21: an older
failed Prime launch left `last_launch.exit_failure_reason` / failure metadata
behind, while later Prime dispatch was suppressed by `work_intent_already_held`.
The original candidate fix cited the now-retired
`scripts/cross_harness_bridge_trigger.py`; the current dispatcher architecture
has migrated to `scripts/dispatcher_runtime.py` plus
`scripts/gtkb_dispatcher_daemon.py`.

This proposal does not restore the retired trigger or assume the stale item is
automatically closed. It authorizes a current-state disposition after `GO`:
prove the migrated runtime/daemon/health tests cover the stale-failure +
work-intent suppression class, add or repair only a narrow guard inside the
declared dispatcher-health paths if the proof exposes a live gap, and then
resolve only the WI-4725 backlog row with explicit evidence. The strongest
current evidence is the already-VERIFIED
`bridge/gtkb-wi5002-prime-stale-failure-health-004.md`, which fixed and
verified stale Prime failure-field cleanup on benign `unchanged` and
`work_intent_already_held` paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this disposition requires a live bridge
  `GO`, an implementation-start packet, an implementation report, and Loyal
  Opposition verification before WI-4725 can be treated as terminal.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the
  owner-approved Batch B scope for WI-4725.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does
  not bypass bridge review; it only avoids another owner prompt for this scoped
  Batch B disposition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  declares target paths, requirement sufficiency, and spec-derived verification
  before any terminal backlog mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the header binds this
  proposal to the active PAUTH, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must carry forward this spec-to-evidence map and observed command output.
- `GOV-STANDING-BACKLOG-001` - the WI-4725 row may become terminal only through
  a governed backlog update with explicit completion evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - stale backlog work is resolved by an
  evidence-backed lifecycle disposition rather than silent omission.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the WI, PAUTH, bridge chain,
  verified predecessor evidence, tests, and backlog resolution must remain one
  durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale/superseded work requires an
  explicit terminal transition and trigger evidence.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` - overall dispatcher health must
  distinguish genuine dispatch impossibility from recoverable or stale
  per-recipient runtime history.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch health/state accounting
  belongs to the centralized daemon/runtime service, not the retired trigger.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - current dispatcher behavior is
  governed by the migrated dispatcher runtime and signature/suppression model.
- `ADR-DISPATCHER-ARCHITECTURE-001` - disposition must preserve the daemon-owned
  dispatcher architecture and avoid restoring harness-hook trigger behavior.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-approved Batch B
  continuation created the active WI-4725 project authorization used here.
- `bridge/gtkb-wi5002-prime-stale-failure-health-001.md` - proposed the
  current stale Prime failure-field cleanup for benign Prime dedupe /
  work-intent suppression paths.
- `bridge/gtkb-wi5002-prime-stale-failure-health-003.md` - implementation
  report showing `_clear_stale_failure_fields()` in the runtime and matching
  daemon cleanup paths.
- `bridge/gtkb-wi5002-prime-stale-failure-health-004.md` - Loyal Opposition
  VERIFIED the stale-failure cleanup and focused runtime/daemon tests.
- `bridge/gtkb-wi5003-opus-floor-c-stdin-dispatch-004.md` - related VERIFIED
  daemon test expectation correction cited by the WI-5002 verification.
- `INTAKE-b8875adc` - OPS proposals need explicit trigger/evidence fields; this
  disposition uses concrete current-state checks rather than assuming old
  cross-harness trigger behavior still exists.

## Owner Decisions / Input

Owner approval evidence: `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`
authorized Batch B continuation and the PAUTH
`PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4725-BATCH-B-20260705`.
Approval packet:
`.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json`.

No new owner decision is required. The proposal is limited to current-state
evidence, a narrow dispatcher-health repair only if the evidence exposes a
live gap in the declared paths, and a single-work-item backlog resolution after
bridge verification.

## Requirement Sufficiency

Existing requirements sufficient. The linked bridge authority,
project-authorization, backlog lifecycle, dispatcher architecture, centralized
dispatch service, single-harness dispatcher, and dispatch-health semantics
requirements are enough to verify whether WI-4725 is already covered by the
migrated dispatcher behavior or needs a narrow current-runtime repair.

No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

Specification-to-evidence mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001`,
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: after `GO`, run
  `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4725-stale-failure-health-disposition`;
  expected result is an implementation-start packet scoped to the declared
  target paths.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` and
  `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: prove stale Prime failure metadata
  is cleared or discounted on benign Prime non-launch paths and that expected
  work-intent suppression is health-neutral.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` and
  `ADR-DISPATCHER-ARCHITECTURE-001`: prove verification uses the migrated
  dispatcher runtime/daemon surfaces and does not restore
  `scripts/cross_harness_bridge_trigger.py`.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: run a dry-run backlog resolution for
  WI-4725, record exact evidence, then apply the single-row terminal update
  only after bridge `GO` and implementation evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report
  must carry forward this mapping and observed command output.

Expected verification commands:

```text
Test-Path scripts/cross_harness_bridge_trigger.py
Test-Path platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py::test_wi5002_prime_unchanged_clears_stale_failure_fields platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_wi5002_daemon_prime_fanout_unchanged_clears_stale_failure_fields platform_tests/scripts/test_dispatcher_runtime.py::test_diagnose_treats_work_intent_already_held_as_healthy_suppression platform_tests/scripts/test_dispatcher_runtime.py::test_dispatch_cycle_clears_terminal_bridge_failover_residue platform_tests/scripts/test_dispatcher_runtime.py::test_dispatch_cycle_clears_terminal_work_item_failover_residue platform_tests/scripts/test_bridge_dispatch_config.py::test_terminal_work_item_dispatch_residue_is_health_pass -q --tb=short
gt backlog resolve WI-4725 --status-detail "Resolved by bridge VERIFIED: stale failed-launch/work-intent suppression premise re-assessed after dispatcher migration; verified WI-5002 stale-failure cleanup plus current runtime/daemon/health tests cover the failure class." --related-bridge-threads "[\"bridge/gtkb-wi4725-stale-failure-health-disposition-001.md\",\"bridge/gtkb-wi5002-prime-stale-failure-health-004.md\"]" --owner-approved --change-reason "WI-4725 bridge-verified current-state disposition" --dry-run --json
```

If those checks fail because the stale-health class still manifests in the
migrated dispatcher, the implementation may make a narrow repair in the
declared dispatcher-health target paths and add/adjust focused tests before
filing the implementation report. If the required repair exceeds those paths
or weakens genuine runtime-failure reporting, Prime Builder must stop and file
a `REVISED` proposal instead of applying the terminal backlog update.

## Risk / Rollback

Primary risk is closing a stale P2 defect while a variant still exists. The
mitigation is explicit: no applied backlog resolution without live `GO`, an
implementation-start packet, current retired-file absence checks, focused
runtime/daemon/health tests, and an implementation report that maps each linked
specification to observed evidence.

Rollback is conventional and narrow: revert any source/test change made under
the eventual `GO`, or reopen/supersede WI-4725 with evidence if Loyal
Opposition later finds the failure class still exists. Bridge files remain
append-only and are not rewritten.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4725-stale-failure-health-disposition`; no prior
version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the
numbered file chain are the live workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore:` - the expected implementation is evidence-backed backlog disposition
and, only if current verification exposes a gap, a narrow dispatcher-health
guard.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
