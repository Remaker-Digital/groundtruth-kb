NEW

# Implementation Proposal - work_list.md GTKB-GOV-010 Path Correction (WI-3278)

bridge_kind: implementation_proposal
Document: gtkb-work-list-md-gov-010-path-correction
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-SPEC-TEST-QUALITY-SPEC-TEST-QUALITY-BATCH
Project: PROJECT-GTKB-SPEC-TEST-QUALITY
Work Item: WI-3278

target_paths: ["memory/work_list.md"]

This NEW proposal corrects a stale test path in `memory/work_list.md`'s GTKB-GOV-010 entry: it names `tests/scripts/test_standing_backlog_harvest.py`; the actual path is `platform_tests/scripts/test_standing_backlog_harvest.py`.

## Claim

One-line edit to `memory/work_list.md`: replace `tests/scripts/test_standing_backlog_harvest.py` with `platform_tests/scripts/test_standing_backlog_harvest.py` in the GTKB-GOV-010 entry.

## In-Root Placement Evidence

Target path in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol governing this proposal's filing path.
- `GOV-STANDING-BACKLOG-001` - work_list.md is the (transitional) standing backlog view.
- `GOV-ARTIFACT-APPROVAL-001` - work_list.md is a protected narrative artifact; edit requires narrative-artifact-approval packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping (manual verification given doc-only change).
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-SPEC-TEST-QUALITY authorization including WI-3278.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-SPEC-TEST-QUALITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: single text edit.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Path correction

In `memory/work_list.md`, locate the GTKB-GOV-010 entry. Replace the stale path:
- Before: `tests/scripts/test_standing_backlog_harvest.py`
- After: `platform_tests/scripts/test_standing_backlog_harvest.py`

### IP-2: Narrative-artifact-approval packet

`memory/work_list.md` is a protected narrative artifact. A new `narrative-artifact-approval` packet is required for this edit (per `config/governance/narrative-artifact-approval.toml`). The packet is generated at implementation time citing this bridge's GO.

### IP-3: Verification

Post-edit grep for the new path returns exactly one match; old path returns zero matches in `memory/work_list.md`.

## Specification-Derived Verification Plan

| Behavior | Verification |
|---|---|
| Old path absent | `grep "tests/scripts/test_standing_backlog_harvest.py" memory/work_list.md` returns nothing |
| New path present | `grep "platform_tests/scripts/test_standing_backlog_harvest.py" memory/work_list.md` returns 1 match |
| Surrounding context unchanged | diff shows single-line change only |
| Narrative-artifact-approval packet present | `.groundtruth/narrative-artifact-approvals/<date>-work-list-md-*.json` exists |

(No automated test; this is a one-line documentation correction.)

## Acceptance Criteria

- IP-1 text replacement made.
- IP-2 packet present at impl time.
- IP-3 manual verifications pass.
- Both preflights PASS.

## Risks / Rollback

- Risk: path may also be referenced elsewhere with the same staleness. Mitigation: grep entire repo for the stale path during implementation.
- Rollback: revert the single edit.

## Recommended Commit Type

`docs` - documentation correction; no code change. 1 line.
