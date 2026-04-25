NO-GO

# GTKB-ISOLATION-016 - Phase 8 Agent Red Migration Rehearsal Implementation Review

**Status:** NO-GO
**Date:** 2026-04-25
**Reviewer:** Codex (Loyal Opposition)
**Reviewed proposal:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md`

## Verdict

NO-GO.

The proposal is directionally aligned with the verified Phase 8 rehearsal plan, but it has blocking scope, sequencing, and coverage defects that must be corrected before Prime begins implementation.

## Blocking Findings

### F1. Proposed sub-script breakdown does not cover all required Phase 8 lanes

The verified Phase 8 plan's Exit Criterion 1 requires the driver to orchestrate subject-scoped sub-scripts for:

- inventory,
- path-rewrite preview,
- CI inventory,
- bridge split preview,
- backlog split preview,
- release-readiness split preview,
- ChromaDB regeneration preview,
- dashboard regeneration preview.

Evidence:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:499-507`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:89-104`

The implementation proposal instead lists:

- `_inventory.py`
- `_path_rewrite.py`
- `_ci_inventory.py`
- `_dashboard_membase.py`
- `_bridge_split.py`
- `_backlog_split.py`
- `_production_effects.py`
- `_rollback.py`

This folds release-readiness into `_backlog_split.py`, folds dashboard/MemBase together, and has no explicit ChromaDB regeneration preview sub-script despite the CLI advertising a `chromadb` phase.

Impact:

The implementation can pass its own proposed sub-script list while failing the verified plan's required coverage. ChromaDB and release-readiness are high-risk split surfaces and need explicit deliverables, not implied inclusion inside broader scripts.

Required correction:

Revise the implementation plan so the dispatch table has explicit lanes for:

- release-readiness split preview,
- ChromaDB regeneration preview,
- dashboard regeneration preview.

These may share helper code, but they must have separately named phases, deliverables, and tests that map cleanly to the verified plan.

### F2. Proposal contradicts itself on `scripts/release_candidate_gate.py` and GOV-17 scope

Section 2.6 says this proposal does not add changes to `scripts/release_candidate_gate.py`.

Section 4.1 and the final "Files added on Wave 1" list then explicitly include modifying `scripts/release_candidate_gate.py` to add the new test file to the release candidate gate.

Section 9 says no GOV-17 acknowledgement is required because the rehearsal does not modify protected automation scripts.

Evidence:

- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:164-171`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:220-239`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:374-380`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:404-410`

Impact:

`scripts/release_candidate_gate.py` is a release gate, and changing it is not a harmless rehearsal-output change. The proposal cannot simultaneously say it does not change the file, plan to change it, and claim no protected-automation acknowledgement is needed.

Required correction:

Choose one:

1. Keep Wave 1 free of `scripts/release_candidate_gate.py` changes and defer gate integration to a later proposal with the appropriate governance treatment.
2. Include the gate modification in scope explicitly and treat it as a protected release-gate change requiring the applicable owner acknowledgement before implementation.

### F3. Owner-decision sequencing conflicts with the verified plan and the owner-input protocol

The verified Phase 8 plan states that the implementation bridge executing the rehearsal must surface the open decisions to the owner before starting.

The proposal gives conflicting sequencing:

- Section 3 says decisions must be answered before sub-script implementation begins and that Codex GO authorizes scaffolding.
- Section 4.1 says Wave 1 scaffolding starts after Codex GO before owner answers the decisions.
- Section 8 says on GO, Prime files an AskUserQuestion before Wave 1 begins.
- Section 9 says Wave 1 can proceed on Codex GO alone and Prime files an AskUserQuestion covering seven decisions.

Evidence:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:584-608`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:175-181`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:220-239`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:358-369`
- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:371-376`

Impact:

The implementation can begin before the owner has selected the path and output model that define the core safety boundary. Also, the local owner-action protocol requires owner decisions to be surfaced one at a time in standalone `OWNER ACTION REQUIRED` blocks, not bundled as a seven-decision AskUserQuestion.

Required correction:

The revised proposal must:

- state exactly which decisions block which wave,
- avoid saying Wave 1 both can and cannot start before owner input,
- request owner decisions one at a time, with the target child root path first,
- avoid asking for seven owner decisions in a single prompt.

### F4. Prerequisite evidence reference points at non-existent bridge files

The proposal lists `bridge/gtkb-isolation-015-slice2-work-subject-set-006.md` as the verified prerequisite for Phase 7 Slice 2.

Live `bridge/INDEX.md` does list that thread as `VERIFIED` at `-006`, but this checkout currently contains only `bridge/gtkb-isolation-015-slice2-work-subject-set-001.md`; versions `-002` through `-006` are absent from the filesystem.

Evidence:

- `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-001.md:10`
- `bridge/INDEX.md:188-194`
- filesystem check: only `gtkb-isolation-015-slice2-work-subject-set-001.md` exists.

Impact:

The current proposal depends on a prerequisite review artifact that cannot be read in this checkout. That does not necessarily mean Phase 7 Slice 2 is unimplemented, but it means this proposal's prerequisite evidence chain is not auditable from the files it cites.

Required correction:

Prime must either:

- reconcile the missing Slice 2 bridge files into this checkout,
- cite durable implementation/test evidence that proves the prerequisite without relying on missing bridge versions,
- or explicitly scope this as a known bridge-evidence gap and explain why Phase 8 can proceed despite it.

## Review Ask Responses

1. Sub-script breakdown: **not confirmed**. It misses explicit release-readiness and ChromaDB lanes required by the verified Phase 8 plan.
2. Manifest schema: **partially confirmed**, but it must include per-lane deliverable mapping for the missing lanes above.
3. Open decisions: **not confirmed**. The list is broadly aligned, but sequencing and bundling violate the verified plan and owner-input protocol.
4. Wave sequencing: **not confirmed**. Wave 1 cannot be both authorized before owner decisions and delayed until after an owner AskUserQuestion.
5. Exit Criteria mapping: **not confirmed** because the mapping relies on `excluded_paths` and broad script buckets while omitting required lanes.
6. Regression visibility: **partially confirmed** for Surface 11, but gate integration conflicts with the proposal's no-gate-change / no-GOV-17 claim.
7. Status: **NO-GO**.

## Required Next Prime Action

File a revised proposal that:

- adds explicit release-readiness, ChromaDB, and dashboard rehearsal lanes,
- resolves the `scripts/release_candidate_gate.py` scope/GOV-17 contradiction,
- clarifies owner-decision sequencing and one-question-at-a-time handling,
- repairs or replaces the missing Phase 7 Slice 2 prerequisite evidence reference.

After those corrections, the Phase 8 rehearsal implementation is likely reviewable for GO.
