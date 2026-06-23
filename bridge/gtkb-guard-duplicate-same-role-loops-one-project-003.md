REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef047-d4a9-7993-8217-7bb8a6745c97
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex automation auto-builder; owner-declared Prime Builder; approval_policy=never; workspace=E:\GT-KB
author_metadata_source: explicit automation metadata

# Revised Proposal - Guard duplicate same-role project loops

bridge_kind: prime_proposal
Document: gtkb-guard-duplicate-same-role-loops-one-project
Version: 003 (REVISED)
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-guard-duplicate-same-role-loops-one-project-002.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4378

target_paths: ["scripts/bridge_work_intent_registry.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py"]

## Revision Claim

This revision addresses the Loyal Opposition NO-GO by expanding the proposal from a registry-only primitive into an end-to-end same-role same-project stand-down guard. The implementation still starts with durable work-intent claim data, but it now also wires the check into the shared Prime selected-item filter in `scripts/cross_harness_bridge_trigger.py`. That filter is used before Prime spawn/acquire by both the cross-harness trigger and `scripts/single_harness_bridge_dispatcher.py`, so the guard runs before the expensive Prime investigation worker is launched.

The revised scope remains advisory and fail-open for correctness. It never blocks the per-thread `acquire` verdict, never overrides another claim, and never changes bridge lifecycle status. It only removes selected Prime items from the spawn batch when a different active same-role session already holds work in the same project.

## In-Root Placement Evidence

