REVISED

# Implementation Proposal - work_list.md GTKB-GOV Stale-Path Correction (WI-3278)

bridge_kind: implementation_proposal
Document: gtkb-work-list-md-gov-010-path-correction
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-SPEC-TEST-QUALITY-SPEC-TEST-QUALITY-BATCH
Project: PROJECT-GTKB-SPEC-TEST-QUALITY
Work Item: WI-3278

target_paths: ["memory/work_list.md", ".groundtruth/formal-artifact-approvals/*-work-list-md-*.json"]

This REVISED proposal corrects the genuinely-stale standing-backlog-harvest test path in `memory/work_list.md` and aligns the S342 follow-up diagnostic observation with current file state.

## Revision Notes (-003 vs -001)

This REVISED version addresses every finding in the `-002` NO-GO
(`bridge/gtkb-work-list-md-gov-010-path-correction-002.md`):

- **FINDING-P1-001 (P1) — The cited GTKB-GOV-010 defect was stale against
  current file content.** The `-001` proposal targeted the GTKB-GOV-010 entry,
  but the current `memory/work_list.md:1696` (the GTKB-GOV-010 "Required
  outcome" line) already names the correct
  `platform_tests/scripts/test_standing_backlog_harvest.py`. The genuinely
  stale live string is at `memory/work_list.md:1666` — the GTKB-GOV-004
  "Regression visibility" line, which still names
  `tests/scripts/test_standing_backlog_harvest.py`. This `-003` retargets the
  correction to that actual stale live line (IP-1). The diagnostic narrative at
  `memory/work_list.md:1706` (GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 item 1)
  is handled separately and explicitly (IP-2).
- **FINDING-P1-002 (P1) — The whole-file zero-match grep verification would
  require removing diagnostic/historical text.** The `-001` verification
  required `grep "tests/scripts/test_standing_backlog_harvest.py"
  memory/work_list.md` to return zero matches. That would wrongly flag the
  diagnostic narrative at line 1706, which legitimately quotes the old path to
  describe the stale-path observation. This `-003` replaces the whole-file
  zero-match check with line-scoped checks that distinguish the live directive
  (line 1666) from the diagnostic narrative (the
  GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 block).
- **FINDING-P1-003 (P1) — The required narrative-artifact approval-packet
  write was outside `target_paths`.** `memory/work_list.md` is a protected
  narrative artifact; the edit requires a narrative-artifact-approval packet.
  This `-003` adds the packet glob
  `.groundtruth/formal-artifact-approvals/*-work-list-md-*.json` to
  `target_paths` and the `## Owner Decisions / Input` section notes that a
  narrative-artifact approval packet will be required at implementation time.

### Line ~1706 diagnostic-text disposition (FINDING-P1-001 explicit requirement)

The NO-GO required this proposal to state the intended disposition of the
`memory/work_list.md:1706` diagnostic text. **Disposition: UPDATE (not remove,
not leave wholly untouched).**

Rationale: the diagnostic observation at line 1706 currently says the
GTKB-GOV-010 entry "(above, line 1696)" cites the stale path. That premise is
now false — line 1696 already names the correct `platform_tests/...` path. The
text is therefore partially inaccurate as live diagnostic narrative. It is NOT
removed, because (a) it still records a real, not-yet-fully-closed observation
(the GTKB-GOV-004 line and the three historical snapshot files still carry the
stale path), and (b) the S342 follow-up block is explicitly a batched-hygiene
record per `memory/work_list.md:1704`. IP-2 updates the line-1706 text so it
accurately reflects current state: the GTKB-GOV-010 line-1696 reference has
already been corrected; the remaining stale live reference is the GTKB-GOV-004
"Regression visibility" line; the three historical snapshot files are preserved
unchanged as evidence. The historical snapshot files
(`STANDING-BACKLOG-HARVEST-2026-04-23-*.md`) are NOT targeted by this proposal
and remain untouched as point-in-time evidence.

No technical-scope expansion beyond retargeting to the correct stale line and
correcting the diagnostic narrative; this remains a `memory/work_list.md`
text-only correction plus its required approval packet.

## Claim

Two line-scoped text corrections within `memory/work_list.md`:

1. At the GTKB-GOV-004 "Regression visibility" line (currently `memory/work_list.md:1666`), replace `tests/scripts/test_standing_backlog_harvest.py` with `platform_tests/scripts/test_standing_backlog_harvest.py`.
2. At the GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 item-1 diagnostic text (currently `memory/work_list.md:1706`), update the narrative so it accurately states current file state (GTKB-GOV-010 line 1696 already corrected; the remaining stale live reference is the GTKB-GOV-004 line; historical snapshots preserved as evidence).

The GTKB-GOV-010 "Required outcome" line (currently `memory/work_list.md:1696`) is already correct and is NOT edited.

## In-Root Placement Evidence

Both target paths are in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol governing this proposal's filing path.
- GOV-STANDING-BACKLOG-001 - work_list.md is the (transitional) standing backlog view.
- GOV-ARTIFACT-APPROVAL-001 - work_list.md is a protected narrative artifact; edit requires a narrative-artifact-approval packet.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - in-root only; both target paths are inside `E:\GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - mandatory specification linkage.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping (manual line-scoped verification given doc-only change).
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - bridge proposal project + work-item metadata requirement.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol; target_paths and verification-gate requirements.
- `.claude/rules/project-root-boundary.md` - root-boundary discipline.

## Prior Deliberations

- DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS - batch-5 owner authorization for the GTKB-SPEC-TEST-QUALITY project grouping, including WI-3278.
- DELIB-0839 - records the original standing backlog harvest snapshot and the original `tests/scripts/test_standing_backlog_harvest.py` wiring (cited in the `-002` NO-GO; the path moved in commit `a641f622`).
- DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE - owner directive that `memory/work_list.md` is a transitional compatibility surface with MemBase as the formal backlog source-of-truth direction.
- DELIB-1902 - verified bridge thread for the backlog work-list retirement directive.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the GTKB-SPEC-TEST-QUALITY project authorization (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`) including WI-3278; recorded via formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. This authorizes WI-3278 implementation work through the bridge protocol.
- Narrative-artifact approval at implementation time: `memory/work_list.md` is a protected narrative artifact per `config/governance/narrative-artifact-approval.toml`. A narrative-artifact-approval packet at `.groundtruth/formal-artifact-approvals/<date>-work-list-md-*.json` will be required before the `memory/work_list.md` edit is written. That packet is a per-edit owner-visible approval and is collected at implementation time after this proposal's GO; the bridge GO does not substitute for the per-artifact narrative-artifact-approval packet.

