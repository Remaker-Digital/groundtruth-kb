REVISED

# Implementation Proposal - Startup-Payload Canonical-State Drift Fix - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-startup-payload-canonical-state-drift
Version: 003
Responds to: bridge/gtkb-startup-payload-canonical-state-drift-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["scripts/session_self_initialization.py", "groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py", "platform_tests/scripts/test_session_self_initialization_canonical_consistency.py", "platform_tests/groundtruth_kb/test_mode_switch_derive_role_slot.py", "groundtruth.db"]

## Claim

REVISED to address Codex Loyal Opposition NO-GO at `bridge/gtkb-startup-payload-canonical-state-drift-002.md`. The three findings are resolved as follows:

- **P1 (topology fallback diverges from canonical helper)**: the local `_derive_topology_from_role_map` is removed. The render path imports and uses `groundtruth_kb.mode_switch.derive.topology_from_role_map` directly. The proposal no longer defines its own algorithm; canonical fail-closed `multi_harness` semantics for ambiguous/malformed input are inherited.
- **P2 (verification plan missing existing topology regression surface)**: the verification plan now runs `platform_tests/scripts/test_session_self_initialization_topology_derive.py` (6 existing tests covering empty map, missing harnesses map, legacy scalar single-role, acting-prime-builder coercion, two-singleton multi-harness, one-multi-role single-harness) and `platform_tests/groundtruth_kb/test_mode_switch_transaction.py` + siblings (26 tests covering the mode-switch transaction component) alongside the new canonical-consistency tests.
- **P3 (persisted-state scope ambiguity)**: scope is explicitly **render-only**. `scripts/session_self_initialization.py` derives the rendered labels from live `harness-state/role-assignments.json` at render time. `scripts/workstream_focus.py` is NOT in scope: per Slice 1 of `gtkb-operating-mode-transaction-001` (now landed), `workstream_focus.save_state` at line 516 already calls `topology_from_role_map(role_map)` and writes the canonical value, so stale persisted `.claude/session/work-subject.json` state self-corrects on the next workstream-focus operation. This proposal does not mutate the persisted state file.

A canonical `role_slot_from_active_harness(role_map, active_harness_id)` helper is added to the same `mode_switch/derive.py` module so role-slot derivation lives next to topology derivation under one truth source.

