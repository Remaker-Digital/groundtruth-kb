NO-GO

# Loyal Opposition Review - GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH Scoping Proposal REVISED-1

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed proposal: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md`
Verdict: NO-GO

## Claim

The revision substantially improves the original proposal and resolves the prior `-002.md` findings in the main design direction. It is still not approvable because the revised proposal now cites deliberation and formal-artifact governance but does not satisfy those governance surfaces in its own proposal structure, and one proposed schema invariant is still underspecified.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched the Deliberation Archive before review for backlog source-of-truth, standing backlog, markdown backlog discipline, implementation ordering, and deliberation-query topics.

Relevant results:

- `DELIB-0838` - standing backlog is a governed cross-session work authority.
- `DELIB-0839` - standing backlog harvest snapshot and reconciliation obligations.
- `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT` - advisory finding on MemBase/backlog/bridge source fragmentation.
- `DELIB-S324-OM-DELTA-0004-CHOICE` - backlog order is shaped by priority, dependencies, readiness, owner decisions, and current system state; chronology is audit trail, not ordering.
- `DELIB-1404` - candidate specification statements backlog advisory.

No prior deliberation found in this search already approves the DB-backed backlog replacement design.

## Findings

### F1 - Proposal links `deliberation-protocol.md` but does not satisfy its proposal-search output requirement

Severity: Blocking

Evidence:

- `.claude/rules/deliberation-protocol.md` requires Prime Builder, before proposing, to search deliberations and, if prior reviews exist, cite DELIB IDs in the proposal's `Prior Deliberations` section and explain how the proposal differs from or builds on prior decisions (`.claude/rules/deliberation-protocol.md:13`, `.claude/rules/deliberation-protocol.md:16`).
- The revised proposal adds `.claude/rules/deliberation-protocol.md` to `Specification Links` and says it defines deliberation search and owner-decision archival obligations (`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md:87`).
- The proposal has no `Prior Deliberations` section. `rg` found no proposal citations for `DELIB-0839`, `DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`, `DELIB-S324-OM-DELTA-0004-CHOICE`, or `DELIB-1404`, even though those are relevant to standing backlog authority, fragmentation, ordering semantics, and candidate backlog material.

Risk/impact:

The revision operationalizes deliberation-query storage for future backlog rows, but the proposal itself does not demonstrate the live deliberation-search discipline it now cites as governing. That is especially risky here because the design changes the backlog authority surface and must preserve prior owner decisions about backlog continuity and ordering.

Recommended action:

Add a `Prior Deliberations` section to the proposal. Cite the relevant DELIB IDs found above or explain why Prime's own search finds a different relevant set. For each, state whether the proposal preserves, supersedes, or builds on the prior decision.

Decision needed from owner:

None. This is Prime-fixable.

### F2 - `GOV-ARTIFACT-APPROVAL-001` is used as a governing requirement but omitted from `Specification Links`

Severity: Blocking

Evidence:

- The bridge protocol requires the `Specification Links` section to cite every relevant governing specification, rule, ADR, DCL, proposal standard, or durable specification artifact, and says the only valid verdict is `NO-GO` if any relevant specification is missing (`.claude/rules/file-bridge-protocol.md:20`, `.claude/rules/file-bridge-protocol.md:23`, `.claude/rules/file-bridge-protocol.md:35`).
- The revised proposal references `GOV-ARTIFACT-APPROVAL-001` as the formal-approval contract for the owner directive archival (`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md:69`), as an acceptance criterion for successor ADR/DCL creation (`:255`), and as the Slice 1 governing approval path (`:274`).
- `GOV-ARTIFACT-APPROVAL-001` is not listed in the proposal's `Specification Links` section (`:71`-`:87`).
- Existing project state describes `GOV-ARTIFACT-APPROVAL-001` as requiring strict review, full native-format display, approval or acknowledgement evidence, and rich auditability (`memory/work_list.md:76`).

Risk/impact:

Slice 1 is explicitly a formal-artifact approval packet. If `GOV-ARTIFACT-APPROVAL-001` is not part of the linked specification set, the proposal's test/verification mapping cannot prove that the successor ADR/DCL/GOV mutations follow the applicable owner-approval contract.

Recommended action:

Add `GOV-ARTIFACT-APPROVAL-001` to `Specification Links`, then map it to concrete Slice 1 verification: owner approval evidence for the successor ADR, successor DCL, updated GOV record, and delayed owner-directive deliberation capture.

Decision needed from owner:

None. This is Prime-fixable.

### F3 - Append-only enforcement is asserted as a direct-SQL invariant without a concrete schema mechanism

Severity: Blocking

Evidence:

- The revised schema defines the `backlog_items` base table and `current_backlog_items` view, then describes current-row uniqueness as service-layer enforcement through insert/reorder transactions (`bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md:146`, `:170`).
- The revised test plan says `test_append_only_invariant_for_backlog_items` will prove that direct SQL `UPDATE` on `backlog_items` raises via a `CHECK constraint or trigger` (`:232`).
- The acceptance criteria separately require append-only versioning to be enforced at the schema level (`:248`).
- The cited existing MemBase principle is append-only versioning with no `UPDATE/DELETE` (`CLAUDE.md:91`), but the proposal does not specify the trigger, view-write pattern, permission boundary, or other concrete mechanism that will make direct SQL `UPDATE` fail for this new table.

Risk/impact:

An implementation team could satisfy the table/view shape while leaving the direct-SQL append-only test impossible or accidentally unenforced. That would undermine the core reason for moving from markdown to a durable source-of-truth table.

Recommended action:

Revise the schema section to define the concrete append-only enforcement mechanism. A sufficient fix would specify SQLite `BEFORE UPDATE` and `BEFORE DELETE` triggers on `backlog_items` that `RAISE(ABORT, ...)`, plus tests proving those triggers reject raw SQL mutation while append-style version inserts still work.

Decision needed from owner:

None. This is Prime-fixable.

## Verification

Commands and checks performed:

- Read live `bridge/INDEX.md`; selected document's latest status was `REVISED`, actionable for Loyal Opposition.
- Read the full selected bridge entry: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-003.md`.
- Read prior entry versions `-001.md` and `-002.md`.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, and `CLAUDE.md`.
- Searched Deliberation Archive via `KnowledgeDB.search_deliberations()` for backlog source-of-truth, standing backlog, markdown backlog discipline, implementation ordering, and deliberation-query topics.
- Used `rg` to check the revised proposal and governance surfaces for cited rules, missing prior-deliberation citations, and append-only/schema enforcement claims.

I did not run pytest or ruff because this is still a scoping/design proposal with no implementation changes to verify.

## Required Revision

Resubmit as `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-005.md` with:

1. A `Prior Deliberations` section satisfying `.claude/rules/deliberation-protocol.md`, including the relevant standing-backlog and ordering deliberations or an evidence-backed reason to exclude them.
2. `GOV-ARTIFACT-APPROVAL-001` added to `Specification Links` and mapped to Slice 1 verification.
3. A concrete schema-level append-only enforcement mechanism for `backlog_items`, with tests that prove raw SQL `UPDATE`/`DELETE` fail and append-style new versions succeed.

After those changes, the proposal is likely reviewable for GO.

