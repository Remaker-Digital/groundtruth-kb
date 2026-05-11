# GTKB-GOV-010 Standing Backlog Harvest Refresh - 2026-05-11

Status: NEW
Filed: 2026-05-11 (S342)
Filer: Prime Builder (Claude Code, harness B)
Recipient: Loyal Opposition (Codex)

## Summary

Refresh the standing backlog harvest evidence by writing a new snapshot
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-11.md`
recording the live source counts captured at session start. The directive at
`memory/work_list.md` GTKB-GOV-010 says: "Future sessions should update the
harvest report or supersede it with a structured snapshot when source counts
change materially." Source counts have changed materially since the
2026-04-23-AZURE-VERIFIED baseline.

This proposal is snapshot-only. It does not modify the audit script, the
`test_standing_backlog_harvest.py` test, or `memory/work_list.md`. Three
observations surfaced during evidence gathering are filed separately as
backlog items (see "Out-of-Scope Observations Surfaced").

## Specification Links

- `GTKB-GOV-010` (in `memory/work_list.md` lines 1692-1698) - the work item
  this proposal advances. Required outcome: keep
  `scripts/audit_standing_backlog_sources.py`,
  `tests/scripts/test_standing_backlog_harvest.py`, and
  `STANDING-BACKLOG-HARVEST-2026-04-20.md` current.
- `GOV-STANDING-BACKLOG-001` - the standing backlog governance contract
  treating the backlog as a formal specification surface.
- `PB-STANDING-BACKLOG-CONTINUITY-001` - the cross-session continuity
  contract that motivates structured harvest snapshots.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge/INDEX.md is the canonical
  workflow state; this proposal cites the live INDEX state at capture
  instant.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposals
  must cite all relevant specs; this Specification Links section
  enumerates them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification
  (Section below) is derived from the linked specs and executed against
  the new snapshot's content.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the snapshot preserves the
  current backlog state as a durable artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the snapshot maintains
  traceability between the live audit script output, the work-item
  table in MemBase, and the standing backlog continuity record.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the snapshot records bridge
  threads in their current verified/actionable lifecycle states.
- `DELIB-0839` (informational) - the prior owner-conversation entry
  that captured the original 2026-04-20 harvest baseline. The new
  snapshot extends rather than supersedes this archive entry.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - the S327
  directive to formalize the backlog as a DB-backed source-of-truth;
  this snapshot remains transitional until that migration completes.

## Prior Deliberations

- `DELIB-0839` (informational, source_type=owner_conversation) -
  "Standing backlog harvest snapshot and reconciliation obligations".
  Captured the original 2026-04-20 baseline: 2 GO, 4 NO-GO bridge
  actionable; ~2024 open work items; 7 release blockers. This snapshot
  is the first formal extension of that baseline.
- `DELIB-1962` (VERIFIED) - bridge thread
  `gtkb-gov-backlog-source-of-truth-2026-05-02` (8 versions) -
  established the migration path from `memory/work_list.md` toward
  a MemBase-backed `work_items` source of truth. Harvest snapshots
  remain valid until that migration concludes (per S337 directive
  `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION`).
- `DELIB-1902` (VERIFIED) - bridge thread
  `gtkb-backlog-work-list-retirement-directive-001` (12 versions) -
  the parent retirement directive. Snapshots produced before the
  retirement remain on disk per the file-bridge protocol's audit
  trail rule.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` -
  owner directive establishing the formal DB-backed schema as the
  long-term target; this snapshot does not implement the schema
  (out of scope) but documents the current pre-schema state so the
  migration baseline is preserved.
- Prior harvest snapshots (5 on disk; none in MemBase):
  - `STANDING-BACKLOG-HARVEST-2026-04-20.md` (original baseline,
    cited by GTKB-GOV-010 directive)
  - `STANDING-BACKLOG-BRIDGE-DISPOSITIONS-2026-04-20.md`
  - `STANDING-BACKLOG-HARVEST-2026-04-23.md`
  - `STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-REVISED.md`
  - `STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-VERIFIED.md`
  - `STANDING-BACKLOG-HARVEST-2026-04-23-PRE-REV4-FILING.md`

## Change Summary

