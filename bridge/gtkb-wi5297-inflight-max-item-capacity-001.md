NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-15T05-27-23Z
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Desktop interactive Prime Builder; resumed fleet goal
author_metadata_source: owner-resumed-interactive-session

bridge_kind: prime_proposal
Document: gtkb-wi5297-inflight-max-item-capacity
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5297-MAX-ITEM-INFLIGHT-CAP-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5297
Test: TEST-11443
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

# Implementation Proposal - Enforce per-harness max-item capacity across live dispatch cycles

## Claim

Repair the dispatcher so a harness configured with `dispatch_max_items = 1`
cannot accumulate two simultaneous live or launching work items across separate
daemon cycles. Active launch-ledger documents consume the harness capacity
until their exit is processed; terminal failures release capacity for one
subsequent launch. A full harness is skipped without killing its workers,
rewriting leases, or preventing another eligible harness from receiving work.

This is a source-and-test proposal only. It does not change live dispatcher
configuration, routing, eligibility, roles, leases, runtime JSON, worker
allowances, credentials, deployments, or releases.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
and `SPEC-DISPATCHER-CONTROL-SURFACE-001` govern dispatch capacity and truthful
control-plane state; WI-5297 and linked TEST-11443 preserve the observed
regression and define a deterministic integration outcome. The owner decision
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded
repair of defects discovered during genuine A/B/C/D/F/H fleet proof.

## In-Root Placement Evidence

Both target paths are under `E:/GT-KB`. The proposal has no dependency on an
external project, harness-local scratchpad, direct provider session, runtime
JSON edit, lease edit, or out-of-root artifact.

## Observed Defect Evidence

The recurrence is dispatcher-produced and substantive:

- Harness C was configured with `dispatch_max_items = 1` but received
  `2026-07-15T20-07-19Z-loyal-opposition-C-5c5018` followed by
  `2026-07-15T20-09-13Z-loyal-opposition-C-6a66b7` before the first item had
  been reconciled.
- Harness H was configured with `dispatch_max_items = 1` but received
  `2026-07-15T20-40-32Z-loyal-opposition-H-21cba8` followed by
  `2026-07-15T20-41-42Z-loyal-opposition-H-c3b8b4`.
- The clearest live recurrence is harness D: both
  `2026-07-15T21-04-18Z-loyal-opposition-D-33f5a7` and
  `2026-07-15T21-04-53Z-loyal-opposition-D-cecdcd` were simultaneously alive
  under `dispatch_max_items = 1`, on different bridge documents, with healthy
  `pythonw` PIDs 30828 and 23652. The launch ledger reported two active entries.

No worker was terminated and no dispatcher state was changed while collecting
this evidence.

## Proposed Scope

1. Compute active in-flight item usage for the exact target harness from its
   launch ledger after ordinary exit-code processing and terminal bridge
   reconciliation have run.
2. Count unresolved selected documents, not merely worker processes. Use the
   launch's per-document outcomes when present and a bounded compatibility
   fallback for older launch records.
3. Derive available capacity as
   `max(0, effective_target_max_items - active_inflight_item_count)` and select
   no more than that many new documents for the target.
4. When capacity is exhausted, record a stable non-failure
   `dispatch_capacity_held` result with configured, active, and available item
   counts. Do not acquire a new document lease or spawn a worker.
5. Continue ranked target evaluation so a full H, D, or other target does not
   dead-end the whole Loyal Opposition queue when another eligible target has
   capacity.
6. Preserve launch failure, provider backoff, stale-run, circuit-breaker,
   oldest-first, signature, document-lease, and work-intent behavior. A
   processed terminal exit releases capacity on the next normal cycle.
7. Add focused regressions for max-one overlap, processed-failure release,
   partial max-two capacity, legacy-ledger compatibility, and ranked failover.

## Out Of Scope

- Killing, interrupting, draining, recovering, or reoffering either currently
  live D worker.
- Direct edits to dispatcher runtime JSON, launch ledgers, leases, daemon
  locks, eligibility, caps, rules, weights, roles, models, or allowances.
- Changing the 600-turn, 900-second operation, 3,600-second session,
  4,200-second worker, or 4,500-second lease policy.
- Provider/harness contact, credential lifecycle, unrelated cleanup, Git
  history rewrite, push, deployment, or release.
