NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Orphan-WI backfill Slice 2b: per-WI retire/exclude service (deterministic per-WI lifecycle surface)

bridge_kind: prime_proposal
Document: gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3464

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_projects_cli.py"]

Implementation proposal for a bounded code or platform change.

## Claim

GT-KB has no public per-work-item retire/exclude lifecycle surface. `ProjectLifecycleService` (`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`) exposes `add_project_item()`, `remove_project_item()` (a benign append-only *detach* that writes a `"removed"` membership version), and project-level `retire_project()`, but no `retire_project_work_item()` that performs an owner-approved, governed per-WI retirement gated on `GOV-ARTIFACT-APPROVAL-001` approval-packet evidence. The `gt projects` CLI correspondingly has no `retire-item` verb. As a result, Slice 2's resolution driver (`scripts/resolve_orphan_wi_memberships.py`) cannot execute owner `retire`/`exclude` decisions: per its `apply_resolution()` (lines ~167-210), those decisions are written as deferred-execution records to `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json` and never applied. This WI delivers the missing governed surface plus the consumer that drains that deferred-actions artifact.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-ARTIFACT-APPROVAL-001` already establishes that governed lifecycle mutations require owner-approval-packet evidence; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` already establishes the candidate/active/deferred/retired lifecycle states that this per-WI retirement transition fits; and the canonical packet validator (`groundtruth_kb.governance.approval_packet.validate_packet` + `parse_packet_path_from_change_reason`) already exists. This slice composes those existing surfaces into a per-WI retire service; it introduces no new public requirement/specification. (The WI's optional contract-change alternative — "model/display that automatic completion can precede report verification" — is out of scope and is NOT proposed here; were it pursued it would need a new/revised requirement.)

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_projects_cli.py`. The change is confined to the GT-KB platform package and platform tests; no adopter/application subtree under `applications/` is touched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed and tracked through the canonical bridge protocol; bridge `VERIFIED` is the authoritative terminal signal before the new governed surface is committed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the per-WI retirement is preserved as a durable artifact-lifecycle transition (an append-only non-active membership version plus cited approval-packet evidence), not an ephemeral mutation.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from a cited spec clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries `Project Authorization` / `Project` / `Work Item` linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - the retire/exclude decisions this service consumes originate from owner AUQ decisions captured by the Slice 2 driver; the consumer must honor that owner-decision provenance and refuse to act without it.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change stays in `groundtruth-kb/src/...` and `platform_tests/`; no application-placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-3464 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES; this is its bounded implementation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the new `gt projects retire-item` CLI verb is a harness-neutral surface invokable from either harness; no Claude-only assumption is introduced.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the retirement transition is artifact-backed (append-only membership version + approval packet reference in `change_reason`) rather than inferred.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the per-WI retire action with the durable lifecycle state (`retired`) it represents, distinct from the benign `removed` detach state.
- `GOV-ARTIFACT-APPROVAL-001` - the governing authority for this slice: `retire_project_work_item()` MUST refuse to execute unless its `change_reason` cites a valid, in-root, owner-approved formal-artifact-approval packet that passes `validate_packet()`.

## Prior Deliberations

- `DELIB-2509` - Owner AUQ Answer: Per-WI PAUTH + Assign-Only Scope for WI-3450 Orphan Backfill Driver. This is the decision that explicitly scoped Slice 2 to assignment-only and deferred per-WI retire/exclude execution to this follow-on slice (WI-3464).
- `DELIB-20261480` - Loyal Opposition Review, Orphan-WI Membership Backfill Slice 2 Implementation. Records the Slice 2 review context whose NO-GO (FINDING-P1-002) surfaced the absent per-WI retire/exclude surface this WI now supplies.
- `DELIB-2633` - Loyal Opposition Review, Orphan-WI Membership Backfill Slice 2 Implementation. Sibling Slice 2 review record corroborating the deferred-action contract and the `deferred_actions.json` artifact shape consumed here.
- `DELIB-20260745` - Loyal Opposition Review, `gt projects remove-item` REVISED Proposal. The remove-item precedent (append-only non-active membership) whose pattern `retire_project_work_item()` mirrors while adding the approval-packet gate; clarifies the remove-vs-retire distinction.
- `DELIB-20261322` - Loyal Opposition Review, `gt projects remove-item` REVISED Proposal. Records the non-active-status invariant (a `remove`/`retire` must never append an *active* membership) that this slice must also honor.
- `DELIB-20265457` - Owner decision (2026-06-21 AUQ) authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch; WI-3464 is in scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - the project-scoped non-fast-lane authorization envelope that admits WI-3464's implementation under PROJECT-GTKB-RELIABILITY-FIXES; this WI introduces a new public surface (a service method + CLI verb) so it is intentionally routed through the non-fast-lane batch authorization rather than the reliability fast-lane.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items in the non-fast-lane batch; this decision is the owner authorization basis for filing this proposal. Note: GOV-ARTIFACT-APPROVAL-001 per-execution approval packets remain required at *runtime* for each canonical per-WI retirement; this batch authorization covers the *implementation* of the surface, not any individual retirement it later performs.

## Proposed Scope

Minimal, three-file change composing existing surfaces:

1. `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` - add a public `retire_project_work_item()` method to `ProjectLifecycleService`:
   - Signature mirrors `remove_project_item()` plus an explicit approval-packet contract: `retire_project_work_item(project_id, work_item_id, *, changed_by, change_reason, project_root, status="retired")`.
   - Gate: parse the cited approval-packet path from `change_reason` via `approval_packet.parse_packet_path_from_change_reason()`; resolve it against `project_root` and require the resolved path stays in-root; load + JSON-parse the packet; require `approval_packet.validate_packet(packet).is_valid` is True. Refuse (raise `ProjectLifecycleError`) with a clear message when the path is missing, out-of-root, unreadable, or fails validation. This is the `GOV-ARTIFACT-APPROVAL-001` enforcement point.
   - Effect on pass: append a non-active membership version via `db.link_project_work_item(..., status=normalized_status)` carrying forward the current active membership's role/order/source (same append-only pattern as `remove_project_item`). Reuse the existing non-active-status invariant: empty status or case-insensitive `"active"` is rejected; default is `"retired"` (distinct from remove's `"removed"`). Fail closed when there is no active membership to retire.
2. `groundtruth-kb/src/groundtruth_kb/cli.py` - add a `gt projects retire-item` command mirroring `projects_remove_item`, with `project_id`/`work_item_id` arguments, `--status` (default `retired`), `--changed-by`, a required `--change-reason` (which must cite the approval-packet path), and `--json`. It resolves `project_root` from the active config and calls `service.retire_project_work_item(...)`, mapping `ProjectLifecycleError` to a `click.ClickException`.
3. `platform_tests/scripts/test_projects_cli.py` - add spec-derived regression tests for the three required behaviors (owner-approved execution, missing-packet refusal, idempotency) plus the in-root-packet check (see verification plan).

A data-migration PAUTH for the *canonical execution* against live `deferred_actions.json` (WI item 3) is explicitly NOT part of this code change; the canonical drain run is a separate owner-gated operational step performed after VERIFIED, and each retirement it performs supplies its own per-execution approval packet. This proposal delivers items (1), (2), the consumer surface for item (4) (the CLI/service that drains a deferred-actions record), and item (5) (tests).

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-ARTIFACT-APPROVAL-001` (governed retirement requires a valid owner-approval packet) | `test_retire_item_executes_with_valid_approval_packet` | With an in-root, schema-valid approval packet whose path is cited in `--change-reason`, `gt projects retire-item` appends a `"retired"` (non-active) membership version and the work item is excluded from the active membership set. |
| `GOV-ARTIFACT-APPROVAL-001` (refuse without packet evidence) | `test_retire_item_refused_when_packet_missing_or_invalid` | When `--change-reason` cites no packet path (or cites an out-of-root / malformed / schema-invalid packet), the command exits non-zero, raises a clear `ProjectLifecycleError`-derived message, and makes NO membership mutation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (idempotent, append-only lifecycle state) | `test_retire_item_idempotent_and_distinct_from_removed` | Retiring an already-retired (no active membership) WI fails closed without writing a new active version; a `retired` membership status is recorded distinctly from the benign `removed` detach state; the prior active version is preserved for audit. |
| `SPEC-AUQ-POLICY-ENGINE-001` (owner-decision provenance honored) | `test_retire_item_change_reason_carries_owner_decision_reference` | The appended membership version's `change_reason` carries forward the cited approval-packet reference (owner-decision provenance), confirming the retirement is traceable to owner-approval evidence rather than an unattributed mutation. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_projects_cli.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py`

