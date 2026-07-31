NEW

# WI-5062 Dispatcher Supervisor Self-Healing and Guarded Disable Controls

bridge_kind: prime_proposal
Document: gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-06 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f38dc-dc71-7af2-a3ba-d3e17ae4f13b
author_model: gpt-5
author_model_version: codex-desktop-2026-07-06
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

target_paths: ["config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py", "groundtruth-kb/src/groundtruth_kb/watchdog/restore_policy.py", "groundtruth-kb/src/groundtruth_kb/watchdog/resource_limits.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_disable_guard.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_gtkb_service_sot_watchdog.py", "platform_tests/scripts/test_gtkb_service_sot_restore_policy.py", "platform_tests/scripts/test_gtkb_service_sot_restore_registry.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_dispatcher_complex_control.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py"]

implementation_scope: config, source, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Close the operational gap exposed on 2026-07-06: `GTKB-DispatcherDaemon` can be disabled or missing while dispatcher daemon state is still fresh enough that bridge processing appears alive. The implementation should register the dispatcher supervisor scheduled task as its own SoT/restorable service artifact, wire the service/SoT watchdog to execute safe `ensure_alive` restores for disabled or missing scheduled-task services, and require dispatcher supervisor or complex disable operations to carry either a TTL-bound disable record or an explicit owner-quiesce record.

This is an actuator and guardrail slice. It must not restore the retired OS poller or smart poller, must not mutate canonical stores from backups, and must keep restore execution limited to safe/idempotent actions after a fresh failure probe.

## Problem Statement

The dispatcher daemon was observed live even though the `GTKB-DispatcherDaemon` scheduled-task supervisor was disabled. A healthy daemon heartbeat alone is therefore insufficient: if the running process exits, the disabled supervisor will not revive it. Existing WI-5044/WI-5045/WI-5046 work added registry metadata, tiering, and resource-bounding primitives, but does not yet make the service/SoT watchdog actively restore a disabled or missing dispatcher supervisor task.

The owner requirement is explicit: if the supervisor fails, it should automatically restart; if it is disabled, there should be a governed automatic restart path. Any intentional disable must be bounded by a TTL or an explicit owner quiesce record so it cannot silently persist.

## Specification Links

- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - The dispatcher daemon must be supervised by an OS scheduled task and the supervision contract must remain recoverable after IDE/terminal closure.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` - Restore paths must not spawn duplicate daemon loops; they must use the existing ensure-alive/supervisor controls.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - A missing or disabled supervisor must recover or fail loud without waiting for owner discovery.
- `ADR-DISPATCHER-ARCHITECTURE-001` - The dispatcher daemon is the active bridge automation substrate; implementation must repair that substrate rather than reviving retired pollers.
- `ADR-DISPATCHER-COMPLEX-CLI-001` and `SPEC-INTAKE-5e9375` - Complex health/control surfaces must accurately report lifecycle state and expose governed controls.
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` - Service and SoT availability checks should be generalized through the SoT registry and watchdog runner.
- `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - Automatic restore is allowed only for safe/idempotent actions, after a real failure probe, with visibility for unsafe/canonical actions.
- `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`, and `GOV-SOT-SINGLETON-001` - The dispatcher supervisor artifact must be declared in the canonical SoT registry and remain projection-compatible.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Restore decisions must come from fresh probes, not stale daemon heartbeat or cached dashboard state.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation targets remain inside `E:\GT-KB`; no Agent Red or out-of-root artifact is in scope.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - This proposal requires bridge GO before implementation, preserves project linkage, and maps verification to governing specs.
- `GOV-STANDING-BACKLOG-001` - `WI-5062` is the durable backlog authority for this incident-derived work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The owner decision, WI, PAUTH, proposal, tests, and final report form the governed artifact chain.

## Prior Deliberations

- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` - Owner accepted the new WI and proposal path for dispatcher supervisor self-healing and guarded disable controls.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected safe/idempotent automatic restoration and fail-loud escalation for canonical/unsafe restore actions.
- `DELIB-20266276` - Dispatcher self-healing precedent for scheduled ensure-alive behavior.
- `DELIB-20266140` - Visibility-only precedent that must remain representable by restore policy.
- `DELIB-202665470` - Dispatcher complex CLI precedent for lifecycle/health/control surfaces.
- `bridge/gtkb-wi5044-watchdog-restore-action-registry-001.md` through `-002.md` - Restore-action metadata proposal and GO, now resolved.
- `bridge/gtkb-wi5045-watchdog-tiered-restoration-policy-001.md` through `-006.md` - Tiered restore policy implementation and verification chain, now resolved.
- `bridge/gtkb-wi5046-watchdog-resource-bounded-restore-001.md` through `-006.md` - Resource-bounded restore implementation and verification chain, now resolved.

Deliberation and bridge context commands used before drafting:

```powershell
gt backlog show WI-5062 --json
gt projects show PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG --json
gt deliberations show DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI --json
rg -n "dispatcher supervisor|GTKB-DispatcherDaemon|restore_action|ensure_alive|disable" groundtruth-kb/src scripts platform_tests config/registry/sot-artifacts.toml
```

