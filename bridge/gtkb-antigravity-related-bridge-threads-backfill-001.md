NEW

# Antigravity Onboarding: WI-3362 - Backfill related_bridge_threads Linkage for WI-3337..WI-3349

bridge_kind: implementation_proposal
Document: gtkb-antigravity-related-bridge-threads-backfill
Version: 001 (NEW)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3362 (PROJECT-ANTIGRAVITY-INTEGRATION umbrella-direct work item)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3362
target_paths: ["groundtruth.db"]
Recommended commit type: chore:

## Summary

The thirteen PROJECT-ANTIGRAVITY-INTEGRATION work items WI-3337 through WI-3349 all have an empty `related_bridge_threads` field in MemBase (verified: all thirteen rows return None). Without that linkage, the verified-backlog reconciler (scripts/bridge_verified_backlog_reconciler.py) cannot mechanically connect a work item to the bridge thread that implements it, so it cannot auto-resolve those work items when their threads reach VERIFIED. WI-3362 backfills the field.

This proposal backfills `related_bridge_threads` on the nine of those work items that already have a bridge thread (WI-3337 through WI-3345), using an evidence-verified work-item-to-thread mapping. The four onboarding work items WI-3346 through WI-3349 have no bridge thread yet (their onboarding work is not started), so there is nothing to link; they are recorded here as deferred and will be linked when their threads are filed. The backfill changes no work-item lifecycle state - it adds a linkage metadata field only.

## Background

The reconciler's contract (scripts/bridge_verified_backlog_reconciler.py): `parse_related_bridge_threads` reads the field into bridge document slugs, and `bridge_thread_has_parent_evidence` then requires the bridge thread chain itself to carry the exact work item ID before it will mechanically close the work item. So `related_bridge_threads` is the linkage hint that points the reconciler at the candidate thread; the reconciler still does its own parent-evidence check before resolving. Backfilling the field does not by itself resolve any work item - it enables the reconciler to find the thread and run that check.

The Antigravity Integration tracker (memory/antigravity-integration-status.md section 3) records a working work-item-to-thread mapping but notes it is "evidence-based where a GO file or impl-authorization packet names the WI; otherwise title inference," and that the empty `related_bridge_threads` field is exactly what WI-3362 exists to backfill. This proposal carries that mapping forward as the proposed backfill data and commits the implementation phase to evidence-verify each link against the bridge thread before writing it.

## Specification Links

- REQ-HARNESS-REGISTRY-001 - the governing requirement; WI-3362 is umbrella-direct hygiene under the Antigravity Integration project that implements it.
- DELIB-2079 - the owner-decided Antigravity Integration design; WI-3362 keeps the project's work-item records mechanically reconcilable.
- GOV-STANDING-BACKLOG-001 - the work_items backlog governance; WI-3362 mutates a metadata field on work_items rows and changes no lifecycle state (see Clause Scope Clarification).
- GOV-FILE-BRIDGE-AUTHORITY-001 - this work proceeds through the file bridge; bridge/INDEX.md remains canonical workflow state, and the bridge thread slugs are the linkage values being written.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the only artifact mutated is groundtruth.db within the E:\GT-KB project root (see In-Root Placement Evidence).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the backfill verification from the linked specifications and WI-3362's scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the work-item-to-thread linkage is preserved as durable MemBase metadata (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the backfill restores traceability across the Antigravity work-item / bridge-thread artifact graph (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - correct linkage is what lets the reconciler act on the VERIFIED lifecycle trigger (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design; WI-3362 is umbrella-direct hygiene under that project.
- DELIB-2081 - the owner decision (AUQ DECISION-0663) that the Antigravity PAUTH covers REQ-HARNESS-REGISTRY-001 and ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 work; WI-3362 falls under that authorization.
- bridge/gtkb-bridge-verified-backlog-retirement-006.md - a prior NO-GO that found an overbroad `related_bridge_threads` closure predicate; it is why the reconciler now requires explicit parent evidence (the bridge thread chain carrying the work item ID) in addition to the linkage field. This proposal's evidence-verified mapping respects that: linkage is a hint, not a closure authority.
- No prior deliberation was found that resolves or supersedes the WI-3337..WI-3349 linkage backfill; WI-3362 is the work item created for exactly this gap.

## Owner Decisions / Input

The Antigravity Integration project was owner-decided in the 2026-05-16 eleven-question AskUserQuestion clarification interview recorded as DELIB-2079; the project authorization PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2081; scope REQ-HARNESS-REGISTRY-001) authorizes the project's implementation work through the bridge protocol. WI-3362 is an umbrella-direct work item under that project. On 2026-05-18 the owner directed, via AskUserQuestion, that the Antigravity onboarding sequence be prioritized and explicitly directed Prime Builder to proceed with WI-3362.

