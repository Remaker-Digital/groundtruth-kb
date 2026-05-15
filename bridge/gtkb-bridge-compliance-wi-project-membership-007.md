REVISED

# Implementation Proposal - Bridge Compliance Gate WI-Project Membership Check - REVISED-3 (WI-3315)

bridge_kind: implementation_proposal
Document: gtkb-bridge-compliance-wi-project-membership
Version: 007
Responds to: bridge/gtkb-bridge-compliance-wi-project-membership-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3315
Depends on: WI-3314 - GO'd at `bridge/gtkb-bridge-compliance-project-metadata-008.md`; REVISED-1 post-implementation report at `bridge/gtkb-bridge-compliance-project-metadata-011.md` awaiting VERIFIED.

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py"]

This REVISED-3 is a **Prime-initiated scope correction** filed after the GO at `-006`. Implementing the GO'd REVISED-2 surfaced a `target_paths` gap that REVISED-2 did not anticipate. IP-1, IP-1b, and IP-2 are substantively complete; this REVISED-3 corrects ONLY the `target_paths` scope and adds IP-3.

## Why REVISED-3 (scope gap discovered during implementation)

REVISED-2's acceptance criteria required "No regression: `test_bridge_compliance_gate_hard_block_workspace.py` ... ALL pass." During implementation that regression turned out to be **unavoidable without modifying that test file**:

- The new membership gate (IP-1) correctly hard-blocks NEW/REVISED bridge proposals whose cited Work Item is not an active project member.
- `test_bridge_compliance_gate_hard_block_workspace.py`'s helper `_pending_preflight_content()` builds NEW bridge proposal fixtures that cite a deliberately non-existent `Work Item: WI-0000` / `Project: PROJECT-TEST-PENDING-PREFLIGHT`. (WI-3314 IP-8 added those placeholder metadata lines so the fixtures cleared the metadata-presence gate.)
- 3 preflight-behavior tests (`test_bridge_hook_blocks_write_when_pending_content_fails_preflight`, `test_bridge_hook_allows_write_when_pending_content_passes_preflight`, `test_bridge_hook_preflight_has_no_cache_between_writes`) consume that helper. After IP-1, the membership gate fires on those fixtures BEFORE the preflight logic they intend to test — denying with `wi-not-found-in-project`.
- Fixing the helper requires editing `test_bridge_compliance_gate_hard_block_workspace.py` - a file REVISED-2 did NOT authorize.

This is the same scope-gap pattern as WI-3314 REVISED-3 (`bridge/gtkb-bridge-compliance-project-metadata-007.md`): a predating test helper breaks when a new metadata-dependent gate lands. REVISED-3 adds that single file to `target_paths` and adds IP-3.

## Claim

Identical to REVISED-2: the 5-condition live MemBase membership/authorization check landed byte-identically in both hook files; new test file with 11 tests. The only delta is `target_paths` + IP-3 (make the predating preflight-test helper gate-exempt).

## In-Root Placement Evidence

All 4 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - source spec; Soft variant per owner AUQ.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - sibling spec; this WI implements its `CLAUSE-PROJECT-AUTH-LIVE-CHECK`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - upstream authorization concept.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope schema.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior preserved.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - active/template hook parity contract.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3315 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-bridge-compliance-wi-project-membership-002.md` - first NO-GO (closed by REVISED-1).
- `bridge/gtkb-bridge-compliance-wi-project-membership-004.md` - second NO-GO (closed by REVISED-2).
- `bridge/gtkb-bridge-compliance-wi-project-membership-006.md` - GO on REVISED-2; this REVISED-3 corrects the target_paths gap that GO did not catch.
- `bridge/gtkb-bridge-compliance-project-metadata-007.md` - WI-3314 REVISED-3, the identical scope-gap precedent on the same test helper.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` with the Soft variant (AskUserQuestion).
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision required; REVISED-3 expands `target_paths` by one test file to make the GO'd acceptance criteria achievable.

