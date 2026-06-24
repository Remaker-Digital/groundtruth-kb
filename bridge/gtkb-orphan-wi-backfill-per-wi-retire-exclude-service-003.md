REVISED

# Revised Proposal - Orphan-WI Per-Item Retire/Exclude Service

author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ef094-6d42-7541-a32f-0ae73d233921
author_model: gpt-5-codex
author_model_version: 2026-06-22
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

bridge_kind: prime_revision
Document: gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
Version: 003
Responds-To: bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3464

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_projects_cli.py"]

## Revision Claim

This revision preserves the bounded service and CLI implementation scope from version 001 while correcting the two version 002 NO-GO findings.

The implementation slice now claims only:

1. a public `ProjectLifecycleService.retire_project_work_item()` service method;
2. a `gt projects retire-item` CLI command that invokes that service; and
3. focused platform tests for owner-approved execution, mismatched-packet rejection, missing/invalid-packet rejection, idempotency, and status semantics.

The approval gate is strengthened: a syntactically valid approval packet is not enough. The service must validate that the cited owner-approval packet covers the exact `project_id`, exact `work_item_id`, exact lifecycle action (`retire` or `exclude`, according to the requested status/action), and the requested non-active status. A valid packet for any other project, work item, lifecycle action, or status must fail closed without a membership mutation.

This proposal no longer claims to drain `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`. The canonical deferred-action consumer and any data-migration PAUTH remain follow-on work after the service and CLI surface are VERIFIED. That follow-on work is expected to target `scripts/resolve_orphan_wi_memberships.py` or another explicit drain path and must carry its own bridge authorization.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision is filed through the canonical bridge protocol before any protected source mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - per-WI retirement/exclusion is preserved as an append-only lifecycle artifact with owner-approval evidence, not an ephemeral deletion.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the revised proposal cites the governing specs constraining the service, CLI, and tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps every required behavior to an executable test or quality gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths remain machine-readable in this revision.
- `SPEC-AUQ-POLICY-ENGINE-001` - retire/exclude execution must honor owner-decision provenance and refuse to act without approval evidence that binds to the exact requested lifecycle action.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation remains inside GT-KB platform source and platform tests; no adopter/application subtree is touched.
- `GOV-STANDING-BACKLOG-001` - `WI-3464` remains the standing-backlog source for this bounded implementation slice.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the new CLI surface is harness-neutral and can be invoked from either supported harness.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the lifecycle transition remains traceable through a membership version and approval-packet reference in `change_reason`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the new non-active statuses represent durable lifecycle transitions distinct from active assignment and benign `removed` detach.
- `GOV-ARTIFACT-APPROVAL-001` - the service must refuse governed per-WI retirement/exclusion unless cited owner-approval evidence is valid, in-root, and target-bound.

## Prior Deliberations

- `DELIB-2509` - owner AUQ answer selecting per-WI PAUTH plus assign-only scope for the Slice 2 orphan backfill driver; retire/exclude execution was deferred to this follow-on.
- `DELIB-20261480` - Loyal Opposition review of Orphan-WI Membership Backfill Slice 2, surfacing the absent per-WI retire/exclude surface.
- `DELIB-2633` - sibling Slice 2 review context corroborating the deferred-action artifact contract.
- `DELIB-20260745` - review of `gt projects remove-item` revised proposal, providing the append-only non-active-membership precedent.
- `DELIB-20261322` - review context for the non-active-status invariant shared with remove/retire lifecycle changes.
- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` authorizes this implementation proposal under PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-20265457` authorizes filing non-fast-lane proposals for the open reliability-fix work items, including `WI-3464`.

No new owner decision is required for this revision. Runtime per-item retire/exclude execution still requires per-execution owner-approval-packet evidence. Deferred-action draining is explicitly left to follow-on bridge work and is not approved by this proposal.

## Requirement Sufficiency

Existing requirements sufficient.

## Findings Addressed

### Finding P1-001 - Approval Packet Validation Does Not Bind To The Retired Item

Response: resolved by strengthening the required service contract and tests.

`retire_project_work_item()` must parse the packet path from `change_reason`, resolve it under `project_root`, load and validate it, and then confirm the packet covers the exact requested lifecycle mutation:

- exact `project_id`;
- exact `work_item_id`;
- exact lifecycle action (`retire` or `exclude`, derived from the requested operation/status contract); and
- exact requested non-active status.

If the current packet schema lacks dedicated structured fields for one of those values, the implementation must use a deterministic coverage helper over the packet's structured fields plus approval/evidence text and document that matching rule in code or tests. The helper must fail closed on ambiguity. The CLI test suite must include negative cases proving a valid packet for a different project, different work item, wrong lifecycle action/status, missing packet, malformed packet, schema-invalid packet, and out-of-root packet is rejected without writing any membership version.

### Finding P1-002 - Deferred-Action Drain Is Claimed But Not In Scope