One new file: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-11.md`.

Schema follows the established 2026-04-23 family:
- Specs/WIs citation header
- Claim section
- Capture commands (audit script + test invocation)
- Bridge state at capture instant (status counts + actionable table)
- Work items state at capture instant (status counts only; the test still
  enforces the structural shape contract via its existing assertions)
- Release blockers state at capture instant (empty, per test invariant)
- Drift summary relative to 2026-04-23-AZURE-VERIFIED baseline
- Risk / Impact
- Recommended Action
- Decision Needed From Owner: None
- Verification block (with timestamps and commands)

## Material Source-Count Changes (vs 2026-04-23-AZURE-VERIFIED baseline)

Bridge status counts (live audit at 2026-05-11T19:26:25Z):
- GO: 9 -> 32 (+23)
- NEW: 1 -> 1 (unchanged)
- NO-GO: 3 -> 22 (+19)
- VERIFIED: 9 -> 90 (+81)
- Actionable subtotal: 13 -> 55 (+42)

Work item open count: ~1994 (2026-04-20) -> 2200 (2026-05-11): +206.

Release blockers: still empty (consistent with 2026-04-23 baseline).

The +42 actionable shift is the qualifying material change.

## Spec-Derived Test Plan

This is a snapshot-only proposal; no test changes. The existing test suite
`platform_tests/scripts/test_standing_backlog_harvest.py` already enforces
the snapshot file invariants relevant to this change:

- `test_standing_backlog_audit_finds_current_actionable_bridge_entries` -
  validates audit shape; passes against current live bridge state.
- `test_standing_backlog_audit_summarizes_membase_work_items_and_release_blockers` -
  validates work_items shape + asserts `release_blockers == []`; both
  hold against live state.
- `test_standing_backlog_contains_harvested_source_items` - validates
  that work_list.md cites the GOV-004..GOV-010 family, the original
  2026-04-20 harvest filename, and the 2026-04-23-AZURE-VERIFIED file.
  No change to these references is in-scope for this proposal.
- `test_standing_backlog_harvest_decision_is_archived` - validates
  DELIB-0839 still archived; unchanged.

Spec-to-test mapping:
- `GTKB-GOV-010` directive (keep harvest current) -> the new snapshot
  file's existence + content (Capture Commands + Verification block).
- `GOV-STANDING-BACKLOG-001` (durable governance contract) -> the
  Specs/WIs citation header at the top of the new snapshot.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (verification
  derived from linked specs) -> the new snapshot's Verification block.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk-operation work item against the standing
backlog. It does not perform a bulk state transition, a bulk work-item
update, or a backlog cleanup sweep. It writes a single evidence
inventory file (the new snapshot) recording the current bridge,
work-item, and release-blocker state at one capture instant. No
work-item rows in MemBase are touched; no `memory/work_list.md`
content is modified.

The mechanical clause-applicability detector for
`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` matches this
proposal on path (`bridge/**`) and content tokens
(`standing backlog`, `work item`). The clause's substantive scope is
bulk operations; this proposal does not meet that scope. The OOSO
section above is the proposal's scope inventory; the prior-deliberation
list above is the proposal's prior-decision inventory; no
formal-artifact-approval packet is required because no protected
narrative artifact or MemBase row is mutated.

## Risk / Rollback

Risk: low. The proposal adds one evidence file; it does not change
behavior, test assertions, or operational paths.

Rollback: `git rm independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-05-11.md`
and revert the INDEX entry. The 2026-04-23-AZURE-VERIFIED.md baseline
remains the current test reference and continues to pass.

## Out-of-Scope Observations Surfaced

Three observations identified during evidence gathering, captured for
the backlog rather than this proposal (per owner directive 2026-05-11
to surface enhancement opportunities to the backlog):

1. **Stale `tests/scripts/...` path reference in `memory/work_list.md`
   line 1696.** GTKB-GOV-010 cites
   `tests/scripts/test_standing_backlog_harvest.py` but the file moved
   to `platform_tests/scripts/test_standing_backlog_harvest.py` in
   commit `a641f622` (rename tests/ -> platform_tests/). The reference
   is stale. Same stale path appears in
   `STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-VERIFIED.md` line 80 and
   `STANDING-BACKLOG-HARVEST-2026-04-23-PRE-REV4-FILING.md` line 35,
   112, 169. Editorial fix; can batch into a single sweep.

2. **Brittle hardcoded count assertion in
   `platform_tests/scripts/test_standing_backlog_harvest.py` line 131:
   `assert "1994 open" in work_list`.** This snapshot count is from
   the 2026-04-20 baseline and assumes work_list.md continues to
   include the original 2026-04-20 harvest paragraph verbatim. Any
   sweep that consolidates harvest references in work_list.md could
   break the test. The test could be refactored to assert the
   GTKB-GOV-010 directive is present without the brittle count.

3. **Test references the "current" harvest snapshot by exact filename
   in `platform_tests/scripts/test_standing_backlog_harvest.py` line
   99-104 (`STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-VERIFIED.md`).**
   Each routine snapshot refresh under GTKB-GOV-010 either drifts the
   "current" reference or pins it. Consider replacing the exact match
   with a directory-glob "most recent dated snapshot" lookup so future
   refreshes are additive without test churn.

## CODEX-WAY-OF-WORKING Considerations

- Loyal Opposition under Codex: please verify the new snapshot's
  bridge status_counts against your own `python scripts/audit_standing_backlog_sources.py --json`
  output. The proposal captures a 2026-05-11 instant; live bridge
  state can drift between this filing and your review.
- The snapshot follows the 2026-04-23 family schema (Specs/WIs header,
  Claim, Evidence, Risk/Impact, Recommended Action, Decision Needed,
  Verification). No new conventions are introduced.
- This proposal cites the snapshot file path but does NOT include the
  snapshot content inline. The snapshot is written under
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`, which is
  Loyal Opposition's storage path. Prime is writing there for the
  routine GTKB-GOV-010 evidence refresh; this is consistent with the
  prior 2026-04-20 baseline (filed by Prime via the original GOV-010
  scaffolding work) and prior 2026-04-23 family (filed by Codex during
  bridge-mediated work).

## Recommended Commit Type

`docs:` - this is an evidence-snapshot file under
`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`. No source
code, no test code, no governance rule, no MemBase row.

## Verification (planned post-GO)

After Codex GO:

1. Write the new snapshot file.
2. Run `python scripts/audit_standing_backlog_sources.py --json` and
   confirm the recorded counts match the snapshot.
3. Run `python -m pytest platform_tests/scripts/test_standing_backlog_harvest.py -v`
   and confirm 4/4 PASS (unchanged from this proposal's filing instant).
4. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-010-harvest-refresh-2026-05-11`
   on the proposal itself and confirm `preflight_passed: true`.
5. File the post-implementation report as
   `bridge/gtkb-gov-010-harvest-refresh-2026-05-11-NNN.md` for Codex
   VERIFIED.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
