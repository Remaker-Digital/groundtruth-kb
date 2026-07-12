NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: Codex desktop
author_model_configuration: xhigh reasoning; interactive Prime Builder; owner-authorized governed implementation

# WI-5208 Implementation Report - Concurrent dispatch launch ledger

bridge_kind: implementation_report
Document: gtkb-wi5208-concurrent-dispatch-launch-ledger
Version: 003 (NEW post-implementation report)
Responds to GO: bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-002.md
Approved proposal: bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5208-CONCURRENT-LAUNCH-LEDGER-20260711
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5208
Linked Test: TEST-11362
Implementation claim: row 31221, session 019f5474-93a6-7f70-8e54-d6d8b0a31bb4, deadline 2026-07-12T09:25:37Z
Implementation authorization packet: sha256:60e98d13eca41b463626b1c606349ff9c71cdd2e6a60b9e576207da09c8a0ba7
Recommended commit type: feat

## Implementation Claim

Each recipient now carries a durable `launch_ledger` dictionary keyed by dispatch id. Every successful runtime or daemon spawn is registered after its work-intent and document-lease metadata is attached. Exit reconciliation migrates legacy successful `last_launch` state, processes every ledger record independently, preserves each record's exact-once lease-release flag, and retains all active records plus the newest 16 completed records. Active population remains bounded by the existing hard global live-process cap (default eight); completed history has an explicit per-recipient bound.

`last_launch` is now a compatibility projection of the newest actual spawn ordered strictly by `launched_at` and dispatch id. `last_attempt` separately records the newest attempt, including `document_lease_held`, work-intent suppression, unlaunchable target, quiesce, launch failure, and dry-run outcomes. Non-launch attempts therefore remain observable without erasing active launch authority. Reconciliation accepts ledger records directly rather than swapping them through `last_launch`; exit sidecars are processed in observed completion order while launch projection remains launch-time ordered.

Role-alias migration merges duplicate dispatch ids by reconciliation progress, soft recipient reset clears and reaps the complete ledger, and all existing WI-5207 per-document completion behavior remains passing.

## Changed Paths

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

All four paths were clean at `2227ccf5` before WI-5208 implementation. No foreign hunk is authorized for the focused commit. Operational eligibility changes in `harness-state/harness-registry.json` and all other dirty-tree paths are excluded.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

The GO advisory was applied: auto-populated `SPEC-AUQ-POLICY-ENGINE-001` and `ADR-CODEX-HOOK-PARITY-FALLBACK-001` are not implementation-bearing for this ledger repair and are not asserted as verification dependencies. They remain historical proposal links only.

## Owner Decisions / Input

- `DELIB-202666173` directs correction of every defect discovered during genuine six-harness proof.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5208-CONCURRENT-LAUNCH-LEDGER-20260711` authorizes the bounded ledger repair through 2026-07-18T23:59:59Z.
- No new owner decision was required.

## Fresh Reproduction Evidence

The defect reproduced during WI-5207 verification after the GO. Original B dispatch `2026-07-12T07-40-30Z-loyal-opposition-B-52e8af` remained healthy and active for 34 minutes. At `08:08:53Z`, the daemon launched concurrent B dispatch `2026-07-12T08-08-53Z-loyal-opposition-B-089dda` for a different document because the single compatibility slot no longer represented the first active worker. The operations report showed both workers live simultaneously. Both later exited 0; the original produced WI-5207 VERIFIED commit `2227ccf5`, while the second correctly stood down on H-reserved WI-5199. This is genuine dispatcher-produced proof of the exact concurrency model WI-5208 repairs.

## Prime Builder Explorer Review

A read-only Prime Builder explorer independently mapped every write and reconciliation site and found three P1 issues in the first draft: non-launch attempts still polluted `last_launch`, projection order used completion time, and reconciliation used `last_launch` as mutable scratch state. All three were corrected before this report. It also identified stale duplicate-id alias merging, now covered by a dedicated test. The explorer made no file edits.

## Specification-Derived Verification

| Requirement | Executed evidence | Observed result |
| --- | --- | --- |
| Three concurrent launches keyed independently | Daemon executes three successful LO spawn decisions for one recipient | Three distinct dispatch ids remain in `launch_ledger`; active count is three |
| Out-of-order exit reconciliation | Runtime observes B and C exit sidecars before A, then A later | Each record processes independently; completion counts advance 0/2/3 |
| Exact-once lease release | Reconciliation is repeated before and after A's late sidecar | Exactly one release call per dispatch/document; no repeat release |
| Non-launch cannot erase active evidence | Later `document_lease_held` attempt after three spawns | `last_attempt` records lease-held; `last_launch` and all ledger records remain actual launches |
| Truthful compatibility projection | Older launch A completes after newer launch C | `last_launch` remains C, ordered by launch time rather than completion time |
| Legacy migration | Legacy successful `last_launch` without ledger is reconciled | Record is added by dispatch id, remains active without sidecar, then completes normally |
| Bounded history | 19 completed plus one active fixture | Active record preserved; only newest 16 completed retained |
| Alias merge progress | Same dispatch id appears active and completed across role aliases | Completed/reconciled record wins |
| WI-5207 compatibility | Complete runtime suite, including seven WI-5207 nodes | Runtime module passes entirely |

## Commands And Observed Results

1. Focused WI-5208 tests:
   `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short -k wi5208`
   Result: `5 passed, 241 deselected`.
2. Full approved runtime/daemon suite in the implementation worktree:
   Result: `235 passed, 11 failed`.
3. Identical suite in detached clean worktree `.gtkb-state/wi5208-baseline` at `2227ccf5`:
   Result: `230 passed, 11 failed`. The same eleven daemon nodes fail for the already-disclosed work-intent/provenance fixture drift and stale 3600/5400 lifetime expectations. WI-5208 adds five passing tests and zero failures.
4. Ruff lint across all four paths:
   Result: `All checks passed!`.
5. Ruff format check across all four paths:
   Result: `4 files already formatted`.

## GO Conditions

- [x] Per-recipient ledger is keyed by dispatch id.
- [x] Three concurrent launches reconcile independently out of order.
- [x] Every launch releases its own leases exactly once.
- [x] New launches and non-launch attempts cannot erase earlier active evidence.
- [x] `last_launch` remains a truthful newest-actual-launch projection; `last_attempt` preserves non-launch observability.
- [x] Legacy state migrates fail-safe.
- [x] Completed history is explicitly bounded; active entries are bounded by the hard live-process cap and are never dropped before reconciliation.
- [x] Alias-state merge keeps the more advanced record.
- [x] WI-5207 per-document completion and signatures remain compatible.
- [x] D/F/H 600-turn, 900-second operation, 28,800-second session, and 29,400-second worker allowances are unchanged.

## Risk And Rollback

Residual risk is limited to pathological manually-corrupted state containing more active records than the hard global process cap could have produced. Active records are intentionally never pruned because doing so would recreate the lease-loss defect; normal production active cardinality is bounded before spawn by the existing process cap. The focused commit is the rollback boundary. Bridge history and runtime telemetry remain append-only.

## Loyal Opposition Asks

1. Inspect all four path diffs and confirm no foreign hunk.
2. Independently rerun the five focused tests, full runtime/daemon suite, lint, and format checks.
3. Reproduce the clean `2227ccf5` baseline and confirm the exact `+5 passing / +0 failing` delta.
4. Stress the explorer-identified seams: last-attempt separation, launch-time projection, direct-record reconciliation, duplicate-id merge, and concurrent WI-5207 signatures.
5. If all evidence holds, write VERIFIED and create one focused commit containing only the four approved paths plus the WI-5208 bridge chain.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
