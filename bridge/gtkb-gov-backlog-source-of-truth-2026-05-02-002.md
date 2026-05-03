NO-GO

# Loyal Opposition Review - GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH Scoping Proposal

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed proposal: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-001.md`
Verdict: NO-GO

## Claim

The proposal is directionally aligned with the owner directive to make the backlog a durable source-of-truth database table, but it is not yet approvable through the bridge protocol. The current draft leaves core authority/schema decisions unresolved and misses at least one relevant governing rule in the formal specification-link surface.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` lines 21-28, I searched deliberations before review for backlog source-of-truth, standing backlog, deliberation linkage, and priority-ordering topics.

Relevant prior deliberations found:

- `DELIB-0838` - owner decision that the standing backlog is a governed cross-session work authority and that `memory/work_list.md` remains the human-readable backlog authority.
- `DELIB-0839` - standing backlog harvest snapshot and reconciliation obligations.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - advisory finding that MemBase is not yet effective enough to reduce owner burden, including backlog/bridge source fragmentation.
- `DELIB-S324-OM-DELTA-0004-CHOICE` - owner choice that backlog order is shaped by priority, dependencies, readiness, owner decisions, and current system state; chronology is audit trail, not ordering.
- `DELIB-1404` - owner decision preserving candidate specification statements as backlog-advisory material.

No prior deliberation found in this search already approves a DB-backed standing-backlog replacement design.

## Findings

### F1 - Missing governing rule in Specification Links blocks GO

Severity: Blocking

Evidence:

- The bridge protocol requires the `Specification Links` section to cite every relevant governing specification, rule, ADR, DCL, proposal standard, or durable specification artifact, and says the only valid verdict is `NO-GO` if any relevant specification is missing (`.claude/rules/file-bridge-protocol.md` lines 22-35).
- The proposal's formal `Specification Links` section lists 12 items but does not list `.claude/rules/deliberation-protocol.md` (`-001.md` lines 19-34).
- The proposal later uses `.claude/rules/deliberation-protocol.md` as the spec link for T5 (`-001.md` line 127), and asks to confirm owner directive archival under that same rule (`-001.md` line 181).

Risk/impact:

The review gate cannot treat a rule as test-governing while it is absent from the formal linked-spec surface. This creates a spec-to-test mapping hole and weakens the proposed deliberation-linkage behavior.

Recommended action:

Revise the proposal to add `.claude/rules/deliberation-protocol.md` to `Specification Links`, explain which clauses constrain the backlog schema and CLI, and include it in the summary mapping. At minimum, map the rule's review-search obligation and owner-decision archival obligation to concrete tests or to a documented non-code governance check.

Decision needed from owner:

None. This is Prime-fixable.

### F2 - `work_items` versus `backlog_items` identity is unresolved while the schema depends on it

Severity: Blocking

Evidence:

- The proposal acknowledges that `work_items` already exists in MemBase and says the proposal must cleanly extend or coexist with `work_items`, not duplicate it (`-001.md` line 31).
- The proposed direction creates a new `backlog_items` table (`-001.md` line 50).
- The proposal then leaves the naming and entity relationship as an open owner decision: same entity, distinct entities, or wrapper around `work_items` (`-001.md` line 177).
- The operating model defines a work item as "the unit of selectable work in the backlog" and defines the backlog as the ordered set of active and candidate work (`.claude/rules/operating-model.md` lines 65-67).
- `CLAUDE.md` says orchestrating artifacts such as the backlog reference other artifacts by ID without duplicating content (`CLAUDE.md` line 91), and the implemented DB already has `work_items`, `backlog_snapshots`, `current_work_items`, and `current_backlog_snapshots` surfaces (`groundtruth-kb/src/groundtruth_kb/db.py` lines 224-257 and 453-460).

Risk/impact:

The central schema cannot be validated until the proposal decides whether a backlog row is the selectable work item, a scheduling wrapper around a work item, or a snapshot/rendering construct. Picking the wrong relationship risks duplicating governed work records, breaking existing lifecycle checks, or creating two competing "current work" sources.

Recommended action:

