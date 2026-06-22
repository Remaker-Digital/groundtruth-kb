NEW
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: codex-wi4753-hotfix-20260622
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop session; owner-approved bridge hotfix

# Bridge Hotfix Proposal - WI-4753 Active-Session Dispatch Suppression

bridge_kind: prime_proposal
Document: gtkb-wi4753-active-session-dispatch-hotfix
Version: 001
Author: Codex Loyal Opposition under owner-approved bridge-function repair authority
Date: 2026-06-22 UTC
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4753

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_bridge_dispatch_per_document_lease.py", "platform_tests/scripts/test_cross_harness_trigger_suppression.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Summary

Apply a narrow bridge-dispatch hotfix so hook-fired `cross_harness_bridge_trigger.py`
does not spawn a headless worker when the selected target harness already has a
fresh foreground active-session lock. The live incident is a Windows
Console Window Host process storm, with repeated headless dispatch attempts
while active Codex and Claude sessions are already present.

The current trigger already defines `check_target_active(target, state_dir)`,
but the live dispatch path no longer calls it before spawning. This proposal
authorizes restoring that guard as a pre-spawn suppression check, ahead of the
per-document lease filtering. Per-document lease behavior remains the governing
path when no target foreground session is active.

## Role Eligibility And Bridge-Repair Note

Codex harness A is currently operating as Loyal Opposition. Loyal Opposition is
normally not the author of `NEW` Prime Builder proposals. This filing is made
under the standing bridge-function repair exception in AGENTS.md: Loyal
Opposition has owner authority to diagnose and repair correct bridge function
and bridge use. The owner explicitly approved this incident hotfix in-session on
2026-06-22 with the prompt `approve bridge hotfix`.

## Problem Evidence

- Windows Task Manager showed a large `Console Window Host` population.
- Process inspection found the largest conhost family parented by Claude
  Desktop, while GT-KB dispatch state also showed repeated Codex/Claude
  headless worker launches and failed launches against the same bridge queue.
- `cross_harness_bridge_trigger.py` defines active-session suppression helpers,
  but the dispatch path suppresses only when all selected documents are leased;
  a fresh target active-session lock does not currently block spawning.
- `gt bridge dispatch status` and trigger diagnostics reported degraded dispatch
  health with repeated `launch_failed` and authorization-packet failure states.

## Scope

In scope:

- Restore a target-active-session pre-spawn suppression branch in
  `scripts/cross_harness_bridge_trigger.py`.
- Update focused tests so the expected behavior is explicit:
  a fresh target active-session lock suppresses spawning, while per-document
  leases still control same-document and cross-document behavior when no target
  active-session lock is present.

Out of scope:

- Replacing the per-document lease registry.
- Changing hook registration, retired poller behavior, dispatch prompt content,
  project authorization logic, or MemBase schemas.
- Increasing dispatch concurrency or changing reviewer routing.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge dispatch work remains governed by
  status-bearing bridge files and implementation authorization.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - live dispatch state and health must not
  continue to report or create stale/false worker state while the target harness
  is visibly active.
- `GOV-AUTOMATION-VALUE-VS-COST-001` - the automation cost of repeated
  headless process spawning outweighs the value while a foreground target
  session is already present.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` - event-driven dispatch remains
  enabled; this hotfix adds a pre-spawn guard rather than restoring retired
  interval polling.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - auto-trigger-on-actionable-change is
  preserved; spawning is suppressed only when the selected target is already
  active.
- `SPEC-INTAKE-57a736` - per-document leases remain the same-document
  contention mechanism when no target active-session lock is fresh.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete
  governing links are cited in this proposal.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization,
  project, and work item metadata are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification is mapped
  to focused source and test behavior below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under
  `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4753 is a single reliability work item, not a
  bulk backlog operation.

## Prior Deliberations

- `DELIB-2512` and `DELIB-2513` established and authorized per-document lease
  substitution. This hotfix acknowledges that history and limits the restored
  active-session guard to an incident backpressure role.
- `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-006.md`
  verified the per-document lease implementation.
- `bridge/gtkb-bridge-auto-dispatch-storm-004.md` verified earlier spawn
  backpressure/rate-guard work, but the current incident shows active target
  foreground sessions are still not suppressing hook-fired spawns.

## Owner Decisions / Input

The owner approved the hotfix in this session on 2026-06-22 by replying
`approve bridge hotfix` after the missing implementation authorization gate
blocked a direct source patch. No additional owner decision is required for
this bounded reliability fix.

## Requirement Sufficiency

Existing requirements sufficient. The bridge dispatch reliability and
automation value/cost requirements already require preventing runaway or
low-value headless dispatch. The prior per-document lease decision remains
governing for document-level contention; this hotfix adds an incident
backpressure guard for the separate case where the target harness itself is
already active in the foreground.

## Specification-Derived Verification Plan

| Spec or behavior | Verification |
|---|---|
| `GOV-AUTOMATION-VALUE-VS-COST-001` active foreground target should avoid duplicate headless process cost | Focused test proves a fresh target active-session lock returns `target_active_session_present` or the existing suppression token and does not dry-run/spawn. |
| `SPEC-INTAKE-57a736` per-document lease behavior remains valid without a foreground active lock | Existing lease tests still pass after updating the active-lock expectation. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` actionable signatures stay retryable | Suppression records `last_suppressed_signature`; no `last_dispatched_signature` is written for active-session suppression. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest over the trigger suppression and per-document lease test modules. |

Commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status
```

## Acceptance Criteria

1. `run_trigger` checks the selected target's active-session lock before
   spawning a headless worker.
2. A fresh target active-session lock suppresses dispatch and records a
   suppressed signature for retry.
3. Per-document lease tests still prove same-document lease refusal and
   cross-document non-suppression when no target foreground session is active.
4. Focused pytest, ruff check, and ruff format check pass for the changed files.

