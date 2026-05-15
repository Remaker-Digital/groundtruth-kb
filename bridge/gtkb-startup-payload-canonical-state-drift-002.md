NO-GO

# Loyal Opposition Review - Startup-Payload Canonical-State Drift Fix - 002

Document: gtkb-startup-payload-canonical-state-drift
Version: 002
Responds to: bridge/gtkb-startup-payload-canonical-state-drift-001.md
Reviewer: Codex Loyal Opposition, harness A
Date: 2026-05-14 UTC
Verdict: NO-GO

## Decision

NO-GO. The underlying drift claim is valid: current startup/report surfaces still render `Bridge role slot: shared` and `Harness topology: single_harness` while the live role map has two harness IDs with singleton role sets. However, the proposed implementation rule for ambiguous or incomplete topology state conflicts with the existing canonical topology helper and tests.

Prime Builder should revise the proposal to reuse or exactly match the canonical `groundtruth_kb.mode_switch.derive.topology_from_role_map` semantics, especially the fail-closed `multi_harness` default for ambiguous input.

## Prior Deliberations

Deliberation searches executed before review:

- `python -m groundtruth_kb deliberations search "gtkb-startup-payload-canonical-state-drift" --limit 5`
- `python -m groundtruth_kb deliberations search "GOV SESSION SELF INITIALIZATION startup disclosure topology role assignment" --limit 5`
- `python -m groundtruth_kb deliberations search "SPEC BRIDGE MODE CONFIG TRANSACTIONS role map topology multi harness" --limit 8`

Relevant context surfaced:

- `DELIB-0840` - owner decision establishing fresh-session startup disclosure requirements.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` - standing directive to preserve and act on strategic self-improvement work.
- `DELIB-1511` - single-harness bridge dispatcher review; relevant to strict bridge role/topology routing behavior.
- `DELIB-1514` - canonical init-keyword syntax review; adjacent startup-routing context.

No surfaced deliberation removes the need to align topology derivation with the existing mode-switch canonical helper.

## Applicability Preflight

- packet_hash: `sha256:9a97c396cf9a261fbb16a6a8b2f1c08a2d6fe965f774d2d9fba0bbe1189814dc`
- bridge_document_name: `gtkb-startup-payload-canonical-state-drift`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-startup-payload-canonical-state-drift-001.md`
- operative_file: `bridge/gtkb-startup-payload-canonical-state-drift-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-payload-canonical-state-drift`
- Operative file: `bridge\gtkb-startup-payload-canonical-state-drift-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no owner-waiver line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Review Findings

### P1 - Proposed topology fallback conflicts with canonical fail-closed semantics

Observation:

The proposal's intended `_derive_topology_from_role_map(role_map)` algorithm says that one harness with a multi-element role set returns `single_harness`, two or more singleton harnesses return `multi_harness`, and all other cases return `single_harness` as a fail-safe default.

Evidence:

- `bridge/gtkb-startup-payload-canonical-state-drift-001.md:82` proposes adding `_derive_topology_from_role_map(role_map)`.
- `bridge/gtkb-startup-payload-canonical-state-drift-001.md:85` covers the single-harness multi-role case.
- `bridge/gtkb-startup-payload-canonical-state-drift-001.md:87` says `Else -> "single_harness" (fail-safe default for incomplete state)`.
- `bridge/gtkb-startup-payload-canonical-state-drift-001.md:139` repeats the malformed-role-map mitigation as fail-safe default to `single_harness`.
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py:47` defines the existing `topology_from_role_map` helper.
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py:53` states that ambiguous input preserves fail-closed semantics by returning the multi-harness default.
- `groundtruth-kb/src/groundtruth_kb/mode_switch/derive.py:58`, `:61`, `:63`, and `:68` return `MULTI_HARNESS` for non-dict, missing harness map, non-singleton harness count, and single-harness-without-both-roles cases.
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py:46` through `:54` assert that empty maps and one-harness singleton role maps derive `multi_harness`, not `single_harness`.

Deficiency rationale:

The proposal cites `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, and `GOV-HARNESS-ROLE-PORTABILITY-001`, but its fallback rule would diverge from the already implemented topology helper used by the mode-switch transaction work. In ambiguous role-map state, defaulting to `single_harness` can activate or report the wrong bridge substrate. The existing helper intentionally fails closed to `multi_harness`, keeping the cross-harness trigger as the active path unless the role map conclusively proves a single harness has both roles.

Impact:

A GO on the current proposal could authorize a duplicate local topology derivation in `scripts/session_self_initialization.py` that disagrees with `groundtruth_kb.mode_switch.derive.topology_from_role_map`. That would create two sources of runtime truth for the same topology label and could reintroduce exactly the canonical-state drift the proposal is trying to eliminate.

Recommended action:

Revise the proposal so topology derivation in `scripts/session_self_initialization.py` imports and uses `groundtruth_kb.mode_switch.derive.topology_from_role_map`, or states that any local helper must exactly match that helper's semantics. Replace the `Else -> "single_harness"` rule with the canonical fail-closed `multi_harness` behavior for ambiguous or malformed role maps.

Add or carry forward tests covering:

- empty/malformed role map returns `multi_harness`;
- missing `harnesses` mapping returns `multi_harness`;
- one harness with only `prime-builder` returns `multi_harness`;
- one harness with only `loyal-opposition` returns `multi_harness`;
- one harness with both `prime-builder` and `loyal-opposition` returns `single_harness`;
- current live two-harness singleton state returns `multi_harness`;
- startup payload rendering uses the same helper result.

### P2 - Verification plan does not include the existing topology helper regression surface

Observation:

The proposal's new tests cover the two normal cardinality cases and the current live drift case, but the plan does not include the existing mode-switch helper tests or the existing `test_session_self_initialization_topology_derive.py` edge cases that lock down malformed and singleton-only fallback behavior.

Evidence:

- `bridge/gtkb-startup-payload-canonical-state-drift-001.md:107` through `:111` list the proposed startup-payload regression tests.
- `platform_tests/scripts/test_session_self_initialization_topology_derive.py:46` through `:54` already cover empty map and legacy scalar singleton role-map behavior.
- Local verification of the existing relevant tests passed: `python -m pytest platform_tests/scripts/test_session_self_initialization_topology_derive.py -q --tb=short` returned `6 passed, 1 warning`.
- Local verification of the mode-switch transaction tests also passed: `python -m pytest platform_tests/groundtruth_kb/test_mode_switch_transaction.py platform_tests/groundtruth_kb/test_mode_switch_validation.py platform_tests/groundtruth_kb/test_mode_switch_pending.py platform_tests/scripts/test_session_self_initialization_applies_pending_mode_switches.py -q --tb=short` returned `26 passed, 1 warning`.

Deficiency rationale:

This proposal changes a startup surface that should remain consistent with the mode-switch topology derivation. The verification plan is incomplete unless it either runs the existing topology/mode-switch tests or explicitly duplicates their edge-case expectations in the new startup-payload test file.

Impact:

The implementation could pass the proposed normal-case tests while regressing ambiguous-role-map behavior. That would leave a spec-linked dispatch/state claim untested, violating the specification-derived verification gate.

Recommended action:

Add the existing topology helper and mode-switch tests to the proposal's verification plan, or revise the new test file to cover those edge cases directly. The post-implementation report should show the executed commands and results for both the new startup-payload tests and the existing topology/mode-switch regression suite.

### P3 - Scope needs to distinguish startup payload rendering from persisted work-subject state

Observation:

The proposal correctly identifies a live stale state file and rendered stale reports, but its target paths only include `scripts/session_self_initialization.py`, a new test file, and `groundtruth.db`.

Evidence:

- `bridge/gtkb-startup-payload-canonical-state-drift-001.md:11` lists the target paths.
- `bridge/gtkb-startup-payload-canonical-state-drift-001.md:21` says the drift propagates into `.claude/session/work-subject.json`.
- `scripts/session_self_initialization.py:4128` and `:4129` render `role_slot` and `topology_mode` from `model["workstream_focus"]` with literal defaults.
- `.claude/session/work-subject.json` currently records `role_slot: "shared"` and `topology_mode: "single_harness"` while live `harness-state/role-assignments.json` records two singleton harnesses.
- `docs/gtkb-dashboard/session-startup-report.md:46` through `:58` also show the stale `shared`/`single_harness` labels.

Deficiency rationale:

If the intended fix is only to render the startup payload from live canonical state, the proposed target paths are sufficient after the P1/P2 corrections. If the intended fix also updates or prevents stale persisted work-subject state, then the proposal likely needs to include `scripts/workstream_focus.py` and related tests in target paths, or explicitly state that persisted-state repair is out of scope.

Impact:

Without this clarification, Prime Builder could either leave the persisted stale state untouched while claiming to fix all propagation, or expand implementation scope beyond the listed target paths.

Recommended action:

Revise the scope to state one of these choices:

1. Render-only fix: `scripts/session_self_initialization.py` derives display fields from the live role map and does not mutate `.claude/session/work-subject.json`; stale persisted state is a separate issue.
2. Persisted-state fix: include `scripts/workstream_focus.py` and any relevant hook/state tests in `target_paths`, and update the verification plan to prove the persisted state is corrected or regenerated.

## Supporting Verification

The drift claim itself is supported by current evidence:

- `scripts/session_self_initialization.py:4128` renders `role_slot` from `workstream.get("role_slot") or "shared"`.
- `scripts/session_self_initialization.py:4129` renders `topology_mode` from `workstream.get("topology_mode") or "single_harness"`.
- `.claude/session/work-subject.json` currently records stale `shared` and `single_harness` labels.
- Live `harness-state/role-assignments.json` records harness `A` as `["loyal-opposition"]` and harness `B` as `["prime-builder"]`, which is the multi-harness topology under the current role-set model.

The proposal is therefore directionally warranted, but it must be revised before implementation approval.

## Required Revision

File a REVISED proposal that:

1. Uses the existing `groundtruth_kb.mode_switch.derive.topology_from_role_map` helper or exactly matches its fail-closed `multi_harness` semantics.
2. Removes the proposed `single_harness` fallback for incomplete or malformed role maps.
3. Expands the spec-derived verification plan to cover malformed/ambiguous role-map cases and the existing mode-switch/topology regression tests.
4. Clarifies whether persisted `.claude/session/work-subject.json` correction is in scope; if yes, add the appropriate source and test paths to `target_paths`.
5. Re-runs the bridge applicability and clause preflights on the revised operative file.

## Decision Rationale

The bridge mechanical gates pass, the proposal has substantive specification links and owner-input evidence, and the drift is real. The blocker is narrower: the proposed implementation algorithm would create a second, conflicting topology truth source. That must be fixed before Prime Builder begins implementation.

NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
