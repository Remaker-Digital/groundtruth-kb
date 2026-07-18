REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-17T10-20-39Z
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined PB role; interactive WI-5297 bridge revision after WI-5255 VERIFIED

# Revised Implementation Proposal - Enforce per-harness max-item capacity across live dispatch cycles

bridge_kind: prime_proposal
Document: gtkb-wi5297-inflight-max-item-capacity
Version: 005
Responds to: bridge/gtkb-wi5297-inflight-max-item-capacity-004.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5297-MAX-ITEM-INFLIGHT-CAP-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5297
Test: TEST-11443
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

## Revision Claim

Re-file the WI-5297 proposal after the only blocking NO-GO finding in
version 004 cleared. Version 004 rejected the active GO because
`platform_tests/scripts/test_dispatcher_runtime.py` was owned by the
non-terminal WI-5255 implementation report. The predecessor bridge thread
`gtkb-wi5255-bc-telemetry-worker-provenance` is now latest `VERIFIED` at
`bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md`, and the two
WI-5297 target paths are clean in the current worktree.

The implementation scope is unchanged from version 001: repair the dispatcher
so a harness configured with `dispatch_max_items = 1` cannot receive two
simultaneous unresolved items across daemon cycles. Active launch-ledger
documents consume capacity until their terminal exit is processed; capacity
exhaustion records a stable non-failure result and ranked target evaluation
continues to another eligible target.

This revision authorizes no implementation by itself. Source or test mutation
still requires independent LO `GO`, a matching `go_implementation` claim,
implementation-start authorization, spec-derived tests, a post-implementation
report, and independent `VERIFIED`.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, the linked WI-5297 defect record, and
`TEST-11443` define the required behavior and regression visibility for this
bounded dispatcher-capacity repair. No new or revised requirement is required
before implementation.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch selection and launch capacity must be deterministic across daemon cycles.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - configured caps and reported effective capacity must agree.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - active harnesses must receive genuine governed work without duplicate over-cap dispatch.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - source work requires proposal, independent verdict, report, and independent verification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - launch and document attribution remain bound to selected harness/session evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete governing requirements are linked before mutation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports must execute the mapped tests before `VERIFIED`.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, PAUTH, WI, test, and target paths are declared.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - implementation must remain inside the active PAUTH operation envelope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no protected edit precedes GO, claim, and implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live recurrence remains preserved as a work item, test, and bridge lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - evidence, defect, implementation, test, verdict, and commit remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a post-VERIFIED recurrence triggers a new regression carrier.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the repair stays inside the GT-KB platform root.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - behavior is verified through deterministic source/tests and live dispatcher evidence.
- `GOV-STANDING-BACKLOG-001` - the regression remains visible until terminal verification.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded repair of fleet-proof defects.
- `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-004.md` - prior VERIFIED per-batch max-item selection repair; WI-5297 covers the remaining cross-cycle in-flight gap.
- `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-004.md` - launch-ledger predecessor that provides authoritative per-recipient launch history.
- `bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md` - predecessor ownership conflict now terminal `VERIFIED`.
- `bridge/gtkb-wi5297-inflight-max-item-capacity-004.md` - latest NO-GO whose sole blocking finding was the WI-5255 target-ownership conflict.

## Owner Decisions / Input

No new owner decision is required for this revision. The existing owner
authority from `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` and
the active WI-5297 PAUTH remain the governing approval basis. The owner also
directed that funded, functional harnesses remain dispatchable unless a
specific reason exists; this proposal preserves routing instead of disabling a
harness or the bridge.

## Findings Addressed

### F1 (P0, blocking) - Peer Implementation Report Conflict (`platform_tests/scripts/test_dispatcher_runtime.py`)

Response: cleared. The conflicting predecessor thread
`gtkb-wi5255-bc-telemetry-worker-provenance` is latest `VERIFIED` at
`bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md`. A scoped worktree
check shows no current dirty changes in `scripts/dispatcher_runtime.py` or
`platform_tests/scripts/test_dispatcher_runtime.py`.

## Scope Changes

No source, test, configuration, runtime-state, credential, release, deployment,
or target-path scope changes are introduced by this revision. The target list
remains exactly:

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

The proposal remains out of scope for killing workers, draining the dispatcher,
rewriting leases or launch ledgers, changing configured caps, changing
harness eligibility, changing provider credentials, Git history rewrite, push,
deployment, or release.

## Proposed Implementation

1. Compute active in-flight item usage for the selected harness from its launch
   ledger after ordinary exit-code processing and terminal bridge
   reconciliation.
2. Count unresolved selected documents, not only worker processes. Use
   per-document outcomes when present and a bounded compatibility fallback for
   older launch records.
3. Derive available capacity as
   `max(0, effective_target_max_items - active_inflight_item_count)`.
4. Select no more than the available item count for that target.
5. When capacity is exhausted, record stable non-failure
   `dispatch_capacity_held` evidence with configured, active, and available
   item counts. Do not acquire a new document lease or spawn a worker.
6. Continue ranked target evaluation so a full eligible target does not
   dead-end the LO queue when another eligible target has capacity.
7. Preserve launch failure, provider backoff, stale-run, circuit-breaker,
   oldest-first, signature, document-lease, and work-intent behavior. A
   processed terminal exit releases capacity on the next normal cycle.

## Verification Plan

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
9. Independent LO returns `VERIFIED` before finalization.

## Pre-Filing Preflight Subsection

The helper-mediated filing path must run the canonical applicability and
clause preflights against this completed revision body before writing the live
bridge file.

## Risk And Rollback

The main risk is under-dispatch if an old launch record remains unresolved.
The design therefore counts only launch-ledger entries whose exits have not
been processed after the existing reconciliation pass, preserves bounded
legacy fallbacks, and exposes counts for diagnosis. The safer failure mode is
temporary capacity hold, not duplicate live work. Rollback is a focused revert
of the eventual source/test commit; append-only WI, test, bridge, and verdict
evidence remains historical.
