NEW

# Implementation Proposal - Orphan-WI Retire Item Start-Gate Repair

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-c239-7df0-8c15-537755d0eb70
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop Prime Builder session; owner init keyword `::init gtkb pb`; approval_policy=never; workspace=E:\GT-KB
author_metadata_source: transcript-declared interactive Prime Builder role plus repaired in-root session marker

bridge_kind: prime_proposal
Document: gtkb-orphan-wi-retire-item-start-gate-repair
Version: 001

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3464

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_projects_cli.py"]

## Claim

This proposal supersedes the non-startable GO thread `gtkb-orphan-wi-backfill-per-wi-retire-exclude-service` for the bounded service/CLI/test slice of `WI-3464`.

The prior thread reached `GO` at `bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-004.md`, but the mandatory implementation-start gate refused to authorize the approved proposal:

```json
{
  "authorized": false,
  "error": "Approved proposal is missing ## Requirement Sufficiency"
}
```

The governed revision helper correctly refused to publish a `REVISED` file over latest `GO`, so Prime Builder is filing this fresh `NEW` thread instead of bypassing bridge state. No source, test, database, deferred-action, or drain-script implementation mutation was performed under the failed start attempt.

This proposal preserves the version 003/004 implementation substance:

1. add `ProjectLifecycleService.retire_project_work_item()`;
2. add a harness-neutral `gt projects retire-item` CLI command;
3. add focused platform tests proving exact owner-approval-packet binding, mismatch rejection, missing/invalid/out-of-root packet rejection, idempotency, non-active status semantics, and change-reason provenance.

It does not authorize a canonical live drain of `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`, a data-migration PAUTH execution, a `groundtruth.db` mutation, or edits to the orphan-WI drain script. Those remain follow-on bridge work after this service/CLI surface is verified.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-ARTIFACT-APPROVAL-001` already requires governed lifecycle mutations to carry owner-approval evidence; `SPEC-AUQ-POLICY-ENGINE-001` already requires owner-decision provenance to be honored; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` already distinguishes durable lifecycle states such as active, deferred, removed, and retired; and the existing approval-packet utilities already provide packet-path parsing and packet validation.

The missing implementation surface is the composition of those existing requirements into a per-work-item retire/exclude service method, a `gt projects retire-item` CLI verb, and focused tests. This proposal introduces no new GOV, SPEC, ADR, DCL, PB, or REQ requirement and does not seek a formal-artifact mutation.

Runtime execution of any concrete per-WI retire/exclude action remains separately gated by owner-approval-packet evidence that binds to the exact project, work item, requested lifecycle action, and requested non-active status.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this fresh proposal follows the canonical numbered bridge chain after the prior GO proved non-startable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specifications constraining the service, CLI, tests, project linkage, and implementation-start gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps every required behavior to executable tests or source/quality gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries machine-readable `Project Authorization`, `Project`, `Work Item`, and `target_paths` metadata.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - per-WI retirement/exclusion is represented as an append-only lifecycle artifact with cited owner evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the lifecycle transition is traceable through a membership version and approval-packet reference in `change_reason`.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the requested non-active statuses represent durable lifecycle transitions distinct from benign `removed` detach.
- `GOV-ARTIFACT-APPROVAL-001` - the implementation must refuse governed per-WI retire/exclude execution unless cited owner-approval evidence is valid, in-root, and target-bound.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision provenance must be preserved and enforced when consuming retire/exclude decisions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation remains inside the GT-KB platform package and platform tests; no adopter/application subtree is touched.
- `GOV-STANDING-BACKLOG-001` - `WI-3464` is the standing-backlog source for this bounded implementation slice under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the new CLI surface is harness-neutral and can be invoked from supported harnesses without Claude-only assumptions.

## Project Root Boundary

All declared targets are under `E:\GT-KB`:

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\lifecycle.py`
- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\cli.py`
- `E:\GT-KB\platform_tests\scripts\test_projects_cli.py`

