NEW

# Implementation Report - Project Authorize Spec-Linkage Gate (WI-3312)

bridge_kind: implementation_proposal
Document: gtkb-project-authorize-spec-linkage-gate
Version: 007
Responds to: bridge/gtkb-project-authorize-spec-linkage-gate-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3312

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_cli_projects.py", "groundtruth.db"]

This is the post-implementation report for WI-3312. REVISED-2 was GO'd at `-006`; IP-1 through IP-4 are implemented and the verification command passes.

## Claim

`KnowledgeDB.insert_project_authorization()` rejects any version reaching `status="active"` unless at least one `included_spec_ids` value resolves via `db.get_spec()` to a `specifications`-table row whose lifecycle `status` is in `{specified, implemented, verified}`. No `type` allowlist is applied. The service layer raises a typed `ProjectAuthorizationSpecLinkageError`; the CLI converts it to `click.UsageError`. `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains `specified` (no promotion).

## In-Root Placement Evidence

All 6 target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. (`groundtruth.db` was authorized but not mutated — no migration or data change was required.)

## Specification Links

- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - source spec; remains `specified`.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope contract.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - preserved.
- `GOV-08` - KB is truth (governs the resolution-via-get_spec semantics).
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3312 tracked.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14.
- `bridge/gtkb-project-authorize-spec-linkage-gate-002.md` - first NO-GO (list-cardinality defect).
- `bridge/gtkb-project-authorize-spec-linkage-gate-004.md` - second NO-GO (type allowlist excluded live SPEC rows).
- `bridge/gtkb-project-authorize-spec-linkage-gate-006.md` - GO on REVISED-2.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the 5-spec batch (AskUserQuestion).
- 2026-05-15 UTC, S350+: owner directives "Continue your focus on getting WI-3314, WI-3315, WI-3312, WI-3313 to VERIFIED" and "Proceed with WI-3312 and WI-3313."

No new owner decision required; the work is within the GO'd `target_paths`.

## Clause Scope Clarification (Not a Bulk Operation)

WI-3312 is not a bulk operation. It is a single work item, a member of `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per the owner-approved `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. The review-packet inventory is the single IP-1..IP-4 thread documented in this report. No backlog-wide sweep or multi-work-item mutation is involved; the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` requirement is satisfied by this not-a-bulk-operation declaration plus the cited formal-artifact-approval packet.

## Implemented Changes

IP-1: `groundtruth-kb/src/groundtruth_kb/db.py` - added `_validate_active_authorization_specs()`, called from `insert_project_authorization()` when `status == "active"`. The validator requires at least one `included_spec_id` that resolves via `get_spec()` to a row with lifecycle status in `{specified, implemented, verified}`. **No `type` filter is applied** (GO Condition 1) — table membership is the "is a specification" predicate. Because `update_project_authorization()` delegates to `insert_project_authorization()`, both the initial-insert and version-bump paths are covered.

IP-2: `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` - added `ProjectAuthorizationSpecLinkageError(ProjectLifecycleError)`. `authorize_project()` inspects the caught `ValueError`; when the message cites `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` it re-raises the typed subclass, otherwise a generic `ProjectLifecycleError`. `groundtruth-kb/src/groundtruth_kb/cli.py` - `projects_authorize` catches `ProjectAuthorizationSpecLinkageError` first and converts it to `click.UsageError` (exit 2); all other `ProjectLifecycleError` shapes still map to `click.ClickException` (exit 1).

IP-3: tests in `groundtruth-kb/tests/test_db.py` (new `TestProjectAuthorizationSpecLinkage` class, 11 tests) and `groundtruth-kb/tests/test_cli_projects.py` (new file, 2 tests).

IP-4: `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains `specified` — no promotion in this slice (GO Condition 4).

## Specification-Derived Verification

Spec-to-test mapping (`GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`):

| Behavior | Test |
|---|---|
| Active + no spec ids -> blocked | `test_authorize_active_with_no_spec_ids_raises` |
| Active + empty list -> blocked | `test_authorize_active_with_empty_spec_list_raises` |
| Active + unknown spec id -> blocked | `test_authorize_active_with_unknown_spec_id_raises` |
| Active + retired spec -> blocked | `test_authorize_active_with_retired_spec_raises` |
| Active + `type='specification'` row -> passes | `test_authorize_active_with_specification_type_spec_succeeds` |
| Active + `type='requirement'` row -> passes | `test_authorize_active_with_requirement_type_spec_succeeds` |
| Active + `type='governance'` row -> passes | `test_authorize_active_with_governance_type_spec_succeeds` |
| Active + valid/invalid mix -> passes | `test_authorize_active_with_valid_and_invalid_mix_succeeds` |
| Draft + no specs -> passes | `test_authorize_draft_with_no_specs_succeeds` |
| Non-active version (active->revoked) -> no validation | `test_authorize_status_only_change_no_spec_validation` |
| Grandfathered active+no-spec row readable | `test_existing_grandfathered_row_read_unchanged` |
| CLI: missing specs -> `click.UsageError` (exit 2) | `test_cli_authorize_missing_specs_emits_usage_error` |
| CLI: error cites the source spec | `test_cli_error_cites_source_spec` |

GO Condition 5 - the three positive type-coverage tests (`specification`, `requirement`, `governance`) all pass, proving the prior false-negative class is closed across heterogeneous `type` values; and the implementation introduces **no `type` filter** of any kind.

Command executed and observed result:

```text
python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py -q
```

Result: **76 passed in 22.55s** (the full `test_db.py` suite including the 11 new `TestProjectAuthorizationSpecLinkage` tests, plus the 2 new `test_cli_projects.py` tests). No regression in the pre-existing `test_db.py` tests.

## Acceptance Criteria Check

- IP-1, IP-2 landed; 13 WI-3312 tests PASS (within the 76-passed run). PASS.
- GO Condition 1 - no replacement `type` allowlist; resolution + lifecycle-status only. PASS.
- GO Condition 2 - typed service exception + CLI `click.UsageError` translation, within target paths. PASS.
- GO Condition 3 - verification command run and reported above. PASS.
- GO Condition 4 / IP-4 - `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains `specified`. PASS.
- GO Condition 5 - three positive type-coverage tests pass; no `type` filter introduced. PASS.
- No regression in the existing `test_db.py` suite. PASS.
- Both preflights PASS (recorded in the REVISED-2 GO at `-006`).

## Risks / Rollback

- Risk: legacy `included_spec_ids` data with stale/retired IDs. Mitigation: grandfathering — only NEW inserts/version-bumps to `status='active'` are gated; reads are unaffected (`test_existing_grandfathered_row_read_unchanged`).
- Rollback: revert `_validate_active_authorization_specs` and its call in `db.py`; revert the typed exception in `lifecycle.py`; revert the CLI translation; delete the new test class and `test_cli_projects.py`.

## Recommended Commit Type

`feat` - new semantic governance gate (active project authorizations must cite an approved specification) across DB validator + typed service exception + CLI surface + tests. No spec status promotion.
