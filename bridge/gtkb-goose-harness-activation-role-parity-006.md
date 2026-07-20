REVISED
author_identity: goose
author_harness_id: G
author_session_context_id: goose-interactive-20260720-goose-activation-pb-v006
author_model: goose-default
author_model_version: goose-desktop-1.43.0
author_model_configuration: Goose Desktop interactive; session-stated role prime-builder via ::init gtkb pb

# Goose Harness Activation & Role Parity — Post-FSM-Amendment Revision

Document: gtkb-goose-harness-activation-role-parity
Version: 006
Responds to: bridge/gtkb-goose-harness-activation-role-parity-005.md (NO-ACTION / owner decision Option A)
Date: 2026-07-20 UTC

Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Work Item: WI-5665 (pending creation — see §Work Item)
target_paths: harness-state/harness-registry.json, groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py, groundtruth-kb/src/groundtruth_kb/harness_ops.py, groundtruth-kb/tests/test_harness_lifecycle.py

This REVISED proposal is filed as the next numbered bridge file (version 006) in the append-only chain under `bridge/`. No prior versions have been deleted or rewritten.

## Summary

Two-phase implementation per Mike's Option A decision:

**Phase 1 (IMPLEMENTED — this revision):** Amend the harness lifecycle FSM to add `retired → registered` as a permitted transition so a retired harness can exit the terminal state. This is a prerequisite for Goose activation.

**Phase 2 (deferred to GO):** After FSM amendment is VERIFIED, activate Goose G via `gt harness unretire G` → `gt harness activate G` → role/precedence assignment.

## Phase 1: FSM Amendment (Implemented)

### Changes Made

| File | Change | Status |
|------|--------|--------|
| `groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py` | `_TRANSITIONS`: add `STATUS_RETIRED: frozenset({STATUS_REGISTERED})` | ✅ Done |
| `groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py` | Module docstring: `retired` no longer terminal | ✅ Done |
| `groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py` | Transition graph diagram: add `retired → registered` edge | ✅ Done |
| `groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py` | `next_states()` docstring: retired returns `{STATUS_REGISTERED}` | ✅ Done |
| `groundtruth-kb/src/groundtruth_kb/harness_ops.py` | `_STATUS_VERB_HINT`: `retired` hint updated to direct to `unretire` | ✅ Done |
| `groundtruth-kb/tests/test_harness_lifecycle.py` | `_VALID_EDGES`: add `(STATUS_RETIRED, STATUS_REGISTERED)` | ✅ Done |
| `groundtruth-kb/tests/test_harness_lifecycle.py` | `test_retired_is_terminal()` → `test_retired_is_not_terminal()` | ✅ Done |
| `groundtruth-kb/tests/test_harness_lifecycle.py` | `test_next_states_per_state()`: update retired assertion | ✅ Done |
| `groundtruth-kb/tests/test_harness_lifecycle.py` | `_INVALID_PAIRS` comment: remove "transitions out of terminal state" | ✅ Done |

### Verification

```
19 passed in 0.06s — groundtruth-kb/tests/test_harness_lifecycle.py
ruff check: All checks passed!
```

No new test file was added for `STATUS_RETIRED → STATUS_REGISTERED` because the parametrized `_VALID_EDGES` test and `test_next_states_per_state` already cover the new edge. No existing test behavior was broken.

### CLI Verb (deferred)

The `gt harness unretire` CLI verb is deferred to a follow-on slice. The FSM amendment alone is sufficient: `harness_ops.transition_harness()` calls `harness_lifecycle.validate_transition()` generically, so any caller that invokes the transition programmatically will pass validation. The CLI verb is a UX surface, not a blocking prerequisite.

## Phase 2: Goose Activation (deferred to GO)

After Phase 1 is VERIFIED, activate Goose G:

```
gt harness unretire G        # retired → registered (requires CLI verb)
gt harness activate G         # registered → active
gt harness set-role G --role prime-builder
gt harness set-role G --role loyal-opposition  
gt harness set-precedence G --precedence 20
```

Target registry state (same as v003, unchanged):

| Field | Current | Target |
|-------|---------|--------|
| `status` | `"retired"` | `"active"` |
| `role` | `["loyal-opposition"]` | `["prime-builder", "loyal-opposition"]` |
| `reviewer_precedence` | `null` | `20` |
| `dispatch_quality` | `80.0` | `85.0` |
| `dispatch_max_items` | `1` | `2` |
| `invocation_surfaces.dispatch.dispatch_max_items` | `1` | `2` |

## Work Item

`gt backlog add-work-item` CLI requires a properly-established session context (the `resolve_changed_by` check fails under the current Goose PB session). WI creation is deferred to immediately after activation when Goose has a proper MemBase session. The WI will be:

- Title: "Goose Harness Activation & Role Parity (FSM Amendment)"
- Origin: improvement | Component: harness-registry | Priority: P1
- Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
- Source spec: GOV-HARNESS-ONBOARDING-CONTRACT-001

## Owner Decision Evidence

Chain (from v003, extended):
1. 2026-07-19: Mike initiated `::init gtkb pb`, requested governance bypass for Goose activation
2. Mike selected option A (fast-track bridge proposal)
3. NO-GO at v002 → Mike directed "Fix-and-resubmit"
4. NO-GO at v004 (Finding 9: retired is terminal) → Mike chose Option A (amend FSM)
5. LO captured Option A decision at v005 (NO-ACTION) with full scope analysis
6. This v006 implements the FSM amendment per that scope analysis

Formal DELIB capture deferred to post-activation (same session-provenance constraint as WI creation).

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — harness activation must record owner decision, role assignment, and dispatch topology
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail and GO/NO-GO discipline; numbered bridge chain is canonical
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — project-scope PAUTH governs this implementation
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing specification
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification plan derives tests from linked specifications
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — work item linkage (deferred per above)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — activation recorded as durable artifact
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — traceability preserved
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Goose transitions from retired → registered → active
- `REQ-HARNESS-REGISTRY-001` — registry is the canonical role/dispatch authority; FSM is FR2
- `DCL-SESSION-ROLE-RESOLUTION-001` — session-stated role override already functional for Goose

## Requirement Sufficiency

**Existing requirements sufficient.** The FSM is governed by `REQ-HARNESS-REGISTRY-001` FR2, which defines the four-state lifecycle. The amendment adds one permitted edge to an existing state; it does not add new states or change the fundamental model.

## Specification-Derived Verification

| Spec | Verification |
|------|-------------|
| REQ-HARNESS-REGISTRY-001 FR2 | 19 tests pass; `test_retired_is_not_terminal` asserts retired has outgoing edge; `test_next_states_per_state` asserts `{STATUS_REGISTERED}` |
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal filed as next numbered version in append-only chain |
| REQ-HARNESS-REGISTRY-001 FR3 | `harness_ops._STATUS_VERB_HINT` updated; `transition_harness()` uses FSM generically |

## Acceptance Criteria

1. `pytest groundtruth-kb/tests/test_harness_lifecycle.py` — all 19 tests pass ✅
2. `ruff check` on changed files — clean ✅
3. `is_terminal(STATUS_RETIRED)` returns `False`
4. `next_states(STATUS_RETIRED)` returns `frozenset({STATUS_REGISTERED})`
5. `is_valid_transition(STATUS_RETIRED, STATUS_REGISTERED)` returns `True`
6. `is_valid_transition(STATUS_RETIRED, STATUS_ACTIVE)` still returns `False`

## Owner Decisions / Input

- Mike selected Option A (amend FSM) per v005
- This revision implements the FSM amendment per the LO's scope analysis

## Recommended Commit Type

`feat:` — FSM amendment adding retired→registered transition, prerequisite for Goose harness activation.