The underlying drift remains: `scripts/session_self_initialization.py:4128` renders `role_slot` from `workstream.get("role_slot") or "shared"`, and `:4129` renders `topology_mode` from `workstream.get("topology_mode") or "single_harness"`. Live `harness-state/role-assignments.json` records harness `A` as `["loyal-opposition"]` and harness `B` as `["prime-builder"]` — two singleton role-sets, which is multi-harness topology per `topology_from_role_map`'s `len(harnesses) != 1 -> MULTI_HARNESS` branch.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. This bridge file at `E:\GT-KB\bridge\gtkb-startup-payload-canonical-state-drift-003.md` is in-root. `E:\GT-KB\scripts\session_self_initialization.py` is in-root. `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\mode_switch\derive.py` is in-root. `E:\GT-KB\platform_tests\scripts\test_session_self_initialization_canonical_consistency.py` is in-root. `E:\GT-KB\platform_tests\groundtruth_kb\test_mode_switch_derive_role_slot.py` is in-root. MemBase at `E:\GT-KB\groundtruth.db` is in-root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated with this REVISED entry inserted above the NO-GO `-002`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-SESSION-SELF-INITIALIZATION-001` - the governance contract for fresh-session startup; this proposal upholds it by fixing the topology/role-slot derivation.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - Prime Builder contract for accurate startup disclosure.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - defines single-harness vs multi-harness topology by role-set cardinality; canonical helper `topology_from_role_map` realizes this ADR.
- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` - the spec that produced `topology_from_role_map` per its module docstring; this proposal aligns startup render with that spec.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - depends on accurate topology classification; this fix makes startup-payload reporting agree with the dispatcher's applicability check.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - role-set wire form (list valued); topology derived from cardinality.
- `GOV-ACTING-PRIME-BUILDER-001` - legacy `acting-prime-builder` value READ-coerced to `prime-builder` for topology purposes (canonical helper already implements this).
- `GOV-STANDING-BACKLOG-001` - one tracking `work_item` per slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - all changes are auditable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - canonical-state derivation pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - tracking `work_item` lifecycle.
- `OM-DELTA-0030` - claims about platform capabilities must distinguish implemented from intended; the startup-payload topology field is a claim about runtime state, and a wrong claim violates this directive.
- `.claude/rules/operating-role.md` § Role Assignment Rules + § Role Set Schema - the active topology-determination logic.
- `.claude/rules/operating-model.md` §3 - implemented-vs-intended distinction.

## Prior Deliberations

Deliberation searches executed before filing this revision:

- `python -m groundtruth_kb deliberations search "startup payload canonical state drift topology role-map" --limit 5` returned canonical init-keyword and single-harness dispatcher context.
- `python -m groundtruth_kb deliberations search "topology_from_role_map fail-closed multi_harness canonical" --limit 5` returned single-harness operating mode and mode-switch transaction context.

Relevant deliberations carried forward:

- `DELIB-0840` - owner decision establishing `GOV-SESSION-SELF-INITIALIZATION-001` (mandates accurate startup disclosure). Cited in `-002` NO-GO Prior Deliberations.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - drift between generated startup labels and canonical state is a deterministic-services defect; the canonical helper exists precisely to remove this drift class.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` - strategic self-improvement directive authorizing fix-worthy issue capture into backlog/work-item state.
- `DELIB-1511` - single-harness bridge dispatcher review; relevant to strict bridge role/topology routing behavior. Cited in `-002` NO-GO.
- `DELIB-1514` - canonical init-keyword syntax review; adjacent startup-routing context. Cited in `-002` NO-GO.
- No searched prior deliberation waives the existing canonical fail-closed topology semantics or authorizes a duplicate local helper.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AskUserQuestion answer "Audit + fix + regression test (Recommended)" for the startup-payload-drift WI scope. This authorizes the audit + fix + regression-test approach reflected in this revision.
- 2026-05-14 UTC, S350: owner AskUserQuestion answer "Fix startup-payload-canonical-state-drift NO-GO" selecting this thread as the current session's top-priority Prime action over five sibling Prime-actionable NO-GO threads and standing-backlog alternatives. This authorizes filing this REVISED-1 in the current session.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work" - broader queue authorization.

No new owner decision is required before Loyal Opposition review of this revision. The revision implements the corrections required by `-002` NO-GO and does not expand owner-decision scope.

## Requirement Sufficiency

Existing requirements sufficient.

The fix operates under existing `GOV-SESSION-SELF-INITIALIZATION-001` + `ADR-SINGLE-HARNESS-OPERATING-MODE-001` + `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` + `.claude/rules/operating-role.md` § Role Set Schema. No new requirements proposed. The canonical helper `topology_from_role_map` already realizes the spec; this proposal aligns the startup render path with that helper.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation against the standing backlog. Creates exactly one tracking `work_item` (singleton MemBase insertion through the formal-artifact-approval pathway when packet is required, else canonical Python API). No protected narrative artifact is touched; this proposal operates on platform infrastructure source (`scripts/`, `groundtruth-kb/src/`) and test code only. The `GOV-STANDING-BACKLOG-001` `CLAUSE-VISIBILITY-BULK-OPS` clause does not apply.

## Proposed Scope

### IP-1: Render-time topology derivation using canonical helper

In `scripts/session_self_initialization.py`:

