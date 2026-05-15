NEW

# Implementation Proposal - Legacy GOV WI Cleanup (GTKB-GOV-CODE-QUALITY-BASELINE / GOV-DA-ENFORCEMENT / GOV-004)

bridge_kind: implementation_proposal
Document: gtkb-legacy-gov-wi-cleanup
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-CODE-QUALITY-BASELINE

target_paths: ["groundtruth.db"]

This NEW proposal triages 3 legacy GTKB-GOV-* work items that exist as placeholder entries with empty/minimal descriptions: GTKB-GOV-CODE-QUALITY-BASELINE, GTKB-GOV-DA-ENFORCEMENT, GTKB-GOV-004. Each is evaluated for: (a) retire as superseded, (b) reframe into a real work item with proper scope, or (c) consolidate into another active project.

## Claim

These 3 WIs are vestigial backlog entries from earlier governance experiments. Each receives a documented disposition. GTKB-GOV-004 has a description ("Reconcile legacy MemBase work items into a high-quality unified...") that suggests it's still meaningful; the other two appear to be name-only placeholders.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - backlog hygiene.
- `GOV-ARTIFACT-APPROVAL-001` - WI mutation evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-GOVERNANCE-HARDENING authorization including these 3 legacy WIs.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

This is a 3-WI cleanup; per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json` all 3 are members of PROJECT-GTKB-GOVERNANCE-HARDENING. Each WI is dispositioned independently — review-packet inventory enumerates per-WI rationale + status transition.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: GTKB-GOV-CODE-QUALITY-BASELINE disposition

Read existing description (empty/minimal). Verdict: retire as vestigial. Update WI: `resolution_status='wont_fix'`, `change_reason='Vestigial placeholder; no concrete scope. Retired per GTKB-GOVERNANCE-HARDENING cleanup batch.'`

### IP-2: GTKB-GOV-DA-ENFORCEMENT disposition

Similar inspection. Likely retire as superseded by DA-related work already in flight (Deliberation Archive protocol is operational; see `.claude/rules/deliberation-protocol.md`). Update WI: `resolution_status='resolved'` if superseded by existing implementation, else `'wont_fix'`.

### IP-3: GTKB-GOV-004 disposition

Description references "reconcile legacy MemBase work items into unified..." — this is real scope. Disposition: keep open but reframe as `GTKB-GOV-004-LEGACY-WI-RECONCILE`. Update title for clarity; do not retire.

### IP-4: No spec promotion (cleanup-only)

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| GTKB-GOV-CODE-QUALITY-BASELINE retired | manual: `db.get_work_item('GTKB-GOV-CODE-QUALITY-BASELINE')['resolution_status'] in ('wont_fix', 'retired')` |
| GTKB-GOV-DA-ENFORCEMENT dispositioned | manual: status updated |
| GTKB-GOV-004 reframed | manual: title clarified |
| Change_reason cites this proposal | manual: per-WI change_reason references this bridge ID |

(No automated test; this is a backlog-data triage operation. Verification is manual.)

## Acceptance Criteria

- IP-1..IP-3 dispositions applied.
- Per-WI change_reason cites this bridge.
- Both preflights PASS.

## Risks / Rollback

- Risk: GTKB-GOV-DA-ENFORCEMENT may have unrecorded prior owner intent. Mitigation: search Deliberation Archive before retiring; if found, surface to owner.
- Rollback: revert each WI's resolution_status (single MemBase update per WI).

## Recommended Commit Type

`chore` - backlog data hygiene. No code change.
