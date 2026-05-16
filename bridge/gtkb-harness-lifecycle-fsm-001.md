# Implementation Proposal — Harness Lifecycle Finite State Machine (WI-3339)

bridge_kind: prime_implementation_proposal
Version: 001 (NEW)

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py", "groundtruth-kb/tests/test_harness_lifecycle.py"]

Project Authorization: PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-HARNESS-REGISTRY-REFACTOR
Work Item: WI-3339

## Summary

Add the harness lifecycle finite state machine as a new pure-logic module
`groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py`. The module defines the
four lifecycle states, the deterministic transition graph, and validation
functions that decide whether a given `status` transition is permitted.

This is work item WI-3339 (A3) of the `PROJECT-HARNESS-REGISTRY-REFACTOR`
sub-project. It implements `REQ-HARNESS-REGISTRY-001` FR2: each harness has a
lifecycle `status` governed by a four-state finite state machine —
`registered → active ⇄ suspended → retired` — with deterministic, validated
transitions; `retired` is terminal; records are never deleted.

The change is strictly additive — one new module and one new test file. It does
NOT modify the `harnesses` table, the `insert_harness` accessor, the projection
generator, or any existing module, hook, or reader.

## Scope

In scope:

1. A new module `groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py` that
   defines: the four status constants and the `HARNESS_STATUSES` set; the
   transition graph; `is_valid_transition(from_status, to_status)`;
   `validate_transition(from_status, to_status)` (raises a clear `ValueError`
   on a disallowed or unknown-state transition); `next_states(status)` (the set
   of permitted successor states); and `is_terminal(status)`.
2. Unit tests in `groundtruth-kb/tests/test_harness_lifecycle.py`.

Out of scope:

- Wiring the FSM into a status-changing DB accessor or the `gt harness` CLI
  verbs (`activate` / `suspend` / `resume` / `retire`) — that is WI-3340, which
  consumes this module. No DB accessor is modified here.
- Modifying `insert_harness` — the WI-3337 registration primitive is unchanged;
  it remains the raw append used to register a harness at `registered`.
- The hot-path projection (WI-3338, VERIFIED), role portability (WI-3341),
  reader migration (WI-3342), the ADR new version (WI-3343), and data-driven
  dispatch (WI-3344).

## In-Root Placement Evidence

Both target paths are within `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\harness_lifecycle.py` — FSM module.
- `E:\GT-KB\groundtruth-kb\tests\test_harness_lifecycle.py` — FSM tests.

