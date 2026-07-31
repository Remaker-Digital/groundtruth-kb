NEW

# WI-5320 Dispatcher Work-Intent-Acquire Batch-Abort Fix — Implementation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5320-dispatcher-work-intent-batch-abort-fix
Version: 001
Date: 2026-07-16 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2f6a0618-d857-497d-ac8c-a509f544007e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; session-stated resolved role Prime Builder; ::init gtkb pb; ::open build. Note: the work-intent claim for this thread resolved session_id 4a5e6c94-bfde-4bfb-bfcf-49a924bdbdb9 (this harness's process-level scratchpad session id) rather than this conversation's own session_id used consistently as author_session_context_id throughout this session's other authored artifacts. This discrepancy is evidence for WI-5328 (session-provenance resolution defect) and does not affect this proposal's content or scope.

Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5320-STARVATION-FIX-20260716
Work Item: WI-5320
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py"]

## Problem Statement

`scripts/dispatcher_runtime.py` lines 2280-2355 implement the Prime Builder dispatch
batch's work-intent-acquisition loop. Two distinct failure classes are handled
inconsistently:

- `MalformedBridgeStatusError` (line 2300-2325): the handler appends the item to
  `quarantined_slugs`, records the failure, and executes `continue` — the batch
  proceeds to the next item.
- `WorkIntentRegistryError` and its subclass `WorkIntentAuthorizationError`
  (`scripts/bridge_work_intent_registry.py:39-44`, raised when the current PAUTH
  denies a work-intent operation) (line 2326-2355): on `not acquired`, the
  handler releases already-acquired slugs and executes a hard `return`,
  aborting the **entire selected batch** immediately.

The function's own docstring (line 2280-2286) states this all-or-nothing
abort-and-retry-next-cycle behavior is intentional for **transient** failures
(ordinary lease contention — "the batch fails fast so subsequent dispatch
cycles can retry"). It is the wrong behavior for a **permanent** failure such
as `WorkIntentAuthorizationError`, which will deny the identical operation on
every future attempt until the underlying project authorization is corrected.
Because the `except` clause catches the base `WorkIntentRegistryError` class,
the handler cannot distinguish "will never succeed" from "try again shortly,"
even though the exception hierarchy (`WorkIntentAuthorizationError(WorkIntentRegistryError)`)
already encodes that distinction.

### Observed impact (2026-07-16)

`PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715` denied
work-intent acquisition for `gtkb-dispatcher-black-box-spec-foundation`
(unregistered `forbidden_operations` tokens — see companion fix below). Every
PB dispatch cycle selected that document first (oldest-first priority
ordering), hit the permanent `WorkIntentAuthorizationError`, and aborted the
whole batch before any lower-priority item was attempted. Live dispatcher
state showed zero successful PB dispatches for a multi-hour window
(21:48:32Z through at least 01:48:03Z) while approximately 11 other
actionable PB items sat untried. Loyal Opposition dispatch (harness B)
completed 10+ successful headless runs in the same window with no issue,
confirming the defect is specific to this PB work-intent-acquire batch path.

Three of the four active project authorizations on this project were found to
carry unregistered `forbidden_operations` tokens (verified against the
canonical primary source, `config/governance/project-authorization-operation-taxonomy.toml`,
not a prior DELIB's summary text, which was found to be incomplete — it
omitted `git_push`, a genuinely registered operation):

| PAUTH | Unregistered tokens found |
| --- | --- |
| `PAUTH-DISPATCHER-BLACK-BOX-WI5268-FOUNDATION-GATE-V2-20260715` | `dispatcher_topology_routing_mutation`, `unrelated_runtime_mutation` |
| `PAUTH-DISPATCHER-BLACK-BOX-WI5268-SPEC-FOUNDATION-20260715` | `source`, `configuration` (mutation-class names placed in the operation field) |
| `PAUTH-DISPATCHER-BLACK-BOX-WI5268-REVISED-FOUNDATION-20260715` | `configuration`, `non_test_source`, `runtime_mutation` |
| `PAUTH-DISPATCHER-BLACK-BOX-WI5307-BASELINE-DISPOSITION-20260715` | `dispatcher_topology_routing_mutation`, `unrelated_runtime_mutation` |

All four were authored on 2026-07-15, consistent with a same-day authoring-time
gap: no write-time validation exists to reject unregistered `forbidden_operations`
tokens against the canonical taxonomy at PAUTH-authoring time; only the
work-intent-acquire read-time check catches the mismatch, and only when a
dispatch attempt is actually made against that specific PAUTH.

## Proposed Fix

### Part 1 — Structural: distinguish permanent from transient work-intent-acquire failure

In the batch-acquisition loop (`scripts/dispatcher_runtime.py`, the function
containing lines 2280-2355), split the exception handling:

- `except WorkIntentAuthorizationError as exc:` (checked before the broader
  `WorkIntentRegistryError` clause, since it is a subclass): treat as
  permanent. Append to `quarantined_slugs` with a distinct reason (e.g.
  `"impl_auth_quarantined"`-style or a new `"work_intent_authorization_denied"`
  reason, to be decided during implementation to match existing memoization
  conventions), record the failure via `_record_dispatch_failure`, and
  `continue` — matching the treatment `MalformedBridgeStatusError` already
  receives, so the batch proceeds to the next candidate.
- `except WorkIntentRegistryError as exc:` (any other subtype — ordinary
  transient lease contention): preserve the existing behavior exactly —
  release acquired slugs, record the failure with reason
  `work_intent_acquire_failed`, and hard `return` to abort the batch,
  since retrying the whole batch next cycle remains correct for genuinely
  transient contention.

This is a narrow, targeted change to one function's exception handling; it
does not alter the acquisition semantics, the PAUTH-denial logic itself, or
any other dispatcher code path.

### Part 2 — Tactical: reissue the four affected project authorizations

Reissue each of the four PAUTHs listed above as a new version (via the
governed `gt projects authorize` transaction, citing the same owner-decision
lineage each currently carries) with `forbidden_operations` corrected to use
only tokens registered in `config/governance/project-authorization-operation-taxonomy.toml`:
`dispatcher_topology_routing_mutation` → `dispatcher_mutation`;
`unrelated_runtime_mutation` → removed (no canonical equivalent identified;
the intent — preventing unrelated runtime-state mutation — is already covered
by the narrow `allowed_mutation_classes` allow-list on each PAUTH, making this
token redundant rather than load-bearing); `source`/`configuration` (where
present as forbidden **operations**, not mutation classes) → removed, since
`source`/`configuration` are already governed correctly via each PAUTH's
`allowed_mutation_classes` field, not `forbidden_operations`;
`non_test_source`/`runtime_mutation` → removed for the same reason. This
restores each PAUTH's intended deny-list without changing its actual
authorized scope (`included_work_item_ids`, `allowed_mutation_classes`
remain unchanged).

### Part 3 — Regression coverage

Extend `platform_tests/scripts/test_dispatcher_runtime_work_intent.py` with:

1. A test asserting that when the selected batch contains one item whose
   `acquire_work_intent` raises `WorkIntentAuthorizationError` and one healthy
   item, the healthy item still successfully acquires its work intent in the
   same batch (proving the fix — this currently fails on `main`, since today's
   code aborts the whole batch on the first item).
2. A test asserting that when `acquire_work_intent` raises an ordinary
   `WorkIntentRegistryError` that is **not** a `WorkIntentAuthorizationError`
   (simulated transient lease contention), the existing abort-and-retry
   behavior is preserved unchanged (batch aborts, `reason="work_intent_acquire_failed"`,
   no item is quarantined) — proving the fix does not regress the transient
   case the original design was built for.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
already establishes that PAUTH forbidden-operation enforcement happens at
work-intent-acquire time; this proposal fixes a defect in how the dispatcher's
batch-acquisition loop *responds* to that enforcement (treating a permanent
denial as if it were transient), not a gap in the enforcement mechanism
itself. No new specification or requirement capture is needed.

## Owner Decisions / Input

- Owner directed the urgent investigation of PB-dispatch throughput (this
  session, 2026-07-16) that surfaced this defect.
- Owner selected, via `AskUserQuestion` (2026-07-16): "New project-scoped
  PAUTH for WI-5320 (recommended)" — captured as
  `DELIB-20260716-WI5320-PAUTH-AUTHORIZATION`, which cites the exact scope
  now recorded in `PAUTH-DISPATCHER-BLACK-BOX-WI5320-STARVATION-FIX-20260716`.
  This authorization covers filing this proposal; it does not itself
  authorize implementation, which remains gated on independent Loyal
  Opposition `GO`.

## Prior Deliberations

- `DELIB-20260716-WI5320-PAUTH-AUTHORIZATION` — the owner authorization for
  this fix's PAUTH.
- `bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-004.md` — prior,
  independently-verified precedent for the correct canonical forbidden-operation
  vocabulary and for the pattern of correcting an unregistered-token PAUTH.
  That thread's fix is blocked on an unrelated shared-binary-carrier
  finalization issue (foreign WI-5241 append), not on the vocabulary
  correction itself, which the Loyal Opposition verdict confirmed passes
  independently.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-008.md` — the GO verdict
  whose prose ("dispatcher topology or routing mutation") was paraphrased
  into the unregistered `dispatcher_topology_routing_mutation` token,
  identifying the authoring-time root cause.
- Deliberation search performed before drafting
  (`gt deliberations search "dispatcher work intent batch abort quarantine
  permanent transient"`, `gt deliberations search "forbidden operations
  taxonomy registered vocabulary PAUTH"`) returned no other directly
  duplicating implementation record for this exact structural fix.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Verification Plan (Spec-Derived)

| Specification / surface | Test / verification evidence |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | New test: `WorkIntentAuthorizationError` on one batch item is quarantined and does not block the remaining batch items from acquiring work intent. |
| Existing transient-contention behavior (undocumented as a formal spec but load-bearing per the function's own docstring) | New test: an ordinary `WorkIntentRegistryError` (not `WorkIntentAuthorizationError`) still aborts the batch with `reason="work_intent_acquire_failed"`, preserving current behavior. |
| `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | The four reissued PAUTHs preserve their existing `included_work_item_ids`/`allowed_mutation_classes`; only `forbidden_operations` tokens change. Verified via `gt projects show-authorization <id> --json` diff against the pre-fix values recorded in this proposal. |
| Canonical forbidden-operation vocabulary | Each reissued PAUTH's `forbidden_operations` tokens verified present in `config/governance/project-authorization-operation-taxonomy.toml` `[[operation]]` names, by direct read of the reissued record. |

## Commands To Run

- `python -m pytest platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short`
- `python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
- `python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
- `gt projects show-authorization <each-of-the-four-reissued-ids> --json` (post-reissue, to confirm corrected tokens)

## Risk And Rollback

The structural fix (Part 1) is a narrow, additive exception-handling change
scoped to one function; it does not alter the acquisition success path for
any currently-succeeding case. If a regression is found post-implementation,
reverting the one function to its current form restores prior behavior
exactly (no data migration, no schema change). The PAUTH reissuance (Part 2)
is append-only per this project's versioning discipline — the prior versions
remain in the audit trail and are not destructively altered.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge-mediated implementation work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable-artifact traceability
  (WI-5320, the PAUTH, this proposal, the eventual implementation report).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-graph traceability.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the project-authorization
  model this proposal operates under.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` — governs the new
  PAUTH's restrictive `included_work_item_ids` scoping.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the
  forbidden-operation enforcement mechanism this proposal's fix responds to
  correctly without weakening.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project, Project
  Authorization, and Work Item metadata above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths remain under
  `E:/GT-KB`.
- `GOV-STANDING-BACKLOG-001` — WI-5320 is the backlog authority for this fix.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the dispatcher-owned batch-acquisition
  behavior this proposal corrects.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the NEW to GO to implementation
  report to VERIFIED lifecycle this proposal follows.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