- Adopting foreign WI-5217, WI-5236, WI-5255, WI-5222, or other current dirty
  hunks in the two shared target files.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - centralized selection and launch capacity must be deterministic across daemon cycles.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - configured caps and reported effective capacity must agree.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - active harnesses must receive genuine governed work without duplicate over-cap dispatch.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - source work requires proposal, independent verdict, report, and independent verification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - launch and document attribution remain bound to the selected harness/session.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing requirements are linked before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the report must execute the mapped tests before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, PAUTH, WI, test, and target paths are declared.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - implementation must remain inside the active PAUTH operation envelope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no protected edit precedes GO, claim, and implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live recurrence is preserved as a work item, test, and bridge lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - evidence, defect, implementation, test, verdict, and commit remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a post-VERIFIED recurrence triggers a new regression carrier.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the repair stays inside the GT-KB platform root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - behavior is verified through deterministic source/tests and live dispatcher evidence.
- `GOV-STANDING-BACKLOG-001` - the new regression remains visible until terminal verification.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded repair of fleet-proof defects.
- `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-004.md` - prior VERIFIED repair for per-batch max-item selection; this recurrence demonstrates the remaining cross-cycle in-flight gap.
- `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-004.md` - launch-ledger predecessor that provides the authoritative per-recipient launch history.
- `WI-5297` and `TEST-11443` - durable recurrence and integration-test carriers.

## Owner Decisions / Input

- The owner directed that all funded, functional harnesses remain dispatchable
  unless a specific reason exists; duplicate suppression must therefore
  preserve useful routing rather than disable the bridge or harnesses.
- The owner prohibited disabling the bridge to suppress console windows and
  directed that work continue while manual PB/LO processing is active.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and the active
  WI-5297 PAUTH authorize only the bounded source/test lifecycle described here.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Max-one cross-cycle capacity | Focused runtime integration test with one unresolved prior launch and a distinct actionable document | no second spawn or lease; `dispatch_capacity_held`; active=1, available=0 |
| Terminal release | Add a processed failure/exit to the prior launch and rerun | exactly one subsequent launch is permitted |
| Partial max-two capacity | Seed one unresolved document under cap two | exactly one additional document is selected |
| Legacy compatibility | Seed a pre-outcomes launch-ledger record with selected documents | unresolved documents consume bounded capacity without crashing |
| Ranked failover | First LO target full, second target available | first records capacity hold and second receives the item |
| No worker/lease mutation | Assert process termination and lease-release helpers are not called by the capacity branch | existing live work is untouched |
| Existing dispatcher contracts | Run full `platform_tests/scripts/test_dispatcher_runtime.py` plus Ruff checks | all tests pass; no oldest-first, signature, lease, backoff, or allowance regression |

## Acceptance Criteria

1. A target with `dispatch_max_items = 1` and one unresolved in-flight document
   receives no second item on a later daemon cycle.
2. Capacity is item-based and bounded for both current and legacy launch-ledger
   records.
3. A processed terminal exit releases capacity exactly once through normal
   reconciliation.
4. A full target does not block another ranked eligible target with capacity.
5. The capacity branch acquires no new lease, spawns no worker, kills no
   process, and mutates no existing launch record.
6. Dispatcher status/report evidence exposes configured, active, and available
   item counts with a stable non-failure reason.
7. Exact focused and full runtime tests plus Ruff check/format pass.
8. The final candidate contains only WI-5297 hunks from the two approved paths,
   the bridge chain, and exact governed proof artifacts.
9. An independent dispatcher-produced LO session returns VERIFIED before one
   focused local commit is created.

## Risks And Rollback

The main risk is under-dispatch if an old launch record remains unresolved.
The design therefore counts only launch-ledger entries whose exits have not
been processed after the existing reconciliation pass, preserves bounded
legacy fallbacks, and exposes counts for diagnosis. The safer failure mode is
temporary capacity hold, not duplicate live work. Rollback is a focused revert
of the eventual source/test commit; append-only WI, test, bridge, and verdict
evidence remains historical.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`fix`

## Pre-Filing Preflight

The proposal body was checked before filing with the canonical pending-content
preflights. The helper-mediated filing path must repeat its compliance audit
against the filed body.

- Applicability packet: `sha256:9aa78e53be8e9d313cec71a1fac54b3e5a2883ef88e8c3b8f95f070be516633e`
- `preflight_passed`: `true`
- `missing_required_specs`: `[]`
- `missing_advisory_specs`: `[]`
- `blocking_errors`: `[]`
- Clauses evaluated: 5
- `must_apply`: 4; `may_apply`: 1; `not_applicable`: 0
- Evidence gaps in must-apply clauses: 0
- Blocking gaps: 0
- Mandatory clause-preflight exit: 0

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
