NEW

# Implementation Proposal - Bridge Compliance Gate Work Item Project Membership Check (WI-3315)

bridge_kind: implementation_proposal
Document: gtkb-bridge-compliance-wi-project-membership
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3315
Depends on: WI-3314 (bridge-compliance-gate must already enforce `Work Item:` metadata line before this membership check can read it)

target_paths: [".claude/hooks/bridge-compliance-gate.py", "tests/hooks/test_bridge_compliance_gate.py", "platform_tests/hooks/test_bridge_compliance_gate.py"]

This NEW proposal implements `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` (v1 specified 2026-05-14, Soft variant). Work items may exist unattached in MemBase (triage state), but bridge proposal Writes citing a `Work Item: WI-NNNN` line are rejected if the WI is not an active member of an approved, non-expired project authorization.

## Claim

Extend the bridge-compliance-gate (already enforcing `Work Item:` metadata presence after WI-3314 lands) with a live MemBase lookup: parse the `Work Item:` value, query `current_project_work_item_memberships` joined to `current_project_authorizations` (status=`active`, not expired), and block when no membership row links the WI to an active authorization.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-bridge-compliance-wi-project-membership-001.md`. Targets in `.claude/hooks/`, `tests/hooks/`, `platform_tests/hooks/`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - source spec; v1 specified 2026-05-14; Soft variant.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - sibling spec (WI-3314); provides the metadata line this check reads.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3315 is a tracked work_item.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive establishing the 5-spec chain and selecting Soft variant for this spec via AUQ.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved 5-spec batch including DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 with Soft variant.
- 2026-05-14 UTC, S350+: owner directive "Please proceed with parallel implementation proposals for as many backlog items as possible" - explicit authorization to file this NEW.

No new owner decision required. Soft-variant selection already recorded in DELIB.

## Requirement Sufficiency

Existing requirements sufficient. DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 v1 fully specifies the Soft variant (triage WIs permitted in MemBase; bridge dispatch blocked without project membership).

## Clause Scope Clarification (Not a Bulk Operation)

NOT a bulk operation. One operative work item (WI-3315), an active member of project GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (membership check) + IP-2 (tests) scoped to single thread file.

## Bridge INDEX Update Evidence

NEW filed at `bridge/gtkb-bridge-compliance-wi-project-membership-001.md`; new top-of-file entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Add WI-project membership check to bridge-compliance-gate.py

Build on WI-3314's metadata-presence detection. When `Work Item: WI-NNNN` line is present (passed WI-3314's check):

1. Parse the WI ID from the metadata line.
2. Open `groundtruth.db` read-only via `sqlite3.connect("groundtruth.db", uri=False)`.
3. Query: `SELECT 1 FROM current_project_work_item_memberships m JOIN current_project_authorizations a ON m.project_id = a.project_id WHERE m.work_item_id = ? AND a.status = 'active' AND (a.expires_at IS NULL OR a.expires_at > datetime('now'))`.
4. If no row, emit `{"decision": "block", "reason": "BLOCKED (DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP): cited Work Item <WI-NNNN> is not an active member of an approved project authorization. Either attach it to an approved project or move to a non-implementation bridge_kind."}`.
5. Triage-state WIs (no membership) remain valid in MemBase but cannot dispatch to bridge (CLAUSE-TRIAGE-WI-PERMITTED).
6. Verdict files and non-implementation `bridge_kind` are already exempt from WI-3314's check and remain exempt here.

### IP-2: Spec status promotion

Promote `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` from `specified` to `implemented` after IP-1 lands and tests pass.

## Specification-Derived Verification Plan

Tests in `tests/hooks/test_bridge_compliance_gate.py`:

| Clause | Test |
|---|---|
| BRIDGE-WI-PROJECT-MEMBERSHIP | `test_bridge_proposal_wi_not_in_any_project_blocked` (fixture: WI exists, no membership) |
| BRIDGE-WI-PROJECT-MEMBERSHIP | `test_bridge_proposal_wi_member_of_inactive_authorization_blocked` (fixture: WI member of project with status=revoked authorization) |
| BRIDGE-WI-PROJECT-MEMBERSHIP | `test_bridge_proposal_wi_member_of_expired_authorization_blocked` (fixture: expires_at in past) |
| BRIDGE-WI-PROJECT-MEMBERSHIP | `test_bridge_proposal_wi_active_membership_passes` (fixture: WI member of project with active, non-expired authorization) |
| TRIAGE-WI-PERMITTED | `test_wi_exists_in_membase_without_project_membership_no_bridge_check_path` (verify db row creation path doesn't trigger this check) |
| Composition with WI-3314 | `test_bridge_proposal_no_work_item_metadata_blocked_by_wi3314_not_this_check` (regression: WI-3314 gate fires first when Work Item line is missing) |

Test execution: `python -m pytest tests/hooks/test_bridge_compliance_gate.py platform_tests/hooks/test_bridge_compliance_gate.py -v`.

## Acceptance Criteria

- IP-1 membership check landed; 6 tests PASS.
- IP-2 spec promotion recorded.
- WI-3314 must be GO'd / VERIFIED first (this WI's implementation reads its metadata line). Codex may review this proposal design in parallel; implementation gates on WI-3314 GO.
- No regression in existing test_bridge_compliance_gate.py.
- Both preflights PASS for this bridge ID.

## Risks / Rollback

- Risk: SQLite read from a hook adds latency on every bridge proposal Write. Mitigation: cached connection or fast read-only open; benchmark in IP-2 tests.
- Risk: `current_project_work_item_memberships` view query semantics differ from raw table. Mitigation: use the view (already mentioned in canonical-terminology glossary as the live-state surface).
- Rollback: revert IP-1 (single-function-scope change).

## Recommended Commit Type

`feat` - adds new mechanical governance gate. ~40 LOC net + tests.
