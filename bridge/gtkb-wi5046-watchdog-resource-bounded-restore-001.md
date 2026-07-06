NEW

# WI-5046 Watchdog Resource-Bounded Restore Execution

bridge_kind: prime_proposal
Document: gtkb-wi5046-watchdog-resource-bounded-restore
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3821-e2fc-75d2-814f-2a3ec0f71244
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-GTKB-SERVICE-SOT-WATCHDOG-WATCHDOG-FULL-PROJECT-IMPLEMENTATION
Project: PROJECT-GTKB-SERVICE-SOT-WATCHDOG
Work Item: WI-5046

target_paths: ["groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py", "groundtruth-kb/src/groundtruth_kb/watchdog/resource_limits.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py", "scripts/gtkb_service_sot_watchdog.py", "platform_tests/scripts/test_gtkb_service_sot_resource_limits.py"]

implementation_scope: source, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the resource-bounding layer for watchdog restore execution. Heavy restore actions must be gated by a fresh availability probe, deferred or throttled when the host is already under load, and run under a whole-process-tree cap rather than a per-PID-only limit.

This slice should provide the execution wrapper and tests for load-aware decisions and process-tree containment. It must not broaden policy authorization beyond the WI-5045 safe/canonical decision result.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires platform-wide restoration to be practical without creating new silent operational hazards.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Requires probe-before-restore, resource-bounded heavy restores, whole-process-tree caps, and symptom-based success.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires bridge-mediated proposal/report lifecycle.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires complete spec linkage and verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the project authorization, project, and work item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires executed spec-derived tests before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - Treats WI-5046 as durable work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Require traceable lifecycle evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires all implementation targets to remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized WI-5046 under the full watchdog project envelope.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner policy requires safe restoration to remain bounded and fail-loud when unsafe.
- `DELIB-20266276` - Dispatcher self-healing precedent includes auto-recovery but not unbounded host saturation.

Deliberation search command used before drafting:

```powershell
gt deliberations search "WI-5046 resource bounded restoration load-aware throttle process tree cap probe before restore symptom based health" --json
```

## Owner Decisions / Input

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` authorizes WI-5046 implementation under the active project authorization.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` constrains restore execution to safe/idempotent actions and fail-loud escalation for unsafe actions.

## Requirement Sufficiency

Existing requirements sufficient. WI-5046 and `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` specify the load-aware, process-tree, probe-before-restore, and symptom-based success constraints.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Heavy restores are deferred/throttled under load, guarded by a fresh probe, wrapped in a process-tree cap abstraction, and judged by symptom probes. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_resource_limits.py -q --tb=short` |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | Resource layer composes with watchdog runner/policy rather than hard-coding one service. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_resource_limits.py -q --tb=short` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files stay under declared GT-KB root paths. | `git diff --name-only -- groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/resource_limits.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_resource_limits.py` |

Implementation report must also include `ruff check` and `ruff format --check` for changed Python files.

## Risk / Rollback

Primary risk is giving a false sense of containment on Windows if child processes escape per-PID limits. The implementation should make the Windows Job Object / non-Windows process-group abstraction explicit and degrade safely when unavailable. Rollback is a single-commit revert of the resource wrapper and tests.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5046-watchdog-resource-bounded-restore`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat: this slice adds resource-bounded restore execution support and tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