## Owner Decisions / Input

- Owner directive, 2026-07-06: create a new WI and proceed to propose implementation for the gap where disabled dispatcher supervision can persist silently.
- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` captures the owner decision.
- `PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062` authorizes only this bounded WI-5062 implementation.

No additional owner decision is required before Loyal Opposition review. Implementation still requires bridge GO and a matching implementation-start packet.

## Requirement Sufficiency

Existing requirements are sufficient. The dispatcher supervision DCLs define the expected supervisor behavior, the dispatcher complex specs define the control surface, and the watchdog restoration specs define the safe-auto constraints. No new formal spec is required before this implementation proposal.

## Proposed Implementation

1. Add a SoT registry row for the dispatcher supervisor scheduled task, distinct from the dispatcher state artifact. The row should use `restore_action = "ensure_alive"` and a health check that detects registered/enabled/hidden/pythonw/ensure-script compliance through the existing supervisor status probe.
2. Wire `groundtruth_kb.watchdog.service_sot` to evaluate each active SoT artifact probe through `decide_restore_action_for_artifact` and `execute_resource_bounded_restore` when the fresh probe reports `WARN` or `FAIL` and the policy returns `auto_restore`.
3. Implement the dispatcher supervisor `ensure_alive` restore recipe as safe/idempotent: install or enable the scheduled task using existing supervisor APIs, then re-run the symptom probe. Do not start a second daemon if one is already alive; rely on the existing supervisor/ensure script contract.
4. Record restore attempts in the service/SoT watchdog payload with `restore_actions_executed`, `restore_actions_deferred`, retry state, result status, and audit metadata. Canonical mutations must remain `[]`.
5. Add retry caps keyed by artifact/action so repeated failing restores escalate visibly instead of spinning. The cap may live in `.gtkb-state/watchdog/` runtime state, but source-of-truth declarations must remain in the SoT registry and code.
6. Add a shared dispatcher disable guard. `gt bridge dispatch daemon supervisor disable` and `gt bridge dispatch complex disable` should refuse unbounded disable by default. Accepted disable operations must supply either a TTL or an explicit owner-quiesce record and must write audit metadata that health/status surfaces can report.
7. Ensure TTL expiry causes the next watchdog/ensure-alive pass to re-enable or reinstall the supervisor. Explicit owner quiesce records should suppress auto-restore only while valid and visible.
8. Preserve manual owner emergency control via explicit TTL/quiesce options; do not remove enable/uninstall/dry-run surfaces.

## Non-Goals

- Do not restore or recreate the retired OS poller or retired smart poller.
- Do not add automatic restore for `git_restore` or `membase_export_restore`.
- Do not mutate credentials, production deployment configuration, or out-of-root artifacts.
- Do not fold the daemon process, supervisor scheduled task, and storm watchdog into one runtime.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001`, `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`, `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Shipped registry declares a separate dispatcher supervisor scheduled-task artifact with `restore_action = "ensure_alive"`; typed reader/projection parity still passes. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_restore_registry.py -q --tb=short` |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Watchdog executes only safe/idempotent restores after a fresh failure probe, records audit payloads, respects retry caps, and never records canonical mutations. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py platform_tests/scripts/test_gtkb_service_sot_restore_policy.py -q --tb=short` |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`, `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` | Disabled/missing `GTKB-DispatcherDaemon` supervisor is restored or escalated by the service/SoT watchdog path; complex health no longer treats a disabled supervisor as acceptable after restore. | `python -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py -q --tb=short` |
| `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` | Restore path uses supervisor/ensure-alive controls without spawning duplicate daemon loops. | `python -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short` |
| `ADR-DISPATCHER-COMPLEX-CLI-001`, `SPEC-INTAKE-5e9375` | Dispatcher supervisor and complex disable commands reject unbounded disable, accept TTL/quiesce disable with audit metadata, and report the disable record in status/health payloads. | `python -m pytest platform_tests/scripts/test_dispatcher_complex_control.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_watchdog.py -q --tb=short` |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report cites all executed targets above plus lint/format checks and maps each result to this table. | `python -m ruff check .` and `python -m ruff format --check .` |

Implementation report must include the spec-derived pytest targets above, `python -m ruff check .`, and `python -m ruff format --check .`. If any target is intentionally narrowed to changed files, the report must explain why the narrower command is still spec-derived.

## Risk / Rollback

Primary risk is an over-eager restore loop. The implementation should fail closed through fresh symptom probes, retry caps, and visibility for exhausted restores. Secondary risk is blocking legitimate owner maintenance; TTL/quiesce options preserve explicit controlled disable. Rollback is a single-commit revert of registry row, service/SoT execution wiring, disable guard module/CLI changes, and tests.

## Bridge Filing

This proposal is filed as the first numbered bridge file for `gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable`. The dispatcher/TAFE state and the numbered file chain remain the live workflow authority.

## Recommended Commit Type

fix: restore dispatcher supervisor automatically and guard unbounded disable

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
