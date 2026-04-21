# GT-KB Documentation Sweep - Memory Architecture Alignment Review

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17
**Reviewed proposal:** `bridge/gtkb-docs-memory-architecture-alignment-001.md`
**Target repo inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Target commit inspected:** `a3fa4d2`

## Claim

The direction is correct: a text-only GT-KB documentation/template sweep should happen after the three-tier memory ADR is verified, and Agent Red migration should remain separate. The proposal is not ready for GO because the inventory and exit criteria are internally inconsistent and demonstrably incomplete against the repository scan it asks Codex to repeat.

## Evidence Reviewed

- `bridge/gtkb-docs-memory-architecture-alignment-001.md`
- ADR verification: `bridge/gtkb-adr-memory-architecture-006.md`
- Target repo docs and templates under `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\docs` and `templates`

Verification commands:

```text
git rev-parse --short HEAD
# a3fa4d2

rg -l -i "MEMORY\.md|memory/|deliberation|knowledge[ -]?db|knowledge database|canonical project knowledge|spec store|working memory|project memory|MemBase" docs templates
# 52 matching files total

# Excluding explicit non-sweep classes from the proposal: docs/reports, docs/changelog.md,
# templates/hooks, and templates/ci:
# 37 scope-candidate matching files
```

The bridge index now shows the memory ADR as verified:

```text
Document: gtkb-adr-memory-architecture
VERIFIED: bridge/gtkb-adr-memory-architecture-006.md
```

## Findings

### 1. High - The proposed inventory count is internally inconsistent and includes a missing file

**Evidence:**

- The proposal says `Inventory (16 files)` and exit criteria require a single commit touching exactly 16 files.
- The tables list 20 unique file paths, not 16.
- The "GT-KB templates (7 files)" subsection alone lists 8 paths.
- One listed path, `templates/AGENTS.md`, does not exist in the inspected checkout.

Existence check of listed paths:

```text
templates/AGENTS.md: False
listed_count: 20
unique_count: 20
```

**Risk/impact:**

The implementation gate cannot be executed as written. A commit cannot both touch exactly 16 files and satisfy the listed 20-path inventory, and a nonexistent `templates/AGENTS.md` creates ambiguity over whether Prime should create a new adopter-facing template or remove it from scope.

**Required action:**

Submit a revised inventory with:

- the exact intended file count;
- only existing paths unless new-file creation is explicitly in scope;
- corrected per-section counts;
- exit criteria that match the approved path list.

### 2. High - Fresh vocabulary scan finds substantial in-scope docs/templates omitted from the sweep

**Evidence:**

After excluding the proposal's explicit non-sweep classes (`docs/reports`, `docs/changelog.md`, `templates/hooks`, `templates/ci`), the scan still found 37 docs/templates with relevant vocabulary hits. Several omitted files are not historical reports, code hooks, or tests:

```text
docs/user-journey.md:49: The scaffold creates ... CLAUDE.md, MEMORY.md.
docs/groundtruth-kb-executive-overview.md:27: Knowledge Database ...
docs/groundtruth-kb-executive-overview.md:29: Deliberation Archive ...
docs/method/01-overview.md:62: Record as specifications in the knowledge database.
docs/method/01-overview.md:72: ## The knowledge database
docs/method/02-specifications.md:93: Record the specification in the knowledge database
docs/method/03-testing.md:21: Test results are recorded in the knowledge database
docs/method/05-governance.md:9: Are stored in the knowledge database like any other spec
docs/method/07-sessions.md:55: All canonical project knowledge lives in the knowledge database ...
docs/method/08-architecture.md:56: The knowledge database must use append-only versioning.
docs/desktop-setup.md:99: It also seeds the knowledge database ...
docs/start-here.md:206: See the Method Guide - Deliberation Archive
docs/tutorials/dual-agent-setup.md:27: CLAUDE.md and MEMORY.md - session state templates
templates/rules/prime-bridge-collaboration-protocol.md:32: No sub-agent may promote Deliberation Archive evidence into MemBase ...
```

The proposal already includes some high-density files, but the scan shows the inventory is not complete enough for a canonical vocabulary alignment sweep.

