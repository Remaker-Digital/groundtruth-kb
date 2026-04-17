NO-GO

# Loyal Opposition Review: GT-KB ADR Three-Tier Memory Architecture

Reviewed document: `bridge/gtkb-adr-memory-architecture-001.md`
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Verdict: NO-GO until the insertion plan and factual inventory are corrected.

## Summary

The three-tier concept is directionally sound: MemBase as authoritative,
Deliberation Archive as evidentiary, and MEMORY.md as operational/provisional
is consistent with current GT-KB code and docs. The proposal should not be
inserted into MemBase as written because it contains executable API mismatches,
stale file-path claims, and unverified numeric/file inventory claims that would
become authoritative once recorded as an ADR.

## Prior Deliberations

No prior deliberations found for three-tier memory architecture in the inspected
`groundtruth-kb` checkout.

Evidence:
- Command: `python -m groundtruth_kb deliberations search "three-tier memory architecture" --limit 5 --json`
- Result: `[]`
- Command: `python -m groundtruth_kb deliberations search "MEMORY.md MemBase Deliberation Archive" --limit 5 --json`
- Result: `[]`

The proposal cites S297/S282 conversations, but this review could not verify
those as DELIB records in the target checkout.

## Findings

### 1. Blocker: proposed MemBase insertion code cannot run against KnowledgeDB

Claim:
The proposal says the ADR can be inserted with `db.insert_spec(...,
rationale="<contents...>", source_paths=[...])`, and that post-implementation
evidence should call `db.get_spec(id='ADR-NNNN', version=1)`.

Evidence:
- Proposal insertion snippet: `bridge/gtkb-adr-memory-architecture-001.md:276`
  through `bridge/gtkb-adr-memory-architecture-001.md:288`
- Proposal post-implementation check: `bridge/gtkb-adr-memory-architecture-001.md:295`
  through `bridge/gtkb-adr-memory-architecture-001.md:297`
- Actual `KnowledgeDB.insert_spec` signature has `description`, `priority`,
  `scope`, `section`, `handle`, `tags`, `assertions`, `type`, enriched fields,
  and `source_paths`; it does not define `rationale`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:709`
- Actual `KnowledgeDB.get_spec` accepts only `spec_id`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:1021`
- Smoke command in a temp DB:
  `KnowledgeDB.insert_spec(..., rationale="context and alternatives", ...)`
  returned `TypeError KnowledgeDB.insert_spec() got an unexpected keyword argument 'rationale'`.
- Smoke command in a temp DB:
  `db.get_spec(id='ADR-0001', version=1)` returned
  `TypeError KnowledgeDB.get_spec() got an unexpected keyword argument 'id'`.

Risk/impact:
Prime would get a runtime failure during insertion, or worse, revise ad hoc
during implementation and leave the authoritative ADR with an unreviewed storage
mapping. The exit criteria also ask for a field round-trip that the schema does
not support.

Required action:
Revise the artifact insertion plan to match the current API. At minimum:
- Remove the nonexistent `rationale=` argument.
- Specify where Context, Decision, Alternatives, Consequences, and source links
  are stored in existing fields.
- Use `db.get_spec("ADR-NNNN")` for latest-version readback and
  `db.get_spec_history("ADR-NNNN")` if version-specific evidence is required.
- Keep `list_specs(type="architecture_decision")`; that filter is supported at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:1038`.

### 2. Blocker: ADR context cites stale or contradictory file paths

Claim:
The proposal says the canonical spec store is accessed via
`tools/knowledge-db/db.py`, operational notes live at `memory/MEMORY.md`, and
Agent Red currently has `memory/MEMORY.md`, `memory/feedback_*.md`, and
`memory/project_*.md` inventories.

Evidence:
- Proposal path claims: `bridge/gtkb-adr-memory-architecture-001.md:32`
  through `bridge/gtkb-adr-memory-architecture-001.md:43`
- Proposal Agent Red migration claims:
  `bridge/gtkb-adr-memory-architecture-001.md:255` through
  `bridge/gtkb-adr-memory-architecture-001.md:260`
- Actual DB implementation is
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py`.
- `groundtruth-kb` project scaffolding copies root `MEMORY.md`, not
  `memory/MEMORY.md`: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:162`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:168`
  and reports root `CLAUDE.md, MEMORY.md` in created files at
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:820`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:824`.
- `templates/MEMORY.md` already says canonical project knowledge lives in the
  knowledge database and this file is operational memory:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\MEMORY.md:30`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\MEMORY.md:33`.
- Agent Red current `memory/` inventory from `Get-ChildItem -Recurse -File memory`:
  `memory\s133-live-test-migration.md` (4925 bytes),
  `memory\testing-research.md` (12742 bytes), and
  `memory\work_list.md` (15711 bytes).
- `rg --files -g 'MEMORY.md'` in Agent Red returned no matches.
- `rg --files -g 'feedback_*.md' -g 'project_*.md'` in Agent Red returned no matches.

Risk/impact:
The ADR would make a path convention authoritative while the current scaffold
and current Agent Red checkout use different paths. Downstream docs, doctor
checks, and migration bridges could be built against a false inventory.

Required action:
Resolve and state the canonical adopter path before approval:
- Either revise the ADR to use root `MEMORY.md`, matching current scaffold, or
  explicitly include the scaffold/docs change required to move to
  `memory/MEMORY.md`.
- Replace the Agent Red migration section with the verified current inventory,
  or remove Agent Red migration claims from this ADR and handle them in a
  separate migration bridge after a fresh inventory.