No `applications/` paths; no paths outside the GT-KB platform root. Compliant
with the in-root placement constraint of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` — governing requirement. FR2 specifies the
  four-state lifecycle FSM (`registered → active ⇄ suspended → retired`),
  deterministic validated transitions, the terminal `retired` state, and that
  records are never deleted. This proposal implements the FSM and its
  transition-validation functions. FR1's `status` column (delivered by WI-3337)
  is the field this FSM governs.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness-registry architecture
  this requirement extends; the lifecycle FSM governs the `status` field of the
  `harnesses` records that ADR's role-set model also describes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  derives tests from FR2's transition graph.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the file bridge is the canonical workflow
  state; this proposal is filed as a NEW bridge entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both target paths are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; the FSM is a governed
  deterministic-logic artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; the module follows the
  established pure-logic-module pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; the proposal lifecycle is
  NEW then GO/NO-GO then VERIFIED per the file-bridge protocol.

## Prior Deliberations

- `DELIB-2079` — the consolidated owner decision for the Antigravity
  Integration design. Q3 (per-harness lifecycle FSM) directly authorizes this
  work item: the owner decided `registered → active ⇄ suspended → retired`
  (four states, a single enum), rejecting a three-state model and two
  orthogonal axes.
- `DELIB-2080` — the role-portability amendment; relevant context because role
  portability (FR9) operates on harnesses whose `status` this FSM governs, but
  this work item does not implement FR9.
- The WI-3337 thread `gtkb-harness-registry-table-schema` (VERIFIED) established
  the `harnesses` table with the `status` column defaulting to `registered`.
  The WI-3338 thread `gtkb-harness-registry-hot-path-projection` (VERIFIED)
  added the projection. No prior deliberation proposed or rejected a harness
  lifecycle FSM module; the pre-proposal deliberation search (`harness lifecycle
  FSM`, `harness status state machine`) returned only the DELIB-2079 design
  record and the two VERIFIED sibling threads, none in conflict.

## Owner Decisions / Input

This proposal implements owner-decided work and depends on owner approval
recorded as:

- `DELIB-2079` (`outcome=owner_decision`) — owner approved the Antigravity
  Integration design via an 11-answer AskUserQuestion grill on 2026-05-16,
  including Q3 (the four-state lifecycle FSM).
- `DELIB-2080` — owner-confirmed role-portability amendment.
- `PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`
  — active project authorization covering WI-3337 through WI-3344.

The project authorization is owner-approval evidence for the bounded project
work; it does not replace this proposal's Loyal Opposition review or the GO
gate.

## Requirement Sufficiency

Existing requirements sufficient. `REQ-HARNESS-REGISTRY-001` FR2 fully specifies
the four states and the transition graph.

Interpretation note for the reviewer: FR2's notation
`registered → active ⇄ suspended → retired` is implemented as the literal
four-edge transition graph — `registered → active`, `active → suspended`,
`suspended → active`, and `suspended → retired`. Under this literal reading,
`retired` is terminal (no outgoing edges) and there is no direct
`active → retired` edge: retiring an `active` harness is the two-step
`active → suspended → retired`. This is a complete, deterministic FSM and is
sufficient to implement. If the owner intends a direct `active → retired`
transition, that is a one-edge addition to the transition graph and a small
follow-up requirement clarification; it does not block this work item. The
implementation and tests below reflect the literal four-edge reading.

## Implementation Plan

1. Add `groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py`:
   - Status constants `STATUS_REGISTERED`, `STATUS_ACTIVE`, `STATUS_SUSPENDED`,
     `STATUS_RETIRED`, and `HARNESS_STATUSES` (the frozenset of all four).
   - `_TRANSITIONS` — a mapping from each status to the frozenset of permitted
     successor states: `registered → {active}`, `active → {suspended}`,
     `suspended → {active, retired}`, `retired → {}`.
   - `next_states(status)` — returns the permitted successor frozenset; raises
     `ValueError` for an unknown status.
   - `is_terminal(status)` — `True` only for `retired`.
   - `is_valid_transition(from_status, to_status)` — `True` iff `to_status` is
     in `next_states(from_status)`; `False` for unknown states and same-state
     pairs (a same-state pair is not a transition edge).
   - `validate_transition(from_status, to_status)` — returns `None` on a valid
     transition; raises `ValueError` with an informative message naming the
     offending states and the permitted successors on an invalid or
     unknown-state transition.
2. Add `groundtruth-kb/tests/test_harness_lifecycle.py` (see Spec-to-Test
   Mapping).

The module is pure logic — it imports only the Python standard library, opens
no DB connection, and modifies no existing file.

## Spec-to-Test Mapping

`REQ-HARNESS-REGISTRY-001` FR2 (four-state FSM, deterministic validated
transitions, terminal `retired`) is verified by tests added to
`groundtruth-kb/tests/test_harness_lifecycle.py`:

- `test_four_states_defined` — `HARNESS_STATUSES` is exactly the four FR2
  states.
- `test_valid_transitions_accepted` — each of the four FR2 edges
  (`registered→active`, `active→suspended`, `suspended→active`,
  `suspended→retired`) is accepted by `is_valid_transition` and
  `validate_transition`.
- `test_invalid_transitions_rejected` — representative non-edges
  (`registered→retired`, `registered→suspended`, `active→retired`,
  `active→active`, `suspended→suspended`) are rejected.
- `test_retired_is_terminal` — `is_terminal(retired)` is `True`, the other
  three are `False`, and `next_states(retired)` is empty.
- `test_validate_transition_raises_on_invalid` — `validate_transition` raises
  `ValueError` on a disallowed transition and the message names the offending
  states.
- `test_unknown_status_rejected` — an unknown status raises `ValueError` from
  `validate_transition` / `next_states` and yields `False` from
  `is_valid_transition`.
- `test_next_states_per_state` — `next_states` returns the exact permitted set
  for each of the four states.

## Risks

- **Interpretation of the FR2 notation.** As stated in Requirement Sufficiency,
  the literal four-edge reading is implemented. *Mitigation:* the interpretation
  is documented here for the reviewer; a direct `active → retired` edge, if the
  owner later wants it, is a one-line change.
- **Unused module until WI-3340.** The FSM is delivered here but consumed by the
  WI-3340 CLI verbs. *Mitigation:* the module is fully unit-tested in isolation;
  an unconsumed pure-logic module is inert and risk-free.

## Rollback

Remove the two new files. Nothing else references them, so removal is clean.

## Verification Procedure

Run, from the project root:

- `python -m pytest groundtruth-kb/tests/test_harness_lifecycle.py -q`
- `python -m pytest groundtruth-kb/tests/test_db.py -q` (regression — the
  `harnesses` table and accessors are not modified)

Expected: all new tests pass and `test_db.py` remains green (94 passed).

## Acceptance Criteria

- The module defines exactly the four FR2 states and the four-edge transition
  graph.
- `is_valid_transition` / `validate_transition` accept every FR2 edge and reject
  every non-edge, unknown state, and same-state pair.
- `retired` is terminal — `is_terminal(retired)` is `True` and
  `next_states(retired)` is empty.
- All spec-derived tests pass; the existing `test_db.py` suite is green.
- No existing table, accessor, module, hook, or reader is modified.

## Bridge Protocol Compliance

This proposal is filed as `bridge/gtkb-harness-lifecycle-fsm-001.md` with a
corresponding `bridge/INDEX.md` entry at `NEW` status, inserted at the top of
the entry list per the file-bridge protocol. No prior bridge version is deleted
or rewritten; `bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001`. The mandatory pre-filing applicability and
clause preflights are run after the INDEX entry exists; their results are
recorded in the review verdict.

## Clause Scope Clarification

This proposal is not a bulk operation. It adds exactly one module and one test
file, and implements exactly one work item (`WI-3339`); it does not inventory,
batch-mutate, promote, retire, or sweep multiple artifacts. The
`GOV-STANDING-BACKLOG-001` bulk-operations visibility clause therefore does not
substantively apply: no bulk-operation inventory artifact, review packet, or
`DECISION DEFERRED` marker is produced because there is no bulk action to gate.
Owner approval for the bounded project work is recorded via the
formal-artifact-approval-backed `DELIB-2079` and the active project
authorization
`PAUTH-PROJECT-HARNESS-REGISTRY-REFACTOR-HARNESS-REGISTRY-REFACTOR-IMPLEMENTATION-AUTHORIZATION`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