The proposal does not target `E:\GT-KB\applications\`, `E:\Claude-Playground`, any out-of-root path, `groundtruth.db`, `.gtkb-state/orphan-wi-discovery/**`, or `scripts/resolve_orphan_wi_memberships.py`.

## Prior Deliberations

- `DELIB-2509` - owner AUQ answer selecting per-WI PAUTH plus assign-only scope for the parent orphan-WI backfill driver; retire/exclude execution was deferred to this follow-on surface.
- `DELIB-20261480` - Loyal Opposition review of Orphan-WI Membership Backfill Slice 2, surfacing the absent per-WI retire/exclude surface.
- `DELIB-2633` - sibling Slice 2 review context corroborating the deferred-action artifact contract.
- `DELIB-20260745` - review of `gt projects remove-item` revised proposal, providing the append-only non-active-membership precedent.
- `DELIB-20261322` - review context for the non-active-status invariant shared with remove/retire lifecycle changes.
- `DELIB-20265457` - prior owner decision authorizing the earlier non-fast-lane proposal batch for this project.
- `DELIB-20265542` - Loyal Opposition NO-GO requiring exact approval-packet binding and removal or explicit deferral of the deferred-action drain claim.
- `DELIB-20265586` - current owner decision authorizing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23` for the 31 snapshot-bound member work items in `PROJECT-GTKB-RELIABILITY-FIXES`, including `WI-3464`.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23` authorizes bounded implementation work for the project's 31 snapshot-bound open member WIs, including `WI-3464`, and allows the relevant mutation classes: source, test addition, CLI extension, and related scaffold/update work inside the approved target paths.
- `DELIB-20265586` is the owner decision backing that project authorization.
- New work items added after the PAUTH snapshot are outside this authorization. This proposal does not add a work item.
- No additional owner decision is required for this corrected implementation proposal. Runtime per-item retire/exclude execution still requires separate owner-approval-packet evidence for each concrete lifecycle action.

## Proposed Scope

In scope:

1. `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` - add `ProjectLifecycleService.retire_project_work_item()` with exact approval-packet binding and append-only non-active membership semantics.
2. `groundtruth-kb/src/groundtruth_kb/cli.py` - add a `gt projects retire-item` command that invokes the service and exposes `project_id`, `work_item_id`, `--status`, `--changed-by`, required `--change-reason`, and `--json`.
3. `platform_tests/scripts/test_projects_cli.py` - add focused tests for exact matching approval packets, mismatch rejection, missing/invalid/out-of-root packet rejection, idempotency/status semantics, and change-reason provenance.

Out of scope:

- canonical live drain of `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`;
- data-migration PAUTH execution;
- `groundtruth.db` mutation;
- `scripts/resolve_orphan_wi_memberships.py` edits;
- any path outside the three approved target paths.

## Prior Review Findings Carried Forward

### Approval Packet Validation Must Bind To The Retired Item

`retire_project_work_item()` must parse the packet path from `change_reason`, resolve it under `project_root`, load and validate it, and confirm exact coverage of:

- `project_id`;
- `work_item_id`;
- lifecycle action (`retire` or `exclude`, derived from requested operation/status);
- requested non-active status.

If the current packet schema lacks dedicated structured fields for one value, the implementation must use a deterministic coverage helper over structured fields plus approval/evidence text and must fail closed on ambiguity. The tests must prove that valid packets for another project, another work item, a wrong action, or a wrong status are rejected without mutation.

### Deferred-Action Drain Is Not In Scope

The slice is narrowed to service, CLI, and tests. Deferred-action draining remains follow-on bridge work after this surface is verified.

## Specification-Derived Verification Plan

| Spec / obligation | Executable verification | Expected result |
| --- | --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` - governed lifecycle mutation needs valid owner approval evidence | `test_retire_item_executes_with_exact_matching_approval_packet` | With an in-root, valid packet covering the exact project, work item, action, and status, `gt projects retire-item` appends a non-active membership version and active membership lookup excludes the WI. |
| `GOV-ARTIFACT-APPROVAL-001` - approval evidence must bind to this requested mutation | `test_retire_item_rejects_mismatched_approval_packet` | Valid packets for a different project, different work item, wrong action, or wrong status exit non-zero and produce no membership mutation. |
| `GOV-ARTIFACT-APPROVAL-001` - missing or unsafe packet evidence fails closed | `test_retire_item_refuses_missing_invalid_or_out_of_root_packet` | Missing packet reference, malformed JSON, schema-invalid packet, unreadable packet, or out-of-root path fails with a clear CLI error and no mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - append-only non-active lifecycle state | `test_retire_item_idempotent_and_distinct_from_removed` | The previous active version is preserved, the new status is non-active and distinct from `removed`, empty/`active` status is rejected, and a second retire with no active membership fails closed without creating a duplicate active version. |
| `SPEC-AUQ-POLICY-ENGINE-001` - owner-decision provenance is preserved | `test_retire_item_change_reason_carries_owner_decision_reference` | The appended membership version carries the approval-packet reference in `change_reason`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation-start gate requires a sufficiency statement | `python scripts/implementation_authorization.py begin --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair` after GO and active claim | The gate authorizes this operative proposal instead of reporting a missing Requirement Sufficiency section. |
| Proposal scope discipline | source/test status inspection plus no drain-path diff | No source changes outside the three approved target paths; no `deferred_actions.json`, `groundtruth.db`, or `scripts/resolve_orphan_wi_memberships.py` mutation is part of this slice. |

Implementation verification commands after GO and implementation-start authorization:

```powershell
python -m pytest platform_tests\scripts\test_projects_cli.py -q --tb=short
python -m ruff check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
python -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
git diff --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair
```

Expected `git diff --name-only` output is limited to the three approved source/test target paths.

## Acceptance Criteria

1. The implementation-start gate authorizes this operative proposal after Loyal Opposition `GO` and active Prime work-intent claim.
2. `ProjectLifecycleService.retire_project_work_item()` exists and refuses to mutate unless `change_reason` cites an in-root, valid owner-approval packet that binds to the exact project, work item, lifecycle action, and requested non-active status.
3. `gt projects retire-item` exposes the service with `project_id`, `work_item_id`, required packet-bearing `--change-reason`, `--changed-by`, `--status` defaulting to `retired`, and `--json`.
4. Valid execution appends an audit-preserving non-active membership version and keeps the prior active version for history.
5. Mismatched, missing, malformed, schema-invalid, unreadable, or out-of-root packets fail closed without membership mutation.
6. No canonical live drain of `deferred_actions.json`, no `groundtruth.db` mutation, and no edit to `scripts/resolve_orphan_wi_memberships.py` occurs in this slice.
7. Focused CLI tests, ruff check, and ruff format check pass on the approved target set.

## Pre-Filing Preflight Subsection

Before live filing, Prime Builder runs:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair --content-file .gtkb-state/bridge-revisions/drafts/gtkb-orphan-wi-retire-item-start-gate-repair-001-complete.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-retire-item-start-gate-repair --content-file .gtkb-state/bridge-revisions/drafts/gtkb-orphan-wi-retire-item-start-gate-repair-001-complete.md
```

Observed pre-filing results:

```text
Applicability preflight:
- packet_hash: sha256:f130748d5080a9cabfbae1eb67e6b0655359b08f3dbd3caa75761cbe2e54d3db
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []

Clause applicability:
- clauses_evaluated: 5
- must_apply: 4
- may_apply: 1
- evidence_gaps_in_must_apply_clauses: 0
- blocking_gaps_gate_failing: 0

Placeholder scan:
- no placeholder sentinel terms found
```

## Risk And Rollback

Risk: this fresh thread could be mistaken for a duplicate implementation proposal. Mitigation: it explicitly supersedes the non-startable GO thread and preserves the same narrow three-file scope.

Risk: packet coverage matching could be too loose if implemented as generic text search. Mitigation: use structured packet fields where available, constrain any evidence-text fallback to exact project/work-item/action/status tokens, and prove mismatch rejection with tests.

Risk: narrowing this bridge slice leaves the backlog item's deferred-action drain unfinished. Mitigation: this proposal states that the drain remains follow-on bridge work after the verified service exists.

Rollback is path-local: revert the service method, CLI command, and tests in the three approved target paths. Because this proposal performs no live data drain or schema migration, rollback requires no data repair.

## Recommended Commit Type

`feat:` - the implementation adds a new governed service/CLI surface.