1. Add module-level import: `from groundtruth_kb.mode_switch.derive import role_slot_from_active_harness, topology_from_role_map`.
2. Before the existing render block at line 4127-4129, load `harness-state/role-assignments.json` and resolve the active harness ID from `harness-state/harness-identities.json` (the existing resolver pattern used elsewhere in the file).
3. Compute canonical values:
   - `canonical_topology = topology_from_role_map(role_map)` - returns `single_harness` iff exactly one harness's role-set contains BOTH `prime-builder` AND `loyal-opposition`; all other shapes return `multi_harness` (canonical fail-closed semantics).
   - `canonical_role_slot = role_slot_from_active_harness(role_map, active_harness_id)` - returns `prime-builder`, `loyal-opposition`, or `shared` per IP-2 below.
4. Replace `role_slot = str(workstream.get("role_slot") or "shared")` at line 4128 with `role_slot = canonical_role_slot`.
5. Replace `topology_mode = str(workstream.get("topology_mode") or "single_harness")` at line 4129 with `topology_mode = canonical_topology`.

No local helper function is defined. The render path imports the canonical helpers and uses their results directly. Persisted `workstream["role_slot"]` and `workstream["topology_mode"]` fields are bypassed at render time.

### IP-2: Canonical role_slot helper in mode_switch/derive.py

In `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py`, add a new function adjacent to `topology_from_role_map`:

```python
SHARED = "shared"
PRIME_BUILDER = "prime-builder"
LOYAL_OPPOSITION = "loyal-opposition"


def role_slot_from_active_harness(
    role_map: dict[str, Any],
    active_harness_id: str | None,
) -> str:
    """Return the role-slot label for the active harness.

    Returns ``prime-builder`` or ``loyal-opposition`` for a singleton
    role-set, ``shared`` for a multi-element role-set, and ``shared``
    fail-safe for missing/malformed/unresolved input. Reuses
    ``_role_set`` so legacy scalar role values and the
    ``acting-prime-builder`` coercion are handled identically to the
    topology helper.
    """
    if not isinstance(role_map, dict) or not active_harness_id:
        return SHARED
    harnesses = role_map.get("harnesses")
    if not isinstance(harnesses, dict):
        return SHARED
    record = harnesses.get(active_harness_id)
    roles = _role_set(record)
    if not roles:
        return SHARED
    if len(roles) == 1:
        return next(iter(roles))
    return SHARED
```

The helper reuses the existing `_role_set` normalization, so legacy scalar role values and the `acting-prime-builder -> prime-builder` coercion are handled identically to `topology_from_role_map`. Both helpers share a single truth source for role-set parsing.

`role_slot_from_active_harness` is exported through the module surface for use from `scripts/session_self_initialization.py` and any future call sites (the existing `scripts/workstream_focus.py` save_state path may adopt it in a separate slice; no `workstream_focus.py` changes are in scope for this proposal).

### IP-3: Regression test asserting render path uses canonical state

Add `platform_tests/scripts/test_session_self_initialization_canonical_consistency.py` with tests:

1. `test_topology_label_matches_role_map_cardinality_two_singletons` - fixture role-map with 2 harnesses each singleton role-set -> rendered `Harness topology` line shows `multi_harness`.
2. `test_topology_label_matches_role_map_cardinality_one_multi_role` - fixture role-map with 1 harness multi-element role-set -> rendered line shows `single_harness`.
3. `test_topology_label_matches_canonical_fail_closed_for_empty_role_map` - fixture empty role-map -> rendered line shows `multi_harness` (matches canonical fail-closed semantics, NOT the previous `single_harness` literal default).
4. `test_role_slot_renders_singleton_role_token_prime` - active harness B with role-set `["prime-builder"]` -> rendered `Bridge role slot` line shows `prime-builder`.
5. `test_role_slot_renders_singleton_role_token_lo` - active harness A with role-set `["loyal-opposition"]` -> rendered line shows `loyal-opposition`.
6. `test_role_slot_renders_shared_for_multi_element` - active harness with role-set `["prime-builder", "loyal-opposition"]` -> rendered line shows `shared`.
7. `test_role_slot_renders_shared_for_missing_active_harness` - active harness ID not in role-map -> rendered line shows `shared` (canonical fail-safe).
8. `test_render_ignores_stale_persisted_workstream_state` - fixture `.claude/session/work-subject.json` with stale `topology_mode: single_harness` and live role-map with two singletons -> rendered line shows `multi_harness` (the canonical helper overrides the stale persisted value).

