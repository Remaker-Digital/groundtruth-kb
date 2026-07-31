NEW

# WI-5043 Service and SoT Watchdog Runner

bridge_kind: prime_proposal
Document: gtkb-wi5043-service-sot-watchdog-runner
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
Work Item: WI-5043

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py", "scripts/gtkb_service_sot_watchdog.py", "scripts/install_service_sot_watchdog_task.ps1", "scripts/uninstall_service_sot_watchdog_task.ps1", "platform_tests/scripts/test_gtkb_service_sot_watchdog.py"]

implementation_scope: source, tests, scheduled-task
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the foundational runner for the platform-wide service and SoT availability watchdog. The runner will execute a dependency-light scheduled pass over the current `gt status` components and the SoT-registry health-check functions, producing deterministic machine-readable results that later restore-policy slices can consume.

This slice is intentionally detection-first. It may add a CLI/script wrapper and scheduled-task install/uninstall helpers, but it must not auto-restore, mutate canonical stores, or claim completion of the restore-action registry, policy engine, or resource-bounding slices. Those remain separate work items in the same project.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires a platform-wide watchdog that generalizes the dispatcher D2/D4 posture to every `gt status` component and every SoT-registry `health_check_function`, with a dependency-light detection path.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Constrains this runner to fresh probes and symptom-based health evidence, and prevents this slice from auto-executing unsafe/canonical restoration.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires all GT-KB implementation targets to remain inside the GT-KB root and not silently resolve to Agent Red or any out-of-root application surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires status-bearing bridge files and dispatcher/TAFE state to be the live workflow authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this implementation proposal to cite all relevant governing specifications and map them to verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the Project Authorization, Project, and Work Item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the implementation report to carry forward these specifications and execute derived tests before verification.
- `GOV-STANDING-BACKLOG-001` - Treats WI-5043 and PROJECT-GTKB-SERVICE-SOT-WATCHDOG as the durable MemBase work authority for this scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires concrete implementation plans, owner decisions, risks, and future work to be preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Frames this work as part of the durable artifact graph connecting project, work item, bridge proposal, tests, and verification report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Requires lifecycle states and transition evidence to remain explicit as the project moves from proposal to implementation report to verification.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized the full watchdog project, including WI-5043, while preserving per-WI bridge GO requirements.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected tiered auto-restore for safe/idempotent actions and fail-loud escalation for canonical/at-risk actions; this runner supplies the probe input for that policy.
- `DELIB-20266276` - Dispatcher self-healing precedent: D2 full auto-recovery, D3 scheduled ensure-alive, and D4 alert-and-degrade are the model being generalized.
- `DELIB-20266140` - Visibility-only precedent: owner-marked components must remain visible and must not be silently auto-restored.

Deliberation search command used before drafting:

```powershell
gt deliberations search "PROJECT-GTKB-SERVICE-SOT-WATCHDOG WI-5043 platform service SoT availability watchdog runner scheduled verification" --json
```

## Owner Decisions / Input

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` records the owner AUQ authorizing full-project implementation for all six watchdog work items, including WI-5043. The authorization allows `source`, `tests`, `config`, and `scheduled-task` mutation classes, and forbids canonical-store data mutation, deployment, credential operations, and force-push.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` records the owner AUQ selecting tiered auto-restore plus fail-loud escalation. This proposal uses that decision only to shape detection and output semantics; restore execution belongs to later project slices.

## Requirement Sufficiency

Existing requirements sufficient. The implementation is bounded by `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001`, WI-5043, and the active project authorization. No new or revised requirement is needed before implementing this detection-runner slice.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | Runner enumerates `gt status` components and SoT-registry records with `health_check_function` values without depending on the watched services as prerequisites. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short` |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Runner performs fresh probes, emits symptom-oriented health results, and does not auto-restore or mutate canonical stores in this slice. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation modifies only GT-KB root paths listed in `target_paths`; no Agent Red lifecycle-independent repository or out-of-root path is touched. | `git diff --name-only -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/sot_registry.py groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py scripts/install_service_sot_watchdog_task.ps1 scripts/uninstall_service_sot_watchdog_task.ps1 platform_tests/scripts/test_gtkb_service_sot_watchdog.py` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation report carries the same project authorization, project, work item, and target-path scope. | `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5043-service-sot-watchdog-runner` before protected edits |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report maps these specs to executed tests and observed results. | Report-time evidence: `python -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short`; plus ruff lint/format on changed Python files |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Bridge proposal, implementation report, and work item linkage remain explicit durable artifacts through the lifecycle. | `gt bridge show gtkb-wi5043-service-sot-watchdog-runner --json --compact` after filing/reporting |

Additional implementation-report gates if Python files change:

```powershell
ruff check groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py
ruff format --check groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py scripts/gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_watchdog.py
```

## Risk / Rollback

Primary risk is over-coupling the runner to services it watches or accidentally turning the detection slice into a restore slice. The implementation should isolate collection from restoration, emit structured status, and keep scheduled-task helpers idempotent. Rollback is a single-commit revert of the new runner, CLI/script wrapper, scheduled-task helper scripts, and tests.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5043-service-sot-watchdog-runner`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat: this slice adds a new watchdog runner capability, its scheduled wrapper surface, and targeted tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
