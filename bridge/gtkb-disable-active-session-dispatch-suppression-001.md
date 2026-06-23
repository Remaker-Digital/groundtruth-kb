NEW
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019ef07d-dbf6-7083-bd4c-3c997d20f111
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; owner-directed bridge-function repair; approval_policy=never

# Implementation Proposal - Disable Active-Session Dispatch Suppression

bridge_kind: prime_proposal
Document: gtkb-disable-active-session-dispatch-suppression
Version: 001
Author: Codex Loyal Opposition under owner-directed bridge-function repair authority
Date: 2026-06-22 UTC
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-CA9165
target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_bridge_dispatch_per_document_lease.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Claim

Disable the live cross-harness trigger's active-session spawn veto so a foreground Codex or Claude session no longer blocks headless dispatch to the same harness. The dispatcher should observe real contention through per-document leases, work-intent claims, and global/per-role process caps instead of suppressing the launch attempt at harness granularity.

## Problem Statement

The live dispatcher is currently eligible to send Loyal Opposition work to Codex A, but when a fresh active-session heartbeat lock is present the trigger records `target_active_session_present` and skips spawning that target. That guard is now acting as an infrastructure-level impediment to the platform's parallelism goal: it hides whether same-harness headless work would contend correctly under the newer lease and cap mechanisms.

The owner explicitly directed this session on 2026-06-22: disable this restriction and observe the actual contention, because unfettered parallelism is a core architectural goal and demonstrated contention problems should be corrected by better coordination, not by suppressing parallelism.

## Proposed Change

1. Remove the `check_target_active(target, state_dir)` pre-spawn branch from `run_trigger` in `scripts/cross_harness_bridge_trigger.py`.
2. Preserve active-session heartbeat files and `check_target_active` as diagnostic/status helpers only; do not let them prevent dispatch.
3. Preserve per-document lease filtering before dispatch selection, including the existing all-selected-items-leased result path.
4. Preserve `_spawn_harness` global concurrency and `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE` per-role caps.
5. Keep launch evidence visible in dispatcher state and dispatch-run metadata so post-change observation can distinguish actual process contention, claim conflicts, lease refusal, per-role saturation, and subprocess launch failure.

## Requirement Sufficiency

Existing requirements sufficient.

The owner direction in this session aligns with prior governing requirements and deliberations: `SPEC-INTAKE-ca9165`, `SPEC-INTAKE-9cb2ee`, `DELIB-2512`, `DELIB-20263189`, `DELIB-20263313`, and `DELIB-20263956`. No new formal requirement is needed before implementation; this proposal restores the bounded-parallel dispatch design that was already approved but later undercut by WI-4753's incident hotfix.

## Specification Links

- `SPEC-INTAKE-ca9165` - bounded parallel cross-harness auto-dispatch; supersede binary same-role active-session suppression.
- `SPEC-INTAKE-9cb2ee` - claim-gated implementation-start remains required before protected target edits.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass the bridge GO or implementation-start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge files and dispatcher/TAFE state remain the governed coordination path.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals must cite governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute spec-derived tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal includes project linkage metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - cited work item and authorization must resolve through MemBase.
- `GOV-STANDING-BACKLOG-001` - work remains tied to the MemBase work item.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - owner decision and bridge evidence are preserved as artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner directive is routed through durable bridge review.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - superseding a verified bridge hotfix is an artifact lifecycle event.

## Prior Deliberations

- `DELIB-2512` - owner clarification that harness-wide active-session suppression is not desirable and should be replaced with per-document leasing.
- `DELIB-20263189` - owner authorized the 22c078, 9cb2ee, and ca9165 dispatch/bridge-reliability package while preserving bridge and protected-artifact gates.
- `DELIB-20263313` - Loyal Opposition GO for bounded parallel cross-harness auto-dispatch, approving replacement of binary same-role active-session suppression with bounded per-role concurrency.
- `DELIB-20263956` - prior active-session suppression NO-GO, including citation to `DELIB-2512`; it required retryability and highlighted that active-session suppression is only a heuristic.
- `bridge/gtkb-bounded-parallel-cross-harness-dispatch-003.md` - withdrew the bounded-parallel proposal as already satisfied, which current live behavior shows was premature after WI-4753 reintroduced a spawn veto.
- `bridge/gtkb-wi4753-active-session-dispatch-hotfix-006.md` - VERIFIED the incident hotfix that restored active-session pre-spawn suppression; this proposal supersedes that hotfix in favor of the owner-stated parallelism goal.

## Owner Decisions / Input

Owner directive in this interactive session on 2026-06-22: disable the active-session suppression and observe actual contention. The owner stated that active-session suppression is an infrastructure-level impediment to parallelism, that unfettered parallelism is a core architectural goal, and that demonstrated contention problems should be corrected directly rather than resolved by restricting parallelism.

## Pre-Filing Preflight

This proposal is filed through the Codex non-bypass bridge writer. That helper runs the bridge-compliance gate in audit-only mode against the in-memory candidate before writing; the gate includes the pending applicability preflight and fails closed on missing required specifications, missing project metadata, invalid work-item/project authorization, missing Requirement Sufficiency, or author metadata gaps.

Loyal Opposition should rerun the mechanical review preflights on the filed operative bridge file before issuing any verdict:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-disable-active-session-dispatch-suppression
```

## Spec-Derived Verification Plan

- `SPEC-INTAKE-ca9165` / `DELIB-20263313`: add or update tests proving a fresh active-session lock no longer suppresses dispatch when no per-document lease blocks the selected work.
- `DELIB-2512`: preserve or update lease tests proving an active lease on document X does not suppress document Y, while a same-document lease still prevents duplicate processing.
- `SPEC-INTAKE-9cb2ee` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: perform implementation only after latest `GO`, matching work-intent claim, and a current implementation-start packet.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run focused trigger, lease, and cap tests plus ruff lint/format checks before filing the implementation report.

Expected focused verification commands:

```text
python -m pytest platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py -q --tb=short
ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

## Observation Plan

After implementation and restart/reload of the trigger environment, observe dispatcher state under live pending work:

- `gt bridge dispatch status --json`
- `gt bridge dispatch health --json`
- `.gtkb-state/bridge-poller/dispatch-state.json`
- dispatch-run metadata and stdout/stderr under the trigger run-state directory

Expected post-change behavior: a fresh active-session heartbeat may still be visible diagnostically, but it must not produce `target_active_session_present` as a pre-spawn veto. Any remaining blockage should classify as lease refusal, work-intent claim conflict, per-role/global concurrency cap, subprocess failure, or downstream verification failure.

## Acceptance Criteria

1. Active-session heartbeat locks no longer suppress eligible same-harness dispatch.
2. Per-document lease filtering still prevents duplicate processing of the same bridge item.
3. Per-role and global caps still bound live headless process count.
4. Dispatcher state exposes real contention or launch failures rather than hiding them behind active-session suppression.
5. No retired poller or alternate queue runtime is restored or created.

## Risk and Rollback

Risk: removing the veto may expose claim conflicts, subprocess hangs, or dispatch storms that were previously hidden. Mitigation: per-document leases, work-intent claims, global cap, and `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE` remain in force; observation should classify actual failures for follow-up fixes.

Rollback: restore the removed pre-spawn branch if the bounded controls fail catastrophically, then file a follow-up defect with the observed contention evidence. Rollback should be treated as temporary emergency backpressure, not the desired architecture.
