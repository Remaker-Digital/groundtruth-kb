NEW

# WI-5062 Post-Reboot Dispatcher Supervisor Recovery

bridge_kind: prime_proposal
Document: gtkb-wi5062-post-reboot-dispatcher-supervisor-recovery
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f38dc-dc71-7af2-a3ba-d3e17ae4f13b
author_model: gpt-5
author_model_version: codex-desktop-2026-07-07
author_model_configuration: Codex desktop interactive Prime Builder; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-PLATFORM-SERVICE-SOT-WATCHDOG-AUTHORIZE-WI-5062
Project: PROJECT-PLATFORM-SERVICE-AND-SOT-AVAILABILITY-WATCHDOG
Work Item: WI-5062

target_paths: ["scripts/install_dispatcher_daemon_task.ps1", "scripts/install_service_sot_watchdog_task.ps1", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/watchdog/service_sot.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py", "platform_tests/scripts/test_gtkb_service_sot_watchdog.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py"]

implementation_scope: scripts, source, tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add the post-workstation-reboot acceptance case to WI-5062. The already-VERIFIED WI-5062 implementation added restore actions and disable guards, but a real workstation restart showed `GTKB-DispatcherDaemon` could still remain `Disabled` with no active disable guard while the dispatcher daemon was not running. That means the terminal verdict did not cover reboot persistence.

This follow-up keeps the same WI and PAUTH but uses a new bridge thread because the original thread is already `VERIFIED` and must remain append-only. The implementation should ensure the dispatcher supervisor task and service/SoT watchdog task are registered with reboot/startup trigger coverage, and that status probes expose and require that coverage.

## Problem Statement

Post-reboot evidence from 2026-07-06 showed:

- `GTKB-DispatcherDaemon` registered but `state = Disabled`.
- `GTKB-DispatcherDaemon` had no active `dispatcher-disable-guard.json` quiesce/TTL record.
- Dispatcher daemon `running = false`.
- `GTKB-HarnessStormWatchdog` remained healthy.

Manual remediation re-enabled the supervisor and started the daemon, after which complex health returned to `PASS`. WI-5062 terminal closure must not depend on this manual step.

## Specification Links

- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - Supervision must survive IDE, terminal, and workstation lifecycle boundaries.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - Disabled or missing supervisor state must recover or fail loud without owner discovery.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` - Reboot/startup recovery must use the existing ensure-alive path and must not spawn duplicate daemon loops.
- `ADR-DISPATCHER-ARCHITECTURE-001` - Repair the active dispatcher daemon substrate; do not restore retired pollers.
- `ADR-DISPATCHER-COMPLEX-CLI-001` and `SPEC-INTAKE-5e9375` - Dispatcher complex health and lifecycle status must reflect the whole daemon/supervisor/watchdog complex.
- `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001` and `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` - The service/SoT watchdog must be able to observe and safely restore platform service artifacts.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - Verification must rely on fresh scheduled-task/status probes, not stale heartbeat or cached dispatcher decisions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All implementation targets stay under `E:\GT-KB`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - This follow-up requires bridge GO before implementation and spec-derived verification before terminal closure.
- `GOV-STANDING-BACKLOG-001` - WI-5062 remains the durable backlog authority; the MemBase WI description has been amended with this scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Preserve the owner decision, amended WI, follow-up bridge trail, tests, and final verification as durable artifacts.

## Prior Deliberations

- `DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE` - Owner directed adding the post-reboot failure to WI-5062 scope and driving it to terminal state.
- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` - Original WI-5062 owner decision.
- `DELIB-20260706-WATCHDOG-RESTORATION-SAFETY-TIERED` - Owner selected safe/idempotent automatic restoration and fail-loud escalation for unsafe/canonical restore actions.
- `DELIB-20266276` - Dispatcher self-healing precedent for scheduled ensure-alive behavior.
- `bridge/gtkb-wi5062-dispatcher-supervisor-self-healing-guarded-disable-001.md` through `-004.md` - Prior WI-5062 proposal, GO, implementation report, and VERIFIED verdict. This follow-up adds acceptance evidence the verified chain did not include.

## Owner Decisions / Input

- Owner asked on 2026-07-06: "Can you add this to the scope of WI-5062 and drive it to terminal state?"
- `DELIB-20260706-WI5062-POST-REBOOT-RECOVERY-SCOPE` captures that decision.
- `WI-5062` description was updated to require post-workstation-reboot recovery or fail-loud blocked-restore evidence.

No further owner decision is needed before Loyal Opposition review.

## Requirement Sufficiency

Existing requirements sufficient. The dispatcher supervision and watchdog specifications already cover this behavior. The missing behavior is an acceptance and implementation gap in scheduled-task registration/status validation, not a new architecture decision.

## Proposed Implementation

1. Update `scripts/install_dispatcher_daemon_task.ps1` so the dispatcher supervisor task includes startup trigger coverage in addition to the existing interval repetition trigger.
2. Update `scripts/install_service_sot_watchdog_task.ps1` similarly so the watchdog runner can fire after reboot and restore disabled/missing service artifacts without requiring the dispatcher daemon to already be alive.
3. Extend `collect_supervisor_status()` to read scheduled-task triggers and expose whether the task has startup trigger coverage and repetition/interval trigger coverage. A registered task without startup trigger coverage should be unhealthy.
4. Extend service/SoT watchdog task status similarly so watchdog health can prove it has reboot/startup trigger coverage.
5. Add focused tests that fail on the current one-shot-only registration shape and pass only when startup trigger coverage is rendered/detected.
6. After implementation, re-register the live `GTKB-DispatcherDaemon` and `GTKB-ServiceSoTWatchdog` tasks through the governed install commands, then verify live status reports startup trigger coverage and dispatcher complex health is `PASS`.

## Non-Goals

- Do not restore retired OS poller or smart poller behavior.
- Do not change dispatcher routing configuration or harness eligibility.
- Do not add canonical backup restore actions.
- Do not require another physical reboot as the only verification path; a live Task Scheduler trigger/status probe plus simulated tests is acceptable, with the observed reboot failure cited as the regression.

## Spec-Derived Verification Plan

| Specification | Required evidence | Verification command |
| --- | --- | --- |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`, `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` | Dispatcher supervisor installer renders/registers startup trigger coverage and status marks missing startup trigger unhealthy. | `python -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_daemon_supervisor.py -q --tb=short` |
| `ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001`, `DCL-SERVICE-SOT-WATCHDOG-RESTORATION-SAFETY-001` | Service/SoT watchdog task installer/status exposes startup trigger coverage so the watchdog itself can recover services after reboot. | `python -m pytest platform_tests/scripts/test_gtkb_service_sot_watchdog.py -q --tb=short` |
| `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` | Startup trigger still invokes the existing ensure-alive entrypoint, preserving no-op when the daemon is already alive. | `python -m pytest platform_tests/scripts/test_dispatcher_daemon_supervision.py -q --tb=short` |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `ADR-DISPATCHER-COMPLEX-CLI-001`, `SPEC-INTAKE-5e9375` | Live post-implementation commands show supervisor enabled/healthy with startup trigger coverage and complex health `PASS`. | `gt bridge dispatch daemon supervisor status --json`; `gt watchdog service-sot status --json`; `gt bridge dispatch complex health --json` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps the tests and live commands above, plus changed-file lint/format checks. | `python -m ruff check <changed files>` and `python -m ruff format --check <changed files>` |

## Risk / Rollback

Primary risk is duplicate or noisy task firing after boot. The existing ensure-alive entrypoint is idempotent, so repeated task starts should no-op when the daemon is already alive. Rollback is a single revert of the installer trigger changes, status trigger parsing, tests, and any live task re-registration by rerunning the prior installer version.

## Bridge Filing

This proposal starts a new WI-5062 follow-up bridge thread because the original WI-5062 thread is already terminal `VERIFIED`. No existing bridge file is rewritten.

## Recommended Commit Type

fix: add post-reboot dispatcher supervisor recovery coverage

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