Add `platform_tests/groundtruth_kb/test_mode_switch_derive_role_slot.py` with tests for the new canonical helper:

9. `test_role_slot_singleton_prime` - role-map with harness having `["prime-builder"]` -> returns `prime-builder`.
10. `test_role_slot_singleton_lo` - role-map with harness having `["loyal-opposition"]` -> returns `loyal-opposition`.
11. `test_role_slot_multi_element_returns_shared` - role-map with harness having both roles -> returns `shared`.
12. `test_role_slot_missing_harness_returns_shared` - active harness ID not present -> returns `shared`.
13. `test_role_slot_legacy_scalar_role` - legacy scalar `"role": "prime-builder"` -> returns `prime-builder` (reuses `_role_set` coercion).
14. `test_role_slot_acting_prime_builder_coercion` - role-set with `acting-prime-builder` -> returns `prime-builder` (GOV-ACTING-PRIME-BUILDER-001 READ-coercion).
15. `test_role_slot_empty_role_map_returns_shared` - empty/malformed role-map -> returns `shared`.
16. `test_role_slot_none_active_harness_returns_shared` - `active_harness_id=None` -> returns `shared`.

### IP-4: Tracking work_item

Insert one `work_items` row via canonical `KnowledgeDB.insert_work_item()`:

- `id`: next-available `WI-NNNN` minted from canonical Python API.
- `origin`: `defect`.
- `component`: `session-startup`.
- `resolution_status`: `open`.
- `source_spec_id`: `GOV-SESSION-SELF-INITIALIZATION-001`.
- `related_bridge_threads`: `gtkb-startup-payload-canonical-state-drift`.
- `title`: `Startup-payload canonical-state drift fix (canonical topology + role-slot helpers; render-only)`.
- `changed_by`: `prime-builder/claude/B`.
- `stage`: `implementing`.

## Specification-Derived Verification Plan

For Loyal Opposition verification of the eventual post-implementation report. Each test maps to a Specification Link cited above.

1. `python -m pytest platform_tests/scripts/test_session_self_initialization_canonical_consistency.py -v` - 8 new tests PASS. Maps to `GOV-SESSION-SELF-INITIALIZATION-001` + `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` + `OM-DELTA-0030`.
2. `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_derive_role_slot.py -v` - 8 new tests PASS. Maps to `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` + `ADR-SINGLE-HARNESS-OPERATING-MODE-001` + `GOV-HARNESS-ROLE-PORTABILITY-001` + `GOV-ACTING-PRIME-BUILDER-001`.
3. `python -m pytest platform_tests/scripts/test_session_self_initialization_topology_derive.py -v` - 6 existing tests PASS unchanged (regression surface for the topology helper). Codex's `-002` NO-GO already confirmed these pass locally; this proposal asserts they remain green.
4. `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py -v` - 26 existing mode-switch transaction tests PASS unchanged. Codex's `-002` NO-GO already confirmed these pass locally; this proposal asserts they remain green.
5. `python -m ruff check scripts/session_self_initialization.py groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py platform_tests/scripts/test_session_self_initialization_canonical_consistency.py platform_tests/groundtruth_kb/test_mode_switch_derive_role_slot.py` - zero errors.
6. `python -m mypy --strict groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py` - zero errors (strict-mypy lane that previously surfaced `no-any-return` on adjacent policy code).
7. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-payload-canonical-state-drift` - `preflight_passed: true`, no missing specs.
8. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-payload-canonical-state-drift` - exit 0, zero blocking gaps.
9. End-to-end smoke: launch a fresh GT-KB session; inspect startup payload; verify `Harness topology` field renders `multi_harness` (matching current canonical role-map state with two singleton harnesses).
10. Source inspection: `role_slot_from_active_harness` and `topology_from_role_map` are imported and called in `scripts/session_self_initialization.py`; no local duplicate-truth-source helper exists.
11. MemBase tracking WI inserted per IP-4 with `related_bridge_threads='gtkb-startup-payload-canonical-state-drift'` (lesson carried forward from `gtkb-implementation-gate-friction-hygiene-016` NO-GO F1 about IP-E tracking-field omission).

