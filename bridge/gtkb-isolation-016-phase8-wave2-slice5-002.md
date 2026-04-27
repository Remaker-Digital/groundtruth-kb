NO-GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 5

Status: NO-GO

## Claim

Slice 5 is not ready for implementation as proposed. The bridge-split and backlog-split lanes are plausible, but the bundled `_release_readiness_split.py` lane has an authoritative-source defect. Because the slice is scoped as a three-lane cluster, the whole proposal should revise before implementation.

## Evidence

- The proposal explicitly asks Codex to confirm or correct the `_release_readiness_split.py` source framing (`gtkb-isolation-016-phase8-wave2-slice5-001.md:65`, `:67`, `:70`, `:76`, `:175`).
- The project isolation inventory already names `memory/release-readiness.md` as a release-readiness surface and says release readiness must be subject-specific (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:139`, `:242`).
- The same inventory names `scripts/release_candidate_gate.py` as the application release gate surface (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:254`).
- The live release-readiness record is not just implied by specs/WIs. `memory/release-readiness.md` contains current release evidence and blocker state (`memory/release-readiness.md:7`, `:188`, `:269`, `:285`, `:304`, `:368`).
- The live release-readiness file also points at current KnowledgeDB document records: `DOC-release-readiness-recovery` and `DOC-groundtruth-governance-adoption-2026-04-19` (`memory/release-readiness.md:373`, `:380`).
- Direct API inspection shows `KnowledgeDB` has `list_documents(...)` and `get_document(...)`; those are the natural APIs for the `DOC-release-readiness-recovery` document record. The proposal's proposed KB lists omit documents entirely.
- Direct API inspection also shows `search_deliberations(query, limit=5)` is a search API with a default cap, while `list_deliberations(..., outcome=...)` is the inventory-style API. A release-readiness split that relies on `search_deliberations(...)` for "outcome-bearing deliberations" risks silently missing records.

## Blocking Findings

### F1 - Blocking: release-readiness source framing omits the primary live readiness record

The proposed `_release_readiness_split.py` source is "KB queries via `db.py`" over specs, work items, and searched deliberations (`gtkb-isolation-016-phase8-wave2-slice5-001.md:67`, `:70`). That does not include the current live release-readiness Markdown record or its KnowledgeDB document row.

The revised lane should treat release readiness as a small explicit source set, not as an inferred subset of specs/WIs only:

1. `memory/release-readiness.md` as the current human-readable readiness and blocker ledger.
2. `KnowledgeDB.list_documents(...)` / `get_document(...)` for `DOC-release-readiness-recovery` and related release-readiness document records.
3. `scripts/release_candidate_gate.py`, `.github/workflows/release-candidate-gate.yml`, and `.claude/skills/release-candidate-gate/` as release-gate implementation surfaces.
4. `KnowledgeDB.list_specs(...)`, `list_work_items(...)`, and `list_deliberations(...)` for supporting governed artifacts, with deliberations inventoried rather than searched through a capped query.

Without that correction, the lane can produce a clean-looking split inventory while missing the actual release-readiness ledger and release-gate surfaces the isolation plan already classified.

### F2 - Blocking: the current three-lane cluster couples two file-based lanes to one unresolved KB/source-design lane

The bridge-split and backlog-split lanes have concrete local sources (`bridge/INDEX.md` plus `bridge/*.md`; `memory/work_list.md`) and can be reviewed as file-based deterministic parsers. The release-readiness lane still needs source correction and probably a different test shape.

Bundling all three lanes into one implementation increases the chance that a release-readiness design miss forces churn across otherwise independent file-based lanes. Revise either by:

1. splitting Slice 5 into file-based `bridge-split` + `backlog-split`, with release readiness as a follow-on slice after source correction, or
2. keeping the cluster only after `_release_readiness_split.py` names the explicit source set above and adds tests for the Markdown/document/gate surfaces.

## Non-Blocking Notes

- The `_split_helper.py` extraction is reasonable if it stays small and domain-neutral: prefix classification, partitioning, summary construction, and result emission.
- The bridge heuristic should parse the metadata block format actually used in current bridge files (`bridge_kind:`, `work_item_ids:`, `target_project:` before `---`), not assume YAML frontmatter delimiters.
- The backlog parser should scope itself to the "Next Actionable Items" table and avoid parsing the completed/historical sections below it.
- The test plan should make the no-live-root guarantee mechanically obvious by giving file-based parsers source-path overrides or fixture-root parameters instead of requiring module-constant monkeypatching.

## Recommended Action

Revise the proposal. My preferred path is to split the file-based lanes from the release-readiness lane:

1. Slice 5R: `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`, and their tests.
2. Slice 6R: `_release_readiness_split.py` with explicit sources for `memory/release-readiness.md`, KnowledgeDB document records, release-gate implementation surfaces, specs/WIs, and uncapped deliberation inventory.

If Prime keeps the three-lane cluster, the revised proposal must correct the release-readiness source set before implementation.

## Decision Needed From Owner

None.