This proposal implements WI-3362 within that authorized scope. It asserts no new requirement and requires no further owner decision before GO.

## Requirement Sufficiency

Existing requirements sufficient. WI-3362 is a data-hygiene backfill: it populates an existing metadata field so an existing mechanism (the verified-backlog reconciler) can function as designed. It introduces no new behavior contract. The reconciler's contract and the `related_bridge_threads` field already exist. No new or revised GOV/SPEC/PB/DCL artifact is required before implementation.

## Clause Scope Clarification

WI-3362 mutates the `related_bridge_threads` metadata field on up to nine work_items rows. It does NOT resolve, retire, promote, or change the lifecycle state (stage, resolution_status, status) of any work item; it produces no inventory that removes or hides work; the visible open-backlog state is unchanged. It is a linkage-metadata backfill, not a standing-backlog lifecycle bulk operation.

Where GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS asks for visibility controls on a multi-item operation, this proposal satisfies them in place: the Scope section below enumerates every work item and the exact proposed `related_bridge_threads` value for each (the operation's complete inventory); the proposal is reviewed by Loyal Opposition before any write (the review packet); and the operation is owner-authorized under DELIB-2079 and the active Antigravity PAUTH. No work item's tracked/open status changes, so no deferred-decision marker or separate owner-approval packet for a lifecycle bulk action is required.

## In-Root Placement Evidence

Per ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT, the only artifact mutated by this work is `E:\GT-KB\groundtruth.db` - the MemBase database, in-root. The backfill creates no new files, no runtime state directory, and no `applications/` paths. No artifact outside E:\GT-KB is created, read as a live dependency, or required.

## Scope

### The backfill

For each work item below, the implementation sets `related_bridge_threads` to a JSON list of the bridge thread slug(s) that implement it, via the governed work-item update path (one append-only new work-item version per row, with `changed_by`, `changed_at`, and a `change_reason` citing this proposal). The proposed mapping, carried forward from the Antigravity Integration tracker and to be evidence-verified at implementation:

| Work item | Proposed related_bridge_threads | Verified-state note |
| --- | --- | --- |
| WI-3337 | ["gtkb-harness-registry-table-schema"] | thread VERIFIED |
| WI-3338 | ["gtkb-harness-registry-hot-path-projection"] | thread VERIFIED |
| WI-3339 | ["gtkb-harness-lifecycle-fsm"] | thread VERIFIED |
| WI-3340 | ["gtkb-harness-cli-command-group"] | thread VERIFIED |
| WI-3341 | ["gtkb-harness-role-portability-fr9"] | thread VERIFIED |
| WI-3342 | ["gtkb-harness-registry-reader-migration"] | thread in progress |
| WI-3343 | ["gtkb-adr-harness-registry-extension"] | thread VERIFIED at -008 |
| WI-3344 | ["gtkb-harness-data-driven-dispatch"] | thread VERIFIED |
| WI-3345 | ["gtkb-antigravity-ide-research-spike"] | thread NEW (filed 2026-05-18) |
| WI-3346 | (none - no thread yet) | onboarding not started |
| WI-3347 | (none - no thread yet) | onboarding not started |
| WI-3348 | (none - no thread yet) | onboarding not started |
| WI-3349 | (none - no thread yet) | onboarding not started |

### Implementation-phase evidence verification

Before writing each link, the implementation phase confirms the bridge thread chain for the proposed slug carries the exact work item ID (the same parent-evidence standard the reconciler's `bridge_thread_has_parent_evidence` applies). A proposed link that fails this check is corrected or recorded as unverified rather than written. This keeps the backfill from reintroducing the overbroad-linkage defect that `bridge/gtkb-bridge-verified-backlog-retirement-006.md` flagged.

### Deferred items

WI-3346 through WI-3349 have no bridge thread yet (their onboarding work is gated on the WI-3345 research spike). They are in WI-3362's nominal range but have nothing to link; their `related_bridge_threads` stays empty. When their threads are filed during the onboarding sequence, the linkage is added then - by the onboarding work items or a follow-on backfill, not by this proposal.

## Files Expected To Change

- `groundtruth.db` - up to nine new append-only work-item versions (WI-3337 through WI-3345), each setting `related_bridge_threads`. No other table is touched. No work item's lifecycle fields change.

No source, test, hook, or configuration file is modified.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| WI-3362 scope (backfill related_bridge_threads for WI-3337..WI-3349) | After the backfill, a MemBase read of each of WI-3337..WI-3345 confirms `related_bridge_threads` is populated with the verified thread slug; WI-3346..WI-3349 remain empty as recorded. |
| Reconciler contract (scripts/bridge_verified_backlog_reconciler.py) | `parse_related_bridge_threads` applied to each backfilled value returns the expected slug; the value is a well-formed JSON list of slug strings the reconciler can consume. |
| Evidence-verified linkage (gtkb-bridge-verified-backlog-retirement-006 NO-GO) | For each written link, the post-implementation report records that the bridge thread chain carries the work item ID, satisfying the reconciler's parent-evidence requirement. |
| GOV-STANDING-BACKLOG-001 (no lifecycle change) | A before/after comparison confirms each work item's stage, resolution_status, and status are unchanged; only `related_bridge_threads` changed. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping, the exact MemBase read commands, and the observed before/after values per work item. |

The backfill is a MemBase metadata mutation, not a code change; per the file-bridge protocol a test may be a logical assertion (the field is populated / equals the expected value / lifecycle fields unchanged). Verification is by MemBase read-back, demonstrated in the post-implementation report, plus `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill`.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] Each proposed work-item-to-thread link is evidence-verified (the bridge thread chain carries the work item ID) before it is written.
- [ ] WI-3337 through WI-3345 each have `related_bridge_threads` populated with the verified thread slug as a well-formed JSON list.
- [ ] WI-3346 through WI-3349 remain unlinked (no thread yet) and are recorded as deferred.
- [ ] No work item's lifecycle fields (stage, resolution_status, status) change.
- [ ] The post-implementation report carries the per-work-item before/after values and the parent-evidence confirmation.
- [ ] Loyal Opposition returns VERIFIED before the backfill is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this -001 draft via --content-file before the live INDEX entry is inserted, and re-run against the indexed operative file after filing. Observed results are recorded in the Applicability Preflight and Clause Applicability sections below.

## Applicability Preflight

The applicability preflight was run against this -001 draft via `--content-file` prior to INDEX insertion:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill --content-file bridge/gtkb-antigravity-related-bridge-threads-backfill-001.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:1d6a8a28a4d3675e349cfc8e98657b14b340996b2a371342610524f3a5367b46

All applicable required and advisory cross-cutting specs are cited in this proposal's Specification Links.

## Clause Applicability

The ADR/DCL clause preflight was run against this -001 draft via `--content-file` prior to INDEX insertion:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill --content-file bridge/gtkb-antigravity-related-bridge-threads-backfill-001.md`

- Clauses evaluated: 5 (must_apply: 5, may_apply: 0, not_applicable: 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (pass)

| Clause | Applicability | Evidence found |
|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | must_apply | yes |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | must_apply | yes |

GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evaluates must_apply with evidence found: the Clause Scope Clarification section documents this as a metadata-linkage backfill with no lifecycle-state change, and the per-work-item inventory, Loyal Opposition review, and owner authorization satisfy the clause's visibility controls.

## Risk And Rollback

- R1 (medium): a proposed work-item-to-thread link is wrong (a title-inference mapping points at the wrong thread). Mitigation: the implementation phase evidence-verifies each link against the bridge thread chain before writing it; a link that fails verification is corrected or withheld. The mapping in this proposal is explicitly "proposed, to be verified," not asserted as final.
- R2 (low): the backfill format does not match what the reconciler expects. Mitigation: the value is a JSON list of bridge document slugs, matching `parse_related_bridge_threads`; the spec-to-test mapping verifies the parsed result.
- R3 (low): a concurrent session versions one of these work items between verification and write. Mitigation: append-only versioning means the backfill writes a new version over the latest; the implementation re-reads each work item immediately before writing and the change_reason cites this proposal for audit.
- R4 (very low): the backfill is mistaken for a lifecycle bulk operation. Mitigation: no lifecycle field is touched; the Clause Scope Clarification and the no-lifecycle-change acceptance criterion make the metadata-only nature explicit and checkable.

Rollback: append-only versioning keeps the prior (empty-field) work-item versions retrievable; a corrective new version restores the prior state if a link is later found wrong. No file is modified, so there is no on-disk residue.

## Loyal Opposition Asks

1. Confirm that backfilling a linkage metadata field on nine work items, with no lifecycle-state change, is correctly treated as a metadata backfill rather than a GOV-STANDING-BACKLOG-001 lifecycle bulk operation, given the Clause Scope Clarification.
2. Confirm the proposed work-item-to-thread mapping is sound as a starting point, with implementation-phase evidence verification as the gate before each write.
3. Confirm that deferring WI-3346..WI-3349 (no thread yet) rather than forcing a link is correct, and that the onboarding work items will carry their own linkage when their threads are filed.
4. Confirm the JSON-list-of-slugs format matches the reconciler's `parse_related_bridge_threads` expectation.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
