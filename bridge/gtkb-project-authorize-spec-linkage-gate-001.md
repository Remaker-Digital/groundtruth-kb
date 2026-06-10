NEW

# Implementation Proposal - Project Authorize Spec-Linkage Gate (WI-3312)

bridge_kind: prime_proposal
Document: gtkb-project-authorize-spec-linkage-gate
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3312

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_cli_projects.py", "groundtruth.db"]

This NEW proposal implements `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (v1, specified, landed 2026-05-14) as the first mechanical gate of the spec→project→work item→bridge enforcement chain established by owner directive 2026-05-14 (S350+). Project authorization `PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN` is `active` and includes WI-3312 in `included_work_item_ids`.

The proposal voluntarily includes the new `Project Authorization` / `Project` / `Work Item` metadata lines per `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (sibling WI-3314 is the gate landing; this proposal exercises the format ahead of activation to validate forward-compatibility).

## Claim

`gt projects authorize` and `KnowledgeDB.insert_project_authorization()` must mechanically reject authorization transitions to `status="active"` when `included_spec_ids` is empty. Pre-existing `active` authorizations with empty `included_spec_ids` are grandfathered until their next mutation (which triggers the gate).

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-project-authorize-spec-linkage-gate-001.md`. Targets at `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`, `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`, `E:\GT-KB\groundtruth-kb\tests\test_db.py`, `E:\GT-KB\groundtruth-kb\tests\test_cli_projects.py`, `E:\GT-KB\groundtruth.db`. No `applications/` paths. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - source spec for this WI; v1 specified 2026-05-14; this proposal is its mechanical implementation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance contract that this gate amends.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope contract; gate operates within its schema.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior; gate does not bypass.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root paths only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in Specification-Derived Verification Plan section.
- `GOV-STANDING-BACKLOG-001` - WI-3312 is a MemBase work_item; not a bulk operation.
- `GOV-ARTIFACT-APPROVAL-001` - no protected narrative artifact mutation in this proposal.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14 establishing the 5-spec governance chain and authorizing this project + WI scope.
- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - prior owner decision establishing the project_authorizations envelope this proposal extends. Predecessor; not in tension with the new spec.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner directive (verbatim) stating the spec→project→work item→bridge chain enforcement requirements. Recorded in `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT`.
- 2026-05-14 UTC, S350+: owner AUQ "Approve full 5-spec batch" answered "Approve all 5 as drafted" - includes GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001.
- 2026-05-14 UTC, S350+: owner AUQ "Bridge dispatch sequencing for the 6 work items" answered "Dispatch WI-3312 + WI-3317 (independent low-priority) in parallel" - explicit authorization to file this proposal NEW now.

No new owner decision required by this proposal. Implementation scope matches the cited spec exactly.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` v1 fully specifies the gate behavior (project authorization cannot reach `active` status without at least one cited approved specification; pre-spec projects grandfathered until next reauthorization). No new requirements introduced.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation is NOT a bulk operation against the standing backlog. CLAUSE-VISIBILITY-BULK-OPS evidence: exactly one work item (WI-3312) is the operative target, and it is already an active member of project `GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001` per project_authorizations row inserted via formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. No work_items insert/update/delete in this proposal beyond the optional stage transition to `implementing`. No spec status mutations. No protected narrative artifact (rule file, canonical-terminology, operating-model, ADR, DCL) edited.

## Bridge INDEX Update Evidence

This NEW is filed at `bridge/gtkb-project-authorize-spec-linkage-gate-001.md` with a new top-of-file `Document:` entry prepended to `bridge/INDEX.md`. No prior INDEX entry deleted or rewritten.

## Proposed Scope

### IP-1: Add empty-included_specs validation to insert_project_authorization()

In `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`, extend `KnowledgeDB.insert_project_authorization()`:

- When `status == "active"` AND (`included_spec_ids is None OR len(included_spec_ids) == 0`), raise `ValueError("Project authorization status='active' requires at least one included_spec_id (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001).")` before any DB write.
- Pre-existing `active` rows with empty `included_spec_ids` are unaffected (no read-side mutation); only NEW insertions or version bumps that set `status="active"` are gated.
- Status `draft` and `revoked` remain spec-linkage-optional.

### IP-2: Surface the validation in the gt CLI

In `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`, the `projects authorize` command must produce a clear, citation-tagged error when the `ValueError` from IP-1 is raised. Specifically: convert the `ValueError` to a `click.UsageError` that cites `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` and suggests `--include-spec SPEC-NNNN`.

### IP-3: Spec status promotion from `specified` to `implemented`

After IP-1 + IP-2 land and tests pass, promote `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` from `specified` to `implemented` via `KnowledgeDB.update_spec()` with `change_reason` citing the post-impl bridge file.

## Specification-Derived Verification Plan

Tests derived from `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` clauses:

| Spec clause | Test |
|---|---|
| "cannot reach active status without citing at least one approved specification" | `test_authorize_active_without_include_spec_raises` (in test_db.py): calls `db.insert_project_authorization(..., status="active", included_spec_ids=None)` and asserts ValueError with citation. |
| Same | `test_authorize_active_with_empty_include_spec_raises` (test_db.py): same as above with `included_spec_ids=[]`. |
| "project records may exist in a draft state without specs" | `test_authorize_draft_without_specs_succeeds` (test_db.py): `status="draft"` with `included_spec_ids=None` → no exception, row created. |
| "the authorization step that allows work items to dispatch to the bridge requires explicit spec linkage" | `test_authorize_active_with_one_spec_succeeds` (test_db.py): positive case, returns row. |
| CLI surface | `test_cli_projects_authorize_missing_specs_fails_with_citation` (test_cli_projects.py): runs `gt projects authorize ...` without `--include-spec`, asserts non-zero exit + error text contains "GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001". |
| Grandfathering | `test_existing_active_authorization_without_specs_remains_active` (test_db.py): pre-insert a row at status=active with empty specs (bypassing the gate via direct SQL fixture), verify get_project_authorizations returns it unchanged. |

Test execution: `python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py -v` per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

Implementation reaches `VERIFIED` only when all 6 tests PASS and IP-3 spec promotion is recorded.

## Acceptance Criteria

- IP-1 validation present; 5 test_db.py tests PASS.
- IP-2 CLI surface present; 1 test_cli_projects.py test PASSES.
- IP-3 spec status promotion recorded; `db.get_spec('GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001')['status'] == 'implemented'`.
- No regression in existing test_db.py / test_cli_projects.py suites.
- Bridge applicability preflight and clause preflight both PASS for this bridge ID.

## Risks / Rollback

- Risk: existing CI scripts or scaffold templates that call `gt projects authorize` without `--include-spec` would break. Mitigation: grep CI for invocations in same PR; add `--include-spec` where missing. Grandfathering rule prevents existing data corruption.
- Risk: scaffold-generated project authorizations in adopter projects might lack specs. Mitigation: scaffolds out of scope for this WI; tracked separately if discovered.
- Rollback: revert the ValueError in IP-1 (single-function-scope change); CLI error mapping in IP-2 is mechanical to revert.

## Recommended Commit Type

`feat` - adds new mechanical governance gate and CLI behavior. ~50 LOC net addition (validation + CLI surface + tests).
