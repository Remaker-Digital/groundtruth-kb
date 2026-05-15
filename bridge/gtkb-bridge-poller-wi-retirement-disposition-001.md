NEW

# Implementation Proposal - Retirement Disposition for Bridge Poller WIs + Claude Axis-2 Thread WI

bridge_kind: implementation_proposal
Document: gtkb-bridge-poller-wi-retirement-disposition
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-POLLER-001

target_paths: ["groundtruth.db"]

This NEW proposal dispositions 4 work items that no longer warrant implementation: 3 bridge-poller-* WIs (poller retired 2026-05-09 per Slice 4) and WI-3256 (Claude axis-2 thread automation; 4 NO-GOs + question of whether parity is worth the cost).

## Claim

Apply retirement / wont_fix dispositions to:
1. GTKB-BRIDGE-POLLER-001 - poller umbrella; superseded by cross-harness event-driven trigger.
2. GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR - trigger-conditional refactor no longer applicable.
3. GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT - smart-poller-specific gap; not applicable post-retirement.
4. WI-3256 - Claude-side axis-2 thread automation; 4 NO-GOs surfaced cost-benefit question that owner chose to defer indefinitely.

## In-Root Placement Evidence

Target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog hygiene.
- `GOV-ARTIFACT-APPROVAL-001` - WI mutation evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; poller retirement supersedes these WIs.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the canonical dispatch substrate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - poller retirement decision.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.
- `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` - Slice 4 retirement that superseded the 3 poller WIs.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-BRIDGE-PROTOCOL-RELIABILITY authorization; this proposal cleans the inventory of superseded WIs.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

This is a 4-WI disposition cleanup, member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory enumerates per-WI disposition + rationale.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Retire 3 poller WIs

Update each WI to `resolution_status='retired'` with `change_reason` citing `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09`:

- GTKB-BRIDGE-POLLER-001
- GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR
- GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT

### IP-2: Disposition WI-3256

Update WI-3256 to `resolution_status='wont_fix'` with `change_reason` citing the 4-NO-GO history + owner-deferral question + the fact that Codex-side axis-2 automation already exists and is operational. Re-evaluation tracker created as a future-monitor DELIB if owner re-opens.

### IP-3: No spec changes

No spec promotions or new specs.

## Specification-Derived Verification Plan

| Behavior | Verification |
|---|---|
| 3 poller WIs marked retired | `db.get_work_item('GTKB-BRIDGE-POLLER-001').resolution_status == 'retired'` (and siblings) |
| WI-3256 marked wont_fix | `db.get_work_item('WI-3256').resolution_status == 'wont_fix'` |
| Change_reason cites superseding DELIB | per-WI change_reason references `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` |
| No code regressions | not applicable; no code mutations |

(No automated tests; this is backlog data triage.)

## Acceptance Criteria

- IP-1, IP-2 dispositions applied.
- Per-WI change_reason cites this proposal + superseding DELIB.
- Both preflights PASS.

## Risks / Rollback

- Risk: an unrecorded owner intent may exist for one of the poller WIs that I haven't surfaced. Mitigation: search Deliberation Archive for poller-specific decisions before applying retirement.
- Rollback: revert each WI's resolution_status; restore prior change_reason.

## Recommended Commit Type

`chore` - backlog data hygiene. No code change.
