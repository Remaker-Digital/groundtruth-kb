NEW

# WI-4702 - Dispatcher Reset Recipient State Directory Alignment

bridge_kind: prime_proposal
Document: gtkb-wi4702-dispatch-reset-recipient-state-dir
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-05T23:52:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4702-BATCH-B-20260705
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4702

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/dispatcher_runtime.py", "platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4702 exists because the operator-facing dispatcher reset path can report a
successful recipient reset while touching an obsolete or non-live state
directory. The stale finding was originally described against the retired
`cross_harness_bridge_trigger.py` path, so this proposal deliberately
re-derives the repair against the current dispatcher daemon/runtime surfaces:
`groundtruth_kb.bridge_dispatch_reset`, the `gt bridge dispatch reset` CLI, and
`scripts/dispatcher_runtime.py`.

The implementation will make reset-recipient state-dir-correct by construction.
The operator path must target the canonical bridge-poller/dispatcher state used
by `gt bridge dispatch status` and health reporting, refuse or clearly fail
ambiguous reset attempts, and add focused regression coverage proving that a
false-green reset cannot leave the live breaker or recipient residue untouched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - implementation requires a live bridge `GO`,
  a matching work-intent claim, an implementation-start packet, and a
  post-implementation report before Loyal Opposition verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH bounds the
  owner-approved mutation classes, work item, forbidden operations, and
  implementation scope for this project item.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH allows Prime
  Builder to proceed through the bridge autonomously; it does not bypass Loyal
  Opposition review or implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  links the governing specifications and maps each one to verification
  evidence before review.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the machine-readable
  `Project Authorization`, `Project`, and `Work Item` lines above bind this
  proposal to the active project authorization.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  must carry forward these specifications and execute tests derived from them.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the proposal preserves the defect,
  owner authorization, implementation scope, verification plan, and eventual
  backlog disposition as durable artifacts rather than transient chat context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair is framed as a linked
  artifact graph: WI, PAUTH, bridge proposal, source/test changes,
  implementation report, and verification verdict.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the work item remains active until
  implementation and verification evidence establish a terminal lifecycle
  transition.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher reset behavior belongs on
  the governed dispatcher control surface and must be state-dir-correct for
  operators.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - recipient reset semantics must
  remain consistent with the single-harness dispatcher runtime state model and
  must not revive retired poller assumptions.
- `ADR-DISPATCHER-ARCHITECTURE-001` - implementation must preserve the migrated
  dispatcher daemon/runtime architecture and avoid restoring retired trigger
  substrates.
- `GOV-STANDING-BACKLOG-001` - WI-4702 remains an open MemBase work item until
  the bridge implementation is verified and backlog closure evidence exists.

## Prior Deliberations

- `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE` - owner-approved Batch B
  continuation created the active WI-4702 project authorization used here.
- `INTAKE-f8bc08a3` - dispatcher/bridge CLI operations should be routed through
  a primary governed CLI surface; this proposal keeps the reset repair on the
  `gt bridge dispatch` control path.
- `INTAKE-e380887b` - direct harness-to-harness invocation is prohibited; this
  proposal confines reset behavior to dispatcher state and operator commands,
  not peer harness calls.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-001.md`
  - historical overlap work made `--state-dir .gtkb-state/bridge-poller`
  explicit; WI-4702 closes the remaining false-green reset trap by aligning the
  current reset path with live dispatcher state.

## Owner Decisions / Input

Owner approval evidence: `DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE`
authorized Batch B continuation and the PAUTH
`PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI4702-BATCH-B-20260705`.
Approval packet:
`.groundtruth/formal-artifact-approvals/2026-07-05-DELIB-20260705-HIGH-PRIORITY-QUEUE-CONTINUE.json`.

No new owner decision is required for this proposal because the implementation
scope stays within the active PAUTH, avoids credential lifecycle and deployment
operations, and proceeds through the normal bridge `GO` and
implementation-start gates.

## Requirement Sufficiency

Existing requirements sufficient - the governing requirements and constraints
are the linked dispatcher control-surface, project-authorization, bridge
authority, project-linkage, spec-derived testing, single-harness dispatcher,
dispatcher architecture, and standing-backlog records above. No new or revised
formal requirement is needed before implementing this bounded repair.

## Spec-Derived Verification Plan

Specification-to-evidence mapping:

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
  `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run
  `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4702-dispatch-reset-recipient-state-dir`
  after `GO`; expected result is an implementation-start packet scoped only to
  the declared `target_paths`.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`: add or update CLI regression coverage
  in `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`; expected
  result proves `gt bridge dispatch reset` uses the canonical dispatcher state
  directory and cannot report success when only stale/obsolete state was
  cleared.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` and
  `ADR-DISPATCHER-ARCHITECTURE-001`: add or update dispatcher-runtime/reset
  tests in `platform_tests/scripts/test_dispatcher_runtime.py` and
  `platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py`;
  expected result proves recipient reset semantics operate on the live migrated
  dispatcher state and do not restore retired trigger behavior.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the implementation report
  must carry this mapping forward and report the exact commands and observed
  results.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: the implementation report and backlog
  disposition must cite the WI, PAUTH, bridge chain, tests, and lifecycle state
  evidence rather than treating the fix as untracked cleanup.
- `GOV-STANDING-BACKLOG-001`: after Loyal Opposition `VERIFIED`, reconcile the
  WI-4702 backlog row only through the governed backlog/project surface with
  verification evidence.

Expected focused verification commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/dispatcher_runtime.py platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/dispatcher_runtime.py platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_dispatcher_runtime.py
```

The implementation report may narrow the pytest command to the exact affected
tests only if it explains why the reduced set still covers the linked
specifications.

## Risk / Rollback

Primary risk is touching dispatcher reset semantics while other dispatcher work
is active. Mitigation: keep changes limited to the reset-recipient path, state
directory resolution, and focused tests; do not restart the dispatcher daemon,
change harness eligibility, modify credentials, or restore retired poller
substrates. Rollback is a single scoped revert of the eventual verified commit,
which should restore the previous reset behavior and tests.

## Pre-Filing Preflight

Pre-filing self-checks were run against this completed draft before filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4702-dispatch-reset-recipient-state-dir-001.md --json
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4702-dispatch-reset-recipient-state-dir-001.md
```

Observed applicability result:

- `preflight_passed`: true
- `missing_required_specs`: []
- `missing_advisory_specs`: []
- `packet_hash`: `sha256:1315aa8b465a1ff95ae8e11b7d475839f1f3282f438f520dfe8d6967c9e2650d`

Observed clause result:

- `must_apply`: 3
- `Evidence gaps in must_apply clauses`: 0
- `Blocking gaps (gate-failing)`: 0
- Exit code: 0

Phantom-spec sweep: every cited `SPEC` / `GOV` / `ADR` / `DCL` / `PB` id
resolved through `gt spec show <id> --json`.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4702-dispatch-reset-recipient-state-dir`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` - the proposed implementation repairs a live operator false-green
dispatcher reset defect and adds regression coverage without adding a new
user-facing capability beyond the corrected reset behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