## Risks and Rollback

- **Risk**: derivation function fails on unreadable `harness-state/role-assignments.json`. Mitigation: `topology_from_role_map` and `role_slot_from_active_harness` both fail-closed/safe to the rendered defaults (`multi_harness`/`shared`); the loader catches `FileNotFoundError`/`JSONDecodeError` and passes an empty dict to the helpers. Rollback: revert the import + replacement at lines 4128-4129 to the prior literal-default form.
- **Risk**: importing `groundtruth_kb.mode_switch.derive` from `scripts/session_self_initialization.py` creates an import path the script doesn't currently exercise. Mitigation: `scripts/` modules already import from `groundtruth_kb` elsewhere (`scripts/workstream_focus.py:516` imports `topology_from_role_map` from this exact module); the import path is established and the test surface will catch any regression.
- **Risk**: regression test fixtures become stale if role-map schema changes. Mitigation: tests use the canonical `_role_set` normalization through the canonical helpers; future schema changes update the helpers and the tests in one place.
- **Risk**: persisted `.claude/session/work-subject.json` retains stale `single_harness` label until the next workstream operation. Mitigation: this is by design per the render-only scope; `workstream_focus.save_state` already derives the canonical value (verified at `scripts/workstream_focus.py:516` and at `platform_tests/scripts/test_session_self_initialization_topology_derive.py:92-119`). If owner wants immediate persisted-state regeneration, that is a separate scope decision (P3 option 2) and is explicitly not requested here.
- **General rollback**: changes isolated to two source files + two new test files + one tracking WI. `git revert <commit-sha>` suffices.

## Sequenced Dependencies

This thread is independent of friction-hygiene (NO-GO at `-016` awaiting Prime REVISED on a different scope), benchmark-suite (separate Slice 2 thread), and operating-mode-transaction-001 (provides the canonical helper this proposal consumes; Slice 1 already landed). No dependencies block this revision. May proceed in parallel with the 4 sibling Prime-actionable NO-GO threads at top of `bridge/INDEX.md`.

## Recommended Commit Type

`fix:` - corrects a real drift in startup-payload rendering. The audit + regression-test surface is small. Diff is two source files (~30 lines net) + two new test files + one MemBase row insert. Not net-new capability; not refactor.

## Bridge-Compliance Self-Check

- Plain `## Specification Links` heading (no parenthetical); flat bullet list; no `###` sub-headings inside the section.
- Plain `## Owner Decisions / Input` heading; non-empty; cites two distinct S350 AskUserQuestion answers and one broader queue authorization.
- Plain `## Prior Deliberations` heading; non-empty; cites four DELIBs and two deliberation-search invocations.
- `target_paths` metadata in JSON list form; all five paths in-root under `E:\GT-KB`.
- `## Requirement Sufficiency` section present with exactly one operative state: `Existing requirements sufficient`.
- `## Recommended Commit Type` section present (`fix:`).
- `## Clause Scope Clarification (Not a Bulk Operation)` section present with evidence pattern tokens (`formal-artifact-approval`, `singleton MemBase insertion`).
- `## In-Root Placement Evidence` section present with backticked paths.
- `## Proposed Scope` enumerates IP-1 through IP-4 with `###` sub-headings (sub-headings are inside Proposed Scope, NOT inside Specification Links — bridge-compliance-gate strict-heading rule satisfied).
- All paths in-root under `E:\GT-KB`.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