## Acceptance Criteria

1. `ProjectLifecycleService.retire_project_work_item()` exists and refuses to mutate unless its `change_reason` cites a valid, in-root, schema-valid owner-approval packet (`validate_packet().is_valid`).
2. On a valid packet, it appends a non-active `"retired"` membership version (append-only; prior active version preserved), distinct from `remove_project_item`'s `"removed"` detach; it fails closed when there is no active membership and rejects empty/`"active"` status.
3. `gt projects retire-item` exposes the service via the CLI with the same arguments/options shape as `remove-item` plus packet-path-bearing `--change-reason`.
4. The four spec-derived tests pass; `ruff check` and `ruff format --check` are clean on all three changed files.
5. No canonical live drain of `deferred_actions.json` and no `groundtruth.db` mutation occur as part of this code change (the canonical drain is a separate owner-gated step).

## Risks / Rollback

- Risk: a too-weak gate (accepting a packet whose content does not actually cover this WI's retirement) could let a generic packet authorize an unrelated retirement. Mitigation: the gate requires a structurally valid packet cited in `change_reason`; the verification plan asserts refusal on missing/invalid packets. (Tightening the gate to also assert the packet mentions the specific `work_item_id`/`project_id`, as `packet_covers_amendment` does for spec amendments, is a reasonable hardening Loyal Opposition may require; it is a small additive check within the same file.)
- Risk: confusion between `remove-item` (benign detach, `removed`) and `retire-item` (governed retirement, `retired`). Mitigation: distinct CLI verbs, distinct default statuses, and a test asserting the distinction; docstrings state the difference explicitly.
- Risk: over-tightening could block legitimate retirements if the in-root packet-path resolution is too strict on path separators. Mitigation: reuse the established `parse_packet_path_from_change_reason()` (which already normalizes separators) rather than a new parser.
- Rollback: the change is additive (one new method, one new CLI command, new tests) with no schema migration; revert the three edits to fully restore prior behavior. The Slice 2 driver's deferred-action records remain intact and re-consumable.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_projects_cli.py`

## Recommended Commit Type

`feat`
