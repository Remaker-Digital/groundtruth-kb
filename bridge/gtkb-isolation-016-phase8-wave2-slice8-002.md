NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 8

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md`
Scope: MemBase export rehearsal lane proposal for `scripts/rehearse/_membase_export.py`

## Claim

Slice 8 is not ready to implement. The proposal's sparse, current-record `KnowledgeDB.list_*()` manifest is not sufficient to drive the Phase 8 cutover requirement to preserve versioned MemBase history.

## Evidence

- The proposal says the lane produces a partition manifest of every artifact in live `groundtruth.db`, with full content left in the database for selective SQL extraction at cutover: `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md:33`.
- The source strategy is current API enumeration via `KnowledgeDB.list_*()` methods: `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md:39` to `:54`.
- The manifest schema is explicitly sparse: `{id, type, classification, classification_signal}` only, with no content and no version/table row identity: `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md:93`, `:115`, `:141` to `:173`.
- The proposal says cutover will consume `partition_manifest.json` to drive selective SQL extraction: `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md:247` to `:248`.
- The Phase 8 rehearsal plan requires MemBase Specs/Work Items to be split by scoped SQL export and requires append-only versioning to be preserved without renumbering: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:302` to `:310`.

## Risk / Impact

A manifest of only current logical records can classify the latest visible artifact, but it cannot prove that all historical rows needed by `UNIQUE(id, version)` are selected, preserved, and reinserted correctly. Using it as the cutover driver risks silent history loss or version drift in the app-local database.

## Required Revision

- Add explicit version-preservation design before implementation.
- Either query the versioned base tables directly during this lane, or include enough stable SQL extraction keys in the manifest to identify every source table, record id, version, and related row needed at cutover.
- Add tests that fail when older versions for a classified artifact are omitted.
- Clarify whether high-volume assertion run rows are deliberately out of scope and cite the governing plan basis, or include a latest-run/versioned-row policy that does not conflict with cutover preservation requirements.

## Decision Needed From Owner

None at this point. Prime needs to revise the proposal so the manifest can support the documented cutover semantics.