- Replace `tools/knowledge-db/db.py` with `src/groundtruth_kb/db.py`.

### 3. High: numeric Deliberation Archive evidence is not verified in target checkout

Claim:
The proposal says the Deliberation Archive is ChromaDB-backed with 6990 chunks
as of S282.

Evidence:
- Proposal claim: `bridge/gtkb-adr-memory-architecture-001.md:36` through
  `bridge/gtkb-adr-memory-architecture-001.md:39`
- Direct SQLite count of target `groundtruth.db`: `deliberations 0`.
- Direct Chroma SQLite count of target `.groundtruth-chroma\chroma.sqlite3`:
  `collections 1`, `segments 2`, `embeddings 0`, `embedding_metadata 0`.
- The code does support Chroma-backed deliberation indexing:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4448`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4466`,
  and search fallback:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4595`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4668`.

Risk/impact:
The architectural statement "DA exists and is ChromaDB-backed" is valid, but
the specific 6990-chunk claim is not supported by the inspected target repo. An
ADR should not preserve stale runtime metrics without a cited source.

Required action:
Remove the chunk count, or cite the exact database/export/DELIB source where
S282's 6990 chunks were measured. Treat runtime counts as evidence in a report,
not as durable architecture text, unless they are clearly historical context.

### 4. Medium: DCL enablement is right to defer, but the proposed DCL wording needs tighter scope

Claim:
The ADR enables future DCLs including "DCL-DA-APPEND-ONLY: deliberation table
inserts only; no UPDATE or DELETE (already true)."

Evidence:
- Proposal DCL list: `bridge/gtkb-adr-memory-architecture-001.md:241` through
  `bridge/gtkb-adr-memory-architecture-001.md:253`
- Deliberation writes use `INSERT INTO deliberations`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4263`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4294`.
- Chroma indexing legitimately deletes stale vector chunks before re-indexing:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4567`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4571`,
  and `rebuild_deliberation_index()` deletes/recreates the Chroma collection:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4670`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4688`.

Risk/impact:
A broad "no DELETE" DCL would incorrectly flag valid Chroma maintenance code.
The invariant should be about canonical SQLite `deliberations` rows, not all
DA-related storage.

Required action:
Keep the four DCLs deferred to separate bridges. When drafting
DCL-DA-APPEND-ONLY, scope assertions to canonical SQLite `deliberations` table
mutation, and explicitly allow Chroma index deletion/rebuild because the index
is rebuildable from SQLite.

### 5. Medium: peer taxonomy is underspecified relative to the proposal's own consequences

Claim:
The ADR names four peer categories: `gt-kb-state.md`, `gt-sessions.md`,
`gt-feedback/*.md`, and `gt-strategy/*.md`.

Evidence:
- Peer taxonomy section: `bridge/gtkb-adr-memory-architecture-001.md:139`
  through `bridge/gtkb-adr-memory-architecture-001.md:155`
- Later consequences introduce additional files outside those four categories:
  `memory/gt-phase-a-metrics.md` and `memory/gt-scanner-deny.log` at
  `bridge/gtkb-adr-memory-architecture-001.md:226` through
  `bridge/gtkb-adr-memory-architecture-001.md:230`.

Risk/impact:
If the taxonomy is meant to be closed, the consequences violate it. If it is
extensible, the ADR does not define the extension rule. That ambiguity will
surface immediately in docs and doctor checks.

Required action:
Revise peer taxonomy to be explicitly extensible or add categories such as
`gt-metrics/`, `gt-logs/`, and `gt-handoff.md`. If logs belong outside memory,
say so now and move `gt-scanner-deny.log` out of the ADR consequences.

## Responses to Prime Review Targets

1. Naming:
   Conditionally acceptable. "MemBase / Deliberation Archive / MEMORY.md" is
   workable for adopters, but the ADR must distinguish the label from the exact
   storage path because current scaffold uses root `MEMORY.md` while the
   proposal standardizes `memory/MEMORY.md`.

2. Promotion rule completeness:
   Mostly complete. Add an explicit "expires/discarded without promotion" path
   for scratch notes that never become evidence, truth, bridge work, or docs.
   Also describe projection regeneration separately from promotion, since
   `gt-*` peer files are derived views.

3. Peer taxonomy specifics:
   Not yet sufficient. The four categories are good anchors, but the proposal
   itself adds metrics and deny-log files. Either include those categories or
   define a naming extension rule.

4. DCL enablement:
   Defer all four DCLs to separate bridges. Do not make them directly binding
   in this ADR until assertions and allowed exceptions are reviewed.

5. Agent Red migration:
   Do not include the migration claims as written. Current Agent Red inventory
   does not match the proposal. Use a separate migration bridge after verified
   file inventory and owner path decision.

## Required Conditions For GO

1. Correct the MemBase insertion code and post-implementation evidence to match
   `KnowledgeDB` exactly.
2. Resolve the canonical MEMORY path question: root `MEMORY.md` vs
   `memory/MEMORY.md`.
3. Replace stale path and file inventory claims with verified evidence.
4. Remove or source the 6990 Chroma chunk count.
5. Clarify whether the peer taxonomy is closed or extensible, and reconcile
   metrics/log files.
6. Keep future DCLs deferred and scoped narrowly enough to avoid false positives
   against Chroma index maintenance.

## Owner Decision Needed

Mike should decide whether adopter projects should keep root `MEMORY.md` as
the operational notepad, matching current scaffold, or migrate to
`memory/MEMORY.md` with scaffold/docs changes. That decision affects the ADR,
doctor checks, templates, and any Agent Red migration bridge.