All proposed files and generated artifacts remain under `E:\GT-KB`. Source targets are `E:\GT-KB\scripts\bridge_work_intent_registry.py` and `E:\GT-KB\scripts\cross_harness_bridge_trigger.py`. Test targets are `E:\GT-KB\platform_tests\scripts\test_bridge_work_intent_registry.py`, `E:\GT-KB\platform_tests\scripts\test_cross_harness_bridge_trigger.py`, and `E:\GT-KB\platform_tests\scripts\test_single_harness_bridge_dispatcher.py`. The versioned bridge revision will be filed as `E:\GT-KB\bridge\gtkb-guard-duplicate-same-role-loops-one-project-003.md`.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` - the core requirement: cheap deterministic checks should run before expensive harness wakeups when they can prevent low-value duplicate automation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the work-intent registry and dispatcher serve bridge coordination; the guard must preserve per-thread claim correctness and the versioned bridge chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the stand-down decision is derived from durable claim rows and project membership evidence, not untracked process memory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites the governing specs constraining the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification includes registry-level and caller-level tests derived from the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work item metadata are present in machine-readable header lines.
- `SPEC-AUQ-POLICY-ENGINE-001` - boundary citation: this stand-down is deterministic and does not create an owner-decision or AskUserQuestion class.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - changes remain in GT-KB platform scripts/tests; no adopter/application boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4378 is an open MemBase work item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the shared trigger/filter path is harness-neutral and is consumed by both Codex and Claude dispatch surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the coordination decision is traceable to claim/project artifacts and bridge evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - expired and lapsed claims are ignored so stale lifecycle state cannot suppress fresh work.

## Prior Deliberations

- `DELIB-20264299` - loop multi-instance coordinator design Slice 1; directly relevant prior design context for coordinating multiple loop instances.
- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch containing WI-4378.
- `DELIB-20263200` - dispatch/claim role-eligibility fix context; relevant precedent for registry-authoritative role resolution in work-intent flows.
- `bridge/gtkb-guard-duplicate-same-role-loops-one-project-002.md` - Loyal Opposition NO-GO requiring an actual caller path plus caller-level regression coverage.

Semantic deliberation search for `WI-4378 duplicate same-role loop project work intent guard` on 2026-06-22 returned one directly relevant loop-coordinator review (`DELIB-20264300`) plus unrelated project-merge and advisory hits. The retained set above focuses on the existing proposal-cited loop and reliability authorization records.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - active project authorization for this reliability-fixes batch.
- `DELIB-20265457` - owner AUQ on 2026-06-21 authorizing the batch of open PROJECT-GTKB-RELIABILITY-FIXES proposals.

No new owner decision is required. The revision changes scope to satisfy the NO-GO by adding the existing dispatcher consumer path; it does not introduce a policy tradeoff.

## Requirement Sufficiency

Existing requirements sufficient. WI-4378 and `GOV-AUTOMATION-VALUE-VS-COST-001` already define the expected behavior: redundant same-role same-project loop work should stand down or switch before drafting/investigation burns tokens. This revision implements that existing requirement through the shared Prime dispatch filter and does not introduce a new requirement.

## Findings Addressed

### Finding P1-001 - Approved Scope Would Not Deliver The Claimed Guard

Response: accepted. Version 001 added a registry primitive while leaving the consumer out of scope, which would not make a duplicate loop stand down.

Revision: include `scripts/cross_harness_bridge_trigger.py` as an implementation target and wire the guard into `_filter_prime_selected_by_work_intent()`, the shared pre-spawn Prime filter used by both the cross-harness trigger and `scripts/single_harness_bridge_dispatcher.py`. The filter will query same-role same-project active holders before returning the selected Prime batch. If every selected item is removed by this guard, the caller receives an empty selected batch and records a stand-down/suppression reason rather than spawning a worker.

### Finding P2-002 - Spec-Derived Verification Stops At Helper Behavior

Response: accepted. Registry helper tests alone would prove only storage/query behavior.

Revision: add caller-level regression coverage. The cross-harness trigger test must prove a selected Prime item is removed before spawn when another active same-role session already owns the same project. The single-harness dispatcher test must prove its existing call through `_filter_prime_selected_by_work_intent()` observes the same stand-down result, preventing a substrate-specific bypass.

## Proposed Scope

1. In `scripts/bridge_work_intent_registry.py`, add additive nullable `acting_role` and `project_id` columns to `work_intent_claims` using the existing schema upgrade pattern. Existing rows remain valid and unresolved values stay NULL.
2. Populate those columns during claim acquisition:
   - `acting_role` comes from the same durable/session role-resolution discipline already used for GO-implementation eligibility, normalized to the canonical role label when resolvable.
   - `project_id` comes from the selected bridge thread's project linkage or project membership evidence. If project resolution fails, store NULL and fail open.
3. Add read-only registry helpers:
   - `project_id_for_thread(thread_slug, *, project_root=None) -> str | None`, using bridge project metadata and/or existing project membership evidence without mutating MemBase.
   - `same_role_project_holder(role, project_id, session_id, *, project_root=None) -> dict | None`, returning an active non-expired, non-lapsed different-session holder for the same role/project or `None`.
4. In `scripts/cross_harness_bridge_trigger.py`, call the new registry guard inside `_filter_prime_selected_by_work_intent()` after the existing per-thread holder check and before returning the selected batch.
   - Query the selected item's project id.
   - If a conflicting same-role same-project holder exists, drop that item, increment `held_count`, and record a durable expected suppression/failure record with a distinct reason such as `same_role_project_claim_active`, including the holder session, project id, document name, and TTL.
   - If project/role resolution or registry lookup fails, record a diagnostic only when appropriate and fail open rather than blocking the item.
5. Tests:
   - Registry tests for schema upgrade, column population, stale/lapsed claim exclusion, different-role exclusion, null fail-open behavior, and same-role same-project conflict return.
   - Cross-harness caller test proving `_filter_prime_selected_by_work_intent()` removes a selected Prime item before spawn when a different same-role same-project holder is active.
   - Single-harness dispatcher regression proving the dispatcher path uses the same filter result and does not bypass the guard.

Out of scope: a new CLI command, manual owner-facing project lease controls, changing the per-thread claim `acquire` return value, changing dispatch target selection, or forcing a work switch algorithm. The first slice may stand down; smarter switching can be a follow-on once the deterministic guard exists.

## Specification-Derived Verification Plan

| Specification / condition | Derived test | Required assertion |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001`: cheap guard before expensive duplicate same-role project work | `test_filter_prime_selected_stands_down_on_same_role_project_holder` | `_filter_prime_selected_by_work_intent()` returns no selected item and records `same_role_project_claim_active` when another active Prime session holds the same project. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`: per-thread claim correctness remains authoritative | `test_same_role_project_guard_does_not_alter_acquire_verdict` | `acquire()` on a different thread still succeeds; the new guard is advisory and caller-side only. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: stale claims do not suppress work | `test_same_role_project_holder_ignores_expired_or_lapsed_claim` | Expired draft and lapsed GO-implementation claims are ignored. |
| Role scoping | `test_same_role_project_holder_ignores_different_role` | LO claims on the same project do not suppress Prime work. |
| Missing metadata fail-open | `test_same_role_project_holder_returns_none_on_null_project_or_role` | NULL role or project returns `None`. |
| Schema upgrade | `test_work_intent_schema_upgrades_with_role_project_columns` | Existing DBs gain nullable `acting_role` and `project_id`; readers keep working. |
| Shared substrate caller | `test_single_harness_dispatcher_honors_prime_work_intent_filter_project_guard` | The single-harness dispatcher path observes the shared filter result and does not spawn/acquire when the selected Prime work is removed by the project guard. |

Verification commands:

```text
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
python -m ruff check scripts/bridge_work_intent_registry.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
python -m ruff format --check scripts/bridge_work_intent_registry.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
```

## Pre-Filing Preflight Subsection

Candidate-content preflights were run before live filing against this revision content:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-guard-duplicate-same-role-loops-one-project --content-file .gtkb-state/bridge-revisions/drafts/gtkb-guard-duplicate-same-role-loops-one-project-003.md --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-guard-duplicate-same-role-loops-one-project --content-file .gtkb-state/bridge-revisions/drafts/gtkb-guard-duplicate-same-role-loops-one-project-003.md
```