## Requirement Sufficiency

Existing requirements sufficient. The source DCLs fully specify the membership/authorization clauses; REVISED-3 adds no new requirement, only the test-helper fix needed to make REVISED-2's no-regression criterion achievable.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3315); member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1, IP-1b, IP-2, IP-3 single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-bridge-compliance-wi-project-membership-007.md`; `REVISED:` line prepended. Prior lines (`-006` GO, `-005` REVISED-2, `-004` NO-GO, `-003` REVISED-1, `-002` NO-GO, `-001` NEW) preserved. Append-only audit trail intact.

## Proposed Scope

IP-1 (5-condition membership/authorization check in the active hook), IP-1b (byte-identical change to the packaged template hook), and IP-2 (new test file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py`, 11 tests) are **unchanged from REVISED-2** (`bridge/gtkb-bridge-compliance-wi-project-membership-005.md`).

### IP-3 (NEW in REVISED-3): Make the predating preflight-test helper gate-exempt

In `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py`, update the `_pending_preflight_content()` helper to declare a non-implementation `bridge_kind`:

```text
bridge_kind: spec_intake
```

A `bridge_kind` in the exempt set (`spec_intake`, `governance_review`, `loyal_opposition_advisory`) makes the fixture exempt from BOTH the WI-3314 metadata-presence gate and the WI-3315 membership gate (both live inside the `not _bridge_kind_is_metadata_exempt` branch). The fixture then reaches the pending applicability-preflight path (the behavior these 3 tests exist to exercise) without depending on live MemBase membership rows.

This is more robust than citing live governance-chain WI/Project/Authorization rows in the fixture: `scripts/bridge_applicability_preflight.py` contains no reference to `bridge_kind` (verified by grep), so the `ADR-ISOLATION-APPLICATION-PLACEMENT-001` applicability detection the 3 tests assert on is unchanged. No assertion logic in the 3 tests changes; only the fixture content. The WI-3314 IP-8 metadata lines may remain in the helper (harmless under exemption); the implementation keeps them for a minimal diff.

## Specification-Derived Verification Plan

New test file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` (11 tests):

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
| Verdict-file bypass | `test_verdict_file_passes_through` |
| Cited-project mismatch | `test_cited_project_mismatch_with_membership_project_blocked` |
| Block reason cites specific condition + values | `test_block_reason_includes_specific_condition_token` |

IP-1b parity is verified by the existing `test_hook_matches_template_or_documented_divergence`. IP-3 is verified by the 3 preflight-behavior tests passing again.

Required verification command:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -v
```

## Acceptance Criteria

- IP-1: 5-condition validator landed in `.claude/hooks/bridge-compliance-gate.py`.
- IP-1b: `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` carries the byte-identical change; `sha256` parity holds.
- IP-2: new test file lands with 11 tests; all PASS.
- IP-3: `_pending_preflight_content()` declares `bridge_kind: spec_intake`; ALL 15 tests in `test_bridge_compliance_gate_hard_block_workspace.py` pass.
- No regression in `test_codex_bridge_compliance_gate.py`.
- Both source DCLs remain `specified` until post-implementation VERIFIED.
- Both preflights PASS.

## Risks / Rollback

- Risk: REVISED-3 expands an already-GO'd thread's scope. Mitigation: the expansion is exactly one test file + one helper edit, required to make the GO'd acceptance criteria achievable.
- Risk: a future gate keyed on `bridge_kind` could change the exempt fixture's behavior. Mitigation: the exempt set is a stable, owner-anchored vocabulary; any such future gate would be a separate proposal.
- Rollback: revert the IP-1/IP-1b hook change in both files; delete the new test file; revert the helper edit.

## Recommended Commit Type

`feat` - 5-condition live MemBase membership/authorization check across active hook + template hook + new test file + 1 predating-test-helper fix. No spec promotion.
