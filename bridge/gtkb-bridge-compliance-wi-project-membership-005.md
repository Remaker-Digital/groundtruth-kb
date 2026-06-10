REVISED

# Implementation Proposal - Bridge Compliance Gate WI-Project Membership Check - REVISED-2 (WI-3315)

bridge_kind: prime_proposal
Document: gtkb-bridge-compliance-wi-project-membership
Version: 005
Responds to: bridge/gtkb-bridge-compliance-wi-project-membership-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3315
Depends on: WI-3314 - GO'd at `bridge/gtkb-bridge-compliance-project-metadata-008.md` (REVISED-3); post-implementation report filed at `bridge/gtkb-bridge-compliance-project-metadata-009.md` awaiting VERIFIED. WI-3314 landed the metadata-presence detection (CLAUSE-PROJECT-METADATA-PRESENT) this WI builds on.

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py"]

This REVISED-2 addresses the NO-GO at `bridge/gtkb-bridge-compliance-wi-project-membership-004.md`:

- **F1 (P1/blocking)** - `target_paths` authorized only the active hook, but the existing parity regression test (`test_hook_matches_template_or_documented_divergence` in `test_bridge_compliance_gate_hard_block_workspace.py`) requires the packaged template hook to stay byte-identical -> **closed** by adding `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` to `target_paths` and adding IP-1b requiring the byte-identical change.
- **F2 (P2)** - the verification command named only the new membership test file, omitting the no-regression surfaces the proposal itself cited -> **closed** by expanding the required verification command to run the parity suite and the Codex-side regression suite.
- **Required-revision item 4** - the stale `Depends on:` reference to `bridge/gtkb-bridge-compliance-project-metadata-003.md` -> **closed**: the `Depends on:` line above now references WI-3314's current state (GO at `-008`, post-impl report at `-009`).

IP-1 (validation semantics), IP-2 (new test file), and IP-3 (no spec promotion) carry forward from REVISED-1 unchanged except where noted.

## Claim

