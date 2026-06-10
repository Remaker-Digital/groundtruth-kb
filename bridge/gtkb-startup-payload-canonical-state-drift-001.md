NEW

# Implementation Proposal - Startup-Payload Canonical-State Drift Fix

bridge_kind: prime_proposal
Document: gtkb-startup-payload-canonical-state-drift
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization_canonical_consistency.py", "groundtruth.db"]

## Claim

The fresh-session startup payload renders `Harness topology: single_harness` and `Bridge role slot: shared` regardless of the canonical role-assignment state. Direct inspection of `scripts/session_self_initialization.py:4128-4129` shows the topology and role-slot fields default to literal strings (`"shared"`, `"single_harness"`) via `workstream.get(...) or "<default>"`, without reading `harness-state/role-assignments.json` to derive the actual topology from role-set cardinality.

Canonical state inspected this session:
- `harness-state/harness-identities.json`: two harnesses (A=codex, B=claude); installation-stable IDs assigned 2026-05-05.
- `harness-state/role-assignments.json`: A has role-set `["loyal-opposition"]` (singleton), B has role-set `["prime-builder"]` (singleton); updated 2026-05-13T21:34:35Z.

Two singletons with two distinct harness IDs is **multi-harness topology** per `.claude/rules/operating-role.md` § Role Assignment Rules. The startup payload's `single_harness` label is wrong; the same drift propagates into `.claude/session/work-subject.json` which Codex's SessionStart hook (`single_harness_bridge_automation.py --ensure`) writes back.

This proposal fixes the drift at the source: `scripts/session_self_initialization.py` derives topology + role-slot from the canonical role-assignment data rather than defaulting to literals.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. This bridge file at `E:\GT-KB\bridge\gtkb-startup-payload-canonical-state-drift-001.md` is in-root. Target source at `E:\GT-KB\scripts\session_self_initialization.py` is in-root. Target test file at `E:\GT-KB\platform_tests\scripts\test_session_self_initialization_canonical_consistency.py` is in-root. MemBase target `E:\GT-KB\groundtruth.db` is in-root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated with this NEW entry.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-SESSION-SELF-INITIALIZATION-001` - the governance contract for fresh-session startup; this proposal upholds it by fixing the topology/role-slot derivation.
- `PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001` - the Prime Builder contract for accurate startup disclosure; the fix restores accurate disclosure.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - defines single-harness vs multi-harness topology by role-set cardinality.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - depends on accurate topology classification; this fix aligns the startup-payload-reported topology with the dispatcher's actual applicability.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - role-set wire form (list valued); topology derived from cardinality.
- `GOV-STANDING-BACKLOG-001` - one tracking work_item per slice.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - all changes are auditable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - canonical-state derivation pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - tracking work_item lifecycle.
- `OM-DELTA-0030` - claims about platform capabilities must distinguish implemented from intended; the startup-payload `Harness topology` field is a CLAIM about runtime state, and a wrong claim violates this directive.
- `.claude/rules/operating-role.md` - § Role Assignment Rules + § Role Set Schema; the active topology-determination logic.
- `.claude/rules/operating-model.md` - §3 implemented-vs-intended distinction.
- `bridge/gtkb-self-diagnostic-leak-closure-slice-2-benchmark-suite-009.md` - sibling self-diagnostic GO'd at -010 (context).

## Prior Deliberations

- `DELIB-0840` - owner decision establishing GOV-SESSION-SELF-INITIALIZATION-001 (mandates accurate startup disclosure).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - drift between generated startup labels and canonical state is a deterministic-services defect.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE` - strategic self-improvement directive authorizing fix-worthy issue capture.
- 2026-05-14 UTC, S350: owner AskUserQuestion answered "Audit + fix + regression test (Recommended)" when asked about WI scope for the startup-payload drift discovery. Confirmed earlier this session.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work" - authorization for filing this proposal among the 5-item queue.
- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit directive for this filing.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner AUQ answer "Audit + fix + regression test (Recommended)" for the startup-payload-drift WI scope. This authorizes the audit + fix + regression-test approach in this proposal.
- 2026-05-14 UTC, S350: owner prompt "Proceed with all identified work" - broader queue authorization.
- 2026-05-14 UTC, S350: owner prompt "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal" - explicit directive for this filing.

No new owner decision is required before review.

## Requirement Sufficiency

Existing requirements sufficient.

The fix operates under existing `GOV-SESSION-SELF-INITIALIZATION-001` + `ADR-SINGLE-HARNESS-OPERATING-MODE-001` + `.claude/rules/operating-role.md` § Role Set Schema. No new requirements proposed.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation against the standing backlog. Creates exactly one tracking `work_item`. No formal-artifact-approval packet required (no protected narrative artifact touched; operational platform infrastructure only).

## Proposed Scope

### IP-1: Topology derivation from role-assignment cardinality

In `scripts/session_self_initialization.py`:

1. Replace the literal default `"single_harness"` at line 4129 with a function `_derive_topology_from_role_map(role_map)` that:
   - Loads `harness-state/role-assignments.json` if not already in `workstream` context.
   - Counts distinct harness IDs (`len(role_map["harnesses"])`).
   - If exactly ONE harness ID exists AND its role-set has 2+ elements → `"single_harness"`.
   - If 2+ harness IDs exist each with singleton role-sets → `"multi_harness"`.
   - Else → `"single_harness"` (fail-safe default for incomplete state).