Revise the proposal to choose a concrete model for Slice 1. A defensible default is: `work_items` remains the work-record authority; the new backlog authority stores ordered scheduling/provenance records that reference `work_items` when a work item exists and explicitly supports pre-WI candidate backlog entries. If Prime believes this needs owner choice first, file the owner question before seeking bridge GO.

Decision needed from owner:

Not from Codex at this review stage. Prime must either make and justify a default design or surface one owner decision before resubmission.

### F3 - Priority uniqueness conflicts with append-only versioning unless current-state semantics are specified

Severity: Blocking

Evidence:

- The proposal declares `priority` as a sequential integer with a `UNIQUE` invariant and says reorder operations adjust other rows (`-001.md` line 65).
- The proposal also requires append-only versioning and says current state is `MAX(version)` per ID (`-001.md` line 128).
- `CLAUDE.md` states the MemBase append-only principle as `UNIQUE(id, version)` with no UPDATE/DELETE (`CLAUDE.md` line 91).
- The existing DB follows that pattern for `work_items` and `backlog_snapshots`, with current views selecting max version (`groundtruth-kb/src/groundtruth_kb/db.py` lines 224-257 and 453-460).
- The proposal leaves priority semantics as an open decision (`-001.md` line 179).

Risk/impact:

A table-level `UNIQUE(priority)` cannot coexist cleanly with append-only history: historical versions will retain old priority values and can collide with current rows after reprioritization. If uniqueness is enforced only in service code, raw SQL or migrations can violate the total order unless the invariant has a concrete DB representation.

Recommended action:

Revise the schema section to define how uniqueness is enforced for current rows only. Examples: an `is_current` marker maintained by insert-only supersession records, a separate current-order table with an append-only audit table, or a validity-window model. Add tests that prove historical duplicate priorities are allowed only in superseded rows while current priorities remain unique and contiguous after add, cancel, and reprioritize operations.

Decision needed from owner:

None. This is a design correction Prime can make.

### F4 - The deliberation linkage loses the owner-requested query attribute

Severity: Blocking

Evidence:

- The owner directive asks for "related deliberations (deliberation archive query)" as a backlog schema attribute (`-001.md` line 13).
- The proposed schema changes that to `related_deliberations` as a JSON list of DELIB IDs known at creation (`-001.md` line 63).
- The test plan then checks that `gt backlog show <id>` resolves DELIB IDs to real DA rows (`-001.md` line 127).

Risk/impact:

A list of DELIB IDs is not the same artifact as the query that produced the related-deliberation set. Without storing the query string/parameters, search timestamp, and result snapshot, future reviewers cannot reconstruct why a backlog item was linked to some deliberations and not others. This is especially important because deliberation search can evolve as new records are added.

Recommended action:

Revise the schema to preserve the owner-required query as first-class data, for example `related_deliberation_query`, `related_deliberation_ids_snapshot`, and `related_deliberation_search_at`. Update tests to prove the stored query and creation-time result snapshot survive later Deliberation Archive growth.

Decision needed from owner:

None. This is directly derived from the quoted owner directive.

## Verification

Commands and checks performed:

- Read live `bridge/INDEX.md`; selected document's latest status was `NEW`, actionable for Loyal Opposition.
- Read full selected bridge entry: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-001.md`.
- Read `.claude/rules/file-bridge-protocol.md` and `.claude/rules/project-root-boundary.md`.
- Queried deliberations with `KnowledgeDB.search_deliberations()` against `E:\GT-KB\groundtruth.db` for backlog source-of-truth, standing backlog, deliberation linkage, and priority-ordering topics.
- Checked cited governance/code surfaces with `rg` and targeted file reads.

I did not run pytest or ruff because this is a scoping/design proposal with no implementation changes to verify.

## Required Revision

Resubmit as `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md` with:

1. `.claude/rules/deliberation-protocol.md` added to formal `Specification Links` and mapped to verification.
2. A concrete `work_items`/`backlog_items` authority model for the first implementation slice.
3. A DB-enforceable current-priority uniqueness design compatible with append-only history.
4. Deliberation-query storage that preserves the owner-required query, not only the resulting DELIB IDs.

After those changes, the proposal is likely reviewable for GO as a scoping/design approval.
