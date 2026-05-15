NEW

# Implementation Report - Bridge Compliance Gate WI-Project Membership Check (WI-3315)

bridge_kind: implementation_proposal
Document: gtkb-bridge-compliance-wi-project-membership
Version: 009
Responds to: bridge/gtkb-bridge-compliance-wi-project-membership-008.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3315

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py"]

This is the post-implementation report for WI-3315. REVISED-3 was GO'd at `-008`; IP-1, IP-1b, IP-2, and IP-3 are implemented and all verification commands pass.

## Claim

The live MemBase WI/project membership + authorization gate for `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/CLAUSE-PROJECT-AUTH-LIVE-CHECK` is implemented. The bridge-compliance-gate now hard-blocks NEW/REVISED implementation proposals whose cited Work Item is not an active member of the cited Project, or whose cited Project Authorization is missing, inactive, expired, project-mismatched, or excludes the Work Item. Both source DCLs remain `specified` (no promotion in this slice).

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
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3315 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-bridge-compliance-wi-project-membership-006.md` - GO on REVISED-2.
- `bridge/gtkb-bridge-compliance-wi-project-membership-008.md` - GO on REVISED-3.
- `bridge/gtkb-bridge-compliance-project-metadata-007.md` - WI-3314 REVISED-3, the sibling scope-gap precedent on the same test helper.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch including `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` with the Soft variant (AskUserQuestion).
- 2026-05-15 UTC, S350+: owner directive "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED."

No new owner decision required; the work is within the GO'd REVISED-3 `target_paths`.

## Clause Scope Clarification (Not a Bulk Operation)

WI-3315 is not a bulk operation. It is a single work item, a member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per the owner-approved `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. The review-packet inventory is the single IP-1/IP-1b/IP-2/IP-3 thread documented in this report. No backlog-wide sweep or multi-work-item mutation is involved; the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` evidence requirement is satisfied by this not-a-bulk-operation declaration plus the cited formal-artifact-approval packet.

## WI-3314 Baseline (GO Condition 6)

This WI's hook change shares `.claude/hooks/bridge-compliance-gate.py` with WI-3314. At the time of filing, live `bridge/INDEX.md` records WI-3314 (`gtkb-bridge-compliance-project-metadata`) latest status `NO-GO` at `bridge/gtkb-bridge-compliance-project-metadata-012.md`. That NO-GO was caused by this WI's membership gate landing in the shared hook and regressing the 3 `_pending_preflight_content()` preflight tests. IP-3 (below) resolves that regression; once this report is VERIFIED, WI-3314's report can be re-filed because the 3 tests pass again.

## Implemented Changes

IP-1: Active hook `.claude/hooks/bridge-compliance-gate.py` - added the 5-condition live MemBase membership/authorization check (`import sqlite3`; constants `PROJECT_AUTHORIZATION_VALUE_RE`, `PROJECT_VALUE_RE`, `WORK_ITEM_VALUE_RE`; helpers `_extract_project_metadata`, `_parse_json_id_list`, `_wi_project_membership_gap`; new check in `_deny_reason_for_content` inside the NEW/REVISED metadata branch). The check fails open on any sqlite/OS error (read-only DB connection, `timeout=5`).

IP-1b: Template hook `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` - byte-identical to the active hook.

IP-2: New test file `platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py` - 11 tests with an isolated fixture `groundtruth.db`.

IP-3: `platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py` - `_pending_preflight_content()` declares `bridge_kind: spec_intake`, making the fixture exempt from both the metadata-presence gate and the membership gate so the 3 preflight-behavior tests reach the pending-preflight path. No assertion logic changed.

## Specification-Derived Verification

Spec-to-test mapping:

| Clause / behavior | Tests |
|---|---|
| `CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP` / `CLAUSE-PROJECT-AUTH-LIVE-CHECK` - wi-not-found | `test_wi_not_in_any_project_blocked`, `test_cited_project_mismatch_with_membership_project_blocked` |
| - wi-membership-inactive | `test_wi_membership_inactive_blocked` |
| - authorization-not-found | `test_wrong_project_authorization_blocked` |
| - authorization-inactive | `test_inactive_authorization_blocked` |
| - authorization-expired | `test_expired_authorization_blocked` |
| - wi-excluded-from-authorization | `test_excluded_wi_blocked` |
| - wi-not-included-by-authorization | `test_wi_not_in_included_list_blocked` |
| - active happy path | `test_active_membership_active_auth_passes` |
| - verdict-file bypass | `test_verdict_file_passes_through` |
| - block reason cites condition + values | `test_block_reason_includes_specific_condition_token` |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - hook/template parity (IP-1b) | `test_hook_matches_template_or_documented_divergence` |
| IP-3 - fixture exemption restores preflight tests | `test_bridge_hook_blocks_write_when_pending_content_fails_preflight`, `test_bridge_hook_allows_write_when_pending_content_passes_preflight`, `test_bridge_hook_preflight_has_no_cache_between_writes` |

Command executed and observed result:

```text
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py platform_tests/scripts/test_codex_bridge_compliance_gate.py -q
```

Result: **33 passed in 58.53s** (11 wi_project_membership + 15 hard_block_workspace + 7 codex_bridge_compliance_gate). Hook-template `sha256` parity confirmed by `test_hook_matches_template_or_documented_divergence` within that run.

## Acceptance Criteria Check

- IP-1: 5-condition validator landed in the active hook. PASS.
- IP-1b: template hook byte-identical; parity test passes. PASS.
- IP-2: new test file with 11 tests; all PASS. PASS.
- IP-3: `_pending_preflight_content()` declares `bridge_kind: spec_intake`; ALL 15 `test_bridge_compliance_gate_hard_block_workspace.py` tests pass. PASS.
- No regression in `test_codex_bridge_compliance_gate.py` (7 passed). PASS.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` and `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` remain `specified`. PASS.
- Both preflights PASS (recorded in the REVISED-3 GO at `-008`).

## Risks / Rollback

- Risk: the membership gate opens the live `groundtruth.db` on bridge-proposal writes. Mitigation: read-only connection, `timeout=5`, fail-open on any sqlite/OS error; query measured at 0.8 ms; WAL journal mode (readers do not block on writers).
- Rollback: revert the IP-1/IP-1b hook change in both files; delete the new test file; revert the IP-3 helper edit.

## Recommended Commit Type

`feat` - new mechanical governance gate (5-condition live MemBase membership/authorization check) across active hook + template hook + new test file + 1 predating-test-helper fix. No spec status promotion.
