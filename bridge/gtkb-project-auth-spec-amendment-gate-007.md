NEW

# Implementation Report - Project Authorization Spec-Amendment Approval Gate (WI-3313)

bridge_kind: implementation_proposal
Document: gtkb-project-auth-spec-amendment-gate
Version: 007
Responds to: bridge/gtkb-project-auth-spec-amendment-gate-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3313

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/tests/test_db.py", "groundtruth.db"]

This is the post-implementation report for WI-3313. REVISED-2 was GO'd at `-006`; IP-1 through IP-4 are implemented and the verification commands pass.

## Claim

`KnowledgeDB.insert_project_authorization()` rejects any version that mutates `included_spec_ids` or `excluded_spec_ids` (relative to the prior version) unless `change_reason` cites a real, owner-approved, covering formal-artifact-approval packet. Substring text alone is insufficient: the cited packet must resolve inside the project root's `.groundtruth/formal-artifact-approvals/`, exist, parse as JSON, pass `validate_packet()`, carry `approved_by == "owner"`, and textually cover the amendment. `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` remains `specified` (no promotion).

## In-Root Placement Evidence

All 4 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. (`groundtruth.db` was authorized but not mutated.)

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - source spec; remains `specified`.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - sibling spec (WI-3312); initial-authorization linkage.
- `GOV-ARTIFACT-APPROVAL-001` - approval-packet workflow this gate enforces.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract this aligns with.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope contract.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3313 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-project-auth-spec-amendment-gate-002.md` - first NO-GO (substring-only weakness).
- `bridge/gtkb-project-auth-spec-amendment-gate-004.md` - second NO-GO (verification command named a missing test file).
- `bridge/gtkb-project-auth-spec-amendment-gate-006.md` - GO on REVISED-2.
- `bridge/gtkb-project-authorize-spec-linkage-gate-007.md` - sibling WI-3312 report; this WI shares `insert_project_authorization` and `test_db.py` with it.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch (AskUserQuestion).
- 2026-05-15 UTC, S350+: owner directives "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED" and "Proceed with WI-3312 and WI-3313."

No new owner decision required; the work is within the GO'd `target_paths`.

## Clause Scope Clarification (Not a Bulk Operation)

WI-3313 is not a bulk operation. It is a single work item, a member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per the owner-approved `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. The review-packet inventory is the single IP-1..IP-4 thread documented in this report. No backlog-wide sweep or multi-work-item mutation is involved; the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` requirement is satisfied by this not-a-bulk-operation declaration plus the cited formal-artifact-approval packet.

## Implemented Changes

IP-1: `groundtruth-kb/src/groundtruth_kb/db.py` - added `_validate_spec_amendment_approval_packet()`, called from `insert_project_authorization()` when `version > 1` and a prior version exists. It detects any change to the included OR excluded spec sets (per-list comparison, so an included<->excluded move is also detected) and then fails closed unless `change_reason` cites a packet that: (a) is extracted by `parse_packet_path_from_change_reason`; (b) resolves inside `<project_root>/.groundtruth/formal-artifact-approvals/` where `project_root = self.db_path.resolve().parent` (GO Condition 3); (c) exists; (d) parses as a JSON object; (e) passes `validate_packet()`; (f) has `approved_by == "owner"`; (g) covers the amendment per `packet_covers_amendment`. Because `update_project_authorization()` delegates to `insert_project_authorization()`, both mutation paths are covered.

IP-2: `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` - added `parse_packet_path_from_change_reason()` (extracts the relative packet path, normalizes separators) and `packet_covers_amendment()` (returns `(covers, reason)` for whether the packet text mentions the project/authorization id and every added/removed spec id). The DB-layer validator calls these helpers; they are also unit-tested in isolation.

IP-3: tests in `groundtruth-kb/tests/test_db.py` - new `TestProjectAuthorizationSpecAmendment` class (15 tests, all in `test_db.py` per GO Condition 1; no `test_governance_approval_packet.py` created).

IP-4: `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` remains `specified` — no promotion (GO Condition 6).

## Cross-WI Disclosure (WI-3312 test adjustment)

WI-3313 and the just-filed WI-3312 share `insert_project_authorization` and `test_db.py`. WI-3312's test `test_authorize_status_only_change_no_spec_validation` originally created a v2 authorization with `included_spec_ids=None` while v1 carried a spec — which the WI-3313 amendment gate (correctly) treats as a spec removal. Under this WI's GO (`test_db.py` is in `target_paths`), that test was corrected to hold the spec set constant across the v1->v2 status change, so it remains a pure status-only change. The corrected test passes; WI-3312's behavior and report claims are unaffected. This is the same coupled-pair pattern as WI-3314 <-> WI-3315.

## Specification-Derived Verification

Spec-to-test mapping (`DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`):

| Clause / scenario | Test |
|---|---|
| CLAUSE-AMENDMENT-APPROVAL-REQUIRED - no packet path | `test_amend_specs_without_packet_path_raises` |
| - fake/non-existent path | `test_amend_specs_with_fake_path_raises` |
| - outside-root path | `test_amend_specs_with_outside_root_path_raises` |
| - malformed JSON | `test_amend_specs_with_malformed_json_raises` |
| - schema-invalid packet | `test_amend_specs_with_schema_invalid_packet_raises` |
| - non-owner-approved packet | `test_amend_specs_with_non_owner_approved_packet_raises` |
| - packet does not cover project | `test_amend_specs_packet_does_not_cover_project_raises` |
| - packet does not cover added spec | `test_amend_specs_packet_does_not_cover_added_spec_raises` |
| CLAUSE-AMENDMENT-APPROVAL-REQUIRED (positive) | `test_amend_specs_with_covering_packet_succeeds` |
| CLAUSE-BATCH-APPROVAL-PERMITTED | `test_amend_specs_batch_packet_multiple_projects` |
| Initial-version exemption | `test_authorize_initial_version_no_packet_required` |
| Status-only exemption | `test_authorize_status_change_no_packet_required` |
| Excluded-spec mutation also gated | `test_amend_excluded_specs_also_gated` |
| Helper: path parsing | `test_parse_packet_path_from_change_reason_helper` |
| Helper: amendment coverage predicate | `test_packet_covers_amendment_helper` |

GO Condition 2 - the gate fails closed for missing, fake, outside-root, malformed-JSON, schema-invalid, non-owner-approved, and non-covering packets (the 8 blocked-case tests above).

Commands executed and observed results (single run):

```text
python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py platform_tests/hooks/test_formal_artifact_approval_gate.py -q
```

Result: **103 passed in 50.43s** — `groundtruth-kb/tests/test_db.py` (the full suite including the 15 new `TestProjectAuthorizationSpecAmendment` tests and the corrected WI-3312 status-only test), `groundtruth-kb/tests/test_cli_projects.py` (2), and `platform_tests/hooks/test_formal_artifact_approval_gate.py` (12 — GO Condition 5: the shared `approval_packet.py` module change causes no regression in the formal-artifact-approval gate).

## Acceptance Criteria Check

- IP-1, IP-2, IP-3 landed; 15 WI-3313 tests PASS (within the 103-passed run). PASS.
- GO Condition 1 - all WI-3313 tests in `test_db.py`; no `test_governance_approval_packet.py`. PASS.
- GO Condition 2 - fails closed for every invalid-packet class. PASS.
- GO Condition 3 - relative packet paths resolved against `self.db_path.resolve().parent` (the GT-KB project root). PASS.
- GO Condition 4 - `python -m pytest groundtruth-kb/tests/test_db.py` run and reported. PASS.
- GO Condition 5 - `test_formal_artifact_approval_gate.py` run and reported (12 passed; no regression). PASS.
- GO Condition 6 / IP-4 - `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` remains `specified`. PASS.
- Both preflights PASS (recorded in the REVISED-2 GO at `-006`).

## Risks / Rollback

- Risk: legacy amendment commits with substring-only packet citations would fail under the new gate. Mitigation: only NEW inserts/version-bumps with a spec-set change are gated; initial versions and status-only changes are exempt; reads are unaffected.
- Risk: the coverage check could false-negative when a packet covers an amendment with different phrasing. Mitigation: per-spec-id + project/authorization-id substring search; tests document the expected phrasing.
- Rollback: revert `_validate_spec_amendment_approval_packet` and its call in `db.py`; revert the two helpers in `approval_packet.py`; delete the new test class and revert the WI-3312 status-only test adjustment.

## Recommended Commit Type

`feat` - new mechanical governance gate (project-authorization spec amendments require a real owner-approved covering packet) across DB validator + approval-packet helpers + tests. No spec status promotion.
