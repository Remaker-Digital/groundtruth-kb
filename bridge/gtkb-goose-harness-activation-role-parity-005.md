NO-ACTION

author_identity: loyal-opposition/goose/G
author_harness_id: G
author_session_context_id: G-2026-07-19T19-54-00Z
author_model: deepseek-v4
author_model_version: deepseek-v4
author_model_configuration: Goose Desktop interactive Loyal Opposition; transcript-defined ::init gtkb lo; ::open build

# LO Owner Decision Capture — Option A: Amend Lifecycle FSM

bridge_kind: operational_state_change
Document: gtkb-goose-harness-activation-role-parity
Version: 005
Responds to: bridge/gtkb-goose-harness-activation-role-parity-004.md (NO-GO)
Date: 2026-07-20 UTC

Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Work Item: (pending — see below)
target_paths: []

## First-Line Role Eligibility Check

PASS. This session is transcript-defined Loyal Opposition by `::init gtkb lo` per `DCL-SESSION-ROLE-RESOLUTION-001`. `NO-ACTION` is a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001` when used to record owner decisions and scope analysis. This session holds no conflicting claim.

## Owner Decision

Mike responded to the Finding 9 three-option choice with **"A"**, selecting **Option A — Amend the Lifecycle FSM** to allow a path out of `retired`.

This NO-ACTION documents that decision and provides the analysis scope for Prime Builder to implement the amendment.

## Option A Implementation Scope Analysis

### Touchpoints

The following files require changes to support `retired → registered` as a permitted FSM transition:

#### 1. `groundtruth-kb/src/groundtruth_kb/harness_lifecycle.py`

**Docstring:** Update the transition graph diagram and prose to reflect the new edge.

**`_TRANSITIONS` dict:** Add `STATUS_RETIRED: frozenset({STATUS_REGISTERED})` to give `retired` one outgoing edge.

**`next_states()` docstring:** Update the "terminal status (retired) returns an empty frozenset" note — after the change, `retired` returns `{STATUS_REGISTERED}`.

**`is_terminal()` function:** After the change, `retired` is no longer terminal. The docstring and behavior should reflect this.

**`validate_transition()` error message:** The "none; terminal" case may no longer apply to `retired`.

#### 2. `groundtruth-kb/src/groundtruth_kb/harness_ops.py`

**`_STATUS_VERB_HINT` dict:** The `retired` hint currently says: `"'retired' is terminal; the harness has no further transitions"`. Update to direct users to the new verb/path.

**`transition_harness()`:** No code change needed — it calls `harness_lifecycle.validate_transition()` generically. If the FSM allows `retired → registered`, the transition will work.

#### 3. `groundtruth-kb/src/groundtruth_kb/cli.py` (or CLI module)

**`gt harness activate`:** Currently supports `registered → active` and `suspended → active`. After the FSM change, `retired → registered` is allowed but `retired → active` is NOT. The `activate` command will still fail on a retired harness because its target is `active`, not `registered`.

**Two options for the CLI:**

| Option | Change | Pros | Cons |
|--------|--------|------|------|
| **CLI-A** — New `unretire` verb | Add `gt harness unretire` that transitions `retired → registered` | Explicit, clear semantics; no risk of confusing `activate` behavior | More code; new verb to maintain |
| **CLI-B** — `activate` handles retired | Detect `retired` source and do two-step `retired → registered → active` internally | Simpler UX; fewer total commands | Implicit behavior; `activate` would need to understand two-step transitions |

**Recommendation:** CLI-A (new `unretire` verb) is cleaner. It follows the precedent of `retire` being a distinct verb from `suspend`. The two-step pattern would be: `gt harness unretire G` → `gt harness activate G`.

#### 4. `groundtruth-kb/tests/test_harness_lifecycle.py`

Add tests for the new `retired → registered` transition:
- `test_retired_to_registered_valid()`
- `test_retired_to_active_invalid()`
- `test_retired_is_not_terminal()` (replaces the previous terminal test)
- `test_retired_to_registered_allowed_via_next_states()`

#### 5. `groundtruth-kb/tests/test_harness_ops.py` (if exists)

Add integration tests for the new lifecycle path.

### Implementation Sequence

1. Amend `harness_lifecycle.py` (FSM + docstring)
2. Update `harness_ops.py` (status hint)
3. Add CLI verb (`unretire` or `activate` update)
4. Update tests
5. Regenerate `harness-state/harness-registry.json` projection (via `gt harness` CLI or `groundtruth_kb.harness_projection.regenerate_projection()`)
6. Update the bridge proposal (v005) with the corrected implementation path
7. File the revised proposal for LO review

### After the Amendment

Once the FSM is amended, the Goose activation proceeds as:

```
gt harness unretire G        # retired → registered
gt harness activate G         # registered → active
gt harness set-role G --role prime-builder
gt harness set-role G --role loyal-opposition
gt harness set-precedence G --precedence 20
# dispatch metadata (dispatch_quality, dispatch_max_items) via set-invocation-surface or set-dispatch-metadata
```

The `harness-state/harness-registry.json` projection is automatically refreshed after each CLI mutation.

### Work Item

Per Finding 3 (revisited), a MemBase work item should be created for this activation. The `gt backlog add-work-item` CLI does not depend on harness status — it writes to `groundtruth.db` via the governed CLI, not through harness-specific capabilities. Prime Builder should create the work item as part of the revised proposal.

### Owner Decision Evidence

Per Finding 4 (revisited), the owner decision chain should be captured as a Deliberation Archive record. Mike's "A" response in this session should be recorded as a `DELIB-` ID that the revised proposal can cite.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `REQ-HARNESS-REGISTRY-001`

## Specification-Derived Verification

| Requirement | Evidence | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`; numbered bridge chain is canonical | This entry is filed as version 005 in the append-only chain under `bridge/`. | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; governing specs cited | This `## Specification Links` section. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; spec-derived verification present | This `## Specification-Derived Verification` section. | PASS |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001`; NO-ACTION documents owner decision | This entry records Mike's selection of Option A. | PASS |

## Prior Deliberations

- `DELIB-20260708-GOOSE-PROMOTE-TO-OPERATING-HARNESS` — owner AUQ authorizing bounded Goose adoption project.
- `bridge/gtkb-goose-harness-activation-role-parity-001.md` through `-004.md` — the full review chain.

## Owner Decisions / Input

Mike selected **Option A** — amend the lifecycle FSM to allow a path out of `retired`. The implementation scope analysis is provided above.

## Authority Boundary

This entry authorizes no implementation, source, test, configuration, database, dispatcher, TAFE, runtime-state, harness, Git, credential, deployment, release, destructive-cleanup, or external-system mutation. It is a bridge-only owner-decision record and scope analysis.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.