Extend the bridge-compliance-gate (after WI-3314's metadata-presence detection) with a live MemBase 5-condition check on every Write of an implementation bridge proposal citing a `Work Item:`. The check aligns byte-for-byte with the existing `implementation_authorization.py` validator semantics so the gate and the implementation-start gate agree. The behavior change lands byte-identically in BOTH the active hook and the packaged template hook so hook-template parity holds.

## In-Root Placement Evidence

All 3 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - source spec; Soft variant per owner AUQ.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - sibling spec; this WI also implements its `CLAUSE-PROJECT-AUTH-LIVE-CHECK` per WI-3314 handoff.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior preserved.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - active/template hook parity contract (governs IP-1b).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3315 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-bridge-compliance-wi-project-membership-002.md` - first NO-GO (closed by REVISED-1).
- `bridge/gtkb-bridge-compliance-wi-project-membership-004.md` - second NO-GO (closed by this REVISED-2).
- `bridge/gtkb-bridge-compliance-project-metadata-008.md` - sibling WI-3314 REVISED-3 GO; the metadata-presence slice this WI depends on.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` with the Soft variant (AskUserQuestion).
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision required; this REVISED-2 is a mechanical scope correction.

## Requirement Sufficiency

Existing requirements sufficient. The F1 fix aligns the gate with `implementation_authorization.py`'s established 5-condition semantics - no new validation invented. IP-1b adds nothing new; it preserves the existing hook-template parity contract.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3315); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (5-condition validator) + IP-1b (template parity) + IP-2 (tests) + IP-3 (no promotion) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-bridge-compliance-wi-project-membership-005.md`; `REVISED:` line prepended. Prior lines (`-004` NO-GO, `-003` REVISED-1, `-002` NO-GO, `-001` NEW) preserved. Append-only audit trail intact.

## Proposed Scope

### IP-1: 5-condition membership + authorization check in the active hook

In `.claude/hooks/bridge-compliance-gate.py`, when `Work Item: WI-NNNN`, `Project: <id>`, and `Project Authorization: PAUTH-...` are present on a bridge proposal Write, perform a single SQL query aligning with `implementation_authorization.py`:

```sql
SELECT 1
FROM current_project_work_item_memberships m
JOIN current_project_authorizations a ON m.project_id = a.project_id
WHERE m.work_item_id           = :cited_wi
  AND m.project_id             = :cited_project
  AND m.status                 = 'active'
  AND a.id                     = :cited_authorization
  AND a.status                 = 'active'
  AND (a.expires_at IS NULL OR a.expires_at > datetime('now'))
```

Post-SQL Python: load `a.included_work_item_ids` / `a.excluded_work_item_ids` (JSON); fail closed if `cited_wi` is excluded; if `included_work_item_ids` is non-empty require membership. On failure emit a structured block reason naming the specific failed condition from the fixed list: `wi-not-found-in-project`, `wi-membership-inactive`, `authorization-not-found`, `authorization-inactive`, `authorization-expired`, `wi-excluded-from-authorization`, `wi-not-included-by-authorization`. Verdict files and non-implementation `bridge_kind` proposals remain exempt.

### IP-1b (NEW in REVISED-2): Byte-identical change to the packaged template hook

Apply the IP-1 behavior change to `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` byte-identically with the active hook. After implementation, `sha256(.claude/hooks/bridge-compliance-gate.py) == sha256(groundtruth-kb/templates/hooks/bridge-compliance-gate.py)`. This preserves `ADR-CODEX-HOOK-PARITY-FALLBACK-001` and the existing `test_hook_matches_template_or_documented_divergence` parity test.

### IP-2: Tests (new file)

New file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` (explicitly NEW). 11 tests per the verification plan below.

### IP-3: Deferred spec promotion (no promotion at proposal time)

`DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` BOTH remain `specified` at proposal-filing time. Promotion happens at post-implementation VERIFIED.

## Specification-Derived Verification Plan

New test file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`:

| Failed condition / scenario | Test |
|---|---|
| `wi-not-found-in-project` | `test_wi_not_in_any_project_blocked` |
| `wi-membership-inactive` | `test_wi_membership_inactive_blocked` |
| `authorization-not-found` | `test_wrong_project_authorization_blocked` |
| `authorization-inactive` | `test_inactive_authorization_blocked` |
| `authorization-expired` | `test_expired_authorization_blocked` |
| `wi-excluded-from-authorization` | `test_excluded_wi_blocked` |
| `wi-not-included-by-authorization` | `test_wi_not_in_included_list_blocked` |
| Active happy path | `test_active_membership_active_auth_passes` |
| Verdict-file fast path bypass | `test_verdict_file_passes_through` |
| Wrong-project metadata cross-check | `test_cited_project_mismatch_with_membership_project_blocked` |
| Block reason cites specific failing condition | `test_block_reason_includes_specific_condition_token` |

IP-1b parity is verified by the existing `test_hook_matches_template_or_documented_divergence` test inside `test_bridge_compliance_gate_hard_block_workspace.py`.

Required verification command (F2 - now includes the no-regression surfaces):

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v
```

## Acceptance Criteria

- IP-1: 5-condition validator landed in `.claude/hooks/bridge-compliance-gate.py`.
- IP-1b: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` carries the byte-identical change; `sha256` parity holds; `test_hook_matches_template_or_documented_divergence` passes.
- IP-2: new test file lands with 11 tests; all PASS.
- IP-3: BOTH source DCLs remain `specified` at proposal time.
- No regression: `test_bridge_compliance_gate_hard_block_workspace.py` and `test_codex_bridge_compliance_gate.py` ALL pass under the expanded verification command.
- Both preflights PASS.

## Risks / Rollback

- Risk: hook-template drift if only one file is edited. Mitigation: IP-1b mandates byte-identical change; the parity test in the verification command fails closed if they diverge.
- Risk: SQL semantic drift between this gate and `implementation_authorization.py`. Mitigation: gate adopts the same validator query shape; equivalence covered by the membership test fixtures.
- Risk: `excluded_work_item_ids` semantics are stricter than the implementation-start gate. Mitigation: spot-check existing `project_authorizations` rows for excluded-WI usage during implementation; if non-zero, gate the excluded branch behind a flag pending owner review.
- Rollback: revert the IP-1/IP-1b single-function-scope change in both hook files; delete the new test file.

## Recommended Commit Type

`feat` - adds a 5-condition live MemBase check to the bridge-compliance-gate (active + template hooks, byte-identical), consolidating two DCL clauses' enforcement. No spec promotion in this commit.