## Requirement Sufficiency

Existing requirements sufficient. The governing specifications (GOV-STANDING-BACKLOG-001 for the backlog view, GOV-ARTIFACT-APPROVAL-001 for the protected-narrative-artifact discipline, and the bridge-protocol rule set) fully constrain this text-only correction. No new or revised requirement or specification is created by this work.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk operation. It is a single-work-item (WI-3278) text-only correction to `memory/work_list.md` plus the one narrative-artifact-approval packet that the protected-narrative-artifact discipline requires for that edit. It performs no batch resolve, promote, retire, or reorder of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single WI-3278 and its governed `memory/work_list.md` surface only. WI-3278 is an active member of PROJECT-GTKB-SPEC-TEST-QUALITY (membership record `PWM-PROJECT-GTKB-SPEC-TEST-QUALITY-WI-3278`, status `active`). Applicable evidence pattern: a single-WI documentation-correction implementation proposal with `inventory` of touched files limited to the two `target_paths` entries and `formal-artifact-approval` discipline preserved (the narrative-artifact-approval packet is collected per `GOV-ARTIFACT-APPROVAL-001`).

## Bridge INDEX Update Evidence

`REVISED: bridge/gtkb-work-list-md-gov-010-path-correction-003.md` prepended to this thread's INDEX entry, above the `-002` NO-GO line.

## Proposed Scope

### IP-1: GTKB-GOV-004 stale-path correction (the genuine live defect)

In `memory/work_list.md`, locate the GTKB-GOV-004 entry's "Regression visibility" line (currently line 1666). Replace the stale path:

- Before: `... keep \`scripts/audit_standing_backlog_sources.py\` and \`tests/scripts/test_standing_backlog_harvest.py\` in the release-candidate gate ...`
- After: `... keep \`scripts/audit_standing_backlog_sources.py\` and \`platform_tests/scripts/test_standing_backlog_harvest.py\` in the release-candidate gate ...`

Only the `tests/scripts/` -> `platform_tests/scripts/` segment of that one line changes. The GTKB-GOV-004 priority text, required outcome, and the `scripts/audit_standing_backlog_sources.py` reference are unchanged.

### IP-2: GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 item-1 diagnostic-text update

In `memory/work_list.md`, locate item 1 of the GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 block (currently line 1706). The current text asserts the GTKB-GOV-010 entry "(above, line 1696)" cites the stale path; that premise is now false. Update the narrative to accurately reflect current state. Intended replacement text for item 1:

> 1. **Stale `tests/scripts/...` path reference in this file.** The GTKB-GOV-010 entry's required-outcome line was previously stale and has since been corrected to `platform_tests/scripts/test_standing_backlog_harvest.py`. The remaining stale live reference in this file is the GTKB-GOV-004 "Regression visibility" line, corrected under WI-3278. The same stale path still appears in the historical snapshots `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STANDING-BACKLOG-HARVEST-2026-04-23-AZURE-VERIFIED.md` line 80 and `STANDING-BACKLOG-HARVEST-2026-04-23-PRE-REV4-FILING.md` lines 35, 112, 169; those snapshot files are preserved unchanged as point-in-time evidence and are intentionally not edited.

The disposition is UPDATE: the observation is preserved (it still records the historical-snapshot staleness, which is real and intentionally not swept), but its now-inaccurate live-line premise is corrected. The historical snapshot files themselves are NOT edited. Items 2 and 3 of the S342 follow-up block are unchanged and remain open hygiene items.

### IP-3: Narrative-artifact-approval packet