2. Replace literal default `"shared"` at line 4128 with a function `_derive_role_slot_from_active_harness(role_map, harness_id)`:
   - Resolves the active harness's role-set.
   - If role-set is a singleton: returns the single role token (`"prime-builder"` or `"loyal-opposition"`).
   - If role-set has multiple roles: returns `"shared"`.
3. Both derivations execute before the existing `workstream.get(...)` fallback so the rendered label reflects canonical state.

### IP-2: Audit of generated startup-payload fields

Add comments to `scripts/session_self_initialization.py` documenting which fields are CANONICALLY-DERIVED (must match `harness-state/*.json` or `groundtruth.db`) vs USER-INPUT (set by SessionStart hook context). The five fields in scope:
- `harness_topology` → canonically-derived from role-map cardinality
- `role_slot` → canonically-derived from active harness's role-set
- `bridge_role_slot` → canonically-derived (same source)
- `active_application` → user-input from work-subject.json
- `current_subject` → user-input from work-subject.json

### IP-3: Regression test asserting payload labels match canonical state

Add `platform_tests/scripts/test_session_self_initialization_canonical_consistency.py` with tests:

1. `test_topology_label_matches_role_map_cardinality_singleton_role_sets` - fixture role-map with 2 harnesses each singleton role-set → payload renders `multi_harness`.
2. `test_topology_label_matches_role_map_cardinality_multi_element_role_set` - fixture role-map with 1 harness multi-element role-set → payload renders `single_harness`.
3. `test_role_slot_matches_active_harness_singleton` - active harness B with role-set `["prime-builder"]` → role_slot renders `prime-builder`.
4. `test_role_slot_renders_shared_for_multi_element` - active harness with role-set `["prime-builder", "loyal-opposition"]` → role_slot renders `shared`.
5. `test_topology_drift_against_current_canonical_state_fails_loudly` - assert current canonical role-map state derives multi-harness; render payload; verify label says `multi_harness` (not `single_harness`).

### IP-4: Tracking work_item

Insert one `work_items` row via `KnowledgeDB.insert_work_item()`:
- `id`: WI-NNNN (next available; minted from canonical Python API).
- `origin`: `defect`.
- `component`: `session-startup`.
- `resolution_status`: `open`.
- `source_spec_id`: `GOV-SESSION-SELF-INITIALIZATION-001`.
- `title`: `Startup-payload canonical-state drift fix (topology + role-slot derived from role-map cardinality)`.
- `changed_by`: `prime-builder/claude/B`.
- `stage`: `implementing`.

## Specification-Derived Verification Plan

For Loyal Opposition verification of the eventual post-implementation report:

1. `python -m pytest platform_tests/scripts/test_session_self_initialization_canonical_consistency.py -v` - 5 new tests PASS.
2. `python -m ruff check scripts/session_self_initialization.py` - zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-payload-canonical-state-drift` - `preflight_passed: true`, no missing specs.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-payload-canonical-state-drift` - exit 0, zero blocking gaps.
5. End-to-end smoke: launch a fresh GT-KB session; inspect startup payload; verify `Harness topology` field renders `multi_harness` (matching canonical role-map state).
6. Source inspection: `_derive_topology_from_role_map` and `_derive_role_slot_from_active_harness` exist in `scripts/session_self_initialization.py`; both consult `harness-state/role-assignments.json`.
7. MemBase tracking WI inserted per IP-4.

## Risks and Rollback

- **Risk**: derivation function fails on malformed role-map JSON. Mitigation: fail-safe default to `"single_harness"` (matches current behavior for malformed cases). Rollback: revert to literal-default lines.
- **Risk**: regression test fixtures become stale if role-map schema changes. Mitigation: tests assert against canonical schema; future schema changes update both. 
- **General rollback**: changes isolated to one source file + one new test file + one tracking WI. `git revert <commit-sha>` suffices.

## Sequenced Dependencies

This thread is independent of friction-hygiene (NEW @ -013 awaiting Codex VERIFIED) and benchmark-suite (REVISED @ -015 awaiting Codex). No dependencies on operating-mode-transaction or convenience-verbs. May proceed in parallel with the 4 sibling slice-N proposals being filed this session.

## Recommended Commit Type

`fix:` - corrects a known drift in startup-payload rendering. The audit + regression test surface is small.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` section with flat bullets; no `###` sub-headings inside.
- Non-empty `## Prior Deliberations` section.
- Non-empty `## Owner Decisions / Input` section citing explicit S350 directives.
- target_paths metadata in JSON form; all paths in-root under `E:\GT-KB`.
- `## Requirement Sufficiency` section with exactly one operative state: `Existing requirements sufficient`.
- `## Recommended Commit Type` section present.
- `## Clause Scope Clarification (Not a Bulk Operation)` section present.
- `## In-Root Placement Evidence` section present with backticked paths.
- `## Proposed Scope` enumerates IP-1 through IP-4.
- All paths in-root under `E:\GT-KB`.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
