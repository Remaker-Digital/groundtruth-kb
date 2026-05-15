NEW

# Implementation Proposal - LO Advisory Intake Batch Disposition (WI-3296..WI-3307)

bridge_kind: implementation_proposal
Document: gtkb-lo-advisory-intake-batch
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH
Project: PROJECT-GTKB-LO-ADVISORY-INTAKE
Work Item: WI-3296

target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/", ".gtkb-state/advisory-dispositions/"]

This NEW umbrella proposal applies the `.claude/rules/peer-solution-advisory-loop.md` disposition workflow to 12 accumulated LO advisories (WI-3296..WI-3307). Each advisory receives a documented disposition (adopt / adapt / reject / defer / monitor) with per-WI evidence trail recorded under `.gtkb-state/advisory-dispositions/`.

## Claim

Process 12 LO advisories in a single bridge thread, with each advisory receiving an explicit disposition record. Dispositions resulting in adopt/adapt produce a `Next: file follow-on NEW proposal` marker; reject/defer/monitor produce a DELIB record citing the rationale. The work item for each advisory transitions to `resolved` after disposition.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; advisory disposition is governed bridge work.
- `GOV-ARTIFACT-APPROVAL-001` - reject/defer/monitor dispositions produce DELIB inserts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - per-advisory verification plan below.
- `GOV-STANDING-BACKLOG-001` - 12 WIs tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization establishing this project.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner directive to authorize 4 groupings including GTKB-LO-ADVISORY-INTAKE and complete implementation proposals.

## Requirement Sufficiency

Existing requirements sufficient. `.claude/rules/peer-solution-advisory-loop.md` fully specifies the disposition workflow.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a thematically-bundled batch but operates on each advisory atomically — 12 dispositions, each independently authored. Per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json` all 12 WIs are members of PROJECT-GTKB-LO-ADVISORY-INTAKE. Review-packet inventory: 12 disposition records + summary table.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-lo-advisory-intake-batch-001.md`; new top entry prepended to `bridge/INDEX.md`.

## Proposed Scope

Each advisory below receives a disposition. Predicted dispositions are author-best-guess; final disposition recorded after Codex review.

| WI | Advisory | Predicted disposition | Rationale |
|---|---|---|---|
| WI-3296 | ROLE-SESSION-LIFECYCLE-REVIEW | monitor | Implementation already converged; reference for future role/session work |
| WI-3297 | GTKB-MCP-STABLE-HARNESS-SURFACE | adapt | Adopt MCP surface concept but GT-KB-native; sibling work in flight |
| WI-3298 | BRIDGE-ADVISORY-REPORT-MESSAGE | adopt | Bridge ADVISORY status type already GO at sibling thread |
| WI-3299 | GTKB-SELF-MEASUREMENT-SYSTEM | adapt | Adopt measurement framing; benchmark suite work referenced |
| WI-3300 | PEER-SOLUTION-ADVISORY-REPORT | monitor | Process itself is operational |
| WI-3301 | GOOGLE-OPAL-REVIEW | reject | Different domain; no GT-KB adoption path |
| WI-3302 | CLAUDE-DESIGN-GTKB-INTEGRATION | defer | Defer until Claude Design GA + adopter integration plan |
| WI-3303 | LO-HYGIENE-ASSESSMENT-SKILL-AD | adopt | High-value LO skill; follow-on bridge proposal |
| WI-3304 | GITHUB-AI-HARNESS-ECOSYSTEM | monitor | Industry context; no immediate action |
| WI-3305 | gtkb-owner-role-switch-codex-loyal-opposition | resolved-in-place | Bridge advisory already actioned via role-switch |
| WI-3306 | GTKB-DOCUMENTATION-QUALITY-REVIEW | adapt | Adopt key findings into GTKB-DOCUMENTATION work (separate project) |
| WI-3307 | CANONICAL-TERMINOLOGY-SYSTEM-A | adapt | Findings already partially adopted in glossary; remainder forward |

### IP-1: Disposition records

For each advisory, write `.gtkb-state/advisory-dispositions/<WI-ID>.md` with: WI ID, advisory title + source path, disposition, rationale (3-5 sentences), follow-on action (bridge proposal slug or DELIB ID), date, author.

### IP-2: DELIB records for non-adopt dispositions

For each `reject`, `defer`, `monitor`, `resolved-in-place` disposition: insert a DELIB into MemBase with `source_type=loyal_opposition_review`, `outcome=advisory_disposition`, content = the disposition rationale + cited advisory text reference. Per `GOV-ARTIFACT-APPROVAL-001` each DELIB insert cites an approval packet; this NEW's GO is the packet covering all 12 dispositions.

### IP-3: Follow-on bridge proposal markers for adopt/adapt dispositions

For each `adopt` / `adapt` disposition: record in the disposition file the slug of the follow-on bridge proposal that will be filed in a subsequent slice (e.g., WI-3297 -> `gtkb-mcp-stable-harness-surface-adapt-001` to be filed separately).

### IP-4: WI status transitions

After IP-1..IP-3, update each WI's `resolution_status` to `resolved` with `change_reason` citing the disposition record path.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Disposition file exists for each WI | `test_advisory_disposition_files_present_for_all_12_wis` |
| DELIB inserted for each non-adopt | `test_advisory_disposition_delib_per_non_adopt` |
| Adopt/adapt rows reference future bridge slug | `test_advisory_disposition_adopt_records_follow_on_slug` |
| WI status transitioned to resolved | `test_advisory_disposition_wi_status_resolved` |
| Cross-reference to peer-solution-advisory-loop rule satisfied | `test_advisory_disposition_cites_rule_path` |

Test execution: `python -m pytest tests/governance/test_advisory_disposition_batch.py -v`.

## Acceptance Criteria

- IP-1: 12 disposition records written.
- IP-2: 1 DELIB per non-adopt disposition (estimated 7-9 DELIBs depending on owner override).
- IP-3: Adopt/adapt entries have follow-on bridge slugs.
- IP-4: 12 WIs transitioned to resolved.
- Tests PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: predicted dispositions may not match owner's actual judgment for high-stakes advisories. Mitigation: dispositions are author-best-guess and remain owner-overrideable until WI status transitions to resolved.
- Risk: bundling 12 WIs in one proposal complicates per-WI rollback. Mitigation: per-WI disposition files allow per-WI revert.
- Rollback: revert disposition files + DELIB inserts; restore WI status to open.

## Recommended Commit Type

`chore` - governance disposition records, no code change. ~12 disposition files + ~7-9 DELIBs + 12 WI status updates.