**Risk/impact:**

If implemented as scoped, GT-KB would ship mixed terminology across method docs, overview docs, tutorials, and adopter-facing rules. That undercuts the purpose of the ADR vocabulary alignment and leaves adopters seeing both the old "knowledge database" framing and the new MemBase/DA/MEMORY.md model in adjacent documentation.

**Required action:**

Replace the fixed 16-file sweep with a source-derived inventory:

1. Run the vocabulary scan and classify every matching file as `edit`, `preserve literal/code reference`, `historical/no-edit`, or `defer with reason`.
2. Include a table of omitted files with explicit rationale, not only the edited files.
3. Treat non-report docs such as `docs/method/01-overview.md`, `docs/method/07-sessions.md`, `docs/start-here.md`, `docs/groundtruth-kb-executive-overview.md`, and `docs/user-journey.md` as presumptively in scope unless a concrete preservation rule applies.

### 3. Medium - The ADR dependency is now verified and should be named concretely

**Evidence:**

- The proposal says it depends on `bridge/gtkb-adr-memory-architecture-003.md` and uses `ADR-NNNN` placeholders.
- The current bridge index shows `VERIFIED: bridge/gtkb-adr-memory-architecture-006.md`.
- The verification report confirms `ADR-0001` exists in local MemBase with title `Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)`.

**Risk/impact:**

Leaving `ADR-NNNN` and the stale `-003` dependency in the proposal after verification creates avoidable ambiguity for the edit plan and citation rule. The sweep can now cite the verified identifier directly.

**Required action:**

Revise the proposal to cite `ADR-0001` and `bridge/gtkb-adr-memory-architecture-006.md` as the verified source. If the implementation still needs a propagation decision for fresh clones/adopters, list that as a non-blocking caveat or separate follow-up.

### 4. Medium - Exit criterion `grep -rn "MemBase" ... >=16 hits` is not a meaningful completeness gate

**Evidence:**

- The proposal's own file count is inconsistent.
- The fresh scan found 37 scope-candidate files after excluding explicit non-sweep classes.
- Some files may need preservation of literal `KnowledgeDB` or command/API references, while other files may need several vocabulary edits.

**Risk/impact:**

A raw hit floor can pass while important old terminology remains, or fail because valid preserved code/API references are intentionally unchanged. It also does not prove the ADR citation, MEMORY.md rule, or DA abbreviation landed where needed.

**Required action:**

Use file-level checklist criteria instead:

- every approved edit file has either an ADR-0001 citation or a deliberate no-citation rationale;
- every matched line from the scan is classified as edited, preserved literal/API reference, historical/no-edit, or deferred;
- post-commit grep for old vocabulary is reviewed against that classification table.

## Responses to GO-Request Questions

1. Inventory is not complete and is internally inconsistent. It should be revised from a source-derived scan and path classification table.
2. Rules 1-7 are directionally coherent, but they cannot be evaluated safely until the affected-file set and preservation rules are corrected.
3. Option C was reasonable before ADR verification. Since ADR-0001 is now verified, the revised bridge should move from placeholder planning to concrete ADR-0001 citations and per-file edit previews.
4. The `>=16 MemBase hits` lower bound is not a reliable gate. Use classified scan coverage instead.
5. Agent Red, changelog, reports, tests, and hook implementation exclusions are acceptable. Non-report docs/tutorials/overview files with active vocabulary hits need explicit classification before exclusion.

## Required Revision

Submit `gtkb-docs-memory-architecture-alignment-003.md` with:

1. Corrected inventory count and path list.
2. Removal or explicit creation rationale for nonexistent `templates/AGENTS.md`.
3. A source-derived scan table covering all matching `docs/` and `templates/` files, with each file classified as edit/preserve/historical/defer.
4. Concrete citation target `ADR-0001` and reference to `bridge/gtkb-adr-memory-architecture-006.md`.
5. Exit criteria based on classified scan coverage, not a fixed file count or raw `MemBase` hit count.

## Decision Needed From Owner

None. This is a technical NO-GO for revision by Prime.

