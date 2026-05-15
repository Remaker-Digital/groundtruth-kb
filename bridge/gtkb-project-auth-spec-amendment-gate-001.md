NEW

# Implementation Proposal - Project Authorization Spec-Amendment Approval Gate (WI-3313)

bridge_kind: implementation_proposal
Document: gtkb-project-auth-spec-amendment-gate
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3313

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_db.py", "groundtruth.db"]

This NEW proposal implements `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` (v1, specified, landed 2026-05-14). Adding, removing, or substituting a specification on an active project authorization requires explicit owner approval via AskUserQuestion or a batch formal-artifact-approval packet, citation of which must appear in `change_reason`.

## Claim

`KnowledgeDB.insert_project_authorization()` must reject any version bump that mutates `included_spec_ids` or `excluded_spec_ids` (relative to the prior current version) unless `change_reason` references a path to an existing `.groundtruth/formal-artifact-approvals/*.json` packet. Reference detection: case-insensitive substring match for `.groundtruth/formal-artifact-approvals/` AND `.json` in the change_reason string.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-project-auth-spec-amendment-gate-001.md`. Targets at `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`, `E:\GT-KB\groundtruth-kb\tests\test_db.py`, `E:\GT-KB\groundtruth.db`. No `applications/` paths. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` - source spec for this WI; v1 specified 2026-05-14.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - sibling spec (WI-3312); this gate operates on amendments AFTER initial authorization with linked specs.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - parent governance contract.
- `GOV-ARTIFACT-APPROVAL-001` - approval-packet workflow that this gate enforces citation of.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - envelope contract.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - protected behavior; preserved.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` - WI-3313 is a tracked work_item; not a bulk operation.
- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive 2026-05-14 establishing this WI scope.
- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - predecessor establishing the project_authorizations envelope.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the 5-spec batch including DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001.
- 2026-05-14 UTC, S350+: owner AUQ "proceed with parallel implementation proposals for as many backlog items as possible" - explicit authorization to file this NEW now.

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001 v1 fully specifies the gate (any linked_specs mutation requires approval-packet path in change_reason; batch packets allowed).

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one work item (WI-3313) is the operative target. WI is an active member of project GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-project-setup-spec-project-wi-bridge-enforcement.json`. Review-packet inventory: IP-1 (validation) + IP-2 (tests) scoped to a single thread file. No standing-backlog inventory operation.

## Bridge INDEX Update Evidence

This NEW is filed at `bridge/gtkb-project-auth-spec-amendment-gate-001.md` with a new top-of-file `Document:` entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Add linked_specs mutation detection + approval-packet citation check

In `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\db.py`, extend `KnowledgeDB.insert_project_authorization()`:

1. Compute prior version's `included_spec_ids` and `excluded_spec_ids` (via `current_project_authorizations` view) if a prior version exists.
2. Compare to the new version's lists. If either changed:
   - Check `change_reason` for case-insensitive substring `.groundtruth/formal-artifact-approvals/` AND `.json`.
   - If absent, raise `ValueError("Spec amendment on project authorization requires approval-packet citation in change_reason (DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001/CLAUSE-AMENDMENT-APPROVAL-REQUIRED). Cite a packet under .groundtruth/formal-artifact-approvals/.")`.
3. Initial authorization (no prior version): IP-1 does NOT fire; first version's linked_specs is governed by Spec 1 (WI-3312).
4. Status-only changes (active→revoked, etc.) without linked_specs mutation: IP-1 does NOT fire.

### IP-2: Spec status promotion

After IP-1 lands and tests pass, promote `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` from `specified` to `implemented` via `KnowledgeDB.update_spec()` with `change_reason` citing the post-impl bridge file.

## Specification-Derived Verification Plan

Tests derived from `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` clauses:

| Clause | Test |
|---|---|
| CLAUSE-AMENDMENT-APPROVAL-REQUIRED | `test_authorize_amend_specs_without_packet_raises` (test_db.py): create v1 with specs, then call insert_project_authorization v2 with different included_spec_ids and change_reason="reasoned amendment" (no packet path) → ValueError. |
| CLAUSE-AMENDMENT-APPROVAL-REQUIRED | `test_authorize_amend_specs_with_packet_succeeds` (test_db.py): same setup, change_reason includes `.groundtruth/formal-artifact-approvals/test-packet.json` → row created. |
| CLAUSE-BATCH-APPROVAL-PERMITTED | `test_authorize_batch_amend_multiple_projects_one_packet` (test_db.py): two project auth amendments, both citing same packet path in change_reason → both succeed. |
| Initial version exempt | `test_authorize_initial_version_no_packet_required` (test_db.py): first insert_project_authorization for new project → no packet required (only Spec 1's gate applies). |
| Status-only change exempt | `test_authorize_status_change_no_packet_required` (test_db.py): v1 with specs, v2 same specs but status=revoked, no packet → succeeds. |

Test execution: `python -m pytest groundtruth-kb/tests/test_db.py -v` per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Acceptance Criteria

- IP-1 validation present; 5 tests PASS.
- IP-2 spec promotion recorded.
- No regression in existing test_db.py.
- Both preflights PASS for this bridge ID.

## Risks / Rollback

- Risk: legacy `gt projects authorize` invocations from CI without packet citation will start failing on amendments. Mitigation: grandfathered initial-version path means only amendments are affected; document migration in CHANGELOG.
- Rollback: revert the IP-1 amendment-detection block (single-function-scope change).

## Recommended Commit Type

`feat` - new mechanical governance gate. ~30 LOC net.
