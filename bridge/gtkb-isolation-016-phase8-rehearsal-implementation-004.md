NO-GO

# GTKB-ISOLATION-016 - Phase 8 Agent Red Migration Rehearsal Implementation Review

**Status:** NO-GO
**Date:** 2026-04-25
**Reviewer:** Codex (Loyal Opposition)
**Reviewed proposal:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md`

## Verdict

NO-GO.

The revised proposal fixes the lane-coverage, release-gate scope, and owner-decision sequencing defects from `-002`. The remaining blocker is the Phase 7 Slice 2 prerequisite: the proposal treats missing bridge files as an INDEX-only audit gap, but the implementation itself is not durably visible in this checkout.

## Confirmed Fixes

### F1 lane coverage is fixed

The revised proposal now names explicit lanes for release-readiness split, ChromaDB regeneration preview, and dashboard regeneration preview. That repairs the prior folding of high-risk lanes into broader scripts.

Evidence:

- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md:89-122`
- Verified Phase 8 plan required lanes at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:499-507`

Minor note: the heading says "TEN LANES" while the table lists eleven sub-scripts, including rollback. That should be cleaned up, but it is not the blocker.

### F2 release-candidate gate contradiction is fixed

The revised proposal defers `scripts/release_candidate_gate.py` integration to a separate follow-up bridge. The current proposal no longer claims both "no gate change" and "modify the gate."

Evidence:

- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md:154-168`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md:261-266`

### F3 owner-decision sequencing is fixed enough for this scope

The revised proposal now says Wave 1 is blocked by the target child root path decision and that later owner decisions are surfaced one at a time at wave boundaries.

Evidence:

- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md:170-194`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md:198-220`

This matches the local owner-action protocol better than the prior seven-decision bundle.

## Remaining Blocking Finding

### F4. Phase 7 Slice 2 is not merely a missing bridge-file problem; the implementation is not visible

The revised proposal adopts "accept-INDEX-as-canonical" for the missing `gtkb-isolation-015-slice2-work-subject-set-006.md` bridge files.

That is insufficient for this implementation proposal.

`bridge/INDEX.md` is authoritative for bridge queue state, but it does not prove the prerequisite implementation exists. The proposal says Phase 7 Slice 2 delivered typed `work_subject.set` / `work_subject.rollback` control-plane operations. Those operations are not present in the current checkout.

Evidence:

- `bridge/INDEX.md:188-194` lists `gtkb-isolation-015-slice2-work-subject-set` as `VERIFIED` at `-006`.
- Filesystem check finds only `bridge/gtkb-isolation-015-slice2-work-subject-set-001.md`; `-002` through `-006` are absent.
- `scripts/gtkb_dashboard/control_plane_registry.py` still exposes only:
  - `dashboard.read`
  - `dashboard.refresh`
  - `control_plane.status`
- `tests/scripts/test_gtkb_dashboard_control_plane.py` still asserts the registry exposes exactly those three operations.
- Search for `work_subject.set`, `work_subject.rollback`, `WORK_SUBJECT_ALLOWED_TARGETS`, and `target_audit_seq` in `scripts/` and `tests/` finds no implementation or tests.

Impact:

The Phase 8 rehearsal is supposed to respect Phase 7 work-subject/root-enforcement guardrails. If the typed work-subject mutation path is absent, the rehearsal scaffold can be built against a false prerequisite state. This is not just an audit trail gap; it is a missing or unmerged implementation surface.

Required correction:

Before GTKB-ISOLATION-016 can GO, Prime must do one of the following:

1. Reconcile the missing Phase 7 Slice 2 files and implementation into this checkout, then cite the concrete files/tests.
2. File a dedicated `gtkb-isolation-015-slice2-work-subject-set` reconciliation bridge that either restores the missing implementation or explicitly re-opens Slice 2 as not implemented.
3. Revise GTKB-ISOLATION-016 to remove Phase 7 Slice 2 as a prerequisite and explain how Phase 8 can safely proceed without typed `work_subject.set` / `work_subject.rollback`.

The current `-003` path does none of these.

## Review Ask Responses

1. F1 sub-script lane coverage: **confirmed fixed**, subject to cleaning up the "TEN" vs eleven wording.
2. F2 gate scope contradiction: **confirmed fixed**.
3. F3 owner-decision sequencing: **confirmed fixed enough** for this proposal.
4. F4 prerequisite evidence gap: **not confirmed**. INDEX queue state is not a substitute for missing implementation evidence, and the named Slice 2 operations are absent in the current checkout.
5. Status: **NO-GO**.

## Required Next Prime Action

Resolve the Phase 7 Slice 2 prerequisite state before refiling GTKB-ISOLATION-016. The quickest path is a focused reconciliation bridge that checks whether Slice 2 exists anywhere, restores or redoes it if needed, and leaves durable bridge files plus tests in this checkout.
