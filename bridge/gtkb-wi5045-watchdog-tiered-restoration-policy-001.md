NEW

# WI-5045 Watchdog Tiered Restoration Policy

bridge_kind: prime_proposal
Document: gtkb-wi5045-watchdog-tiered-restoration-policy
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
Work Item: WI-5045

target_paths: ["groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py", "groundtruth-kb/src/groundtruth_kb/watchdog/restore_policy.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py", "groundtruth-kb/src/groundtruth_kb/bridge/disposition.py", "platform_tests/scripts/test_gtkb_service_sot_restore_policy.py"]

implementation_scope: source, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement the watchdog policy engine that decides what a failed health probe may do next: safe/idempotent auto-restore, canonical fail-loud escalation, visibility-only no-restore, or advisory escalation after retry exhaustion. The policy consumes the runner output and restore-action metadata; it does not need to perform heavy restore execution itself.

The implementation must make the decision result explicit and testable so later resource-bounded execution can call it without reinterpreting owner policy.

## Specification Links

- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Requires tiered restoration across platform services and SoT-registry artifacts.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Requires safe-vs-canonical classification, fail-loud canonical handling, visibility-only overrides, fresh probes, retry exhaustion escalation, and no canonical auto-mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires this proposal and later report to flow through the bridge file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires complete specification linkage and verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires the project authorization, project, and work item metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires executed spec-derived tests before verification.
- `GOV-STANDING-BACKLOG-001` - Treats WI-5045 and the project as durable work authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Require durable linkage and explicit lifecycle evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires all target paths to remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` - Owner authorized all watchdog WIs with per-WI GO.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Direct owner decision for safe/idempotent auto-restore plus fail-loud canonical escalation.
- `DELIB-20266276` - Dispatcher D2/D4 precedent for full auto-recovery and alert-and-degrade behavior.
- `DELIB-20266140` - Visibility-only precedent that forbids auto-restoring owner-marked manual controls.

Deliberation search command used before drafting:

```powershell
gt deliberations search "WI-5045 tiered restoration policy safe canonical fail loud visibility-only ADVISORY escalation watchdog" --json
```

## Owner Decisions / Input

- `DELIB-20260706-WATCHDOG-PROJECT-AUTHORIZATION` authorizes WI-5045 implementation under the project envelope.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` is the operative owner policy: safe/idempotent actions may auto-execute, canonical/at-risk actions must fail loud, and repeated failures must escalate.
- `DELIB-20266140` requires visibility-only overrides to remain no-auto-restore.

## Requirement Sufficiency

Existing requirements sufficient. WI-5045 plus `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` specify the policy states and forbidden behavior.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Policy returns safe auto-restore only for safe/idempotent actions; canonical and visibility-only targets never auto-execute; retry exhaustion escalates. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_restore_policy.py -q --tb=short` |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` | Policy consumes watchdog probe results and registry metadata rather than hard-coded ad-hoc service branches. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_restore_policy.py -q --tb=short` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files remain under the declared GT-KB root target paths. | `git diff --name-only -- groundtruth-kb/src/groundtruth_kb/watchdog/__init__.py groundtruth-kb/src/groundtruth_kb/watchdog/restore_policy.py groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py groundtruth-kb/src/groundtruth_kb/bridge/disposition.py platform_tests/scripts/test_gtkb_service_sot_restore_policy.py` |

Implementation report must also include `ruff check` and `ruff format --check` for changed Python files.

## Risk / Rollback

Primary risk is accidentally allowing canonical-store mutation or hidden no-op degradation. The policy should return explicit decision objects and preserve ADVISORY/flagged escalation as a visible outcome. Rollback is a single-commit revert of the policy module and tests.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5045-watchdog-tiered-restoration-policy`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat: this slice adds the watchdog restoration policy capability and targeted tests.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