`memory/work_list.md` is a protected narrative artifact per `config/governance/narrative-artifact-approval.toml`. A `narrative-artifact-approval` packet at `.groundtruth/formal-artifact-approvals/<date>-work-list-md-*.json` is required for this edit and is generated at implementation time citing this bridge thread's GO and the exact edited content / content hash. This path is included in `target_paths` so the implementation-start authorization envelope covers it.

## Specification-Derived Verification Plan

Whole-file zero-match verification is intentionally NOT used (it would wrongly flag diagnostic narrative). Verification is line-scoped.

| Behavior | Verification |
|---|---|
| GTKB-GOV-004 live directive corrected | The GTKB-GOV-004 "Regression visibility" line names `platform_tests/scripts/test_standing_backlog_harvest.py` and no longer names `tests/scripts/test_standing_backlog_harvest.py`. |
| GTKB-GOV-010 line left correct | The GTKB-GOV-010 "Required outcome" line still names `platform_tests/scripts/test_standing_backlog_harvest.py` (unchanged; was already correct). |
| S342 follow-up item-1 narrative updated | The GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 item-1 text accurately states the GTKB-GOV-010 line is already corrected and the remaining live stale reference is the GTKB-GOV-004 line; the three historical snapshot file references are preserved. |
| Diagnostic / historical text preserved | The S342 follow-up observation block still exists; items 2 and 3 are byte-unchanged; the historical snapshot files are byte-unchanged. |
| Scope is minimal | `git diff memory/work_list.md` shows only the GTKB-GOV-004 path segment and the S342 item-1 narrative changed; no other lines changed. |
| Narrative-artifact-approval packet present | A packet matching `.groundtruth/formal-artifact-approvals/*-work-list-md-*.json` exists, cites this thread's GO, and its content hash matches the written `memory/work_list.md` edit. |

This is a documentation correction; there is no automated unit test. Verification is the line-scoped manual checks above plus the `git diff` minimality check, executed and pasted into the post-implementation report.

## Acceptance Criteria

- IP-1: the GTKB-GOV-004 "Regression visibility" line is corrected to `platform_tests/scripts/test_standing_backlog_harvest.py`.
- IP-2: the GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 item-1 narrative is updated to current-state-accurate text; items 2 and 3 unchanged; historical snapshot files unedited.
- IP-3: a narrative-artifact-approval packet exists at the `target_paths` glob and matches the edited content.
- The GTKB-GOV-010 "Required outcome" line is unchanged (it was already correct).
- All line-scoped verifications above pass; `git diff` shows only the two intended changes.
- Both preflights pass.

## Files Expected To Change

- `memory/work_list.md` - GTKB-GOV-004 "Regression visibility" path segment corrected; GTKB-GOV-010-FOLLOWUP-OBSERVATIONS-S342 item-1 diagnostic text updated.
- `.groundtruth/formal-artifact-approvals/<date>-work-list-md-*.json` - narrative-artifact-approval packet for the `memory/work_list.md` edit (generated at implementation time).

## Risks / Rollback

- Risk: the stale path may also be referenced elsewhere in live files. Mitigation: during implementation, grep the whole repo for `tests/scripts/test_standing_backlog_harvest.py`; live directive references found outside the GTKB-GOV-004 line are reported (not silently edited) and, if any are found, work stops and a revised proposal listing the additional lines is filed. Historical snapshot files under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` are explicitly out of scope and preserved.
- Risk: a strict reviewer might expect the historical snapshots corrected too. Disposition is explicit: snapshots are point-in-time evidence and are intentionally preserved unchanged; the S342 follow-up block already records them as a separate batched-hygiene observation.
- Rollback: revert the two `memory/work_list.md` edits and remove the narrative-artifact-approval packet; the change is two text spans in one file.

## Recommended Commit Type

`docs` - documentation correction to `memory/work_list.md` (a governance/backlog narrative surface) plus its required approval packet; no source code, test, or capability change.

## Applicability Preflight

Re-run on this `-003` operative file after the INDEX `REVISED` line was added. Full output is embedded below under "Applicability Preflight (Embedded Output)".

## Applicability Preflight (Embedded Output)

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-list-md-gov-010-path-correction`

```text
## Applicability Preflight

- packet_hash: `sha256:c65a71226f98cbe041fa3f68deacc1d965ad4e09907b6027dc0e1e71ca27a501`
- bridge_document_name: `gtkb-work-list-md-gov-010-path-correction`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-work-list-md-gov-010-path-correction-003.md`
- operative_file: `bridge/gtkb-work-list-md-gov-010-path-correction-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

Exit 0. `preflight_passed: true`; `missing_required_specs: []`. The three `missing_advisory_specs` are advisory-severity only and never gate `GO`; the proposal cites the blocking cross-cutting set in full.

## Clause Applicability (Embedded Output)

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-list-md-gov-010-path-correction`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-work-list-md-gov-010-path-correction`
- Operative file: `bridge\gtkb-work-list-md-gov-010-path-correction-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Exit 0. 5/5 `must_apply` clauses with evidence found; 0 blocking gaps. No owner-waiver line is required.