Response: resolved by narrowing the bridge slice.

This revision removes the claim that version 001 would deliver the deferred-action consumer or drain `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`. The approved target paths stay limited to the service, CLI, and CLI tests:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_projects_cli.py`

The deferred-action drain remains a follow-on bridge item after this surface is VERIFIED. That later slice should include the actual drain path and tests, likely `scripts/resolve_orphan_wi_memberships.py`, and should use the verified service/CLI instead of embedding a second lifecycle mutation path.

## Scope Changes

Scope is narrowed from version 001:

- In scope: service method, CLI command, and focused tests for exact packet binding and lifecycle semantics.
- Out of scope: canonical live drain of `deferred_actions.json`, data-migration PAUTH execution, `groundtruth.db` mutation, and edits to `scripts/resolve_orphan_wi_memberships.py`.
- Target paths are unchanged from version 001 because the revision chooses narrowing instead of expanding scope.

## Pre-Filing Preflight Subsection

Before live filing, this completed revision content is checked with:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service --content-file .gtkb-state/bridge-revisions/drafts/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-003.md
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service --content-file .gtkb-state/bridge-revisions/drafts/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-003.md
```

The governed revision helper reruns these checks before publishing the live `REVISED` bridge file.

## Revised Verification Plan

| Spec / obligation | Executable verification | Expected result |
| --- | --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` - governed lifecycle mutation needs valid owner approval evidence | `test_retire_item_executes_with_exact_matching_approval_packet` | With an in-root, valid packet covering the exact project, work item, action, and status, `gt projects retire-item` appends a non-active membership version and active membership lookup excludes the WI. |
| `GOV-ARTIFACT-APPROVAL-001` - approval evidence must bind to this requested mutation | `test_retire_item_rejects_mismatched_approval_packet` | Valid packets for a different project, different work item, wrong action, or wrong status exit non-zero and produce no membership mutation. |
| `GOV-ARTIFACT-APPROVAL-001` - missing or unsafe packet evidence fails closed | `test_retire_item_refuses_missing_invalid_or_out_of_root_packet` | Missing packet reference, malformed JSON, schema-invalid packet, unreadable packet, or out-of-root path fails with a clear CLI error and no mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - append-only non-active lifecycle state | `test_retire_item_idempotent_and_distinct_from_removed` | The previous active version is preserved, the new status is non-active and distinct from `removed`, empty/`active` status is rejected, and a second retire with no active membership fails closed without creating a new active version. |
| `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision provenance is preserved | `test_retire_item_change_reason_carries_owner_decision_reference` | The appended membership version carries the approval-packet reference in `change_reason`. |
| Proposal scope discipline | targeted source/test status inspection plus no drain-path diff | No source changes outside the three approved target paths; no `deferred_actions.json`, `groundtruth.db`, or `scripts/resolve_orphan_wi_memberships.py` mutation is part of this slice. |

Implementation verification commands:

```powershell
python -m pytest platform_tests\scripts\test_projects_cli.py -q --tb=short
python -m ruff check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
python -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
git diff --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
```

Expected `git diff --name-only` output is limited to the three approved source/test target paths.

## Acceptance Criteria

1. `ProjectLifecycleService.retire_project_work_item()` exists and refuses to mutate unless `change_reason` cites an in-root, valid owner-approval packet that binds to the exact project, work item, lifecycle action, and requested non-active status.
2. `gt projects retire-item` exposes the service with `project_id`, `work_item_id`, required packet-bearing `--change-reason`, `--changed-by`, `--status` defaulting to `retired`, and `--json`.
3. Valid execution appends an audit-preserving non-active membership version and keeps the prior active version for history.
4. Mismatched, missing, malformed, schema-invalid, unreadable, or out-of-root packets fail closed without membership mutation.
5. No canonical live drain of `deferred_actions.json`, no `groundtruth.db` mutation, and no edit to `scripts/resolve_orphan_wi_memberships.py` occurs in this slice.
6. Focused CLI tests, ruff check, and ruff format check pass on the approved target set.

## Risk And Rollback

Risk: packet coverage matching could be too loose if implemented as generic text search. Mitigation: use structured packet fields where available, constrain any evidence-text fallback to exact project/work-item/action/status tokens, and prove mismatch rejection with tests.

Risk: narrowing this bridge slice leaves the backlog item's deferred-action drain unfinished. Mitigation: this revision states that the drain remains follow-on bridge work after the verified service exists. That prevents a false VERIFIED signal while still unblocking the prerequisite surface.

Risk: confusion between `remove-item` and `retire-item`. Mitigation: distinct CLI verb, distinct default status, governed approval gate, and tests asserting `retired` remains distinct from benign `removed`.

Rollback is additive and path-local: revert the service method, CLI command, and tests in the three approved target paths. Because this proposal performs no live data drain or schema migration, rollback requires no data repair.
