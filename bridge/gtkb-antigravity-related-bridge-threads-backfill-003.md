REVISED

# Antigravity Onboarding: WI-3362 - Backfill related_bridge_threads Linkage for WI-3337..WI-3349

bridge_kind: prime_proposal
Document: gtkb-antigravity-related-bridge-threads-backfill
Version: 003 (REVISED; responds to the NO-GO at -002 - re-scopes WI-3362 to a traceability-only metadata backfill and defers automatic closure of INDEX-pruned historical threads to a separate governed slice)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Implements: WI-3362 (PROJECT-ANTIGRAVITY-INTEGRATION umbrella-direct work item)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3362
target_paths: ["groundtruth.db"]
Recommended commit type: chore:

## Summary

The thirteen PROJECT-ANTIGRAVITY-INTEGRATION work items WI-3337 through WI-3349 all have an empty related_bridge_threads field in MemBase (verified: all thirteen rows return None). WI-3362 backfills that field for the nine work items that have a bridge thread (WI-3337 through WI-3345), establishing canonical work-item-to-bridge-thread traceability in MemBase.

This REVISED -003 re-scopes WI-3362 to a traceability-only metadata backfill, per path (b) of the -002 NO-GO. The -002 review found that the backfill alone cannot deliver automatic reconciler closure for six of the nine work items, because their bridge threads have been pruned from live bridge/INDEX.md (the verified-backlog reconciler's authoritative status source). -003 keeps the traceability backfill - which is correct and useful on its own - and explicitly defers automatic closure of the INDEX-pruned historical threads to a separate governed slice. The four onboarding work items WI-3346 through WI-3349 have no bridge thread yet and remain deferred.

## Response to NO-GO (-002)

The -002 NO-GO issued one P1-blocking finding (F1) and one P3 finding (F2).

F1 (P1) - Backfill does not make six historical threads mechanically reconcilable. The -002 review simulated the proposed related_bridge_threads values against scripts/bridge_verified_backlog_reconciler.py: WI-3342 and WI-3343 would resolve; WI-3345 correctly waits (its thread is GO, not VERIFIED); but WI-3337, WI-3338, WI-3339, WI-3340, WI-3341, and WI-3344 would skip as missing_bridge_document, because the reconciler derives latest bridge status from live bridge/INDEX.md and those six threads' Document entries have been pruned from the live index. The -001 proposal claimed automatic reconciler closure as its purpose, which the backfill alone cannot deliver for those six.

Resolution in -003 (path b of the NO-GO's two offered corrections): WI-3362 is re-scoped to a traceability-only metadata backfill. The automatic-resolution claim is removed from the Summary, the acceptance criteria, and the risk framing. Backfilling related_bridge_threads remains correct and valuable as canonical artifact-graph traceability: it records, in MemBase, which bridge thread implemented each work item. For the three work items whose threads are live in bridge/INDEX.md (WI-3342 and WI-3343 VERIFIED; WI-3345 currently GO), the backfill additionally enables reconciler recognition as a side effect. For the six work items whose threads are INDEX-pruned, the backfill provides traceability only; automatic closure of those is explicitly out of scope and deferred (see Deferred Work). This proposal does not restore pruned INDEX entries or change the reconciler.

F2 (P3) - Stale status notes. The -001 mapping called WI-3342's thread "in progress" and WI-3345's thread NEW. -003 refreshes the mapping table from live bridge/INDEX.md state as of 2026-05-18: WI-3342's thread gtkb-harness-registry-reader-migration is VERIFIED; WI-3343's thread gtkb-adr-harness-registry-extension is VERIFIED at -008; WI-3345's thread gtkb-antigravity-ide-research-spike is GO at -002.

## Background

The reconciler's contract (scripts/bridge_verified_backlog_reconciler.py): parse_related_bridge_threads reads the field into bridge document slugs, parse_latest_bridge_statuses derives latest statuses from live bridge/INDEX.md, and a parsed link not present in that live status map classifies as missing_bridge_document; bridge_thread_has_parent_evidence then requires the bridge thread chain to carry the exact work item ID before mechanical closure. So related_bridge_threads is a traceability hint; mechanical closure additionally requires the linked thread to be recognized by the live status source. WI-3362, re-scoped, delivers the traceability hint and is honest that mechanical closure of INDEX-pruned threads is a separate problem.

## Specification Links

- REQ-HARNESS-REGISTRY-001 - the governing requirement; WI-3362 is umbrella-direct traceability hygiene under the Antigravity Integration project that implements it.
- DELIB-2079 - the owner-decided Antigravity Integration design; WI-3362 keeps the project's work-item records traceably linked to their bridge threads.
- GOV-STANDING-BACKLOG-001 - the work_items backlog governance; WI-3362 mutates a metadata field on work_items rows and changes no lifecycle state (see Clause Scope Clarification).
- GOV-FILE-BRIDGE-AUTHORITY-001 - this work proceeds through the file bridge; bridge/INDEX.md remains canonical workflow state, and the bridge thread slugs are the linkage values being written.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - the only artifact mutated is groundtruth.db within the E:\GT-KB project root (see In-Root Placement Evidence).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below derives the backfill verification from the linked specifications and WI-3362's re-scoped traceability-only scope.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the work-item-to-thread linkage is preserved as durable MemBase metadata (advisory).
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the backfill restores traceability across the Antigravity work-item / bridge-thread artifact graph (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - correct linkage is one input the reconciler uses to act on the VERIFIED lifecycle trigger, for threads whose status is live-recognized (advisory).

## Prior Deliberations

- DELIB-2079 - the owner-decided Antigravity Integration design; WI-3362 is umbrella-direct hygiene under that project.
- DELIB-2081 - the owner decision tying the Antigravity PAUTH to REQ-HARNESS-REGISTRY-001; WI-3362 falls under that authorization.
- bridge/gtkb-antigravity-related-bridge-threads-backfill-002.md - the NO-GO this revision responds to; its F1 (re-scope) and F2 (refresh status notes) are addressed above.
- bridge/gtkb-bridge-verified-backlog-retirement-006.md - a prior NO-GO that found an overbroad related_bridge_threads closure predicate; it is why the reconciler now requires explicit parent evidence plus live bridge-status recognition. -003 respects that: the backfill is a traceability hint, not a closure authority, and -003 does not claim closure for INDEX-pruned threads.

## Owner Decisions / Input

The Antigravity Integration project was owner-decided in the 2026-05-16 eleven-question AskUserQuestion clarification interview recorded as DELIB-2079; the project authorization PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION (status active; owner decision DELIB-2081; scope REQ-HARNESS-REGISTRY-001) authorizes the project's implementation work through the bridge protocol. WI-3362 is an umbrella-direct work item under that project. On 2026-05-18 the owner directed, via AskUserQuestion, that the Antigravity onboarding sequence be prioritized and explicitly directed Prime Builder to proceed with WI-3362. This proposal implements WI-3362 within that authorized scope; the re-scope to traceability-only follows the -002 NO-GO's offered correction and asserts no new requirement.

## Requirement Sufficiency

Existing requirements sufficient. WI-3362, as re-scoped, is a traceability metadata backfill: it populates an existing metadata field with the work-item-to-bridge-thread linkage. It introduces no new behavior contract. No new or revised GOV/SPEC/PB/DCL artifact is required. The deferred problem - automatic closure of INDEX-pruned historical threads - is recorded under Deferred Work for a future governed slice; it is not a requirement WI-3362 must satisfy.

## Clause Scope Clarification

WI-3362 mutates the related_bridge_threads metadata field on up to nine work_items rows. It does NOT resolve, retire, promote, or change the lifecycle state (stage, resolution_status, status) of any work item; it produces no inventory that removes or hides work; the visible open-backlog state is unchanged. It is a linkage-metadata backfill, not a standing-backlog lifecycle bulk operation.

Where GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS asks for visibility controls on a multi-item operation, this proposal satisfies them in place: the Scope section enumerates every work item and the exact proposed related_bridge_threads value for each (the operation's complete inventory); the proposal is reviewed by Loyal Opposition before any write (the review packet); and the operation is owner-authorized under DELIB-2079 and the active Antigravity PAUTH. No work item's tracked/open status changes, so no deferred-decision marker or separate owner-approval packet for a lifecycle bulk action is required.

## In-Root Placement Evidence

Per ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT, the only artifact mutated by this work is E:\GT-KB\groundtruth.db - the MemBase database, in-root. The backfill creates no new files, no runtime state directory, and no applications/ paths. No artifact outside E:\GT-KB is created, read as a live dependency, or required.

## Scope

### The traceability backfill

For each work item below, the implementation sets related_bridge_threads to a JSON list of the bridge thread slug(s) that implement it, via the governed work-item update path (one append-only new work-item version per row, with changed_by, changed_at, and a change_reason citing this proposal). The proposed mapping, with status notes refreshed from live bridge/INDEX.md as of 2026-05-18, and to be evidence-verified at implementation:

| Work item | Proposed related_bridge_threads | Live thread status (2026-05-18) | Reconciler effect of the backfill |
| --- | --- | --- | --- |
| WI-3337 | ["gtkb-harness-registry-table-schema"] | VERIFIED; INDEX entry pruned | traceability only (thread INDEX-pruned) |
| WI-3338 | ["gtkb-harness-registry-hot-path-projection"] | VERIFIED; INDEX entry pruned | traceability only (thread INDEX-pruned) |
| WI-3339 | ["gtkb-harness-lifecycle-fsm"] | VERIFIED; INDEX entry pruned | traceability only (thread INDEX-pruned) |
| WI-3340 | ["gtkb-harness-cli-command-group"] | VERIFIED; INDEX entry pruned | traceability only (thread INDEX-pruned) |
| WI-3341 | ["gtkb-harness-role-portability-fr9"] | VERIFIED; INDEX entry pruned | traceability only (thread INDEX-pruned) |
| WI-3342 | ["gtkb-harness-registry-reader-migration"] | VERIFIED; INDEX entry live | traceability + reconciler-recognized |
| WI-3343 | ["gtkb-adr-harness-registry-extension"] | VERIFIED at -008; INDEX entry live | traceability + reconciler-recognized |
| WI-3344 | ["gtkb-harness-data-driven-dispatch"] | VERIFIED; INDEX entry pruned | traceability only (thread INDEX-pruned) |
| WI-3345 | ["gtkb-antigravity-ide-research-spike"] | GO at -002; INDEX entry live | traceability; reconciler waits (not yet VERIFIED) |
| WI-3346 | (none - no thread yet) | onboarding not started | deferred (see Deferred Work) |
| WI-3347 | (none - no thread yet) | onboarding not started | deferred |
| WI-3348 | (none - no thread yet) | onboarding not started | deferred |
| WI-3349 | (none - no thread yet) | onboarding not started | deferred |

### Implementation-phase evidence verification

Before writing each link, the implementation phase confirms the bridge thread chain for the proposed slug carries the exact work item ID (the same parent-evidence standard the reconciler's bridge_thread_has_parent_evidence applies). A proposed link that fails this check is corrected or recorded as unverified rather than written. The bridge files for the INDEX-pruned threads still exist on disk, so this evidence check is performed against the on-disk thread files.

### Deferred Work (explicitly out of WI-3362 scope)

Automatic reconciler closure of the six work items whose bridge threads are pruned from live bridge/INDEX.md (WI-3337, WI-3338, WI-3339, WI-3340, WI-3341, WI-3344) is NOT delivered by WI-3362 and is deferred to a separate governed slice. That slice must decide and implement a protocol-compatible way to restore or recognize authoritative latest bridge status for pruned historical threads (for example: an authoritative status surface independent of INDEX trimming, or a reconciler path that consults the on-disk thread chain). WI-3362 does not pre-judge that design; it records the gap. WI-3346 through WI-3349 are deferred because they have no bridge thread yet; their linkage is added when their threads are filed.

## Files Expected To Change

- groundtruth.db - up to nine new append-only work-item versions (WI-3337 through WI-3345), each setting related_bridge_threads. No other table is touched. No work item's lifecycle fields change.

No source, test, hook, or configuration file is modified.

## Spec-To-Test Mapping

| Spec / governing surface | Verification |
| --- | --- |
| WI-3362 re-scoped scope (traceability backfill of related_bridge_threads for WI-3337..WI-3345) | After the backfill, a MemBase read of each of WI-3337..WI-3345 confirms related_bridge_threads is populated with the verified thread slug; WI-3346..WI-3349 remain empty as recorded. |
| Reconciler contract (scripts/bridge_verified_backlog_reconciler.py) | parse_related_bridge_threads applied to each backfilled value returns the expected slug; the value is a well-formed JSON list of slug strings. The post-implementation report records, per work item, whether the thread is currently INDEX-recognized or traceability-only. |
| Evidence-verified linkage (gtkb-bridge-verified-backlog-retirement-006 NO-GO) | For each written link, the post-implementation report records that the bridge thread chain carries the work item ID, satisfying the parent-evidence standard. |
| GOV-STANDING-BACKLOG-001 (no lifecycle change) | A before/after comparison confirms each work item's stage, resolution_status, and status are unchanged; only related_bridge_threads changed. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping, the exact MemBase read commands, and the observed before/after values per work item. |

The backfill is a MemBase metadata mutation, not a code change; per the file-bridge protocol a test may be a logical assertion (the field is populated / equals the expected value / lifecycle fields unchanged). Verification is by MemBase read-back, plus python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill and python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill.

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] Each proposed work-item-to-thread link is evidence-verified (the bridge thread chain carries the work item ID) before it is written.
- [ ] WI-3337 through WI-3345 each have related_bridge_threads populated with the verified thread slug as a well-formed JSON list.
- [ ] WI-3346 through WI-3349 remain unlinked (no thread yet) and are recorded as deferred.
- [ ] No work item's lifecycle fields (stage, resolution_status, status) change.
- [ ] The post-implementation report records, per work item, whether the linked thread is currently INDEX-recognized (reconciler can act on VERIFIED) or traceability-only (INDEX-pruned), with no claim of automatic closure for the traceability-only set.
- [ ] Loyal Opposition returns VERIFIED before the backfill is treated as complete.

## Pre-Filing Preflight Subsection

The applicability preflight and the ADR/DCL clause preflight are run against this -003 draft via --content-file before the REVISED INDEX entry is inserted, and re-run against the indexed operative file after filing. Observed results are recorded in the Applicability Preflight and Clause Applicability sections below.

## Applicability Preflight

The applicability preflight was run against this -003 draft via `--content-file` prior to the REVISED INDEX entry:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill --content-file bridge/gtkb-antigravity-related-bridge-threads-backfill-003.md`

- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
- packet_hash: sha256:ed310e8ac3115d97a84ef56c143c7283d801bcb8e5337fd0163a56e2b91803e1

All applicable required and advisory cross-cutting specs are cited in this proposal's Specification Links.

## Clause Applicability

The ADR/DCL clause preflight was run against this -003 draft via `--content-file` prior to the REVISED INDEX entry:

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-antigravity-related-bridge-threads-backfill --content-file bridge/gtkb-antigravity-related-bridge-threads-backfill-003.md`

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

GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS evaluates must_apply with evidence found: the Clause Scope Clarification documents this as a metadata-linkage backfill with no lifecycle-state change, and the per-work-item inventory, Loyal Opposition review, and owner authorization satisfy the clause's visibility controls.

## Risk And Rollback

- R1 (medium): a proposed work-item-to-thread link is wrong (a title-inference mapping points at the wrong thread). Mitigation: the implementation phase evidence-verifies each link against the on-disk bridge thread chain before writing it; a link that fails verification is corrected or withheld.
- R2 (low): the backfill format does not match what the reconciler expects. Mitigation: the value is a JSON list of bridge document slugs, matching parse_related_bridge_threads.
- R3 (low): a reader treats the traceability-only links as a promise of automatic closure. Mitigation: -003 removes the automatic-resolution claim; the mapping table and acceptance criteria state per work item whether the thread is reconciler-recognized or traceability-only; Deferred Work explicitly carves out closure of INDEX-pruned threads.
- R4 (very low): the backfill is mistaken for a lifecycle bulk operation. Mitigation: no lifecycle field is touched; the Clause Scope Clarification and the no-lifecycle-change acceptance criterion make the metadata-only nature explicit and checkable.

Rollback: append-only versioning keeps the prior (empty-field) work-item versions retrievable; a corrective new version restores the prior state if a link is later found wrong. No file is modified, so there is no on-disk residue.

## Loyal Opposition Asks

1. Confirm the re-scope to a traceability-only metadata backfill (path b of the -002 NO-GO) closes finding F1, and that deferring automatic closure of the six INDEX-pruned threads to a separate governed slice is the correct disposition.
2. Confirm the refreshed status notes (F2) match live bridge/INDEX.md.
3. Confirm the proposed work-item-to-thread mapping is sound as traceability, with implementation-phase evidence verification against the on-disk thread chains as the gate before each write.
4. Confirm that backfilling a linkage metadata field on nine work items, with no lifecycle-state change, is correctly treated as a metadata backfill rather than a GOV-STANDING-BACKLOG-001 lifecycle bulk operation.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
