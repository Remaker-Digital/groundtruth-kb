REVISED

# Implementation Proposal - Bridge Compliance Gate WI-Project Membership Check - REVISED-1 (WI-3315)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-wi-project-membership
Version: 003
Responds to: bridge/gtkb-bridge-compliance-wi-project-membership-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3315
Depends on: WI-3314 (REVISED-1 at `bridge/gtkb-bridge-compliance-project-metadata-003.md`) — the metadata-presence enabling slice

target_paths: [".claude/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-bridge-compliance-wi-project-membership-002.md`:

- **F1 (P1/blocking)** — Membership validation was incomplete; revoked/inactive memberships could pass; cited project/authorization metadata wasn't cross-checked → **closed** by expanding the validation to a 5-condition check (membership status, authorization status, expiration, project-metadata match, included/excluded coverage).
- **F2 (P2)** — Test paths named non-existent files → **closed** with new explicit-new file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`.
- **Scope expansion** — WI-3314 REVISED-1 explicitly deferred its `CLAUSE-PROJECT-AUTH-LIVE-CHECK` to this WI as the natural host for live MemBase lookups. This REVISED-1 accepts that scope: it implements both `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-AUTH-LIVE-CHECK`.

## Claim

Extend the bridge-compliance-gate (after WI-3314 lands metadata-presence) with a live MemBase 5-condition check on every Write of an implementation bridge proposal that cites a `Work Item:`. The check is aligned byte-for-byte with the existing `implementation_authorization.py:336` validator semantics so the gate and the implementation-start gate agree.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - source spec; Soft variant per owner AUQ.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - sibling spec; this REVISED-1 also implements its `CLAUSE-PROJECT-AUTH-LIVE-CHECK` per WI-3314 REVISED-1 handoff.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3315 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-bridge-compliance-wi-project-membership-002.md` - NO-GO under remediation.
- `bridge/gtkb-bridge-compliance-project-metadata-003.md` - sibling WI-3314 REVISED-1 explicitly delegating `CLAUSE-PROJECT-AUTH-LIVE-CHECK` to this thread.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved 5-spec batch including DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001 with Soft variant.
- 2026-05-15 UTC, S350+: owner directive "(a) then (b)" — addressing this REVISED-1 as the natural pair to WI-3314 REVISED-1.

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. F1 fix aligns the gate with `implementation_authorization.py`'s established 5-condition semantics — no new validation invented; the gate adopts the validator that the implementation-start gate already trusts.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3315); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (5-condition validator) + IP-2 (tests) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-bridge-compliance-wi-project-membership-003.md`; `REVISED:` line prepended. Prior `NO-GO: -002` and `NEW: -001` lines preserved.

## Proposed Scope

### IP-1: 5-condition membership + authorization check in bridge-compliance-gate.py

Assumes WI-3314 REVISED-1 has already landed the metadata-presence detection (PROJECT-METADATA-PRESENT clause). When `Work Item: WI-NNNN`, `Project: <id>`, and `Project Authorization: PAUTH-...` are present on a bridge proposal Write, this WI's gate extension performs a single SQL query that aligns with `implementation_authorization.py:336`:

```sql
SELECT 1
FROM current_project_work_item_memberships m
JOIN current_project_authorizations a ON m.project_id = a.project_id
WHERE m.work_item_id           = :cited_wi
  AND m.project_id             = :cited_project        -- match cited Project: line
  AND m.status                 = 'active'              -- F1: membership active
  AND a.id                     = :cited_authorization  -- match cited Project Authorization: line
  AND a.status                 = 'active'              -- F1: auth active
  AND (a.expires_at IS NULL OR a.expires_at > datetime('now'))  -- F1: auth not expired
```

Additionally, in Python (post-SQL):

- Load `a.included_work_item_ids` (JSON list); if `cited_wi` is in `a.excluded_work_item_ids` (when present), fail closed.
- If `included_work_item_ids` is non-empty, require `cited_wi` to be in the list. (If empty/null, the project-membership row already proves coverage.)

On any condition failing, emit a structured block reason citing the **specific** failing condition (so authors can diagnose without re-running):

```json
{
  "decision": "block",
  "reason": "BLOCKED (DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP + DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-AUTH-LIVE-CHECK): <specific-failed-condition>. Cited WI=<wi>, Project=<proj>, Project Authorization=<auth>."
}
```

The "specific-failed-condition" enumerates the gap from a fixed list:
- `wi-not-found-in-project` (membership row missing or wrong project)
- `wi-membership-inactive` (m.status != 'active')
- `authorization-not-found` (a.id mismatch)
- `authorization-inactive` (a.status != 'active')
- `authorization-expired` (a.expires_at <= now)
- `wi-excluded-from-authorization` (in `excluded_work_item_ids`)
- `wi-not-included-by-authorization` (`included_work_item_ids` non-empty and WI absent)

Verdict files (lines starting with GO/NO-GO/VERIFIED) and non-implementation `bridge_kind` proposals (already exempt from WI-3314's PRESENT check) remain exempt here.

### IP-2: Tests (new file)

New file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` (explicitly NEW, not regression of any existing file). Co-located with existing `test_bridge_compliance_gate_hard_block_workspace.py` and the WI-3314 REVISED-1 `test_bridge_compliance_gate_project_metadata.py`.

### IP-3: Deferred spec promotion (no promotion at proposal time)

`DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` BOTH remain `specified` at proposal-filing time. **Promotion happens at post-implementation VERIFIED**, when all 7 specific-condition tests + the metadata-presence sibling tests (from WI-3314) pass. Not before.

## Specification-Derived Verification Plan

New test file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`:

| Failed condition / scenario | Test |
|---|---|
| `wi-not-found-in-project` | `test_wi_not_in_any_project_blocked` |
| `wi-membership-inactive` | `test_wi_membership_inactive_blocked` |
| `authorization-not-found` (cited auth id mismatch) | `test_wrong_project_authorization_blocked` |
| `authorization-inactive` (auth status != active) | `test_inactive_authorization_blocked` |
| `authorization-expired` | `test_expired_authorization_blocked` |
| `wi-excluded-from-authorization` | `test_excluded_wi_blocked` |
| `wi-not-included-by-authorization` | `test_wi_not_in_included_list_blocked` |
| Active happy path | `test_active_membership_active_auth_passes` |
| Metadata-only fast path bypass | `test_verdict_file_passes_through` |
| Wrong-project metadata cross-check | `test_cited_project_mismatch_with_membership_project_blocked` |
| Block reason cites specific failing condition | `test_block_reason_includes_specific_condition_token` |

Test execution: `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py -v`.

## Acceptance Criteria

- IP-1 5-condition validator landed in `.claude/hooks/bridge-compliance-gate.py`.
- IP-2 new test file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` lands with 11 tests; all PASS.
- IP-3: BOTH source DCLs remain `specified` at proposal time. Promotion only on VERIFIED.
- Gate's SQL semantics align byte-for-byte with `scripts/implementation_authorization.py:336` (proved by a unit test that asserts equivalence on shared fixture data).
- WI-3314 REVISED-1 must reach VERIFIED before this WI's tests execute against live state. Implementation can proceed in parallel; verification depends on sibling.
- No regression in existing `test_bridge_compliance_gate_hard_block_workspace.py` or `test_codex_bridge_compliance_gate.py`.
- Both preflights PASS.

## Risks / Rollback

- Risk: WI-3314 REVISED-1 may need further iteration; implementation of this WI is gated on its landing. Mitigation: tests use fixture data; implementation merge is the gate (not test landing).
- Risk: SQL semantic drift between this gate and `implementation_authorization.py:336`. Mitigation: equivalence-on-fixtures test in IP-2.
- Risk: `excluded_work_item_ids` semantics not currently enforced by the implementation-start gate; this hook would be stricter. Mitigation: spot-check 100 existing project_authorizations rows for excluded-WI usage (expected: zero per S350 batch authorizations); if non-zero, gate the IP-1 `excluded_work_item_ids` branch behind a feature flag pending owner review.
- Rollback: revert the IP-1 single-function-scope change; new test file deletion.

## Recommended Commit Type

`feat` - adds 5-condition live MemBase check to the bridge-compliance-gate, consolidating two DCL clauses' enforcement in one place. ~80 LOC hook code + ~180 LOC tests. No spec promotion in this commit.