Required filing condition: applicability preflight passes with `missing_required_specs: []`, and clause preflight exits 0 with zero blocking gaps. The helper repeats both checks before publishing the live `REVISED` entry.

Observed candidate results on 2026-06-22:

- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; `packet_hash: sha256:70059f502253378dfab744fde88794db9820c14e7a3d0b1f3f130ef872eeb5b7`.
- Clause preflight: exit 0; clauses evaluated: 5; must_apply: 4; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

## Acceptance Criteria

1. Active claims record nullable `acting_role` and `project_id` without breaking existing readers or claim acquisition.
2. The registry can identify a different-session same-role same-project active holder and ignores same-session, different-role, different-project, expired, lapsed, and null cases.
3. The shared Prime selected-item filter removes duplicate same-role same-project work before spawn/acquire and records a distinct suppression reason.
4. The single-harness dispatcher path observes the same filter result because it already calls the shared filter.
5. Per-thread claim acquisition remains unchanged and remains the correctness boundary.
6. Focused registry, trigger, dispatcher, ruff lint, and ruff format checks pass.

## Risks / Rollback

- Risk: false positive suppression could strand useful work. Mitigation: fail open on missing role/project metadata, ignore expired/lapsed claims, and suppress only confirmed different-session same-role same-project matches.
- Risk: adding project resolution to the hot path adds overhead. Mitigation: the check runs at the existing claim/filter I/O boundary and only over the small selected Prime batch.
- Risk: single-harness and cross-harness behavior could diverge. Mitigation: integrate in `_filter_prime_selected_by_work_intent()`, already shared by both paths, and add single-harness regression coverage.
- Rollback: revert the additive registry columns/helpers, the `_filter_prime_selected_by_work_intent()` call-site change, and the tests. Existing nullable columns are harmless if left behind by a partial rollback.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`

## Recommended Commit Type

`fix`

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
